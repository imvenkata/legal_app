# Legal AI App - White Screen Fix Guide

If you're experiencing a white screen in the frontend application, follow these steps to resolve the issue.

## Quick Solutions

We've created multiple solutions to fix the white screen issue:

### Option 1: Use the Static HTML Uploader (Simplest)

1. Open the `static_uploader.html` file directly in your browser:
   - Double-click the file in your file explorer
   - Or run: `open static_uploader.html` (Mac) / `xdg-open static_uploader.html` (Linux)

This bypasses React completely and should work regardless of frontend issues.

### Option 2: Try the Simplified React App

1. Run the fix script: 
   ```
   chmod +x fix_white_screen.sh && ./fix_white_screen.sh
   ```

2. This script will:
   - Create backups of your original files
   - Stop any running React processes
   - Open the static HTML version
   - Fix CORS issues on the backend
   - Start a simplified React app

3. Try accessing http://localhost:3000/upload directly in your browser

### Option 3: Manual Steps

If the scripts don't work, try these manual steps:

1. Make sure the backend is running:
   ```
   cd backend && source ../venv/bin/activate && python app.py
   ```

2. Test the backend API directly:
   ```
   curl -v http://localhost:8000/health
   ```

3. Open the static HTML uploader in your browser

4. If the static uploader works but the React app doesn't, the issue is with your React setup.

## Common Issues & Solutions

### React White Screen

React white screens are usually caused by:

1. **JavaScript Errors**: Check your browser console (F12)
2. **Missing Dependencies**: Try reinstalling node modules with `npm install`
3. **Redux/Router Issues**: Our simplified app removes these dependencies
4. **CORS Problems**: Our fix script updates CORS settings

### Authentication Issues

If the app requires authentication:

1. Check if you're logged in (look for token in localStorage)
2. Try using the manual uploader which doesn't require authentication

### Backend Connectivity

Make sure:

1. Backend is running on port 8000
2. No CORS errors in console
3. Network requests are going to the right endpoint

## Additional Resources

If you continue having issues:

1. Check the terminal output for errors
2. Look at the browser console (F12 > Console)
3. View the network requests (F12 > Network)

## Restoring Your Original Setup

To restore your original configuration:
```
cp backup/index.js.bak frontend/src/index.js
cp backup/App.js.bak frontend/src/App.js
``` 