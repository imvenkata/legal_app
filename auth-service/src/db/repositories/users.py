from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from passlib.context import CryptContext

from src.db.models import UserTable, UserCreate, UserUpdate, User, UserInDB

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Generate a hashed password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_username(db: Session, username: str) -> Optional[UserTable]:
    """Get a user by username."""
    return db.query(UserTable).filter(UserTable.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[UserTable]:
    """Get a user by email."""
    return db.query(UserTable).filter(UserTable.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[UserTable]:
    """Get a user by ID."""
    return db.query(UserTable).filter(UserTable.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserTable]:
    """Get all users."""
    return db.query(UserTable).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> UserTable:
    """Create a new user."""
    # Check if username or email already exists
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if user.email and get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = UserTable(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error"
        )

def update_user(db: Session, user_id: int, user: UserUpdate) -> UserTable:
    """Update an existing user."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Update fields if provided
    update_data = user.dict(exclude_unset=True)
    
    # Handle password separately
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error"
        ) 