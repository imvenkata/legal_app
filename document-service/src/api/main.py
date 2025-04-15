from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Dict, Any
import logging
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from .routes import documents, versions, chat
from src.db.mongo_session import db as mongo_db, connect_to_mongo, close_mongo_connection
from src.core.storage import get_storage_service
from src.core.parser import extract_text_from_content
from src.db import mongo_crud, crud
from src.db.session import get_db
from src.db.models import DocumentCreate, DocumentStatus
from src.db.init_db import init_db

# Set up logging
logging.basicConfig(level=logging.INFO) # Use INFO for less verbose logs in production
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Document Service API",
    description="Document storage and metadata management service for Legal App",
    version="0.1.0",
)

# Initialize database tables on startup
@app.on_event("startup")
async def startup_db_client():
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialization complete")
    
    # Connect to MongoDB
    logger.info("Connecting to MongoDB...")
    await connect_to_mongo()
    logger.info("MongoDB connection initialized")

@app.on_event("shutdown")
async def shutdown_db_client():
    logger.info("Closing MongoDB connection...")
    await close_mongo_connection()
    logger.info("MongoDB connection closed")

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    # Add any frontend URLs here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log basic request info
    logger.info(f"Request: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        # Log response status
        logger.info(f"Response: {response.status_code}")
        return response
    except Exception as e:
        # Log exceptions during request processing
        logger.exception(f"Error processing request {request.method} {request.url.path}: {e}")
        # Re-raise the exception to let FastAPI handle it (e.g., return 500)
        raise e

# Include routers (without auth dependency)
app.include_router(
    documents.router,
    prefix="/api/documents",
    tags=["documents"]
)

app.include_router(
    versions.router,
    prefix="/api/versions",
    tags=["versions"]
)

app.include_router(
    chat.router,
    prefix="/api/chat", # Assuming chat routes also live under /api?
    tags=["chat"]
)

@app.get("/", tags=["Health"])
def read_root():
    logger.info("Root endpoint accessed")
    return {"status": "ok", "service": "document-service"}

@app.get("/health", tags=["Health"])
def health_check():
    logger.info("Health check endpoint accessed")
    return {
        "status": "healthy",
        "version": app.version,
        "storage_type": os.getenv("STORAGE_TYPE", "local")
    }

@app.get("/debug/mongo", tags=["Debug"])
async def debug_mongo():
    """Debug endpoint to check MongoDB connection."""
    logger.info("MongoDB debug endpoint accessed")
    mongo_url = os.getenv("MONGODB_URL", "Not set")
    mongo_db_name = os.getenv("MONGO_DB_NAME", "Not set")
    
    result = {
        "mongodb_url": mongo_url,
        "mongo_db_name": mongo_db_name,
        "mongo_client_initialized": mongo_db is not None
    }
    
    # Try to ping MongoDB
    if mongo_db is not None:
        try:
            # Try to access a collection
            await mongo_db.get_collection("test").find_one({"_id": "test"})
            result["connection_test"] = "success"
            
            # Check the specific collections we need
            collections = await mongo_db.list_collection_names()
            result["collections"] = collections
            
            # Check if we can access the parsed_documents collection
            try:
                parsed_docs = await mongo_db.get_collection("parsed_documents").count_documents({})
                result["parsed_documents_count"] = parsed_docs
            except Exception as e:
                result["parsed_documents_error"] = str(e)
                
        except Exception as e:
            result["connection_test"] = "failed"
            result["error"] = str(e)
    else:
        result["connection_test"] = "skipped - client not initialized"
    
    return result 

@app.get("/debug/storage", tags=["Debug"])
async def debug_storage():
    """Debug endpoint to check storage service."""
    logger.info("Storage debug endpoint accessed")
    storage_type = os.getenv("STORAGE_TYPE", "local")
    storage_path = os.getenv("STORAGE_PATH", "uploads")
    
    result = {
        "storage_type": storage_type,
        "storage_path": storage_path
    }
    
    # Try to interact with the storage service
    try:
        try:
            # First check if the storage service initializes correctly
            storage = get_storage_service()
            result["storage_service_class"] = storage.__class__.__name__
            result["storage_service_initialized"] = True
        except Exception as init_e:
            logger.exception("Storage service initialization error")
            result["storage_service_initialized"] = False
            result["init_error"] = str(init_e)
            return result
        
        # Try to list files in uploads directory
        if storage_type == "local":
            try:
                # Check directory directly
                if os.path.exists(storage_path):
                    files = os.listdir(storage_path)
                    result["files_count"] = len(files)
                    result["files_sample"] = files[:5] if files else []  # Just show the first 5 files
                else:
                    result["directory_exists"] = False
            except Exception as dir_e:
                logger.exception("Error accessing upload directory")
                result["directory_error"] = str(dir_e)
    except Exception as e:
        logger.exception("Unhandled exception in storage debug endpoint")
        result["error"] = str(e)
        result["error_type"] = type(e).__name__
    
    return result 

@app.get("/debug/env", tags=["Debug"])
def debug_env():
    """Debug endpoint to check environment variables."""
    logger.info("Environment debug endpoint accessed")
    
    # Gather all relevant environment variables
    env_vars = {
        "DATABASE_URL": os.getenv("DATABASE_URL", "Not set"),
        "MONGODB_URL": os.getenv("MONGODB_URL", "Not set"),
        "MONGO_DB_NAME": os.getenv("MONGO_DB_NAME", "Not set"),
        "STORAGE_TYPE": os.getenv("STORAGE_TYPE", "Not set"),
        "STORAGE_PATH": os.getenv("STORAGE_PATH", "Not set"),
        "AUTH_SERVICE_URL": os.getenv("AUTH_SERVICE_URL", "Not set"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "Not set"),
        "PORT": os.getenv("PORT", "Not set"),
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "Not set"),
        "DEEPSEEK_API_KEY": "Set but hidden for security" if os.getenv("DEEPSEEK_API_KEY") else "Not set",
        "OPENAI_API_KEY": "Set but hidden for security" if os.getenv("OPENAI_API_KEY") else "Not set",
    }
    
    # Check if upload directory exists and is writable
    uploads_path = os.getenv("STORAGE_PATH", "uploads")
    path_info = {
        "path": uploads_path,
        "exists": os.path.exists(uploads_path),
        "is_dir": os.path.isdir(uploads_path) if os.path.exists(uploads_path) else False,
        "writable": os.access(uploads_path, os.W_OK) if os.path.exists(uploads_path) else False,
    }
    
    if path_info["exists"] and path_info["is_dir"]:
        path_info["file_count"] = len(os.listdir(uploads_path))
        path_info["files"] = os.listdir(uploads_path)[:5]  # First 5 files
    
    # Add module availability checks
    try:
        import motor.motor_asyncio
        motor_available = True
    except ImportError:
        motor_available = False
        
    try:
        from PyPDF2 import PdfReader
        pypdf2_available = True
    except ImportError:
        pypdf2_available = False
        
    modules = {
        "motor": motor_available,
        "PyPDF2": pypdf2_available
    }
    
    return {
        "environment": env_vars,
        "uploads_path": path_info,
        "modules": modules,
        "cwd": os.getcwd()
    } 

@app.get("/debug/parse", tags=["Debug"])
async def debug_parse():
    """Debug endpoint to test file parsing."""
    logger.info("Parser debug endpoint accessed")
    
    # Try to find a file to parse
    uploads_path = os.getenv("STORAGE_PATH", "uploads")
    if not os.path.exists(uploads_path) or not os.path.isdir(uploads_path):
        return {"error": f"Uploads directory {uploads_path} does not exist or is not a directory"}
    
    files = os.listdir(uploads_path)
    result = {"available_files": len(files)}
    
    # Find a suitable test file
    test_file = None
    for file in files:
        if file.endswith('.pdf'):
            test_file = file
            break
    
    if not test_file:
        for file in files:
            if file.endswith('.txt') or file.endswith('.md'):
                test_file = file
                break
    
    if not test_file:
        return {"error": "No suitable test file found in uploads directory", "files": files[:5]}
    
    # Try to read and parse the file
    result["test_file"] = test_file
    file_path = os.path.join(uploads_path, test_file)
    file_type = os.path.splitext(test_file)[1][1:]  # Get extension without dot
    
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            result["file_size"] = len(content)
            
            # Try to parse the file
            try:
                extracted_text = await extract_text_from_content(content, file_type)
                result["parsing_success"] = True
                result["extracted_text_length"] = len(extracted_text)
                result["extracted_text_sample"] = extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
            except Exception as parse_e:
                logger.exception(f"Error parsing file {test_file}")
                result["parsing_success"] = False
                result["parsing_error"] = str(parse_e)
    except Exception as file_e:
        logger.exception(f"Error reading file {test_file}")
        result["file_read_success"] = False
        result["file_error"] = str(file_e)
    
    return result 

@app.get("/debug/mongo-save", tags=["Debug"])
async def debug_mongo_save():
    """Debug endpoint to test saving parsed text to MongoDB."""
    logger.info("MongoDB save debug endpoint accessed")
    
    # Generate a test document ID
    test_id = f"test_{uuid.uuid4()}"
    test_text = f"This is a test document with ID {test_id}. Generated on {datetime.now().isoformat()}."
    
    result = {
        "test_id": test_id,
        "test_text_length": len(test_text)
    }
    
    # Try to save to MongoDB
    try:
        save_success = await mongo_crud.save_parsed_document(test_id, test_text)
        result["save_success"] = save_success
        
        if save_success:
            # Try to retrieve it back
            retrieved_text = await mongo_crud.get_parsed_document_text(test_id)
            result["retrieval_success"] = retrieved_text is not None
            result["text_match"] = retrieved_text == test_text
            
            # Delete the test document
            delete_success = await mongo_crud.delete_parsed_document(test_id)
            result["delete_success"] = delete_success
    except Exception as e:
        logger.exception(f"Error in MongoDB save test")
        result["error"] = str(e)
        result["error_type"] = type(e).__name__
    
    return result 

@app.get("/debug/sql", tags=["Debug"])
def debug_sql(db: Session = Depends(get_db)):
    """Debug endpoint to test SQL database operations."""
    logger.info("SQL debug endpoint accessed")
    
    # Create a mock user ID
    mock_user_id = "999"
    
    result = {
        "database_url": os.getenv("DATABASE_URL", "Not set"),
        "mock_user_id": mock_user_id
    }
    
    try:
        # Create a test document with the correct field names according to the model
        doc_data = DocumentCreate(
            title="Test Document",
            description="This is a test document",
            filename="test.txt",
            file_size=123,
            file_type="txt",
            storage_path=f"test_{uuid.uuid4()}.txt",
            tags=["test", "debug"],
            owner_id=int(mock_user_id)
        )
        
        # Try to save to database
        db_document = crud.create_document_db(db, doc_data)
        result["document_created"] = db_document is not None
        
        if db_document:
            result["document_id"] = str(db_document.id)
            
            # Get document back to verify - we need to pass user_id
            retrieved = crud.get_document_db(db, str(db_document.id), mock_user_id)
            result["retrieval_success"] = retrieved is not None
            
            if retrieved:
                result["document_fields"] = {
                    "id": str(retrieved.id),
                    "title": retrieved.title,
                    "status": retrieved.status.value if hasattr(retrieved.status, 'value') else retrieved.status
                }
                
                # Delete the test document - we need to pass user_id
                deleted = crud.delete_document_db(db, str(retrieved.id), mock_user_id)
                result["document_deleted"] = deleted
    except Exception as e:
        logger.exception(f"Error in SQL database test")
        result["error"] = str(e)
        result["error_type"] = type(e).__name__
    
    return result