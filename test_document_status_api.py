import requests
import json
import sys
import time

# Configuration
BASE_URL = "http://localhost:8002/api/documents"  # Document service URL
MOCK_TOKEN = "mock_token_for_testing"

def test_get_document_status(document_id):
    """Test getting document status."""
    print(f"\n=== TESTING GET DOCUMENT STATUS API ===")
    if not document_id:
        print("No document ID provided, skipping test")
        return
    
    try:
        response = requests.get(
            f"{BASE_URL}/{document_id}/status",
            headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
        )
        
        print(f"Get status response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Document status retrieved successfully:")
            print(f"Status: {result.get('status')}")
            print(f"Description: {result.get('description')}")
            print(f"Updated at: {result.get('updated_at')}")
            return result
        else:
            print(f"Error getting document status: {response.text}")
            return None
    except Exception as e:
        print(f"Exception during get document status: {str(e)}")
        return None

def test_update_document_status(document_id, new_status):
    """Test updating document status."""
    print(f"\n=== TESTING UPDATE DOCUMENT STATUS API ===")
    if not document_id:
        print("No document ID provided, skipping test")
        return
    
    try:
        response = requests.put(
            f"{BASE_URL}/{document_id}/status?status_value={new_status}",
            headers={
                "Authorization": f"Bearer {MOCK_TOKEN}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"Update status response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Document status updated successfully:")
            print(f"New status: {result.get('status')}")
            print(f"Description: {result.get('description')}")
            print(f"Updated at: {result.get('updated_at')}")
            return result
        else:
            print(f"Error updating document status: {response.text}")
            return None
    except Exception as e:
        print(f"Exception during update document status: {str(e)}")
        return None

def test_invalid_status_update(document_id):
    """Test updating document with an invalid status."""
    print(f"\n=== TESTING INVALID STATUS UPDATE ===")
    if not document_id:
        print("No document ID provided, skipping test")
        return
    
    try:
        response = requests.put(
            f"{BASE_URL}/{document_id}/status?status_value=invalid_status",
            headers={
                "Authorization": f"Bearer {MOCK_TOKEN}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"Invalid status update response status: {response.status_code}")
        if response.status_code == 400:
            print(f"Expected error received: {response.text}")
            return True
        else:
            print(f"Unexpected response: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Exception during invalid status update: {str(e)}")
        return False

def test_complete_workflow(document_id):
    """Test a complete document status workflow."""
    print(f"\n=== TESTING COMPLETE STATUS WORKFLOW ===")
    if not document_id:
        print("No document ID provided, skipping test")
        return
    
    workflow_steps = [
        "uploaded",
        "parsing",
        "parsing_completed",
        "analyzing",
        "analyzed"
    ]
    
    for step in workflow_steps:
        print(f"\nSetting document status to: {step}")
        result = test_update_document_status(document_id, step)
        if not result:
            print(f"Failed to update status to {step}")
            return False
        
        # Verify the status was updated correctly
        status = test_get_document_status(document_id)
        if not status or status.get('status') != step:
            print(f"Status verification failed for {step}")
            return False
        
        print(f"Successfully updated and verified status: {step}")
        time.sleep(1)  # Short delay between status updates
    
    print("\nComplete status workflow test passed!")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a document ID as command line argument")
        sys.exit(1)
    
    document_id = sys.argv[1]
    print(f"Testing document-status API for document ID: {document_id}")
    
    # Test getting document status
    test_get_document_status(document_id)
    
    # Test updating document status
    test_update_document_status(document_id, "parsing_completed")
    
    # Test invalid status update
    test_invalid_status_update(document_id)
    
    # Test complete workflow
    test_complete_workflow(document_id) 