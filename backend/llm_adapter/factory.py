from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

from .openai_adapter import OpenAIAdapter
from .gemini_adapter import GeminiAdapter
from .deepseek_adapter import DeepSeekAdapter
from .base_adapter import BaseLLMAdapter

# Load environment variables
load_dotenv()

class LLMAdapterFactory:
    """Factory for creating LLM adapters"""
    
    def __init__(self):
        self.adapters = {
            "openai": {
                "gpt-4": OpenAIAdapter,
                "gpt-3.5-turbo": OpenAIAdapter,
            },
            "gemini": {
                "gemini-pro": GeminiAdapter,
            },
            "deepseek": {
                "deepseek-chat": DeepSeekAdapter,
            }
        }
    
    def get_adapter(self, provider: str, model: str) -> BaseLLMAdapter:
        """
        Get the appropriate LLM adapter based on provider and model
        
        Args:
            provider: The LLM provider (openai, gemini, deepseek)
            model: The specific model to use
            
        Returns:
            An instance of the appropriate LLM adapter
            
        Raises:
            ValueError: If the provider or model is not supported
        """
        if provider not in self.adapters:
            raise ValueError(f"Provider '{provider}' not supported. Available providers: {list(self.adapters.keys())}")
        
        provider_models = self.adapters[provider]
        
        if model not in provider_models:
            # If the specific model isn't found, use the default model for the provider
            default_model = next(iter(provider_models.keys()))
            adapter_class = next(iter(provider_models.values()))
            return adapter_class(model)
        
        adapter_class = provider_models[model]
        return adapter_class(model)
    
    def get_available_models(self) -> Dict[str, list]:
        """
        Get a dictionary of available providers and their models
        
        Returns:
            A dictionary with providers as keys and lists of models as values
        """
        return {
            provider: list(models.keys())
            for provider, models in self.adapters.items()
        }
