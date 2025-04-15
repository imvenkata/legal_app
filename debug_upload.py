import os
import requests
import logging
from http.client import HTTPConnection

# Enable logging for requests
HTTPConnection.debuglevel = 1
logging.basicConfig(level=logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

# Configuration
PDF_PATH = "/Users/venkata/startup/legal_app/document-service/documents/state_v._smith.pdf"
API_URL = "http://localhost:8002/api/documents/"

# Check if the file exists
if not os.path.exists(PDF_PATH):
    print(f"Error: File {PDF_PATH} not found")
    exit(1)

print(f"File exists and size is {os.path.getsize(PDF_PATH)} bytes")

# Prepare the multipart form data
files = {
    'file': open(PDF_PATH, 'rb')
}

data = {
    'title': 'State v. Smith Case - Test Upload',
    'description': 'Legal case document for functionality testing',
    'tags': 'legal,test,upload,document',
}

headers = {
    "Authorization": "Bearer mock_token_for_testing"
}

try:
    # Make the request
    print("Sending upload request...")
    response = requests.post(
        API_URL,
        headers=headers,
        files=files,
        data=data
    )
    
    # Check the response
    print(f"Response status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response body: {response.text}")
    
except Exception as e:
    print(f"Exception occurred: {str(e)}")
finally:
    files['file'].close() 