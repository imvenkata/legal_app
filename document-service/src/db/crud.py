from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Optional, List

from . import models
from .models import Document, DocumentCreate, DocumentStatus, DocumentUpdate

# --- Document CRUD (SQLAlchemy) --- 

def create_document_db(db: Session, doc_data: DocumentCreate) -> Optional[models.Document]:
    """Creates the initial document metadata record in the relational database."""
    try:
        logging.debug(f"Creating document with data: {doc_data.model_dump()}")
        db_doc = models.Document(**doc_data.model_dump())
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        logging.info(f"Created document record in SQL DB: {db_doc.id}")
        return db_doc
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Error creating document record in SQL DB: {e}")
        return None
    except Exception as e:
        db.rollback()
        logging.error(f"Unexpected error creating document in SQL DB: {e}")
        return None

def update_document_status_db(db: Session, document_id: str, status: DocumentStatus) -> bool:
    """Updates the status of a document in the relational database."""
    try:
        db_doc = db.query(models.Document).filter(models.Document.id == document_id).first()
        if db_doc:
            db_doc.status = status
            db.commit()
            logging.info(f"Updated status for document {document_id} to {status.value} in SQL DB.")
            return True
        else:
            logging.warning(f"Document {document_id} not found in SQL DB for status update.")
            return False
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Error updating status for document {document_id} in SQL DB: {e}")
        return False
    except Exception as e:
        db.rollback()
        logging.error(f"Unexpected error updating status for {document_id} in SQL DB: {e}")
        return False

def get_document_db(db: Session, document_id: str, user_id: str = None) -> Optional[models.Document]:
    """Gets a specific document by ID, ensuring ownership if user_id is provided."""
    try:
        if user_id:
            db_doc = db.query(models.Document).filter(
                models.Document.id == document_id,
                models.Document.owner_id == user_id # Check ownership
            ).first()
        else:
            # Debug mode - skip ownership check
            db_doc = db.query(models.Document).filter(
                models.Document.id == document_id
            ).first()
        
        if db_doc:
            logging.debug(f"Retrieved document {document_id} from SQL DB.")
        else:
            # Check if the document exists at all (for logging/debugging)
            exists = db.query(models.Document.id).filter(models.Document.id == document_id).first() is not None
            if exists and user_id:
                 logging.warning(f"User {user_id} attempted to access document {document_id} owned by another user.")
            else:
                 logging.warning(f"Document {document_id} not found in SQL DB.")
        return db_doc
    except SQLAlchemyError as e:
        logging.error(f"Error retrieving document {document_id} from SQL DB: {e}")
        return None

def get_user_documents_db(
    db: Session, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None, 
    tag: Optional[str] = None
) -> List[models.Document]:
    """Gets a list of documents for a user with optional filtering."""
    try:
        query = db.query(models.Document).filter(models.Document.owner_id == user_id)
        
        # Add filters if provided
        if search:
            # Simple title search (adjust for more complex search needs)
            query = query.filter(models.Document.title.ilike(f"%{search}%")) 
        if tag:
            # Assuming tags are stored as a JSON list
            query = query.filter(models.Document.tags.contains([tag]))
            
        documents = query.offset(skip).limit(limit).all()
        logging.debug(f"Retrieved {len(documents)} documents for user {user_id} from SQL DB.")
        return documents
    except SQLAlchemyError as e:
        logging.error(f"Error retrieving documents for user {user_id} from SQL DB: {e}")
        return []

def update_document_metadata_db(db: Session, document_id: str, user_id: str, doc_update: DocumentUpdate) -> Optional[models.Document]:
    """Updates the metadata (title, desc, tags) of a document, ensuring ownership."""
    try:
        db_doc = db.query(models.Document).filter(
            models.Document.id == document_id,
            models.Document.owner_id == user_id
        ).first()
        
        if not db_doc:
            logging.warning(f"Document {document_id} not found or user {user_id} lacks permission for update.")
            return None
            
        update_data = doc_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_doc, key, value)
            
        db.commit()
        db.refresh(db_doc)
        logging.info(f"Updated metadata for document {document_id} in SQL DB.")
        return db_doc
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Error updating metadata for document {document_id} in SQL DB: {e}")
        return None

def delete_document_db(db: Session, document_id: str, user_id: str = None) -> bool:
    """Deletes a document record from the relational database, ensuring ownership if user_id is provided."""
    try:
        if user_id:
            db_doc = db.query(models.Document).filter(
                models.Document.id == document_id,
                models.Document.owner_id == user_id
            ).first()
        else:
            # Debug mode - skip ownership check
            db_doc = db.query(models.Document).filter(
                models.Document.id == document_id
            ).first()
        
        if db_doc:
            db.delete(db_doc)
            db.commit()
            logging.info(f"Deleted document record {document_id} from SQL DB.")
            return True
        else:
            if user_id:
                logging.warning(f"Document {document_id} not found or user {user_id} lacks permission for deletion.")
            else:
                logging.warning(f"Document {document_id} not found in SQL DB.")
            return False
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Error deleting document {document_id} from SQL DB: {e}")
        return False

# Add CRUD functions for other models like AnalysisResult if needed 