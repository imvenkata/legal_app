"""
Direct test script for document-status functionality.
Uses SQLAlchemy models and CRUD operations directly.
"""
import os
import sys
import uuid
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import models and CRUD functions
try:
    from document_service.src.db.models import DocumentTable as Document, DocumentStatus
except ImportError:
    try:
        from src.db.models import DocumentTable as Document, DocumentStatus
    except ImportError:
        print("Failed to import document models. Make sure you're in the correct directory.")
        sys.exit(1)

def setup_test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    Base = declarative_base()
    
    # Define a simplified Document table structure for testing
    class TestDocument(Base):
        __tablename__ = "documents"
        
        id = Document.__table__.c.id.copy()
        title = Document.__table__.c.title.copy()
        description = Document.__table__.c.description.copy()
        filename = Document.__table__.c.filename.copy()
        file_size = Document.__table__.c.file_size.copy()
        file_type = Document.__table__.c.file_type.copy()
        storage_path = Document.__table__.c.storage_path.copy()
        owner_id = Document.__table__.c.owner_id.copy()
        status = Document.__table__.c.status.copy()
        created_at = Document.__table__.c.created_at.copy()
        updated_at = Document.__table__.c.updated_at.copy()
    
    Base.metadata.create_all(engine)
    session = Session()
    
    return session, TestDocument

def create_test_document(db, TestDocument):
    """Create a test document in the database."""
    doc_id = str(uuid.uuid4())
    test_doc = TestDocument(
        id=doc_id,
        title="Test Document",
        description="A test document for status testing",
        filename="test.txt",
        file_size=100,
        file_type="txt",
        storage_path=f"{doc_id}.txt",
        owner_id=123,
        status=DocumentStatus.UPLOADED,
        created_at=datetime.datetime.now()
    )
    
    db.add(test_doc)
    db.commit()
    
    print(f"Created test document with ID: {doc_id}")
    return doc_id

def update_document_status(db, TestDocument, doc_id, status):
    """Update document status in the database."""
    try:
        doc = db.query(TestDocument).filter(TestDocument.id == doc_id).first()
        if doc:
            doc.status = status
            db.commit()
            print(f"Updated status for document {doc_id} to {status.value}.")
            return True
        else:
            print(f"Document {doc_id} not found in DB for status update.")
            return False
    except Exception as e:
        db.rollback()
        print(f"Error updating status for document {doc_id}: {e}")
        return False

def test_document_status_cycle(db, TestDocument, doc_id):
    """Test updating the document status through various states."""
    status_sequence = [
        DocumentStatus.UPLOADED,
        DocumentStatus.PARSING,
        DocumentStatus.PARSING_COMPLETED,
        DocumentStatus.ANALYZING,
        DocumentStatus.ANALYZED,
    ]
    
    for status in status_sequence:
        print(f"\nUpdating document status to: {status.value}")
        update_result = update_document_status(db, TestDocument, doc_id, status)
        if update_result:
            # Get the document to verify the status change
            doc = db.query(TestDocument).filter(TestDocument.id == doc_id).first()
            print(f"Current status: {doc.status.value}")
            print(f"Status updated successfully: {doc.status == status}")
        else:
            print(f"Failed to update status to {status.value}")
            return False
    
    return True

def main():
    """Main test function."""
    print("Setting up test database...")
    db, TestDocument = setup_test_db()
    
    print("Creating test document...")
    doc_id = create_test_document(db, TestDocument)
    
    print("Running document status cycle test...")
    test_result = test_document_status_cycle(db, TestDocument, doc_id)
    
    if test_result:
        print("\nAll document status tests passed!")
    else:
        print("\nSome document status tests failed.")

if __name__ == "__main__":
    main() 