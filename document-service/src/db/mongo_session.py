import motor.motor_asyncio
import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

MONGO_DETAILS = os.getenv("MONGODB_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "document_service")

if not MONGO_DETAILS:
    logging.warning("MONGODB_URL environment variable not set. MongoDB features will not work.")
    client = None
    db = None
else:
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
        db = client[MONGO_DB_NAME]
        logging.info(f"Successfully connected to MongoDB database: {MONGO_DB_NAME}")
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        client = None
        db = None

def get_mongo_db():
    """Dependency function to get the MongoDB database instance."""
    if db is None:
        raise RuntimeError("MongoDB connection is not available. Check configuration.")
    return db

async def get_document_collection():
    """Returns the collection for storing parsed document text."""
    if db is None:
        raise RuntimeError("MongoDB connection is not available.")
    return db.get_collection("parsed_documents")

async def get_chat_collection():
    """Returns the collection for storing chat sessions."""
    if db is None:
        raise RuntimeError("MongoDB connection is not available.")
    return db.get_collection("chat_sessions")

async def get_analysis_collection():
    """Returns the collection for storing document analysis results."""
    if db is None:
        raise RuntimeError("MongoDB connection is not available.")
    return db.get_collection("document_analysis")

# Optional: Add startup/shutdown logic if needed for connection pooling or cleanup
async def connect_to_mongo():
    global client, db
    MONGO_DETAILS = os.getenv("MONGODB_URL")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "document_service")
    if MONGO_DETAILS:
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
            db = client[MONGO_DB_NAME]
            # You might want to ping the server to ensure connection
            await client.admin.command('ping') 
            logging.info(f"MongoDB connected: {MONGO_DB_NAME}")
        except Exception as e:
            logging.error(f"MongoDB connection failed on startup: {e}")
            client = None
            db = None
    else:
        logging.warning("MONGODB_URL not set, MongoDB connection skipped.")

async def close_mongo_connection():
    global client
    if client:
        client.close()
        logging.info("MongoDB connection closed.")

# Example usage in FastAPI startup/shutdown events (in main.py):
# app.add_event_handler("startup", connect_to_mongo)
# app.add_event_handler("shutdown", close_mongo_connection) 