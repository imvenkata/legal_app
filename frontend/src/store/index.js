import { configureStore } from '@reduxjs/toolkit';
import userReducer from './userSlice';
import documentReducer from './documentSlice';
import researchReducer from './researchSlice';
import contractReducer from './contractSlice';

const store = configureStore({
  reducer: {
    user: userReducer,
    document: documentReducer,
    research: researchReducer,
    contract: contractReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false
    })
});

export default store;
