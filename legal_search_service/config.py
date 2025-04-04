import os # Import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# Construct path to .env file relative to this config file
env_path = os.path.join(os.path.dirname(__file__), '.env')
# Check if the relative path exists, otherwise default to looking in cwd
if not os.path.exists(env_path):
    env_path = '.env' # Fallback to current directory

class Settings(BaseSettings):
    # Load .env file from the calculated path
    model_config = SettingsConfigDict(env_file=env_path, env_file_encoding='utf-8', extra='ignore')

    # Qdrant settings
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None # Optional API key
    COLLECTION_NAME: str = "legal_documents"

    # Embedding model
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2" # Default Sentence Transformer

    # LlamaParse settings (if needed)
    LLAMA_CLOUD_API_KEY: str | None = None

    # OpenAI settings
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL_NAME: str = "gpt-4o" # Or another suitable model like gpt-4-turbo

    # DeepSeek settings (for OpenAI-compatible API)
    DEEPSEEK_API_KEY: str | None = None
    DEEPSEEK_MODEL_NAME: str = "deepseek-chat" # Or deepseek-coder
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1" # Verify this is the correct endpoint

    # --- LLM Selection ---
    # Choose the LLM provider: "openai" or "deepseek"
    LLM_PROVIDER: str = "deepseek" # Default to deepseek for initial testing

    # --- Data Path ---
    DATA_PATH: str = "./data"

settings = Settings()
