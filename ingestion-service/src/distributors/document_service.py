import os
import logging
import aiohttp
import json
from typing import Dict, Any, Optional
import tempfile
import aiofiles

from src.core.schemas import ProcessedDocument

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get service URL from environment
DOCUMENT_SERVICE_URL = os.getenv("DOCUMENT_SERVICE_URL", "http://localhost:8002")

async def store_document(document: ProcessedDocument) -> Optional[str]:
    """
    Store a processed document in the document service.
    
    Args:
        document: The processed document
    
    Returns:
        Document ID from the document service, or None if storage failed
    """
    logger.info(f"Storing document in document service: {document.task_id}")
    
    try:
        # Create a temporary file containing the text
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(document.text_content.encode('utf-8'))
        
        # Prepare form data
        data = {
            'title': document.title,
            'description': document.description or '',
            'tags': ','.join(document.tags) if document.tags else ''
        }
        
        # Prepare file
        files = {
            'file': (
                document.filename, 
                open(temp_path, 'rb'),
                'text/plain'
            )
        }
        
        # Make request to document service
        async with aiohttp.ClientSession() as session:
            url = f"{DOCUMENT_SERVICE_URL}/api/documents"
            
            # Add JWT token header
            headers = {
                # In a real implementation, this would be a real token
                # We'd need to either have a service token or impersonate the user
                "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
            }
            
            async with session.post(url, data=data, files=files, headers=headers) as response:
                if response.status == 201:
                    result = await response.json()
                    logger.info(f"Document stored in document service with ID: {result.get('id')}")
                    return result.get('id')
                else:
                    error_text = await response.text()
                    logger.error(f"Error storing document: {response.status}, {error_text}")
                    return None
    
    except Exception as e:
        logger.error(f"Error in store_document: {str(e)}")
        return None
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path) 