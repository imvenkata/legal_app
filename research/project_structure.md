# Legal AI Application Project Structure

This document outlines the project structure for our legal AI application.

```
legal_app/
├── backend/                      # Python backend
│   ├── api_gateway/              # FastAPI API Gateway
│   │   ├── app.py                # Main FastAPI application
│   │   ├── auth/                 # Authentication modules
│   │   ├── middleware/           # Middleware components
│   │   └── routers/              # API route definitions
│   ├── services/                 # Microservices
│   │   ├── document_service/     # Document processing service
│   │   │   ├── app.py            # Service entry point
│   │   │   ├── models/           # Data models
│   │   │   ├── routers/          # API routes
│   │   │   └── utils/            # Utility functions
│   │   ├── research_service/     # Legal research service
│   │   │   ├── app.py            # Service entry point
│   │   │   ├── models/           # Data models
│   │   │   ├── routers/          # API routes
│   │   │   └── utils/            # Utility functions
│   │   └── contract_service/     # Contract management service
│   │       ├── app.py            # Service entry point
│   │       ├── models/           # Data models
│   │       ├── routers/          # API routes
│   │       └── utils/            # Utility functions
│   ├── llm_adapter/              # LLM integration layer
│   │   ├── adapters/             # Model-specific adapters
│   │   │   ├── openai_adapter.py # OpenAI GPT adapter
│   │   │   ├── gemini_adapter.py # Google Gemini adapter
│   │   │   └── deepseek_adapter.py # DeepSeek adapter
│   │   ├── prompts/              # Prompt templates
│   │   └── utils/                # Utility functions
│   ├── common/                   # Shared components
│   │   ├── database/             # Database connections
│   │   ├── models/               # Shared data models
│   │   └── utils/                # Shared utilities
│   ├── tests/                    # Backend tests
│   ├── requirements.txt          # Python dependencies
│   └── docker-compose.yml        # Docker configuration
├── frontend/                     # React frontend
│   ├── public/                   # Static assets
│   ├── src/                      # Source code
│   │   ├── components/           # Reusable UI components
│   │   │   ├── common/           # Common components
│   │   │   ├── document/         # Document review components
│   │   │   ├── research/         # Legal research components
│   │   │   └── contract/         # Contract drafting components
│   │   ├── pages/                # Page components
│   │   │   ├── Dashboard.jsx     # Main dashboard
│   │   │   ├── DocumentReview.jsx # Document review page
│   │   │   ├── LegalResearch.jsx # Legal research page
│   │   │   ├── ContractDrafting.jsx # Contract drafting page
│   │   │   └── Settings.jsx      # Settings page
│   │   ├── services/             # API service clients
│   │   ├── store/                # Redux store
│   │   ├── utils/                # Utility functions
│   │   ├── App.jsx               # Main application component
│   │   └── index.jsx             # Entry point
│   ├── package.json              # NPM dependencies
│   └── vite.config.js            # Vite configuration
├── docs/                         # Documentation
│   ├── api/                      # API documentation
│   ├── deployment/               # Deployment guides
│   │   ├── local.md              # Local deployment guide
│   │   └── azure.md              # Azure deployment guide
│   └── user/                     # User guides
├── scripts/                      # Utility scripts
│   ├── setup.sh                  # Setup script
│   └── dev.sh                    # Development script
└── docker-compose.yml            # Root Docker Compose file
```

This structure follows a microservices architecture with clear separation of concerns:

1. The backend is organized into an API gateway and three microservices, each handling a specific use case
2. The LLM adapter layer provides a unified interface to different LLM models
3. The frontend is organized by features with reusable components
4. Documentation and scripts are included for easy setup and deployment
