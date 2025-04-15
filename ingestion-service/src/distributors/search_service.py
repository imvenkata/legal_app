import os
import logging
import aiohttp
import json
from typing import Dict, Any, Optional

from src.core.schemas import ProcessedDocument

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get service URL from environment
SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL", "http://localhost:8004")

async def index_document(document: ProcessedDocument) -> Optional[str]:
    """
    Index a processed document in the search service.
    
    Args:
        document: The processed document
    
    Returns:
        Document ID from the search service, or None if indexing failed
    """
    logger.info(f"Indexing document in search service: {document.task_id}")
    
    try:
        # Prepare document data for indexing
        doc_data = {
            "document_id": document.document_id,  # ID from document service
            "title": document.title,
            "content": document.text_content,
            "metadata": {
                "description": document.description,
                "filename": document.filename,
                "authors": document.metadata.authors,
                "created_date": document.metadata.created_date,
                "modified_date": document.metadata.modified_date,
                "language": document.metadata.language,
                "page_count": document.metadata.page_count,
                "content_type": document.metadata.content_type,
                "ocr_applied": document.ocr_applied
            },
            "tags": document.tags,
            "user_id": document.user_id
        }
        
        # Make request to search service
        async with aiohttp.ClientSession() as session:
            url = f"{SEARCH_SERVICE_URL}/api/v1/documents"
            
            # Add JWT token header
            headers = {
                "Content-Type": "application/json",
                # In a real implementation, this would be a real token
                # We'd need to either have a service token or impersonate the user
                "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
            }
            
            async with session.post(url, json=doc_data, headers=headers) as response:
                if response.status in (200, 201):
                    result = await response.json()
                    logger.info(f"Document indexed in search service with ID: {result.get('id')}")
                    return result.get('id')
                else:
                    error_text = await response.text()
                    logger.error(f"Error indexing document: {response.status}, {error_text}")
                    return None
    
    except Exception as e:
        logger.error(f"Error in index_document: {str(e)}")
        return None 