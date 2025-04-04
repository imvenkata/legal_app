from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys
import logging
from pathlib import Path
import datetime
import base64
import io
import re
from typing import List, Dict, Any, Optional
import asyncio
import shutil
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
logger.info(f"Upload directory: {UPLOAD_DIR.absolute()}")

# Create the FastAPI app
app = FastAPI(title="Simple Document API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class DocumentResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    file_path: str
    file_type: str
    status: str
    created_at: str

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

# In-memory database for documents
documents_db = {}

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

@app.get("/")
async def root():
    return {"message": "Simple Document API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/documents/upload", response_model=DocumentResponse)
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
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Create a unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        logger.info(f"Saving file to: {file_path}")
        
        # Save the file
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            logger.info("File saved successfully")
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise HTTPException(
                status_code=500,
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
            "created_at": datetime.datetime.now().isoformat()
        }
        
        documents_db[document_id] = document
        logger.info(f"Document record created: {document_id}")
        
        return document
    except HTTPException as he:
        logger.error(f"HTTP Exception during upload: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

@app.post("/api/documents/{document_id}/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document(document_id: str):
    if document_id not in documents_db:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
    
    try:
        document = documents_db[document_id]
        file_path = Path(document["file_path"])
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Document file not found"
            )
        
        # Analyze document
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        
        # Create a summary
        summary = text[:200] + "..." if len(text) > 200 else text
        
        # Extract key points
        key_points = extract_key_points(text)
        
        # Identify risks
        risks = identify_risks(text)
        
        # Extract entities
        entity_list = extract_entities(text)
        
        # Create analysis result
        analysis_result = {
            "summary": summary,
            "key_points": key_points,
            "risks": risks or ["No specific risks identified"],
            "entities": entity_list
        }
        
        # Update document status
        documents_db[document_id]["status"] = "analyzed"
        documents_db[document_id]["analysis"] = analysis_result
        
        # Return the formatted response
        return {
            "document_id": document_id,
            "summary": analysis_result.get("summary", "No summary available"),
            "key_points": analysis_result.get("key_points", []),
            "risks": analysis_result.get("risks", []),
            "entities": analysis_result.get("entities", []),
            "model": "document-analyzer"
        }
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/api/documents", response_model=List[DocumentResponse])
async def get_documents():
    return list(documents_db.values())

@app.get("/api/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    if document_id not in documents_db:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
    return documents_db[document_id]

if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 3001))
        logger.info(f"Starting server on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        sys.exit(1) 