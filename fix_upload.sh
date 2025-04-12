#!/bin/bash

echo "Diagnosing document upload issues..."

# Ensure upload directory exists with the correct permissions
mkdir -p backend/uploads
chmod 755 backend/uploads

# Check backend is running on the correct port
echo "Checking backend health..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
echo "Backend health response: $HEALTH_RESPONSE"

# Test document upload with a sample file
echo "Testing document upload API..."
echo "This is a test document content" > test_upload.txt
UPLOAD_RESPONSE=$(curl -s -F "file=@test_upload.txt" -F "title=Test Document" -F "description=Testing upload fix" http://localhost:8000/api/documents/upload)
echo "Upload API response: $UPLOAD_RESPONSE"

# Check frontend environment
echo "Checking frontend environment..."
cd frontend
cat .env

# Check relevant code sections
echo "Checking document uploader code..."
grep -n "upload" src/components/document/DocumentUploaderConnected.jsx | head -10

echo -e "\n=== Diagnostics Complete ===\n"
echo "If you're still encountering issues, try:"
echo "1. Make sure the backend is running on port 8000"
echo "2. Make sure CORS is properly configured"
echo "3. Try using a smaller document file (<2MB)"
echo "4. Check browser developer console for any errors"
echo "5. Make sure user authentication is working properly" 