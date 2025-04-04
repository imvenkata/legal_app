import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  templates: [],
  selectedTemplate: null,
  parameters: {},
  generatedContract: null,
  loading: false,
  error: null
};

export const contractSlice = createSlice({
  name: 'contract',
  initialState,
  reducers: {
    fetchTemplatesStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchTemplatesSuccess: (state, action) => {
      state.loading = false;
      state.templates = action.payload;
    },
    fetchTemplatesFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    generateContractStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    generateContractSuccess: (state, action) => {
      state.loading = false;
      state.generatedContract = action.payload;
    },
    generateContractFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    setSelectedTemplate: (state, action) => {
      state.selectedTemplate = action.payload;
      // Reset parameters when template changes
      state.parameters = {};
    },
    setParameter: (state, action) => {
      state.parameters = {
        ...state.parameters,
        [action.payload.name]: action.payload.value
      };
    },
    clearGeneratedContract: (state) => {
      state.generatedContract = null;
    },
    clearError: (state) => {
      state.error = null;
    }
  }
});

export const {
  fetchTemplatesStart,
  fetchTemplatesSuccess,
  fetchTemplatesFailure,
  generateContractStart,
  generateContractSuccess,
  generateContractFailure,
  setSelectedTemplate,
  setParameter,
  clearGeneratedContract,
  clearError
} = contractSlice.actions;

// Thunk actions
export const fetchTemplates = () => async (dispatch) => {
  try {
    dispatch(fetchTemplatesStart());
    
    // In a real app, this would call the API service
    // const response = await contractService.getTemplates();
    
    // Simulate API call for demo
    await new Promise(resolve => setTimeout(resolve, 1000));
    const response = [
      {
        id: 'nda',
        name: 'Non-Disclosure Agreement',
        description: 'Standard NDA for protecting confidential information',
        parameters: [
          { name: 'party_1_name', label: 'First Party Name', type: 'text', required: true },
          { name: 'party_1_address', label: 'First Party Address', type: 'text', required: true },
          { name: 'party_2_name', label: 'Second Party Name', type: 'text', required: true },
          { name: 'party_2_address', label: 'Second Party Address', type: 'text', required: true },
          { name: 'effective_date', label: 'Effective Date', type: 'text', required: true },
          { name: 'term_months', label: 'Term (months)', type: 'number', required: true },
          { name: 'governing_law', label: 'Governing Law', type: 'text', required: true }
        ]
      },
      {
        id: 'service',
        name: 'Service Agreement',
        description: 'Contract for professional services',
        parameters: [
          { name: 'party_1_name', label: 'Service Provider Name', type: 'text', required: true },
          { name: 'party_1_address', label: 'Service Provider Address', type: 'text', required: true },
          { name: 'party_2_name', label: 'Client Name', type: 'text', required: true },
          { name: 'party_2_address', label: 'Client Address', type: 'text', required: true },
          { name: 'effective_date', label: 'Effective Date', type: 'text', required: true },
          { name: 'start_date', label: 'Service Start Date', type: 'text', required: true },
          { name: 'end_date', label: 'Service End Date', type: 'text', required: true },
          { name: 'services_description', label: 'Description of Services', type: 'textarea', required: true },
          { name: 'compensation_amount', label: 'Compensation Amount', type: 'text', required: true },
          { name: 'payment_terms', label: 'Payment Terms', type: 'text', required: true },
          { name: 'governing_law', label: 'Governing Law', type: 'text', required: true }
        ]
      },
      {
        id: 'employment',
        name: 'Employment Contract',
        description: 'Standard employment agreement',
        parameters: [
          { name: 'employer_name', label: 'Employer Name', type: 'text', required: true },
          { name: 'employer_address', label: 'Employer Address', type: 'text', required: true },
          { name: 'employee_name', label: 'Employee Name', type: 'text', required: true },
          { name: 'employee_address', label: 'Employee Address', type: 'text', required: true },
          { name: 'position_title', label: 'Position Title', type: 'text', required: true },
          { name: 'start_date', label: 'Start Date', type: 'text', required: true },
          { name: 'salary_amount', label: 'Salary Amount', type: 'text', required: true },
          { name: 'payment_frequency', label: 'Payment Frequency', type: 'text', required: true },
          { name: 'benefits_description', label: 'Benefits Description', type: 'textarea', required: true },
          { name: 'termination_notice', label: 'Termination Notice Period (days)', type: 'number', required: true },
          { name: 'governing_law', label: 'Governing Law', type: 'text', required: true }
        ]
      }
    ];
    
    dispatch(fetchTemplatesSuccess(response));
    return response;
  } catch (error) {
    dispatch(fetchTemplatesFailure(error.message));
    throw error;
  }
};

export const generateContract = (templateId, parameters, llmModel) => async (dispatch) => {
  try {
    dispatch(generateContractStart());
    
    // In a real app, this would call the API service
    // const response = await contractService.generateContract(templateId, parameters, llmModel);
    
    // Simulate API call for demo
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    let contractText = '';
    const template = templateId;
    
    if (template === 'nda') {
      contractText = `
      NON-DISCLOSURE AGREEMENT

      THIS AGREEMENT is made on ${parameters.effective_date},

      BETWEEN:
      ${parameters.party_1_name}, with an address at ${parameters.party_1_address} ("Disclosing Party"),

      AND:
      ${parameters.party_2_name}, with an address at ${parameters.party_2_address} ("Receiving Party").

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
      This Agreement shall remain in effect for a period of ${parameters.term_months} months from the Effective Date.

      4. GOVERNING LAW
      This Agreement shall be governed by and construed in accordance with the laws of ${parameters.governing_law}.

      IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

      ${parameters.party_1_name}

      By: ________________________
      Name: 
      Title: 

      ${parameters.party_2_name}

      By: ________________________
      Name: 
      Title: 
      `;
    } else if (template === 'service') {
      contractText = `
      SERVICE AGREEMENT

      THIS AGREEMENT is made on ${parameters.effective_date},

      BETWEEN:
      ${parameters.party_1_name}, with an address at ${parameters.party_1_address} ("Service Provider"),

      AND:
      ${parameters.party_2_name}, with an address at ${parameters.party_2_address} ("Client").

      WHEREAS, the Client wishes to engage the Service Provider to provide certain services, and

      WHEREAS, the Service Provider is willing to provide such services to the Client under the terms of this Agreement,

      NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree as follows:

      1. SERVICES
      The Service Provider shall provide the following services to the Client:
      ${parameters.services_description}

      2. TERM
      This Agreement shall commence on ${parameters.start_date} and continue until ${parameters.end_date}, unless terminated earlier in accordance with this Agreement.

      3. COMPENSATION
      The Client shall pay the Service Provider ${parameters.compensation_amount} for the services.
      
      4. PAYMENT TERMS
      ${parameters.payment_terms}

      5. INDEPENDENT CONTRACTOR
      The Service Provider is an independent contractor and not an employee of the Client. The Service Provider shall be responsible for all taxes, insurance, and other obligations related to the performance of services under this Agreement.

      6. CONFIDENTIALITY
      Each party agrees to maintain the confidentiality of any proprietary or confidential information of the other party disclosed during the performance of this Agreement.

      7. GOVERNING LAW
      This Agreement shall be governed by and construed in accordance with the laws of ${parameters.governing_law}.

      IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

      ${parameters.party_1_name}

      By: ________________________
      Name: 
      Title: 

      ${parameters.party_2_name}

      By: ________________________
      Name: 
      Title: 
      `;
    } else if (template === 'employment') {
      contractText = `
      EMPLOYMENT AGREEMENT

      THIS AGREEMENT is made on ${parameters.start_date},

      BETWEEN:
      ${parameters.employer_name}, with an address at ${parameters.employer_address} ("Employer"),

      AND:
      ${parameters.employee_name}, with an address at ${parameters.employee_address} ("Employee").

      WHEREAS, the Employer desires to employ the Employee, and the Employee desires to accept employment with the Employer, under the terms and conditions set forth in this Agreement,

      NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree as follows:

      1. POSITION AND DUTIES
      The Employer hereby employs the Employee as ${parameters.position_title}, and the Employee hereby accepts such employment. The Employee shall perform such duties as are customarily performed by someone in such position and such other duties as may be assigned from time to time by the Employer.

      2. TERM
      This Agreement shall commence on ${parameters.start_date} and continue until terminated by either party in accordance with this Agreement.

      3. COMPENSATION
      The Employer shall pay the Employee a salary of ${parameters.salary_amount}, payable ${parameters.payment_frequency}.

      4. BENEFITS
      The Employee shall be entitled to the following benefits:
      ${parameters.benefits_description}

      5. TERMINATION
      Either party may terminate this Agreement by providing the other party with at least ${parameters.termination_notice} days' written notice.

      6. GOVERNING LAW
      This Agreement shall be governed by and construed in accordance with the laws of ${parameters.governing_law}.

      IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

      ${parameters.employer_name}

      By: ________________________
      Name: 
      Title: 

      ${parameters.employee_name}

      By: ________________________
      `;
    }
    
    const response = {
      id: Math.random().toString(36).substring(2, 9),
      title: template === 'nda' ? 'Non-Disclosure Agreement' : 
             template === 'service' ? 'Service Agreement' : 'Employment Contract',
      content: contractText,
      template_id: templateId,
      parameters: parameters,
      status: 'generated',
      created_at: new Date().toISOString(),
      llm_model: llmModel
    };
    
    dispatch(generateContractSuccess(response));
    return response;
  } catch (error) {
    dispatch(generateContractFailure(error.message));
    throw error;
  }
};

export default contractSlice.reducer;
