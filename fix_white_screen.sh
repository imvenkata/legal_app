#!/bin/bash

echo "====================================="
echo "  Legal AI App White Screen Fix"
echo "====================================="

# Create backup of original files
mkdir -p backup
echo "Creating backups of original files..."
[ -f frontend/src/index.js ] && cp frontend/src/index.js backup/index.js.bak
[ -f frontend/src/App.js ] && cp frontend/src/App.js backup/App.js.bak

# Stop any running processes
echo "Stopping any running React processes..."
pkill -f "npm start" || echo "No React processes running"

# Step 1: Try opening the static HTML version
echo "Step 1: Opening static HTML version that bypasses React..."
open static_uploader.html || xdg-open static_uploader.html || echo "Please open static_uploader.html manually in your browser"

# Step 2: Fix potential CORS issues
echo "Step 2: Starting backend with CORS debugging..."
cd backend && python -c "
import os
from app import app
from fastapi.middleware.cors import CORSMiddleware

# Remove any existing CORS middleware
app.middleware_stack.middlewares = [m for m in app.middleware_stack.middlewares if not isinstance(m, CORSMiddleware)]

# Add new CORS middleware with explicit settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Print CORS settings
print('CORS middleware reconfigured to allow all origins for testing')
" > cors_fix.py

# Start backend in a separate terminal
gnome-terminal -- bash -c "cd backend && source ../venv/bin/activate && python app.py" || 
    osascript -e 'tell app "Terminal" to do script "cd '$PWD'/backend && source ../venv/bin/activate && python app.py"' || 
    echo "Please start the backend manually: cd backend && source ../venv/bin/activate && python app.py"

echo "Step 3: Starting simplified React app..."
cd frontend && BROWSER=none npm start

echo "If the application still shows a white screen, try accessing http://localhost:3000/upload directly in your browser"
echo "You can also use the static HTML version by opening static_uploader.html in your browser" 