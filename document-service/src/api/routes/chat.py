from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os
from datetime import datetime
import logging

from src.db.session import get_db
from src.db.models import (ChatRequest, ChatResponse, ChatMessageMongo, 
                           DocumentStatus, User) # Use Mongo model for messages
from src.core.auth import get_current_user
from src.core.llm import get_llm_adapter, OpenAIAdapter, DeepSeekAdapter # Keep specific adapters if needed for API key logic
# from src.core.storage import get_storage_service # No longer needed here
from src.db import crud, mongo_crud # Import both CRUD modules

# For testing without auth
MOCK_USER_ID = "123"

router = APIRouter()

@router.post("/{document_id}/chat", response_model=ChatResponse)
async def chat_with_document(
    document_id: str,
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Commented out for testing
):
    """
    Chat with a document. Requires parsing to be completed.
    Uses MongoDB for chat history and parsed text retrieval.
    """
    # Use mock user ID instead of requiring authentication
    user_id = MOCK_USER_ID  # For testing without auth
    session_id = f"{user_id}:{document_id}" # Define chat session ID
    logging.info(f"User {user_id} starting chat for document {document_id} (session: {session_id})")

    # 1. Get document metadata from SQL to check status and authorization
    document = crud.get_document_db(db, document_id, user_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or not authorized")

    # 2. Check document status
    if document.status != DocumentStatus.PARSING_COMPLETED and document.status != DocumentStatus.ANALYZED:
        # Allow chat if parsing is done, even if analysis hasn't run or failed
        logging.warning(f"Chat requested for document {document_id} but status is {document.status.value}")
        if document.status in [DocumentStatus.UPLOADED, DocumentStatus.PARSING]:
             detail = "Document is still being processed. Please try again later."
        elif document.status == DocumentStatus.PARSING_FAILED:
             detail = "Failed to extract text from document. Cannot chat."
        else:
             detail = f"Document not ready for chat (status: {document.status.value})."
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    # 3. Get extracted text from MongoDB
    logging.debug(f"Fetching parsed text for {document_id} from MongoDB for chat context.")
    document_text = await mongo_crud.get_parsed_document_text(document_id)
    if document_text is None:
        logging.error(f"Parsed text for {document_id} not found in MongoDB despite acceptable SQL status ({document.status.value}).")
        crud.update_document_status_db(db, document_id, DocumentStatus.ERROR) # Mark inconsistency
        raise HTTPException(status_code=500, detail="Internal error: Parsed content missing.")

    # 4. Load chat history from MongoDB
    logging.debug(f"Loading chat history for session {session_id} from MongoDB.")
    chat_session = await mongo_crud.get_chat_session(session_id)
    message_history = []
    if chat_session:
        message_history = [msg.model_dump() for msg in chat_session.messages]
        logging.debug(f"Loaded {len(message_history)} messages for session {session_id}.")
    else:
        logging.debug(f"No existing chat session found for {session_id}. Starting new history.")

    # 5. Prepare messages for LLM (history + current user message)
    current_user_message = {"role": "user", "content": chat_request.message}
    llm_messages = message_history + [current_user_message]

    # 6. Call LLM
    llm_adapter = get_llm_adapter() # Using default adapter
    api_key = os.getenv("OPENAI_API_KEY") # Simplified API key logic
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM API key not configured.")

    try:
        await llm_adapter.initialize(api_key=api_key)
        logging.info(f"Sending chat request to LLM for session {session_id}...")
        assistant_response_content = await llm_adapter.chat(
            messages=llm_messages, 
            document_context=document_text
        )
        logging.info(f"Received LLM response for session {session_id}.")

    except Exception as e:
        logging.exception(f"LLM chat API error for session {session_id}: {e}")
        raise HTTPException(status_code=502, detail=f"Error communicating with LLM: {e}")

    # 7. Save messages to MongoDB chat history
    user_message_obj = ChatMessageMongo(role="user", content=chat_request.message)
    assistant_message_obj = ChatMessageMongo(role="assistant", content=assistant_response_content)
    
    logging.debug(f"Saving user message to session {session_id}...")
    saved_user = await mongo_crud.add_message_to_chat_session(session_id, user_id, document_id, user_message_obj)
    logging.debug(f"Saving assistant message to session {session_id}...")
    saved_assistant = await mongo_crud.add_message_to_chat_session(session_id, user_id, document_id, assistant_message_obj)

    if not saved_user or not saved_assistant:
        # Log error, but proceed to return response to user if LLM call succeeded
        logging.error(f"Failed to save one or both messages to chat session {session_id} in MongoDB.")

    # 8. Return response including the latest exchange
    # Fetch the updated history to be absolutely sure, though less efficient
    # updated_session = await mongo_crud.get_chat_session(session_id)
    # final_messages = updated_session.messages if updated_session else [user_message_obj, assistant_message_obj]
    # More efficiently, just append the new messages to the loaded history:
    final_messages = (chat_session.messages if chat_session else []) + [user_message_obj, assistant_message_obj]
    
    # Convert datetime objects to strings to satisfy the response model
    for msg in final_messages:
        if hasattr(msg, 'created_at') and isinstance(msg.created_at, datetime):
            msg.created_at = msg.created_at.isoformat()
    
    return ChatResponse(
        document_id=document_id,
        messages=final_messages, 
        created_at=datetime.now().isoformat() # Convert datetime to string
    ) 