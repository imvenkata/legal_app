from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import the routes
from .routes import auth, users

app = FastAPI(
    title="Auth Service API",
    description="Authentication and user management service for Legal App",
    version="0.1.0",
)

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    # Add any frontend URLs here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])

@app.get("/", tags=["Health"])
def read_root():
    """Health check endpoint."""
    return {"status": "ok", "service": "auth-service"} 