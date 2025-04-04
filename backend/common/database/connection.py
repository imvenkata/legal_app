import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pymongo import MongoClient
import motor.motor_asyncio

# Load environment variables
load_dotenv()

# PostgreSQL connection
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "legal_ai")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "legal_ai")

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB]

# Async MongoDB connection for FastAPI
mongo_async_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
mongo_async_db = mongo_async_client[MONGO_DB]

# Database dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# MongoDB collections
documents_collection = mongo_db.documents
research_collection = mongo_db.research
contracts_collection = mongo_db.contracts
templates_collection = mongo_db.templates

# Async MongoDB collections
async_documents_collection = mongo_async_db.documents
async_research_collection = mongo_async_db.research
async_contracts_collection = mongo_async_db.contracts
async_templates_collection = mongo_async_db.templates
