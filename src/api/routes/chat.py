from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os
from datetime import datetime
import logging

from src.db.session import get_db
from src.db.models import (ChatRequest, ChatResponse, ChatMessageMongo, 
                           DocumentStatus) # Removed User import
# Removed auth import: from src.core.auth import get_current_user_placeholder
from src.core.llm import get_llm_adapter, OpenAIAdapter, DeepSeekAdapter
from src.db import crud, mongo_crud

router = APIRouter()

# Define the same mock user ID as in documents.py
MOCK_USER_ID = "mock_user_id_123"

@router.post("/{document_id}/chat", response_model=ChatResponse)
async def chat_with_document(
    document_id: str,
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
    # Removed: current_user: User = Depends(get_current_user_placeholder)
):
    """
    Chat with a document (authentication disabled).
    """
    user_id = MOCK_USER_ID # Use hardcoded user ID
    session_id = f"{user_id}:{document_id}" 
    logging.info(f"User '{user_id}' starting chat for document {document_id} (session: {session_id})")

    # 1. Get document metadata from SQL
    document = crud.get_document_db(db, document_id, user_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # 2. Check document status
    if document.status != DocumentStatus.PARSING_COMPLETED and document.status != DocumentStatus.ANALYZED:
        # ... (status check logic remains same) ...
        logging.warning(f"Chat requested for doc {document_id} but status is {document.status.value}")
        if document.status in [DocumentStatus.UPLOADED, DocumentStatus.PARSING]:
             detail = "Document is still being processed."
        elif document.status == DocumentStatus.PARSING_FAILED:
             detail = "Cannot chat (parsing failed)."
        else:
             detail = f"Document not ready for chat (status: {document.status.value})."
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    # 3. Get extracted text from MongoDB
    document_text = await mongo_crud.get_parsed_document_text(document_id)
    if document_text is None:
        logging.error(f"Parsed text missing for {document_id} in MongoDB.")
        crud.update_document_status_db(db, document_id, DocumentStatus.ERROR)
        raise HTTPException(status_code=500, detail="Internal error: Parsed content missing.")

    # 4. Load chat history from MongoDB
    chat_session = await mongo_crud.get_chat_session(session_id)
    message_history = []
    if chat_session:
        message_history = [msg.model_dump() for msg in chat_session.messages]
        logging.debug(f"Loaded {len(message_history)} messages for session {session_id}.")
    else:
        logging.debug(f"No existing chat session found for {session_id}.")

    # 5. Prepare messages for LLM
    current_user_message = {"role": "user", "content": chat_request.message}
    llm_messages = message_history + [current_user_message]

    # 6. Call LLM
    llm_adapter = get_llm_adapter()
    api_key = os.getenv("OPENAI_API_KEY")
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
    
    saved_user = await mongo_crud.add_message_to_chat_session(session_id, user_id, document_id, user_message_obj)
    saved_assistant = await mongo_crud.add_message_to_chat_session(session_id, user_id, document_id, assistant_message_obj)

    if not saved_user or not saved_assistant:
        logging.error(f"Failed to save one or both messages to chat session {session_id}.")

    # 8. Return response
    final_messages = (chat_session.messages if chat_session else []) + [user_message_obj, assistant_message_obj]
    
    return ChatResponse(
        document_id=document_id,
        messages=final_messages, 
        created_at=datetime.now()
    ) 