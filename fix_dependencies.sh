#!/bin/bash

echo "Fixing Legal AI Application dependencies..."

# Activate the virtual environment
source venv/bin/activate

# Uninstall problematic packages
pip uninstall -y transformers tokenizers torch

# Install specific versions that work together
pip install torch==2.0.1
pip install tokenizers==0.15.0
pip install transformers==4.35.0
pip install accelerate==0.23.0

echo "Dependencies fixed, starting the application..."

# Run the backend service
cd backend
python3 app.py 