#!/bin/bash

# Quick Azure Deployment Script for GOFAP
# This script automates the entire Azure infrastructure setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   GOFAP Azure Deployment Script                      ║${NC}"
echo -e "${BLUE}║   Government Operations Financial Accounting Platform║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI is not installed${NC}"
    echo -e "${YELLOW}Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli${NC}"
    exit 1
fi

# Login to Azure
echo -e "${BLUE}🔐 Logging in to Azure...${NC}"
az login

# Prompt for configuration
echo ""
echo -e "${YELLOW}📋 Please provide the following information:${NC}"
echo ""

read -p "Resource Group Name [gofap-rg]: " RESOURCE_GROUP
RESOURCE_GROUP=${RESOURCE_GROUP:-gofap-rg}

read -p "Location [eastus]: " LOCATION
LOCATION=${LOCATION:-eastus}

read -p "Web App Name [gofap-app]: " WEBAPP_NAME
WEBAPP_NAME=${WEBAPP_NAME:-gofap-app}

read -p "PostgreSQL Admin Password: " -s POSTGRES_PASSWORD
echo ""

if [ -z "$POSTGRES_PASSWORD" ]; then
    echo -e "${RED}❌ PostgreSQL password is required${NC}"
    exit 1
fi

# Generate unique names
TIMESTAMP=$(date +%s)
ACR_NAME="gofapreg${TIMESTAMP}"
KEY_VAULT_NAME="gofapkv${TIMESTAMP}"
POSTGRES_SERVER="gofappg${TIMESTAMP}"

echo ""
echo -e "${GREEN}✅ Configuration complete${NC}"
echo ""
echo -e "${BLUE}Deploying with the following settings:${NC}"
echo -e "  Resource Group: ${GREEN}$RESOURCE_GROUP${NC}"
echo -e "  Location: ${GREEN}$LOCATION${NC}"
echo -e "  Web App: ${GREEN}$WEBAPP_NAME${NC}"
echo -e "  Container Registry: ${GREEN}$ACR_NAME${NC}"
echo -e "  Key Vault: ${GREEN}$KEY_VAULT_NAME${NC}"
echo -e "  PostgreSQL Server: ${GREEN}$POSTGRES_SERVER${NC}"
echo ""

read -p "Continue with deployment? (y/N): " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}🚀 Starting deployment...${NC}"
echo ""

# Deploy using ARM template
echo -e "${BLUE}📦 Deploying Azure resources...${NC}"
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --template-file azure-resources.json \
    --parameters \
        webAppName=$WEBAPP_NAME \
        containerRegistryName=$ACR_NAME \
        keyVaultName=$KEY_VAULT_NAME \
        postgresServerName=$POSTGRES_SERVER \
        postgresAdminPassword=$POSTGRES_PASSWORD \
    --query 'properties.outputs' \
    -o json > deployment-output.json

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Azure resources deployed successfully${NC}"
else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi

# Extract outputs
WEB_APP_URL=$(jq -r '.webAppUrl.value' deployment-output.json)
ACR_LOGIN_SERVER=$(jq -r '.containerRegistryLoginServer.value' deployment-output.json)
POSTGRES_FQDN=$(jq -r '.postgresServerFqdn.value' deployment-output.json)
KEY_VAULT_URI=$(jq -r '.keyVaultUri.value' deployment-output.json)
INSIGHTS_KEY=$(jq -r '.appInsightsInstrumentationKey.value' deployment-output.json)

echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}Deployment Information${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "🌐 Web App URL: ${GREEN}$WEB_APP_URL${NC}"
echo -e "🐳 Container Registry: ${GREEN}$ACR_LOGIN_SERVER${NC}"
echo -e "🗄️  PostgreSQL Server: ${GREEN}$POSTGRES_FQDN${NC}"
echo -e "🔐 Key Vault: ${GREEN}$KEY_VAULT_URI${NC}"
echo -e "📊 Application Insights Key: ${GREEN}${INSIGHTS_KEY:0:20}...${NC}"
echo ""

# Get Container Registry credentials
echo -e "${BLUE}📝 Retrieving Container Registry credentials...${NC}"
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}Next Steps${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}1. Build and push Docker image:${NC}"
echo -e "   docker build -t $ACR_LOGIN_SERVER/gofap:latest ."
echo -e "   az acr login --name $ACR_NAME"
echo -e "   docker push $ACR_LOGIN_SERVER/gofap:latest"
echo ""
echo -e "${YELLOW}2. Configure GitHub Secrets:${NC}"
echo -e "   AZURE_REGISTRY_LOGIN_SERVER: $ACR_LOGIN_SERVER"
echo -e "   AZURE_REGISTRY_USERNAME: $ACR_USERNAME"
echo -e "   AZURE_REGISTRY_PASSWORD: <saved to azure-credentials.txt>"
echo ""
echo -e "${YELLOW}3. Add secrets to Azure Key Vault:${NC}"
echo -e "   az keyvault secret set --vault-name $KEY_VAULT_NAME --name SECRET-KEY --value 'your-flask-secret'"
echo -e "   az keyvault secret set --vault-name $KEY_VAULT_NAME --name DATABASE-URL --value 'postgresql://...'"
echo ""
echo -e "${YELLOW}4. Configure Cloudflare DNS:${NC}"
echo -e "   CNAME record: gofap → $WEBAPP_NAME.azurewebsites.net"
echo ""

# Save credentials to file
echo "Container Registry Credentials" > azure-credentials.txt
echo "================================" >> azure-credentials.txt
echo "Login Server: $ACR_LOGIN_SERVER" >> azure-credentials.txt
echo "Username: $ACR_USERNAME" >> azure-credentials.txt
echo "Password: $ACR_PASSWORD" >> azure-credentials.txt
echo "" >> azure-credentials.txt
echo "PostgreSQL Connection" >> azure-credentials.txt
echo "================================" >> azure-credentials.txt
echo "Server: $POSTGRES_FQDN" >> azure-credentials.txt
echo "Database: gofap_db" >> azure-credentials.txt
echo "Username: gofapadmin" >> azure-credentials.txt
echo "" >> azure-credentials.txt
echo "Key Vault" >> azure-credentials.txt
echo "================================" >> azure-credentials.txt
echo "Name: $KEY_VAULT_NAME" >> azure-credentials.txt
echo "URI: $KEY_VAULT_URI" >> azure-credentials.txt

echo -e "${GREEN}✅ Credentials saved to azure-credentials.txt${NC}"
echo -e "${RED}⚠️  Keep this file secure and delete after setup${NC}"
echo ""
echo -e "${GREEN}🎉 Azure deployment complete!${NC}"
