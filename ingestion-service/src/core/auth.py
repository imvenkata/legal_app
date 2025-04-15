import os
import requests
from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Auth service URL from environment
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")

# OAuth2 scheme setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Verify JWT token with auth service and get current user.
    
    This function calls the auth service to validate the token and get user info.
    In a production environment, you might want to cache the result or verify
    the token locally using the same secret key for better performance.
    """
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