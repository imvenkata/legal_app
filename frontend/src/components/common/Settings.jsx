import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  TextField, 
  Switch, 
  FormControlLabel,
  Button,
  Divider,
  Grid,
  Card,
  CardContent,
  CardHeader,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Alert
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import NotificationsIcon from '@mui/icons-material/Notifications';
import SecurityIcon from '@mui/icons-material/Security';
import LanguageIcon from '@mui/icons-material/Language';

const Settings = () => {
  const [settings, setSettings] = useState({
    llmModel: 'gpt-4',
    apiKey: '',
    theme: 'light',
    notifications: {
      email: true,
      inApp: true,
      documentAnalysis: true,
      researchUpdates: false,
      contractGeneration: true
    },
    language: 'en'
  });
  
  const [saveSuccess, setSaveSuccess] = useState(false);
  
  const handleModelChange = (event) => {
    setSettings({
      ...settings,
      llmModel: event.target.value
    });
  };
  
  const handleApiKeyChange = (event) => {
    setSettings({
      ...settings,
      apiKey: event.target.value
    });
  };
  
  const handleThemeChange = (event) => {
    setSettings({
      ...settings,
      theme: event.target.checked ? 'dark' : 'light'
    });
  };
  
  const handleNotificationChange = (key) => (event) => {
    setSettings({
      ...settings,
      notifications: {
        ...settings.notifications,
        [key]: event.target.checked
      }
    });
  };
  
  const handleLanguageChange = (event) => {
    setSettings({
      ...settings,
      language: event.target.value
    });
  };
  
  const handleSaveSettings = () => {
    // Simulate API call to save settings
    setTimeout(() => {
      setSaveSuccess(true);
      
      // Hide success message after 3 seconds
      setTimeout(() => {
        setSaveSuccess(false);
      }, 3000);
    }, 500);
  };
  
  // Available LLM models
  const llmModels = [
    { id: 'gpt-4', name: 'GPT-4', provider: 'OpenAI' },
    { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'OpenAI' },
    { id: 'gemini-pro', name: 'Gemini Pro', provider: 'Google' },
    { id: 'gemini-ultra', name: 'Gemini Ultra', provider: 'Google' },
    { id: 'deepseek-chat', name: 'DeepSeek Chat', provider: 'DeepSeek' },
    { id: 'deepseek-coder', name: 'DeepSeek Coder', provider: 'DeepSeek' }
  ];
  
  // Available languages
  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'zh', name: 'Chinese' },
    { code: 'ja', name: 'Japanese' }
  ];
  
  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      
      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Settings saved successfully!
        </Alert>
      )}
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="LLM Model Settings" 
              avatar={<SmartToyIcon color="primary" />}
            />
            <Divider />
            <CardContent>
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel id="llm-model-label">LLM Model</InputLabel>
                <Select
                  labelId="llm-model-label"
                  value={settings.llmModel}
                  onChange={handleModelChange}
                  label="LLM Model"
                >
                  {llmModels.map((model) => (
                    <MenuItem key={model.id} value={model.id}>
                      {model.name} ({model.provider})
                    </MenuItem>
                  ))}
                </Select>
                <Typography variant="caption" color="textSecondary" sx={{ mt: 1 }}>
                  Select the LLM model to use for all AI-powered features
                </Typography>
              </FormControl>
              
              <TextField
                fullWidth
                label="API Key"
                type="password"
                value={settings.apiKey}
                onChange={handleApiKeyChange}
                helperText="Enter your API key for the selected model provider"
              />
              
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Model Information
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="Provider" 
                      secondary={llmModels.find(m => m.id === settings.llmModel)?.provider || 'Unknown'} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Features" 
                      secondary="Document Analysis, Legal Research, Contract Generation" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Token Limit" 
                      secondary={settings.llmModel.includes('gpt-4') ? '8,192 tokens' : '4,096 tokens'} 
                    />
                  </ListItem>
                </List>
              </Box>
            </CardContent>
          </Card>
          
          <Card sx={{ mt: 3 }}>
            <CardHeader 
              title="Appearance" 
              avatar={<DarkModeIcon color="primary" />}
            />
            <Divider />
            <CardContent>
              <FormControlLabel
                control={
                  <Switch 
                    checked={settings.theme === 'dark'} 
                    onChange={handleThemeChange} 
                  />
                }
                label="Dark Mode"
              />
              
              <FormControl fullWidth sx={{ mt: 3 }}>
                <InputLabel id="language-label">Language</InputLabel>
                <Select
                  labelId="language-label"
                  value={settings.language}
                  onChange={handleLanguageChange}
                  label="Language"
                >
                  {languages.map((lang) => (
                    <MenuItem key={lang.code} value={lang.code}>
                      {lang.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="Notifications" 
              avatar={<NotificationsIcon color="primary" />}
            />
            <Divider />
            <CardContent>
              <Typography variant="subtitle2" gutterBottom>
                Notification Channels
              </Typography>
              <FormControlLabel
                control={
                  <Switch 
                    checked={settings.notifications.email} 
                    onChange={handleNotificationChange('email')} 
                  />
                }
                label="Email Notifications"
              />
              <FormControlLabel
                control={
                  <Switch 
                    checked={settings.notifications.inApp} 
                    onChange={handleNotificationChange('inApp')} 
                  />
                }
                label="In-App Notifications"
              />
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="subtitle2" gutterBottom>
                Notification Types
              </Typography>
              <FormControlLabel
                control={
                  <Switch 
                    checked={settings.notifications.documentAnalysis} 
                    onChange={handleNotificationChange('documentAnalysis')} 
                  />
                }
                label="Document Analysis Completion"
              />
              <FormControlLabel
                control={
                  <Switch 
                    checked={settings.notifications.researchUpdates} 
                    onChange={handleNotificationChange('researchUpdates')} 
                  />
                }
                label="Research Updates"
              />
              <FormControlLabel
                control={
                  <Switch 
                    checked={settings.notifications.contractGeneration} 
                    onChange={handleNotificationChange('contractGeneration')} 
                  />
                }
                label="Contract Generation Completion"
              />
            </CardContent>
          </Card>
          
          <Card sx={{ mt: 3 }}>
            <CardHeader 
              title="Security & Privacy" 
              avatar={<SecurityIcon color="primary" />}
            />
            <Divider />
            <CardContent>
              <Typography variant="body2" paragraph>
                Your data security and privacy are important to us. Configure how your data is stored and processed.
              </Typography>
              
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Enable data encryption"
              />
              
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Store documents locally when possible"
              />
              
              <FormControlLabel
                control={<Switch />}
                label="Allow anonymous usage statistics"
              />
              
              <Box sx={{ mt: 2 }}>
                <Button variant="outlined" color="error" size="small">
                  Delete All Data
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<SaveIcon />}
          onClick={handleSaveSettings}
          size="large"
        >
          Save Settings
        </Button>
      </Box>
    </Box>
  );
};

export default Settings;
