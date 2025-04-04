import logging
import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams
from legal_search_service.config import settings
from .models import get_embedding_model # We need the model to get vector size

logger = logging.getLogger(__name__)

_qdrant_client = None

def get_qdrant_client() -> QdrantClient:
    """Initializes and returns a Qdrant client instance."""
    global _qdrant_client
    if _qdrant_client is None:
        logger.info(f"Initializing Qdrant client for URL: {settings.QDRANT_URL}")
        try:
            _qdrant_client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY, # api_key is optional
                # timeout=None, # Increase timeout if needed
            )
            # Optional: Check connection
            # _qdrant_client.get_collections()
            logger.info("Qdrant client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}", exc_info=True)
            raise
    return _qdrant_client

def create_collection_if_not_exists(collection_name: str = settings.COLLECTION_NAME):
    """Creates the Qdrant collection if it doesn't already exist."""
    client = get_qdrant_client()
    try:
        collections = client.get_collections().collections
        collection_names = [col.name for col in collections]

        if collection_name in collection_names:
            logger.info(f"Collection '{collection_name}' already exists.")
            # Optional: Check if vector params match
            coll_info = client.get_collection(collection_name=collection_name)
            # Updated attribute access based on qdrant-client changes
            current_size = coll_info.config.params.vectors.size
            model = get_embedding_model()
            expected_size = model.get_sentence_embedding_dimension()
            if current_size != expected_size:
                 logger.warning(f"Collection '{collection_name}' exists but vector size mismatch! Expected {expected_size}, found {current_size}. Search might fail.")
            return True

        logger.info(f"Collection '{collection_name}' not found. Creating...")
        model = get_embedding_model()
        vector_size = model.get_sentence_embedding_dimension()
        if not vector_size:
            logger.error("Could not determine vector size from embedding model. Cannot create collection.")
            return False

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE) # Using Cosine distance
            # Add hnsw_config or quantization_config for optimization if needed later
        )
        logger.info(f"Successfully created collection '{collection_name}' with vector size {vector_size}.")
        return True

    except Exception as e:
        logger.error(f"Failed to create or verify collection '{collection_name}': {e}", exc_info=True)
        return False

def upsert_embeddings(embeddings: List[List[float]], chunks: List[Dict[str, Any]], collection_name: str = settings.COLLECTION_NAME):
    """
    Upserts embeddings and associated chunk data into the specified Qdrant collection.
    Each point will be assigned a unique UUID.

    Args:
        embeddings: List of vector embeddings.
        chunks: List of chunk dictionaries (must contain 'metadata' and 'text').
        collection_name: The name of the Qdrant collection.
    """
    client = get_qdrant_client()
    if len(embeddings) != len(chunks):
        logger.error(f"Mismatch between number of embeddings ({len(embeddings)}) and chunks ({len(chunks)}). Aborting upsert.")
        return

    if not embeddings:
        logger.info("No embeddings to upsert.")
        return

    # Prepare points for Qdrant upsert
    points = []
    for i, chunk in enumerate(chunks):
        # Generate a unique UUID for each point
        point_id = str(uuid.uuid4())
        payload = chunk.get("metadata", {}) # Store metadata in payload
        payload["text"] = chunk.get("text", "") # Store the text itself in the payload
        # Store original chunk ID in payload for reference if needed
        original_chunk_id = chunk.get("id")
        if original_chunk_id:
            payload["original_chunk_id"] = original_chunk_id

        # No longer need to check for chunk.get("id") as we generate UUIDs

        points.append(models.PointStruct(
            id=point_id, # Use the generated UUID
            vector=embeddings[i],
            payload=payload
        ))

    if not points:
        logger.error("No valid points generated for upsert.")
        return

    logger.info(f"Upserting {len(points)} points into collection '{collection_name}'...")
    try:
        # Use wait=True for synchronous operation, easier for scripts
        # Consider wait=False and handling async for API calls
        client.upsert(
            collection_name=collection_name,
            points=points,
            wait=True
        )
        logger.info(f"Successfully upserted {len(points)} points.")
    except Exception as e:
        logger.error(f"Failed to upsert points into collection '{collection_name}': {e}", exc_info=True)
