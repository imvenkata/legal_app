import React, { useState, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useDropzone } from 'react-dropzone';
import { 
    Box, 
    Typography, 
    Paper, 
    Button, 
    List, 
    ListItem, 
    ListItemIcon, 
    ListItemText, 
    LinearProgress, 
    Alert, 
    IconButton,
    Tooltip
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DescriptionIcon from '@mui/icons-material/Description';
import ClearIcon from '@mui/icons-material/Clear';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';

import { uploadDocsForIngestion, clearIngestionUploadStatus } from '../../store/documentSlice';

const IngestionUploader = () => {
    const [selectedFiles, setSelectedFiles] = useState([]);
    const dispatch = useDispatch();
    const {
        ingestionUploading, 
        ingestionUploadError, 
        lastIngestionUploadResult
    } = useSelector((state) => state.document);

    const onDrop = useCallback((acceptedFiles) => {
        // Append new files to the existing list
        setSelectedFiles(prevFiles => [...prevFiles, ...acceptedFiles]);
        // Clear previous upload status/errors when new files are added
        if (lastIngestionUploadResult || ingestionUploadError) {
            dispatch(clearIngestionUploadStatus());
        }
    }, [dispatch, lastIngestionUploadResult, ingestionUploadError]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
            'application/msword': ['.doc'], // Older Word format
            'text/plain': ['.txt'],
        },
        multiple: true,
    });

    const handleUpload = () => {
        if (selectedFiles.length === 0) return;

        const formData = new FormData();
        selectedFiles.forEach((file) => {
            formData.append('files', file); // Key must match FastAPI endpoint ('files')
        });

        dispatch(uploadDocsForIngestion(formData));
        // Clear selected files after dispatching upload
        setSelectedFiles([]); 
    };
    
    const handleClearSelection = () => {
        setSelectedFiles([]);
        dispatch(clearIngestionUploadStatus());
    };

    return (
        <Paper elevation={2} sx={{ p: 3, mt: 4 }}>
             <Typography variant="h6" gutterBottom>
                Upload Documents for Search Indexing
            </Typography>
            
            <Box 
                {...getRootProps()} 
                sx={{
                    p: 3,
                    border: '2px dashed #ccc',
                    borderRadius: 1,
                    textAlign: 'center',
                    cursor: 'pointer',
                    backgroundColor: isDragActive ? 'action.hover' : 'background.default',
                    mb: 2,
                    '&:hover': { borderColor: 'primary.main' }
                }}
            >
                <input {...getInputProps()} />
                <CloudUploadIcon sx={{ fontSize: 40, color: 'primary.light', mb: 1 }} />
                {isDragActive ? (
                    <Typography>Drop the files here ...</Typography>
                ) : (
                    <Typography>Drag 'n' drop files here, or click to select (PDF, DOCX, TXT)</Typography>
                )}
            </Box>

            {selectedFiles.length > 0 && (
                <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2">Files ready for upload:</Typography>
                    <List dense>
                        {selectedFiles.map((file, index) => (
                            <ListItem key={index} disableGutters>
                                <ListItemIcon sx={{ minWidth: '30px'}}><DescriptionIcon fontSize="small" /></ListItemIcon>
                                <ListItemText primary={file.name} secondary={`${(file.size / 1024).toFixed(1)} KB`} />
                            </ListItem>
                        ))}
                    </List>
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1, mt: 1 }}>
                         <Button onClick={handleClearSelection} size="small" color="inherit">
                            Clear Selection
                         </Button>
                        <Button 
                            variant="contained" 
                            onClick={handleUpload} 
                            disabled={ingestionUploading}
                            startIcon={ingestionUploading ? <CircularProgress size={16} color="inherit"/> : <CloudUploadIcon />}
                        >
                            {ingestionUploading ? 'Uploading...' : `Upload ${selectedFiles.length} File(s)`}
                        </Button>
                    </Box>
                </Box>
            )}

            {/* Display Upload Progress/Status */}
            {ingestionUploading && <LinearProgress sx={{ my: 2 }} />}
            
            {ingestionUploadError && (
                <Alert severity="error" sx={{ my: 2 }}>
                    Upload failed: {ingestionUploadError}
                </Alert>
            )}

            {lastIngestionUploadResult && (
                <Alert severity="success" sx={{ my: 2 }} action={
                    <Tooltip title="Clear Status">
                        <IconButton
                            color="inherit"
                            size="small"
                            onClick={() => dispatch(clearIngestionUploadStatus())}
                        >
                            <ClearIcon fontSize="inherit" />
                        </IconButton>
                     </Tooltip>
                }>
                    {lastIngestionUploadResult.message} (Files: {lastIngestionUploadResult.filenames?.join(', ') || 'N/A'})
                    <Typography variant="caption" display="block" sx={{mt: 0.5}}>
                        Ingestion is running in the background. Search results will update shortly.
                    </Typography>
                </Alert>
            )}
        </Paper>
    );
};

export default IngestionUploader; 