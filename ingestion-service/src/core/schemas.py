from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class ProcessingStatus(str, Enum):
    """Enum for document processing status."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class IngestRequest(BaseModel):
    """Model for document ingestion request."""
    task_id: str
    filename: str
    title: str
    description: Optional[str] = None
    tags: List[str] = []
    user_id: int
    extract_text: bool = True
    extract_metadata: bool = True
    ocr_if_needed: bool = True
    priority: int = 1
    batch_id: Optional[str] = None

class IngestResponse(BaseModel):
    """Model for document ingestion response."""
    task_id: str
    status: ProcessingStatus
    message: str
    created_at: str

class IngestBatchRequest(BaseModel):
    """Model for batch ingestion request."""
    batch_id: str
    file_details: List[Dict[str, Any]]
    user_id: int
    extract_text: bool = True
    extract_metadata: bool = True
    ocr_if_needed: bool = True
    priority: int = 1

class IngestBatchResponse(BaseModel):
    """Model for batch ingestion response."""
    batch_id: str
    task_ids: List[str]
    total_documents: int
    status: ProcessingStatus
    message: str
    created_at: str

class ExtractedMetadata(BaseModel):
    """Model for extracted document metadata."""
    title: Optional[str] = None
    authors: List[str] = []
    created_date: Optional[str] = None
    modified_date: Optional[str] = None
    keywords: List[str] = []
    language: Optional[str] = None
    page_count: Optional[int] = None
    content_type: Optional[str] = None
    custom_metadata: Dict[str, Any] = {}

class ProcessedDocument(BaseModel):
    """Model for processed document."""
    task_id: str
    filename: str
    title: str
    description: Optional[str] = None
    text_content: str
    metadata: ExtractedMetadata
    tags: List[str] = []
    user_id: int
    ocr_applied: bool = False
    processing_time: float  # In seconds
    document_id: Optional[str] = None  # ID from document service
    search_id: Optional[str] = None  # ID from search service

class TaskStatusResponse(BaseModel):
    """Model for task status response."""
    task_id: str
    status: ProcessingStatus
    message: str
    user_id: int
    filename: str
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    document_id: Optional[str] = None
    error: Optional[str] = None

class BatchStatusResponse(BaseModel):
    """Model for batch status response."""
    batch_id: str
    task_ids: List[str]
    total_documents: int
    completed: int
    processing: int
    failed: int
    queued: int
    status: ProcessingStatus
    message: str
    created_at: str
    updated_at: str 