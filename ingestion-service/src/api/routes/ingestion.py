from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import os
import uuid
from datetime import datetime

from src.core.auth import get_current_user
from src.pipeline.manager import process_document
from src.core.schemas import (
    IngestRequest,
    IngestResponse,
    IngestBatchRequest,
    IngestBatchResponse,
    ProcessingStatus
)

router = APIRouter()

@router.post("/document", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    extract_text: bool = Form(True),
    extract_metadata: bool = Form(True),
    ocr_if_needed: bool = Form(True),
    priority: int = Form(1),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Ingest a document for processing.
    
    The document will be processed asynchronously:
    1. Text extraction (plain text, with formatting information discarded)
    2. Metadata extraction (title, author, creation date, etc.)
    3. OCR if the document is an image or doesn't contain text
    4. Distribution to other services (document-service, search-service)
    
    Returns a task ID that can be used to check the status of the processing.
    """
    # Generate a task ID
    task_id = str(uuid.uuid4())
    
    # Process tags
    tag_list = tags.split(",") if tags else []
    
    # Create request object
    request = IngestRequest(
        task_id=task_id,
        filename=file.filename,
        title=title or file.filename,
        description=description,
        tags=tag_list,
        user_id=current_user["id"],
        extract_text=extract_text,
        extract_metadata=extract_metadata,
        ocr_if_needed=ocr_if_needed,
        priority=priority
    )
    
    # Read file content once
    file_content = await file.read()
    
    # Start background processing
    background_tasks.add_task(
        process_document,
        request=request,
        file_content=file_content
    )
    
    # Return response with task ID
    return IngestResponse(
        task_id=task_id,
        status=ProcessingStatus.QUEUED,
        message="Document queued for processing",
        created_at=datetime.now().isoformat()
    )

@router.post("/batch", response_model=IngestBatchResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_batch(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    extract_text: bool = Form(True),
    extract_metadata: bool = Form(True),
    ocr_if_needed: bool = Form(True),
    priority: int = Form(1),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Ingest a batch of documents for processing.
    
    Each document will be processed asynchronously.
    Returns a list of task IDs that can be used to check the status of each document.
    """
    # Create response
    batch_id = str(uuid.uuid4())
    task_ids = []
    
    # Process each file
    for file in files:
        task_id = str(uuid.uuid4())
        task_ids.append(task_id)
        
        # Create request object
        request = IngestRequest(
            task_id=task_id,
            batch_id=batch_id,
            filename=file.filename,
            title=file.filename,
            tags=[],
            user_id=current_user["id"],
            extract_text=extract_text,
            extract_metadata=extract_metadata,
            ocr_if_needed=ocr_if_needed,
            priority=priority
        )
        
        # Read file content
        file_content = await file.read()
        
        # Start background processing
        background_tasks.add_task(
            process_document,
            request=request,
            file_content=file_content
        )
    
    # Return response with batch information
    return IngestBatchResponse(
        batch_id=batch_id,
        task_ids=task_ids,
        total_documents=len(files),
        status=ProcessingStatus.QUEUED,
        message="Batch queued for processing",
        created_at=datetime.now().isoformat()
    ) 