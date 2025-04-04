import React, { useState } from 'react';
import { Box, Typography, Paper, TextField, Button, CircularProgress, Divider, Chip } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import HistoryIcon from '@mui/icons-material/History';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import AssessmentIcon from '@mui/icons-material/Assessment';
import LegalSearchVector from '../Search/LegalSearch';

const LegalResearch = () => {
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [predicting, setPredicting] = useState(false);
  const [selectedCase, setSelectedCase] = useState(null);

  const handleSearch = () => {
    if (!query) return;
    
    setSearching(true);
    setResults([]);
    
    // Simulate API call
    setTimeout(() => {
      const mockResults = [
        {
          id: '1',
          title: 'Smith v. Johnson (2022)',
          content: 'This case established the precedent for contractual obligations in remote work arrangements.',
          relevance_score: 0.95,
          source: 'Supreme Court',
          url: 'https://example.com/cases/smith-v-johnson'
        },
        {
          id: '2',
          title: 'Davis Corp v. Miller Inc. (2021)',
          content: 'Landmark case regarding intellectual property rights in software development contracts.',
          relevance_score: 0.87,
          source: 'Federal Circuit',
          url: 'https://example.com/cases/davis-v-miller'
        },
        {
          id: '3',
          title: 'Thompson v. City of Springfield (2020)',
          content: 'Case involving municipal liability for contractual breaches with private contractors.',
          relevance_score: 0.82,
          source: 'State Supreme Court',
          url: 'https://example.com/cases/thompson-v-springfield'
        },
        {
          id: '4',
          title: 'Wilson Enterprises v. Global Solutions (2019)',
          content: 'International contract dispute establishing jurisdiction for cross-border service agreements.',
          relevance_score: 0.78,
          source: 'International Court of Commerce',
          url: 'https://example.com/cases/wilson-v-global'
        },
      ];
      
      setResults(mockResults);
      setSearching(false);
    }, 1500);
  };

  const handlePrediction = () => {
    if (!query) return;
    
    setPredicting(true);
    setPrediction(null);
    
    // Simulate API call
    setTimeout(() => {
      const mockPrediction = {
        prediction: 'Based on similar precedents, the plaintiff is likely to prevail (75% probability).',
        confidence: 0.75,
        factors: [
          { name: 'Clear contractual language', impact: 'high' },
          { name: 'Established precedent in similar cases', impact: 'high' },
          { name: 'Documented breach of terms', impact: 'medium' },
          { name: 'Mitigating circumstances', impact: 'low' }
        ],
        similar_cases: [
          { case_name: 'Smith v. Johnson (2022)', similarity: 0.85 },
          { case_name: 'Davis Corp v. Miller Inc. (2021)', similarity: 0.72 }
        ]
      };
      
      setPrediction(mockPrediction);
      setPredicting(false);
    }, 2000);
  };

  const handleCaseSelect = (caseItem) => {
    setSelectedCase(caseItem);
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Legal Research & Predictive Analytics
      </Typography>
      
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
        />
        
        <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<SearchIcon />}
            onClick={handleSearch}
            disabled={!query || searching}
          >
            {searching ? <CircularProgress size={24} /> : 'Search Cases'}
          </Button>
          
          <Button
            variant="outlined"
            color="secondary"
            startIcon={<AssessmentIcon />}
            onClick={handlePrediction}
            disabled={!query || predicting}
          >
            {predicting ? <CircularProgress size={24} /> : 'Predict Outcome'}
          </Button>
        </Box>
      </Paper>
      
      <Box sx={{ display: 'flex', gap: 3 }}>
        {/* Search Results */}
        <Box sx={{ flex: 1 }}>
          <Typography variant="h6" gutterBottom>
            Search Results
          </Typography>
          
          {results.length === 0 ? (
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="body1" color="textSecondary">
                {searching ? 'Searching...' : 'No results yet. Try searching for legal cases.'}
              </Typography>
            </Paper>
          ) : (
            results.map((result) => (
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
                This is a placeholder for more detailed case information that would be retrieved from the API in a real implementation. This would include the full text of the case, legal reasoning, and citations.
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                <Button startIcon={<BookmarkIcon />} variant="outlined" size="small">
                  Save Case
                </Button>
                <Button startIcon={<HistoryIcon />} variant="outlined" size="small">
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
      
      <LegalSearchVector />
    </Box>
  );
};

export default LegalResearch;
