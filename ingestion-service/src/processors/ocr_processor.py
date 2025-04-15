import os
import logging
from typing import Dict, Any, Tuple
import asyncio
import tempfile
import subprocess
from pathlib import Path
import pytesseract
from PIL import Image
import numpy as np
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def apply_ocr_if_needed(file_path: str, mime_type: str) -> Tuple[str, bool]:
    """
    Apply OCR to a file if it's an image or if text extraction failed.
    
    Args:
        file_path: Path to the file
        mime_type: MIME type of the file
    
    Returns:
        Tuple of (extracted text, whether OCR was applied)
    """
    logger.info(f"Checking if OCR is needed for file: {file_path}, MIME type: {mime_type}")
    
    # If it's an image, apply OCR
    if mime_type.startswith('image/'):
        logger.info(f"Applying OCR to image: {file_path}")
        text = await extract_text_with_ocr(file_path)
        return text, True
    
    # If it's a PDF, convert to images and apply OCR
    elif mime_type == 'application/pdf':
        logger.info(f"Converting PDF to images and applying OCR: {file_path}")
        text = await extract_text_from_pdf_with_ocr(file_path)
        return text, True
    
    # For other file types, don't apply OCR
    return "", False

async def extract_text_with_ocr(image_path: str) -> str:
    """Extract text from an image using OCR."""
    # This needs to be run in a thread pool to avoid blocking
    return await asyncio.to_thread(_extract_text_with_ocr_sync, image_path)

def _extract_text_with_ocr_sync(image_path: str) -> str:
    """Synchronous function to extract text from an image using OCR."""
    try:
        # Open the image
        img = Image.open(image_path)
        
        # Apply OCR
        text = pytesseract.image_to_string(img)
        
        return text
    except Exception as e:
        logger.error(f"Error applying OCR to image: {str(e)}")
        return ""

async def extract_text_from_pdf_with_ocr(pdf_path: str) -> str:
    """
    Extract text from a PDF by converting to images and applying OCR.
    
    This is useful for scanned PDFs that don't have embedded text.
    """
    try:
        # Create a temporary directory for the images
        with tempfile.TemporaryDirectory() as temp_dir:
            # Convert PDF to images (using poppler tools)
            await _convert_pdf_to_images(pdf_path, temp_dir)
            
            # Apply OCR to each image
            all_text = []
            for img_file in sorted(Path(temp_dir).glob('*.png')):
                text = await extract_text_with_ocr(str(img_file))
                all_text.append(text)
            
            return "\n\n".join(all_text)
    except Exception as e:
        logger.error(f"Error converting PDF and applying OCR: {str(e)}")
        return ""

async def _convert_pdf_to_images(pdf_path: str, output_dir: str) -> None:
    """
    Convert a PDF to a series of PNG images using pdftoppm.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the images
    """
    try:
        # Command to convert PDF to PNG images
        cmd = [
            'pdftoppm',  # This requires poppler-utils to be installed
            '-png',      # Output format
            pdf_path,    # Input PDF
            f"{output_dir}/page"  # Output pattern
        ]
        
        # Run the command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for the process to complete
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Error converting PDF to images: {stderr.decode()}")
            raise Exception(f"PDF conversion failed with code {process.returncode}")
    
    except FileNotFoundError:
        logger.error("pdftoppm command not found. Make sure poppler-utils is installed.")
        raise
    except Exception as e:
        logger.error(f"Error in PDF conversion: {str(e)}")
        raise 