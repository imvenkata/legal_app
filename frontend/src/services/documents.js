import axios from 'axios';

// Get the API URL from environment variables or use default
const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

console.log('Document API Base URL:', BASE_URL);

// Create a dedicated API client for document operations
const documentClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000, // Longer timeout for uploads (30 seconds)
  headers: {
    'Content-Type': 'multipart/form-data',
  },
  withCredentials: false // Disable sending cookies for cross-origin requests
});

// Add request interceptor for auth token
documentClient.interceptors.request.use(
  (config) => {
    console.log('Document API request config:', config.url);
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Document API request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
documentClient.interceptors.response.use(
  (response) => {
    console.log('Document API response:', response.status);
    return response;
  },
  (error) => {
    console.error('Document API error:', error);
    if (error.response) {
      // Server responded with error status
      const errorMessage = error.response.data?.detail || 
                          error.response.data?.message || 
                          `Server error: ${error.response.status}`;
      console.error('Server response error:', errorMessage);
      return Promise.reject(new Error(errorMessage));
    } else if (error.request) {
      // Request was made but no response
      console.error('No response received:', error.request);
      return Promise.reject(new Error('No response from server. Please try again.'));
    } else {
      // Something else happened
      console.error('Unknown error:', error.message);
      return Promise.reject(error);
    }
  }
);

export const documentAPI = {
  /**
   * Upload a document
   * @param {FormData} formData - FormData containing file, title, etc.
   * @returns {Promise<object>} - Document data
   */
  uploadDocument: async (formData) => {
    try {
      // Check if formData contains the required fields
      if (!formData.get('file') || !formData.get('title')) {
        throw new Error('Missing required fields: file and title');
      }

      // Ensure user is authenticated if needed
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (!formData.get('user_id') && user.id) {
        formData.append('user_id', user.id);
      }

      console.log('Uploading document:', formData.get('title'));

      // Log file details
      const file = formData.get('file');
      console.log('File details:', { 
        name: file.name, 
        size: `${(file.size / 1024).toFixed(2)} KB`, 
        type: file.type
      });

      // Make the upload request with proper error handling
      console.log('Sending upload request to:', `${BASE_URL}/api/documents/upload`);
      const response = await documentClient.post('/api/documents/upload', formData);
      
      console.log('Upload successful:', response.data);
      return response;
    } catch (error) {
      console.error('Document upload failed:', error);
      throw error;
    }
  },

  /**
   * Get all documents
   * @returns {Promise<object>} - List of documents
   */
  getDocuments: async (userId) => {
    return documentClient.get('/api/documents', { params: { userId } });
  },

  /**
   * Get a document by ID
   * @param {string} id - Document ID
   * @returns {Promise<object>} - Document data
   */
  getDocument: async (id) => {
    return documentClient.get(`/api/documents/${id}`);
  },

  /**
   * Analyze a document
   * @param {string} id - Document ID
   * @param {string} model - Model to use for analysis
   * @returns {Promise<object>} - Analysis result
   */
  analyzeDocument: async (id, model = 'default') => {
    return documentClient.post(`/api/documents/${id}/analyze`, { model });
  },

  /**
   * Delete a document
   * @param {string} id - Document ID
   * @returns {Promise<void>}
   */
  deleteDocument: async (id) => {
    return documentClient.delete(`/api/documents/${id}`);
  }
}; 