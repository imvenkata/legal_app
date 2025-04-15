# Document Service

This service handles document storage, metadata management, and versioning for the Legal App.

## Features

- Document upload and download
- Document metadata management
- Document versioning
- Flexible storage backends (local filesystem or S3-compatible storage)
- Integration with auth service for user authentication

## Development Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- Minio (for S3 storage, optional)

### Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # Copy the example env file
   cp .env.example .env
   # Edit .env with your settings
   ```

### Database Setup

1. Create the database:
   ```bash
   # Using psql
   createdb document_db
   ```

2. Run migrations:
   ```bash
   alembic upgrade head
   ```

### Storage Setup

#### Local Storage
By default, the service uses local file storage in the `uploads` directory.

#### S3 Storage
To use S3-compatible storage:

1. Set `STORAGE_TYPE=s3` in your `.env` file
2. Configure the S3 settings in `.env`
3. If using Minio for development:
   ```bash
   docker run -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ":9001"
   ```

### Running the Service

```bash
uvicorn src.api.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

After starting the service, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker

To run using Docker:

```bash
docker-compose up
```

## Testing

```bash
pytest
``` 