import httpx
import os
import pytest
from fastapi.testclient import TestClient
import sys
import json
from pathlib import Path

# Add src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.api.main import app
from src.core.llm import OpenAIAdapter, DeepSeekAdapter

client = TestClient(app)

# Mock JWT token for testing
mock_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwibmFtZSI6IlRlc3QgVXNlciIsImV4cCI6MTY5MTI0NTgwMH0.mock_signature"

# Mock document ID for testing
mock_document_id = "123e4567-e89b-12d3-a456-426614174000"

def test_analyze_document_endpoint():
    """Test the document analysis endpoint."""
    # Skip test if no API keys are configured
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("DEEPSEEK_API_KEY"):
        pytest.skip("No API keys configured for testing")
    
    response = client.post(
        f"/api/documents/{mock_document_id}/analyze",
        headers={"Authorization": f"Bearer {mock_token}"},
        data={"llm_model": "gpt-4o"}
    )
    
    # Check response status
    assert response.status_code == 200
    
    # Check response content
    result = response.json()
    assert "document_id" in result
    assert "summary" in result
    assert "entities" in result
    assert "risk_factors" in result
    assert "recommendations" in result
    assert "model_used" in result

@pytest.mark.asyncio
async def test_openai_adapter():
    """Test the OpenAI adapter directly."""
    # Skip test if no OpenAI API key is configured
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("No OpenAI API key configured for testing")
    
    adapter = OpenAIAdapter()
    await adapter.initialize(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Test document text
    document_text = """
    TRADEMARK ASSIGNMENT
    
    This Trademark Assignment ("Assignment") is made and entered into as of January 15, 2023 
    ("Effective Date"), by and between ABC Corporation, a Delaware corporation ("Assignor"), 
    and XYZ Inc., a California corporation ("Assignee").
    
    WHEREAS, Assignor is the owner of all right, title and interest in and to the trademark 
    "TECHWAVE" (Registration No. 4,123,456) for use in connection with computer software 
    and related goods and services ("Trademark");
    
    WHEREAS, Assignor desires to assign all of its right, title and interest in and to the 
    Trademark to Assignee, and Assignee desires to accept such assignment;
    
    NOW, THEREFORE, for good and valuable consideration, the receipt and sufficiency of which 
    are hereby acknowledged, the parties agree as follows:
    
    1. ASSIGNMENT. Assignor hereby irrevocably assigns, transfers and conveys to Assignee all 
    of Assignor's right, title and interest in and to the Trademark, together with the goodwill 
    of the business symbolized by the Trademark, including all rights to sue for and recover 
    damages for past infringement.
    
    2. CONSIDERATION. In consideration for this Assignment, Assignee shall pay Assignor the 
    sum of Five Hundred Thousand Dollars ($500,000) within thirty (30) days of the Effective Date.
    
    3. FURTHER ASSURANCES. Assignor agrees to execute any additional documents reasonably 
    requested by Assignee to evidence the assignment of the Trademark.
    
    4. REPRESENTATIONS AND WARRANTIES. Assignor represents and warrants that (a) it is the 
    sole and exclusive owner of all right, title and interest in and to the Trademark; (b) the 
    Trademark is free and clear of all liens, claims, and encumbrances; (c) it has the full 
    right and authority to enter into this Assignment; and (d) it has not granted any licenses, 
    registered any security interests, or made any assignments relating to the Trademark to any 
    third party.
    
    IN WITNESS WHEREOF, the parties have executed this Assignment as of the Effective Date.
    
    ABC CORPORATION
    
    By: ________________________
    Name: John Smith
    Title: Chief Executive Officer
    
    XYZ INC.
    
    By: ________________________
    Name: Jane Doe
    Title: President
    """
    
    result = await adapter.analyze_document(document_text)
    
    # Check result structure
    assert "summary" in result
    assert "entities" in result
    assert "risks" in result
    assert "recommendations" in result
    
    # Print result for inspection
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    # Run the adapter test directly
    import asyncio
    asyncio.run(test_openai_adapter()) 