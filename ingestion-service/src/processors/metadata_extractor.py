import os
import logging
from typing import Dict, Any
import asyncio
from datetime import datetime
import langdetect
from pathlib import Path

# For PDF extraction
try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

# For DOCX extraction
from docx import Document as DocxDocument
from docx.document import Document
from docx.core import DocumentCore

from src.core.schemas import ExtractedMetadata

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def extract_metadata_from_file(file_path: str, mime_type: str) -> ExtractedMetadata:
    """
    Extract metadata from a file based on its MIME type.
    
    Args:
        file_path: Path to the file
        mime_type: MIME type of the file
    
    Returns:
        ExtractedMetadata object
    """
    logger.info(f"Extracting metadata from file: {file_path}, MIME type: {mime_type}")
    
    # Process based on MIME type
    if mime_type == "application/pdf":
        return await extract_metadata_from_pdf(file_path)
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return await extract_metadata_from_docx(file_path)
    else:
        # For other file types, extract basic metadata
        return await extract_basic_metadata(file_path, mime_type)

async def extract_metadata_from_pdf(file_path: str) -> ExtractedMetadata:
    """Extract metadata from a PDF file."""
    # This needs to be run in a thread pool to avoid blocking
    return await asyncio.to_thread(_extract_metadata_from_pdf_sync, file_path)

def _extract_metadata_from_pdf_sync(file_path: str) -> ExtractedMetadata:
    """Synchronous function to extract metadata from a PDF file."""
    try:
        reader = PdfReader(file_path)
        info = reader.metadata
        
        # Extract basic metadata
        title = info.title if info and hasattr(info, 'title') else None
        authors = [info.author] if info and hasattr(info, 'author') and info.author else []
        created_date = info.creation_date if info and hasattr(info, 'creation_date') else None
        modified_date = info.modification_date if info and hasattr(info, 'modification_date') else None
        
        # Convert dates to string format if they exist
        if created_date:
            created_date = created_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        if modified_date:
            modified_date = modified_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            
        # Extract keywords
        keywords = []
        if info and hasattr(info, 'keywords') and info.keywords:
            kw = info.keywords
            if isinstance(kw, str):
                # Split keywords by comma or semicolon
                keywords = [k.strip() for k in kw.replace(';', ',').split(',')]
        
        # Count pages
        page_count = len(reader.pages)
        
        # Detect language (from first page)
        language = None
        if reader.pages and len(reader.pages) > 0:
            first_page_text = reader.pages[0].extract_text()
            if first_page_text and len(first_page_text) > 50:
                try:
                    language = langdetect.detect(first_page_text)
                except:
                    pass
        
        return ExtractedMetadata(
            title=title,
            authors=authors,
            created_date=created_date,
            modified_date=modified_date,
            keywords=keywords,
            language=language,
            page_count=page_count,
            content_type="application/pdf"
        )
    except Exception as e:
        logger.error(f"Error extracting metadata from PDF: {str(e)}")
        return ExtractedMetadata(content_type="application/pdf")

async def extract_metadata_from_docx(file_path: str) -> ExtractedMetadata:
    """Extract metadata from a DOCX file."""
    # This needs to be run in a thread pool to avoid blocking
    return await asyncio.to_thread(_extract_metadata_from_docx_sync, file_path)

def _extract_metadata_from_docx_sync(file_path: str) -> ExtractedMetadata:
    """Synchronous function to extract metadata from a DOCX file."""
    try:
        doc = DocxDocument(file_path)
        core_props = doc.core_properties
        
        # Extract basic metadata
        title = core_props.title
        authors = core_props.author.split(';') if core_props.author else []
        created_date = core_props.created.strftime('%Y-%m-%dT%H:%M:%SZ') if core_props.created else None
        modified_date = core_props.modified.strftime('%Y-%m-%dT%H:%M:%SZ') if core_props.modified else None
        
        # Extract keywords
        keywords = core_props.keywords.split(',') if core_props.keywords else []
        
        # Count paragraphs as a proxy for page count (not accurate)
        page_count = None
        
        # Detect language from text
        language = None
        text = '\n'.join([p.text for p in doc.paragraphs if p.text])
        if text and len(text) > 50:
            try:
                language = langdetect.detect(text)
            except:
                pass
        
        return ExtractedMetadata(
            title=title,
            authors=authors,
            created_date=created_date,
            modified_date=modified_date,
            keywords=keywords,
            language=language,
            page_count=page_count,
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        logger.error(f"Error extracting metadata from DOCX: {str(e)}")
        return ExtractedMetadata(
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

async def extract_basic_metadata(file_path: str, mime_type: str) -> ExtractedMetadata:
    """Extract basic metadata common to all file types."""
    try:
        file_stat = os.stat(file_path)
        created_date = datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%dT%H:%M:%SZ')
        modified_date = datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        return ExtractedMetadata(
            title=None,
            authors=[],
            created_date=created_date,
            modified_date=modified_date,
            keywords=[],
            language=None,
            page_count=None,
            content_type=mime_type
        )
    except Exception as e:
        logger.error(f"Error extracting basic metadata: {str(e)}")
        return ExtractedMetadata(content_type=mime_type) 