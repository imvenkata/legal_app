import os
import time
from celery import Celery
from typing import Dict, Any, Optional
import json
import logging
import traceback

from .schemas import IngestRequest, ProcessingStatus
from ..pipeline.manager import process_document_worker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get configurations from environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

# Create Celery application
celery_app = Celery(
    "ingestion_worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,  # Process one task at a time
    task_acks_late=True,  # Acknowledge tasks after execution
    task_reject_on_worker_lost=True,  # Requeue tasks if worker is lost
    task_track_started=True  # Track when tasks are started
)

# Define tasks
@celery_app.task(name="process_document", bind=True)
def process_document_task(self, request_dict: Dict[str, Any], file_path: str) -> Dict[str, Any]:
    """
    Celery task to process a document.
    
    Args:
        request_dict: Dictionary representation of IngestRequest
        file_path: Path to the temporary file
    
    Returns:
        Dictionary with processing result
    """
    start_time = time.time()
    logger.info(f"Starting task: {self.request.id}, Task ID: {request_dict.get('task_id')}")
    
    try:
        # Update task status
        self.update_state(state=ProcessingStatus.PROCESSING)
        
        # Convert dict to IngestRequest
        request = IngestRequest(**request_dict)
        
        # Process document
        result = process_document_worker(request, file_path)
        
        # Record processing time
        processing_time = time.time() - start_time
        logger.info(f"Task completed in {processing_time:.2f} seconds: {request.task_id}")
        
        # Return result
        return {
            "status": ProcessingStatus.COMPLETED,
            "task_id": request.task_id,
            "document_id": result.get("document_id"),
            "message": "Document processed successfully",
            "processing_time": processing_time
        }
        
    except Exception as e:
        # Record error
        error_msg = str(e)
        stack_trace = traceback.format_exc()
        logger.error(f"Error processing document: {error_msg}\n{stack_trace}")
        
        # Return error
        return {
            "status": ProcessingStatus.FAILED,
            "task_id": request_dict.get("task_id"),
            "message": "Document processing failed",
            "error": error_msg,
            "processing_time": time.time() - start_time
        } 