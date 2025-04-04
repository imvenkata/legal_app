import logging
from typing import List, Dict, Any
from transformers import AutoTokenizer # For accurate token counting

logger = logging.getLogger(__name__)

# --- Simple Recursive Character Text Splitter --- 
# Adapted from common patterns, could be replaced by library implementations (e.g., Langchain)

class RecursiveCharacterTextSplitter:
    """Recursively splits text based on a list of separators."""
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, separators: List[str] | None = None, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " ", ""] # Default separators
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            logger.info(f"Tokenizer loaded for model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load tokenizer for {model_name}. Using basic length function. Error: {e}")
            # Fallback to character count if tokenizer fails
            self.tokenizer = None

    def _get_length(self, text: str) -> int:
        """Calculates the length of the text, preferably in tokens."""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            return len(text) # Fallback to character count

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Splits text by the best separator found."""
        final_chunks = []
        separator = separators[-1] # Start with the last, least specific separator
        for sep in separators:
            if sep == "": # Handle the case of empty separator for character splitting
                separator = sep
                break
            if sep in text:
                separator = sep
                break

        if separator:
            splits = text.split(separator)
        else:
            splits = list(text) # Split by character if no separator found

        # Combine small splits
        current_chunk = ""
        for i, split in enumerate(splits):
            # Check if adding the separator back is needed (unless it was empty)
            chunk_to_add = split
            if separator and (i < len(splits) - 1):
                chunk_to_add += separator

            if self._get_length(current_chunk + chunk_to_add) <= self.chunk_size:
                current_chunk += chunk_to_add
            else:
                if current_chunk: # Add the previous chunk if it's not empty
                    final_chunks.append(current_chunk.strip())
                # Start new chunk, handling cases where a single split exceeds chunk_size
                if self._get_length(chunk_to_add) > self.chunk_size:
                    # If a single split is too large, recursively split it further
                    if len(separators) > 1:
                        final_chunks.extend(self._split_text(chunk_to_add, separators[1:]))
                    else:
                        # Cannot split further, add it as is (might be larger than chunk_size)
                        final_chunks.append(chunk_to_add.strip())
                        logger.warning(f"Chunk larger than chunk_size ({self.chunk_size}) created due to indivisible split.")
                    current_chunk = "" # Reset current chunk after handling large split
                else:
                    current_chunk = chunk_to_add # Start the new chunk

        if current_chunk: # Add the last remaining chunk
            final_chunks.append(current_chunk.strip())

        return [chunk for chunk in final_chunks if chunk] # Remove empty chunks

    def split_text(self, text: str) -> List[str]:
        """Splits text using the configured separators and chunk size."""
        return self._split_text(text, self.separators)

    def create_chunks(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Takes a document dictionary and returns a list of chunk dictionaries.
        Each chunk includes the chunk text and inherits metadata, adding chunk info.
        """
        text = document.get("content", "")
        if not text:
            return []

        text_chunks = self.split_text(text)
        chunked_documents = []
        doc_metadata = document.get("metadata", {})
        doc_id = document.get("id", "unknown")

        for i, chunk_text in enumerate(text_chunks):
            chunk_metadata = doc_metadata.copy()
            chunk_metadata.update({
                "doc_id": doc_id, # Link back to the original document
                "chunk_index": i,
                # Add other chunk-specific info if needed (e.g., start/end position)
            })
            chunk_id = f"{doc_id}_chunk_{i}" # Unique ID for the chunk
            chunked_documents.append({
                "id": chunk_id,
                "text": chunk_text,
                "metadata": chunk_metadata
            })

        logger.info(f"Split document '{doc_id}' into {len(chunked_documents)} chunks.")
        return chunked_documents

# --- Placeholder for more advanced/context-aware chunking --- 
# def context_aware_chunking(text: str):
#     # Implementation using sentence boundaries, NLP libraries (spaCy), 
#     # or techniques that preserve citations would go here.
#     pass


