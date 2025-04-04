from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import List, Dict, Any, Optional
import os
import uvicorn
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import routers
try:
    from routers import documents, research, contracts, users
    logger.info("Routers imported successfully")
except ImportError as e:
    logger.error(f"Error importing routers: {str(e)}")
    sys.exit(1)

app = FastAPI(title="Legal AI API Gateway")

# Configure rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Get allowed origins from environment variable
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
logger.info(f"Allowed origins: {ALLOWED_ORIGINS}")

# Configure CORS with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"] + [origin.replace("http://", "").replace("https://", "") for origin in ALLOWED_ORIGINS]
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["Authentication"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(research.router, prefix="/api/research", tags=["Research"])
app.include_router(contracts.router, prefix="/api/contracts", tags=["Contracts"])

@app.get("/")
@limiter.limit("5/minute")
async def root(request: Request):
    return {"message": "Welcome to Legal AI API Gateway"}

@app.get("/health")
@limiter.limit("10/minute")
async def health_check(request: Request):
    return {"status": "healthy"}

if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 8080))
        logger.info(f"Starting server on port {port}")
        uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        sys.exit(1)
