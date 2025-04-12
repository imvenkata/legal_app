import os
from typing import Dict, Any, Optional, List
from .base_adapter import LlmAdapter
from PIL import Image
import torch
import logging
import json

logger = logging.getLogger(__name__)

# Import necessary components from transformers
try:
    from transformers import AutoTokenizer, AutoProcessor, PaliGemmaForConditionalGeneration
    # PaliGemma uses PaliGemmaProcessor which combines tokenizer and image processor
    # Using AutoProcessor might simplify things if it correctly loads PaliGemmaProcessor
    # Using AutoModel might work but PaliGemmaForConditionalGeneration is more specific
    COLPALI_AVAILABLE = True
except ImportError:
    logger.warning("Transformers library (or specific ColPali/PaliGemma components) not found. ColPali adapter will not work.")
    AutoTokenizer = None
    AutoProcessor = None # Add this
    PaliGemmaForConditionalGeneration = None # Add this
    COLPALI_AVAILABLE = False

class ColPaliAdapter(LlmAdapter):
    """
    Adapter for ColPali / PaliGemma Vision Language Models.
    Requires transformers, torch (or other backend), PIL, and accelerate.
    """
    
    def __init__(self):
        self.model = None
        # PaliGemma uses a Processor, not just a tokenizer
        self.processor = None 
        self.device = None
        self.model_name = None
        # self.tokenizer_name = None # Processor handles tokenization

    # Updated initialize signature - tokenizer_name might not be needed if processor is used
    async def initialize(self, model_name: str, model_params: Dict[str, Any]) -> None:
        """Initialize the ColPali/PaliGemma adapter"""
        if not COLPALI_AVAILABLE:
             raise ImportError("Transformers library is required for ColPaliAdapter.")
             
        self.model_name = model_name
        # self.tokenizer_name = tokenizer_name # Likely replaced by processor
        self.device = model_params.get("device", "cuda:0" if torch.cuda.is_available() else "cpu")
        # Determine torch dtype based on device
        self.dtype = torch.bfloat16 if self.device.startswith("cuda") else torch.float32
        
        logger.info(f"Initializing PaliGemma adapter. Model: {self.model_name}, Device: {self.device}, Dtype: {self.dtype}")
        
        try:
            # Load model and processor
            # Use PaliGemma specific classes for clarity and potentially better handling
            # The processor handles both text tokenization and image preprocessing
            self.processor = AutoProcessor.from_pretrained(self.model_name)
            # Load the model with appropriate dtype and device mapping
            # `device_map='auto'` requires `accelerate` library
            self.model = PaliGemmaForConditionalGeneration.from_pretrained(
                self.model_name, 
                torch_dtype=self.dtype, 
                device_map="auto", # Automatically distribute across GPUs if available
                revision="bfloat16", # Specify revision if using bf16 weights
            ).eval() # Set to evaluation mode
            
            logger.info(f"PaliGemma model '{self.model_name}' and processor loaded successfully to {self.device}.")
            
        except Exception as e:
            logger.error(f"Error loading PaliGemma model/processor: {e}", exc_info=True)
            raise RuntimeError(f"Failed to initialize PaliGemma: {e}")

    async def process_page(self, image: Image.Image, prompt: str, max_new_tokens: int = 1000) -> str:
        """Process a single page image with a prompt using PaliGemma."""
        if not self.model or not self.processor:
            raise RuntimeError("PaliGemma adapter not initialized.")
            
        logger.info(f"Processing page with prompt: '{prompt[:50]}...'")
        
        try:
            # 1. Preprocess image and prompt using the processor
            # Ensure image is in RGB format
            if image.mode != "RGB":
                 image = image.convert("RGB")
                 
            inputs = self.processor(text=prompt, images=image, return_tensors="pt").to(self.dtype).to(self.device)
            
            # 2. Run model inference
            # Use generate method for text generation tasks
            with torch.no_grad(): # Disable gradient calculation for inference
                 outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False) # Adjust generation params as needed
            
            # 3. Decode the output tokens, skipping prompt and special tokens
            # The output includes the input prompt tokens, so we need to decode only the generated part
            output_text = self.processor.decode(outputs[0], skip_special_tokens=True)
            # Remove the input prompt from the beginning of the output string
            # This assumes the prompt structure used by the processor matches this simple removal
            if output_text.startswith(prompt):
                 decoded_text = output_text[len(prompt):].lstrip() # Remove prompt and leading space
            else:
                # Fallback if prompt isn't exactly at the start (might need refinement)
                logger.warning("Generated text did not start with the exact prompt. Returning full decoded output.")
                decoded_text = output_text

            logger.info(f"VLM generated response (first 100 chars): {decoded_text[:100]}...")
            return decoded_text
            
        except Exception as e:
            logger.error(f"Error processing page with PaliGemma: {e}", exc_info=True)
            return "" # Return empty string on error

    # --- Implement other required methods from LlmAdapter ---

    async def generate_text(self, prompt: str, max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> str:
        """Generate text using PaliGemma (Text-only input)."""
        if not self.model or not self.processor:
            raise RuntimeError("PaliGemma adapter not initialized.")

        logger.info(f"Generating text (text-only) with prompt: '{prompt[:50]}...'")
        effective_max_tokens = max_tokens if max_tokens is not None else 1000 # Default max_new_tokens

        try:
            # Process only text input
            inputs = self.processor(text=prompt, return_tensors="pt").to(self.dtype).to(self.device)
            
            with torch.no_grad():
                 outputs = self.model.generate(**inputs, max_new_tokens=effective_max_tokens, do_sample=False) # Adjust params if needed
                 
            output_text = self.processor.decode(outputs[0], skip_special_tokens=True)
            if output_text.startswith(prompt):
                 decoded_text = output_text[len(prompt):].lstrip()
            else:
                 logger.warning("Generated text did not start with the exact prompt. Returning full decoded output.")
                 decoded_text = output_text
                 
            return decoded_text
            
        except Exception as e:
             logger.error(f"Error generating text with PaliGemma: {e}", exc_info=True)
             return ""

    async def extract_entities_from_page(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Extract entities from a single page image using PaliGemma."""
        # Refine prompt for PaliGemma if needed - might need specific instruction format
        prompt = "Extract all named entities (people, organizations, locations, dates, monetary values) from this page. Respond ONLY with a valid JSON list of objects, each having 'name', 'type', and 'context' keys. Example: [{\"name\": \"John Doe\", \"type\": \"PERSON\", \"context\": \"mentioned in section 3\"}]. If no entities are found, return an empty list []."
        
        entities = []
        try:
            # Increase max_new_tokens as JSON output can be verbose
            response_text = await self.process_page(image, prompt, max_new_tokens=1500)
            
            if not response_text:
                logger.warning("Received empty response from VLM for entity extraction.")
                return []
                
            # Attempt to parse the JSON response
            try:
                 # Clean potential markdown code blocks or extraneous text before JSON
                 json_start = response_text.find('[')
                 json_end = response_text.rfind(']')
                 if json_start != -1 and json_end != -1:
                     json_str = response_text[json_start:json_end+1]
                 else:
                      logger.warning(f"Could not find JSON list markers in VLM response: {response_text[:100]}...")
                      return []
                      
                 parsed_entities = json.loads(json_str)
                 
                 if isinstance(parsed_entities, list):
                     # Basic validation of list items
                     for item in parsed_entities:
                         if isinstance(item, dict) and 'name' in item and 'type' in item:
                             entities.append(item)
                         else:
                              logger.warning(f"Skipping malformed entity object in VLM response: {item}")
                     return entities 
                 else:
                    logger.warning(f"VLM entity response JSON was not a list: {json_str[:100]}...")
                    return []
            except json.JSONDecodeError as json_err:
                 logger.error(f"Failed to parse VLM entity response as JSON: {json_err}")
                 logger.error(f"VLM Raw Response: {response_text}")
                 return [] # Return empty list on JSON parsing error
            
        except Exception as e:
            logger.error(f"Error extracting entities with PaliGemma: {e}", exc_info=True)
            return []

    async def get_embedding(self, text: str, image: Optional[Image.Image] = None) -> list:
        """Get embedding using PaliGemma (not directly supported via generate)."""
        # PaliGemma generate doesn't typically return embeddings directly.
        # Accessing underlying model components might be needed, or use a different model for embeddings.
        logger.warning("get_embedding not directly supported by this PaliGemma adapter implementation.")
        return []

    def get_token_count(self, text: str) -> int:
        """Estimate token count using the PaliGemma processor."""
        if not self.processor:
            logger.warning("PaliGemma processor not available for token counting.")
            return len(text) // 4 # Rough fallback estimate
        
        try:
            # Use the processor's tokenizer component to encode the text
            # The exact way to access the tokenizer might depend on the processor class
            # Assuming processor itself can handle text directly or has a tokenizer attribute
            if hasattr(self.processor, 'tokenizer'):
                 return len(self.processor.tokenizer.encode(text))
            else:
                 # Fallback if tokenizer attribute isn't standard
                 return len(self.processor(text=text)["input_ids"][0])
        except Exception as e:
            logger.error(f"Error counting tokens with PaliGemma processor: {e}")
            return len(text) // 4 # Fallback estimate

    # Implementing required abstract methods

    async def analyze_document(self, document_text: str) -> Dict[str, Any]:
        """Analyze a document using PaliGemma."""
        logger.info("PaliGemma analyze_document called (text-only).")
        
        # Create a prompt for document analysis
        prompt = f"""
        Please analyze the following legal document and provide:
        1. A summary of the document
        2. Key entities mentioned (people, organizations, dates)
        3. Important clauses or provisions
        4. Potential risks or issues
        5. Recommendations

        Document:
        {document_text[:4000]}  # Truncate to avoid token limits
        """
        
        try:
            # Use the text-only generation function
            response = await self.generate_text(prompt, max_tokens=2000)
            
            # Return a basic structure - in a real implementation, 
            # this would parse the response more robustly
            return {
                "summary": response[:500],  # First part as summary
                "entities": [],  # Would be better to parse from response
                "clauses": [],
                "risks": [],
                "recommendations": []
            }
        except Exception as e:
            logger.error(f"Error analyzing document with PaliGemma: {e}")
            return {
                "summary": f"Error analyzing document: {e}",
                "entities": [],
                "clauses": [],
                "risks": [],
                "recommendations": []
            }

    async def research_query(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Process a legal research query using PaliGemma."""
        logger.info("PaliGemma research_query called.")
        
        prompt = f"""
        Please research the following legal query and provide:
        1. Relevant legal principles
        2. Key precedents or cases
        3. Analysis and interpretation
        4. Conclusion or recommendation

        Query: {query}
        """
        
        if context:
            prompt += f"\nAdditional context: {context}"
        
        try:
            response = await self.generate_text(prompt, max_tokens=2000)
            
            # Simple implementation - in production, would parse more robustly
            return {
                "principles": [],
                "precedents": [],
                "analysis": response[:1000],  # Use response as analysis
                "conclusion": response[1000:1500] if len(response) > 1000 else ""
            }
        except Exception as e:
            logger.error(f"Error processing research query with PaliGemma: {e}")
            return {
                "principles": [],
                "precedents": [],
                "analysis": f"Error processing research query: {e}",
                "conclusion": "Error occurred during processing"
            }

    async def generate_contract(self, template: str, parameters: Dict[str, Any]) -> str:
        """Generate a contract based on a template and parameters using PaliGemma."""
        logger.info("PaliGemma generate_contract called.")
        
        # Replace placeholders in the template with parameter values
        for key, value in parameters.items():
            placeholder = f"{{{key}}}"
            template = template.replace(placeholder, str(value))
        
        prompt = f"""
        Please review and complete the following contract template, filling in any missing details and ensuring legal correctness:

        {template}
        """
        
        try:
            response = await self.generate_text(prompt, max_tokens=3000)
            return response
        except Exception as e:
            logger.error(f"Error generating contract with PaliGemma: {e}")
            return template # Return original template on error 