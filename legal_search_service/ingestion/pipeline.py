import logging
from pathlib import Path
import argparse

# Use absolute-style imports assuming 'legal_search_service' is in PYTHONPATH
from legal_search_service.config import settings
from legal_search_service.ingestion.parsers import parse_document
from legal_search_service.ingestion.preprocess import preprocess_content
# Import the embedding pipeline function
from legal_search_service.embedding.pipeline import run_embedding_pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt"] # Add more as LlamaParse supports them


def run_ingestion(data_directory: Path):
    """
    Runs the ingestion pipeline:
    1. Finds supported documents in the data directory.
    2. Parses each document.
    3. Preprocesses the extracted content.
    4. (Later) Sends preprocessed data to the embedding pipeline.
    """
    logger.info(f"Starting ingestion process for directory: {data_directory}")
    processed_files = 0
    documents_to_embed = [] # Store results for next step

    for file_path in data_directory.rglob('*'): # Use rglob for recursive search
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            logger.info(f"Processing file: {file_path.name}")
            try:
                raw_content = parse_document(file_path)
                if raw_content:
                    preprocessed_content = preprocess_content(raw_content)
                    if preprocessed_content:
                        # For now, just store it. Later, pass to embedding.
                        documents_to_embed.append({
                            "id": str(file_path.relative_to(data_directory)), # Use relative path as ID
                            "content": preprocessed_content,
                            "metadata": { # Basic metadata
                                "source": str(file_path.relative_to(data_directory)),
                                "filename": file_path.name
                                # Add more extracted metadata here later (citations, etc.)
                            }
                        })
                        processed_files += 1
                        logger.info(f"Successfully preprocessed: {file_path.name}")
                        # print(f"--- Preprocessed {file_path.name} ---")
                        # print(preprocessed_content[:500] + "...")
                    else:
                        logger.warning(f"Preprocessing resulted in empty content for: {file_path.name}")
                else:
                    logger.warning(f"Parsing failed or returned empty content for: {file_path.name}")
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
        elif file_path.is_file():
            logger.debug(f"Skipping unsupported file type: {file_path.name}")

    logger.info(f"Ingestion complete. Processed {processed_files} files.")
    logger.info(f"Total documents prepared for embedding: {len(documents_to_embed)}")

    # --- Call the embedding pipeline --- #
    if documents_to_embed:
        logger.info("Proceeding to embedding pipeline...")
        run_embedding_pipeline(documents_to_embed)
    else:
        logger.info("No documents to embed. Skipping embedding pipeline.")
    # ----------------------------------- #

    # For now, just return the list
    # return documents_to_embed # No longer need to return here


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the document ingestion pipeline.")
    parser.add_argument(
        "--data-dir",
        type=str,
        default=settings.DATA_PATH,
        help=f"Directory containing documents to ingest (default: {settings.DATA_PATH})"
    )
    args = parser.parse_args()

    data_path = Path(args.data_dir)
    if not data_path.is_dir():
        logger.error(f"Data directory not found: {data_path}")
        exit(1)

    # Make sure .env is loaded if running as script
    from dotenv import load_dotenv
    load_dotenv()

    # Update settings if key is in environment after load_dotenv
    import os
    if os.getenv("LLAMA_CLOUD_API_KEY"):
        settings.LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")

    run_ingestion(data_path)
