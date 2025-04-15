import requests
import json
import time
import os
import sys

# API Configuration
BASE_URL = "http://localhost:8002/api"
MOCK_TOKEN = "mock_token_for_testing"

DOCUMENT_PATH = "/Users/venkata/startup/legal_app/document-service/documents/state_v._smith.pdf"

def test_document_upload():
    """Test uploading a document to the API"""
    print("\n1. Testing document upload...")
    url = f"{BASE_URL}/documents/"
    
    file_obj = open(DOCUMENT_PATH, 'rb')
    files = {
        'file': ('state_v._smith.pdf', file_obj, 'application/pdf')
    }
    
    data = {
        'title': 'State v. Smith Legal Case',
        'description': 'Sample legal document for testing',
        'tags': 'legal,case,test'
    }
    
    try:
        response = requests.post(url, files=files, data=data)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"Document uploaded successfully. ID: {result['id']}")
            return result['id']
        else:
            print(f"Error: {response.text}")
            return None
    finally:
        file_obj.close()

def test_get_document(document_id):
    """Test getting document details"""
    print("\n2. Testing document retrieval...")
    url = f"{BASE_URL}/documents/{document_id}"
    
    response = requests.get(url)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Document details: {json.dumps(result, indent=2)}")
        return result
    else:
        print(f"Error: {response.text}")
        return None

def test_document_analysis(document_id):
    """Test document analysis"""
    print("\n3. Testing document analysis...")
    
    # First, check document status
    url = f"{BASE_URL}/documents/{document_id}"
    max_retries = 10
    retry_count = 0
    
    while retry_count < max_retries:
        response = requests.get(url)
        if response.status_code == 200:
            status = response.json().get('status')
            print(f"Current document status: {status}")
            
            if status in ["parsing_completed", "analyzed"]:
                break
            elif status in ["parsing_failed", "error"]:
                print("Document parsing failed.")
                return None
        
        print("Waiting for document to be ready for analysis...")
        time.sleep(3)
        retry_count += 1
    
    if retry_count >= max_retries:
        print("Timed out waiting for document to be ready.")
        return None
    
    # If document is already analyzed, get the analysis result instead of analyzing again
    if status == "analyzed":
        print("Document already analyzed. Getting analysis result...")
        analysis_url = f"{BASE_URL}/documents/{document_id}/analysis"
        response = requests.get(analysis_url)
    else:
        # Proceed with analysis
        print("Document ready for analysis. Starting analysis...")
        analysis_url = f"{BASE_URL}/documents/{document_id}/analyze"
        data = {'llm_model': 'gpt-4o'}
        response = requests.post(analysis_url, data=data)
    
    print(f"Analysis status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Analysis result: {json.dumps(result, indent=2)}")
        return result
    else:
        print(f"Analysis error: {response.text}")
        return None

def test_document_chat(document_id):
    """Test document chat"""
    print("\n4. Testing document chat...")
    url = f"{BASE_URL}/chat/{document_id}"
    
    data = {
        "message": "What are the key legal issues in this document?"
    }
    
    response = requests.post(url, json=data)
    print(f"Chat status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"AI response: {result['messages'][-1]['content']}")
        
        # Ask a follow-up question
        print("\n5. Testing follow-up question...")
        data = {
            "message": "Who are the main parties involved in this case?"
        }
        
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"AI response: {result['messages'][-1]['content']}")
        else:
            print(f"Follow-up chat error: {response.text}")
            
        return result
    else:
        print(f"Chat error: {response.text}")
        return None

def test_document_deletion(document_id):
    """Test document deletion"""
    print("\n6. Testing document deletion...")
    url = f"{BASE_URL}/documents/{document_id}"
    
    response = requests.delete(url)
    print(f"Deletion status code: {response.status_code}")
    
    if response.status_code == 204:
        print("Document deleted successfully.")
        return True
    else:
        print(f"Deletion error: {response.text}")
        return False

if __name__ == "__main__":
    # Check if a document ID was provided as an argument
    if len(sys.argv) > 1:
        document_id = sys.argv[1]
        print(f"Using provided document ID: {document_id}")
    else:
        # Run the upload test to get a document ID
        document_id = test_document_upload()
    
    if document_id:
        test_get_document(document_id)
        analysis_result = test_document_analysis(document_id)
        
        if analysis_result:
            chat_result = test_document_chat(document_id)
        
        # Uncomment to test deletion
        # test_document_deletion(document_id) 