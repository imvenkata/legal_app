from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LlmAdapter(ABC):
    """
    Abstract base class for LLM adapters.
    All specific model adapters should inherit from this class.
    """
    
    @abstractmethod
    async def initialize(self, api_key: str, model_params: Dict[str, Any]) -> None:
        """Initialize the LLM adapter with API key and model parameters"""
        pass
    
    @abstractmethod
    async def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate text based on the provided prompt"""
        pass
    
    @abstractmethod
    async def analyze_document(self, document_text: str) -> Dict[str, Any]:
        """Analyze a document and return structured information"""
        pass
    
    @abstractmethod
    async def research_query(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Process a legal research query and return relevant information"""
        pass
    
    @abstractmethod
    async def generate_contract(self, template: str, parameters: Dict[str, Any]) -> str:
        """Generate a contract based on a template and parameters"""
        pass
    
    @abstractmethod
    async def get_embedding(self, text: str) -> list:
        """Get vector embedding for the provided text"""
        pass
    
    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """Count the number of tokens in the provided text"""
        pass
