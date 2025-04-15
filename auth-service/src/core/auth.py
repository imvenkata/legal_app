from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os

from src.db.session import get_db
from src.db.repositories.users import get_user_by_username, verify_password
from src.db.models import UserTable, UserInDB

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key_change_in_production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    """Verify a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return {"username": username}
    except JWTError:
        raise credentials_exception

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate a user with username and password."""
    # This is a placeholder until we have database integration
    # In a real implementation, this would use get_user_by_username
    # And verify the password with verify_password
    
    # Hardcoded users for testing
    if username == "test" and password == "test":
        user_dict = {
            "id": 1,
            "username": username,
            "email": "test@example.com",
            "full_name": "Test User",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            "is_active": True
        }
        return user_dict
    
    if username == "testuser" and password == "testpassword":
        user_dict = {
            "id": 2,
            "username": username,
            "email": "test@example.com",
            "full_name": "Test User",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            "is_active": True
        }
        return user_dict
        
    return None

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the current user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(token, credentials_exception)
    # This is a placeholder until we have database integration
    # In a real implementation, this would get the user from the database
    if token_data["username"] == "test":
        user_dict = {
            "id": 1,
            "username": "test",
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True
        }
        return user_dict
    elif token_data["username"] == "testuser":
        user_dict = {
            "id": 2,
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True
        }
        return user_dict
    raise credentials_exception

def get_current_active_user(current_user = Depends(get_current_user)):
    """Check if the current user is active."""
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user 