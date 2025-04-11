from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
import os
from datetime import datetime
import aiofiles
from pathlib import Path
import json
import logging
import PyPDF2
import io
from PIL import Image
import base64
from dotenv import load_dotenv
import torch
import re

# Try to import ColPali models, but provide fallback if they're not available
try:
    from transformers import AutoTokenizer, AutoModel
    # Only try to import ColPali if transformers version is high enough
    COLPALI_AVAILABLE = False
    logging.info("Using standard transformer models as fallback")
except ImportError:
    COLPALI_AVAILABLE = False
    from transformers import AutoTokenizer, AutoModel
    logging.warning("Transformers library not available, using basic fallback implementation")

import asyncio

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
logger.info(f"Upload directory: {UPLOAD_DIR.absolute()}")

# Initialize model and processor (lazy loading to save memory)
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
model = None
processor = None

def get_model():
    global model, processor
    if model is None:
        logger.info(f"Initializing model: {MODEL_NAME}")
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        try:
            # Load model with appropriate precision
            dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
            
            # Use sentence-transformers for document embedding
            model = AutoModel.from_pretrained(MODEL_NAME).to(device).eval()
            processor = AutoTokenizer.from_pretrained(MODEL_NAME)
            logger.info("Sentence transformer model initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing model: {str(e)}")
            raise e
            
    return model, processor

# Models
class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: str
    file_path: str
    file_type: str
    status: str
    created_at: str

class DocumentAnalysisRequest(BaseModel):
    model: str = "document-analyzer"

class DocumentChatRequest(BaseModel):
    query: str
    model: str = "document-analyzer"

class ChatMessage(BaseModel):
    role: str
    content: str

class DocumentChatResponse(BaseModel):
    document_id: str
    response: str
    messages: List[ChatMessage]

class Entity(BaseModel):
    name: str
    type: str
    mentions: List[str]

class DocumentAnalysisResponse(BaseModel):
    document_id: str
    summary: str
    key_points: List[str]
    risks: List[str]
    entities: List[Entity]
    model: str

# In-memory database for documents and chat histories
documents_db = {}
document_chat_histories = {}
document_embeddings = {}  # Store document embeddings for efficient retrieval

async def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from PDF file."""
    try:
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract text from PDF file: {str(e)}"
        )

async def extract_text_from_image(file_path: Path) -> str:
    """Placeholder for OCR functionality"""
    # In a real implementation, you would use an OCR library like pytesseract
    return "Image document - text extraction would require OCR processing."

def extract_entities(text: str) -> List[Dict[str, Any]]:
    """Extract entities using simple regex patterns"""
    entities = []
    
    # Find potential people names (capitalized words)
    person_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
    people = re.findall(person_pattern, text)
    
    # Find potential organizations (uppercase words)
    org_pattern = r'\b[A-Z][A-Z]+\b'
    orgs = re.findall(org_pattern, text)
    
    # Add people entities
    for person in set(people):
        entities.append({
            "name": person,
            "type": "person",
            "mentions": ["Found in document"]
        })
    
    # Add organization entities
    for org in set(orgs):
        entities.append({
            "name": org,
            "type": "organization",
            "mentions": ["Found in document"]
        })
    
    return entities

def extract_key_points(text: str, max_points: int = 5) -> List[str]:
    """Extract key points from text"""
    # Split text into sentences
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # Find sentences with important keywords
    important_keywords = ['must', 'shall', 'required', 'important', 'agreement', 'contract', 'legal', 'rights', 'obligations']
    key_sentences = []
    
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in important_keywords):
            key_sentences.append(sentence)
    
    # If we don't have enough key sentences, add some of the longest sentences
    if len(key_sentences) < max_points:
        remaining = max_points - len(key_sentences)
        sorted_by_length = sorted(sentences, key=len, reverse=True)
        for sentence in sorted_by_length:
            if sentence not in key_sentences:
                key_sentences.append(sentence)
                remaining -= 1
                if remaining <= 0:
                    break
    
    return key_sentences[:max_points]

def identify_risks(text: str) -> List[str]:
    """Identify potential risks in the text"""
    risk_keywords = [
        'risk', 'liability', 'termination', 'penalty', 'breach', 'sue', 'lawsuit',
        'damage', 'claim', 'litigation', 'conflict', 'dispute', 'deadline',
        'fail', 'default', 'violation', 'responsible', 'obligation'
    ]
    
    risks = []
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in risk_keywords):
            risks.append(sentence)
    
    # Limit to 3 risks to avoid overwhelming
    return risks[:3]

async def analyze_document(file_path: Path) -> Dict[str, Any]:
    """
    Analyze document using available models
    """
    try:
        file_type = file_path.suffix.lower()
        
        # Extract text from document
        if file_type == ".pdf":
            text = await extract_text_from_pdf(file_path)
        elif file_type in [".jpg", ".jpeg", ".png"]:
            text = await extract_text_from_image(file_path)
        else:
            # For text files
            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                text = await f.read()
        
        # Create a summary (first 3 sentences)
        sentences = re.split(r'[.!?]', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10] # Filter out short/empty sentences
        summary = ". ".join(sentences[:3]) + "." if sentences else text[:500] # Use first 3 sentences or fallback to 500 chars
        
        # Extract key points
        key_points = extract_key_points(text)
        
        # Identify risks
        risks = identify_risks(text)
        
        # Extract entities
        entity_list = extract_entities(text)
        
        # Create analysis result
        result = {
            "summary": summary,
            "key_points": key_points,
            "risks": risks or ["No specific risks identified"],
            "entities": entity_list
        }
        
        return result
            
    except Exception as e:
        logger.error(f"Error in document analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None)
):
    try:
        logger.info(f"Starting file upload: {file.filename}")
        
        # Validate file type first
        file_type = file.filename.split(".")[-1].lower() if "." in file.filename else ""
        allowed_types = ["pdf", "doc", "docx", "txt", "jpg", "jpeg", "png"]
        
        if file_type not in allowed_types:
            logger.error(f"Invalid file type: {file_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Create a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        logger.info(f"Saving file to: {file_path}")
        
        # Save the file with progress logging
        try:
            content = await file.read()
            file_size = len(content)
            logger.info(f"File size: {file_size} bytes")
            
            async with aiofiles.open(file_path, 'wb') as out_file:
                await out_file.write(content)
            logger.info("File saved successfully")
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
        
        # Create document record
        document_id = str(len(documents_db) + 1)
        document = {
            "id": document_id,
            "title": title,
            "description": description,
            "file_path": str(file_path),
            "file_type": file_type,
            "status": "uploaded",
            "created_at": datetime.now().isoformat()
        }
        
        documents_db[document_id] = document
        
        # Initialize empty chat history for this document
        document_chat_histories[document_id] = []
        
        logger.info(f"Document record created: {document_id}")
        
        return document
    except HTTPException as he:
        logger.error(f"HTTP Exception during upload: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

@router.post("/{document_id}/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document_endpoint(document_id: str, request: DocumentAnalysisRequest):
    if document_id not in documents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    try:
        document = documents_db[document_id]
        file_path = Path(document["file_path"])
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document file not found"
            )
        
        # Analyze with available model
        analysis_result = await analyze_document(file_path)
        
        # Update document status
        documents_db[document_id]["status"] = "analyzed"
        
        # Store the full analysis for future chats
        documents_db[document_id]["analysis"] = analysis_result
        
        # Return the formatted response
        return {
            "document_id": document_id,
            "summary": analysis_result.get("summary", "No summary available"),
            "key_points": analysis_result.get("key_points", []),
            "risks": analysis_result.get("risks", []),
            "entities": analysis_result.get("entities", []),
            "model": request.model
        }
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{document_id}/chat", response_model=DocumentChatResponse)
async def chat_with_document(document_id: str, request: DocumentChatRequest):
    if document_id not in documents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    document = documents_db[document_id]
    file_path = Path(document["file_path"])
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found"
        )
    
    try:
        # Get chat history for this document
        chat_history = document_chat_histories.get(document_id, [])
        
        # Get file type to determine how to process it
        file_type = document["file_type"]
        
        # Extract text from document for context
        if file_type.lower() == "pdf":
            document_text = await extract_text_from_pdf(file_path)
        elif file_type.lower() in ["jpg", "jpeg", "png"]:
            document_text = await extract_text_from_image(file_path)
        else:
            # For text files
            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                document_text = await f.read()
        
        # Generate a response based on the query and document content
        # This is a simple implementation that looks for matching sentences
        query = request.query.lower()
        query_keywords = query.split()
        
        # Find sentences that match keywords in the query
        sentences = re.split(r'[.!?]', document_text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        matching_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in query_keywords):
                matching_sentences.append(sentence)
        
        # Generate response
        if matching_sentences:
            response_text = "I found the following relevant information in the document:\n\n"
            for i, sentence in enumerate(matching_sentences[:3], 1):
                response_text += f"{i}. {sentence}\n\n"
        else:
            # Fall back to document analysis if available
            if "analysis" in document:
                analysis = document["analysis"]
                response_text = f"I couldn't find specific information about your query, but here's a summary of the document:\n\n{analysis.get('summary', '')}"
                
                if analysis.get('key_points'):
                    response_text += "\n\nKey points:\n"
                    for point in analysis.get('key_points'):
                        response_text += f"- {point}\n"
            else:
                response_text = "I couldn't find specific information related to your query in this document."
        
        # Add the messages to history
        chat_history.append({"role": "user", "content": request.query})
        chat_history.append({"role": "assistant", "content": response_text})
        
        # Update the chat history
        document_chat_histories[document_id] = chat_history
        
        # Create response
        return {
            "document_id": document_id,
            "response": response_text,
            "messages": chat_history
        }
        
    except Exception as e:
        logger.error(f"Error in document chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )

@router.get("/{document_id}/chat_history", response_model=List[ChatMessage])
async def get_chat_history(document_id: str):
    if document_id not in documents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Return the chat history for this document
    return document_chat_histories.get(document_id, [])

@router.get("/", response_model=List[DocumentResponse])
async def get_documents():
    return list(documents_db.values())

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    if document_id not in documents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return documents_db[document_id]
