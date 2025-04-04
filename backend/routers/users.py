from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter()

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")  # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Models
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Database connection
client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
db = client.legal_app
users_collection = db.users

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    except JWTError:
        raise credentials_exception
    
    user = await users_collection.find_one({"_id": user_id})
    if user is None:
        raise credentials_exception
    return user

# Authentication routes
@router.post("/login", response_model=TokenResponse)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await users_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["_id"])}, expires_delta=access_token_expires
    )
    
    # Set HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Enable in production
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"]
        }
    }

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    if await users_collection.find_one({"email": user_data.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    hashed_password = get_password_hash(user_data.password)
    user_dict = {
        "name": user_data.name,
        "email": user_data.email,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    }
    
    result = await users_collection.insert_one(user_dict)
    return {"message": "User registered successfully", "id": str(result.inserted_id)}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "name": current_user["name"],
        "email": current_user["email"]
    }

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}
