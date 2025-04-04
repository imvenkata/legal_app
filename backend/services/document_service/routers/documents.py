from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
import os
import uuid
from datetime import datetime

from ...common.database.connection import get_db
from ...common.models.schemas import Document, DocumentCreate, DocumentAnalysisResult
from ...llm_adapter.adapters.base_adapter import LlmAdapter
from ...llm_adapter.factory import get_llm_adapter

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)

# Document upload endpoint
@router.post("/upload", response_model=Document, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    user_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload a document for processing
    """
    # Create a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Define the upload directory
    upload_dir = os.path.join("uploads", "documents")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(upload_dir, unique_filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Create document record
    document = Document(
        id=str(uuid.uuid4()),
        title=title,
        description=description,
        user_id=user_id,
        file_path=file_path,
        file_type=file_extension.lstrip('.'),
        status="uploaded",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Save to database
    # In a real implementation, you would use SQLAlchemy ORM
    # For now, we'll just return the document
    
    return document

# Document analysis endpoint
@router.post("/{document_id}/analyze", response_model=DocumentAnalysisResult)
async def analyze_document(
    document_id: str,
    llm_model: str = Form("gpt-4"),
    db: Session = Depends(get_db)
):
    """
    Analyze a document using the specified LLM model
    """
    # In a real implementation, you would retrieve the document from the database
    # For now, we'll assume the document exists and has a file_path
    
    # Mock document retrieval
    document = Document(
        id=document_id,
        title="Sample Document",
        description="Sample Description",
        user_id="user123",
        file_path="uploads/documents/sample.pdf",
        file_type="pdf",
        status="uploaded",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Check if document exists
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if file exists
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="Document file not found")
    
    # Extract text from document
    # In a real implementation, you would use appropriate libraries based on file type
    # For now, we'll assume we have the text
    document_text = "This is a sample document text for analysis."
    
    # Get LLM adapter
    llm_adapter = get_llm_adapter(llm_model)
    
    # Initialize adapter
    await llm_adapter.initialize(
        api_key="your-api-key",  # In production, retrieve from secure storage
        model_params={"model": llm_model}
    )
    
    # Analyze document
    analysis_result = await llm_adapter.analyze_document(document_text)
    
    # Create analysis result
    result = DocumentAnalysisResult(
        document_id=document_id,
        entities=analysis_result.get("entities", []),
        summary=analysis_result.get("summary", ""),
        risk_factors=analysis_result.get("risks", []),
        recommendations=analysis_result.get("recommendations", [])
    )
    
    # Update document status
    document.status = "analyzed"
    document.updated_at = datetime.now()
    
    # In a real implementation, you would save the analysis result to the database
    
    return result

# Get document by ID endpoint
@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a document by ID
    """
    # In a real implementation, you would retrieve the document from the database
    # For now, we'll return a mock document
    
    document = Document(
        id=document_id,
        title="Sample Document",
        description="Sample Description",
        user_id="user123",
        file_path="uploads/documents/sample.pdf",
        file_type="pdf",
        status="analyzed",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

# Get all documents endpoint
@router.get("/", response_model=List[Document])
async def get_documents(
    user_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all documents, optionally filtered by user ID
    """
    # In a real implementation, you would retrieve documents from the database
    # For now, we'll return a list of mock documents
    
    documents = [
        Document(
            id=str(uuid.uuid4()),
            title=f"Sample Document {i}",
            description=f"Sample Description {i}",
            user_id="user123",
            file_path=f"uploads/documents/sample{i}.pdf",
            file_type="pdf",
            status="analyzed",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        for i in range(1, 6)
    ]
    
    # Filter by user ID if provided
    if user_id:
        documents = [doc for doc in documents if doc.user_id == user_id]
    
    # Apply pagination
    documents = documents[skip:skip+limit]
    
    return documents

# Delete document endpoint
@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a document
    """
    # In a real implementation, you would retrieve and delete the document from the database
    # For now, we'll just return a success response
    
    return None
