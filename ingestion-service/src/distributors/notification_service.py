import os
import logging
import aiohttp
import json
from typing import Dict, Any, Optional, List

from src.core.schemas import ProcessedDocument, BatchStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get service URL from environment
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8005")

async def notify_document_processed(document: ProcessedDocument) -> bool:
    """
    Send a notification about a successfully processed document.
    
    Args:
        document: The processed document
    
    Returns:
        True if notification was sent successfully, False otherwise
    """
    logger.info(f"Sending document processed notification for: {document.task_id}")
    
    try:
        notification_data = {
            "type": "document_processed",
            "user_id": document.user_id,
            "data": {
                "document_id": document.document_id,
                "title": document.title,
                "task_id": document.task_id,
                "batch_id": document.batch_id,
                "success": True,
                "timestamp": document.processed_at.isoformat() if document.processed_at else None
            },
            "priority": "normal"
        }
        
        return await _send_notification(notification_data)
    
    except Exception as e:
        logger.error(f"Error in notify_document_processed: {str(e)}")
        return False

async def notify_document_failed(task_id: str, user_id: str, 
                                error_message: str, batch_id: Optional[str] = None) -> bool:
    """
    Send a notification about a failed document processing.
    
    Args:
        task_id: The task ID
        user_id: The user ID
        error_message: The error message
        batch_id: Optional batch ID
        
    Returns:
        True if notification was sent successfully, False otherwise
    """
    logger.info(f"Sending document failed notification for task: {task_id}")
    
    try:
        notification_data = {
            "type": "document_failed",
            "user_id": user_id,
            "data": {
                "task_id": task_id,
                "batch_id": batch_id,
                "success": False,
                "error": error_message,
                "timestamp": None  # We could add current time here
            },
            "priority": "high"
        }
        
        return await _send_notification(notification_data)
    
    except Exception as e:
        logger.error(f"Error in notify_document_failed: {str(e)}")
        return False

async def notify_batch_completed(batch_status: BatchStatus) -> bool:
    """
    Send a notification about a completed batch.
    
    Args:
        batch_status: The batch status object
        
    Returns:
        True if notification was sent successfully, False otherwise
    """
    logger.info(f"Sending batch completed notification for: {batch_status.batch_id}")
    
    try:
        notification_data = {
            "type": "batch_completed",
            "user_id": batch_status.user_id,
            "data": {
                "batch_id": batch_status.batch_id,
                "total_documents": batch_status.total_count,
                "successful_documents": batch_status.success_count,
                "failed_documents": batch_status.failure_count,
                "timestamp": batch_status.completed_at.isoformat() if batch_status.completed_at else None
            },
            "priority": "normal"
        }
        
        return await _send_notification(notification_data)
    
    except Exception as e:
        logger.error(f"Error in notify_batch_completed: {str(e)}")
        return False

async def _send_notification(notification_data: Dict[str, Any]) -> bool:
    """
    Send notification to the notification service.
    
    Args:
        notification_data: The notification data
        
    Returns:
        True if successful, False otherwise
    """
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{NOTIFICATION_SERVICE_URL}/api/v1/notifications"
            
            # Add JWT token header
            headers = {
                "Content-Type": "application/json",
                # In a real implementation, this would be a real token
                "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
            }
            
            async with session.post(url, json=notification_data, headers=headers) as response:
                if response.status in (200, 201, 202):
                    logger.info("Notification sent successfully")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Error sending notification: {response.status}, {error_text}")
                    return False
    
    except Exception as e:
        logger.error(f"Error in _send_notification: {str(e)}")
        return False 