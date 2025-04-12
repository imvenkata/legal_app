#!/usr/bin/env python3
"""
Fix OpenAI API compatibility issues in the backend.
This updates code to work with the new OpenAI API (v1.0.0+)
"""

import re
import os
import sys
from pathlib import Path

def find_python_files(directory):
    """Find all Python files in a directory recursively."""
    return list(Path(directory).glob('**/*.py'))

def fix_openai_imports(file_path):
    """Fix OpenAI imports and API calls in a file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if file uses OpenAI
    if 'openai' not in content:
        return False
    
    # Fix ChatCompletion API calls
    if 'openai.ChatCompletion' in content:
        print(f"Fixing ChatCompletion in {file_path}")
        # Replace old API call pattern with new API
        content = re.sub(
            r'openai\.ChatCompletion\.create\(\s*model\s*=\s*([^,]+),\s*messages\s*=\s*([^)]+)\)',
            r'openai.chat.completions.create(model=\1, messages=\2)',
            content
        )
    
    # Fix Completion API calls
    if 'openai.Completion' in content:
        print(f"Fixing Completion in {file_path}")
        content = re.sub(
            r'openai\.Completion\.create\(',
            r'openai.completions.create(',
            content
        )
    
    # Write updated content back to file
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def main():
    """Main function to fix OpenAI API compatibility issues."""
    if len(sys.argv) < 2:
        print("Usage: fix_openai.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a directory")
        sys.exit(1)
    
    python_files = find_python_files(directory)
    fixed_count = 0
    
    for file_path in python_files:
        if fix_openai_imports(file_path):
            fixed_count += 1
    
    print(f"Fixed OpenAI compatibility issues in {fixed_count} files.")

if __name__ == "__main__":
    main() 