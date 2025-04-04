import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  user: null,
  isAuthenticated: false,
  loading: false,
  error: null,
  settings: {
    llmProvider: 'openai',
    llmModel: 'gpt-4',
    apiKey: ''
  }
};

export const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    loginStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    loginSuccess: (state, action) => {
      state.loading = false;
      state.user = action.payload.user;
      state.isAuthenticated = true;
    },
    loginFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
    },
    registerStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    registerSuccess: (state) => {
      state.loading = false;
    },
    registerFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    updateSettingsStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    updateSettingsSuccess: (state, action) => {
      state.loading = false;
      state.settings = action.payload;
    },
    updateSettingsFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    }
  }
});

export const { 
  loginStart, 
  loginSuccess, 
  loginFailure, 
  logout, 
  registerStart, 
  registerSuccess, 
  registerFailure,
  updateSettingsStart,
  updateSettingsSuccess,
  updateSettingsFailure,
  clearError
} = userSlice.actions;

// Thunk actions
export const login = (email, password) => async (dispatch) => {
  try {
    dispatch(loginStart());
    const response = await fetch('http://localhost:8000/auth/login', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    dispatch(loginSuccess(data));
    return data;
  } catch (error) {
    dispatch(loginFailure(error.message));
    throw error;
  }
};

export const register = (name, email, password) => async (dispatch) => {
  try {
    dispatch(registerStart());
    const response = await fetch('http://localhost:8000/auth/register', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, email, password }),
    });

    if (!response.ok) {
      throw new Error('Registration failed');
    }

    dispatch(registerSuccess());
  } catch (error) {
    dispatch(registerFailure(error.message));
    throw error;
  }
};

export const updateSettings = (settings) => async (dispatch) => {
  try {
    dispatch(updateSettingsStart());
    const response = await fetch('http://localhost:8000/auth/settings', {
      method: 'PUT',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(settings),
    });

    if (!response.ok) {
      throw new Error('Failed to update settings');
    }

    const data = await response.json();
    dispatch(updateSettingsSuccess(data));
  } catch (error) {
    dispatch(updateSettingsFailure(error.message));
    throw error;
  }
};

export default userSlice.reducer;
