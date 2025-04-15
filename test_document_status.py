"""
Standalone test for document status functionality.
"""
import enum
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Enum, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid

# Create a SQLAlchemy base
Base = declarative_base()

# Define enums
class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    PARSING_FAILED = "parsing_failed"
    PARSING_COMPLETED = "parsing_completed"  # Text extraction successful
    ANALYZING = "analyzing"
    ANALYSIS_FAILED = "analysis_failed"
    ANALYZED = "analyzed"  # Full analysis complete
    DELETING = "deleting"
    DELETED = "deleted"
    ERROR = "error"  # General error state

# Define models
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

class DocumentStatusResponse:
    """Simple class to represent a document status response."""
    def __init__(self, document_id, status, description, updated_at=None):
        self.document_id = document_id
        self.status = status
        self.description = description
        self.updated_at = updated_at

# Create database and session
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def create_test_document():
    """Create a test document in the database."""
    doc_id = str(uuid.uuid4())
    doc = Document(
        id=doc_id,
        title="Test Document",
        description="Test document for status API",
        status=DocumentStatus.UPLOADED,
    )
    session.add(doc)
    session.commit()
    print(f"Created test document with ID: {doc_id}")
    return doc_id

def get_document_status(document_id):
    """Get the status of a document."""
    doc = session.query(Document).filter(Document.id == document_id).first()
    if not doc:
        print(f"Document {document_id} not found")
        return None
    
    # Get status description
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
    
    description = status_descriptions.get(doc.status.value, "Unknown status")
    
    response = DocumentStatusResponse(
        document_id=document_id,
        status=doc.status.value,
        description=description,
        updated_at=doc.updated_at.isoformat() if doc.updated_at else None
    )
    
    return response

def update_document_status(document_id, status_value):
    """Update the status of a document."""
    try:
        # Validate the status value
        new_status = DocumentStatus(status_value)
        
        # Get the document
        doc = session.query(Document).filter(Document.id == document_id).first()
        if not doc:
            print(f"Document {document_id} not found")
            return None
        
        # Update the status
        doc.status = new_status
        doc.updated_at = datetime.now()  # Manually update since we're using SQLite
        session.commit()
        
        # Return the updated status
        return get_document_status(document_id)
    except ValueError:
        valid_statuses = [s.value for s in DocumentStatus]
        print(f"Invalid status value. Valid values are: {', '.join(valid_statuses)}")
        return None
    except Exception as e:
        print(f"Error updating document status: {e}")
        session.rollback()
        return None

def test_document_status_workflow():
    """Test a complete document status workflow."""
    print("Creating test document...")
    doc_id = create_test_document()
    
    # Get initial status
    print("\nGetting initial document status...")
    status = get_document_status(doc_id)
    print(f"Initial status: {status.status}")
    print(f"Description: {status.description}")
    
    # Update through a workflow
    status_workflow = [
        "parsing",
        "parsing_completed",
        "analyzing",
        "analyzed"
    ]
    
    for status_value in status_workflow:
        print(f"\nUpdating status to: {status_value}")
        status = update_document_status(doc_id, status_value)
        if status:
            print(f"New status: {status.status}")
            print(f"Description: {status.description}")
            print(f"Updated at: {status.updated_at}")
        else:
            print(f"Failed to update status to {status_value}")
            return False
    
    # Test invalid status
    print("\nTesting invalid status update...")
    result = update_document_status(doc_id, "invalid_status")
    if result is None:
        print("Invalid status test passed (rejected as expected)")
    else:
        print("Invalid status test failed (should have been rejected)")
        return False
    
    return True

if __name__ == "__main__":
    print("=== Document Status API Test ===")
    result = test_document_status_workflow()
    if result:
        print("\nAll document status tests passed!")
    else:
        print("\nSome document status tests failed.") 