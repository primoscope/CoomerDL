#!/bin/bash
set -e

# CoomerDL Azure Deployment Script
# This script deploys CoomerDL to Azure Container Apps

echo "🚀 CoomerDL Azure Deployment Script"
echo "====================================="
echo ""

# Configuration
PROJECT_NAME="${PROJECT_NAME:-coomerdl}"
ENVIRONMENT="${ENVIRONMENT:-production}"
AZURE_LOCATION="${AZURE_LOCATION:-eastus}"
RESOURCE_GROUP="${PROJECT_NAME}-${ENVIRONMENT}-rg"
DEPLOYMENT_NAME="${PROJECT_NAME}-${ENVIRONMENT}-deployment"

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install it: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install it: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Prerequisites met"
echo ""

# Login check
echo "🔐 Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "Please log in to Azure:"
    az login
fi

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "✅ Logged in to subscription: ${SUBSCRIPTION_ID}"
echo ""

# Configuration
REGISTRY_NAME="${PROJECT_NAME}${ENVIRONMENT}acr"
CONTAINER_IMAGE="${REGISTRY_NAME}.azurecr.io/${PROJECT_NAME}:latest"

echo "📦 Deployment Configuration:"
echo "  Project: ${PROJECT_NAME}"
echo "  Environment: ${ENVIRONMENT}"
echo "  Location: ${AZURE_LOCATION}"
echo "  Resource Group: ${RESOURCE_GROUP}"
echo "  Registry: ${REGISTRY_NAME}"
echo ""

# Create resource group
echo "🏗️  Creating resource group..."
if ! az group show --name ${RESOURCE_GROUP} &> /dev/null; then
    az group create \
        --name ${RESOURCE_GROUP} \
        --location ${AZURE_LOCATION} \
        --tags project=${PROJECT_NAME} environment=${ENVIRONMENT}
    echo "✅ Resource group created"
else
    echo "✅ Resource group already exists"
fi
echo ""

# Create Azure Container Registry
echo "📦 Setting up Azure Container Registry..."
if ! az acr show --name ${REGISTRY_NAME} --resource-group ${RESOURCE_GROUP} &> /dev/null; then
    az acr create \
        --resource-group ${RESOURCE_GROUP} \
        --name ${REGISTRY_NAME} \
        --sku Basic \
        --location ${AZURE_LOCATION} \
        --admin-enabled true
    echo "✅ ACR created"
else
    echo "✅ ACR already exists"
fi
echo ""

# Build and push Docker image
echo "🐳 Building Docker image..."
docker build -t ${PROJECT_NAME}:latest -f Dockerfile.webapp .
echo "✅ Docker image built"
echo ""

echo "📤 Pushing image to ACR..."
az acr login --name ${REGISTRY_NAME}
docker tag ${PROJECT_NAME}:latest ${CONTAINER_IMAGE}
docker push ${CONTAINER_IMAGE}
echo "✅ Image pushed to ACR"
echo ""

# Deploy ARM template
echo "☁️  Deploying Azure resources..."
az deployment group create \
    --resource-group ${RESOURCE_GROUP} \
    --name ${DEPLOYMENT_NAME} \
    --template-file azure/azuredeploy.json \
    --parameters \
        projectName=${PROJECT_NAME} \
        environmentName=${ENVIRONMENT} \
        location=${AZURE_LOCATION} \
        containerImage=${CONTAINER_IMAGE} \
        cpuCores=2 \
        memoryInGb=4 \
        replicaCount=1

echo "✅ Azure resources deployed"
echo ""

# Get outputs
echo "📊 Deployment Information:"
APPLICATION_URL=$(az deployment group show \
    --resource-group ${RESOURCE_GROUP} \
    --name ${DEPLOYMENT_NAME} \
    --query properties.outputs.applicationUrl.value \
    --output tsv)

STORAGE_ACCOUNT=$(az deployment group show \
    --resource-group ${RESOURCE_GROUP} \
    --name ${DEPLOYMENT_NAME} \
    --query properties.outputs.storageAccountName.value \
    --output tsv)

CONTAINER_APP=$(az deployment group show \
    --resource-group ${RESOURCE_GROUP} \
    --name ${DEPLOYMENT_NAME} \
    --query properties.outputs.containerAppName.value \
    --output tsv)

echo "  Application URL: ${APPLICATION_URL}"
echo "  Storage Account: ${STORAGE_ACCOUNT}"
echo "  Container App: ${CONTAINER_APP}"
echo "  Container Registry: ${REGISTRY_NAME}.azurecr.io"
echo ""

# Wait for deployment to be ready
echo "⏳ Waiting for container app to be ready..."
sleep 30  # Give it some time to start

# Check health
echo "🏥 Checking application health..."
if curl -sf "${APPLICATION_URL}/health" > /dev/null 2>&1; then
    echo "✅ Application is healthy"
else
    echo "⚠️  Application may still be starting up. Check logs with:"
    echo "  az containerapp logs show --name ${CONTAINER_APP} --resource-group ${RESOURCE_GROUP} --follow"
fi
echo ""

echo "🎉 Deployment Complete!"
echo ""
echo "📝 Next Steps:"
echo "  1. Visit your application: ${APPLICATION_URL}"
echo "  2. Configure custom domain (optional):"
echo "     az containerapp hostname add --hostname yourdomain.com --resource-group ${RESOURCE_GROUP} --name ${CONTAINER_APP}"
echo "  3. View logs:"
echo "     az containerapp logs show --name ${CONTAINER_APP} --resource-group ${RESOURCE_GROUP} --follow"
echo "  4. Scale replicas:"
echo "     az containerapp update --name ${CONTAINER_APP} --resource-group ${RESOURCE_GROUP} --max-replicas 5"
echo "  5. View metrics: Azure Portal → ${CONTAINER_APP} → Metrics"
echo ""
echo "🗑️  To delete this deployment:"
echo "  az group delete --name ${RESOURCE_GROUP} --yes --no-wait"
echo ""
