import os
import sys
import logging
from pathlib import Path
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
logger.info(f"Upload directory: {UPLOAD_DIR.absolute()}")

def save_file(file_path, content):
    """Save a file to the uploads directory"""
    try:
        with open(file_path, 'wb') as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        return False

def main():
    """Simple file upload test"""
    # Create a test file
    test_content = b"This is a test document for analysis."
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    test_filename = f"{timestamp}_test_document.txt"
    file_path = UPLOAD_DIR / test_filename
    
    # Save the file
    if save_file(file_path, test_content):
        logger.info(f"Successfully saved test file to {file_path}")
        
        # Create document record (in real app this would be saved to a database)
        document = {
            "id": "1",
            "title": "Test Document",
            "description": "Automatically created test document",
            "file_path": str(file_path),
            "file_type": "txt",
            "status": "uploaded",
            "created_at": datetime.datetime.now().isoformat()
        }
        
        logger.info(f"Test document created: {document}")
        logger.info("File upload functionality is working correctly")
    else:
        logger.error("Failed to save test file")
        
if __name__ == "__main__":
    main() 