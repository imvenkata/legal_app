"""
Test script for document upload functionality.
"""
import os
import requests
import json
import time

# Configuration
PDF_PATH = "/Users/venkata/startup/legal_app/document-service/documents/state_v._smith.pdf"
API_URL = "http://localhost:8002/api/documents/"
HEADERS = {"Authorization": "Bearer mock_token_for_testing"}

def test_document_upload():
    """Test uploading a document."""
    print(f"Testing document upload with file: {PDF_PATH}")
    
    # Check if the file exists
    if not os.path.exists(PDF_PATH):
        print(f"Error: File {PDF_PATH} not found")
        return None
    
    print(f"File exists and size is {os.path.getsize(PDF_PATH)} bytes")
    
    # Prepare the multipart form data
    data = {
        'title': 'State v. Smith Case - Test Upload',
        'description': 'Legal case document for functionality testing',
        'tags': 'legal,test,upload,document',
    }
    
    try:
        # Make the request
        print("Sending upload request...")
        file_obj = open(PDF_PATH, 'rb')
        files = {
            'file': ('state_v._smith.pdf', file_obj, 'application/pdf')
        }
        
        response = requests.post(
            API_URL,
            headers=HEADERS,
            files=files,
            data=data
        )
        
        # Check the response
        print(f"Response status code: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print("Document uploaded successfully!")
            print(f"Document ID: {result.get('id')}")
            print(f"Document Title: {result.get('title')}")
            print(f"Document Status: {result.get('status')}")
            return result.get('id')
        else:
            print(f"Error uploading document: {response.text}")
            return None
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return None
    finally:
        file_obj.close()

def test_document_status(document_id):
    """Test checking document status after upload."""
    if not document_id:
        print("No document ID provided, skipping status check")
        return
    
    print(f"\nChecking status for document ID: {document_id}")
    
    try:
        # Poll for status changes
        for i in range(5):  # Try up to 5 times
            print(f"Status check attempt {i+1}...")
            response = requests.get(
                f"{API_URL}{document_id}",
                headers=HEADERS
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('status')
                print(f"Current status: {status}")
                
                if status in ["parsing_completed", "analyzed"]:
                    print("Document processing completed successfully!")
                    return status
                elif status in ["parsing_failed", "error"]:
                    print("Document processing failed.")
                    return status
            else:
                print(f"Error checking status: {response.text}")
            
            # Wait before next check
            print("Waiting 3 seconds before next check...")
            time.sleep(3)
        
        print("Maximum attempts reached, final status unknown.")
        return None
    
    except Exception as e:
        print(f"Exception during status check: {str(e)}")
        return None

if __name__ == "__main__":
    # Test document upload
    document_id = test_document_upload()
    
    if document_id:
        # Test document status checking
        test_document_status(document_id)
    else:
        print("Upload failed, cannot proceed with status checking.") 