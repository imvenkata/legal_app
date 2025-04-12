# Document Upload Fix Guide

This guide helps resolve common issues with document uploads in the Legal AI application.

## Quick Fix Steps

1. Run the created fixes:
   ```
   # Fix OpenAI API compatibility issues
   chmod +x fix_openai.py && python3 fix_openai.py backend
   
   # Restart the backend
   cd backend && source ../venv/bin/activate && python app.py
   ```

2. After the backend is running, open a new terminal and start the frontend:
   ```
   cd frontend && npm start
   ```

3. Access the application at http://localhost:3000

## Common Issues & Solutions

### 1. OpenAI API Compatibility

The error message `openai.ChatCompletion is no longer supported in openai>=1.0.0` indicates an incompatibility with the newer OpenAI API version.

**Solution**: We've created a fix script (`fix_openai.py`) that updates all OpenAI API calls to use the new format:
```
# Before
response = openai.ChatCompletion.create(model="gpt-4", messages=messages)

# After
response = openai.chat.completions.create(model="gpt-4", messages=messages)
```

### 2. Document Upload Failures

If document uploads are failing with a generic error message:

**Potential causes and solutions**:

- **File size too large**: Try uploading a smaller file (<2MB)
- **Authentication issues**: Make sure you're logged in (if required)
- **CORS configuration**: Backend CORS settings must allow your frontend domain
- **Upload directory permissions**: Ensure backend upload directory has correct permissions
- **API endpoint mismatch**: Frontend should call the correct endpoint (/api/documents/upload)

### 3. Frontend API Implementation

We've created improved API services:

- `frontend/src/services/documents.js` with better error handling and logging
- `frontend/src/components/document/DocumentUploader.jsx` with user-friendly error messages

### 4. Debugging Tools

When troubleshooting uploads:

1. Check the browser console (F12) for JavaScript errors
2. Inspect the Network tab to see the actual HTTP request/response
3. Check backend logs for any server-side errors
4. Test API directly using curl:
   ```
   curl -v -F "file=@test_document.txt" -F "title=Test" -F "description=Test" http://localhost:8000/api/documents/upload
   ```

## Advanced Troubleshooting

### User Authentication Issues

If the application requires authentication for uploads:

1. Make sure you're logged in
2. Check localStorage for 'user' and 'token' values
3. Ensure token is being sent in Authorization header

### Missing Dependencies

If backend module errors occur:

```
pip install aiofiles python-multipart
```

### Restarting the Application

Sometimes a full restart resolves issues:

```
# Kill any running servers
pkill -f "python app.py"
pkill -f "npm start"

# Restart backend
cd backend && source ../venv/bin/activate && python app.py

# In a new terminal, restart frontend
cd frontend && npm start
```

## Need More Help?

Check the application logs for detailed error messages or file an issue in the project repository. 