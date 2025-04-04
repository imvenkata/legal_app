#!/bin/bash

# Add uv to PATH if needed
if ! command -v uv &> /dev/null; then
    echo "uv not found in PATH. Please install it first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "Setting up uv for Python dependency management..."

# Create a virtual environment with uv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating new virtual environment with uv..."
    uv venv
else
    echo "Virtual environment already exists. Continuing..."
fi

# Sync dependencies using uv
echo "Installing dependencies from requirements.txt with uv..."
uv pip sync backend/requirements.txt

echo "Setup complete!"
echo "To use uv for installation:   uv pip install <package>"
echo "To add a dependency:          uv pip add <package>"
echo "To remove a dependency:       uv pip remove <package>"
echo "To update dependencies:       uv pip sync backend/requirements.txt"
echo "To generate requirements.txt: uv pip freeze > backend/requirements.txt" 