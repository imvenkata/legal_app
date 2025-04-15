import os
import httpx
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class LlmAdapter(ABC):
    """Abstract base class for LLM adapters."""
    
    @abstractmethod
    async def initialize(self, api_key: str, model_params: Dict[str, Any] = None) -> None:
        """Initialize the LLM adapter with API key and model parameters."""
        pass
    
    @abstractmethod
    async def analyze_document(self, document_text: str) -> Dict[str, Any]:
        """Analyze a document using the LLM."""
        pass
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], document_context: str = None) -> str:
        """Chat with the LLM, optionally providing document context."""
        pass

class OpenAIAdapter(LlmAdapter):
    """LLM adapter for OpenAI models."""
    
    def __init__(self):
        self.api_key = None
        self.model = "gpt-4o"
        self.base_url = "https://api.openai.com/v1"
        self.client = None
        self.timeout = 120.0
    
    async def initialize(self, api_key: str, model_params: Dict[str, Any] = None) -> None:
        """Initialize the OpenAI adapter."""
        self.api_key = api_key
        if model_params and "model" in model_params:
            self.model = model_params["model"]
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            timeout=self.timeout
        )
    
    async def analyze_document(self, document_text: str) -> Dict[str, Any]:
        """Analyze a document using OpenAI."""
        if not self.client:
            raise ValueError("Adapter not initialized. Call initialize() first.")
        
        # Truncate text if too long
        # GPT-4 has a context window of ~8k tokens
        max_length = 32000  # Characters, rough approximation
        if len(document_text) > max_length:
            document_text = document_text[:max_length] + "...[truncated]"
        
        # Prepare prompt for document analysis
        prompt = f"""
        Analyze the following legal document and provide:
        1. A brief summary of the document
        2. A comprehensive structured summary covering all important aspects of the legal document, including:
           - Document type and purpose
           - Key parties involved
           - Critical dates and deadlines
           - Material terms and conditions
           - Legal obligations and rights
           - Governing law and jurisdiction
           - Enforcement and remedies
           - Termination provisions
        3. Key entities mentioned (people, organizations, dates, etc.)
        4. Potential legal risks or issues
        5. Legal recommendations
        
        Document:
        {document_text}
        
        Format your response as a structured JSON with the following keys:
        "summary", "comprehensive_summary" (with nested sections), "entities", "risks", "recommendations"
        """
        
        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a legal document analysis expert specializing in contract review, legal risk assessment, and compliance analysis."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                }
            )
            response.raise_for_status()
            result = response.json()
            
            # Parse the response
            try:
                content = result["choices"][0]["message"]["content"]
                analysis = json.loads(content)
                return analysis
            except (KeyError, json.JSONDecodeError) as e:
                return {
                    "summary": "Error parsing analysis result.",
                    "comprehensive_summary": {
                        "document_type": f"Error parsing analysis: {str(e)}"
                    },
                    "entities": [],
                    "risks": [],
                    "recommendations": [f"Error: {str(e)}"]
                }
        except Exception as e:
            return {
                "summary": "Error analyzing document.",
                "comprehensive_summary": {
                    "document_type": f"Error during analysis: {str(e)}"
                },
                "entities": [],
                "risks": [],
                "recommendations": [f"Error: {str(e)}"]
            }
    
    async def chat(self, messages: List[Dict[str, str]], document_context: str = None) -> str:
        """Chat with OpenAI, optionally with document context."""
        if not self.client:
            raise ValueError("Adapter not initialized. Call initialize() first.")
            
        system_message = "You are a helpful legal document assistant."
        
        if document_context:
            system_message = f"""You are a legal document assistant. Answer questions based on this document content:
            
{document_context[:10000]}

Only respond with information clearly present in the document. If the answer isn't in the document, say so clearly.
"""
        
        try:
            # Create a request payload that can be JSON serialized
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_message},
                ]
            }
            
            # Add all the user messages, ensuring they can be serialized
            for msg in messages:
                serializable_msg = {
                    "role": msg["role"],
                    "content": msg["content"]
                }
                payload["messages"].append(serializable_msg)
                
            payload["temperature"] = 0.1
            
            response = await self.client.post(
                "/chat/completions",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error in chat: {str(e)}"

class DeepSeekAdapter(LlmAdapter):
    """LLM adapter for DeepSeek models."""
    
    def __init__(self):
        self.api_key = None
        self.model = "deepseek-chat"
        self.base_url = "https://api.deepseek.com/v1"
        self.client = None
        self.timeout = 120.0
    
    async def initialize(self, api_key: str, model_params: Dict[str, Any] = None) -> None:
        """Initialize the DeepSeek adapter."""
        self.api_key = api_key
        if model_params and "model" in model_params:
            self.model = model_params["model"]
        
        # DeepSeek API is OpenAI-compatible
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            timeout=self.timeout
        )
    
    async def analyze_document(self, document_text: str) -> Dict[str, Any]:
        """Analyze a document using DeepSeek."""
        if not self.client:
            raise ValueError("Adapter not initialized. Call initialize() first.")
        
        # Truncate text if too long
        max_length = 32000  # Characters, rough approximation
        if len(document_text) > max_length:
            document_text = document_text[:max_length] + "...[truncated]"
        
        # Prepare prompt for document analysis
        prompt = f"""
        Analyze the following legal document and provide:
        1. A brief summary of the document
        2. A comprehensive structured summary covering all important aspects of the legal document, including:
           - Document type and purpose
           - Key parties involved
           - Critical dates and deadlines
           - Material terms and conditions
           - Legal obligations and rights
           - Governing law and jurisdiction
           - Enforcement and remedies
           - Termination provisions
        3. Key entities mentioned (people, organizations, dates, etc.)
        4. Potential legal risks or issues
        5. Legal recommendations
        
        Document:
        {document_text}
        
        Format your response as a structured JSON with the following keys:
        "summary", "comprehensive_summary" (with nested sections), "entities", "risks", "recommendations"
        """
        
        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a legal document analysis expert specializing in contract review, legal risk assessment, and compliance analysis."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                }
            )
            response.raise_for_status()
            result = response.json()
            
            # Parse the response
            try:
                content = result["choices"][0]["message"]["content"]
                analysis = json.loads(content)
                return analysis
            except (KeyError, json.JSONDecodeError) as e:
                return {
                    "summary": "Error parsing analysis result.",
                    "comprehensive_summary": {
                        "document_type": f"Error parsing analysis: {str(e)}"
                    },
                    "entities": [],
                    "risks": [],
                    "recommendations": [f"Error: {str(e)}"]
                }
        except Exception as e:
            return {
                "summary": "Error analyzing document.",
                "comprehensive_summary": {
                    "document_type": f"Error during analysis: {str(e)}"
                },
                "entities": [],
                "risks": [],
                "recommendations": [f"Error: {str(e)}"]
            }
    
    async def chat(self, messages: List[Dict[str, str]], document_context: str = None) -> str:
        """Chat with DeepSeek, optionally with document context."""
        if not self.client:
            raise ValueError("Adapter not initialized. Call initialize() first.")
            
        system_message = "You are a helpful legal document assistant."
        
        if document_context:
            system_message = f"""You are a legal document assistant. Answer questions based on this document content:
            
{document_context[:10000]}

Only respond with information clearly present in the document. If the answer isn't in the document, say so clearly.
"""
        
        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_message},
                        *messages
                    ],
                    "temperature": 0.1
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error in chat: {str(e)}"

def get_llm_adapter(model_name: str = None) -> LlmAdapter:
    """Factory function to get the appropriate LLM adapter."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if model_name:
        # If model name is provided, determine provider based on model name
        if model_name.startswith("gpt"):
            return OpenAIAdapter()
        elif model_name.startswith("deepseek"):
            return DeepSeekAdapter()
    
    # Use configured provider as fallback
    if provider == "deepseek":
        return DeepSeekAdapter()
    else:
        return OpenAIAdapter() 