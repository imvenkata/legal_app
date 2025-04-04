import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { 
    Box, 
    TextField, 
    Button, 
    CircularProgress, 
    List, 
    ListItem, 
    ListItemText, 
    Typography, 
    Paper, 
    Alert,
    IconButton,
    Tooltip,
    Divider,
    Card,
    CardContent,
    CardHeader,
    Chip
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import SourceIcon from '@mui/icons-material/Source';
import { fetchRagAnswer, clearLegalDocResults } from '../../store/researchSlice';

const LegalSearch = () => {
    const [query, setQuery] = useState('');
    const dispatch = useDispatch();
    const { 
        ragQuestion, 
        ragAnswer, 
        ragCitations, 
        ragLoading, 
        ragError 
    } = useSelector((state) => state.research);

    const handleSearch = (e) => {
        e.preventDefault();
        if (!query.trim()) return;
        dispatch(fetchRagAnswer({ question: query, top_k_retrieval: 3 }));
    };

    const handleClear = () => {
        setQuery('');
        dispatch(clearLegalDocResults());
    };

    return (
        <Paper elevation={2} sx={{ p: 3, mt: 2 }}>
            <Typography variant="h6" gutterBottom>
                Ask a Legal Question (RAG)
            </Typography>
            <Box component="form" onSubmit={handleSearch} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <TextField
                    fullWidth
                    variant="outlined"
                    label="Ask a question about your documents..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    size="small"
                />
                <Button 
                    type="submit" 
                    variant="contained" 
                    disabled={ragLoading || !query.trim()}
                    startIcon={<SearchIcon />}
                    sx={{ minWidth: '100px' }}
                >
                    {ragLoading ? <CircularProgress size={24} color="inherit" /> : 'Ask'}
                </Button>
                {(ragQuestion || ragAnswer || ragError) && (
                     <Tooltip title="Clear Question and Answer">
                        <IconButton onClick={handleClear} size="small">
                            <ClearIcon />
                        </IconButton>
                    </Tooltip>
                )}
            </Box>

            {ragError && (
                <Alert severity="error" sx={{ mb: 2 }}>{ragError}</Alert>
            )}

            {ragAnswer && !ragLoading && (
                <Card variant="outlined" sx={{ mt: 2 }}>
                    <CardHeader 
                        avatar={<QuestionAnswerIcon color="primary" />} 
                        title={`Answer to: "${ragQuestion}"`} 
                        titleTypographyProps={{ variant: 'subtitle1' }}
                    />
                    <CardContent>
                        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', mb: 3 }}>
                            {ragAnswer}
                        </Typography>
                        
                        {ragCitations.length > 0 && (
                            <Box>
                                <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                    <SourceIcon fontSize="small" /> Sources Consulted:
                                </Typography>
                                <List dense disablePadding>
                                    {ragCitations.map((citation, index) => (
                                        <ListItem key={index} disableGutters>
                                            <ListItemText 
                                                primary={citation.source}
                                                secondary={citation.text_snippet} 
                                                secondaryTypographyProps={{ variant: 'caption', color: 'text.secondary'}}
                                            />
                                        </ListItem>
                                    ))}
                                </List>
                            </Box>
                        )}
                    </CardContent>
                </Card>
            )}
        </Paper>
    );
};

export default LegalSearch; 