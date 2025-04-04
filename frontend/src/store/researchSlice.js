import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
// Import the actual API service function
import { searchAPI } from '../services/api'; 

const initialState = {
  searchQuery: '',
  searchResults: [],
  selectedCase: null,
  prediction: null,
  loading: false,
  error: null,

  // New state for legal document vector search
  legalDocQuery: '', 
  legalDocResults: [],
  legalDocLoading: false,
  legalDocError: null,

  // New state for RAG results
  ragQuestion: '',
  ragAnswer: '',
  ragCitations: [],
  ragLoading: false,
  ragError: null,
};

// --- New Async Thunk for Legal Doc Search --- 
export const fetchLegalDocResults = createAsyncThunk(
  'research/fetchLegalDocs',
  async (searchData, { rejectWithValue }) => {
    // searchData should be an object like { query: "...", top_k: 5 }
    try {
      const response = await searchAPI.searchLegalDocs(searchData);
      // Assuming the API returns { results: [...] } structure matching SearchResponse schema
      return response.data.results; 
    } catch (error) {
      console.error("Error fetching legal doc results:", error);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to fetch search results';
      return rejectWithValue(errorMsg);
    }
  }
);

// --- New Async Thunk for RAG Query --- 
export const fetchRagAnswer = createAsyncThunk(
  'research/fetchRagAnswer',
  async (ragData, { rejectWithValue }) => {
    // ragData should be { question: "...", top_k_retrieval: 3 }
    try {
      const response = await searchAPI.askLegalQuestion(ragData);
      // API returns { answer: "...", citations: [...] }
      return response.data; 
    } catch (error) {
      console.error("Error fetching RAG answer:", error);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to fetch RAG answer';
      return rejectWithValue(errorMsg);
    }
  }
);

export const researchSlice = createSlice({
  name: 'research',
  initialState,
  reducers: {
    searchCasesStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    searchCasesSuccess: (state, action) => {
      state.loading = false;
      state.searchResults = action.payload;
    },
    searchCasesFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    predictOutcomeStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    predictOutcomeSuccess: (state, action) => {
      state.loading = false;
      state.prediction = action.payload;
    },
    predictOutcomeFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    setSearchQuery: (state, action) => {
      state.searchQuery = action.payload;
    },
    setSelectedCase: (state, action) => {
      state.selectedCase = action.payload;
    },
    clearPrediction: (state) => {
      state.prediction = null;
    },
    clearError: (state) => {
      state.error = null;
      state.legalDocError = null; // Also clear new error state
    },

    // New reducer to set the specific query for legal docs
    setLegalDocQuery: (state, action) => {
      state.legalDocQuery = action.payload;
    },
    clearLegalDocResults: (state) => {
        state.legalDocResults = [];
        state.legalDocQuery = '';
        state.legalDocError = null;
        // Also clear RAG state when clearing
        state.ragQuestion = '';
        state.ragAnswer = '';
        state.ragCitations = [];
        state.ragError = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Handle fetchLegalDocResults lifecycle
      .addCase(fetchLegalDocResults.pending, (state) => {
        state.legalDocLoading = true;
        state.legalDocError = null;
      })
      .addCase(fetchLegalDocResults.fulfilled, (state, action) => {
        state.legalDocLoading = false;
        state.legalDocResults = action.payload; 
        state.legalDocQuery = action.meta.arg.query; // Store the query that produced results
      })
      .addCase(fetchLegalDocResults.rejected, (state, action) => {
        state.legalDocLoading = false;
        state.legalDocError = action.payload; // Error message from rejectWithValue
        state.legalDocResults = []; // Clear results on error
      })
      // Handle fetchRagAnswer lifecycle
      .addCase(fetchRagAnswer.pending, (state, action) => {
        state.ragLoading = true;
        state.ragError = null;
        state.ragQuestion = action.meta.arg.question; // Store question being asked
        state.ragAnswer = ''; // Clear previous answer
        state.ragCitations = []; // Clear previous citations
      })
      .addCase(fetchRagAnswer.fulfilled, (state, action) => {
        state.ragLoading = false;
        state.ragAnswer = action.payload.answer;
        state.ragCitations = action.payload.citations;
      })
      .addCase(fetchRagAnswer.rejected, (state, action) => {
        state.ragLoading = false;
        state.ragError = action.payload; 
        state.ragAnswer = ''; // Clear answer on error
        state.ragCitations = [];
      });
  }
});

export const {
  searchCasesStart,
  searchCasesSuccess,
  searchCasesFailure,
  predictOutcomeStart,
  predictOutcomeSuccess,
  predictOutcomeFailure,
  setSearchQuery,
  setSelectedCase,
  clearPrediction,
  clearError,
  setLegalDocQuery,
  clearLegalDocResults
} = researchSlice.actions;

// Thunk actions
export const searchCases = (query, filters) => async (dispatch) => {
  try {
    dispatch(searchCasesStart());
    dispatch(setSearchQuery(query));
    
    // In a real app, this would call the API service
    // const response = await researchService.searchCases(query, filters);
    
    // Simulate API call for demo
    await new Promise(resolve => setTimeout(resolve, 1500));
    const response = [
      {
        id: '1',
        title: 'Smith v. Jones (2023)',
        content: 'The court ruled in favor of the plaintiff, finding that the defendant had breached the contract by failing to deliver the goods on time.',
        source: 'Supreme Court',
        relevance_score: 0.95
      },
      {
        id: '2',
        title: 'Wilson Corp v. Allen Inc (2022)',
        content: 'The court found that the non-compete clause was overly broad and therefore unenforceable under state law.',
        source: 'Court of Appeals',
        relevance_score: 0.87
      },
      {
        id: '3',
        title: 'Parker LLC v. Thompson (2021)',
        content: 'The court held that the defendant was not liable for damages as the force majeure clause in the contract covered the circumstances in question.',
        source: 'District Court',
        relevance_score: 0.82
      }
    ];
    
    dispatch(searchCasesSuccess(response));
    return response;
  } catch (error) {
    dispatch(searchCasesFailure(error.message));
    throw error;
  }
};

export const predictOutcome = (caseDetails, llmModel) => async (dispatch) => {
  try {
    dispatch(predictOutcomeStart());
    
    // In a real app, this would call the API service
    // const response = await researchService.predictOutcome(caseDetails, llmModel);
    
    // Simulate API call for demo
    await new Promise(resolve => setTimeout(resolve, 2000));
    const response = {
      prediction: "Based on the provided information and similar cases, the court is likely to rule in favor of the plaintiff.",
      confidence: 0.78,
      factors: [
        { name: "Precedent in similar cases", impact: "high" },
        { name: "Strength of evidence", impact: "medium" },
        { name: "Applicable statutes", impact: "medium" },
        { name: "Jurisdiction tendencies", impact: "low" }
      ],
      similar_cases: [
        { case_name: "Smith v. Jones (2023)", similarity: 0.85 },
        { case_name: "Wilson Corp v. Allen Inc (2022)", similarity: 0.72 },
        { case_name: "Parker LLC v. Thompson (2021)", similarity: 0.68 }
      ],
      llm_model: llmModel
    };
    
    dispatch(predictOutcomeSuccess(response));
    return response;
  } catch (error) {
    dispatch(predictOutcomeFailure(error.message));
    throw error;
  }
};

export default researchSlice.reducer;
