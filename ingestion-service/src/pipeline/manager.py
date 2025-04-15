import os
import logging
import tempfile
import time
import aiofiles
from typing import Dict, Any, Optional, BinaryIO
import asyncio
import magic
import json

from src.core.schemas import IngestRequest, ProcessingStatus, ProcessedDocument, ExtractedMetadata
from src.processors.text_extractor import extract_text_from_file
from src.processors.metadata_extractor import extract_metadata_from_file
from src.processors.ocr_processor import apply_ocr_if_needed
from src.distributors.document_service import store_document
from src.distributors.search_service import index_document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def process_document(request: IngestRequest, file_content: bytes) -> Dict[str, Any]:
    """
    Process a document for the API endpoint.
    
    This is the async version for the FastAPI endpoint.
    It saves the file to a temporary location and then calls the Celery task.
    
    Args:
        request: The ingestion request
        file_content: The raw file content
    
    Returns:
        Dictionary with processing result
    """
    # Save file to temporary location
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{request.filename}")
    temp_path = temp_file.name
    
    try:
        # Write content to file
        async with aiofiles.open(temp_path, "wb") as f:
            await f.write(file_content)
        
        # For now, we'll just simulate the processing
        # In a real implementation, this would call the Celery task
        logger.info(f"Document queued for processing: {request.task_id}")
        
        # Start processing in background
        # This would normally be handled by the Celery worker
        asyncio.create_task(_process_document_background(request, temp_path))
        
        return {
            "task_id": request.task_id,
            "status": ProcessingStatus.QUEUED,
            "message": "Document queued for processing"
        }
        
    except Exception as e:
        logger.error(f"Error queueing document: {str(e)}")
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise

async def _process_document_background(request: IngestRequest, file_path: str) -> None:
    """Background task to process the document."""
    try:
        # Process the document
        result = await _process_document_internal(request, file_path)
        logger.info(f"Document processed: {request.task_id}, Result: {result}")
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.unlink(file_path)

async def _process_document_internal(request: IngestRequest, file_path: str) -> Dict[str, Any]:
    """Internal function to process the document."""
    start_time = time.time()
    
    # Detect file type
    mime_type = magic.from_file(file_path, mime=True)
    
    # Extract text (if requested)
    text_content = ""
    if request.extract_text:
        text_content = await extract_text_from_file(file_path, mime_type)
    
    # Extract metadata (if requested)
    metadata = ExtractedMetadata()
    if request.extract_metadata:
        metadata = await extract_metadata_from_file(file_path, mime_type)
    
    # Apply OCR if needed and requested
    ocr_applied = False
    if request.ocr_if_needed and not text_content:
        text_content, ocr_applied = await apply_ocr_if_needed(file_path, mime_type)
    
    # Create processed document object
    document = ProcessedDocument(
        task_id=request.task_id,
        filename=request.filename,
        title=request.title or metadata.title or request.filename,
        description=request.description,
        text_content=text_content,
        metadata=metadata,
        tags=request.tags,
        user_id=request.user_id,
        ocr_applied=ocr_applied,
        processing_time=time.time() - start_time,
        document_id=None,
        search_id=None
    )
    
    # Distribute to document service
    document_id = await store_document(document)
    document.document_id = document_id
    
    # Distribute to search service
    search_id = await index_document(document)
    document.search_id = search_id
    
    # Return result
    return {
        "document_id": document_id,
        "search_id": search_id,
        "processing_time": document.processing_time
    }

def process_document_worker(request: IngestRequest, file_path: str) -> Dict[str, Any]:
    """
    Process a document for the Celery worker.
    
    This is the synchronous version for the Celery task.
    
    Args:
        request: The ingestion request
        file_path: Path to the temporary file
    
    Returns:
        Dictionary with processing result
    """
    # This would be the implementation for the Celery worker
    # For now, we'll use a mock implementation
    # In a real implementation, this would process the document synchronously
    
    # Wait a bit to simulate processing
    time.sleep(2)
    
    # Return mock result
    return {
        "document_id": f"doc-{request.task_id}",
        "search_id": f"search-{request.task_id}",
        "processing_time": 2.0
    } 