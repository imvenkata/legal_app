import logging
from typing import List
from sentence_transformers import SentenceTransformer
from legal_search_service.config import settings

logger = logging.getLogger(__name__)

# Global variable to cache the loaded model
_model = None

def get_embedding_model():
    """Loads and returns the Sentence Transformer model based on config."""
    global _model
    if _model is None:
        model_name = settings.EMBEDDING_MODEL_NAME
        logger.info(f"Loading embedding model: {model_name}")
        try:
            # You might need to specify trust_remote_code=True for some models
            _model = SentenceTransformer(model_name)
            logger.info(f"Embedding model '{model_name}' loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load embedding model '{model_name}': {e}", exc_info=True)
            raise
    return _model

def generate_embeddings(texts: List[str]) -> List[List[float]] | None:
    """
    Generates embeddings for a list of texts using the configured model.

    Args:
        texts: A list of text strings.

    Returns:
        A list of embeddings (each embedding is a list of floats), or None if error.
    """
    if not texts:
        return []
    try:
        model = get_embedding_model()
        # The encode method handles batching internally
        logger.info(f"Generating embeddings for {len(texts)} text chunk(s)...")
        embeddings = model.encode(texts, show_progress_bar=True)
        logger.info(f"Successfully generated {len(embeddings)} embeddings.")
        # Convert numpy arrays to lists for JSON serialization / Qdrant
        return embeddings.tolist()
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}", exc_info=True)
        return None

# --- Placeholder for supporting other embedding models --- 
# class EmbeddingModelFactory:
#     def get_model(provider: str, model_name: str):
#         if provider == "sentence-transformers":
#             return SentenceTransformer(model_name)
#         elif provider == "openai":
#             # Import and setup OpenAI client
#             pass
#         elif provider == "gemini":
#             # Import and setup Gemini client
#             pass
#         # etc.
