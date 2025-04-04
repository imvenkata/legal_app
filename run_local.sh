#!/bin/bash

# Script to run the backend and frontend services for local testing

echo "Starting Legal AI Application for local testing..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
  echo "uv is not installed. Please install it first:"
  echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo "Creating virtual environment with uv..."
  uv venv
else
  echo "Virtual environment exists, activating..."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies with uv..."
uv pip install -r backend/requirements.txt

# Run the backend service in the background
echo "Starting backend service..."
cd backend
python3 app.py &
BACKEND_PID=$!
cd ..

echo "Backend service started with PID: $BACKEND_PID"
echo "Backend API available at: http://localhost:8000"

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Test backend health endpoint
echo "Testing backend health endpoint..."
curl -s http://localhost:8000/health

echo -e "\n\nBackend is running. You can test the API endpoints using curl or a tool like Postman."
echo "Example endpoints:"
echo "- GET http://localhost:8000/health"
echo "- POST http://localhost:8000/auth/login"
echo "- GET http://localhost:8000/documents"
echo "- POST http://localhost:8000/research/search"
echo "- GET http://localhost:8000/contracts/templates"

echo -e "\nPress Ctrl+C to stop the services"

# Keep the script running
wait $BACKEND_PID
