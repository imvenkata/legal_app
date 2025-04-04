from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Dict, Any, Optional
import os

# Import routers from microservices
# These will be imported when the actual services are implemented
# from services.document_service.routers import documents
# from services.research_service.routers import research
# from services.contract_service.routers import contracts

# Create API router for user management
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# Mock user data for demonstration
USERS = {
    "user@example.com": {
        "id": "user123",
        "email": "user@example.com",
        "full_name": "Test User",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        "is_active": True
    }
}

# Authentication endpoints
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = USERS.get(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # In a real implementation, you would verify the password here
    # For now, we'll assume the password is correct if the user exists
    
    # Create access token
    access_token = "mock_access_token"  # In a real implementation, you would generate a JWT
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def read_users_me(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))):
    """
    Get current user
    """
    # In a real implementation, you would decode the JWT and get the user ID
    # For now, we'll return a mock user
    
    return {
        "id": "user123",
        "email": "user@example.com",
        "full_name": "Test User",
        "is_active": True
    }

# Settings endpoints
@router.get("/settings")
async def get_user_settings(user_id: str):
    """
    Get user settings
    """
    # In a real implementation, you would retrieve settings from the database
    # For now, we'll return mock settings
    
    return {
        "user_id": user_id,
        "preferred_llm_model": "gpt-4",
        "theme": "light",
        "notification_preferences": {
            "email": True,
            "in_app": True
        }
    }

@router.put("/settings")
async def update_user_settings(user_id: str, settings: Dict[str, Any]):
    """
    Update user settings
    """
    # In a real implementation, you would update settings in the database
    # For now, we'll just return the updated settings
    
    return {
        "user_id": user_id,
        "preferred_llm_model": settings.get("preferred_llm_model", "gpt-4"),
        "theme": settings.get("theme", "light"),
        "notification_preferences": settings.get("notification_preferences", {
            "email": True,
            "in_app": True
        })
    }

# LLM model settings endpoints
@router.get("/settings/llm-models")
async def get_llm_models():
    """
    Get available LLM models
    """
    # In a real implementation, you would retrieve models from a configuration
    # For now, we'll return mock models
    
    return [
        {
            "id": "gpt-4",
            "name": "GPT-4",
            "provider": "OpenAI",
            "description": "Advanced language model from OpenAI",
            "is_available": True
        },
        {
            "id": "gemini-pro",
            "name": "Gemini Pro",
            "provider": "Google",
            "description": "Google's advanced language model",
            "is_available": True
        },
        {
            "id": "deepseek-chat",
            "name": "DeepSeek Chat",
            "provider": "DeepSeek",
            "description": "DeepSeek's conversational AI model",
            "is_available": True
        }
    ]

@router.put("/settings/llm-model")
async def set_llm_model(user_id: str, model: Dict[str, str]):
    """
    Set preferred LLM model for a user
    """
    # In a real implementation, you would update the user's preferred model in the database
    # For now, we'll just return a success response
    
    return {
        "user_id": user_id,
        "preferred_llm_model": model.get("model", "gpt-4"),
        "updated_at": "2025-03-26T21:52:00Z"
    }
