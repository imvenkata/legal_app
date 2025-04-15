import os
import requests
import logging
from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

# Auth service URL from environment
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")

# Enable mock token for testing
ENABLE_MOCK_AUTH = os.getenv("ENABLE_MOCK_AUTH", "true").lower() in ("true", "1", "yes")
MOCK_TOKEN_PREFIX = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"

# Set up logging
logger = logging.getLogger(__name__)

# OAuth2 scheme setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme), request: Request = None) -> Dict[str, Any]:
    """
    Verify JWT token with auth service and get current user.
    
    This function calls the auth service to validate the token and get user info.
    In a production environment, you might want to cache the result or verify
    the token locally using the same secret key for better performance.
    """
    # If no token is provided
    if not token:
        # Try to get token from Authorization header directly
        auth_header = request.headers.get("Authorization") if request else None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Check if this is a mock token for testing
    if ENABLE_MOCK_AUTH and token.startswith(MOCK_TOKEN_PREFIX):
        logger.debug("Using mock authentication token")
        # Return a mock user for testing
        return {
            "id": 1,
            "username": "test_user",
            "email": "test@example.com",
            "is_active": True,
            "is_admin": True
        }
    
    # Configure request headers with token
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Call auth service to validate token and get user info
        response = requests.get(f"{AUTH_SERVICE_URL}/api/auth/me", headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = response.json()
        return user
        
    except requests.RequestException:
        # Handle connection errors to auth service
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        )

def check_document_access(user_id: int, document_owner_id: int, allowed_roles: Optional[list] = None) -> bool:
    """
    Check if a user has access to a document.
    
    Args:
        user_id: The ID of the user
        document_owner_id: The ID of the document owner
        allowed_roles: Optional list of roles that are allowed access
    
    Returns:
        True if the user has access, False otherwise
    """
    # If the user is the document owner, always allow access
    if user_id == document_owner_id:
        return True
    
    # Role-based access could be implemented here
    # if allowed_roles and user.role in allowed_roles:
    #     return True
    
    return False 