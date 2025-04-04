from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseLLMAdapter(ABC):
    """Base adapter interface for LLM models"""
    
    def __init__(self, model: str):
        self.model = model
    
    @abstractmethod
    async def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate text based on the prompt
        
        Args:
            prompt: The input text prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0-1)
            
        Returns:
            Dictionary containing the generated text and usage statistics
        """
        pass
    
    @abstractmethod
    async def analyze_document(self, document_text: str) -> Dict[str, Any]:
        """
        Analyze a legal document
        
        Args:
            document_text: The text content of the document
            
        Returns:
            Dictionary containing analysis results (summary, key points, entities, etc.)
        """
        pass
    
    @abstractmethod
    async def predict_case_outcome(self, case_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict the outcome of a legal case
        
        Args:
            case_details: Dictionary containing case information
            
        Returns:
            Dictionary containing prediction results
        """
        pass
    
    @abstractmethod
    async def generate_contract(self, template: str, parameters: Dict[str, Any]) -> str:
        """
        Generate a contract based on template and parameters
        
        Args:
            template: The contract template
            parameters: Dictionary of parameters to fill in the template
            
        Returns:
            The generated contract text
        """
        pass
