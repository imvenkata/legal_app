import logging
from pathlib import Path
from llama_parse import LlamaParse
from legal_search_service.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_parser():
    """Initializes and returns the LlamaParse parser."""
    parser_params = {
        "result_type": "text", # Start with text, can explore 'markdown' later
        "verbose": True,
    }
    if settings.LLAMA_CLOUD_API_KEY:
        parser_params["api_key"] = settings.LLAMA_CLOUD_API_KEY
    else:
        # Depending on llama-parse setup, running without an API key might be limited
        # or require local models. Log a warning.
        logger.warning("LLAMA_CLOUD_API_KEY not set. LlamaParse functionality might be limited.")

    # Consider adding language parameter if needed: "language": "en"
    # Consider adding parsing_instruction if needed

    return LlamaParse(**parser_params)


def parse_document(file_path: Path) -> str:
    """
    Parses a document using LlamaParse.

    Args:
        file_path: Path to the document file.

    Returns:
        The extracted text content of the document.
        Returns an empty string if parsing fails.
    """
    logger.info(f"Parsing document: {file_path}")
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return ""

    parser = get_parser()

    try:
        # llama-parse load_data returns a list of Document objects
        documents = parser.load_data(str(file_path))
        if not documents:
            logger.warning(f"LlamaParse returned no documents for: {file_path}")
            return ""
        # Concatenate text from all parsed sub-documents (if any)
        full_text = "\n".join([doc.get_content() for doc in documents])
        logger.info(f"Successfully parsed {len(full_text)} characters from {file_path}")
        return full_text
    except Exception as e:
        logger.error(f"Failed to parse document {file_path}: {e}", exc_info=True)
        return ""

# Example Usage (for testing)
# if __name__ == '__main__':
#     # Make sure you have a .env file with LLAMA_CLOUD_API_KEY if needed
#     # and a sample file in the ../data directory
#     sample_file = Path(__file__).parent.parent / settings.DATA_PATH / "sample.pdf" # Adjust filename
#     if sample_file.exists():
#         text_content = parse_document(sample_file)
#         print("\n--- Parsed Content ---")
#         print(text_content[:1000] + "...") # Print first 1000 chars
#     else:
#         print(f"Sample file not found at {sample_file}, skipping example usage.")
