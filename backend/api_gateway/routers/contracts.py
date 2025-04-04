from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
import httpx
import os

# Create API router for contracts
router = APIRouter(
    prefix="/contracts",
    tags=["contracts"],
    responses={404: {"description": "Not found"}},
)

# Contract service URL
CONTRACT_SERVICE_URL = os.getenv("CONTRACT_SERVICE_URL", "http://localhost:8003")

# Forward contract endpoints to contract service
@router.get("/templates")
async def get_templates(category: Optional[str] = None, skip: int = 0, limit: int = 10):
    """
    Forward get templates request to contract service
    """
    params = {"skip": skip, "limit": limit}
    if category:
        params["category"] = category
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CONTRACT_SERVICE_URL}/contracts/templates", params=params)
        return response.json()

@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """
    Forward get template request to contract service
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CONTRACT_SERVICE_URL}/contracts/templates/{template_id}")
        return response.json()

@router.post("/generate/{template_id}")
async def generate_contract(template_id: str, parameters: Dict[str, Any], llm_model: str = "gpt-4"):
    """
    Forward generate contract request to contract service
    """
    data = {"parameters": parameters, "llm_model": llm_model}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{CONTRACT_SERVICE_URL}/contracts/generate/{template_id}", json=data)
        return response.json()

@router.post("/save", status_code=status.HTTP_201_CREATED)
async def save_contract(contract_data: Dict[str, Any]):
    """
    Forward save contract request to contract service
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{CONTRACT_SERVICE_URL}/contracts/save", json=contract_data)
        return response.json()

@router.get("/")
async def get_contracts(user_id: Optional[str] = None, status_filter: Optional[str] = None, skip: int = 0, limit: int = 10):
    """
    Forward get contracts request to contract service
    """
    params = {"skip": skip, "limit": limit}
    if user_id:
        params["user_id"] = user_id
    if status_filter:
        params["status"] = status_filter
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CONTRACT_SERVICE_URL}/contracts/", params=params)
        return response.json()

@router.get("/{contract_id}")
async def get_contract(contract_id: str):
    """
    Forward get contract request to contract service
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CONTRACT_SERVICE_URL}/contracts/{contract_id}")
        return response.json()

@router.put("/{contract_id}")
async def update_contract(contract_id: str, contract_data: Dict[str, Any]):
    """
    Forward update contract request to contract service
    """
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{CONTRACT_SERVICE_URL}/contracts/{contract_id}", json=contract_data)
        return response.json()

@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(contract_id: str):
    """
    Forward delete contract request to contract service
    """
    async with httpx.AsyncClient() as client:
        await client.delete(f"{CONTRACT_SERVICE_URL}/contracts/{contract_id}")
        return None
