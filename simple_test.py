#!/usr/bin/env python3
"""
Simple test script to check server connection
"""

import requests
import sys
import os

print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")

# Try basic health check
try:
    print("\nChecking server health at http://localhost:8080/health")
    response = requests.get("http://localhost:8080/health", timeout=5)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")
except Exception as e:
    print(f"Error connecting to server: {str(e)}")
    print(f"Type of error: {type(e)}")

# Try a simple GET to the root endpoint
try:
    print("\nChecking root endpoint at http://localhost:8080/")
    response = requests.get("http://localhost:8080/", timeout=5)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")
except Exception as e:
    print(f"Error connecting to server: {str(e)}")
    print(f"Type of error: {type(e)}")

# Try a GET to the documents endpoint with auth
try:
    print("\nChecking documents endpoint at http://localhost:8080/api/documents/")
    mock_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwibmFtZSI6IlRlc3QgVXNlciIsImV4cCI6MTY5MTI0NTgwMH0.mock_signature"
    response = requests.get(
        "http://localhost:8080/api/documents/", 
        headers={"Authorization": f"Bearer {mock_token}"},
        timeout=5
    )
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")
except Exception as e:
    print(f"Error connecting to server: {str(e)}")
    print(f"Type of error: {type(e)}") 