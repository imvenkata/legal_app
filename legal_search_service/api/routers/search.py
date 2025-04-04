import logging
from fastapi import APIRouter, HTTPException, Body
from typing import List

# Use absolute-style imports
from legal_search_service.api.schemas import (
    SearchQuery, SearchResponse, RagQuery, RagResponse, RagCitation, SearchResultItem
)
from legal_search_service.search.retrieval import perform_semantic_search
# Import the generation function
from legal_search_service.search.generation import generate_answer_with_citations

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post(
    "/search", 
    response_model=SearchResponse,
    summary="Perform Semantic Search",
    description="Accepts a query and returns semantically relevant document chunks from the vector database."
)
def search_documents(query: SearchQuery = Body(...)):
    """
    Endpoint to perform semantic search.
    """
    try:
        logger.info(f"Received search request: query='{query.query}', top_k={query.top_k}")
        results = perform_semantic_search(query=query.query, top_k=query.top_k)
        return SearchResponse(results=results)
    except Exception as e:
        logger.error(f"Error during search endpoint processing: {e}", exc_info=True)
        # Return a generic 500 error to the client
        raise HTTPException(status_code=500, detail="An internal server error occurred during search.")

# --- RAG Query Endpoint --- 
@router.post(
    "/query", 
    response_model=RagResponse,
    summary="Ask a Legal Question (RAG)",
    description="Accepts a question, retrieves relevant documents, and generates a cited answer using an LLM."
)
def ask_question(query: RagQuery = Body(...)):
    """
    Endpoint to perform Retrieval-Augmented Generation (RAG).
    """
    try:
        # 1. Retrieve context
        safe_question_snippet = query.question[:100].replace('\n', ' ')
        logger.info(f"Received RAG query: '{safe_question_snippet}...', retrieving {query.top_k_retrieval} chunks.")
        
        # Ensure retrieval returns SearchResultItem instances or dicts convertible to it
        retrieved_context: List[SearchResultItem] = perform_semantic_search(
            query=query.question, # Use the question as the search query
            top_k=query.top_k_retrieval
        )
        
        if not retrieved_context:
             logger.warning(f"No context found for query: {safe_question_snippet}...")
             # Let generation handle empty context for a potentially more informative message

        # 2. Generate answer using context
        generated_result = generate_answer_with_citations(
            question=query.question,
            context=retrieved_context # Pass the list of SearchResultItem
        )

        # 3. Format and return the RagResponse
        # Ensure citations match the Pydantic model RagCitation 
        formatted_citations = []
        for citation_data in generated_result.get("citations", []):
            if isinstance(citation_data, RagCitation):
                formatted_citations.append(citation_data)
            elif isinstance(citation_data, dict): # Handle case where generation returns dicts
                try:
                    formatted_citations.append(RagCitation(**citation_data))
                except Exception as validation_error:
                    logger.warning(f"Skipping invalid citation data: {citation_data}. Error: {validation_error}")
            else:
                 logger.warning(f"Skipping unexpected citation format: {type(citation_data)}")

        return RagResponse(
            answer=generated_result.get("answer", "Error: No answer generated."),
            citations=formatted_citations
        )

    except Exception as e:
        logger.error(f"Error during RAG query endpoint processing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred while generating the answer.")
