from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os
import uuid
from datetime import datetime
import tempfile
import logging
import json

from src.db.session import get_db, get_db_session
from src.db.models import ( Document, DocumentCreate, DocumentUpdate, DocumentResponse, 
                            DocumentAnalysisResult, DocumentStatus, DocumentStatusResponse )
from src.core.storage import get_storage_service
from src.core.llm import get_llm_adapter
from src.core.parser import extract_text_from_content
from src.db import crud, mongo_crud

router = APIRouter()

# Define a mock user ID to use when auth is disabled
MOCK_USER_ID = 123

async def parse_and_store_text_task(document_id: str, storage_path: str, file_type: str, db: Session):
    """Background task: Parse doc, store text in Mongo, update status in SQL."""
    from src.db.session import get_db_session  # Import inside the function to avoid circular imports
    
    logging.info(f"[TASK:{document_id}] Starting background parsing.")
    storage = get_storage_service()
    
    # Create a new session for this background task
    # This is needed because the session from the request might be closed by the time this runs
    db_session = get_db_session()
    
    try:
        # First update status to PARSING
        updated = crud.update_document_status_db(db_session, document_id, DocumentStatus.PARSING)
        if not updated:
             logging.error(f"[TASK:{document_id}] Failed to update status to PARSING.")
             return 
             
        # Retrieve file from storage
        file_content = await storage.retrieve_file(storage_path)
        if not file_content:
            logging.error(f"[TASK:{document_id}] Failed to retrieve file.")
            crud.update_document_status_db(db_session, document_id, DocumentStatus.PARSING_FAILED)
            return
            
        # Extract text
        extracted_text = await extract_text_from_content(file_content, file_type)
        if not extracted_text:
             logging.error(f"[TASK:{document_id}] Text extraction failed.")
             crud.update_document_status_db(db_session, document_id, DocumentStatus.PARSING_FAILED)
             return
             
        # Save to MongoDB
        mongo_success = await mongo_crud.save_parsed_document(document_id, extracted_text)
        if mongo_success:
            crud.update_document_status_db(db_session, document_id, DocumentStatus.PARSING_COMPLETED)
            logging.info(f"[TASK:{document_id}] Parsing completed.")
        else:
            logging.error(f"[TASK:{document_id}] Failed to save text to MongoDB.")
            crud.update_document_status_db(db_session, document_id, DocumentStatus.PARSING_FAILED)
            
    except Exception as e:
        logging.exception(f"[TASK:{document_id}] Error during parsing: {e}")
        try:
            crud.update_document_status_db(db_session, document_id, DocumentStatus.PARSING_FAILED)
        except Exception as update_e:
            logging.error(f"[TASK:{document_id}] Could not update status after error: {update_e}")
    finally:
        # Make sure we close the session at the end
        db_session.close()
        logging.debug(f"[TASK:{document_id}] DB session closed.")

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Create a new document by uploading a file (authentication disabled).
    This endpoint is for testing and development only.
    """
    user_id = MOCK_USER_ID # Use hardcoded user ID
    logging.info(f"Upload document request: '{title}' by user {user_id}, file: {file.filename}")
    
    # Parse tags from string to list if provided
    tag_list = []
    if tags:
        try:
            # First try to parse as JSON if it's in JSON format
            if tags.startswith('[') and tags.endswith(']'):
                tag_list = json.loads(tags)
                if not isinstance(tag_list, list):
                    tag_list = []
            else:
                # Otherwise, treat as comma-separated values
                tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        except Exception as e:
            logging.warning(f"Error parsing tags: {e}")
            # Fallback to simple comma splitting
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
    
    # Generate a unique ID for the document
    document_id = uuid.uuid4()
    
    # Upload file to storage
    try:
        storage = get_storage_service()
        file_content = await file.read()
        file_size = len(file_content)
        
        # Create a unique storage path for this document
        storage_path = f"documents/{user_id}/{document_id}/{file.filename}"
        
        # Upload to storage service (S3, local, etc.)
        await storage.store_file(storage_path, file_content)
        logging.info(f"File uploaded to {storage_path}")
        
        # Create document record in database
        document_data = DocumentCreate(
            title=title,
            description=description,
            filename=file.filename,
            file_size=file_size,
            file_type=file.content_type,
            storage_path=storage_path,
            owner_id=user_id,
            tags=tag_list
        )
        
        # Save to database
        document = crud.create_document_db(db, document_data)
        if not document:
            # If we couldn't create the record, attempt to clean up the file
            try:
                await storage.delete_file(storage_path)
            except Exception as cleanup_e:
                logging.error(f"Failed to clean up file after DB error: {cleanup_e}")
            raise HTTPException(status_code=500, detail="Failed to create document record.")
        
        # Start background task to parse the document text
        background_tasks.add_task(
            parse_and_store_text_task,
            str(document.id), 
            storage_path, 
            file.content_type,
            db
        )
        
        # Create properly serialized response
        document_response = DocumentResponse(
            id=str(document.id),
            title=document.title,
            description=document.description,
            filename=document.filename,
            file_size=document.file_size,
            file_type=document.file_type,
            storage_path=document.storage_path,
            owner_id=document.owner_id,
            tags=document.tags or [],
            created_at=document.created_at.isoformat() if document.created_at else None,
            updated_at=document.updated_at.isoformat() if document.updated_at else None,
            status=document.status.value if document.status else "uploaded"
        )
        
        return document_response
        
    except Exception as e:
        logging.exception(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get documents for the mock user (authentication disabled)."""
    user_id = MOCK_USER_ID # Use hardcoded user ID
    documents = crud.get_user_documents_db(db, user_id, skip, limit, search, tag)
    
    # Convert the documents to Pydantic models with explicit serialization of UUID and datetime
    results = []
    for doc in documents:
        results.append(DocumentResponse(
            id=str(doc.id),
            title=doc.title,
            description=doc.description,
            filename=doc.filename,
            file_size=doc.file_size,
            file_type=doc.file_type,
            storage_path=doc.storage_path,
            owner_id=doc.owner_id,
            tags=doc.tags or [],
            created_at=doc.created_at.isoformat() if doc.created_at else None,
            updated_at=doc.updated_at.isoformat() if doc.updated_at else None,
            status=doc.status.value if doc.status else "uploaded"
        ))
    
    return results

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific document by ID (authentication disabled)."""
    user_id = MOCK_USER_ID # Use hardcoded user ID
    document = crud.get_document_db(db, document_id, user_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    # Convert to Pydantic model with explicit serialization of UUID and datetime
    return DocumentResponse(
        id=str(document.id),
        title=document.title,
        description=document.description,
        filename=document.filename,
        file_size=document.file_size,
        file_type=document.file_type,
        storage_path=document.storage_path,
        owner_id=document.owner_id,
        tags=document.tags or [],
        created_at=document.created_at.isoformat() if document.created_at else None,
        updated_at=document.updated_at.isoformat() if document.updated_at else None,
        status=document.status.value if document.status else "uploaded"
    )

@router.post("/{document_id}/analyze", response_model=DocumentAnalysisResult)
async def analyze_document(
    document_id: str,
    llm_model: Optional[str] = Form("gpt-4o"), 
    db: Session = Depends(get_db)
):
    """
    Analyze a document using an LLM (authentication disabled).
    """
    user_id = MOCK_USER_ID # Use hardcoded user ID
    
    # Check for API key early
    api_key = os.getenv("OPENAI_API_KEY") 
    if not api_key:
        logging.error("Missing OpenAI API key configuration")
        raise HTTPException(status_code=500, detail="LLM API key not configured.")
    
    # Validate document exists and status
    document = crud.get_document_db(db, document_id, user_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        
    if document.status != DocumentStatus.PARSING_COMPLETED:
        logging.warning(f"Analysis requested for doc {document_id} but status is {document.status.value}")
        if document.status in [DocumentStatus.UPLOADED, DocumentStatus.PARSING]:
             detail = "Document is still being processed, try again later."
        elif document.status == DocumentStatus.PARSING_FAILED:
             detail = "Cannot analyze (parsing failed)."
        elif document.status == DocumentStatus.ANALYZING:
             detail = "Document is already being analyzed, try again later."
        elif document.status == DocumentStatus.ANALYZED:
             detail = "Document has already been analyzed."
        else:
             detail = f"Document not ready for analysis (status: {document.status.value})."
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    # Get parsed text from MongoDB
    document_text = await mongo_crud.get_parsed_document_text(document_id)
    if document_text is None:
        logging.error(f"Parsed text missing for {document_id} in MongoDB.")
        crud.update_document_status_db(db, document_id, DocumentStatus.ERROR)
        raise HTTPException(status_code=500, detail="Internal error: Parsed content missing.")
    
    # Initialize LLM adapter
    try:
        llm_adapter = get_llm_adapter(llm_model)
        await llm_adapter.initialize(api_key=api_key, model_params={"model": llm_model})
    except Exception as e:
        logging.error(f"Failed to initialize LLM adapter: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize LLM: {str(e)}")
        
    # Update status before starting analysis
    crud.update_document_status_db(db, document_id, DocumentStatus.ANALYZING)
    
    try:
        logging.info(f"Starting LLM analysis for doc {document_id}...")
        analysis_result_data = await llm_adapter.analyze_document(document_text)
        logging.info(f"LLM analysis completed for doc {document_id}.")
        
        # Process entities which might be a complex structure
        entities = []
        raw_entities = analysis_result_data.get("entities", [])
        
        # Handle different formats from the LLM response
        if isinstance(raw_entities, list):
            entities = raw_entities
        elif isinstance(raw_entities, dict):
            # Flatten the dictionary into a list of entity strings
            for category, items in raw_entities.items():
                if isinstance(items, list):
                    entities.extend(items)
                else:
                    entities.append(f"{category}: {items}")
        
        # Process risk factors which might be a complex structure
        risk_factors = []
        raw_risks = analysis_result_data.get("risks", [])
        if isinstance(raw_risks, list):
            risk_factors = raw_risks
        elif isinstance(raw_risks, dict):
            # Flatten the dictionary into a list of risk strings
            for category, items in raw_risks.items():
                if isinstance(items, list):
                    risk_factors.extend(items)
                else:
                    risk_factors.append(f"{category}: {items}")
        
        # Process recommendations which might be a complex structure
        recommendations = []
        raw_recommendations = analysis_result_data.get("recommendations", [])
        if isinstance(raw_recommendations, list):
            recommendations = raw_recommendations
        elif isinstance(raw_recommendations, dict):
            # Flatten the dictionary into a list of recommendation strings
            for category, items in raw_recommendations.items():
                if isinstance(items, list):
                    recommendations.extend(items)
                else:
                    recommendations.append(f"{category}: {items}")
        
        result = DocumentAnalysisResult(
            document_id=document_id,
            summary=analysis_result_data.get("summary", ""),
            entities=entities,
            risk_factors=risk_factors,
            recommendations=recommendations,
            model_used=llm_model,
            created_at=datetime.now().isoformat()
        )
        
        # Save the analysis result to MongoDB
        analysis_saved = await mongo_crud.save_document_analysis(document_id, result)
        if not analysis_saved:
            logging.error(f"Failed to save analysis result for document {document_id}")
            # We still update the status and return the result, but log the error
        
        crud.update_document_status_db(db, document_id, DocumentStatus.ANALYZED)
        return result
    except Exception as e:
        logging.exception(f"Error during LLM analysis for doc {document_id}: {e}")
        crud.update_document_status_db(db, document_id, DocumentStatus.ANALYSIS_FAILED)
        raise HTTPException(status_code=500, detail=f"Error during analysis: {str(e)}")

@router.get("/{document_id}/analysis", response_model=DocumentAnalysisResult)
async def get_document_analysis(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the analysis result for a document (authentication disabled).
    """
    user_id = MOCK_USER_ID # Use hardcoded user ID
    
    # First verify the document exists
    document = crud.get_document_db(db, document_id, user_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Document not found"
        )
    
    # Check if the document has been analyzed
    if document.status != DocumentStatus.ANALYZED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Analysis not available for this document (status: {document.status.value})"
        )
    
    # Get the analysis result from MongoDB
    analysis_result = await mongo_crud.get_document_analysis(document_id)
    if not analysis_result:
        # This is an inconsistency - document is marked as analyzed but no analysis found
        logging.error(f"Document {document_id} is marked as analyzed but no analysis found")
        crud.update_document_status_db(db, document_id, DocumentStatus.ERROR)
            
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis result not found (inconsistent state)"
        )
    
    return analysis_result

@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """Update a document's metadata (authentication disabled)."""
    user_id = MOCK_USER_ID # Use hardcoded user ID
    updated_document = crud.update_document_metadata_db(db, document_id, user_id, document_update)
    if not updated_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    # Convert to Pydantic model with explicit serialization of UUID and datetime
    return DocumentResponse(
        id=str(updated_document.id),
        title=updated_document.title,
        description=updated_document.description,
        filename=updated_document.filename,
        file_size=updated_document.file_size,
        file_type=updated_document.file_type,
        storage_path=updated_document.storage_path,
        owner_id=updated_document.owner_id,
        tags=updated_document.tags or [],
        created_at=updated_document.created_at.isoformat() if updated_document.created_at else None,
        updated_at=updated_document.updated_at.isoformat() if updated_document.updated_at else None,
        status=updated_document.status.value if updated_document.status else "uploaded"
    )

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a document (authentication disabled).
    """
    user_id = MOCK_USER_ID # Use hardcoded user ID
    logging.info(f"User '{user_id}' requesting deletion of document {document_id}")

    # First, update document status to DELETING to prevent race conditions
    document = crud.get_document_db(db, document_id, user_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    # Set status to DELETING to prevent any operations during deletion
    crud.update_document_status_db(db, document_id, DocumentStatus.DELETING)
    
    storage_path = document.storage_path
    deletion_errors = []
    
    # Step 1: Delete MongoDB data (parsed text, analysis, chat) - continue even if fails
    try:
        # Delete parsed document text
        logging.debug(f"Deleting parsed text for {document_id} from MongoDB.")
        await mongo_crud.delete_parsed_document(document_id)
        
        # Delete document analysis if it exists
        logging.debug(f"Deleting analysis for {document_id} from MongoDB.")
        await mongo_crud.delete_document_analysis(document_id)
        
        # Delete chat sessions
        session_id = f"{user_id}:{document_id}" 
        logging.debug(f"Deleting chat session {session_id} from MongoDB.")
        await mongo_crud.delete_chat_session(session_id)
    except Exception as e:
        deletion_errors.append(f"MongoDB deletion error: {str(e)}")
        logging.error(f"Error deleting MongoDB data for document {document_id}: {e}")
    
    # Step 2: Delete storage file
    try:
        storage = get_storage_service()
        logging.debug(f"Deleting file from storage: {storage_path}")
        await storage.delete_file(storage_path)
        logging.info(f"Successfully deleted file {storage_path}.")
    except Exception as e:
        deletion_errors.append(f"Storage deletion error: {str(e)}")
        logging.error(f"Failed to delete file {storage_path} from storage: {e}")
    
    # Step 3: Delete SQL DB record (do this last)
    try:
        sql_deleted = crud.delete_document_db(db, document_id, user_id)
        if not sql_deleted:
            deletion_errors.append("SQL DB deletion failed")
            logging.error(f"Failed to delete doc {document_id} from SQL DB.")
            # Set status back to ERROR if we couldn't delete
            crud.update_document_status_db(db, document_id, DocumentStatus.ERROR)
    except Exception as e:
        deletion_errors.append(f"SQL deletion error: {str(e)}")
        logging.error(f"Exception deleting doc {document_id} from SQL DB: {e}")
        # Set status back to ERROR if we couldn't delete
        try:
            crud.update_document_status_db(db, document_id, DocumentStatus.ERROR)
        except:
            pass
    
    # If we had errors, log them but don't fail the request
    if deletion_errors:
        logging.warning(f"Document {document_id} deletion completed with errors: {deletion_errors}")
    else:
        logging.info(f"Completed deletion for document {document_id}")
        
    return None

@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the status of a document.
    """
    user_id = MOCK_USER_ID # Use hardcoded user ID
    
    document = crud.get_document_db(db, document_id, user_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    # Get status description based on the status value
    status_descriptions = {
        DocumentStatus.UPLOADED.value: "Document has been uploaded but not yet processed",
        DocumentStatus.PARSING.value: "Document is being processed for text extraction",
        DocumentStatus.PARSING_FAILED.value: "Failed to extract text from the document",
        DocumentStatus.PARSING_COMPLETED.value: "Document text has been extracted and is ready for analysis",
        DocumentStatus.ANALYZING.value: "Document is being analyzed by AI",
        DocumentStatus.ANALYSIS_FAILED.value: "Failed to analyze the document",
        DocumentStatus.ANALYZED.value: "Document has been successfully analyzed",
        DocumentStatus.DELETING.value: "Document is being deleted",
        DocumentStatus.DELETED.value: "Document has been deleted",
        DocumentStatus.ERROR.value: "An error occurred with this document"
    }
    
    description = status_descriptions.get(document.status.value, "Unknown status")
    
    return DocumentStatusResponse(
        document_id=document_id,
        status=document.status.value,
        description=description,
        updated_at=document.updated_at.isoformat() if document.updated_at else None
    )

@router.put("/{document_id}/status", response_model=DocumentStatusResponse)
async def update_document_status(
    document_id: str,
    status_value: str = Query(..., description="The new status value"),
    db: Session = Depends(get_db)
):
    """
    Update the status of a document.
    """
    user_id = MOCK_USER_ID # Use hardcoded user ID
    logging.info(f"Updating status for document {document_id} to {status_value}")
    
    # Validate the status value
    try:
        new_status = DocumentStatus(status_value)
    except ValueError:
        valid_statuses = [s.value for s in DocumentStatus]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Invalid status value. Valid values are: {', '.join(valid_statuses)}"
        )
    
    # Get the document to check if it exists
    document = crud.get_document_db(db, document_id, user_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    # Validate status transitions
    current_status = document.status
    invalid_transitions = {
        DocumentStatus.DELETED: True,  # Can't change from DELETED
        DocumentStatus.DELETING: True,  # Can't change from DELETING
    }
    
    # Check if current status prevents changes
    if current_status in invalid_transitions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot change status from '{current_status.value}'"
        )
    
    # Prevent setting to specific statuses via API (these should only be set by internal processes)
    if new_status in [DocumentStatus.DELETING, DocumentStatus.DELETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot manually set status to '{new_status.value}' - use the delete endpoint instead"
        )
    
    # Update the document status
    updated = crud.update_document_status_db(db, document_id, new_status)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to update document status"
        )
    
    # Get the updated document
    updated_document = crud.get_document_db(db, document_id, user_id)
    
    # Get status description based on the status value
    status_descriptions = {
        DocumentStatus.UPLOADED.value: "Document has been uploaded but not yet processed",
        DocumentStatus.PARSING.value: "Document is being processed for text extraction",
        DocumentStatus.PARSING_FAILED.value: "Failed to extract text from the document",
        DocumentStatus.PARSING_COMPLETED.value: "Document text has been extracted and is ready for analysis",
        DocumentStatus.ANALYZING.value: "Document is being analyzed by AI",
        DocumentStatus.ANALYSIS_FAILED.value: "Failed to analyze the document",
        DocumentStatus.ANALYZED.value: "Document has been successfully analyzed",
        DocumentStatus.DELETING.value: "Document is being deleted",
        DocumentStatus.DELETED.value: "Document has been deleted",
        DocumentStatus.ERROR.value: "An error occurred with this document"
    }
    
    description = status_descriptions.get(updated_document.status.value, "Unknown status")
    
    return DocumentStatusResponse(
        document_id=document_id,
        status=updated_document.status.value,
        description=description,
        updated_at=updated_document.updated_at.isoformat() if updated_document.updated_at else None
    ) 