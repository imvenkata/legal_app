#!/bin/bash

echo "Fixing frontend rendering issues..."

# Kill any existing npm start processes
echo "Stopping existing React processes..."
pkill -f "npm start" || echo "No React processes running"

# Clear npm cache
echo "Clearing npm cache..."
cd frontend
npm cache clean --force

# Install any missing dependencies
echo "Checking for missing dependencies..."
npm install --legacy-peer-deps

# Start the app in development mode with debugging
echo "Starting React in debug mode..."
BROWSER=none npm start 