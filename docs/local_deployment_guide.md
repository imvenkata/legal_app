# Local Deployment Guide for Legal AI Application

This guide will help you set up and run the Legal AI application locally for development and testing purposes.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python 3.10+ (for backend)
- Node.js 16+ and npm (for frontend)
- PostgreSQL 13+ (for relational database)
- MongoDB 5+ (for document storage)
- Git (for version control)

## Step 1: Clone the Repository

```bash
git clone https://github.com/your-organization/legal-app.git
cd legal-app
```

## Step 2: Set Up Backend

### Create a Python Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### Set Up Environment Variables

Create a `.env` file in the `backend` directory with the following content:

```
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=legal_ai

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
MONGO_DB=legal_ai

# LLM API Keys
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# JWT Secret
JWT_SECRET=your_jwt_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
CORS_ORIGINS=http://localhost:3000
```

Replace the placeholder values with your actual configuration.

### Set Up Databases

1. Create PostgreSQL database:

```bash
psql -U postgres
CREATE DATABASE legal_ai;
\q
```

2. MongoDB will create the database automatically when first accessed.

### Run Database Migrations

```bash
alembic upgrade head
```

## Step 3: Start Backend Services

You'll need to start multiple services for the backend. Open separate terminal windows for each service:

### API Gateway

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
cd api_gateway
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Document Service

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
cd services/document_service
uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

### Research Service

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
cd services/research_service
uvicorn app:app --host 0.0.0.0 --port 8002 --reload
```

### Contract Service

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
cd services/contract_service
uvicorn app:app --host 0.0.0.0 --port 8003 --reload
```

## Step 4: Set Up Frontend

### Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Set Up Environment Variables

Create a `.env` file in the `frontend` directory with the following content:

```
REACT_APP_API_BASE_URL=http://localhost:8000
```

### Start Frontend Development Server

```bash
npm start
```

The application should now be running at http://localhost:3000.

## Step 5: Create Initial Admin User

You can create an initial admin user using the provided script:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python scripts/create_admin_user.py
```

## Step 6: Testing the Application

1. Open your browser and navigate to http://localhost:3000
2. Log in with the admin credentials you created
3. You can now test all features of the application:
   - Document Review and Analysis
   - Legal Research with Predictive Analytics
   - Contract Drafting and Generation

## Troubleshooting

### Backend Services Not Starting

- Check if the required ports (8000-8003) are available
- Ensure all dependencies are installed correctly
- Verify database connections are working

### Database Connection Issues

- Check if PostgreSQL and MongoDB services are running
- Verify the connection strings in the `.env` file
- Ensure the database user has appropriate permissions

### LLM Integration Issues

- Verify that your API keys for OpenAI, Google, and DeepSeek are valid
- Check the logs for any API rate limiting or quota issues
- Ensure the LLM adapter configuration is correct

### Frontend Connection Issues

- Verify that the API base URL is correctly set in the frontend `.env` file
- Check for CORS issues in the browser console
- Ensure all backend services are running

## Next Steps

After successfully deploying the application locally, you can:

1. Customize the application for your specific legal use cases
2. Add more LLM models to the adapter layer
3. Enhance the UI/UX based on user feedback
4. Implement additional security measures
5. Deploy to a production environment (see Azure Deployment Guide)
