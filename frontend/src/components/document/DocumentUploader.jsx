import React, { useState } from 'react';
import { Box, Typography, Paper, Button, TextField, CircularProgress } from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DescriptionIcon from '@mui/icons-material/Description';
import DeleteIcon from '@mui/icons-material/Delete';
import IngestionUploader from './IngestionUploader';

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

const DocumentUploader = () => {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);

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
    if (!selectedFile || !title) return;

    setUploading(true);

    // In a real implementation, this would use the API service to upload the file
    // For now, we'll simulate an upload
    setTimeout(() => {
      const newDocument = {
        id: Date.now().toString(),
        title,
        description,
        fileName: selectedFile.name,
        fileSize: selectedFile.size,
        uploadDate: new Date().toISOString(),
        status: 'uploaded',
      };

      setDocuments([...documents, newDocument]);
      setSelectedFile(null);
      setTitle('');
      setDescription('');
      setUploading(false);
    }, 1500);
  };

  const handleDelete = (id) => {
    setDocuments(documents.filter(doc => doc.id !== id));
  };

  const handleAnalyze = (id) => {
    setDocuments(documents.map(doc => 
      doc.id === id ? { ...doc, status: 'analyzing' } : doc
    ));

    // Simulate analysis
    setTimeout(() => {
      setDocuments(documents.map(doc => 
        doc.id === id ? { ...doc, status: 'analyzed' } : doc
      ));
    }, 2000);
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Document Management
      </Typography>
      
      <Typography variant="h5" gutterBottom sx={{mt: 2}}> 
         Upload Document with Metadata
      </Typography>
      <Box sx={{ mb: 4 }}>
        <TextField
          fullWidth
          label="Document Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          margin="normal"
          required
        />
        <TextField
          fullWidth
          label="Description (Optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          margin="normal"
          multiline
          rows={2}
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
        
        <Button
          fullWidth
          variant="contained"
          color="primary"
          onClick={handleUpload}
          disabled={!selectedFile || !title || uploading}
          sx={{ mt: 2 }}
        >
          {uploading ? <CircularProgress size={24} /> : 'Upload Document'}
        </Button>
      </Box>
      
      <IngestionUploader />

      <Typography variant="h5" gutterBottom sx={{mt: 4}}>
        Your Documents (Managed List)
      </Typography>
      
      {documents.length === 0 ? (
        <Typography variant="body1" color="textSecondary" sx={{ textAlign: 'center', py: 4 }}>
          No documents uploaded via this section yet
        </Typography>
      ) : (
        documents.map((doc) => (
          <DocumentItem key={doc.id}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <DescriptionIcon sx={{ mr: 2, color: 'primary.main' }} />
              <Box>
                <Typography variant="subtitle1">{doc.title}</Typography>
                <Typography variant="body2" color="textSecondary">
                  {doc.fileName} • {(doc.fileSize / 1024).toFixed(2)} KB
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

export default DocumentUploader;
