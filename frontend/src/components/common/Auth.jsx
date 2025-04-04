import React, { useState } from 'react';
import { Box, Typography, Paper, TextField, Button, CircularProgress, Alert } from '@mui/material';
import { styled } from '@mui/material/styles';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import PersonOutlineIcon from '@mui/icons-material/PersonOutline';
import { Link, useNavigate } from 'react-router-dom';

const AuthContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '100vh',
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.default
}));

const AuthPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  maxWidth: 400,
  width: '100%'
}));

const AuthForm = styled('form')(({ theme }) => ({
  width: '100%',
  marginTop: theme.spacing(1)
}));

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    
    if (!email || !password) {
      setError('Please enter both email and password');
      return;
    }
    
    setLoading(true);
    
    // Simulate API call for login
    setTimeout(() => {
      // For demo purposes, accept any login with valid format
      if (email.includes('@') && password.length >= 6) {
        // Store user info in localStorage (in a real app, you'd store a token)
        localStorage.setItem('user', JSON.stringify({
          id: 'user123',
          email,
          name: 'John Doe',
          role: 'attorney'
        }));
        
        // Redirect to dashboard
        navigate('/documents');
      } else {
        setError('Invalid email or password');
      }
      
      setLoading(false);
    }, 1000);
  };

  return (
    <AuthContainer>
      <AuthPaper elevation={3}>
        <Box sx={{ mb: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <LockOutlinedIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
          <Typography component="h1" variant="h5">
            Sign in to Legal AI
          </Typography>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <AuthForm onSubmit={handleSubmit}>
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email Address"
            name="email"
            autoComplete="email"
            autoFocus
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Sign In'}
          </Button>
          
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Link to="/register" style={{ textDecoration: 'none' }}>
              <Typography variant="body2" color="primary">
                Don't have an account? Sign up
              </Typography>
            </Link>
          </Box>
        </AuthForm>
      </AuthPaper>
    </AuthContainer>
  );
};

const Register = () => {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    
    // Validate form
    if (!formData.fullName || !formData.email || !formData.password || !formData.confirmPassword) {
      setError('Please fill in all fields');
      return;
    }
    
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }
    
    setLoading(true);
    
    // Simulate API call for registration
    setTimeout(() => {
      setLoading(false);
      setSuccess(true);
      
      // Redirect to login after 2 seconds
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    }, 1000);
  };

  return (
    <AuthContainer>
      <AuthPaper elevation={3}>
        <Box sx={{ mb: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <PersonOutlineIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
          <Typography component="h1" variant="h5">
            Create an Account
          </Typography>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ width: '100%', mb: 2 }}>
            Registration successful! Redirecting to login...
          </Alert>
        )}
        
        <AuthForm onSubmit={handleSubmit}>
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="fullName"
            label="Full Name"
            name="fullName"
            autoComplete="name"
            autoFocus
            value={formData.fullName}
            onChange={handleChange}
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email Address"
            name="email"
            autoComplete="email"
            value={formData.email}
            onChange={handleChange}
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="new-password"
            value={formData.password}
            onChange={handleChange}
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            name="confirmPassword"
            label="Confirm Password"
            type="password"
            id="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
          />
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading || success}
          >
            {loading ? <CircularProgress size={24} /> : 'Sign Up'}
          </Button>
          
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Link to="/login" style={{ textDecoration: 'none' }}>
              <Typography variant="body2" color="primary">
                Already have an account? Sign in
              </Typography>
            </Link>
          </Box>
        </AuthForm>
      </AuthPaper>
    </AuthContainer>
  );
};

export { Login, Register };
