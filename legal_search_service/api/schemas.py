from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SearchQuery(BaseModel):
    query: str = Field(..., description="The search query text.")
    top_k: int = Field(default=5, gt=0, le=50, description="Number of results to return.")
    # Add filter options later if needed (e.g., by date, case number)
    # filters: Optional[Dict[str, Any]] = None

class SearchResultItem(BaseModel):
    id: str = Field(..., description="Unique ID of the retrieved chunk.")
    score: float = Field(..., description="Similarity score of the result.")
    text: str = Field(..., description="The text content of the chunk.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata associated with the chunk.")

class SearchResponse(BaseModel):
    results: List[SearchResultItem] = Field(..., description="List of search results.")

# --- Schemas for RAG Query Endpoint --- 
class RagQuery(BaseModel):
    question: str = Field(..., description="The legal question to answer.")
    top_k_retrieval: int = Field(default=3, gt=0, le=10, description="Number of document chunks to retrieve for context.")
    # Optional: Add parameters for controlling the LLM generation (e.g., model name, temperature)

class RagCitation(BaseModel):
    source: str = Field(..., description="Source identifier (e.g., filename or document ID).")
    text_snippet: str = Field(..., description="Relevant snippet from the source document chunk.")
    score: float = Field(..., description="Original relevance score of the retrieved chunk.")
    file_url: Optional[str] = Field(default=None, description="URL to access the source document.")
    # Optionally add chunk_id etc.

class RagResponse(BaseModel):
    answer: str = Field(..., description="The generated answer to the question.")
    citations: List[RagCitation] = Field(default_factory=list, description="List of cited sources based on retrieved context.")
    # Optionally return the raw retrieved context for debugging/display
    # retrieved_context: List[SearchResultItem] = Field(default_factory=list, description="Raw retrieved context used for generation.")

# --- Schemas for Document Upload --- 
class UploadResponse(BaseModel):
    message: str = Field(..., description="Status message for the upload process.")
    filenames: List[str] = Field(default_factory=list, description="List of filenames received.")
    detail: Optional[str] = Field(default=None, description="Additional details, e.g., background task info.")
