import React, { useState, useRef } from 'react';
import { 
  Typography, 
  Paper, 
  Button, 
  Box, 
  Container, 
  CircularProgress,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  Chip,
  TextField,
  IconButton,
  Card,
  CardContent,
  LinearProgress
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import ArticleIcon from '@mui/icons-material/Article';
import SummarizeIcon from '@mui/icons-material/Summarize';
import FactCheckIcon from '@mui/icons-material/FactCheck';
import WarningIcon from '@mui/icons-material/Warning';
import GroupIcon from '@mui/icons-material/Group';
import BusinessIcon from '@mui/icons-material/Business';
import ChatIcon from '@mui/icons-material/Chat';
import SendIcon from '@mui/icons-material/Send';
import { api } from '../services/api';

function DocumentAnalysis() {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);
  const [document, setDocument] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const fileInputRef = useRef();
  
  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      // Auto-fill title with filename (without extension)
      const fileName = selectedFile.name.split('.').slice(0, -1).join('.');
      setTitle(fileName || 'Document');
    }
  };
  
  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }
    
    if (!title.trim()) {
      setError('Please provide a title for the document');
      return;
    }
    
    setLoading(true);
    setError(null);
    setUploadProgress(0);
    
    try {
      // Create form data
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title);
      if (description) {
        formData.append('description', description);
      }
      
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          const newProgress = prev + Math.random() * 20;
          return newProgress >= 90 ? 90 : newProgress;
        });
      }, 500);
      
      // Upload document
      const response = await api.post('/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // Set the uploaded document
      setDocument(response.data);
      
      // Reset form
      setFile(null);
      setTitle('');
      setDescription('');
      fileInputRef.current.value = '';
      
      // Automatically start analysis
      analyzeDocument(response.data.id);
      
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || 'Failed to upload document. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const analyzeDocument = async (documentId) => {
    setAnalysisLoading(true);
    setError(null);
    
    try {
      const response = await api.post(`/api/documents/${documentId}/analyze`, {
        model: "document-analyzer"
      });
      
      setAnalysis(response.data);
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.response?.data?.detail || 'Failed to analyze document. Please try again.');
    } finally {
      setAnalysisLoading(false);
    }
  };
  
  const handleSendMessage = async () => {
    if (!chatInput.trim() || !document) return;
    
    const userMessage = chatInput.trim();
    setChatInput('');
    
    // Add user message to chat
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setChatLoading(true);
    
    try {
      const response = await api.post(`/api/documents/${document.id}/chat`, {
        query: userMessage,
        model: "document-analyzer"
      });
      
      // Replace all messages with the complete history from the server
      setChatMessages(response.data.messages);
    } catch (err) {
      console.error('Chat error:', err);
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error processing your request.' 
      }]);
    } finally {
      setChatLoading(false);
    }
  };
  
  const renderUploadForm = () => (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Upload Document
      </Typography>
      
      <Box sx={{ mb: 2 }}>
        <Button
          variant="outlined"
          component="label"
          startIcon={<UploadFileIcon />}
          sx={{ mb: 1 }}
        >
          Select File
          <input
            ref={fileInputRef}
            type="file"
            hidden
            onChange={handleFileChange}
            accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
          />
        </Button>
        {file && (
          <Typography variant="body2" sx={{ ml: 1 }}>
            {file.name} ({(file.size / 1024).toFixed(2)} KB)
          </Typography>
        )}
      </Box>
      
      <TextField
        label="Document Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        fullWidth
        margin="normal"
        required
      />
      
      <TextField
        label="Description (Optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        fullWidth
        margin="normal"
        multiline
        rows={2}
      />
      
      {error && (
        <Alert severity="error" sx={{ mt: 2, mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {loading && (
        <Box sx={{ width: '100%', mt: 2, mb: 2 }}>
          <LinearProgress variant="determinate" value={uploadProgress} />
          <Typography variant="body2" align="center" sx={{ mt: 1 }}>
            Uploading... {Math.round(uploadProgress)}%
          </Typography>
        </Box>
      )}
      
      <Button
        variant="contained"
        onClick={handleUpload}
        disabled={loading}
        sx={{ mt: 2 }}
      >
        Upload & Analyze
      </Button>
    </Paper>
  );
  
  const renderAnalysisResult = () => {
    if (!analysis) return null;
    
    return (
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Analysis Results
        </Typography>
        
        <Box sx={{ mt: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Card variant="outlined">
                <CardContent>
                  <Box display="flex" alignItems="center" mb={1}>
                    <SummarizeIcon color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6">Summary</Typography>
                  </Box>
                  <Typography variant="body1">
                    {analysis.summary}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={1}>
                    <FactCheckIcon color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6">Key Points</Typography>
                  </Box>
                  <List dense>
                    {analysis.key_points.map((point, index) => (
                      <ListItem key={index}>
                        <ListItemIcon sx={{ minWidth: '30px' }}>•</ListItemIcon>
                        <ListItemText primary={point} />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={1}>
                    <WarningIcon color="warning" sx={{ mr: 1 }} />
                    <Typography variant="h6">Potential Risks</Typography>
                  </Box>
                  <List dense>
                    {analysis.risks.map((risk, index) => (
                      <ListItem key={index}>
                        <ListItemIcon sx={{ minWidth: '30px' }}>⚠️</ListItemIcon>
                        <ListItemText primary={risk} />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12}>
              <Card variant="outlined">
                <CardContent>
                  <Box display="flex" alignItems="center" mb={1}>
                    <Typography variant="h6">Entities</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {analysis.entities.map((entity, index) => (
                      <Chip 
                        key={index}
                        icon={entity.type === 'person' ? <GroupIcon /> : <BusinessIcon />}
                        label={`${entity.name} (${entity.type})`}
                        variant="outlined"
                        color={entity.type === 'person' ? 'primary' : 'secondary'}
                      />
                    ))}
                    {analysis.entities.length === 0 && (
                      <Typography variant="body2">No entities identified</Typography>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    );
  };
  
  const renderChat = () => {
    if (!document) return null;
    
    return (
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom display="flex" alignItems="center">
          <ChatIcon sx={{ mr: 1 }} />
          Chat with Document
        </Typography>
        
        <Box sx={{ height: '300px', overflowY: 'auto', mb: 2, p: 2, border: '1px solid #eee', borderRadius: 1 }}>
          {chatMessages.length === 0 ? (
            <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 10 }}>
              Ask questions about this document to get started
            </Typography>
          ) : (
            chatMessages.map((msg, index) => (
              <Box 
                key={index}
                sx={{
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  mb: 2
                }}
              >
                <Paper
                  elevation={1}
                  sx={{
                    p: 2,
                    maxWidth: '80%',
                    bgcolor: msg.role === 'user' ? 'primary.light' : 'grey.100',
                    color: msg.role === 'user' ? 'white' : 'text.primary'
                  }}
                >
                  <Typography variant="body1" style={{ whiteSpace: 'pre-line' }}>
                    {msg.content}
                  </Typography>
                </Paper>
              </Box>
            ))
          )}
          {chatLoading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
              <CircularProgress size={24} />
            </Box>
          )}
        </Box>
        
        <Box sx={{ display: 'flex' }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Ask a question about this document..."
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            disabled={chatLoading}
          />
          <IconButton 
            color="primary" 
            onClick={handleSendMessage} 
            disabled={chatLoading || !chatInput.trim()}
            sx={{ ml: 1 }}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Paper>
    );
  };
  
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Document Analysis
        </Typography>
        
        {!document && renderUploadForm()}
        
        {document && !analysis && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
            <Typography variant="body1" sx={{ ml: 2 }}>
              Analyzing document...
            </Typography>
          </Box>
        )}
        
        {document && (
          <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
            <Box display="flex" alignItems="center">
              <ArticleIcon sx={{ mr: 1 }} />
              <Typography variant="h6">
                {document.title}
              </Typography>
            </Box>
            {document.description && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {document.description}
              </Typography>
            )}
            <Typography variant="caption" display="block" sx={{ mt: 1 }}>
              Uploaded on: {new Date(document.created_at).toLocaleString()}
            </Typography>
          </Paper>
        )}
        
        {analysisLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
            <Typography variant="body1" sx={{ ml: 2 }}>
              Analyzing document...
            </Typography>
          </Box>
        )}
        
        {analysis && renderAnalysisResult()}
        
        {document && renderChat()}
      </Box>
    </Container>
  );
}

export default DocumentAnalysis;
