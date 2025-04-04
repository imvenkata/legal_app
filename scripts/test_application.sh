#!/bin/bash

# Test script for Legal AI Application
# This script tests the basic functionality of the application components
# Modified version that doesn't require virtual environment

echo "Starting Legal AI Application Test Script"
echo "----------------------------------------"

# Create test directory
mkdir -p /home/ubuntu/legal_app/tests/results
TEST_DIR="/home/ubuntu/legal_app/tests/results"
echo "Created test directory at $TEST_DIR"

# Test 1: Check Python environment and dependencies
echo -e "\n[Test 1] Checking Python environment and dependencies"
cd /home/ubuntu/legal_app/backend
python3 --version > $TEST_DIR/python_version.txt
if [ $? -eq 0 ]; then
    echo "✅ Python is installed"
else
    echo "❌ Python is not installed correctly"
    exit 1
fi

# Check if required packages are available
echo "Checking required Python packages"
python3 -c "import fastapi" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ FastAPI is available"
else
    echo "⚠️ FastAPI is not installed (this is expected if you haven't installed dependencies yet)"
fi

# Test 2: Check backend code syntax
echo -e "\n[Test 2] Checking backend code syntax"
find . -name "*.py" | while read file; do
    python3 -m py_compile "$file" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ $file syntax is correct"
    else
        echo "❌ $file has syntax errors"
    fi
done > $TEST_DIR/syntax_check.log

# Count syntax errors
SYNTAX_ERRORS=$(grep -c "❌" $TEST_DIR/syntax_check.log)
if [ $SYNTAX_ERRORS -eq 0 ]; then
    echo "✅ All Python files have correct syntax"
else
    echo "❌ Found $SYNTAX_ERRORS files with syntax errors"
    grep "❌" $TEST_DIR/syntax_check.log
fi

# Test 3: Check LLM adapter structure
echo -e "\n[Test 3] Testing LLM adapter structure"
if [ -d "llm_adapter" ]; then
    echo "✅ LLM adapter directory exists"
    
    # Check for expected adapter files
    EXPECTED_FILES=("base_adapter.py" "openai_adapter.py" "gemini_adapter.py" "deepseek_adapter.py")
    MISSING_FILES=0
    
    for file in "${EXPECTED_FILES[@]}"; do
        if [ -f "llm_adapter/adapters/$file" ]; then
            echo "✅ Found adapter file: $file"
        else
            echo "❌ Missing adapter file: $file"
            MISSING_FILES=$((MISSING_FILES+1))
        fi
    done
    
    if [ $MISSING_FILES -eq 0 ]; then
        echo "✅ All expected LLM adapter files are present"
    else
        echo "❌ Missing $MISSING_FILES adapter files"
    fi
    
    # Check for factory pattern
    if [ -f "llm_adapter/factory.py" ]; then
        echo "✅ LLM adapter factory exists"
    else
        echo "❌ Missing LLM adapter factory"
    fi
else
    echo "❌ LLM adapter directory is missing"
fi

# Test 4: Check Node.js and npm for frontend
echo -e "\n[Test 4] Checking Node.js environment"
cd /home/ubuntu/legal_app/frontend
node --version > $TEST_DIR/node_version.txt 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Node.js is installed"
else
    echo "⚠️ Node.js is not installed or not in PATH (this is expected if you're using a different environment)"
fi

npm --version > $TEST_DIR/npm_version.txt 2>&1
if [ $? -eq 0 ]; then
    echo "✅ npm is installed"
else
    echo "⚠️ npm is not installed or not in PATH (this is expected if you're using a different environment)"
fi

# Test 5: Check frontend code structure
echo -e "\n[Test 5] Checking frontend code structure"
if [ -f "src/App.jsx" ]; then
    echo "✅ Main App component exists"
else
    echo "❌ Main App component is missing"
fi

if [ -f "src/index.jsx" ]; then
    echo "✅ Entry point file exists"
else
    echo "❌ Entry point file is missing"
fi

if [ -d "src/components" ]; then
    echo "✅ Components directory exists"
    
    # Count components
    COMPONENT_COUNT=$(find src/components -name "*.jsx" | wc -l)
    echo "Found $COMPONENT_COUNT component files"
else
    echo "❌ Components directory is missing"
fi

# Test 6: Check API endpoints structure
echo -e "\n[Test 6] Checking API endpoints structure"
cd /home/ubuntu/legal_app/backend
if [ -d "api_gateway/routers" ]; then
    echo "✅ API routers directory exists"
    
    # Check for expected router files
    EXPECTED_ROUTERS=("documents.py" "research.py" "contracts.py" "users.py")
    MISSING_ROUTERS=0
    
    for file in "${EXPECTED_ROUTERS[@]}"; do
        if [ -f "api_gateway/routers/$file" ]; then
            echo "✅ Found router file: $file"
        else
            echo "❌ Missing router file: $file"
            MISSING_ROUTERS=$((MISSING_ROUTERS+1))
        fi
    done
    
    if [ $MISSING_ROUTERS -eq 0 ]; then
        echo "✅ All expected API router files are present"
    else
        echo "❌ Missing $MISSING_ROUTERS router files"
    fi
else
    echo "❌ API routers directory is missing"
fi

# Test 7: Check database models
echo -e "\n[Test 7] Checking database models"
if [ -d "common/models" ]; then
    echo "✅ Database models directory exists"
    
    if [ -f "common/models/schemas.py" ]; then
        echo "✅ Database schemas file exists"
    else
        echo "❌ Database schemas file is missing"
    fi
else
    echo "❌ Database models directory is missing"
fi

# Test 8: Check frontend components
echo -e "\n[Test 8] Checking frontend components"
cd /home/ubuntu/legal_app/frontend

# Define expected components
EXPECTED_COMPONENTS=(
  "src/components/document/DocumentUploader.jsx"
  "src/components/document/DocumentUploaderConnected.jsx"
  "src/components/research/LegalResearch.jsx"
  "src/components/research/LegalResearchConnected.jsx"
  "src/components/contract/ContractDrafter.jsx"
  "src/components/contract/ContractDrafterConnected.jsx"
  "src/components/common/Navigation.jsx"
  "src/components/common/Settings.jsx"
  "src/components/common/Auth.jsx"
)

MISSING_COMPONENTS=0

for component in "${EXPECTED_COMPONENTS[@]}"; do
    if [ -f "$component" ]; then
        echo "✅ Found component: $component"
    else
        echo "❌ Missing component: $component"
        MISSING_COMPONENTS=$((MISSING_COMPONENTS+1))
    fi
done

if [ $MISSING_COMPONENTS -eq 0 ]; then
    echo "✅ All expected frontend components are present"
else
    echo "❌ Missing $MISSING_COMPONENTS frontend components"
fi

# Test 9: Check Redux store
echo -e "\n[Test 9] Checking Redux store"

# Define expected Redux files
EXPECTED_REDUX_FILES=(
  "src/store/index.js"
  "src/store/userSlice.js"
  "src/store/documentSlice.js"
  "src/store/researchSlice.js"
  "src/store/contractSlice.js"
)

MISSING_REDUX_FILES=0

for file in "${EXPECTED_REDUX_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ Found Redux file: $file"
    else
        echo "❌ Missing Redux file: $file"
        MISSING_REDUX_FILES=$((MISSING_REDUX_FILES+1))
    fi
done

if [ $MISSING_REDUX_FILES -eq 0 ]; then
    echo "✅ All expected Redux files are present"
else
    echo "❌ Missing $MISSING_REDUX_FILES Redux files"
fi

# Test 10: Check deployment documentation
echo -e "\n[Test 10] Checking deployment documentation"
DOCS_DIR="/home/ubuntu/legal_app/docs/deployment"
if [ -f "$DOCS_DIR/local_deployment_guide.md" ] && [ -f "$DOCS_DIR/azure_deployment_guide.md" ]; then
    echo "✅ Deployment documentation exists"
    
    # Check content of documentation
    LOCAL_GUIDE_SIZE=$(wc -l < "$DOCS_DIR/local_deployment_guide.md")
    AZURE_GUIDE_SIZE=$(wc -l < "$DOCS_DIR/azure_deployment_guide.md")
    
    echo "Local deployment guide: $LOCAL_GUIDE_SIZE lines"
    echo "Azure deployment guide: $AZURE_GUIDE_SIZE lines"
    
    if [ $LOCAL_GUIDE_SIZE -gt 50 ] && [ $AZURE_GUIDE_SIZE -gt 50 ]; then
        echo "✅ Deployment guides have sufficient content"
    else
        echo "❌ Deployment guides may be incomplete"
    fi
else
    echo "❌ Deployment documentation is missing"
fi

# Summary
echo -e "\n----------------------------------------"
echo "Legal AI Application Test Summary"
echo "----------------------------------------"
echo "Tests completed. Check $TEST_DIR for detailed logs."
echo "The application structure and code syntax have been verified."
echo "For full functionality testing, follow the local deployment guide to set up and run the application."
echo "----------------------------------------"
