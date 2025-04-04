# Legal AI Application - Technical Documentation

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Backend Implementation](#backend-implementation)
3. [Frontend Implementation](#frontend-implementation)
4. [LLM Integration](#llm-integration)
5. [API Reference](#api-reference)
6. [Database Schema](#database-schema)
7. [Deployment Procedures](#deployment-procedures)
8. [Security Considerations](#security-considerations)
9. [Performance Optimization](#performance-optimization)
10. [Troubleshooting](#troubleshooting)

## System Architecture

### Overview
The Legal AI Application is built using a microservices architecture with a Python/FastAPI backend, React frontend, and a flexible LLM adapter layer that supports multiple AI models (OpenAI GPT, Google Gemini, and DeepSeek).

### Architecture Diagram
```
┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │
│  React Frontend │◄────┤  API Gateway    │
│                 │     │  (FastAPI)      │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │                 │
         └─────────────►│  Authentication │
                        │  Service        │
                        └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│ Document        │    │ Legal Research  │    │ Contract        │
│ Service         │◄───┤ Service         │◄───┤ Service         │
│                 │    │                 │    │                 │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         │                      ▼                      │
         │             ┌─────────────────┐             │
         └────────────►│                 │◄────────────┘
                       │  LLM Adapter    │
                       │  Layer          │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │                 │
                       │  LLM Models     │
                       │  (GPT/Gemini/   │
                       │   DeepSeek)     │
                       └─────────────────┘
```

### Component Descriptions

#### API Gateway
- Entry point for all client requests
- Handles routing to appropriate microservices
- Manages authentication and authorization
- Implements CORS and security middleware

#### Microservices
1. **Document Service**: Handles document upload, storage, and analysis
2. **Legal Research Service**: Manages legal case search and outcome prediction
3. **Contract Service**: Handles contract template management and generation

#### LLM Adapter Layer
- Provides a unified interface to different LLM models
- Handles model-specific formatting and parameters
- Manages API keys and rate limiting
- Implements caching for improved performance

#### Database Layer
- PostgreSQL for structured data (users, documents metadata, etc.)
- MongoDB for semi-structured data (analysis results, predictions)
- Vector database for semantic search capabilities

## Backend Implementation

### Technology Stack
- **Framework**: FastAPI 0.95.0
- **Python Version**: 3.10+
- **Authentication**: JWT with Python-JOSE
- **Database ORM**: SQLAlchemy
- **API Documentation**: Swagger/OpenAPI
- **Testing**: Pytest

### Directory Structure
```
backend/
├── api_gateway/
│   ├── app.py                 # Main FastAPI application
│   ├── auth/                  # Authentication modules
│   ├── middleware/            # Custom middleware
│   └── routers/               # API route definitions
├── services/
│   ├── document_service/      # Document analysis service
│   ├── research_service/      # Legal research service
│   └── contract_service/      # Contract generation service
├── llm_adapter/
│   ├── adapters/              # Model-specific adapters
│   │   ├── base_adapter.py    # Base adapter interface
│   │   ├── openai_adapter.py  # OpenAI GPT adapter
│   │   ├── gemini_adapter.py  # Google Gemini adapter
│   │   └── deepseek_adapter.py # DeepSeek adapter
│   └── factory.py             # Adapter factory
├── common/
│   ├── database/              # Database connections
│   ├── models/                # Shared data models
│   └── utils/                 # Utility functions
└── requirements.txt           # Python dependencies
```

### Key Implementation Details

#### API Gateway
The API Gateway is implemented using FastAPI and serves as the central entry point for all client requests. It includes:

```python
# app.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from routers import documents, research, contracts, users

app = FastAPI(title="Legal AI API Gateway")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(research.router, prefix="/research", tags=["Research"])
app.include_router(contracts.router, prefix="/contracts", tags=["Contracts"])

@app.get("/")
async def root():
    return {"message": "Welcome to Legal AI API Gateway"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

#### Authentication
Authentication is implemented using JWT tokens with the following flow:

1. User submits credentials to `/auth/login`
2. Server validates credentials and issues a JWT token
3. Client includes token in Authorization header for subsequent requests
4. Server validates token and identifies user for each protected endpoint

```python
# auth/jwt.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception
```

#### LLM Adapter Layer
The LLM Adapter Layer provides a unified interface to different LLM models:

```python
# llm_adapter/base_adapter.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseLLMAdapter(ABC):
    """Base adapter interface for LLM models."""
    
    @abstractmethod
    async def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate text based on a prompt."""
        pass
    
    @abstractmethod
    async def analyze_document(self, document_text: str) -> Dict[str, Any]:
        """Analyze a legal document and return structured information."""
        pass
    
    @abstractmethod
    async def predict_outcome(self, case_details: Dict[str, Any]) -> Dict[str, Any]:
        """Predict the outcome of a legal case."""
        pass
    
    @abstractmethod
    async def generate_contract(self, template: str, parameters: Dict[str, Any]) -> str:
        """Generate a contract based on a template and parameters."""
        pass
```

Implementation for specific models:

```python
# llm_adapter/adapters/openai_adapter.py
import openai
from typing import Dict, Any, List, Optional
from .base_adapter import BaseLLMAdapter

class OpenAIAdapter(BaseLLMAdapter):
    """Adapter for OpenAI GPT models."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key
    
    async def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    async def analyze_document(self, document_text: str) -> Dict[str, Any]:
        prompt = f"""Analyze the following legal document and provide:
        1. A concise summary
        2. Key points
        3. Entities mentioned (people, organizations, dates)
        4. Recommendations for improvement
        
        Document:
        {document_text}
        """
        
        response_text = await self.generate_text(prompt)
        
        # Parse the response into structured data
        # This is a simplified implementation
        lines = response_text.split('\n')
        result = {
            "summary": "",
            "key_points": [],
            "entities": {},
            "recommendations": []
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if "summary" in line.lower():
                current_section = "summary"
            elif "key points" in line.lower():
                current_section = "key_points"
            elif "entities" in line.lower():
                current_section = "entities"
            elif "recommendations" in line.lower():
                current_section = "recommendations"
            elif line and current_section:
                if current_section == "summary":
                    result["summary"] += line + " "
                elif current_section == "key_points" and line.startswith("-"):
                    result["key_points"].append(line[1:].strip())
                elif current_section == "recommendations" and line.startswith("-"):
                    result["recommendations"].append(line[1:].strip())
                elif current_section == "entities":
                    if ":" in line:
                        entity_type, entities = line.split(":", 1)
                        result["entities"][entity_type.strip()] = [e.strip() for e in entities.split(",")]
        
        return result
    
    # Other methods implementation...
```

Factory pattern for selecting the appropriate adapter:

```python
# llm_adapter/factory.py
from typing import Dict, Any
from .adapters.base_adapter import BaseLLMAdapter
from .adapters.openai_adapter import OpenAIAdapter
from .adapters.gemini_adapter import GeminiAdapter
from .adapters.deepseek_adapter import DeepSeekAdapter

class LLMAdapterFactory:
    """Factory for creating LLM adapters."""
    
    @staticmethod
    async def create_adapter(provider: str, config: Dict[str, Any]) -> BaseLLMAdapter:
        """Create an adapter for the specified provider."""
        if provider.lower() == "openai":
            return OpenAIAdapter(
                api_key=config.get("api_key"),
                model=config.get("model", "gpt-4")
            )
        elif provider.lower() == "gemini":
            return GeminiAdapter(
                api_key=config.get("api_key"),
                model=config.get("model", "gemini-pro")
            )
        elif provider.lower() == "deepseek":
            return DeepSeekAdapter(
                api_key=config.get("api_key"),
                model=config.get("model", "deepseek-chat")
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
```

## Frontend Implementation

### Technology Stack
- **Framework**: React 18
- **State Management**: Redux Toolkit
- **UI Components**: Material-UI
- **Routing**: React Router
- **API Client**: Axios
- **Form Handling**: Formik with Yup validation

### Directory Structure
```
frontend/
├── public/                    # Static assets
├── src/
│   ├── components/            # React components
│   │   ├── common/            # Shared components
│   │   ├── document/          # Document analysis components
│   │   ├── research/          # Legal research components
│   │   └── contract/          # Contract generation components
│   ├── pages/                 # Page components
│   ├── services/              # API services
│   ├── store/                 # Redux store
│   │   ├── index.js           # Store configuration
│   │   ├── userSlice.js       # User state management
│   │   ├── documentSlice.js   # Document state management
│   │   ├── researchSlice.js   # Research state management
│   │   └── contractSlice.js   # Contract state management
│   ├── utils/                 # Utility functions
│   ├── App.js                 # Main application component
│   └── index.js               # Application entry point
└── package.json               # Dependencies and scripts
```

### Key Implementation Details

#### Redux Store Configuration
The application uses Redux Toolkit for state management:

```javascript
// store/index.js
import { configureStore } from '@reduxjs/toolkit';
import userReducer from './userSlice';
import documentReducer from './documentSlice';
import researchReducer from './researchSlice';
import contractReducer from './contractSlice';

const store = configureStore({
  reducer: {
    user: userReducer,
    document: documentReducer,
    research: researchReducer,
    contract: contractReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false
    })
});

export default store;
```

#### API Service
The API service handles communication with the backend:

```javascript
// services/api.js
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Authentication services
export const authService = {
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  }
};

// Document services
export const documentService = {
  getDocuments: async () => {
    const response = await api.get('/documents');
    return response.data;
  },
  getDocument: async (id) => {
    const response = await api.get(`/documents/${id}`);
    return response.data;
  },
  uploadDocument: async (formData) => {
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },
  analyzeDocument: async (id, options) => {
    const response = await api.post(`/documents/${id}/analyze`, options);
    return response.data;
  }
};

// Research services
export const researchService = {
  searchCases: async (query) => {
    const response = await api.post('/research/search', { query });
    return response.data;
  },
  predictOutcome: async (caseDetails) => {
    const response = await api.post('/research/predict', caseDetails);
    return response.data;
  }
};

// Contract services
export const contractService = {
  getTemplates: async () => {
    const response = await api.get('/contracts/templates');
    return response.data;
  },
  generateContract: async (templateId, parameters) => {
    const response = await api.post('/contracts/generate', {
      template_id: templateId,
      parameters
    });
    return response.data;
  },
  getContracts: async () => {
    const response = await api.get('/contracts');
    return response.data;
  },
  getContract: async (id) => {
    const response = await api.get(`/contracts/${id}`);
    return response.data;
  }
};

export default api;
```

#### Document Analysis Component
Example of the Document Analysis component:

```jsx
// components/document/DocumentAnalysis.js
import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { 
  Box, Button, Card, CardContent, CircularProgress, 
  Grid, Typography, Paper, Divider, Chip, List, ListItem, 
  ListItemText, MenuItem, FormControl, InputLabel, Select
} from '@mui/material';
import { uploadDocument, analyzeDocument } from '../../store/documentSlice';

const DocumentAnalysis = () => {
  const dispatch = useDispatch();
  const { documents, loading, currentDocument, analysisResult } = useSelector(state => state.document);
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [selectedModel, setSelectedModel] = useState('gpt-4');
  
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };
  
  const handleUpload = async () => {
    if (!file || !title) return;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('description', description);
    
    await dispatch(uploadDocument(formData));
    
    // Reset form
    setFile(null);
    setTitle('');
    setDescription('');
  };
  
  const handleAnalyze = async (documentId) => {
    await dispatch(analyzeDocument({
      documentId,
      options: { llm_model: selectedModel }
    }));
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>Document Analysis</Typography>
      
      {/* Upload Form */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Upload Document</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <input
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFileChange}
              style={{ marginBottom: 16 }}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </Grid>
          <Grid item xs={12}>
            <Button 
              variant="contained" 
              onClick={handleUpload}
              disabled={!file || !title || loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Upload Document'}
            </Button>
          </Grid>
        </Grid>
      </Paper>
      
      {/* Document List */}
      <Typography variant="h6" gutterBottom>Your Documents</Typography>
      <Grid container spacing={2}>
        {documents.map(doc => (
          <Grid item xs={12} sm={6} md={4} key={doc.id}>
            <Card>
              <CardContent>
                <Typography variant="h6">{doc.title}</Typography>
                <Typography variant="body2" color="textSecondary">
                  {doc.description || 'No description'}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Status: {doc.status}
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                    <InputLabel>LLM Model</InputLabel>
                    <Select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      label="LLM Model"
                    >
                      <MenuItem value="gpt-4">GPT-4</MenuItem>
                      <MenuItem value="gpt-3.5-turbo">GPT-3.5 Turbo</MenuItem>
                      <MenuItem value="gemini-pro">Gemini Pro</MenuItem>
                      <MenuItem value="deepseek-chat">DeepSeek</MenuItem>
                    </Select>
                  </FormControl>
                  <Button 
                    variant="contained" 
                    onClick={() => handleAnalyze(doc.id)}
                    disabled={loading}
                    fullWidth
                  >
                    Analyze Document
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      {/* Analysis Results */}
      {analysisResult && (
        <Paper sx={{ p: 2, mt: 3 }}>
          <Typography variant="h6" gutterBottom>Analysis Results</Typography>
          <Typography variant="subtitle1">Summary</Typography>
          <Typography paragraph>{analysisResult.summary}</Typography>
          
          <Divider sx={{ my: 2 }} />
          
          <Typography variant="subtitle1">Key Points</Typography>
          <List>
            {analysisResult.key_points.map((point, index) => (
              <ListItem key={index}>
                <ListItemText primary={point} />
              </ListItem>
            ))}
          </List>
          
          <Divider sx={{ my: 2 }} />
          
          <Typography variant="subtitle1">Entities</Typography>
          {Object.entries(analysisResult.entities).map(([type, entities]) => (
            <Box key={type} sx={{ mb: 2 }}>
              <Typography variant="body2" color="textSecondary">{type}</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {entities.map((entity, index) => (
                  <Chip key={index} label={entity} />
                ))}
              </Box>
            </Box>
          ))}
          
          <Divider sx={{ my: 2 }} />
          
          <Typography variant="subtitle1">Recommendations</Typography>
          <List>
            {analysisResult.recommendations.map((rec, index) => (
              <ListItem key={index}>
                <ListItemText primary={rec} />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
};

export default DocumentAnalysis;
```

## LLM Integration

### Supported Models
The application supports the following LLM models:

1. **OpenAI GPT**
   - Models: gpt-4, gpt-3.5-turbo
   - API: OpenAI API
   - Features: All services (document analysis, legal research, contract generation)

2. **Google Gemini**
   - Models: gemini-pro
   - API: Google AI Generative Language API
   - Features: All services (document analysis, legal research, contract generation)

3. **DeepSeek**
   - Models: deepseek-chat
   - API: DeepSeek API
   - Features: All services (document analysis, legal research, contract generation)

### Integration Architecture
The LLM integration is implemented using the Adapter pattern, which provides a unified interface to different LLM models. This allows the application to switch between models without changing the core business logic.

### Model Selection
Users can select their preferred LLM model in the Settings component:

```jsx
// components/common/Settings.js
import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box, Typography, Paper, Divider, FormControl,
  InputLabel, Select, MenuItem, TextField, Button,
  Alert, Snackbar
} from '@mui/material';
import { updateSettings } from '../../store/userSlice';

const Settings = () => {
  const dispatch = useDispatch();
  const { settings } = useSelector(state => state.user);
  
  const [provider, setProvider] = useState(settings?.provider || 'openai');
  const [model, setModel] = useState(settings?.model || 'gpt-4');
  const [apiKey, setApiKey] = useState(settings?.apiKey || '');
  const [showSuccess, setShowSuccess] = useState(false);
  
  useEffect(() => {
    // Update model options based on selected provider
    if (provider === 'openai' && !['gpt-4', 'gpt-3.5-turbo'].includes(model)) {
      setModel('gpt-4');
    } else if (provider === 'gemini' && model !== 'gemini-pro') {
      setModel('gemini-pro');
    } else if (provider === 'deepseek' && model !== 'deepseek-chat') {
      setModel('deepseek-chat');
    }
  }, [provider]);
  
  const handleSave = () => {
    dispatch(updateSettings({
      provider,
      model,
      apiKey
    }));
    setShowSuccess(true);
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>Settings</Typography>
      
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>LLM Configuration</Typography>
        
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>LLM Provider</InputLabel>
          <Select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            label="LLM Provider"
          >
            <MenuItem value="openai">OpenAI</MenuItem>
            <MenuItem value="gemini">Google Gemini</MenuItem>
            <MenuItem value="deepseek">DeepSeek</MenuItem>
          </Select>
        </FormControl>
        
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Model</InputLabel>
          <Select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            label="Model"
          >
            {provider === 'openai' && (
              <>
                <MenuItem value="gpt-4">GPT-4</MenuItem>
                <MenuItem value="gpt-3.5-turbo">GPT-3.5 Turbo</MenuItem>
              </>
            )}
            {provider === 'gemini' && (
              <MenuItem value="gemini-pro">Gemini Pro</MenuItem>
            )}
            {provider === 'deepseek' && (
              <MenuItem value="deepseek-chat">DeepSeek Chat</MenuItem>
            )}
          </Select>
        </FormControl>
        
        <TextField
          fullWidth
          label="API Key"
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          sx={{ mb: 2 }}
        />
        
        <Button variant="contained" onClick={handleSave}>
          Save Settings
        </Button>
      </Paper>
      
      <Snackbar
        open={showSuccess}
        autoHideDuration={6000}
        onClose={() => setShowSuccess(false)}
      >
        <Alert severity="success">Settings saved successfully!</Alert>
      </Snackbar>
    </Box>
  );
};

export default Settings;
```

## API Reference

### Authentication Endpoints

#### POST /auth/login
Authenticates a user and returns a JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "1",
    "name": "Demo User",
    "email": "user@example.com"
  }
}
```

#### POST /auth/register
Registers a new user.

**Request Body:**
```json
{
  "name": "New User",
  "email": "newuser@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "User registered successfully"
}
```

#### GET /auth/me
Returns the current authenticated user.

**Response:**
```json
{
  "id": "1",
  "name": "Demo User",
  "email": "user@example.com"
}
```

### Document Endpoints

#### GET /documents
Returns a list of documents for the current user.

**Response:**
```json
[
  {
    "id": "1",
    "title": "Employment Contract",
    "description": "Standard employment agreement",
    "file_path": "/documents/employment_contract.pdf",
    "file_type": "pdf",
    "status": "analyzed",
    "created_at": "2025-01-15T12:00:00.000Z"
  },
  {
    "id": "2",
    "title": "Non-Disclosure Agreement",
    "description": "Confidentiality agreement for project X",
    "file_path": "/documents/nda.pdf",
    "file_type": "pdf",
    "status": "uploaded",
    "created_at": "2025-01-16T14:30:00.000Z"
  }
]
```

#### GET /documents/{document_id}
Returns a specific document.

**Response:**
```json
{
  "id": "1",
  "title": "Employment Contract",
  "description": "Standard employment agreement",
  "file_path": "/documents/employment_contract.pdf",
  "file_type": "pdf",
  "status": "analyzed",
  "created_at": "2025-01-15T12:00:00.000Z"
}
```

#### POST /documents/upload
Uploads a new document.

**Request Body (multipart/form-data):**
- `file`: Document file
- `title`: Document title
- `description`: Document description (optional)

**Response:**
```json
{
  "id": "3",
  "title": "Service Agreement",
  "description": "IT services contract",
  "file_path": "/documents/service_agreement.pdf",
  "file_type": "pdf",
  "status": "uploaded",
  "created_at": "2025-01-17T09:45:00.000Z"
}
```

#### POST /documents/{document_id}/analyze
Analyzes a document using the specified LLM model.

**Request Body:**
```json
{
  "llm_model": "gpt-4"
}
```

**Response:**
```json
{
  "document_id": "1",
  "summary": "This contract outlines a service agreement between ABC Corp and XYZ Inc for software development services.",
  "key_points": [
    "Initial term of 12 months with automatic renewal",
    "Payment terms: Net 30 days",
    "Includes confidentiality and non-compete clauses",
    "Intellectual property rights assigned to client"
  ],
  "entities": {
    "people": ["John Smith (CEO)", "Jane Doe (CTO)"],
    "organizations": ["ABC Corporation", "XYZ Inc"],
    "dates": ["January 15, 2025", "December 31, 2025"]
  },
  "recommendations": [
    "Review section 3.2 regarding payment terms",
    "Consider adding more specific deliverable timelines",
    "Strengthen the dispute resolution mechanism"
  ],
  "llm_model": "gpt-4"
}
```

### Research Endpoints

#### POST /research/search
Searches for legal cases based on a query.

**Request Body:**
```json
{
  "query": "contract breach supply chain",
  "filters": {
    "jurisdiction": "federal",
    "date_range": "2020-2025"
  }
}
```

**Response:**
```json
[
  {
    "id": "1",
    "title": "Smith v. Jones (2023)",
    "content": "The court ruled in favor of the plaintiff, finding that the defendant had breached the contract by failing to deliver the goods on time.",
    "source": "Supreme Court",
    "relevance_score": 0.95
  },
  {
    "id": "2",
    "title": "Wilson Corp v. Allen Inc (2022)",
    "content": "The court found that the non-compete clause was overly broad and therefore unenforceable under state law.",
    "source": "Court of Appeals",
    "relevance_score": 0.87
  }
]
```

#### POST /research/predict
Predicts the outcome of a legal case.

**Request Body:**
```json
{
  "case_details": {
    "facts": "On January 10, 2023, Smith entered into a contract with Jones for the delivery of 1,000 custom widgets by March 15, 2023, for a total price of $50,000. Smith paid a 50% deposit ($25,000) upon signing the contract. The contract specified that time was of the essence and included a clause stating that any delay in delivery would result in liquidated damages of $500 per day. Jones delivered the widgets on April 10, 2023, 26 days late. Smith refused to pay the remaining $25,000 and demanded a refund of $13,000 (26 days × $500) from the initial deposit. Jones argued that the delay was caused by supply chain issues beyond his control and refused to pay the liquidated damages.",
    "legal_issues": [
      "Is Jones liable for breach of contract?",
      "Are the liquidated damages enforceable?",
      "Does Jones have a valid defense based on supply chain issues?"
    ],
    "jurisdiction": "New York"
  },
  "llm_model": "gpt-4"
}
```

**Response:**
```json
{
  "prediction": "Based on the provided information and similar cases, the court is likely to rule in favor of the plaintiff.",
  "confidence": 0.78,
  "factors": [
    {"name": "Precedent in similar cases", "impact": "high"},
    {"name": "Strength of evidence", "impact": "medium"},
    {"name": "Applicable statutes", "impact": "medium"},
    {"name": "Jurisdiction tendencies", "impact": "low"}
  ],
  "similar_cases": [
    {"case_name": "Smith v. Jones (2023)", "similarity": 0.85},
    {"case_name": "Wilson Corp v. Allen Inc (2022)", "similarity": 0.72},
    {"case_name": "Parker LLC v. Thompson (2021)", "similarity": 0.68}
  ],
  "llm_model": "gpt-4"
}
```

### Contract Endpoints

#### GET /contracts/templates
Returns a list of available contract templates.

**Response:**
```json
[
  {
    "id": "nda",
    "name": "Non-Disclosure Agreement",
    "description": "Standard NDA for protecting confidential information",
    "parameters": [
      {"name": "party_1_name", "label": "First Party Name", "type": "text", "required": true},
      {"name": "party_1_address", "label": "First Party Address", "type": "text", "required": true},
      {"name": "party_2_name", "label": "Second Party Name", "type": "text", "required": true},
      {"name": "party_2_address", "label": "Second Party Address", "type": "text", "required": true},
      {"name": "effective_date", "label": "Effective Date", "type": "text", "required": true},
      {"name": "term_months", "label": "Term (months)", "type": "number", "required": true},
      {"name": "governing_law", "label": "Governing Law", "type": "text", "required": true}
    ]
  },
  {
    "id": "service",
    "name": "Service Agreement",
    "description": "Contract for professional services",
    "parameters": [
      {"name": "party_1_name", "label": "Service Provider Name", "type": "text", "required": true},
      {"name": "party_1_address", "label": "Service Provider Address", "type": "text", "required": true},
      {"name": "party_2_name", "label": "Client Name", "type": "text", "required": true},
      {"name": "party_2_address", "label": "Client Address", "type": "text", "required": true},
      {"name": "effective_date", "label": "Effective Date", "type": "text", "required": true},
      {"name": "start_date", "label": "Service Start Date", "type": "text", "required": true},
      {"name": "end_date", "label": "Service End Date", "type": "text", "required": true},
      {"name": "services_description", "label": "Description of Services", "type": "textarea", "required": true},
      {"name": "compensation_amount", "label": "Compensation Amount", "type": "text", "required": true},
      {"name": "payment_terms", "label": "Payment Terms", "type": "text", "required": true},
      {"name": "governing_law", "label": "Governing Law", "type": "text", "required": true}
    ]
  }
]
```

#### POST /contracts/generate
Generates a contract based on a template and parameters.

**Request Body:**
```json
{
  "template_id": "nda",
  "parameters": {
    "party_1_name": "XYZ Inc.",
    "party_1_address": "789 Corporate Blvd, Metropolis",
    "party_2_name": "ABC Corporation",
    "party_2_address": "123 Business Ave, Metropolis",
    "effective_date": "March 10, 2025",
    "term_months": 24,
    "governing_law": "California"
  },
  "llm_model": "gpt-4"
}
```

**Response:**
```json
{
  "id": "1",
  "title": "Non-Disclosure Agreement",
  "content": "NON-DISCLOSURE AGREEMENT\n\nTHIS AGREEMENT is made on March 10, 2025,\n\nBETWEEN:\nXYZ Inc., with an address at 789 Corporate Blvd, Metropolis (\"Disclosing Party\"),\n\nAND:\nABC Corporation, with an address at 123 Business Ave, Metropolis (\"Receiving Party\").\n\n...",
  "template_id": "nda",
  "parameters": {
    "party_1_name": "XYZ Inc.",
    "party_1_address": "789 Corporate Blvd, Metropolis",
    "party_2_name": "ABC Corporation",
    "party_2_address": "123 Business Ave, Metropolis",
    "effective_date": "March 10, 2025",
    "term_months": 24,
    "governing_law": "California"
  },
  "status": "generated",
  "created_at": "2025-01-17T10:30:00.000Z",
  "llm_model": "gpt-4"
}
```

#### GET /contracts
Returns a list of generated contracts.

**Response:**
```json
[
  {
    "id": "1",
    "title": "Non-Disclosure Agreement",
    "template_id": "nda",
    "status": "generated",
    "created_at": "2025-01-17T10:30:00.000Z"
  }
]
```

#### GET /contracts/{contract_id}
Returns a specific contract.

**Response:**
```json
{
  "id": "1",
  "title": "Non-Disclosure Agreement",
  "content": "NON-DISCLOSURE AGREEMENT\n\nTHIS AGREEMENT is made on March 10, 2025,\n\nBETWEEN:\nXYZ Inc., with an address at 789 Corporate Blvd, Metropolis (\"Disclosing Party\"),\n\nAND:\nABC Corporation, with an address at 123 Business Ave, Metropolis (\"Receiving Party\").\n\n...",
  "template_id": "nda",
  "parameters": {
    "party_1_name": "XYZ Inc.",
    "party_1_address": "789 Corporate Blvd, Metropolis",
    "party_2_name": "ABC Corporation",
    "party_2_address": "123 Business Ave, Metropolis",
    "effective_date": "March 10, 2025",
    "term_months": 24,
    "governing_law": "California"
  },
  "status": "generated",
  "created_at": "2025-01-17T10:30:00.000Z",
  "llm_model": "gpt-4"
}
```

## Database Schema

### PostgreSQL Schema

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### Documents Table
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'uploaded',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### Contracts Table
```sql
CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    template_id VARCHAR(50) NOT NULL,
    parameters JSONB NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'generated',
    llm_model VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### Settings Table
```sql
CREATE TABLE settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    api_key_encrypted VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### MongoDB Collections

#### DocumentAnalysis Collection
```json
{
  "_id": "ObjectId",
  "document_id": "1",
  "user_id": "1",
  "summary": "This contract outlines a service agreement between ABC Corp and XYZ Inc for software development services.",
  "key_points": [
    "Initial term of 12 months with automatic renewal",
    "Payment terms: Net 30 days",
    "Includes confidentiality and non-compete clauses",
    "Intellectual property rights assigned to client"
  ],
  "entities": {
    "people": ["John Smith (CEO)", "Jane Doe (CTO)"],
    "organizations": ["ABC Corporation", "XYZ Inc"],
    "dates": ["January 15, 2025", "December 31, 2025"]
  },
  "recommendations": [
    "Review section 3.2 regarding payment terms",
    "Consider adding more specific deliverable timelines",
    "Strengthen the dispute resolution mechanism"
  ],
  "llm_model": "gpt-4",
  "created_at": "2025-01-15T14:30:00.000Z"
}
```

#### CasePredictions Collection
```json
{
  "_id": "ObjectId",
  "user_id": "1",
  "case_details": {
    "facts": "On January 10, 2023, Smith entered into a contract with Jones...",
    "legal_issues": [
      "Is Jones liable for breach of contract?",
      "Are the liquidated damages enforceable?",
      "Does Jones have a valid defense based on supply chain issues?"
    ],
    "jurisdiction": "New York"
  },
  "prediction": "Based on the provided information and similar cases, the court is likely to rule in favor of the plaintiff.",
  "confidence": 0.78,
  "factors": [
    {"name": "Precedent in similar cases", "impact": "high"},
    {"name": "Strength of evidence", "impact": "medium"},
    {"name": "Applicable statutes", "impact": "medium"},
    {"name": "Jurisdiction tendencies", "impact": "low"}
  ],
  "similar_cases": [
    {"case_name": "Smith v. Jones (2023)", "similarity": 0.85},
    {"case_name": "Wilson Corp v. Allen Inc (2022)", "similarity": 0.72},
    {"case_name": "Parker LLC v. Thompson (2021)", "similarity": 0.68}
  ],
  "llm_model": "gpt-4",
  "created_at": "2025-01-16T09:45:00.000Z"
}
```

## Deployment Procedures

### Local Deployment

#### Prerequisites
- Python 3.10 or higher
- Node.js 14 or higher
- PostgreSQL
- MongoDB

#### Backend Deployment
1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/legal_app.git
   cd legal_app
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. Set up environment variables
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. Run the application
   ```bash
   python app.py
   ```

#### Frontend Deployment
1. Install dependencies
   ```bash
   cd frontend
   npm install
   ```

2. Set up environment variables
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

3. Run the application
   ```bash
   npm start
   ```

### Azure Deployment

#### Prerequisites
- Azure account
- Azure CLI
- Docker
- Docker Compose

#### Azure Resources
1. Azure Container Registry (ACR)
2. Azure Container Apps
3. Azure Database for PostgreSQL
4. Azure Cosmos DB (MongoDB API)
5. Azure Key Vault

#### Deployment Steps

1. Create Azure resources
   ```bash
   # Login to Azure
   az login
   
   # Create resource group
   az group create --name legal-app-rg --location eastus
   
   # Create Azure Container Registry
   az acr create --resource-group legal-app-rg --name legalappacr --sku Basic
   
   # Create Azure Database for PostgreSQL
   az postgres flexible-server create \
     --resource-group legal-app-rg \
     --name legal-app-postgres \
     --location eastus \
     --admin-user adminuser \
     --admin-password "YourStrongPassword" \
     --sku-name Standard_B1ms
   
   # Create Azure Cosmos DB
   az cosmosdb create \
     --resource-group legal-app-rg \
     --name legal-app-cosmos \
     --kind MongoDB \
     --capabilities EnableMongo
   
   # Create Azure Key Vault
   az keyvault create \
     --resource-group legal-app-rg \
     --name legal-app-keyvault \
     --location eastus
   ```

2. Build and push Docker images
   ```bash
   # Login to ACR
   az acr login --name legalappacr
   
   # Build and push backend image
   cd backend
   docker build -t legalappacr.azurecr.io/legal-app-backend:latest .
   docker push legalappacr.azurecr.io/legal-app-backend:latest
   
   # Build and push frontend image
   cd ../frontend
   docker build -t legalappacr.azurecr.io/legal-app-frontend:latest .
   docker push legalappacr.azurecr.io/legal-app-frontend:latest
   ```

3. Deploy to Azure Container Apps
   ```bash
   # Create Container App Environment
   az containerapp env create \
     --resource-group legal-app-rg \
     --name legal-app-env \
     --location eastus
   
   # Deploy backend
   az containerapp create \
     --resource-group legal-app-rg \
     --name legal-app-backend \
     --environment legal-app-env \
     --image legalappacr.azurecr.io/legal-app-backend:latest \
     --registry-server legalappacr.azurecr.io \
     --target-port 8000 \
     --ingress external \
     --env-vars "DATABASE_URL=postgresql://adminuser:YourStrongPassword@legal-app-postgres.postgres.database.azure.com/legalapp" "MONGODB_URL=mongodb://legal-app-cosmos:YourCosmosKey@legal-app-cosmos.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb"
   
   # Deploy frontend
   az containerapp create \
     --resource-group legal-app-rg \
     --name legal-app-frontend \
     --environment legal-app-env \
     --image legalappacr.azurecr.io/legal-app-frontend:latest \
     --registry-server legalappacr.azurecr.io \
     --target-port 80 \
     --ingress external \
     --env-vars "REACT_APP_API_URL=https://legal-app-backend.azurecontainerapps.io"
   ```

4. Set up CI/CD with GitHub Actions
   Create a GitHub Actions workflow file at `.github/workflows/deploy.yml`:
   ```yaml
   name: Deploy to Azure

   on:
     push:
       branches: [ main ]

   jobs:
     build-and-deploy:
       runs-on: ubuntu-latest
       
       steps:
       - uses: actions/checkout@v2
       
       - name: Login to Azure
         uses: azure/login@v1
         with:
           creds: ${{ secrets.AZURE_CREDENTIALS }}
       
       - name: Login to ACR
         uses: azure/docker-login@v1
         with:
           login-server: legalappacr.azurecr.io
           username: ${{ secrets.ACR_USERNAME }}
           password: ${{ secrets.ACR_PASSWORD }}
       
       - name: Build and push backend image
         run: |
           cd backend
           docker build -t legalappacr.azurecr.io/legal-app-backend:${{ github.sha }} .
           docker push legalappacr.azurecr.io/legal-app-backend:${{ github.sha }}
       
       - name: Build and push frontend image
         run: |
           cd frontend
           docker build -t legalappacr.azurecr.io/legal-app-frontend:${{ github.sha }} .
           docker push legalappacr.azurecr.io/legal-app-frontend:${{ github.sha }}
       
       - name: Update backend Container App
         run: |
           az containerapp update \
             --resource-group legal-app-rg \
             --name legal-app-backend \
             --image legalappacr.azurecr.io/legal-app-backend:${{ github.sha }}
       
       - name: Update frontend Container App
         run: |
           az containerapp update \
             --resource-group legal-app-rg \
             --name legal-app-frontend \
             --image legalappacr.azurecr.io/legal-app-frontend:${{ github.sha }}
   ```

## Security Considerations

### Authentication and Authorization
- JWT-based authentication with secure token handling
- Role-based access control for API endpoints
- Token expiration and refresh mechanisms

### Data Protection
- Encryption of sensitive data at rest and in transit
- Secure storage of API keys in environment variables or Azure Key Vault
- Input validation and sanitization to prevent injection attacks

### API Security
- Rate limiting to prevent abuse
- CORS configuration to restrict access to trusted domains
- Request validation middleware

### LLM Security
- Prompt injection prevention
- Content filtering for generated text
- API key rotation and management

### Deployment Security
- Container image scanning for vulnerabilities
- Network security groups to restrict access
- Regular security updates and patches

## Performance Optimization

### Backend Optimization
- Database query optimization with proper indexing
- Caching of frequently accessed data
- Asynchronous processing for long-running tasks
- Connection pooling for database connections

### Frontend Optimization
- Code splitting for faster initial load
- Lazy loading of components
- Memoization of expensive computations
- Optimized bundle size

### LLM Optimization
- Response caching for similar queries
- Batch processing of requests when possible
- Streaming responses for long-form content
- Model parameter optimization for specific use cases

## Troubleshooting

### Common Issues and Solutions

#### Backend Issues
- **Database Connection Errors**: Check connection strings and network access
- **API Endpoint 500 Errors**: Check logs for detailed error messages
- **Authentication Failures**: Verify JWT secret and token expiration

#### Frontend Issues
- **API Connection Errors**: Check CORS configuration and API URL
- **State Management Issues**: Check Redux actions and reducers
- **Rendering Problems**: Verify component props and state

#### LLM Integration Issues
- **API Key Errors**: Verify API keys and provider settings
- **Rate Limiting**: Implement exponential backoff for retries
- **Response Parsing Errors**: Check response format and error handling

### Logging and Monitoring
- Application logs stored in `/var/log/legal_app/`
- Structured logging with timestamp, severity, and context
- Integration with Azure Application Insights for production monitoring

### Support Resources
- GitHub Issues: https://github.com/yourusername/legal_app/issues
- Documentation: https://github.com/yourusername/legal_app/wiki
- Contact: support@legalapp.example.com
