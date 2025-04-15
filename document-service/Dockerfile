FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install necessary tools for file operations
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create uploads directory
RUN mkdir -p /app/uploads

# Copy the rest of the application
COPY . .

# Ensure the uploads directory exists
CMD mkdir -p /app/uploads && uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload 