# Auth Service

This service handles user authentication and management for the Legal App.

## Features

- User registration and login
- JWT token-based authentication
- User profile management
- Role-based access control

## Development Setup

### Prerequisites

- Python 3.8+
- PostgreSQL

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
   createdb auth_db
   ```

2. Run migrations:
   ```bash
   alembic upgrade head
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