from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Dict, Any

from .routes import ingestion, status

app = FastAPI(
    title="Ingestion Service API",
    description="Document ingestion and processing service for Legal App",
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
app.include_router(ingestion.router, prefix="/api/ingestion", tags=["Ingestion"])
app.include_router(status.router, prefix="/api/status", tags=["Status"])

@app.get("/", tags=["Health"])
def read_root():
    """Health check endpoint."""
    return {"status": "ok", "service": "ingestion-service"}

@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "version": app.version,
        "workers": int(os.getenv("INGESTION_WORKERS", "1"))
    } 