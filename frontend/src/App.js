import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, Container } from '@mui/material';
import { useSelector } from 'react-redux';

// Components
import Navigation from './components/Navigation';
import DocumentAnalysis from './components/DocumentAnalysis';
import LegalResearch from './components/LegalResearch';
import ContractGeneration from './components/ContractGeneration';
import Settings from './components/Settings';
import Login from './components/Login';

function App() {
  const { isAuthenticated } = useSelector((state) => state.user);

  return (
    <Box sx={{ display: 'flex' }}>
      <Navigation />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          height: '100vh',
          overflow: 'auto',
          pt: 8, // Add padding for the app bar
        }}
      >
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Routes>
            <Route
              path="/"
              element={
                isAuthenticated ? (
                  <Navigate to="/documents" />
                ) : (
                  <Navigate to="/login" />
                )
              }
            />
            <Route path="/login" element={<Login />} />
            <Route path="/documents" element={<DocumentAnalysis />} />
            <Route path="/research" element={<LegalResearch />} />
            <Route path="/contracts" element={<ContractGeneration />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Container>
      </Box>
    </Box>
  );
}

export default App;
