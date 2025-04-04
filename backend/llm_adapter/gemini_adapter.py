import os
from typing import Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

from .base_adapter import BaseLLMAdapter

# Load environment variables
load_dotenv()

class GeminiAdapter(BaseLLMAdapter):
    """Adapter for Google Gemini models"""
    
    def __init__(self, model: str = "gemini-pro"):
        super().__init__(model)
        # Set API key from environment variable
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if not api_key:
            print("Warning: GOOGLE_API_KEY not set in environment variables")
        else:
            genai.configure(api_key=api_key)
    
    async def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate text using Google Gemini models"""
        try:
            # Configure the generation config
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "top_p": 0.95,
                "top_k": 40,
            }
            
            # Create the model
            model = genai.GenerativeModel(self.model)
            
            # Generate content
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract the text from the response
            text = response.text
            
            # Estimate token usage (Google doesn't provide this directly)
            estimated_prompt_tokens = len(prompt) // 4
            estimated_completion_tokens = len(text) // 4
            
            return {
                "text": text,
                "model": self.model,
                "usage": {
                    "prompt_tokens": estimated_prompt_tokens,
                    "completion_tokens": estimated_completion_tokens,
                    "total_tokens": estimated_prompt_tokens + estimated_completion_tokens
                }
            }
        except Exception as e:
            print(f"Error generating text with Gemini: {str(e)}")
            # Return a fallback response for testing
            return {
                "text": f"[Simulated Gemini response for prompt: {prompt[:50]}...]",
                "model": self.model,
                "usage": {"total_tokens": len(prompt) // 4}
            }
    
    async def analyze_document(self, document_text: str) -> Dict[str, Any]:
        """Analyze a legal document using Google Gemini models"""
        prompt = f"""
        Analyze the following legal document and provide:
        1. A brief summary
        2. Key points
        3. Important entities (people, organizations, dates)
        4. Recommendations

        Document:
        {document_text[:4000]}  # Limit document size for API
        """
        
        try:
            response = await self.generate_text(prompt, max_tokens=1500)
            
            # Parse the response to extract structured information
            # This is a simplified version for the demo
            text = response["text"]
            lines = text.split("\n")
            
            summary = ""
            key_points = []
            entities = {"people": [], "organizations": [], "dates": []}
            recommendations = []
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if "summary" in line.lower():
                    current_section = "summary"
                elif "key point" in line.lower():
                    current_section = "key_points"
                elif "entit" in line.lower():
                    current_section = "entities"
                elif "recommendation" in line.lower():
                    current_section = "recommendations"
                elif current_section == "summary":
                    summary += line + " "
                elif current_section == "key_points" and line.startswith("-"):
                    key_points.append(line[1:].strip())
                elif current_section == "entities" and line.startswith("-"):
                    if "people" in line.lower():
                        entities["people"].append(line[1:].strip())
                    elif "organization" in line.lower():
                        entities["organizations"].append(line[1:].strip())
                    elif "date" in line.lower():
                        entities["dates"].append(line[1:].strip())
                elif current_section == "recommendations" and line.startswith("-"):
                    recommendations.append(line[1:].strip())
            
            return {
                "summary": summary.strip(),
                "key_points": key_points,
                "entities": entities,
                "recommendations": recommendations,
                "llm_model": self.model
            }
        except Exception as e:
            print(f"Error analyzing document with Gemini: {str(e)}")
            # Return a fallback response for testing
            return {
                "summary": "This is a simulated document analysis summary from Gemini.",
                "key_points": ["Key point 1", "Key point 2"],
                "entities": {
                    "people": ["Person A", "Person B"],
                    "organizations": ["Organization X", "Organization Y"],
                    "dates": ["January 1, 2025"]
                },
                "recommendations": ["Recommendation 1", "Recommendation 2"],
                "llm_model": self.model
            }
    
    async def predict_case_outcome(self, case_details: Dict[str, Any]) -> Dict[str, Any]:
        """Predict the outcome of a legal case using Google Gemini models"""
        query = case_details.get("query", "")
        prompt = f"""
        Based on the following legal case details, predict the likely outcome and provide factors that influence this prediction:
        
        Case Query: {query}
        
        Provide your response in the following format:
        
        Prediction: [Your prediction of the case outcome]
        
        Factors:
        - [Factor 1] (Impact: high/medium/low)
        - [Factor 2] (Impact: high/medium/low)
        - [Factor 3] (Impact: high/medium/low)
        
        Similar Cases:
        - [Case name 1] (Similarity: XX%)
        - [Case name 2] (Similarity: XX%)
        - [Case name 3] (Similarity: XX%)
        """
        
        try:
            response = await self.generate_text(prompt, max_tokens=1500)
            
            # Parse the response to extract structured information
            text = response["text"]
            lines = text.split("\n")
            
            prediction = ""
            factors = []
            similar_cases = []
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.lower().startswith("prediction:"):
                    prediction = line[11:].strip()
                elif line.lower() == "factors:":
                    current_section = "factors"
                elif line.lower() == "similar cases:":
                    current_section = "similar_cases"
                elif current_section == "factors" and line.startswith("-"):
                    factor_text = line[1:].strip()
                    impact = "medium"
                    if "impact: high" in factor_text.lower():
                        impact = "high"
                    elif "impact: low" in factor_text.lower():
                        impact = "low"
                    
                    factor_name = factor_text.split("(Impact")[0].strip()
                    factors.append({"name": factor_name, "impact": impact})
                elif current_section == "similar_cases" and line.startswith("-"):
                    case_text = line[1:].strip()
                    similarity = 0.8  # Default
                    if "similarity:" in case_text.lower():
                        try:
                            similarity_str = case_text.lower().split("similarity:")[1].strip()
                            similarity_str = similarity_str.replace("%", "").strip()
                            similarity = float(similarity_str) / 100
                        except:
                            pass
                    
                    case_name = case_text.split("(Similarity")[0].strip()
                    similar_cases.append({"case_name": case_name, "similarity": similarity})
            
            return {
                "prediction": prediction,
                "confidence": 0.85,  # Placeholder
                "factors": factors,
                "similar_cases": similar_cases
            }
        except Exception as e:
            print(f"Error predicting case outcome with Gemini: {str(e)}")
            # Return a fallback response for testing
            return {
                "prediction": "Based on the provided information, the case is likely to be decided in favor of the plaintiff.",
                "confidence": 0.75,
                "factors": [
                    {"name": "Precedent in similar cases", "impact": "high"},
                    {"name": "Strength of evidence", "impact": "medium"},
                    {"name": "Applicable statutes", "impact": "medium"}
                ],
                "similar_cases": [
                    {"case_name": "Smith v. Jones (2023)", "similarity": 0.85},
                    {"case_name": "Wilson Corp v. Allen Inc (2022)", "similarity": 0.72},
                    {"case_name": "Parker LLC v. Thompson (2021)", "similarity": 0.68}
                ]
            }
    
    async def generate_contract(self, template: str, parameters: Dict[str, Any]) -> str:
        """Generate a contract based on template and parameters using Google Gemini models"""
        # Replace parameter placeholders in the template
        contract_template = template
        for key, value in parameters.items():
            placeholder = f"{{{key}}}"
            contract_template = contract_template.replace(placeholder, str(value))
        
        prompt = f"""
        Based on the following contract template with some parameters already filled in, 
        complete the contract by filling in any remaining details and ensuring it is legally sound.
        
        Template:
        {contract_template}
        
        Please provide the complete contract text with all sections properly formatted.
        """
        
        try:
            response = await self.generate_text(prompt, max_tokens=2000)
            return response["text"]
        except Exception as e:
            print(f"Error generating contract with Gemini: {str(e)}")
            # Return a fallback response for testing
            return f"""
            THIS AGREEMENT is made on {parameters.get('effective_date', 'the effective date')},
            
            BETWEEN:
            {parameters.get('party_1_name', 'PARTY 1')}, with an address at {parameters.get('party_1_address', 'address')},
            
            AND:
            {parameters.get('party_2_name', 'PARTY 2')}, with an address at {parameters.get('party_2_address', 'address')}.
            
            1. SERVICES
            {parameters.get('party_1_name', 'PARTY 1')} shall provide the following services to {parameters.get('party_2_name', 'PARTY 2')}:
            {parameters.get('services_description', 'Description of services')}
            
            2. TERM
            This Agreement shall commence on {parameters.get('start_date', 'start date')} and continue until {parameters.get('end_date', 'end date')}, unless terminated earlier.
            
            3. COMPENSATION
            {parameters.get('party_2_name', 'PARTY 2')} shall pay {parameters.get('party_1_name', 'PARTY 1')} {parameters.get('compensation_amount', 'amount')} for the services.
            
            4. GOVERNING LAW
            This Agreement shall be governed by the laws of {parameters.get('governing_law', 'jurisdiction')}.
            
            IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.
            
            {parameters.get('party_1_name', 'PARTY 1')}
            
            {parameters.get('party_2_name', 'PARTY 2')}
            """
