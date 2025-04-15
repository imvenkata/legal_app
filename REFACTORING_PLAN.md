# Legal App Refactoring Plan

## Overview

This document outlines the plan to refactor the current Legal App codebase into a microservices architecture. The goal is to create independent, decoupled services that can be developed, deployed, and scaled independently.

## Target Architecture

```
legal_app/
├── auth-service/           # Authentication and user management
├── document-service/       # Document storage and metadata management
├── ingestion-service/      # Document processing and distribution pipeline
├── contract-service/       # Contract analysis and management
├── research-service/       # Legal research functionality
├── search-service/         # Vector search and retrieval
├── api-gateway/            # API Gateway for routing and aggregation
└── shared/                 # Shared libraries (optional)
```

## Service Responsibilities

### API Gateway
- Route requests to appropriate services
- Handle authentication and authorization
- Implement rate limiting
- Log requests
- Provide a unified API to frontend clients

### Auth Service
- User registration and authentication
- JWT token issuance and validation
- User profile management
- Role-based access control

### Document Service
- Store document metadata
- Manage document versions
- Handle document permissions
- Provide document retrieval APIs

### Ingestion Service
- Accept document uploads in various formats
- Process and parse documents (PDF, DOCX, TXT)
- Extract text and metadata
- Distribute processed documents to other services
- Track document processing status

### Contract Service
- Contract analysis and extraction
- Contract template management
- Contract generation
- Clause identification and categorization

### Research Service
- Legal research capabilities
- Case law analysis
- Legal Q&A functionality
- Research history and saved searches

### Search Service
- Document indexing
- Vector search capabilities
- Semantic search functionality
- Relevance scoring

## Refactoring Phases

### Phase 1: Infrastructure Setup
1. Create directory structure for new services
2. Set up Docker and docker-compose files
3. Create CI/CD pipelines
4. Set up service discovery mechanism

### Phase 2: Extract Core Services
1. Extract Auth Service from existing user functionality
2. Extract Document Service from existing document handling code
3. Convert Legal Search Service to independent Search Service
4. Implement API Gateway

### Phase 3: Implement New Services
1. Create Ingestion Service
2. Extract Contract Service functionality
3. Extract Research Service functionality
4. Implement shared libraries if needed

### Phase 4: Service Communication
1. Implement REST APIs for synchronous communication
2. Set up message broker (RabbitMQ/Kafka) for asynchronous events
3. Implement event handling in each service
4. Create service clients for inter-service communication

### Phase 5: Database Separation
1. Create separate databases for each service
2. Migrate data to new database structures
3. Implement data consistency patterns

## Implementation Details

### Each Service Structure
```
service-name/
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
├── src/
│   ├── api/                # Service API endpoints
│   │   ├── routes.py       # FastAPI routes
│   │   ├── models.py       # Pydantic models for API
│   │   └── dependencies.py # API dependencies
│   ├── core/               # Business logic
│   ├── db/                 # Database access
│   │   ├── models.py       # DB models
│   │   └── repositories.py # Data access
│   └── utils/              # Service-specific utilities
├── tests/                  # Service-specific tests
└── docker-compose.yml      # Local development setup
```

### Communication Patterns
1. **Synchronous Communication**:
   - REST APIs for direct service-to-service calls
   - Health check endpoints for all services

2. **Asynchronous Communication**:
   - Event-based architecture for loose coupling
   - Message formats defined per event type
   - Common events:
     - `document.uploaded`
     - `document.processed`
     - `document.indexed`
     - `contract.analyzed`

### API Gateway Configuration
- Use FastAPI for the gateway implementation
- Implement routing based on URL paths
- Add authentication middleware
- Configure CORS for frontend access

## Migration Strategy

### Incremental Migration
1. Start with extracting Auth Service and Document Service
2. Implement basic API Gateway routing to these services
3. Continue with Search Service migration
4. Add Ingestion Service
5. Finally implement Contract and Research Services

### Testing Strategy
1. Create unit tests for each service
2. Implement integration tests for service interactions
3. Create end-to-end tests for critical user flows
4. Compare results with existing system

## Development Workflow
1. Each service has its own repository or exists in a monorepo with clear boundaries
2. Services can be developed and tested independently
3. Local development using docker-compose
4. Deployment to development, staging, and production environments

## Next Steps
1. Create the initial directory structure
2. Set up Docker infrastructure
3. Begin extraction of Auth Service
4. Implement basic API Gateway functionality 