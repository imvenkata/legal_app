from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
import httpx
import os

# Create API router for documents
router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)

# Document service URL
DOCUMENT_SERVICE_URL = os.getenv("DOCUMENT_SERVICE_URL", "http://localhost:8001")

# Forward document endpoints to document service
@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(request: Dict[str, Any]):
    """
    Forward document upload request to document service
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{DOCUMENT_SERVICE_URL}/documents/upload", json=request)
        return response.json()

@router.post("/{document_id}/analyze")
async def analyze_document(document_id: str, request: Dict[str, Any]):
    """
    Forward document analysis request to document service
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{DOCUMENT_SERVICE_URL}/documents/{document_id}/analyze", json=request)
        return response.json()

@router.get("/{document_id}")
async def get_document(document_id: str):
    """
    Forward get document request to document service
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DOCUMENT_SERVICE_URL}/documents/{document_id}")
        return response.json()

@router.get("/")
async def get_documents(user_id: Optional[str] = None, skip: int = 0, limit: int = 100):
    """
    Forward get documents request to document service
    """
    params = {}
    if user_id:
        params["user_id"] = user_id
    params["skip"] = skip
    params["limit"] = limit
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DOCUMENT_SERVICE_URL}/documents/", params=params)
        return response.json()

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str):
    """
    Forward delete document request to document service
    """
    async with httpx.AsyncClient() as client:
        await client.delete(f"{DOCUMENT_SERVICE_URL}/documents/{document_id}")
        return None
