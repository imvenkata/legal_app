# Legal Document Service

A comprehensive legal document management and analysis system that allows users to upload, store, analyze, and manage legal documents with AI-powered insights.

## Features

- **Document Management**
  - Upload and store legal documents (PDF, DOCX, etc.)
  - Organize documents with metadata, tags, and descriptions
  - Retrieve and list documents with pagination
  - Update document metadata
  - Delete documents

- **Document Analysis**
  - AI-powered document analysis using language models
  - Extract key points and summaries from legal documents
  - Identify potential issues and concerns
  - Customizable analysis prompts

- **API Integration**
  - RESTful API for all document operations
  - Comprehensive Postman collection for testing
  - Health check and environment debugging endpoints

- **Security**
  - User authentication and authorization
  - Secure document storage
  - API key management for external services

## Architecture

The system consists of multiple microservices:

1. **Document Service**: Handles document upload, storage, and management
2. **Analysis Service**: Processes documents using AI models
3. **User Service**: Manages user authentication and authorization
4. **API Gateway**: Provides a unified interface for all services

## Prerequisites

- Python 3.8+
- MongoDB
- PostgreSQL
- Docker and Docker Compose (optional)
- OpenAI API key (for document analysis)

## Setup

### Without Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/legal_app.git
   cd legal_app
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory with the following variables:
   ```
   # Database
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=legal_app
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   
   # MongoDB
   MONGODB_URI=mongodb://localhost:27017/legal_app
   
   # OpenAI
   OPENAI_API_KEY=your_openai_api_key
   
   # Service ports
   DOCUMENT_SERVICE_PORT=8002
   ANALYSIS_SERVICE_PORT=8003
   USER_SERVICE_PORT=8001
   API_GATEWAY_PORT=8000
   ```

5. **Initialize databases**
   ```bash
   # Start PostgreSQL and MongoDB
   # Then run migrations
   python -m document-service.src.db.migrations
   ```

6. **Run the services**
   ```bash
   # Start the document service
   cd document-service
   uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload
   
   # Start other services in separate terminals
   ```

### With Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/legal_app.git
   cd legal_app
   ```

2. **Set up environment variables**
   Create a `.env` file as described above.

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Check service status**
   ```bash
   docker-compose ps
   ```

## API Documentation

The API documentation is available at:
- Document Service: http://localhost:8002/docs
- Analysis Service: http://localhost:8003/docs
- User Service: http://localhost:8001/docs
- API Gateway: http://localhost:8000/docs

## Testing

### Postman Collection

A Postman collection is provided for testing the API:

1. Import the collection from `postman/output/document_service_collection.json`
2. Set the environment variables:
   - `base_url`: http://localhost:8002
   - `document_id`: (will be set automatically after document creation)
   - `test_document_path`: /path/to/your/test/document.pdf

3. Run the collection in sequence to test the complete workflow

### Automated Tests

Run the automated tests with:
```bash
pytest
```

## Development

### Project Structure

```
legal_app/
├── document-service/       # Document management service
│   ├── src/
│   │   ├── api/           # API routes
│   │   │   └── core/          # Core functionality
│   │   │   └── db/            # Database models and migrations
│   │   │   └── services/      # Business logic
│   │   │   └── main.py        # Application entry point
│   │   ├── tests/             # Test files
│   │   └── Dockerfile         # Docker configuration
│   ├── analysis-service/       # Document analysis service
│   ├── user-service/           # User management service
│   ├── api-gateway/            # API gateway service
│   ├── postman/                # Postman collection and tests
│   ├── docker-compose.yml      # Docker Compose configuration
│   └── README.md               # This file
```

### Adding New Features

1. Create a new branch for your feature
2. Implement the feature in the appropriate service
3. Add tests for the new functionality
4. Update the Postman collection if needed
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check if the database services are running
   - Verify the connection parameters in the `.env` file

2. **Document Upload Failures**
   - Ensure the document file exists and is accessible
   - Check file permissions
   - Verify the file format is supported

3. **Analysis Service Errors**
   - Confirm the OpenAI API key is valid
   - Check if the document has been successfully parsed

### Logs

Logs are available in the following locations:
- Docker: `docker-compose logs [service-name]`
- Local: `logs/` directory in each service

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please contact [your-email@example.com](mailto:your-email@example.com). 