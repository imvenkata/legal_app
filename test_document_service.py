#!/usr/bin/env python3
"""
Comprehensive test script for document service with a specific PDF file
"""

import os
import sys
import json
import logging
from pathlib import Path
import PyPDF2
import io
import requests
import base64
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path to the test PDF document
TEST_PDF_PATH = "/Users/venkata/startup/legal_app/document-service/documents/state_v._smith.pdf"
API_BASE_URL = "http://localhost:8080/api"
MOCK_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwibmFtZSI6IlRlc3QgVXNlciIsImV4cCI6MTY5MTI0NTgwMH0.mock_signature"

def extract_text_from_pdf(pdf_content):
    """Extract text from a PDF file using PyPDF2."""
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text() + "\n\n"
    return text

def test_direct_analysis():
    """Test document text extraction and analysis directly."""
    print("\n=== TESTING DIRECT DOCUMENT ANALYSIS ===")
    
    # Check if the test file exists
    if not os.path.exists(TEST_PDF_PATH):
        print(f"Error: Test file not found: {TEST_PDF_PATH}")
        return
    
    # Read the document content
    print(f"Reading document: {TEST_PDF_PATH}")
    with open(TEST_PDF_PATH, "rb") as f:
        file_content = f.read()
    
    # Extract text from PDF
    print("Extracting text from PDF...")
    try:
        document_text = extract_text_from_pdf(file_content)
        print(f"Document text extracted, size: {len(document_text)} characters")
        print("First 200 characters of text:")
        print(document_text[:200] + "...")
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return

def test_api_upload():
    """Test document upload via API."""
    print("\n=== TESTING DOCUMENT UPLOAD API ===")
    
    # Check if the test file exists
    if not os.path.exists(TEST_PDF_PATH):
        print(f"Error: Test file not found: {TEST_PDF_PATH}")
        return None
    
    # Prepare upload data
    title = "State v. Smith Case"
    description = "2025 Ohio Appeals Court opinion in a criminal case"
    tags = "legal,court,case,opinion"
    
    # Upload document
    print(f"Uploading document: {TEST_PDF_PATH}")
    
    # First let's check if the server is actually running
    try:
        health_check = requests.get("http://localhost:8080/health", timeout=5)
        print(f"Server health check: {health_check.status_code}")
        if health_check.status_code != 200:
            print("Server is not responding correctly to health check")
    except Exception as e:
        print(f"Server health check failed: {str(e)}")
        print("Make sure the server is running with: cd document-service && uvicorn src.api.main:app --reload --port 8080")
        return None
    
    with open(TEST_PDF_PATH, "rb") as f:
        # Create a dictionary with file data
        files = {
            "file": (os.path.basename(TEST_PDF_PATH), f, "application/pdf")
        }
        
        # Create a dictionary with form data
        form_data = {
            "title": title,
            "description": description,
            "tags": tags
        }
        
        # Print request details for debugging
        print(f"API URL: {API_BASE_URL}/documents/")
        print(f"Auth header: Bearer {MOCK_TOKEN[:20]}...")
        print(f"Form data: {form_data}")
        
        try:
            # Send the POST request to upload the document
            response = requests.post(
                f"{API_BASE_URL}/documents/",
                headers={"Authorization": f"Bearer {MOCK_TOKEN}"},
                files=files,
                data=form_data,
                timeout=30  # Increased timeout
            )
            
            print(f"Upload response status: {response.status_code}")
            
            # Try to parse the response as JSON
            try:
                result = response.json()
                print(f"Response body: {result}")
            except:
                print(f"Response body: {response.text}")
            
            if response.status_code == 201:
                print(f"Document uploaded successfully with ID: {result.get('id')}")
                return result
            else:
                print(f"Error uploading document: {response.text}")
                return None
        except Exception as e:
            print(f"Exception during document upload: {str(e)}")
            return None

def test_api_get_document(document_id):
    """Test getting document by ID."""
    print(f"\n=== TESTING GET DOCUMENT API ===")
    if not document_id:
        print("No document ID provided, skipping test")
        return
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/documents/{document_id}",
            headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
        )
        
        print(f"Get document response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Document retrieved successfully:")
            print(f"Title: {result.get('title')}")
            print(f"Status: {result.get('status')}")
            return result
        else:
            print(f"Error getting document: {response.text}")
            return None
    except Exception as e:
        print(f"Exception during get document: {str(e)}")
        return None

def test_api_analyze_document(document_id):
    """Test document analysis via API."""
    print(f"\n=== TESTING DOCUMENT ANALYSIS API ===")
    if not document_id:
        print("No document ID provided, skipping test")
        return
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/documents/{document_id}/analyze",
            headers={"Authorization": f"Bearer {MOCK_TOKEN}"},
            data={"llm_model": "gpt-4o"}
        )
        
        print(f"Analysis response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Document analyzed successfully:")
            print(f"Summary: {result.get('summary', '')[:100]}...")
            print(f"Entities: {len(result.get('entities', []))} found")
            print(f"Risks: {len(result.get('risk_factors', []))} identified")
            return result
        else:
            print(f"Error analyzing document: {response.text}")
            return None
    except Exception as e:
        print(f"Exception during document analysis: {str(e)}")
        return None

def test_api_update_document(document_id):
    """Test updating document metadata."""
    print(f"\n=== TESTING UPDATE DOCUMENT API ===")
    if not document_id:
        print("No document ID provided, skipping test")
        return
    
    update_data = {
        "title": "Updated: State v. Smith Case",
        "description": "Updated description for the court case",
        "tags": ["legal", "court", "updated", "test"]
    }
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/documents/{document_id}",
            headers={
                "Authorization": f"Bearer {MOCK_TOKEN}",
                "Content-Type": "application/json"
            },
            json=update_data
        )
        
        print(f"Update response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Document updated successfully:")
            print(f"New title: {result.get('title')}")
            print(f"New tags: {result.get('tags')}")
            return result
        else:
            print(f"Error updating document: {response.text}")
            return None
    except Exception as e:
        print(f"Exception during document update: {str(e)}")
        return None

def test_api_list_documents():
    """Test listing all documents."""
    print("\n=== TESTING LIST DOCUMENTS API ===")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/documents/",
            headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
        )
        
        print(f"List documents response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Documents retrieved: {len(result)}")
            for i, doc in enumerate(result):
                print(f"{i+1}. {doc.get('title')} (ID: {doc.get('id')})")
            return result
        else:
            print(f"Error listing documents: {response.text}")
            return None
    except Exception as e:
        print(f"Exception during listing documents: {str(e)}")
        return None

def test_api_delete_document(document_id):
    """Test deleting a document."""
    print(f"\n=== TESTING DELETE DOCUMENT API ===")
    if not document_id:
        print("No document ID provided, skipping test")
        return
    
    try:
        response = requests.delete(
            f"{API_BASE_URL}/documents/{document_id}",
            headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
        )
        
        print(f"Delete response status: {response.status_code}")
        if response.status_code == 204:
            print("Document deleted successfully")
            return True
        else:
            print(f"Error deleting document: {response.text}")
            return False
    except Exception as e:
        print(f"Exception during document deletion: {str(e)}")
        return False

def run_all_tests():
    """Run all tests for the document service."""
    print("=== STARTING COMPREHENSIVE DOCUMENT SERVICE TESTS ===")
    print(f"Test document: {TEST_PDF_PATH}")
    print(f"API base URL: {API_BASE_URL}")
    
    # First let's check if the server is actually running
    try:
        health_check = requests.get("http://localhost:8080/health")
        print(f"Server health check: {health_check.status_code}")
        if health_check.status_code != 200:
            print("Server is not responding correctly to health check")
    except Exception as e:
        print(f"Server health check failed: {str(e)}")
        print("Make sure the server is running with: cd document-service && uvicorn src.api.main:app --reload --port 8080")
        return None
    
    # Test direct document analysis
    test_direct_analysis()
    
    # Test API functionality
    # 1. First upload the document
    uploaded_doc = test_api_upload()
    
    if uploaded_doc:
        document_id = uploaded_doc.get('id')
        
        # 2. Get the document by ID
        test_api_get_document(document_id)
        
        # 3. List all documents
        test_api_list_documents()
        
        # 4. Analyze the document
        test_api_analyze_document(document_id)
        
        # 5. Update the document
        test_api_update_document(document_id)
        
        # 6. Get updated document
        test_api_get_document(document_id)
        
        # 7. Delete the document
        test_api_delete_document(document_id)
        
        # 8. Verify deletion by trying to get it again
        test_api_get_document(document_id)
    
    print("\n=== DOCUMENT SERVICE TESTS COMPLETED ===")

if __name__ == "__main__":
    run_all_tests() 