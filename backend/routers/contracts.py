from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

router = APIRouter()

# Models
class ContractTemplate(BaseModel):
    id: str
    name: str
    description: str
    parameters: List[Dict[str, Any]]

class ContractGenerationRequest(BaseModel):
    template_id: str
    parameters: Dict[str, Any]
    llm_model: str

class ContractResponse(BaseModel):
    id: str
    title: str
    content: str
    template_id: str
    parameters: Dict[str, Any]
    status: str
    created_at: str
    llm_model: str

# Mock contract templates
templates_db = [
    {
        "id": "nda",
        "name": "Non-Disclosure Agreement",
        "description": "Standard NDA for protecting confidential information",
        "parameters": [
            {"name": "party_1_name", "label": "First Party Name", "type": "text", "required": True},
            {"name": "party_1_address", "label": "First Party Address", "type": "text", "required": True},
            {"name": "party_2_name", "label": "Second Party Name", "type": "text", "required": True},
            {"name": "party_2_address", "label": "Second Party Address", "type": "text", "required": True},
            {"name": "effective_date", "label": "Effective Date", "type": "text", "required": True},
            {"name": "term_months", "label": "Term (months)", "type": "number", "required": True},
            {"name": "governing_law", "label": "Governing Law", "type": "text", "required": True}
        ]
    },
    {
        "id": "service",
        "name": "Service Agreement",
        "description": "Contract for professional services",
        "parameters": [
            {"name": "party_1_name", "label": "Service Provider Name", "type": "text", "required": True},
            {"name": "party_1_address", "label": "Service Provider Address", "type": "text", "required": True},
            {"name": "party_2_name", "label": "Client Name", "type": "text", "required": True},
            {"name": "party_2_address", "label": "Client Address", "type": "text", "required": True},
            {"name": "effective_date", "label": "Effective Date", "type": "text", "required": True},
            {"name": "start_date", "label": "Service Start Date", "type": "text", "required": True},
            {"name": "end_date", "label": "Service End Date", "type": "text", "required": True},
            {"name": "services_description", "label": "Description of Services", "type": "textarea", "required": True},
            {"name": "compensation_amount", "label": "Compensation Amount", "type": "text", "required": True},
            {"name": "payment_terms", "label": "Payment Terms", "type": "text", "required": True},
            {"name": "governing_law", "label": "Governing Law", "type": "text", "required": True}
        ]
    },
    {
        "id": "employment",
        "name": "Employment Contract",
        "description": "Standard employment agreement",
        "parameters": [
            {"name": "employer_name", "label": "Employer Name", "type": "text", "required": True},
            {"name": "employer_address", "label": "Employer Address", "type": "text", "required": True},
            {"name": "employee_name", "label": "Employee Name", "type": "text", "required": True},
            {"name": "employee_address", "label": "Employee Address", "type": "text", "required": True},
            {"name": "position_title", "label": "Position Title", "type": "text", "required": True},
            {"name": "start_date", "label": "Start Date", "type": "text", "required": True},
            {"name": "salary_amount", "label": "Salary Amount", "type": "text", "required": True},
            {"name": "payment_frequency", "label": "Payment Frequency", "type": "text", "required": True},
            {"name": "benefits_description", "label": "Benefits Description", "type": "textarea", "required": True},
            {"name": "termination_notice", "label": "Termination Notice Period (days)", "type": "number", "required": True},
            {"name": "governing_law", "label": "Governing Law", "type": "text", "required": True}
        ]
    }
]

# Mock contracts database
contracts_db = {}

# Contract routes
@router.get("/templates", response_model=List[ContractTemplate])
async def get_templates():
    return templates_db

@router.post("/generate", response_model=ContractResponse)
async def generate_contract(request: ContractGenerationRequest):
    # Check if template exists
    template = next((t for t in templates_db if t["id"] == request.template_id), None)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # In a real app, we would use the LLM adapter to generate the contract
    # For demo purposes, we'll generate a simple contract based on the template
    
    contract_id = str(len(contracts_db) + 1)
    
    # Generate contract content based on template
    contract_content = ""
    if request.template_id == "nda":
        contract_content = f"""
        NON-DISCLOSURE AGREEMENT

        THIS AGREEMENT is made on {request.parameters.get('effective_date', 'DATE')},

        BETWEEN:
        {request.parameters.get('party_1_name', 'PARTY 1')}, with an address at {request.parameters.get('party_1_address', 'ADDRESS')} ("Disclosing Party"),

        AND:
        {request.parameters.get('party_2_name', 'PARTY 2')}, with an address at {request.parameters.get('party_2_address', 'ADDRESS')} ("Receiving Party").

        WHEREAS, the Disclosing Party possesses certain confidential and proprietary information, and

        WHEREAS, the Receiving Party is willing to receive and hold such confidential information in confidence under the terms of this Agreement,

        NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree as follows:

        1. DEFINITION OF CONFIDENTIAL INFORMATION
        "Confidential Information" means any information disclosed by the Disclosing Party to the Receiving Party, either directly or indirectly, in writing, orally or by inspection of tangible objects, which is designated as "Confidential," "Proprietary" or some similar designation, or that should reasonably be understood to be confidential given the nature of the information and the circumstances of disclosure.

        2. OBLIGATIONS OF RECEIVING PARTY
        The Receiving Party shall:
        (a) Use the Confidential Information only for the purpose of evaluating potential business and investment relationships with the Disclosing Party;
        (b) Hold the Confidential Information in strict confidence and take reasonable precautions to protect such Confidential Information;
        (c) Not disclose any Confidential Information to any third party without the prior written consent of the Disclosing Party;
        (d) Not copy or reproduce any Confidential Information without the prior written consent of the Disclosing Party.

        3. TERM
        This Agreement shall remain in effect for a period of {request.parameters.get('term_months', '12')} months from the Effective Date.

        4. GOVERNING LAW
        This Agreement shall be governed by and construed in accordance with the laws of {request.parameters.get('governing_law', 'STATE')}.

        IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

        {request.parameters.get('party_1_name', 'PARTY 1')}

        By: ________________________
        Name: 
        Title: 

        {request.parameters.get('party_2_name', 'PARTY 2')}

        By: ________________________
        Name: 
        Title: 
        """
    elif request.template_id == "service":
        contract_content = f"""
        SERVICE AGREEMENT

        THIS AGREEMENT is made on {request.parameters.get('effective_date', 'DATE')},

        BETWEEN:
        {request.parameters.get('party_1_name', 'PROVIDER')}, with an address at {request.parameters.get('party_1_address', 'ADDRESS')} ("Service Provider"),

        AND:
        {request.parameters.get('party_2_name', 'CLIENT')}, with an address at {request.parameters.get('party_2_address', 'ADDRESS')} ("Client").

        WHEREAS, the Client wishes to engage the Service Provider to provide certain services, and

        WHEREAS, the Service Provider is willing to provide such services to the Client under the terms of this Agreement,

        NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree as follows:

        1. SERVICES
        The Service Provider shall provide the following services to the Client:
        {request.parameters.get('services_description', 'DESCRIPTION OF SERVICES')}

        2. TERM
        This Agreement shall commence on {request.parameters.get('start_date', 'START DATE')} and continue until {request.parameters.get('end_date', 'END DATE')}, unless terminated earlier in accordance with this Agreement.

        3. COMPENSATION
        The Client shall pay the Service Provider {request.parameters.get('compensation_amount', 'AMOUNT')} for the services.
        
        4. PAYMENT TERMS
        {request.parameters.get('payment_terms', 'PAYMENT TERMS')}

        5. INDEPENDENT CONTRACTOR
        The Service Provider is an independent contractor and not an employee of the Client. The Service Provider shall be responsible for all taxes, insurance, and other obligations related to the performance of services under this Agreement.

        6. CONFIDENTIALITY
        Each party agrees to maintain the confidentiality of any proprietary or confidential information of the other party disclosed during the performance of this Agreement.

        7. GOVERNING LAW
        This Agreement shall be governed by and construed in accordance with the laws of {request.parameters.get('governing_law', 'STATE')}.

        IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

        {request.parameters.get('party_1_name', 'PROVIDER')}

        By: ________________________
        Name: 
        Title: 

        {request.parameters.get('party_2_name', 'CLIENT')}

        By: ________________________
        Name: 
        Title: 
        """
    elif request.template_id == "employment":
        contract_content = f"""
        EMPLOYMENT AGREEMENT

        THIS AGREEMENT is made on {request.parameters.get('start_date', 'DATE')},

        BETWEEN:
        {request.parameters.get('employer_name', 'EMPLOYER')}, with an address at {request.parameters.get('employer_address', 'ADDRESS')} ("Employer"),

        AND:
        {request.parameters.get('employee_name', 'EMPLOYEE')}, with an address at {request.parameters.get('employee_address', 'ADDRESS')} ("Employee").

        WHEREAS, the Employer desires to employ the Employee, and the Employee desires to accept employment with the Employer, under the terms and conditions set forth in this Agreement,

        NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree as follows:

        1. POSITION AND DUTIES
        The Employer hereby employs the Employee as {request.parameters.get('position_title', 'POSITION')}, and the Employee hereby accepts such employment. The Employee shall perform such duties as are customarily performed by someone in such position and such other duties as may be assigned from time to time by the Employer.

        2. TERM
        This Agreement shall commence on {request.parameters.get('start_date', 'START DATE')} and continue until terminated by either party in accordance with this Agreement.

        3. COMPENSATION
        The Employer shall pay the Employee a salary of {request.parameters.get('salary_amount', 'AMOUNT')}, payable {request.parameters.get('payment_frequency', 'FREQUENCY')}.

        4. BENEFITS
        The Employee shall be entitled to the following benefits:
        {request.parameters.get('benefits_description', 'BENEFITS DESCRIPTION')}

        5. TERMINATION
        Either party may terminate this Agreement by providing the other party with at least {request.parameters.get('termination_notice', '30')} days' written notice.

        6. GOVERNING LAW
        This Agreement shall be governed by and construed in accordance with the laws of {request.parameters.get('governing_law', 'STATE')}.

        IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

        {request.parameters.get('employer_name', 'EMPLOYER')}

        By: ________________________
        Name: 
        Title: 

        {request.parameters.get('employee_name', 'EMPLOYEE')}

        By: ________________________
        """
    
    contract = {
        "id": contract_id,
        "title": template["name"],
        "content": contract_content,
        "template_id": request.template_id,
        "parameters": request.parameters,
        "status": "generated",
        "created_at": datetime.now().isoformat(),
        "llm_model": request.llm_model
    }
    
    contracts_db[contract_id] = contract
    return contract

@router.get("/", response_model=List[ContractResponse])
async def get_contracts():
    return list(contracts_db.values())

@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(contract_id: str):
    if contract_id not in contracts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    return contracts_db[contract_id]
