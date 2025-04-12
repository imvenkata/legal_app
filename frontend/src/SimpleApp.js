import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import SimpleUploader from './components/document/SimpleUploader';

// Very simple app with minimal dependencies
function SimpleApp() {
  return (
    <BrowserRouter>
      <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
        <header style={{ marginBottom: '20px' }}>
          <h1>Legal AI App - Simple Mode</h1>
          <nav>
            <Link to="/" style={{ marginRight: '10px' }}>Home</Link>
            <Link to="/upload" style={{ marginRight: '10px' }}>Document Upload</Link>
          </nav>
        </header>
        
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/upload" element={<SimpleUploader />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

// Simple homepage component
function HomePage() {
  return (
    <div>
      <h2>Welcome to Legal AI App</h2>
      <p>This is a simplified version to diagnose frontend issues.</p>
      <p>
        <Link to="/upload">
          <button style={{ padding: '10px', background: '#3f51b5', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Go to Upload Page
          </button>
        </Link>
      </p>
    </div>
  );
}

export default SimpleApp; 