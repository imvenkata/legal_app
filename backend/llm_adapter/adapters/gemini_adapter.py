import os
from typing import Dict, Any, Optional
from .base_adapter import LlmAdapter
import google.generativeai as genai

class GeminiAdapter(LlmAdapter):
    """
    Adapter for Google Gemini models.
    """
    
    async def initialize(self, api_key: str, model_params: Dict[str, Any]) -> None:
        """Initialize the Gemini adapter with API key and model parameters"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model_name = model_params.get("model", "gemini-pro")
        self.max_tokens = model_params.get("max_tokens", 1000)
        self.temperature = model_params.get("temperature", 0.7)
        self.model = genai.GenerativeModel(self.model_name)
        
    async def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate text using Google Gemini models"""
        try:
            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            print(f"Error generating text with Gemini: {e}")
            return ""
    
    async def analyze_document(self, document_text: str) -> Dict[str, Any]:
        """Analyze a document using Google Gemini models"""
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
            response = await self.generate_text(prompt, max_tokens=2000)
            
            # Process the response into structured data
            lines = response.split('\n')
            result = {
                "summary": "",
                "entities": [],
                "clauses": [],
                "risks": [],
                "recommendations": []
            }
            
            current_section = None
            for line in lines:
                line = line.strip()
                if "summary" in line.lower():
                    current_section = "summary"
                elif "entities" in line.lower() or "key entities" in line.lower():
                    current_section = "entities"
                elif "clauses" in line.lower() or "provisions" in line.lower():
                    current_section = "clauses"
                elif "risks" in line.lower() or "issues" in line.lower():
                    current_section = "risks"
                elif "recommendations" in line.lower():
                    current_section = "recommendations"
                elif line and current_section:
                    if current_section == "summary":
                        result["summary"] += line + " "
                    elif current_section in ["entities", "clauses", "risks", "recommendations"]:
                        if line.startswith("- "):
                            result[current_section].append(line[2:])
                        else:
                            result[current_section].append(line)
            
            return result
        except Exception as e:
            print(f"Error analyzing document with Gemini: {e}")
            return {
                "summary": "Error analyzing document",
                "entities": [],
                "clauses": [],
                "risks": [],
                "recommendations": []
            }
    
    async def research_query(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Process a legal research query using Google Gemini models"""
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
            
            # Process the response into structured data
            lines = response.split('\n')
            result = {
                "principles": [],
                "precedents": [],
                "analysis": "",
                "conclusion": ""
            }
            
            current_section = None
            for line in lines:
                line = line.strip()
                if "principles" in line.lower() or "legal principles" in line.lower():
                    current_section = "principles"
                elif "precedents" in line.lower() or "cases" in line.lower():
                    current_section = "precedents"
                elif "analysis" in line.lower() or "interpretation" in line.lower():
                    current_section = "analysis"
                elif "conclusion" in line.lower() or "recommendation" in line.lower():
                    current_section = "conclusion"
                elif line and current_section:
                    if current_section in ["principles", "precedents"]:
                        if line.startswith("- "):
                            result[current_section].append(line[2:])
                        else:
                            result[current_section].append(line)
                    elif current_section in ["analysis", "conclusion"]:
                        result[current_section] += line + " "
            
            return result
        except Exception as e:
            print(f"Error processing research query with Gemini: {e}")
            return {
                "principles": [],
                "precedents": [],
                "analysis": "Error processing research query",
                "conclusion": "Error processing research query"
            }
    
    async def generate_contract(self, template: str, parameters: Dict[str, Any]) -> str:
        """Generate a contract based on a template and parameters using Google Gemini models"""
        # Replace placeholders in the template with parameter values
        for key, value in parameters.items():
            placeholder = f"{{{key}}}"
            template = template.replace(placeholder, str(value))
        
        prompt = f"""
        Please review and complete the following contract template, filling in any missing details and ensuring legal correctness:

        {template}
        """
        
        try:
            response = await self.generate_text(prompt, max_tokens=3000, temperature=0.2)
            return response
        except Exception as e:
            print(f"Error generating contract with Gemini: {e}")
            return template
    
    async def get_embedding(self, text: str) -> list:
        """Get vector embedding for the provided text using Google Gemini embeddings"""
        try:
            # Note: This is a placeholder as Gemini might use a different approach for embeddings
            # In a real implementation, you would use the appropriate Gemini embedding model
            embedding_model = genai.GenerativeModel("embedding-001")
            result = await embedding_model.generate_content_async(text)
            # This is a simplified approach - actual implementation would depend on Gemini's API
            return result.embedding
        except Exception as e:
            print(f"Error getting embedding with Gemini: {e}")
            return []
    
    def get_token_count(self, text: str) -> int:
        """Count the number of tokens in the provided text"""
        # This is a simplified version - in production, you'd want to use the appropriate tokenizer
        # For now, we'll use a rough approximation
        return len(text.split()) * 1.3  # Rough approximation
