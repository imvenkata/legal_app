import logging
import os
from typing import List, Dict, Any
import openai
from fastapi import HTTPException

# Use absolute-style imports
from legal_search_service.api.schemas import SearchResultItem, RagCitation
from legal_search_service.config import settings # Import settings

logger = logging.getLogger(__name__)

# --- Unified LLM Client Initialization --- 
_llm_client = None

def get_llm_client():
    global _llm_client
    if _llm_client is None:
        provider = settings.LLM_PROVIDER.lower()
        logger.info(f"Initializing LLM client for provider: {provider}")
        
        try:
            if provider == "openai":
                api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("Missing OpenAI API Key")
                _llm_client = openai.OpenAI(api_key=api_key)
            
            elif provider == "deepseek":
                api_key = settings.DEEPSEEK_API_KEY or os.getenv("DEEPSEEK_API_KEY")
                if not api_key:
                    raise ValueError("Missing DeepSeek API Key")
                # Use the OpenAI client but point it to the DeepSeek API endpoint
                _llm_client = openai.OpenAI(
                    api_key=api_key,
                    base_url=settings.DEEPSEEK_BASE_URL
                )
            else:
                raise ValueError(f"Unsupported LLM provider specified: {settings.LLM_PROVIDER}")
                
            logger.info(f"LLM client for '{provider}' initialized successfully.")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM client for provider '{provider}': {e}", exc_info=True)
            raise
            
    return _llm_client

def call_llm_chat(system_prompt: str, user_prompt: str) -> str:
    """Calls the configured LLM's chat completions API."""
    client = get_llm_client()
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "openai":
        model = settings.OPENAI_MODEL_NAME
    elif provider == "deepseek":
        model = settings.DEEPSEEK_MODEL_NAME
    else:
        # This case should ideally be caught during client init, but added for safety
        raise ValueError(f"Unsupported LLM provider '{provider}' for model selection.")

    logger.info(f"Calling LLM ({provider}): {model}")
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            # Add other parameters like temperature, max_tokens if needed
        )
        
        if response.choices and response.choices[0].message:
            answer = response.choices[0].message.content
            logger.info(f"Received response from LLM ({provider}).")
            return answer.strip() if answer else ""
        else:
            logger.error(f"LLM ({provider}) response missing expected content.")
            return "Error: Failed to get valid response from LLM."
            
    except openai.APIError as e: # Catches errors for both OpenAI and compatible APIs
        logger.error(f"LLM API ({provider}) returned an API Error: {e}", exc_info=True)
        # Distinguish potential auth errors
        status_code = e.status_code if hasattr(e, 'status_code') else 500
        detail_msg = f"{provider.capitalize()} API Error: {e}"
        if status_code == 401:
             detail_msg = f"Authentication Error with {provider.capitalize()} API. Check your API key."
        raise HTTPException(status_code=status_code, detail=detail_msg) from e
        
    except openai.APIConnectionError as e:
        logger.error(f"Failed to connect to LLM API ({provider}): {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"{provider.capitalize()} Connection Error: {e}") from e
    except openai.RateLimitError as e:
        logger.error(f"LLM API ({provider}) request exceeded rate limit: {e}", exc_info=True)
        raise HTTPException(status_code=429, detail=f"{provider.capitalize()} Rate Limit Error: {e}") from e
    except Exception as e:
        logger.error(f"An unexpected error occurred during LLM ({provider}) call: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected LLM Error: {e}") from e

# --- Renamed placeholder for clarity --- 
def call_openai_llm(*args, **kwargs):
    # This function is deprecated by call_llm_chat
    logger.warning("call_openai_llm is deprecated, use call_llm_chat instead.")
    # Redirect to the new function for backward compatibility if needed, 
    # or remove its usages entirely.
    return call_llm_chat(*args, **kwargs)

# ------------------------------------ 

def format_context(context: List[SearchResultItem]) -> str:
    """Formats the retrieved context chunks into a string for the LLM prompt."""
    snippets = []
    for item in context:
        filename = item.metadata.get('filename', 'N/A')
        text = item.text
        snippets.append(f"Source ID: {item.id}\nSource File: {filename}\nContent: {text}")
    return "\n\n---\n".join(snippets)

def generate_answer_with_citations(
    question: str, 
    context: List[SearchResultItem]
) -> Dict[str, Any]:
    """
    Generates an answer to a question using RAG and attempts citation.

    Args:
        question: The user's question.
        context: List of relevant context chunks (SearchResultItem).

    Returns:
        A dictionary containing the answer and a list of citations.
        e.g., { "answer": "...", "citations": [...] }
    """
    if not context:
        logger.warning("Generation called with no context. Returning generic answer.")
        return { 
            "answer": "I couldn't find relevant documents to answer your question.", 
            "citations": [] 
        }

    formatted_context = format_context(context)
    
    system_prompt = (
        "You are a legal assistant AI. Answer the user's question based *only* on the provided context snippets. "
        "Do not use any prior knowledge. "
        "If the context does not contain the answer, state that you cannot answer based on the provided information. "
        "Be concise and directly answer the question." 
    )
    
    user_prompt = (
        f"**Context Snippets:**\n{formatted_context}\n\n"
        f"**Question:**\n{question}"
    )

    safe_question_snippet = question[:100].replace('\n',' ')
    logger.info(f"Generating answer for question: '{safe_question_snippet}...' using provider: {settings.LLM_PROVIDER}")
    logger.debug(f"System Prompt: {system_prompt}")
    logger.debug(f"User Prompt (truncated):\n{user_prompt[:500]}...")

    # Call the unified LLM chat function
    raw_answer = call_llm_chat(system_prompt=system_prompt, user_prompt=user_prompt)

    # --- Citation Extraction/Generation --- 
    # Create citations based on the retrieved context, including the score and file URL.
    citations = []
    for item in context:
        source_path = item.metadata.get('source') # e.g., 'rawdata/nda.txt'
        file_url = f"/api/v1/documents/{source_path}" if source_path else None
        citations.append(
            RagCitation(
                source=item.metadata.get('filename', source_path or item.id), # Use filename or source path for display
                text_snippet=item.text[:150] + "...",
                score=item.score, 
                file_url=file_url # Add the constructed URL
            )
        )
    # ---------------------------------------------------
    
    logger.info(f"Generated answer (truncated): {raw_answer[:200]}...")
    
    return {
        "answer": raw_answer,
        "citations": citations
    }
