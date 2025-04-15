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
  Chip,
  Tooltip
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
      if (!document) {
        throw new Error('Document not found');
      }
      
      // Check if document is ready for analysis
      if (document.status !== 'parsing_completed' && document.status !== 'uploaded' && 
          document.status !== 'analysis_failed' && document.status !== 'error') {
        if (document.status === 'parsing_failed') {
          throw new Error('Document parsing failed. Please upload the document again.');
        } else if (document.status === 'analyzing' || document.status === 'parsing') {
          throw new Error('Document is currently being processed. Please wait.');
        } else if (document.status === 'analyzed') {
          // If already analyzed, just get the analysis instead of redoing it
          dispatch(setLoading(false));
          handleViewAnalysis(document);
          return;
        } else {
          throw new Error(`Document cannot be analyzed in its current state: ${document.status}`);
        }
      }
      
      // Update document status to analyzing
      dispatch(setDocuments(
        documents.map(doc => 
          doc.id === id ? { ...doc, status: 'analyzing' } : doc
        )
      ));
      
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
      
      // Find current document state to properly revert status
      const currentDoc = documents.find(doc => doc.id === id);
      if (currentDoc && currentDoc.status === 'analyzing') {
        // Only revert if we changed it to analyzing
        const originalStatus = currentDoc.status === 'analyzing' ? 
          (currentDoc.status === 'parsing_completed' ? 'parsing_completed' : 'uploaded') : 
          currentDoc.status;
        
        dispatch(setDocuments(
          documents.map(doc => 
            doc.id === id ? { ...doc, status: originalStatus } : doc
          )
        ));
      }
    }
  };

  const handleViewAnalysis = (document) => {
    // Set the current document and navigate to the analysis view
    dispatch(setCurrentDocument(document));
    // If you have analysis data for this document, you can retrieve it here
    // or fetch it from the server
    documentAPI.getDocumentAnalysis(document.id)
      .then(response => {
        dispatch(setAnalysisResult(response.data));
      })
      .catch(err => {
        dispatch(setError(err.message || 'Failed to fetch analysis'));
      });
  };

  const formatStatus = (status) => {
    const statusMap = {
      'uploaded': 'Uploaded',
      'parsing': 'Processing',
      'parsing_failed': 'Processing Failed',
      'parsing_completed': 'Ready for Analysis',
      'analyzing': 'Analyzing',
      'analysis_failed': 'Analysis Failed',
      'analyzed': 'Analyzed',
      'deleting': 'Deleting',
      'deleted': 'Deleted',
      'error': 'Error'
    };
    return statusMap[status] || status;
  };

  const getStatusColor = (status) => {
    const statusColorMap = {
      'uploaded': 'default',
      'parsing': 'info',
      'parsing_failed': 'error',
      'parsing_completed': 'info',
      'analyzing': 'info',
      'analysis_failed': 'error',
      'analyzed': 'success',
      'deleting': 'warning',
      'deleted': 'default',
      'error': 'error'
    };
    return statusColorMap[status] || 'default';
  };

  const getStatusDescription = (status) => {
    const statusDescriptionMap = {
      'uploaded': 'Document has been uploaded but not yet processed',
      'parsing': 'Document is being processed for text extraction',
      'parsing_failed': 'Failed to extract text from the document',
      'parsing_completed': 'Document text has been extracted and is ready for analysis',
      'analyzing': 'Document is being analyzed by AI',
      'analysis_failed': 'Failed to analyze the document',
      'analyzed': 'Document has been successfully analyzed',
      'deleting': 'Document is being deleted',
      'deleted': 'Document has been deleted',
      'error': 'An error occurred with this document'
    };
    return statusDescriptionMap[status] || 'Unknown status';
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
                  {doc.file_type} • 
                  <Tooltip title={getStatusDescription(doc.status)}>
                    <Chip 
                      label={formatStatus(doc.status)} 
                      size="small" 
                      color={getStatusColor(doc.status)}
                      sx={{ ml: 1 }}
                    />
                  </Tooltip>
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
              {(doc.status === 'parsing' || doc.status === 'analyzing') && (
                <Button
                  variant="outlined"
                  color="primary"
                  disabled
                  sx={{ mr: 1 }}
                >
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  {doc.status === 'parsing' ? 'Processing...' : 'Analyzing...'}
                </Button>
              )}
              {(doc.status === 'parsing_failed' || doc.status === 'analysis_failed' || doc.status === 'error') && (
                <Button
                  variant="outlined"
                  color="error"
                  onClick={() => handleAnalyze(doc.id)}
                  sx={{ mr: 1 }}
                >
                  Retry
                </Button>
              )}
              {doc.status === 'analyzed' && (
                <Button
                  variant="outlined"
                  color="success"
                  sx={{ mr: 1 }}
                  onClick={() => handleViewAnalysis(doc)}
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
