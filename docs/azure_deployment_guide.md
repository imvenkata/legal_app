# Azure Deployment Guide for Legal AI Application

This guide will help you deploy the Legal AI application to Microsoft Azure for production use.

## Prerequisites

Before you begin, ensure you have the following:

- An active Azure subscription
- Azure CLI installed and configured
- Docker installed (for container deployments)
- Git (for version control)
- The Legal AI application code repository

## Step 1: Azure Resource Setup

### Create a Resource Group

```bash
az group create --name legal-ai-rg --location eastus
```

### Set Up Azure Database for PostgreSQL

```bash
az postgres server create \
  --resource-group legal-ai-rg \
  --name legal-ai-postgres \
  --location eastus \
  --admin-user postgres \
  --admin-password <your-secure-password> \
  --sku-name GP_Gen5_2 \
  --version 13

# Create the database
az postgres db create \
  --resource-group legal-ai-rg \
  --server-name legal-ai-postgres \
  --name legal_ai
```

### Set Up Azure Cosmos DB (MongoDB API)

```bash
az cosmosdb create \
  --resource-group legal-ai-rg \
  --name legal-ai-cosmos \
  --kind MongoDB \
  --capabilities EnableMongo \
  --server-version 4.0 \
  --default-consistency-level Session

# Create the database
az cosmosdb mongodb database create \
  --resource-group legal-ai-rg \
  --account-name legal-ai-cosmos \
  --name legal_ai
```

### Create Azure Key Vault for Secrets

```bash
az keyvault create \
  --resource-group legal-ai-rg \
  --name legal-ai-keyvault \
  --location eastus

# Store secrets
az keyvault secret set --vault-name legal-ai-keyvault --name POSTGRES-PASSWORD --value <your-secure-password>
az keyvault secret set --vault-name legal-ai-keyvault --name OPENAI-API-KEY --value <your-openai-api-key>
az keyvault secret set --vault-name legal-ai-keyvault --name GOOGLE-API-KEY --value <your-google-api-key>
az keyvault secret set --vault-name legal-ai-keyvault --name DEEPSEEK-API-KEY --value <your-deepseek-api-key>
az keyvault secret set --vault-name legal-ai-keyvault --name JWT-SECRET --value <your-jwt-secret>
```

## Step 2: Containerize the Application

### Create Docker Files

#### Backend API Gateway Dockerfile

Create a file named `Dockerfile` in the `backend/api_gateway` directory:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Backend Services Dockerfiles

Create similar Dockerfiles for each service in their respective directories.

#### Frontend Dockerfile

Create a file named `Dockerfile` in the `frontend` directory:

```dockerfile
FROM node:16-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

Create an `nginx.conf` file in the `frontend` directory:

```
server {
    listen 80;
    
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://api-gateway:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Create Docker Compose File

Create a `docker-compose.yml` file in the root directory:

```yaml
version: '3.8'

services:
  api-gateway:
    build: ./backend/api_gateway
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_HOST=${POSTGRES_HOST}
      - POSTGRES_PORT=${POSTGRES_PORT}
      - POSTGRES_DB=${POSTGRES_DB}
      - MONGO_URI=${MONGO_URI}
      - MONGO_DB=${MONGO_DB}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - DOCUMENT_SERVICE_URL=http://document-service:8001
      - RESEARCH_SERVICE_URL=http://research-service:8002
      - CONTRACT_SERVICE_URL=http://contract-service:8003

  document-service:
    build: ./backend/services/document_service
    ports:
      - "8001:8001"
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_HOST=${POSTGRES_HOST}
      - POSTGRES_PORT=${POSTGRES_PORT}
      - POSTGRES_DB=${POSTGRES_DB}
      - MONGO_URI=${MONGO_URI}
      - MONGO_DB=${MONGO_DB}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}

  research-service:
    build: ./backend/services/research_service
    ports:
      - "8002:8002"
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_HOST=${POSTGRES_HOST}
      - POSTGRES_PORT=${POSTGRES_PORT}
      - POSTGRES_DB=${POSTGRES_DB}
      - MONGO_URI=${MONGO_URI}
      - MONGO_DB=${MONGO_DB}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}

  contract-service:
    build: ./backend/services/contract_service
    ports:
      - "8003:8003"
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_HOST=${POSTGRES_HOST}
      - POSTGRES_PORT=${POSTGRES_PORT}
      - POSTGRES_DB=${POSTGRES_DB}
      - MONGO_URI=${MONGO_URI}
      - MONGO_DB=${MONGO_DB}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - api-gateway
```

## Step 3: Deploy to Azure Container Apps

### Create Azure Container Registry

```bash
az acr create \
  --resource-group legal-ai-rg \
  --name legalairegistry \
  --sku Basic \
  --admin-enabled true
```

### Build and Push Docker Images

```bash
# Log in to ACR
az acr login --name legalairegistry

# Build and push images
az acr build --registry legalairegistry --image legal-ai/api-gateway:latest ./backend/api_gateway
az acr build --registry legalairegistry --image legal-ai/document-service:latest ./backend/services/document_service
az acr build --registry legalairegistry --image legal-ai/research-service:latest ./backend/services/research_service
az acr build --registry legalairegistry --image legal-ai/contract-service:latest ./backend/services/contract_service
az acr build --registry legalairegistry --image legal-ai/frontend:latest ./frontend
```

### Create Azure Container Apps Environment

```bash
az containerapp env create \
  --resource-group legal-ai-rg \
  --name legal-ai-env \
  --location eastus
```

### Deploy Container Apps

```bash
# Deploy API Gateway
az containerapp create \
  --resource-group legal-ai-rg \
  --name api-gateway \
  --environment legal-ai-env \
  --image legalairegistry.azurecr.io/legal-ai/api-gateway:latest \
  --registry-server legalairegistry.azurecr.io \
  --target-port 8000 \
  --ingress external \
  --env-vars POSTGRES_HOST=legal-ai-postgres.postgres.database.azure.com \
             POSTGRES_USER=postgres@legal-ai-postgres \
             POSTGRES_DB=legal_ai \
             POSTGRES_PORT=5432 \
             MONGO_URI=mongodb://legal-ai-cosmos:${COSMOS_KEY}@legal-ai-cosmos.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb \
             MONGO_DB=legal_ai \
             DOCUMENT_SERVICE_URL=https://document-service.${CONTAINER_APP_ENV_DEFAULT_DOMAIN} \
             RESEARCH_SERVICE_URL=https://research-service.${CONTAINER_APP_ENV_DEFAULT_DOMAIN} \
             CONTRACT_SERVICE_URL=https://contract-service.${CONTAINER_APP_ENV_DEFAULT_DOMAIN}

# Deploy other services similarly
# ...

# Deploy Frontend
az containerapp create \
  --resource-group legal-ai-rg \
  --name frontend \
  --environment legal-ai-env \
  --image legalairegistry.azurecr.io/legal-ai/frontend:latest \
  --registry-server legalairegistry.azurecr.io \
  --target-port 80 \
  --ingress external
```

### Set Up Key Vault Integration

```bash
# Get the managed identity of the container app
IDENTITY_ID=$(az containerapp show --resource-group legal-ai-rg --name api-gateway --query "identity.principalId" -o tsv)

# Grant access to Key Vault
az keyvault set-policy \
  --name legal-ai-keyvault \
  --object-id $IDENTITY_ID \
  --secret-permissions get list
```

## Step 4: Set Up Azure Front Door (Optional)

For production deployments, you may want to set up Azure Front Door for global load balancing and SSL termination:

```bash
# Create Front Door profile
az afd profile create \
  --resource-group legal-ai-rg \
  --profile-name legal-ai-afd \
  --sku Standard_AzureFrontDoor

# Add endpoint
az afd endpoint create \
  --resource-group legal-ai-rg \
  --profile-name legal-ai-afd \
  --endpoint-name legal-ai \
  --enabled-state Enabled

# Add origin group
az afd origin-group create \
  --resource-group legal-ai-rg \
  --profile-name legal-ai-afd \
  --origin-group-name frontend-origin-group \
  --probe-request-type GET \
  --probe-protocol Http \
  --probe-interval-in-seconds 120 \
  --probe-path / \
  --sample-size 4 \
  --successful-samples-required 3 \
  --additional-latency-in-milliseconds 50

# Add origin
az afd origin create \
  --resource-group legal-ai-rg \
  --profile-name legal-ai-afd \
  --origin-group-name frontend-origin-group \
  --origin-name frontend-origin \
  --host-name frontend.${CONTAINER_APP_ENV_DEFAULT_DOMAIN} \
  --http-port 80 \
  --https-port 443 \
  --priority 1 \
  --weight 1000 \
  --enabled-state Enabled

# Add route
az afd route create \
  --resource-group legal-ai-rg \
  --profile-name legal-ai-afd \
  --endpoint-name legal-ai \
  --route-name default-route \
  --origin-group frontend-origin-group \
  --supported-protocols Http Https \
  --patterns-to-match /* \
  --forwarding-protocol MatchRequest \
  --link-to-default-domain Enabled
```

## Step 5: Set Up Custom Domain and SSL (Optional)

If you have a custom domain, you can configure it with Azure Front Door:

```bash
# Add custom domain to Front Door
az afd custom-domain create \
  --resource-group legal-ai-rg \
  --profile-name legal-ai-afd \
  --custom-domain-name legal-ai-custom \
  --host-name legal-ai.yourdomain.com \
  --minimum-tls-version TLS12

# Enable HTTPS for custom domain
az afd custom-domain enable-https \
  --resource-group legal-ai-rg \
  --profile-name legal-ai-afd \
  --custom-domain-name legal-ai-custom
```

## Step 6: Set Up Monitoring and Logging

### Enable Application Insights

```bash
# Create Application Insights resource
az monitor app-insights component create \
  --resource-group legal-ai-rg \
  --app legal-ai-insights \
  --location eastus \
  --kind web \
  --application-type web

# Get the instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --resource-group legal-ai-rg \
  --app legal-ai-insights \
  --query instrumentationKey \
  --output tsv)

# Update container apps to use Application Insights
az containerapp update \
  --resource-group legal-ai-rg \
  --name api-gateway \
  --env-vars APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=$INSTRUMENTATION_KEY
```

## Step 7: Set Up CI/CD Pipeline (Optional)

You can set up a CI/CD pipeline using Azure DevOps or GitHub Actions for automated deployments.

### Example GitHub Actions Workflow

Create a file named `.github/workflows/deploy.yml` in your repository:

```yaml
name: Deploy to Azure

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Log in to Azure
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Log in to ACR
      uses: azure/docker-login@v1
      with:
        login-server: legalairegistry.azurecr.io
        username: ${{ secrets.ACR_USERNAME }}
        password: ${{ secrets.ACR_PASSWORD }}
    
    - name: Build and push images
      run: |
        az acr build --registry legalairegistry --image legal-ai/api-gateway:latest ./backend/api_gateway
        az acr build --registry legalairegistry --image legal-ai/document-service:latest ./backend/services/document_service
        az acr build --registry legalairegistry --image legal-ai/research-service:latest ./backend/services/research_service
        az acr build --registry legalairegistry --image legal-ai/contract-service:latest ./backend/services/contract_service
        az acr build --registry legalairegistry --image legal-ai/frontend:latest ./frontend
    
    - name: Deploy to Container Apps
      run: |
        az containerapp update \
          --resource-group legal-ai-rg \
          --name api-gateway \
          --image legalairegistry.azurecr.io/legal-ai/api-gateway:latest
        
        # Update other services similarly
```

## Troubleshooting

### Database Connection Issues

- Check the connection strings in your environment variables
- Verify that the firewall rules allow connections from your Container Apps
- Ensure the database user has appropriate permissions

### Container Deployment Issues

- Check the container logs using `az containerapp logs show`
- Verify that all environment variables are correctly set
- Check if the container registry is accessible

### Network Issues

- Verify that the Container Apps can communicate with each other
- Check if the Front Door configuration is correct
- Ensure that the custom domain DNS settings are properly configured

## Security Considerations

1. **Network Security**:
   - Use private endpoints for Azure PostgreSQL and Cosmos DB
   - Configure network security groups to restrict access

2. **Secret Management**:
   - Use Azure Key Vault for storing secrets
   - Implement managed identities for accessing Key Vault

3. **Authentication and Authorization**:
   - Implement Azure AD authentication for the application
   - Set up role-based access control (RBAC)

4. **Data Protection**:
   - Enable encryption at rest for all data stores
   - Implement proper backup and recovery procedures

## Cost Optimization

1. **Right-sizing Resources**:
   - Start with smaller instance sizes and scale up as needed
   - Use consumption-based pricing models where appropriate

2. **Auto-scaling**:
   - Configure auto-scaling for Container Apps based on load
   - Scale to zero when not in use for development environments

3. **Reserved Instances**:
   - Consider purchasing reserved instances for production workloads
   - Use Azure Hybrid Benefit if applicable

## Next Steps

After successfully deploying the application to Azure, you can:

1. Set up a staging environment for testing
2. Implement a blue-green deployment strategy
3. Set up automated backups for databases
4. Configure alerts and monitoring dashboards
5. Perform load testing to ensure scalability
