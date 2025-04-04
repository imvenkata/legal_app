import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
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
  Chip,
  Alert
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import DescriptionIcon from '@mui/icons-material/Description';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { contractAPI } from '../../services/api';
import { 
  setTemplates, 
  setSelectedTemplate, 
  setGeneratedContract, 
  addSavedContract,
  setLoading,
  setError
} from '../../store/contractSlice';
import useLlmModel from '../../hooks/useLlmModel';

const ContractDrafterConnected = () => {
  const dispatch = useDispatch();
  const { templates, selectedTemplate, generatedContract, loading, error } = useSelector(state => state.contract);
  const { preferredLlmModel } = useLlmModel();
  
  const [parameters, setParameters] = useState({});
  const [contractName, setContractName] = useState('');
  const [saving, setSaving] = useState(false);
  const [savedContracts, setSavedContracts] = useState([]);

  // Fetch templates on component mount
  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        dispatch(setLoading(true));
        const response = await contractAPI.getTemplates();
        dispatch(setTemplates(response.data));
        dispatch(setLoading(false));
      } catch (err) {
        dispatch(setError(err.message || 'Failed to fetch templates'));
        dispatch(setLoading(false));
      }
    };

    fetchTemplates();
  }, [dispatch]);

  const handleTemplateChange = async (event) => {
    const templateId = event.target.value;
    
    if (!templateId) {
      dispatch(setSelectedTemplate(null));
      setParameters({});
      dispatch(setGeneratedContract(null));
      return;
    }
    
    try {
      dispatch(setLoading(true));
      const response = await contractAPI.getTemplate(templateId);
      dispatch(setSelectedTemplate(response.data));
      
      // Initialize parameters
      const initialParams = {};
      if (response.data && response.data.parameters) {
        response.data.parameters.forEach(param => {
          initialParams[param.name] = '';
        });
      }
      setParameters(initialParams);
      
      dispatch(setGeneratedContract(null));
      dispatch(setLoading(false));
    } catch (err) {
      dispatch(setError(err.message || 'Failed to fetch template details'));
      dispatch(setLoading(false));
    }
  };

  const handleParameterChange = (name, value) => {
    setParameters({
      ...parameters,
      [name]: value
    });
  };

  const handleGenerateContract = async () => {
    if (!selectedTemplate) return;
    
    // Check if all required parameters are filled
    const missingParams = selectedTemplate.parameters
      .filter(param => param.required && !parameters[param.name])
      .map(param => param.label);
      
    if (missingParams.length > 0) {
      dispatch(setError(`Please fill in the following required fields: ${missingParams.join(', ')}`));
      return;
    }
    
    try {
      dispatch(setLoading(true));
      const response = await contractAPI.generateContract(
        selectedTemplate.id, 
        parameters, 
        preferredLlmModel
      );
      dispatch(setGeneratedContract(response.data.content));
      dispatch(setLoading(false));
    } catch (err) {
      dispatch(setError(err.message || 'Failed to generate contract'));
      dispatch(setLoading(false));
    }
  };

  const handleSaveContract = async () => {
    if (!generatedContract || !contractName) {
      dispatch(setError('Please generate a contract and provide a name before saving.'));
      return;
    }
    
    try {
      setSaving(true);
      
      // Get user ID from localStorage
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id;
      
      if (!userId) {
        throw new Error('User not authenticated');
      }
      
      const contractData = {
        user_id: userId,
        title: contractName,
        content: generatedContract,
        template_id: selectedTemplate ? selectedTemplate.id : null,
        parameters: parameters,
        status: 'draft'
      };
      
      const response = await contractAPI.saveContract(contractData);
      
      dispatch(addSavedContract(response.data));
      setSaving(false);
      setContractName('');
      
      // Show success message
      alert('Contract saved successfully!');
    } catch (err) {
      dispatch(setError(err.message || 'Failed to save contract'));
      setSaving(false);
    }
  };

  // Fetch saved contracts on component mount
  useEffect(() => {
    const fetchSavedContracts = async () => {
      try {
        // Get user ID from localStorage
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        const userId = user.id;
        
        if (!userId) {
          return;
        }
        
        const response = await contractAPI.getContracts(userId);
        setSavedContracts(response.data);
      } catch (err) {
        console.error('Failed to fetch saved contracts:', err);
      }
    };

    fetchSavedContracts();
  }, []);

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Contract Drafting & Generation
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => dispatch(setError(null))}>
          {error}
        </Alert>
      )}
      
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
                value={selectedTemplate ? selectedTemplate.id : ''}
                onChange={handleTemplateChange}
                label="Contract Template"
                disabled={loading}
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
                  {selectedTemplate.description}
                </Typography>
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="h6" gutterBottom>
                  2. Fill Contract Parameters
                </Typography>
                
                {selectedTemplate.parameters && selectedTemplate.parameters.map((param) => (
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
                    disabled={loading}
                  />
                ))}
                
                <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
                  <Typography variant="body2" color="textSecondary" sx={{ mr: 1 }}>
                    Using LLM Model:
                  </Typography>
                  <Chip 
                    label={preferredLlmModel} 
                    color="primary" 
                    size="small" 
                    variant="outlined" 
                  />
                </Box>
                
                <Button
                  fullWidth
                  variant="contained"
                  color="primary"
                  onClick={handleGenerateContract}
                  disabled={loading}
                  sx={{ mt: 2 }}
                >
                  {loading ? <CircularProgress size={24} /> : 'Generate Contract'}
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
                        <Typography variant="subtitle2">{contract.title}</Typography>
                        <Typography variant="caption" color="textSecondary">
                          {contract.status} • {new Date(contract.created_at).toLocaleDateString()}
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
          <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              3. Review & Save Contract
            </Typography>
            
            {generatedContract ? (
              <>
                <Box sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                  <TextField
                    label="Contract Name"
                    value={contractName}
                    onChange={(e) => setContractName(e.target.value)}
                    sx={{ flex: 1, mr: 2 }}
                    disabled={saving}
                  />
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<SaveIcon />}
                    onClick={handleSaveContract}
                    disabled={saving || !contractName}
                  >
                    {saving ? <CircularProgress size={24} /> : 'Save'}
                  </Button>
                </Box>
                
                <Box 
                  sx={{ 
                    flex: 1,
                    border: '1px solid #e0e0e0',
                    borderRadius: 1,
                    p: 2,
                    overflowY: 'auto',
                    bgcolor: '#f9f9f9',
                    fontFamily: 'monospace',
                    fontSize: '0.875rem',
                    whiteSpace: 'pre-wrap',
                    position: 'relative'
                  }}
                >
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<ContentCopyIcon />}
                    sx={{ position: 'absolute', top: 8, right: 8 }}
                    onClick={() => navigator.clipboard.writeText(generatedContract)}
                  >
                    Copy
                  </Button>
                  {generatedContract}
                </Box>
              </>
            ) : (
              <Box 
                sx={{ 
                  flex: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: '1px dashed #ccc',
                  borderRadius: 1,
                  p: 3
                }}
              >
                <Typography variant="body1" color="textSecondary" align="center">
                  {selectedTemplate 
                    ? 'Fill in the parameters and click "Generate Contract" to create your contract'
                    : 'Select a contract template to get started'}
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ContractDrafterConnected;
