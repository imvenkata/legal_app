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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert
} from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';

function Settings() {
  const [llmProvider, setLlmProvider] = useState('openai');
  const [llmModel, setLlmModel] = useState('gpt-4');
  const [apiKey, setApiKey] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  
  const providers = {
    openai: {
      name: 'OpenAI',
      models: ['gpt-4', 'gpt-3.5-turbo']
    },
    gemini: {
      name: 'Google Gemini',
      models: ['gemini-pro']
    },
    deepseek: {
      name: 'DeepSeek',
      models: ['deepseek-chat']
    }
  };

  const handleProviderChange = (event) => {
    const newProvider = event.target.value;
    setLlmProvider(newProvider);
    // Set default model for the selected provider
    setLlmModel(providers[newProvider].models[0]);
  };

  const handleSaveSettings = () => {
    setIsSaving(true);
    
    // Simulate API call delay
    setTimeout(() => {
      console.log('Saving settings:', { llmProvider, llmModel, apiKey });
      setIsSaving(false);
      setSaveSuccess(true);
      
      // Hide success message after 3 seconds
      setTimeout(() => {
        setSaveSuccess(false);
      }, 3000);
    }, 1000);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      <Typography variant="body1" paragraph>
        Configure your LLM model preferences and API keys.
      </Typography>
      
      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Settings saved successfully!
        </Alert>
      )}
      
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          LLM Model Configuration
        </Typography>
        
        <FormControl fullWidth margin="normal">
          <InputLabel id="llm-provider-label">LLM Provider</InputLabel>
          <Select
            labelId="llm-provider-label"
            id="llm-provider-select"
            value={llmProvider}
            label="LLM Provider"
            onChange={handleProviderChange}
          >
            {Object.entries(providers).map(([key, provider]) => (
              <MenuItem key={key} value={key}>{provider.name}</MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <FormControl fullWidth margin="normal">
          <InputLabel id="llm-model-label">LLM Model</InputLabel>
          <Select
            labelId="llm-model-label"
            id="llm-model-select"
            value={llmModel}
            label="LLM Model"
            onChange={(e) => setLlmModel(e.target.value)}
          >
            {providers[llmProvider].models.map((model) => (
              <MenuItem key={model} value={model}>{model}</MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <TextField
          label={`${providers[llmProvider].name} API Key`}
          variant="outlined"
          fullWidth
          margin="normal"
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          helperText={`Enter your ${providers[llmProvider].name} API key. This will be stored securely.`}
        />
        
        <Button 
          variant="contained" 
          color="primary" 
          onClick={handleSaveSettings}
          disabled={isSaving}
          startIcon={isSaving ? <CircularProgress size={20} /> : <SettingsIcon />}
          sx={{ mt: 2 }}
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </Paper>
      
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Application Information
        </Typography>
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2">Version</Typography>
          <Typography variant="body2">1.0.0</Typography>
        </Box>
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2">Backend Status</Typography>
          <Typography variant="body2" sx={{ color: 'success.main' }}>Connected</Typography>
        </Box>
        
        <Box>
          <Typography variant="subtitle2">Support</Typography>
          <Typography variant="body2">For support, please contact support@legalai.example.com</Typography>
        </Box>
      </Paper>
    </Box>
  );
}

export default Settings;
