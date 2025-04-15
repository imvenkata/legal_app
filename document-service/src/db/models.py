from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, BigInteger, ARRAY, Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY as PG_ARRAY
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
import datetime
import uuid
import sqlalchemy
from enum import Enum

# Define SQLAlchemy Base
Base = declarative_base()

# --- Enums --- 
class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    PARSING_FAILED = "parsing_failed"
    PARSING_COMPLETED = "parsing_completed" # Text extraction successful
    ANALYZING = "analyzing"
    ANALYSIS_FAILED = "analysis_failed"
    ANALYZED = "analyzed" # Full analysis (summary, etc.) complete
    DELETING = "deleting"
    DELETED = "deleted"
    ERROR = "error" # General error state

# SQLAlchemy Models
class DocumentTable(Base):
    """SQLAlchemy document model."""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    filename = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String, nullable=False)
    storage_path = Column(String, nullable=False, unique=True)
    owner_id = Column(Integer, nullable=False, index=True)
    tags = Column(PG_ARRAY(String), nullable=True)
    status = Column(SQLAlchemyEnum(DocumentStatus), default=DocumentStatus.UPLOADED, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DocumentAnalysisTable(Base):
    """SQLAlchemy document analysis model."""
    __tablename__ = "document_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    summary = Column(Text, nullable=True)
    entities = Column(JSONB, nullable=True)
    risk_factors = Column(JSONB, nullable=True)
    recommendations = Column(JSONB, nullable=True)
    model_used = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DocumentVersionTable(Base):
    """SQLAlchemy document version model."""
    __tablename__ = "document_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    filename = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String, nullable=False)
    storage_path = Column(String, nullable=False, unique=True)
    created_by = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        # Ensure document_id + version_number is unique
        sqlalchemy.UniqueConstraint('document_id', 'version_number', name='uix_document_version'),
    )

# Create aliases for compatibility
Document = DocumentTable
DocumentVersion = DocumentVersionTable
DocumentAnalysis = DocumentAnalysisTable

# Pydantic Models
class DocumentBase(BaseModel):
    """Base document model."""
    title: str
    description: Optional[str] = None
    filename: str
    file_size: int
    file_type: str
    storage_path: str
    owner_id: int
    tags: Optional[List[str]] = []

class DocumentCreate(DocumentBase):
    """Document creation model."""
    pass

class DocumentUpdate(BaseModel):
    """Document update model."""
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class DocumentResponse(DocumentBase):
    """Document response model."""
    id: str
    created_at: str
    updated_at: Optional[str] = None
    status: Optional[str] = "uploaded"

    class Config:
        from_attributes = True
        json_encoders = {
            uuid.UUID: lambda v: str(v),
            datetime.datetime: lambda v: v.isoformat()
        }

class DocumentVersionBase(BaseModel):
    """Base document version model."""
    document_id: str
    filename: str
    file_size: int
    file_type: str
    storage_path: str
    created_by: int
    comment: Optional[str] = None

class DocumentVersionCreate(DocumentVersionBase):
    """Document version creation model."""
    pass

class DocumentVersionResponse(DocumentVersionBase):
    """Document version response model."""
    id: str
    version_number: int
    created_at: str

    class Config:
        from_attributes = True

# Document Analysis Models
class DocumentAnalysisResult(BaseModel):
    """Model for document analysis results."""
    document_id: str
    summary: str
    entities: Union[List[Dict[str, Any]], List[str]]
    risk_factors: List[str]
    recommendations: List[str]
    model_used: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

# Document Chat Models
class ChatMessage(BaseModel):
    """Model for chat messages about documents."""
    role: str  # 'user' or 'assistant'
    content: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    """Model for document chat requests."""
    message: str
    document_id: str
    
    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    """Model for document chat responses."""
    document_id: str
    messages: List[ChatMessage]
    created_at: Optional[datetime.datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {datetime.datetime: lambda dt: dt.isoformat()}

# Additional models for API communication
class DocumentSummary(BaseModel):
    """Document summary model for search results."""
    id: str
    title: str
    description: Optional[str] = None
    file_type: str
    tags: List[str] = []
    created_at: str

class DocumentStatusResponse(BaseModel):
    """Document status response model."""
    document_id: str
    status: str
    description: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True

# --- Pydantic Schemas for MongoDB Data --- 

class ParsedDocumentMongo(BaseModel):
    # Use document_id from SQL as the _id in Mongo for easy linking
    id: str = Field(..., alias="_id") 
    document_id: str # Redundant but explicit link
    extracted_text: str
    parsed_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

    class Config:
        populate_by_name = True # Allows using alias _id
        json_encoders = {datetime.datetime: lambda dt: dt.isoformat()}

class ChatMessageMongo(BaseModel):
    role: str # "user" or "assistant"
    content: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

class ChatSessionMongo(BaseModel):
    # Use a composite key or generate a unique session ID if preferred
    id: str = Field(..., alias="_id") # e.g., f"{user_id}:{document_id}"
    user_id: str
    document_id: str
    messages: List[ChatMessageMongo] = []
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

    class Config:
        populate_by_name = True
        json_encoders = {datetime.datetime: lambda dt: dt.isoformat()}

# --- Mock User Model (replace with your actual auth logic) ---
class User(BaseModel):
    id: str
    username: str
    # ... other fields 