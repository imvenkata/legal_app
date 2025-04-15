import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pymongo.errors import DuplicateKeyError

from .mongo_session import get_document_collection, get_chat_collection, get_analysis_collection
from .models import ParsedDocumentMongo, ChatSessionMongo, ChatMessageMongo, DocumentAnalysisResult

# --- Parsed Document CRUD --- 

async def save_parsed_document(document_id: str, extracted_text: str):
    """Saves the extracted text for a document in MongoDB."""
    collection = await get_document_collection()
    parsed_doc = ParsedDocumentMongo(
        _id=document_id, # Use SQL document ID as Mongo _id
        document_id=document_id, 
        extracted_text=extracted_text
    )
    doc_dict = parsed_doc.model_dump(by_alias=True) # Use model_dump for Pydantic v2
    
    try:
        # Use replace_one with upsert=True to handle potential reruns/updates
        result = await collection.replace_one({"_id": document_id}, doc_dict, upsert=True)
        if result.upserted_id or result.modified_count > 0:
            logging.info(f"Saved/Updated parsed text for document {document_id} in MongoDB.")
            return True
        elif result.matched_count > 0 and result.modified_count == 0:
            logging.warning(f"Parsed text for document {document_id} already exists and is identical.")
            return True # Already exists, treat as success
        else:
            logging.error(f"Failed to save parsed text for document {document_id} (unknown error).")
            return False
    except Exception as e:
        logging.error(f"Error saving parsed document {document_id} to MongoDB: {e}")
        return False

async def get_parsed_document_text(document_id: str) -> Optional[str]:
    """Retrieves the extracted text for a document from MongoDB."""
    collection = await get_document_collection()
    try:
        doc = await collection.find_one({"_id": document_id})
        if doc:
            # Validate with Pydantic model before returning text
            parsed_doc = ParsedDocumentMongo(**doc)
            logging.debug(f"Retrieved parsed text for document {document_id} from MongoDB.")
            return parsed_doc.extracted_text
        else:
            logging.warning(f"Parsed text not found for document {document_id} in MongoDB.")
            return None
    except Exception as e:
        logging.error(f"Error retrieving parsed document {document_id} from MongoDB: {e}")
        return None
        
async def delete_parsed_document(document_id: str) -> bool:
    """Deletes the parsed document text from MongoDB."""
    collection = await get_document_collection()
    try:
        result = await collection.delete_one({"_id": document_id})
        if result.deleted_count > 0:
            logging.info(f"Deleted parsed text for document {document_id} from MongoDB.")
            return True
        else:
            logging.warning(f"Parsed text for document {document_id} not found for deletion.")
            return False
    except Exception as e:
        logging.error(f"Error deleting parsed document {document_id} from MongoDB: {e}")
        return False

# --- Chat Session CRUD --- 

async def get_chat_session(session_id: str) -> Optional[ChatSessionMongo]:
    """Retrieves a chat session and its messages from MongoDB."""
    collection = await get_chat_collection()
    try:
        session_data = await collection.find_one({"_id": session_id})
        if session_data:
            # Parse and return the full session object
            session = ChatSessionMongo(**session_data)
            logging.debug(f"Retrieved chat session {session_id} from MongoDB.")
            return session
        else:
            logging.debug(f"Chat session {session_id} not found in MongoDB.")
            return None
    except Exception as e:
        logging.error(f"Error retrieving chat session {session_id} from MongoDB: {e}")
        return None

async def add_message_to_chat_session(session_id: str, user_id: str, document_id: str, message: ChatMessageMongo) -> bool:
    """Adds a message to a chat session, creating the session if it doesn't exist."""
    collection = await get_chat_collection()
    message_dict = message.model_dump()
    try:
        result = await collection.update_one(
            {"_id": session_id},
            {
                "$push": {"messages": message_dict},
                "$set": {"updated_at": datetime.now()},
                "$setOnInsert": { # Set these fields only if creating the session
                    "_id": session_id,
                    "user_id": user_id,
                    "document_id": document_id,
                    "created_at": datetime.now()
                }
            },
            upsert=True # Create the session if it doesn't exist
        )
        
        if result.upserted_id or result.modified_count > 0:
            logging.debug(f"Added message to chat session {session_id} in MongoDB.")
            return True
        else:
             logging.error(f"Failed to add message to chat session {session_id} (unknown error).")
             return False
    except Exception as e:
        logging.error(f"Error adding message to chat session {session_id}: {e}")
        return False

async def delete_chat_session(session_id: str) -> bool:
    """Deletes a chat session from MongoDB."""
    collection = await get_chat_collection()
    try:
        result = await collection.delete_one({"_id": session_id})
        if result.deleted_count > 0:
            logging.info(f"Deleted chat session {session_id} from MongoDB.")
            return True
        else:
            logging.warning(f"Chat session {session_id} not found for deletion.")
            return False
    except Exception as e:
        logging.error(f"Error deleting chat session {session_id} from MongoDB: {e}")
        return False 

# --- Document Analysis CRUD ---

async def save_document_analysis(document_id: str, analysis_result: DocumentAnalysisResult) -> bool:
    """Saves document analysis results to MongoDB."""
    collection = await get_analysis_collection()
    try:
        # Set the document_id as _id for MongoDB
        analysis_dict = analysis_result.model_dump()
        analysis_dict["_id"] = document_id
        
        result = await collection.replace_one({"_id": document_id}, analysis_dict, upsert=True)
        if result.upserted_id or result.modified_count > 0:
            logging.info(f"Saved/Updated analysis for document {document_id} in MongoDB.")
            return True
        elif result.matched_count > 0 and result.modified_count == 0:
            logging.warning(f"Analysis for document {document_id} already exists and is identical.")
            return True  # Already exists, treat as success
        else:
            logging.error(f"Failed to save analysis for document {document_id} (unknown error).")
            return False
    except Exception as e:
        logging.error(f"Error saving analysis for document {document_id} to MongoDB: {e}")
        return False

async def get_document_analysis(document_id: str) -> Optional[DocumentAnalysisResult]:
    """Retrieves the analysis result for a document from MongoDB."""
    collection = await get_analysis_collection()
    try:
        analysis_data = await collection.find_one({"_id": document_id})
        if analysis_data:
            # Remove the MongoDB _id before parsing
            if "_id" in analysis_data:
                analysis_data.pop("_id")
            # Parse with Pydantic model
            analysis_result = DocumentAnalysisResult(**analysis_data)
            logging.debug(f"Retrieved analysis for document {document_id} from MongoDB.")
            return analysis_result
        else:
            logging.warning(f"Analysis not found for document {document_id} in MongoDB.")
            return None
    except Exception as e:
        logging.error(f"Error retrieving analysis for document {document_id} from MongoDB: {e}")
        return None

async def delete_document_analysis(document_id: str) -> bool:
    """Deletes the analysis result for a document from MongoDB."""
    collection = await get_analysis_collection()
    try:
        result = await collection.delete_one({"_id": document_id})
        if result.deleted_count > 0:
            logging.info(f"Deleted analysis for document {document_id} from MongoDB.")
            return True
        else:
            logging.warning(f"Analysis for document {document_id} not found for deletion.")
            return False
    except Exception as e:
        logging.error(f"Error deleting analysis for document {document_id} from MongoDB: {e}")
        return False 