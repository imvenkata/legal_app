import React, { useState } from 'react';
import { 
  Typography, 
  Paper, 
  Button, 
  Box, 
  TextField, 
  CircularProgress,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import DescriptionIcon from '@mui/icons-material/Description';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';

function ContractGeneration() {
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [parameters, setParameters] = useState({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContract, setGeneratedContract] = useState(null);
  const [llmModel, setLlmModel] = useState('gpt-4');

  // Simulated contract templates
  const contractTemplates = [
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

  const handleTemplateChange = (event) => {
    const templateId = event.target.value;
    setSelectedTemplate(templateId);
    
    // Reset parameters when template changes
    const initialParams = {};
    const template = contractTemplates.find(t => t.id === templateId);
    if (template) {
      template.parameters.forEach(param => {
        initialParams[param.name] = '';
      });
    }
    setParameters(initialParams);
    setGeneratedContract(null);
  };

  const handleParameterChange = (paramName, value) => {
    setParameters(prev => ({
      ...prev,
      [paramName]: value
    }));
  };

  const handleGenerate = () => {
    const template = contractTemplates.find(t => t.id === selectedTemplate);
    if (!template) return;
    
    // Check if all required parameters are filled
    const missingParams = template.parameters
      .filter(param => param.required && !parameters[param.name])
      .map(param => param.name);
    
    if (missingParams.length > 0) {
      alert(`Please fill in all required parameters: ${missingParams.join(', ')}`);
      return;
    }
    
    setIsGenerating(true);
    
    // Simulate contract generation delay
    setTimeout(() => {
      // Generate a simulated contract based on the template and parameters
      let contractText = '';
      
      if (selectedTemplate === 'nda') {
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
      } else if (selectedTemplate === 'service') {
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
      } else if (selectedTemplate === 'employment') {
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
        The Employee shall serve as ${parameters.position_title} and shall perform such duties as are customarily associated with such position and as may be assigned by the Employer from time to time.

        2. COMPENSATION
        The Employee shall receive a salary of ${parameters.salary_amount} per ${parameters.payment_frequency}.

        3. BENEFITS
        The Employee shall be entitled to the following benefits:
        ${parameters.benefits_description}

        4. TERM AND TERMINATION
        This Agreement shall commence on ${parameters.start_date} and continue until terminated by either party upon ${parameters.termination_notice} days' written notice.

        5. GOVERNING LAW
        This Agreement shall be governed by and construed in accordance with the laws of ${parameters.governing_law}.

        IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

        ${parameters.employer_name}

        By: ________________________
        Name: 
        Title: 

        ${parameters.employee_name}

        By: ________________________
        Name: 
        Title: 
        `;
      }

      setGeneratedContract(contractText);
      setIsGenerating(false);
    }, 1500);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Contract Generation
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Select Template</InputLabel>
          <Select
            value={selectedTemplate}
            onChange={handleTemplateChange}
            label="Select Template"
          >
            {contractTemplates.map((template) => (
              <MenuItem key={template.id} value={template.id}>
                {template.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {selectedTemplate && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Parameters
            </Typography>
            <Grid container spacing={2}>
              {contractTemplates
                .find((t) => t.id === selectedTemplate)
                ?.parameters.map((param) => (
                  <Grid item xs={12} sm={6} key={param.name}>
                    <TextField
                      fullWidth
                      label={param.label}
                      value={parameters[param.name] || ''}
                      onChange={(e) => handleParameterChange(param.name, e.target.value)}
                      required={param.required}
                      multiline={param.type === 'textarea'}
                      rows={param.type === 'textarea' ? 4 : 1}
                    />
                  </Grid>
                ))}
            </Grid>

            <Button
              variant="contained"
              color="primary"
              onClick={handleGenerate}
              disabled={isGenerating}
              fullWidth
              sx={{ mt: 3 }}
              startIcon={isGenerating ? <CircularProgress size={20} /> : <AutoFixHighIcon />}
            >
              {isGenerating ? 'Generating...' : 'Generate Contract'}
            </Button>
          </Box>
        )}
      </Paper>

      {generatedContract && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Generated Contract
          </Typography>
          <Card>
            <CardContent>
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
                {generatedContract}
              </pre>
            </CardContent>
          </Card>
        </Paper>
      )}
    </Box>
  );
}

export default ContractGeneration;