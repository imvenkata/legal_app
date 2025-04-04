from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
import httpx
import os

# Create API router for research
router = APIRouter(
    prefix="/research",
    tags=["research"],
    responses={404: {"description": "Not found"}},
)

# Research service URL
RESEARCH_SERVICE_URL = os.getenv("RESEARCH_SERVICE_URL", "http://localhost:8002")

# Forward research endpoints to research service
@router.get("/search")
async def search_legal_cases(query: str, filters: Optional[Dict[str, Any]] = None, skip: int = 0, limit: int = 10):
    """
    Forward search request to research service
    """
    params = {"query": query, "skip": skip, "limit": limit}
    if filters:
        params["filters"] = filters
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{RESEARCH_SERVICE_URL}/research/search", params=params)
        return response.json()

@router.post("/predict")
async def predict_case_outcome(case_details: Dict[str, Any], llm_model: str = "gpt-4"):
    """
    Forward case prediction request to research service
    """
    data = {"case_details": case_details, "llm_model": llm_model}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{RESEARCH_SERVICE_URL}/research/predict", json=data)
        return response.json()

@router.get("/cases/{case_id}")
async def get_case(case_id: str):
    """
    Forward get case request to research service
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{RESEARCH_SERVICE_URL}/research/cases/{case_id}")
        return response.json()

@router.post("/save", status_code=status.HTTP_201_CREATED)
async def save_research(research_data: Dict[str, Any]):
    """
    Forward save research request to research service
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{RESEARCH_SERVICE_URL}/research/save", json=research_data)
        return response.json()

@router.get("/saved")
async def get_saved_research(user_id: str, skip: int = 0, limit: int = 10):
    """
    Forward get saved research request to research service
    """
    params = {"user_id": user_id, "skip": skip, "limit": limit}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{RESEARCH_SERVICE_URL}/research/saved", params=params)
        return response.json()
