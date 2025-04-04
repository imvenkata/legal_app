import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { 
  Box, 
  Typography, 
  Paper, 
  Button, 
  TextField, 
  CircularProgress, 
  Alert,
  Chip
} from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DescriptionIcon from '@mui/icons-material/Description';
import DeleteIcon from '@mui/icons-material/Delete';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import { documentAPI } from '../../services/api';
import { 
  setDocuments, 
  addDocument, 
  setCurrentDocument, 
  setAnalysisResult, 
  removeDocument,
  setLoading,
  setError,
  clearError
} from '../../store/documentSlice';
import useLlmModel from '../../hooks/useLlmModel';

// Styled components
const UploadBox = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  border: '2px dashed #ccc',
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.background.default,
  height: '200px',
  cursor: 'pointer',
  '&:hover': {
    borderColor: theme.palette.primary.main,
    backgroundColor: theme.palette.background.paper,
  },
}));

const DocumentItem = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
}));

const DocumentUploaderConnected = () => {
  const dispatch = useDispatch();
  const { documents, loading, error } = useSelector(state => state.document);
  const { preferredLlmModel } = useLlmModel();
  
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);

  // Fetch documents on component mount
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        dispatch(setLoading(true));
        
        // Get user ID from localStorage
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        const userId = user.id;
        
        if (!userId) {
          throw new Error('User not authenticated');
        }
        
        const response = await documentAPI.getDocuments(userId);
        dispatch(setDocuments(response.data));
        dispatch(setLoading(false));
      } catch (err) {
        dispatch(setError(err.message || 'Failed to fetch documents'));
        dispatch(setLoading(false));
      }
    };

    fetchDocuments();
  }, [dispatch]);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleUpload = async () => {
    if (!selectedFile || !title) {
      dispatch(setError('Please provide a title and select a file'));
      return;
    }

    try {
      dispatch(setLoading(true));
      
      // Get user ID from localStorage
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id;
      
      if (!userId) {
        throw new Error('User not authenticated');
      }
      
      // Create form data
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('title', title);
      formData.append('description', description);
      formData.append('user_id', userId);
      
      const response = await documentAPI.uploadDocument(formData);
      
      dispatch(addDocument(response.data));
      setSelectedFile(null);
      setTitle('');
      setDescription('');
      dispatch(setLoading(false));
    } catch (err) {
      dispatch(setError(err.message || 'Failed to upload document'));
      dispatch(setLoading(false));
    }
  };

  const handleDelete = async (id) => {
    try {
      dispatch(setLoading(true));
      await documentAPI.deleteDocument(id);
      dispatch(removeDocument(id));
      dispatch(setLoading(false));
    } catch (err) {
      dispatch(setError(err.message || 'Failed to delete document'));
      dispatch(setLoading(false));
    }
  };

  const handleAnalyze = async (id) => {
    try {
      dispatch(setLoading(true));
      
      // Find the document to update its status
      const document = documents.find(doc => doc.id === id);
      if (document) {
        // Update document status to analyzing
        dispatch(setDocuments(
          documents.map(doc => 
            doc.id === id ? { ...doc, status: 'analyzing' } : doc
          )
        ));
      }
      
      const response = await documentAPI.analyzeDocument(id, preferredLlmModel);
      
      // Update document status to analyzed
      dispatch(setDocuments(
        documents.map(doc => 
          doc.id === id ? { ...doc, status: 'analyzed' } : doc
        )
      ));
      
      // Set analysis result
      dispatch(setAnalysisResult(response.data));
      
      // Set current document
      dispatch(setCurrentDocument(document));
      
      dispatch(setLoading(false));
    } catch (err) {
      dispatch(setError(err.message || 'Failed to analyze document'));
      dispatch(setLoading(false));
      
      // Revert document status
      dispatch(setDocuments(
        documents.map(doc => 
          doc.id === id ? { ...doc, status: 'uploaded' } : doc
        )
      ));
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Document Upload & Analysis
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => dispatch(clearError())}>
          {error}
        </Alert>
      )}
      
      <Box sx={{ mb: 4 }}>
        <TextField
          fullWidth
          label="Document Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          margin="normal"
          required
          disabled={loading}
        />
        <TextField
          fullWidth
          label="Description (Optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          margin="normal"
          multiline
          rows={2}
          disabled={loading}
        />
        
        <UploadBox
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onClick={() => document.getElementById('file-input').click()}
        >
          <input
            id="file-input"
            type="file"
            accept=".pdf,.doc,.docx,.txt"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
            disabled={loading}
          />
          <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
          {selectedFile ? (
            <Typography variant="body1">{selectedFile.name}</Typography>
          ) : (
            <Typography variant="body1">
              Drag and drop a file here, or click to select a file
            </Typography>
          )}
          <Typography variant="caption" color="textSecondary" sx={{ mt: 1 }}>
            Supported formats: PDF, DOC, DOCX, TXT
          </Typography>
        </UploadBox>
        
        <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
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
            variant="contained"
            color="primary"
            onClick={handleUpload}
            disabled={!selectedFile || !title || loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Upload Document'}
          </Button>
        </Box>
      </Box>
      
      <Typography variant="h5" gutterBottom>
        Your Documents
      </Typography>
      
      {documents.length === 0 ? (
        <Typography variant="body1" color="textSecondary" sx={{ textAlign: 'center', py: 4 }}>
          No documents uploaded yet
        </Typography>
      ) : (
        documents.map((doc) => (
          <DocumentItem key={doc.id}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <DescriptionIcon sx={{ mr: 2, color: 'primary.main' }} />
              <Box>
                <Typography variant="subtitle1">{doc.title}</Typography>
                <Typography variant="body2" color="textSecondary">
                  {doc.file_type} • {doc.status}
                </Typography>
              </Box>
            </Box>
            <Box>
              {doc.status === 'uploaded' && (
                <Button
                  variant="outlined"
                  color="primary"
                  onClick={() => handleAnalyze(doc.id)}
                  sx={{ mr: 1 }}
                  startIcon={<AnalyticsIcon />}
                >
                  Analyze
                </Button>
              )}
              {doc.status === 'analyzing' && (
                <Button
                  variant="outlined"
                  color="primary"
                  disabled
                  sx={{ mr: 1 }}
                >
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  Analyzing...
                </Button>
              )}
              {doc.status === 'analyzed' && (
                <Button
                  variant="outlined"
                  color="success"
                  sx={{ mr: 1 }}
                >
                  View Analysis
                </Button>
              )}
              <Button
                variant="outlined"
                color="error"
                onClick={() => handleDelete(doc.id)}
              >
                <DeleteIcon />
              </Button>
            </Box>
          </DocumentItem>
        ))
      )}
    </Box>
  );
};

export default DocumentUploaderConnected;
