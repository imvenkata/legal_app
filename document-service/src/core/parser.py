import io
import logging
from PyPDF2 import PdfReader
from docx import Document as DocxDocument

async def extract_text_from_content(content: bytes, file_type: str) -> str:
    """
    Extracts text from raw byte content based on file type.
    """
    logging.debug(f"Extracting text from file_type: {file_type}")
    
    # Normalize file_type to handle MIME types
    normalized_type = file_type.lower()
    if "/" in normalized_type:
        # Handle MIME types like application/pdf
        normalized_type = normalized_type.split("/")[-1]
    
    if normalized_type == "pdf":
        try:
            reader = PdfReader(io.BytesIO(content))
            text = "".join(page.extract_text() for page in reader.pages)
            logging.debug(f"Successfully extracted {len(text)} characters from PDF.")
            return text
        except Exception as e:
            logging.error(f"Error reading PDF content: {e}")
            # Fallback or raise specific error
            return content.decode('utf-8', errors='ignore') # Basic fallback
            
    elif normalized_type in ["docx", "vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        try:
            doc = DocxDocument(io.BytesIO(content))
            text = "\n".join([para.text for para in doc.paragraphs])
            logging.debug(f"Successfully extracted {len(text)} characters from DOCX.")
            return text
        except Exception as e:
            logging.error(f"Error reading DOCX content: {e}")
            # Fallback or raise specific error
            return content.decode('utf-8', errors='ignore') # Basic fallback

    elif normalized_type in ["txt", "plain"]:
        try:
            text = content.decode('utf-8')
            logging.debug(f"Successfully decoded TXT content: {len(text)} characters.")
            return text
        except UnicodeDecodeError as e:
             logging.error(f"Error decoding TXT content with UTF-8: {e}, trying latin-1")
             try:
                 # Attempt fallback encoding
                 text = content.decode('latin-1')
                 logging.debug(f"Successfully decoded TXT content with latin-1: {len(text)} characters.")
                 return text
             except Exception as inner_e:
                 logging.error(f"Error decoding TXT content with fallback: {inner_e}")
                 return "" # Return empty if decoding fails
        except Exception as e:
            logging.error(f"Error reading TXT content: {e}")
            return "" # Return empty on other errors

    else:
        logging.warning(f"Unsupported file type for direct text extraction: {file_type} (normalized: {normalized_type}). Attempting basic decode.")
        # Fallback for other types (e.g., try decoding as text)
        try:
             text = content.decode('utf-8', errors='ignore')
             logging.debug(f"Attempted basic decode for {file_type}: {len(text)} characters.")
             return text
        except Exception as e:
            logging.error(f"Could not decode content for file type {file_type}: {e}")
            return "" # Return empty if unknown type and decode fails 