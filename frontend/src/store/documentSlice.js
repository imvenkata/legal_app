import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
// Import the API function we created
import { searchAPI } from '../services/api'; 

const initialState = {
  documents: [],
  currentDocument: null,
  analysis: null,
  loading: false,
  error: null,

  // New state for multi-document upload to search service
  ingestionUploading: false,
  ingestionUploadError: null,
  ingestionUploadProgress: 0, // Placeholder for future progress tracking
  lastIngestionUploadResult: null, // Store the API response
};

// --- New Async Thunk for Search Service Upload --- 
export const uploadDocsForIngestion = createAsyncThunk(
  'document/uploadForIngestion',
  async (formData, { rejectWithValue }) => {
    // formData is expected to be a FormData object with a 'files' key
    try {
      // Use the correct API function from searchAPI
      const response = await searchAPI.uploadLegalDocs(formData);
      // API returns { message: "...", filenames: [...] }
      return response.data; 
    } catch (error) {
      console.error("Error uploading documents for ingestion:", error);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to upload documents';
      return rejectWithValue(errorMsg);
    }
  }
);

export const documentSlice = createSlice({
  name: 'document',
  initialState,
  reducers: {
    fetchDocumentsStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchDocumentsSuccess: (state, action) => {
      state.loading = false;
      state.documents = action.payload;
    },
    fetchDocumentsFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    uploadDocumentStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    uploadDocumentSuccess: (state, action) => {
      state.loading = false;
      state.documents = [...state.documents, action.payload];
      state.currentDocument = action.payload;
    },
    uploadDocumentFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    analyzeDocumentStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    analyzeDocumentSuccess: (state, action) => {
      state.loading = false;
      state.analysis = action.payload;
    },
    analyzeDocumentFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    setCurrentDocument: (state, action) => {
      state.currentDocument = action.payload;
    },
    clearAnalysis: (state) => {
      state.analysis = null;
    },
    clearError: (state) => {
      state.error = null;
      state.ingestionUploadError = null; // Clear new error state too
    },
    // Add reducer to clear upload status if needed
    clearIngestionUploadStatus: (state) => {
        state.ingestionUploading = false;
        state.ingestionUploadError = null;
        state.ingestionUploadProgress = 0;
        state.lastIngestionUploadResult = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Handle uploadDocsForIngestion lifecycle
      .addCase(uploadDocsForIngestion.pending, (state) => {
        state.ingestionUploading = true;
        state.ingestionUploadError = null;
        state.ingestionUploadProgress = 0;
        state.lastIngestionUploadResult = null;
      })
      .addCase(uploadDocsForIngestion.fulfilled, (state, action) => {
        state.ingestionUploading = false;
        state.lastIngestionUploadResult = action.payload; // Store { message, filenames }
        state.ingestionUploadProgress = 100; // Basic completion indication
        // Note: We don't modify state.documents here as ingestion happens in the background
      })
      .addCase(uploadDocsForIngestion.rejected, (state, action) => {
        state.ingestionUploading = false;
        state.ingestionUploadError = action.payload; 
        state.lastIngestionUploadResult = null;
      });
      // Add cases for existing thunks if they are converted later
  }
});

export const {
  fetchDocumentsStart,
  fetchDocumentsSuccess,
  fetchDocumentsFailure,
  uploadDocumentStart,
  uploadDocumentSuccess,
  uploadDocumentFailure,
  analyzeDocumentStart,
  analyzeDocumentSuccess,
  analyzeDocumentFailure,
  setCurrentDocument,
  clearAnalysis,
  clearError,
  clearIngestionUploadStatus
} = documentSlice.actions;

// Thunk actions
export const fetchDocuments = () => async (dispatch) => {
  try {
    dispatch(fetchDocumentsStart());
    // In a real app, this would call the API service
    // const response = await documentService.getDocuments();
    
    // Simulate API call for demo
    await new Promise(resolve => setTimeout(resolve, 1000));
    const response = [
      {
        id: '1',
        title: 'Employment Contract',
        description: 'Standard employment agreement',
        file_path: '/documents/employment_contract.pdf',
        file_type: 'pdf',
        status: 'analyzed',
        created_at: new Date().toISOString()
      },
      {
        id: '2',
        title: 'Non-Disclosure Agreement',
        description: 'Confidentiality agreement for project X',
        file_path: '/documents/nda.pdf',
        file_type: 'pdf',
        status: 'uploaded',
        created_at: new Date().toISOString()
      }
    ];
    
    dispatch(fetchDocumentsSuccess(response));
    return response;
  } catch (error) {
    dispatch(fetchDocumentsFailure(error.message));
    throw error;
  }
};

export const uploadDocument = (file, title, description) => async (dispatch) => {
  try {
    dispatch(uploadDocumentStart());
    // In a real app, this would call the API service
    // const response = await documentService.uploadDocument(file, title, description);
    
    // Simulate API call for demo
    await new Promise(resolve => setTimeout(resolve, 1500));
    const response = {
      id: Math.random().toString(36).substring(2, 9),
      title,
      description,
      file_path: `/documents/${file.name}`,
      file_type: file.name.split('.').pop(),
      status: 'uploaded',
      created_at: new Date().toISOString()
    };
    
    dispatch(uploadDocumentSuccess(response));
    return response;
  } catch (error) {
    dispatch(uploadDocumentFailure(error.message));
    throw error;
  }
};

export const analyzeDocument = (documentId, llmModel) => async (dispatch) => {
  try {
    dispatch(analyzeDocumentStart());
    // In a real app, this would call the API service
    // const response = await documentService.analyzeDocument(documentId, llmModel);
    
    // Simulate API call for demo
    await new Promise(resolve => setTimeout(resolve, 2000));
    const response = {
      document_id: documentId,
      summary: "This contract outlines a service agreement between ABC Corp and XYZ Inc for software development services.",
      key_points: [
        "Initial term of 12 months with automatic renewal",
        "Payment terms: Net 30 days",
        "Includes confidentiality and non-compete clauses",
        "Intellectual property rights assigned to client"
      ],
      entities: {
        people: ["John Smith (CEO)", "Jane Doe (CTO)"],
        organizations: ["ABC Corporation", "XYZ Inc"],
        dates: ["January 15, 2025", "December 31, 2025"]
      },
      recommendations: [
        "Review section 3.2 regarding payment terms",
        "Consider adding more specific deliverable timelines",
        "Strengthen the dispute resolution mechanism"
      ],
      llm_model: llmModel
    };
    
    dispatch(analyzeDocumentSuccess(response));
    return response;
  } catch (error) {
    dispatch(analyzeDocumentFailure(error.message));
    throw error;
  }
};

export default documentSlice.reducer;
