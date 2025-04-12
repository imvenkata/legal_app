import os
from typing import Dict, Any, Optional
from .base_adapter import LlmAdapter
from openai import AsyncOpenAI

class OpenAiAdapter(LlmAdapter):
    """
    Adapter for OpenAI GPT models.
    """
    
    async def initialize(self, api_key: str, model_params: Dict[str, Any]) -> None:
        """Initialize the OpenAI adapter with API key and model parameters"""
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model_params.get("model", "gpt-4")
        self.max_tokens = model_params.get("max_tokens", 1000)
        self.temperature = model_params.get("temperature", 0.7)
        
    async def generate_text(self, prompt: str, max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> str:
        """Generate text using OpenAI GPT models"""
        try:
            current_max_tokens = max_tokens if max_tokens is not None else self.max_tokens
            current_temperature = temperature if temperature is not None else self.temperature
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=current_max_tokens,
                temperature=current_temperature
            )
            if response.choices and response.choices[0].message:
                return response.choices[0].message.content or ""
            else:
                print("OpenAI response did not contain expected content.")
                return ""
        except Exception as e:
            print(f"Error generating text with OpenAI ({self.model}): {e}")
            return ""
    
    async def analyze_document(self, document_text: str) -> Dict[str, Any]:
        """Analyze a document using OpenAI GPT models"""
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
            response_text = await self.generate_text(prompt, max_tokens=2000)
            if not response_text:
                 raise ValueError("Received empty response from generate_text")
                 
            lines = response_text.split('\n')
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
                if not line: continue
                
                lower_line = line.lower()
                if "summary" in lower_line and ":" in lower_line:
                    current_section = "summary"
                    result["summary"] = line.split(":", 1)[1].strip()
                elif ("entities" in lower_line or "key entities" in lower_line) and ":" in lower_line:
                    current_section = "entities"
                elif ("clauses" in lower_line or "provisions" in lower_line) and ":" in lower_line:
                    current_section = "clauses"
                elif ("risks" in lower_line or "issues" in lower_line) and ":" in lower_line:
                    current_section = "risks"
                elif "recommendations" in lower_line and ":" in lower_line:
                    current_section = "recommendations"
                elif current_section:
                    if current_section in ["entities", "clauses", "risks", "recommendations"]:
                        if line.startswith(('-', '*', '1.', '2.', '3.', '4.', '5.')):
                            result[current_section].append(line.split(" ", 1)[1].strip() if " " in line else line)
                        else:
                             result[current_section].append(line)
                    elif current_section == "summary":
                        result["summary"] += " " + line

            result["summary"] = result["summary"].strip()
            
            return result
        except Exception as e:
            print(f"Error analyzing document with OpenAI: {e}")
            return {
                "summary": f"Error analyzing document: {e}",
                "entities": [],
                "clauses": [],
                "risks": [],
                "recommendations": []
            }
    
    async def research_query(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Process a legal research query using OpenAI GPT models"""
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
            response_text = await self.generate_text(prompt, max_tokens=2000)
            if not response_text:
                 raise ValueError("Received empty response from generate_text")
            
            lines = response_text.split('\n')
            result = {
                "principles": [],
                "precedents": [],
                "analysis": "",
                "conclusion": ""
            }
            
            current_section = None
            for line in lines:
                line = line.strip()
                if not line: continue

                lower_line = line.lower()
                if ("principles" in lower_line or "legal principles" in lower_line) and ":" in lower_line:
                    current_section = "principles"
                elif ("precedents" in lower_line or "cases" in lower_line) and ":" in lower_line:
                    current_section = "precedents"
                elif ("analysis" in lower_line or "interpretation" in lower_line) and ":" in lower_line:
                    current_section = "analysis"
                    result["analysis"] = line.split(":", 1)[1].strip()
                elif ("conclusion" in lower_line or "recommendation" in lower_line) and ":" in lower_line:
                    current_section = "conclusion"
                    result["conclusion"] = line.split(":", 1)[1].strip()
                elif current_section:
                    if current_section in ["principles", "precedents"]:
                        if line.startswith(('-', '*', '1.', '2.', '3.', '4.', '5.')):
                            result[current_section].append(line.split(" ", 1)[1].strip() if " " in line else line)
                        else:
                             result[current_section].append(line)
                    elif current_section == "analysis":
                        result["analysis"] += " " + line
                    elif current_section == "conclusion":
                        result["conclusion"] += " " + line

            result["analysis"] = result["analysis"].strip()
            result["conclusion"] = result["conclusion"].strip()
            
            return result
        except Exception as e:
            print(f"Error processing research query with OpenAI: {e}")
            return {
                "principles": [],
                "precedents": [],
                "analysis": f"Error processing research query: {e}",
                "conclusion": f"Error processing research query: {e}"
            }
    
    async def generate_contract(self, template: str, parameters: Dict[str, Any]) -> str:
        """Generate a contract based on a template and parameters using OpenAI GPT models"""
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
            print(f"Error generating contract with OpenAI: {e}")
            return template
    
    async def get_embedding(self, text: str, model: str = "text-embedding-3-small") -> list:
        """Get vector embedding for the provided text using OpenAI embeddings"""
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=text
            )
            if response.data and response.data[0].embedding:
                return response.data[0].embedding
            else:
                print("OpenAI embedding response did not contain expected data.")
                return []
        except Exception as e:
            print(f"Error getting embedding with OpenAI ({model}): {e}")
            return []
    
    def get_token_count(self, text: str) -> int:
        """Count the number of tokens in the provided text"""
        # This is a simplified version - in production, you'd want to use tiktoken
        # For now, we'll use a rough approximation
        return len(text.split()) * 1.3  # Rough approximation
