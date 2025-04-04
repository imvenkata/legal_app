import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  TextField, 
  Button, 
  CircularProgress, 
  Divider, 
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import DescriptionIcon from '@mui/icons-material/Description';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

const ContractDrafter = () => {
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [parameters, setParameters] = useState({});
  const [generating, setGenerating] = useState(false);
  const [generatedContract, setGeneratedContract] = useState('');
  const [contractName, setContractName] = useState('');
  const [saving, setSaving] = useState(false);
  const [savedContracts, setSavedContracts] = useState([]);

  // Mock templates
  const templates = [
    { 
      id: 'employment', 
      name: 'Employment Agreement', 
      description: 'Standard employment agreement for full-time employees',
      parameters: [
        { name: 'company_name', label: 'Company Name', type: 'text', required: true },
        { name: 'employee_name', label: 'Employee Name', type: 'text', required: true },
        { name: 'position', label: 'Position/Title', type: 'text', required: true },
        { name: 'start_date', label: 'Start Date', type: 'date', required: true },
        { name: 'salary', label: 'Annual Salary', type: 'number', required: true },
        { name: 'duties', label: 'Job Duties', type: 'textarea', required: true },
      ]
    },
    { 
      id: 'nda', 
      name: 'Non-Disclosure Agreement', 
      description: 'Confidentiality agreement to protect sensitive information',
      parameters: [
        { name: 'disclosing_party', label: 'Disclosing Party', type: 'text', required: true },
        { name: 'receiving_party', label: 'Receiving Party', type: 'text', required: true },
        { name: 'effective_date', label: 'Effective Date', type: 'date', required: true },
        { name: 'purpose', label: 'Purpose of Disclosure', type: 'textarea', required: true },
        { name: 'term_years', label: 'Term (Years)', type: 'number', required: true },
        { name: 'governing_law', label: 'Governing Law State', type: 'text', required: true },
      ]
    },
    { 
      id: 'service', 
      name: 'Service Agreement', 
      description: 'Contract for professional services',
      parameters: [
        { name: 'provider_name', label: 'Service Provider', type: 'text', required: true },
        { name: 'client_name', label: 'Client Name', type: 'text', required: true },
        { name: 'service_description', label: 'Service Description', type: 'textarea', required: true },
        { name: 'start_date', label: 'Start Date', type: 'date', required: true },
        { name: 'end_date', label: 'End Date', type: 'date', required: true },
        { name: 'fee_amount', label: 'Fee Amount', type: 'number', required: true },
        { name: 'payment_terms', label: 'Payment Terms', type: 'text', required: true },
      ]
    },
  ];

  const handleTemplateChange = (event) => {
    const templateId = event.target.value;
    setSelectedTemplate(templateId);
    
    // Reset parameters for new template
    const initialParams = {};
    const template = templates.find(t => t.id === templateId);
    if (template) {
      template.parameters.forEach(param => {
        initialParams[param.name] = '';
      });
    }
    setParameters(initialParams);
    setGeneratedContract('');
  };

  const handleParameterChange = (name, value) => {
    setParameters({
      ...parameters,
      [name]: value
    });
  };

  const handleGenerateContract = () => {
    const template = templates.find(t => t.id === selectedTemplate);
    if (!template) return;
    
    // Check if all required parameters are filled
    const missingParams = template.parameters
      .filter(param => param.required && !parameters[param.name])
      .map(param => param.label);
      
    if (missingParams.length > 0) {
      alert(`Please fill in the following required fields: ${missingParams.join(', ')}`);
      return;
    }
    
    setGenerating(true);
    
    // Simulate API call
    setTimeout(() => {
      let contractText = '';
      
      if (selectedTemplate === 'employment') {
        contractText = `
EMPLOYMENT AGREEMENT

This Employment Agreement (the "Agreement") is made and entered into as of ${parameters.start_date}, by and between ${parameters.company_name} ("Employer") and ${parameters.employee_name} ("Employee").

1. POSITION AND DUTIES

Employer hereby employs Employee as a ${parameters.position}, and Employee hereby accepts such employment, on the terms and conditions set forth herein. Employee shall perform such duties as are customarily performed by other persons in similar positions, including but not limited to: ${parameters.duties}.

2. TERM

The term of this Agreement shall commence on ${parameters.start_date} and shall continue until terminated as provided herein.

3. COMPENSATION

As compensation for services rendered under this Agreement, Employee shall be entitled to receive from Employer a salary of $${parameters.salary} per year, payable in accordance with Employer's normal payroll procedures.

4. CONFIDENTIALITY

Employee acknowledges that during the course of their employment, they may have access to and become acquainted with various trade secrets and confidential information belonging to Employer. Employee agrees not to disclose such information to any person, firm, or entity, except as required in the course of their employment.

5. AT-WILL EMPLOYMENT

Employee's employment with Employer is "at-will," meaning that either Employee or Employer may terminate the employment relationship at any time, with or without cause, and with or without notice.

6. GOVERNING LAW

This Agreement shall be governed by and construed in accordance with the laws of the state where Employer's principal place of business is located.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

${parameters.company_name}

By: ________________________

${parameters.employee_name}

________________________
        `;
      } else if (selectedTemplate === 'nda') {
        contractText = `
NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement (the "Agreement") is entered into as of ${parameters.effective_date} by and between ${parameters.disclosing_party} ("Disclosing Party") and ${parameters.receiving_party} ("Receiving Party").

1. PURPOSE

The Receiving Party acknowledges that in connection with ${parameters.purpose} (the "Purpose"), the Receiving Party will have access to certain confidential and proprietary information of the Disclosing Party.

2. CONFIDENTIAL INFORMATION

"Confidential Information" means any information disclosed by the Disclosing Party to the Receiving Party, either directly or indirectly, in writing, orally or by inspection of tangible objects, that is designated as "Confidential," "Proprietary," or some similar designation, or that should reasonably be understood to be confidential given the nature of the information and the circumstances of disclosure.

3. NON-DISCLOSURE AND NON-USE

The Receiving Party agrees not to use any Confidential Information for any purpose except to evaluate and engage in discussions concerning the Purpose. The Receiving Party agrees not to disclose any Confidential Information to third parties or to its employees, except to those employees who are required to have the information in order to evaluate or engage in discussions concerning the Purpose.

4. TERM

The obligations of the Receiving Party under this Agreement shall survive for a period of ${parameters.term_years} years from the date of disclosure of the Confidential Information.

5. GOVERNING LAW

This Agreement shall be governed by and construed in accordance with the laws of the State of ${parameters.governing_law}, without regard to conflicts of law principles.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

${parameters.disclosing_party}

By: ________________________

${parameters.receiving_party}

By: ________________________
        `;
      } else if (selectedTemplate === 'service') {
        contractText = `
SERVICE AGREEMENT

This Service Agreement (the "Agreement") is made and entered into as of ${parameters.start_date}, by and between ${parameters.provider_name} ("Service Provider") and ${parameters.client_name} ("Client").

1. SERVICES

Service Provider agrees to provide the following services to Client: ${parameters.service_description} (the "Services").

2. TERM

The term of this Agreement shall commence on ${parameters.start_date} and shall continue until ${parameters.end_date}, unless earlier terminated as provided herein.

3. COMPENSATION

Client agrees to pay Service Provider the sum of $${parameters.fee_amount} for the Services. Payment shall be made as follows: ${parameters.payment_terms}.

4. INDEPENDENT CONTRACTOR

Service Provider is an independent contractor, and neither Service Provider nor Service Provider's staff is, or shall be deemed, Client's employees.

5. INTELLECTUAL PROPERTY

All intellectual property rights in any materials produced by Service Provider in connection with the Services shall be the property of Client.

6. TERMINATION

Either party may terminate this Agreement upon written notice to the other party in the event of a material breach of this Agreement by the other party.

7. GOVERNING LAW

This Agreement shall be governed by and construed in accordance with the laws of the state where Client's principal place of business is located.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

${parameters.provider_name}

By: ________________________

${parameters.client_name}

By: ________________________
        `;
      }
      
      setGeneratedContract(contractText);
      setGenerating(false);
    }, 2000);
  };

  const handleSaveContract = () => {
    if (!generatedContract || !contractName) {
      alert('Please generate a contract and provide a name before saving.');
      return;
    }
    
    setSaving(true);
    
    // Simulate API call
    setTimeout(() => {
      const newContract = {
        id: Date.now().toString(),
        name: contractName,
        template: templates.find(t => t.id === selectedTemplate)?.name || 'Custom Contract',
        created: new Date().toISOString(),
        content: generatedContract
      };
      
      setSavedContracts([...savedContracts, newContract]);
      setSaving(false);
      setContractName('');
      
      // Show success message
      alert('Contract saved successfully!');
    }, 1000);
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Contract Drafting & Generation
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              1. Select Contract Template
            </Typography>
            
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel id="template-select-label">Contract Template</InputLabel>
              <Select
                labelId="template-select-label"
                value={selectedTemplate}
                onChange={handleTemplateChange}
                label="Contract Template"
              >
                <MenuItem value="">
                  <em>Select a template</em>
                </MenuItem>
                {templates.map((template) => (
                  <MenuItem key={template.id} value={template.id}>
                    {template.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            {selectedTemplate && (
              <>
                <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                  {templates.find(t => t.id === selectedTemplate)?.description}
                </Typography>
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="h6" gutterBottom>
                  2. Fill Contract Parameters
                </Typography>
                
                {templates.find(t => t.id === selectedTemplate)?.parameters.map((param) => (
                  <TextField
                    key={param.name}
                    label={param.label}
                    fullWidth
                    margin="normal"
                    required={param.required}
                    type={param.type === 'textarea' ? 'text' : param.type}
                    multiline={param.type === 'textarea'}
                    rows={param.type === 'textarea' ? 3 : 1}
                    value={parameters[param.name] || ''}
                    onChange={(e) => handleParameterChange(param.name, e.target.value)}
                  />
                ))}
                
                <Button
                  fullWidth
                  variant="contained"
                  color="primary"
                  onClick={handleGenerateContract}
                  disabled={generating}
                  sx={{ mt: 2 }}
                >
                  {generating ? <CircularProgress size={24} /> : 'Generate Contract'}
                </Button>
              </>
            )}
          </Paper>
          
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Saved Contracts
            </Typography>
            
            {savedContracts.length === 0 ? (
              <Typography variant="body2" color="textSecondary" sx={{ textAlign: 'center', py: 2 }}>
                No saved contracts yet
              </Typography>
            ) : (
              savedContracts.map((contract) => (
                <Accordion key={contract.id}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                      <DescriptionIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="subtitle2">{contract.name}</Typography>
                        <Typography variant="caption" color="textSecondary">
                          {contract.template} • {new Date(contract.created).toLocaleDateString()}
                        </Typography>
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box sx={{ mb: 2 }}>
                      <Button 
                        size="small" 
                        variant="outlined" 
                        startIcon={<EditIcon />}
                        sx={{ mr: 1 }}
                      >
                        Edit
                      </Button>
                      <Button 
                        size="small" 
                        variant="outlined" 
                        startIcon={<ContentCopyIcon />}
                      >
                        Duplicate
                      </Button>
                    </Box>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', fontSize: '0.75rem' }}>
                      {contract.content.substring(0, 200)}...
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              ))
            )}
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column'<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>