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
  Chip,
  Alert
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import HistoryIcon from '@mui/icons-material/History';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import AssessmentIcon from '@mui/icons-material/Assessment';
import { researchAPI } from '../../services/api';
import { 
  setSearchResults, 
  setSelectedCase, 
  setPrediction, 
  addSavedResearch,
  setLoading,
  setError,
  clearError
} from '../../store/researchSlice';
import useLlmModel from '../../hooks/useLlmModel';

const LegalResearchConnected = () => {
  const dispatch = useDispatch();
  const { searchResults, selectedCase, prediction, loading, error } = useSelector(state => state.research);
  const { preferredLlmModel } = useLlmModel();
  
  const [query, setQuery] = useState('');

  const handleSearch = async () => {
    if (!query) {
      dispatch(setError('Please enter a search query'));
      return;
    }
    
    try {
      dispatch(setLoading(true));
      dispatch(setSearchResults([]));
      dispatch(setPrediction(null));
      
      const response = await researchAPI.searchCases(query);
      
      dispatch(setSearchResults(response.data));
      dispatch(setLoading(false));
    } catch (err) {
      dispatch(setError(err.message || 'Failed to search cases'));
      dispatch(setLoading(false));
    }
  };

  const handlePrediction = async () => {
    if (!query) {
      dispatch(setError('Please enter a query for prediction'));
      return;
    }
    
    try {
      dispatch(setLoading(true));
      dispatch(setPrediction(null));
      
      const caseDetails = { query };
      const response = await researchAPI.predictOutcome(caseDetails, preferredLlmModel);
      
      dispatch(setPrediction(response.data));
      dispatch(setLoading(false));
    } catch (err) {
      dispatch(setError(err.message || 'Failed to predict case outcome'));
      dispatch(setLoading(false));
    }
  };

  const handleCaseSelect = async (caseItem) => {
    try {
      dispatch(setLoading(true));
      
      // If we already have detailed case data, just set it
      if (caseItem.fullDetails) {
        dispatch(setSelectedCase(caseItem));
        dispatch(setLoading(false));
        return;
      }
      
      // Otherwise, fetch the full case details
      const response = await researchAPI.getCase(caseItem.id);
      
      // Combine the search result with the full details
      const fullCase = {
        ...caseItem,
        ...response.data,
        fullDetails: true
      };
      
      dispatch(setSelectedCase(fullCase));
      dispatch(setLoading(false));
    } catch (err) {
      dispatch(setError(err.message || 'Failed to get case details'));
      dispatch(setLoading(false));
    }
  };

  const handleSaveCase = async () => {
    if (!selectedCase) return;
    
    try {
      dispatch(setLoading(true));
      
      // Get user ID from localStorage
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id;
      
      if (!userId) {
        throw new Error('User not authenticated');
      }
      
      const researchData = {
        user_id: userId,
        query,
        case_id: selectedCase.id,
        case_title: selectedCase.title,
        notes: ''
      };
      
      const response = await researchAPI.saveResearch(researchData);
      
      dispatch(addSavedResearch(response.data));
      dispatch(setLoading(false));
      
      // Show success message
      alert('Case saved successfully!');
    } catch (err) {
      dispatch(setError(err.message || 'Failed to save case'));
      dispatch(setLoading(false));
    }
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Legal Research & Predictive Analytics
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => dispatch(clearError())}>
          {error}
        </Alert>
      )}
      
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Search Legal Cases
        </Typography>
        
        <TextField
          fullWidth
          label="Enter your legal research query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          margin="normal"
          placeholder="e.g., Breach of contract in software development agreements"
          multiline
          rows={2}
          disabled={loading}
        />
        
        <Box sx={{ display: 'flex', gap: 2, mt: 2, alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mr: 'auto' }}>
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
            startIcon={<SearchIcon />}
            onClick={handleSearch}
            disabled={!query || loading}
          >
            {loading && !prediction ? <CircularProgress size={24} /> : 'Search Cases'}
          </Button>
          
          <Button
            variant="outlined"
            color="secondary"
            startIcon={<AssessmentIcon />}
            onClick={handlePrediction}
            disabled={!query || loading}
          >
            {loading && prediction === null ? <CircularProgress size={24} /> : 'Predict Outcome'}
          </Button>
        </Box>
      </Paper>
      
      <Box sx={{ display: 'flex', gap: 3 }}>
        {/* Search Results */}
        <Box sx={{ flex: 1 }}>
          <Typography variant="h6" gutterBottom>
            Search Results
          </Typography>
          
          {searchResults.length === 0 ? (
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="body1" color="textSecondary">
                {loading && !prediction ? 'Searching...' : 'No results yet. Try searching for legal cases.'}
              </Typography>
            </Paper>
          ) : (
            searchResults.map((result) => (
              <Paper 
                key={result.id} 
                sx={{ 
                  p: 2, 
                  mb: 2, 
                  cursor: 'pointer',
                  borderLeft: selectedCase?.id === result.id ? '4px solid #1976d2' : 'none',
                  '&:hover': { backgroundColor: '#f5f5f5' }
                }}
                onClick={() => handleCaseSelect(result)}
              >
                <Typography variant="subtitle1" fontWeight="bold">
                  {result.title}
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  {result.content}
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Chip 
                    size="small" 
                    label={`Relevance: ${(result.relevance_score * 100).toFixed(0)}%`}
                    color={result.relevance_score > 0.9 ? 'success' : 'primary'}
                  />
                  <Typography variant="caption" color="textSecondary">
                    Source: {result.source}
                  </Typography>
                </Box>
              </Paper>
            ))
          )}
        </Box>
        
        {/* Case Details or Prediction */}
        <Box sx={{ flex: 1 }}>
          {selectedCase ? (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Case Details
              </Typography>
              <Typography variant="subtitle1" fontWeight="bold">
                {selectedCase.title}
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Typography variant="body1" paragraph>
                {selectedCase.content}
              </Typography>
              <Typography variant="body2" paragraph>
                {selectedCase.fullDetails ? selectedCase.full_text || 'No additional details available.' : 'Click to view full case details.'}
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                <Button 
                  startIcon={<BookmarkIcon />} 
                  variant="outlined" 
                  size="small"
                  onClick={handleSaveCase}
                  disabled={loading}
                >
                  Save Case
                </Button>
                <Button 
                  startIcon={<HistoryIcon />} 
                  variant="outlined" 
                  size="small"
                  disabled={loading}
                >
                  View Similar Cases
                </Button>
              </Box>
            </Paper>
          ) : prediction ? (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Outcome Prediction
              </Typography>
              <Box sx={{ 
                p: 2, 
                bgcolor: '#f8f9fa', 
                borderRadius: 1,
                border: '1px solid #e0e0e0',
                mb: 3
              }}>
                <Typography variant="body1" fontWeight="medium">
                  {prediction.prediction}
                </Typography>
              </Box>
              
              <Typography variant="subtitle2" gutterBottom>
                Key Factors
              </Typography>
              {prediction.factors.map((factor, index) => (
                <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Chip 
                    size="small" 
                    label={factor.impact}
                    color={factor.impact === 'high' ? 'error' : factor.impact === 'medium' ? 'warning' : 'info'}
                    sx={{ mr: 1, width: 70 }}
                  />
                  <Typography variant="body2">
                    {factor.name}
                  </Typography>
                </Box>
              ))}
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="subtitle2" gutterBottom>
                Similar Cases
              </Typography>
              {prediction.similar_cases.map((caseItem, index) => (
                <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">
                    {caseItem.case_name}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {(caseItem.similarity * 100).toFixed(0)}% similar
                  </Typography>
                </Box>
              ))}
            </Paper>
          ) : (
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="body1" color="textSecondary">
                Select a case to view details or use the "Predict Outcome" button to get a prediction.
              </Typography>
            </Paper>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default LegalResearchConnected;
