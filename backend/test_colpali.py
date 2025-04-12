from PIL import Image
from pathlib import Path
import asyncio
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set environment variables for testing
# Use the correct model name directly instead of reading from env
LLM_PROVIDER = "colpali"
LLM_MODEL_NAME = "google/colpali-3b"
DEVICE = "cpu"  # Default to CPU for testing

logger.info(f"Using LLM Provider: {LLM_PROVIDER}, Model: {LLM_MODEL_NAME}, Device: {DEVICE}")

async def test_adapter():
    try:
        # Import after loading environment variables
        from llm_adapter.factory import LLMAdapterFactory

        logger.info("Creating LLM adapter factory...")
        factory = LLMAdapterFactory()
        
        logger.info(f"Getting adapter class for: {LLM_PROVIDER}, {LLM_MODEL_NAME}")
        adapter_class = factory.get_adapter_class(LLM_PROVIDER, LLM_MODEL_NAME)
        
        logger.info(f"Instantiating adapter: {adapter_class.__name__}")
        adapter = adapter_class()
        
        logger.info("Initializing adapter with model params...")
        await adapter.initialize(model_name=LLM_MODEL_NAME, model_params={'device': DEVICE})
        
        logger.info("Adapter initialized successfully!")
        
        # Find a sample image to test with
        uploads_dir = Path("uploads")
        pdf_files = list(uploads_dir.glob("*.pdf"))
        
        if pdf_files:
            logger.info(f"Found {len(pdf_files)} PDF files in uploads directory.")
            logger.info(f"Testing with: {pdf_files[0]}")
            
            # For testing purposes, we won't actually render the PDF, 
            # but we'll create a dummy image
            test_image = Image.new('RGB', (500, 500), color='white')
            
            # Test text generation
            logger.info("Testing text generation...")
            test_prompt = "Extract entities from a legal document."
            response = await adapter.generate_text(test_prompt)
            logger.info(f"Generate text response: {response[:100]}...")
            
            # Test page processing
            logger.info("Testing page processing...")
            page_response = await adapter.process_page(test_image, "Extract the main parties in this document.")
            logger.info(f"Process page response: {page_response[:100]}...")
            
            # Test entity extraction
            logger.info("Testing entity extraction...")
            entities = await adapter.extract_entities_from_page(test_image)
            logger.info(f"Extracted entities: {entities}")
            
            return "All tests completed successfully!"
        else:
            logger.warning("No PDF files found in uploads directory. Skipping image tests.")
            return "Basic adapter tests completed, no image tests run."
            
    except Exception as e:
        logger.error(f"Error in test_adapter: {e}", exc_info=True)
        return f"Test failed: {str(e)}"

if __name__ == "__main__":
    result = asyncio.run(test_adapter())
    logger.info(f"Final result: {result}") 