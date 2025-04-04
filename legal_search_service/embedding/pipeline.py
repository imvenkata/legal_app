import logging
from typing import List, Dict, Any

# Use absolute-style imports
from legal_search_service.config import settings
from legal_search_service.embedding.chunking import RecursiveCharacterTextSplitter
from legal_search_service.embedding.models import generate_embeddings
from legal_search_service.embedding.vector_store import create_collection_if_not_exists, upsert_embeddings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_embedding_pipeline(documents: List[Dict[str, Any]]):
    """
    Runs the embedding pipeline:
    1. Initializes text splitter.
    2. Chunks documents.
    3. Generates embeddings for chunks.
    4. Ensures Qdrant collection exists.
    5. Upserts embeddings and chunk data into Qdrant.
    """
    if not documents:
        logger.warning("Embedding pipeline received no documents. Skipping.")
        return

    logger.info(f"Starting embedding pipeline for {len(documents)} document(s).")

    # 1. Initialize Text Splitter
    # TODO: Make chunk_size, chunk_overlap configurable
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=150, 
        model_name=settings.EMBEDDING_MODEL_NAME
    )

    # 2. Chunk Documents
    all_chunks = []
    for doc in documents:
        chunks = text_splitter.create_chunks(doc)
        all_chunks.extend(chunks)

    if not all_chunks:
        logger.warning("No chunks were created from the documents. Aborting embedding.")
        return

    logger.info(f"Created a total of {len(all_chunks)} chunks.")

    # 3. Generate Embeddings
    chunk_texts = [chunk['text'] for chunk in all_chunks]
    embeddings = generate_embeddings(chunk_texts)

    if embeddings is None or len(embeddings) != len(all_chunks):
        logger.error("Failed to generate embeddings or mismatch in embedding count. Aborting upsert.")
        return

    # 4. Ensure Qdrant Collection Exists
    collection_created = create_collection_if_not_exists()
    if not collection_created:
        logger.error(f"Failed to create or verify Qdrant collection '{settings.COLLECTION_NAME}'. Aborting upsert.")
        return

    # 5. Upsert Embeddings
    upsert_embeddings(embeddings=embeddings, chunks=all_chunks)

    logger.info("Embedding pipeline finished successfully.")

# Example Usage (called from ingestion pipeline)
