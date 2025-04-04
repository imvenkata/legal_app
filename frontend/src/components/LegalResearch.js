import React, { useState } from 'react';
import axios from 'axios';
import { 
  Typography, 
  Paper, 
  Button, 
  Box, 
  TextField, 
  CircularProgress,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
  Grid,
  Alert,
  Link
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import SourceIcon from '@mui/icons-material/Source';

function LegalResearch() {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [searchError, setSearchError] = useState(null);

  const handleQueryChange = (event) => {
    setQuery(event.target.value);
    setSearchError(null);
  };

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setIsSearching(true);
    setSearchResults(null);
    setSearchError(null);

    const apiUrl = process.env.REACT_APP_SEARCH_API_URL || 'http://localhost:8001/api/v1';

    try {
      const response = await axios.post(`${apiUrl}/query`, { question: query });
      console.log("RAG API Response:", response.data);
      if (response.data && response.data.answer !== undefined && response.data.citations !== undefined) {
        setSearchResults(response.data);
      } else {
        console.error("Unexpected API response structure:", response.data);
        setSearchError("Received an unexpected response format from the server.");
      }
    } catch (error) {
      console.error("RAG API Error:", error);
      const errorMessage = error.response?.data?.detail || error.message || "Failed to fetch RAG results.";
      setSearchError(`Search failed: ${errorMessage}`);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Legal Research (RAG Search)
      </Typography>
      <Typography variant="body1" paragraph>
        Ask questions about your indexed legal documents and get cited answers.
      </Typography>
      
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Ask a Legal Question
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <TextField
            fullWidth
            label="Enter your question"
            variant="outlined"
            value={query}
            onChange={handleQueryChange}
            sx={{ mr: 2 }}
          />
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleSearch}
            disabled={!query.trim() || isSearching}
            startIcon={isSearching ? <CircularProgress size={20} /> : <SearchIcon />}
          >
            Ask
          </Button>
        </Box>
      </Paper>
      
      {isSearching && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {searchError && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {searchError}
        </Alert>
      )}

      {searchResults && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card elevation={3}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Generated Answer
                </Typography>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {searchResults.answer}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          {searchResults.citations && searchResults.citations.length > 0 && (
            <Grid item xs={12}>
              <Card elevation={3}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Cited Sources
                  </Typography>
                  <List>
                    {searchResults.citations.map((citation) => (
                      <React.Fragment key={citation.id}>
                        <ListItem alignItems="flex-start">
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <SourceIcon sx={{ mr: 1, color: 'text.secondary' }} />
                                <Typography variant="body1" component="span" sx={{ fontWeight: 'medium' }}>
                                  Source:{" "}
                                  {citation.file_url ? (
                                    <Link href={citation.file_url} target="_blank" rel="noopener noreferrer">
                                      {citation.source}
                                    </Link>
                                  ) : (
                                    citation.source
                                  )}
                                </Typography>
                                <Chip
                                  label={`Score: ${citation.score.toFixed(3)}`}
                                  size="small"
                                  color="primary"
                                  variant="outlined"
                                  sx={{ ml: 2 }}
                                />
                              </Box>
                            }
                            secondary={
                              <Typography variant="body2" color="text.secondary" sx={{ pl: 4 }}>
                                {citation.text}
                              </Typography>
                            }
                          />
                        </ListItem>
                        <Divider component="li" />
                      </React.Fragment>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      )}
    </Box>
  );
}

export default LegalResearch;
