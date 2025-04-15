import httpx
import os
import json
import sys
import asyncio
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Add src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Create mock database session
mock_db = MagicMock()

# Mock the get_db dependency
def override_get_db():
    return mock_db

# Mock the authentication dependency
def override_get_current_user():
    return {"id": 1, "username": "testuser"}

# Path to the test PDF document
TEST_PDF_PATH = "/Users/venkata/startup/legal_app/document-service/documents/20250403_180359_Trademark-Assignment.pdf"

# Import the app and setup mocks after defining the mocks
with patch("src.db.session.get_db", override_get_db):
    from src.api.main import app
    from src.core.auth import get_current_user
    from src.db.session import get_db
    
    # Override dependencies
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

# Create test client
client = TestClient(app)

def test_upload_and_analyze_document():
    """Test document upload and analysis flow."""
    # Skip if the test file doesn't exist
    if not os.path.exists(TEST_PDF_PATH):
        pytest.skip(f"Test file not found: {TEST_PDF_PATH}")
    
    # 1. Upload the document
    with open(TEST_PDF_PATH, "rb") as f:
        file_content = f.read()
    
    # Create a multipart form request
    response = client.post(
        "/api/documents/",
        files={"file": ("Trademark-Assignment.pdf", file_content, "application/pdf")},
        data={
            "title": "Trademark Assignment",
            "description": "Test document for API testing",
            "tags": "trademark,legal,test"
        }
    )
    
    # Check if upload was successful
    assert response.status_code == 201, f"Upload failed with status {response.status_code}: {response.text}"
    
    # Get document ID from response
    upload_result = response.json()
    document_id = upload_result["id"]
    print(f"\nDocument uploaded successfully with ID: {document_id}")
    print(f"Document details: {json.dumps(upload_result, indent=2)}")
    
    # 2. Analyze the document
    # For this test, we'll skip the actual analysis which would require OpenAI API keys
    # and just check that the endpoint is reachable
    analysis_response = client.post(
        f"/api/documents/{document_id}/analyze",
        data={"llm_model": "gpt-4o"}
    )
    
    # Check if analysis request was accepted
    assert analysis_response.status_code == 200, f"Analysis failed with status {analysis_response.status_code}: {analysis_response.text}"
    
    # Get analysis result
    analysis_result = analysis_response.json()
    print(f"\nDocument analysis completed successfully")
    print(f"Analysis summary: {analysis_result.get('summary', 'No summary available')}")
    
    return document_id

def test_get_document(document_id):
    """Test getting a document by ID."""
    response = client.get(f"/api/documents/{document_id}")
    
    # Check if request was successful
    assert response.status_code == 200, f"Get document failed with status {response.status_code}: {response.text}"
    
    # Get document details
    document = response.json()
    print(f"\nDocument retrieved successfully")
    print(f"Document details: {json.dumps(document, indent=2)}")

def test_get_all_documents():
    """Test getting all documents."""
    response = client.get("/api/documents/")
    
    # Check if request was successful
    assert response.status_code == 200, f"Get all documents failed with status {response.status_code}: {response.text}"
    
    # Get documents
    documents = response.json()
    print(f"\nRetrieved {len(documents)} documents")
    for doc in documents:
        print(f"- {doc['title']} (ID: {doc['id']})")

def run_tests():
    """Run all tests in sequence."""
    print("=== Testing Document Service API ===")
    
    try:
        # Upload and analyze document
        document_id = test_upload_and_analyze_document()
        
        # Get document by ID
        test_get_document(document_id)
        
        # Get all documents
        test_get_all_documents()
        
        print("\n=== All tests completed successfully ===")
    except Exception as e:
        print(f"\n=== Test failed: {str(e)} ===")
        raise

if __name__ == "__main__":
    run_tests() 