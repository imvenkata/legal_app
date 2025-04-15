# Document Service API Postman Collection

This Postman collection provides a comprehensive set of API requests for interacting with the Legal Document Service. It includes examples for all major endpoints with sample responses.

## How to Import the Collection

1. Open Postman
2. Click on the "Import" button in the top left corner
3. Choose "File" and select the `document_service_collection.json` file
4. Click "Import" to add the collection to your workspace

## Collection Overview

The collection is organized into the following folders:

### Health Checks
- **Health Check**: Check if the service is running properly
- **Environment Debug**: View environment configuration (useful for troubleshooting)

### Documents
- **Upload Document**: Upload a new document to the service
- **Get All Documents**: List all documents for the current user
- **Get Document**: Retrieve a specific document by ID
- **Update Document**: Modify a document's metadata
- **Delete Document**: Remove a document and its associated data
- **Get Document Status**: Check the current processing status of a document
- **Update Document Status**: Change a document's status

### Analysis
- **Analyze Document**: Start AI analysis of a document
- **Get Document Analysis**: Retrieve analysis results

### Chat
- **Chat with Document**: Have a conversation with a document using AI

## Variables

The collection includes a variable:

- `document_id`: ID of a document in the system (default value is set to a sample document)

You can update this variable by:
1. Clicking on the collection name
2. Going to the "Variables" tab
3. Modifying the "CURRENT VALUE" column

## Authentication

The API currently uses a mock user ID (123) for testing purposes. In a production environment, proper authentication would be required.

## Prerequisites

To use this collection:

1. The Document Service API must be running (typically at http://localhost:8002)
2. MongoDB must be available
3. The OpenAI API key must be properly configured in the service

## Example Workflow

1. Upload a document using the "Upload Document" request
2. Copy the returned document ID to the collection variable
3. Check the document status until it shows "parsing_completed"
4. Analyze the document using "Analyze Document"
5. View the analysis results with "Get Document Analysis"
6. Chat with the document using "Chat with Document" 