import os
import logging
from typing import Dict, Any
import asyncio
import subprocess
from pathlib import Path
import tempfile

# For PDF extraction
try:
    from pypdf import PdfReader
except ImportError:
    # For backward compatibility
    from PyPDF2 import PdfReader

# For DOCX extraction
from docx import Document as DocxDocument

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def extract_text_from_file(file_path: str, mime_type: str) -> str:
    """
    Extract text content from a file based on its MIME type.
    
    Args:
        file_path: Path to the file
        mime_type: MIME type of the file
    
    Returns:
        Extracted text content
    """
    logger.info(f"Extracting text from file: {file_path}, MIME type: {mime_type}")
    
    # Process based on MIME type
    if mime_type == "application/pdf":
        return await extract_text_from_pdf(file_path)
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return await extract_text_from_docx(file_path)
    elif mime_type == "text/plain":
        return await extract_text_from_txt(file_path)
    elif mime_type.startswith("image/"):
        # For images, we don't extract text here - OCR will be applied later if needed
        return ""
    else:
        logger.warning(f"Unsupported MIME type for text extraction: {mime_type}")
        return ""

async def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    # This needs to be run in a thread pool to avoid blocking
    return await asyncio.to_thread(_extract_text_from_pdf_sync, file_path)

def _extract_text_from_pdf_sync(file_path: str) -> str:
    """Synchronous function to extract text from a PDF file."""
    try:
        reader = PdfReader(file_path)
        text_content = []
        
        for page in reader.pages:
            text_content.append(page.extract_text())
        
        return "\n\n".join(text_content)
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return ""

async def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""
    # This needs to be run in a thread pool to avoid blocking
    return await asyncio.to_thread(_extract_text_from_docx_sync, file_path)

def _extract_text_from_docx_sync(file_path: str) -> str:
    """Synchronous function to extract text from a DOCX file."""
    try:
        doc = DocxDocument(file_path)
        text_content = []
        
        for para in doc.paragraphs:
            text_content.append(para.text)
        
        return "\n\n".join(text_content)
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        return ""

async def extract_text_from_txt(file_path: str) -> str:
    """Extract text from a plain text file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error extracting text from TXT: {str(e)}")
        return "" 