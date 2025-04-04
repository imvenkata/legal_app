from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# User models
class UserBase(BaseModel):
    email: str
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    is_active: bool = True
    created_at: datetime
    
    class Config:
        orm_mode = True

# Document models
class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None

class DocumentCreate(DocumentBase):
    user_id: str
    file_type: str

class Document(DocumentBase):
    id: str
    user_id: str
    file_path: str
    file_type: str
    status: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class DocumentAnalysis(BaseModel):
    document_id: str
    summary: str
    key_points: List[str]
    entities: Dict[str, List[str]]
    recommendations: List[str]
    llm_model: str
    
    class Config:
        orm_mode = True

# Research models
class ResearchQuery(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None

class ResearchCase(BaseModel):
    id: str
    title: str
    content: str
    source: str
    relevance_score: float
    
    class Config:
        orm_mode = True

class PredictionRequest(BaseModel):
    case_details: Dict[str, Any]
    llm_model: str

class PredictionResult(BaseModel):
    prediction: str
    confidence: float
    factors: List[Dict[str, Any]]
    similar_cases: List[Dict[str, Any]]
    
    class Config:
        orm_mode = True

# Contract models
class ContractTemplate(BaseModel):
    id: str
    name: str
    description: str
    category: str
    parameters: List[Dict[str, Any]]
    
    class Config:
        orm_mode = True

class ContractGeneration(BaseModel):
    template_id: str
    parameters: Dict[str, Any]
    llm_model: str

class ContractResult(BaseModel):
    id: str
    title: str
    content: str
    template_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    
    class Config:
        orm_mode = True

# LLM models
class LLMRequest(BaseModel):
    prompt: str
    model: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7

class LLMResponse(BaseModel):
    text: str
    model: str
    usage: Dict[str, Any]
