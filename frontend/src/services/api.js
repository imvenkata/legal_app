import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';
const SEARCH_API_BASE_URL = process.env.REACT_APP_SEARCH_API_URL || 'http://localhost:8001/api/v1';

export const api = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
});

// Request interceptor for auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Error handling interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized errors
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Create organized API services
export const authAPI = {
  login: (credentials) => api.post('/api/users/login', credentials),
  register: (userData) => api.post('/api/users/register', userData),
  getProfile: () => api.get('/api/users/me'),
  updateProfile: (data) => api.put('/api/users/me', data),
};

export const documentsAPI = {
  upload: (formData) => api.post('/api/documents/upload', formData),
  getAll: () => api.get('/api/documents'),
  getById: (id) => api.get(`/api/documents/${id}`),
  analyze: (id, data) => api.post(`/api/documents/${id}/analyze`, data),
  chat: (id, data) => api.post(`/api/documents/${id}/chat`, data),
  getChatHistory: (id) => api.get(`/api/documents/${id}/chat_history`),
};

export const contractsAPI = {
  generate: (data) => api.post('/api/contracts/generate', data),
  getTemplates: () => api.get('/api/contracts/templates'),
};

export const chatAPI = {
  sendMessage: (data) => api.post('/api/chat', data),
  getHistory: () => api.get('/api/chat/history'),
};

// --- Search Service API --- 

// Create a separate axios instance for the search service
const searchApiClient = axios.create({
  baseURL: SEARCH_API_BASE_URL,
});

// Optional: Add interceptors specific to search service if needed later
// searchApiClient.interceptors.request.use(...);
// searchApiClient.interceptors.response.use(...);

export const searchAPI = {
  /**
   * Performs semantic search for legal documents.
   * @param {object} data - The search query and parameters.
   * @param {string} data.query - The search text.
   * @param {number} [data.top_k=5] - The number of results to return.
   * @returns {Promise<object>} - A promise that resolves to the search results { results: [...] }.
   */
  searchLegalDocs: (data) => searchApiClient.post('/search', data),

  /**
   * Asks a legal question using RAG.
   * @param {object} data - The RAG query data.
   * @param {string} data.question - The legal question.
   * @param {number} [data.top_k_retrieval=3] - Number of chunks to retrieve.
   * @returns {Promise<object>} - Promise resolving to { answer: "...", citations: [...] }.
   */
  askLegalQuestion: (data) => searchApiClient.post('/query', data),

  /**
   * Uploads legal documents for ingestion.
   * @param {FormData} formData - The FormData object containing the files.
   * @returns {Promise<object>} - Promise resolving to { message: "...", filenames: [...] }.
   */
  uploadLegalDocs: (formData) => searchApiClient.post('/documents/upload', formData, {
    // Important: Set Content-Type header for file uploads
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    // Optional: Add progress tracking later
    // onUploadProgress: progressEvent => { ... }
  }),
};
