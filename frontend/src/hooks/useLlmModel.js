import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setPreferredLlmModel, setAvailableLlmModels } from '../store/userSlice';
import { settingsAPI } from '../services/api';

// Custom hook for LLM model integration
export const useLlmModel = () => {
  const dispatch = useDispatch();
  const { settings, availableLlmModels } = useSelector(state => state.user);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Get the current preferred LLM model
  const preferredLlmModel = settings.preferredLlmModel;

  // Function to change the preferred LLM model
  const changeLlmModel = async (modelId) => {
    try {
      setLoading(true);
      setError(null);
      
      // Get user ID from localStorage
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id;
      
      if (!userId) {
        throw new Error('User not authenticated');
      }
      
      // Call API to update preferred LLM model
      await settingsAPI.setLlmModel(userId, modelId);
      
      // Update Redux store
      dispatch(setPreferredLlmModel(modelId));
      
      setLoading(false);
      return true;
    } catch (err) {
      setError(err.message || 'Failed to change LLM model');
      setLoading(false);
      return false;
    }
  };

  // Function to fetch available LLM models
  const fetchAvailableLlmModels = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Call API to get available LLM models
      const response = await settingsAPI.getLlmModels();
      
      // Update Redux store
      dispatch(setAvailableLlmModels(response.data));
      
      setLoading(false);
      return response.data;
    } catch (err) {
      setError(err.message || 'Failed to fetch available LLM models');
      setLoading(false);
      return [];
    }
  };

  // Return the hook values and functions
  return {
    preferredLlmModel,
    availableLlmModels,
    changeLlmModel,
    fetchAvailableLlmModels,
    loading,
    error
  };
};

// LLM Model Provider component for easy access throughout the app
export const LlmModelProvider = ({ children }) => {
  const { fetchAvailableLlmModels } = useLlmModel();
  
  useEffect(() => {
    // Fetch available LLM models when the app loads
    fetchAvailableLlmModels();
  }, [fetchAvailableLlmModels]);
  
  return <>{children}</>;
};

export default useLlmModel;
