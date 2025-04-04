import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from routers import users, documents, research, contracts

# Initialize FastAPI app
app = FastAPI(
    title="Legal AI API Gateway",
    description="API Gateway for Legal AI Application",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Legal AI API Gateway"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include routers
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(research.router)
app.include_router(contracts.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
