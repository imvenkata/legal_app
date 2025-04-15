from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional
import os

from src.core.auth import get_current_user
from src.core.schemas import (
    TaskStatusResponse,
    BatchStatusResponse,
    ProcessingStatus
)

# In a real implementation, these would be database calls
# For now we'll use an in-memory store for demonstration
task_store = {}

router = APIRouter()

@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get the status of a document processing task.
    """
    # In a real implementation, this would be a database query
    if task_id not in task_store:
        # Just for demonstration - normally we'd check if the task exists
        task_store[task_id] = {
            "task_id": task_id,
            "status": ProcessingStatus.QUEUED,
            "message": "Document is in processing queue",
            "user_id": current_user["id"],
            "filename": "example.pdf",
            "created_at": "2023-07-22T10:30:00Z",
            "updated_at": "2023-07-22T10:30:00Z",
            "completed_at": None,
            "document_id": None,
            "error": None
        }
    
    task = task_store[task_id]
    
    # Check if the user has permission to view this task
    if task["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this task"
        )
    
    return TaskStatusResponse(**task)

@router.get("/batch/{batch_id}", response_model=BatchStatusResponse)
async def get_batch_status(
    batch_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get the status of a batch processing job.
    """
    # In a real implementation, this would be a database query
    # For now, return a dummy response
    return BatchStatusResponse(
        batch_id=batch_id,
        task_ids=["task-123", "task-456"],
        total_documents=2,
        completed=0,
        processing=1,
        failed=0,
        queued=1,
        status=ProcessingStatus.PROCESSING,
        message="Batch is being processed",
        created_at="2023-07-22T10:30:00Z",
        updated_at="2023-07-22T10:31:00Z"
    )

@router.get("/user/tasks", response_model=List[TaskStatusResponse])
async def get_user_tasks(
    status: Optional[ProcessingStatus] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all tasks for the current user.
    """
    # In a real implementation, this would be a database query
    # For now, return a dummy response
    return [
        TaskStatusResponse(
            task_id="task-123",
            status=ProcessingStatus.COMPLETED,
            message="Document processed successfully",
            user_id=current_user["id"],
            filename="example1.pdf",
            created_at="2023-07-21T15:30:00Z",
            updated_at="2023-07-21T15:31:00Z",
            completed_at="2023-07-21T15:31:00Z",
            document_id="doc-123",
            error=None
        ),
        TaskStatusResponse(
            task_id="task-456",
            status=ProcessingStatus.PROCESSING,
            message="Document is being processed",
            user_id=current_user["id"],
            filename="example2.docx",
            created_at="2023-07-22T10:30:00Z",
            updated_at="2023-07-22T10:30:00Z",
            completed_at=None,
            document_id=None,
            error=None
        )
    ]

@router.get("/user/batches", response_model=List[BatchStatusResponse])
async def get_user_batches(
    status: Optional[ProcessingStatus] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all batch jobs for the current user.
    """
    # In a real implementation, this would be a database query
    # For now, return a dummy response
    return [
        BatchStatusResponse(
            batch_id="batch-123",
            task_ids=["task-123", "task-456"],
            total_documents=2,
            completed=1,
            processing=1,
            failed=0,
            queued=0,
            status=ProcessingStatus.PROCESSING,
            message="Batch is being processed",
            created_at="2023-07-22T10:30:00Z",
            updated_at="2023-07-22T10:31:00Z"
        )
    ] 