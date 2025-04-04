import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Import components
import Navigation from './components/common/Navigation';
import { Login, Register } from './components/common/Auth';
import Settings from './components/common/Settings';
import DocumentUploader from './components/document/DocumentUploader';
import LegalResearch from './components/research/LegalResearch';
import ContractDrafter from './components/contract/ContractDrafter';
import { AuthProvider, useAuth } from './components/common/Auth';
import ErrorBoundary from './components/common/ErrorBoundary';
import Loading from './components/common/Loading';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

// Protected route component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <Loading message="Checking authentication..." />;
  }
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  return children;
};

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <Router>
            <Routes>
              {/* Auth routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              {/* Protected routes */}
              <Route path="/" element={
                <ProtectedRoute>
                  <Navigation>
                    <Navigate to="/documents" />
                  </Navigation>
                </ProtectedRoute>
              } />
              
              <Route path="/documents" element={
                <ProtectedRoute>
                  <Navigation>
                    <DocumentUploader />
                  </Navigation>
                </ProtectedRoute>
              } />
              
              <Route path="/research" element={
                <ProtectedRoute>
                  <Navigation>
                    <LegalResearch />
                  </Navigation>
                </ProtectedRoute>
              } />
              
              <Route path="/contracts" element={
                <ProtectedRoute>
                  <Navigation>
                    <ContractDrafter />
                  </Navigation>
                </ProtectedRoute>
              } />
              
              <Route path="/settings" element={
                <ProtectedRoute>
                  <Navigation>
                    <Settings />
                  </Navigation>
                </ProtectedRoute>
              } />
              
              {/* Fallback route */}
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </Router>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
