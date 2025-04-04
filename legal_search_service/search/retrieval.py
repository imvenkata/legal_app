import logging
from typing import List, Dict, Any
from qdrant_client import models

# Use absolute-style imports
from legal_search_service.config import settings
from legal_search_service.embedding.models import generate_embeddings
from legal_search_service.embedding.vector_store import get_qdrant_client
from legal_search_service.api.schemas import SearchResultItem # Use the response schema

logger = logging.getLogger(__name__)

def perform_semantic_search(query: str, top_k: int) -> List[SearchResultItem]:
    """
    Performs semantic search using vector similarity in Qdrant.

    Args:
        query: The search query string.
        top_k: The maximum number of results to return.

    Returns:
        A list of SearchResultItem objects.
    """
    logger.info(f"Performing semantic search for query: '{query[:100]}...' with top_k={top_k}")

    # 1. Generate embedding for the query
    query_embedding = generate_embeddings([query])
    if not query_embedding:
        logger.error("Failed to generate embedding for the query.")
        return []

    # 2. Get Qdrant client and perform search
    client = get_qdrant_client()
    collection_name = settings.COLLECTION_NAME

    try:
        search_result = client.search(
            collection_name=collection_name,
            query_vector=query_embedding[0], # Use the first (and only) embedding
            query_filter=None, # Add filters here later if needed
            limit=top_k,
            with_payload=True # Include payload (metadata and text)
        )
        logger.info(f"Qdrant search returned {len(search_result)} results.")

        # 3. Format results into SearchResultItem objects
        formatted_results = []
        for hit in search_result:
            payload = hit.payload if hit.payload else {}
            formatted_results.append(
                SearchResultItem(
                    id=hit.id,
                    score=hit.score,
                    text=payload.get("text", ""), # Extract text from payload
                    metadata=payload # Pass the whole payload as metadata (excluding text)
                )
            )
            # Clean up metadata - remove text field if it exists to avoid duplication
            if "text" in formatted_results[-1].metadata:
                del formatted_results[-1].metadata["text"]

        return formatted_results

    except Exception as e:
        logger.error(f"Error during Qdrant search in collection '{collection_name}': {e}", exc_info=True)
        return []

# --- Placeholder for Hybrid Search --- 
# def perform_hybrid_search(query: str, top_k: int):
#     # 1. Perform semantic search (as above)
#     # 2. Perform full-text search (e.g., using Qdrant payload indexing or Elasticsearch)
#     # 3. Combine and re-rank results
#     pass
