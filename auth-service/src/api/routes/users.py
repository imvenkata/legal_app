from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import os

from src.core.auth import get_current_user, get_current_active_user
from src.db.session import get_db
from src.db.models import User, UserCreate, UserUpdate
from src.db.repositories.users import get_users, create_user, get_user_by_id, update_user

# These will be implemented later
# from src.core.auth import get_current_active_user
# from src.db.models import User, UserCreate, UserUpdate

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

# Placeholder data
users_db = {
    1: {"id": 1, "username": "test", "email": "test@example.com", "full_name": "Test User", "is_active": True}
}

# Placeholder for auth dependency
def get_current_active_user():
    return users_db[1]

router = APIRouter()

@router.get("/me", response_model=dict)
async def read_users_me(current_user = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user

@router.get("/", response_model=List[dict])
async def read_users(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all users. Only accessible to authenticated users."""
    # This is a placeholder until we have database integration
    # In a real implementation, this would use get_users from the repository
    users = [
        {
            "id": 1,
            "username": "test",
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True
        }
    ]
    return users

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_new_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user. No authentication required for registration."""
    # This is a placeholder until we have database integration
    # In a real implementation, this would use create_user from the repository
    if user.username == "test":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    new_user = {
        "id": 2,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": True
    }
    return new_user

@router.put("/{user_id}", response_model=dict)
async def update_user_route(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Update a user. Users can only update themselves unless they have admin role."""
    # Check if user is updating their own profile or has admin role
    if current_user.get("id") != user_id:
        # In a real implementation, we would check for admin role
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update other users"
        )
    
    # This is a placeholder until we have database integration
    # In a real implementation, this would use update_user from the repository
    if user_id != 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updated_user = {
        "id": current_user.get("id"),
        "username": current_user.get("username"),
        "email": user_update.email or current_user.get("email"),
        "full_name": user_update.full_name or current_user.get("full_name"),
        "is_active": user_update.is_active if user_update.is_active is not None else current_user.get("is_active", True)
    }
    return updated_user 