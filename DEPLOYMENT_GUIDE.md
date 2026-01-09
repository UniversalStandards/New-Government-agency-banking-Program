# Azure, Cloudflare & GitHub Deployment Guide

## GOFAP Deployment to Azure with Cloudflare CDN

This guide provides complete instructions for deploying the Government Operations and Financial Accounting Platform (GOFAP) to Azure App Service with Cloudflare CDN and GitHub Actions CI/CD.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Azure Setup](#azure-setup)
3. [Cloudflare Setup](#cloudflare-setup)
4. [GitHub Setup](#github-setup)
5. [Deployment Process](#deployment-process)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## Prerequisites

### Required Tools
- Azure CLI (`az`) - [Install](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- Docker Desktop - [Install](https://www.docker.com/products/docker-desktop)
- Git - [Install](https://git-scm.com/downloads)
- Node.js 18+ - [Install](https://nodejs.org/)
- Python 3.11+ - [Install](https://www.python.org/downloads/)

### Required Accounts
- Azure account with active subscription
- Cloudflare account (Free or Pro tier)
- GitHub account with repository access
- Domain name (registered through any registrar)

---

## Azure Setup

### Step 1: Create Azure Resources

```bash
# Login to Azure
az login

# Set variables
RESOURCE_GROUP="gofap-rg"
LOCATION="eastus"
APP_SERVICE_PLAN="gofap-plan"
WEBAPP_NAME="gofap-app"
ACR_NAME="gofapregistry"
KEY_VAULT_NAME="gofap-keyvault"
POSTGRES_SERVER="gofap-postgres"
POSTGRES_DB="gofap_db"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Container Registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)

# Create App Service Plan (Linux)
az appservice plan create \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --is-linux \
  --sku P1V2

# Create Web App with container
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_SERVICE_PLAN \
  --name $WEBAPP_NAME \
  --deployment-container-image-name $ACR_LOGIN_SERVER/gofap:latest

# Configure container registry credentials
az webapp config container set \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --docker-custom-image-name $ACR_LOGIN_SERVER/gofap:latest \
  --docker-registry-server-url https://$ACR_LOGIN_SERVER \
  --docker-registry-server-user $ACR_USERNAME \
  --docker-registry-server-password $ACR_PASSWORD

# Enable container logging
az webapp log config \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --docker-container-logging filesystem

# Enable always on
az webapp config set \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --always-on true
```

### Step 2: Create PostgreSQL Database

```bash
# Create PostgreSQL server
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name $POSTGRES_SERVER \
  --location $LOCATION \
  --admin-user gofapadmin \
  --admin-password 'YourSecurePassword123!' \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --version 15

# Create database
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $POSTGRES_SERVER \
  --database-name $POSTGRES_DB

# Configure firewall to allow Azure services
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name $POSTGRES_SERVER \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Get connection string
POSTGRES_CONNECTION_STRING="postgresql://gofapadmin:YourSecurePassword123!@$POSTGRES_SERVER.postgres.database.azure.com/$POSTGRES_DB?sslmode=require"
```

### Step 3: Create Azure Key Vault

```bash
# Create Key Vault
az keyvault create \
  --name $KEY_VAULT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Store secrets
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "SECRET-KEY" --value "your-flask-secret-key-here"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "DATABASE-URL" --value "$POSTGRES_CONNECTION_STRING"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "STRIPE-SECRET-KEY" --value "sk_live_your_stripe_key"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "STRIPE-PUBLISHABLE-KEY" --value "pk_live_your_stripe_key"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "MODERN-TREASURY-API-KEY" --value "your_mt_api_key"

# Grant webapp access to Key Vault
WEBAPP_IDENTITY=$(az webapp identity assign \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query principalId -o tsv)

az keyvault set-policy \
  --name $KEY_VAULT_NAME \
  --object-id $WEBAPP_IDENTITY \
  --secret-permissions get list
```

### Step 4: Configure Application Settings

```bash
# Configure app settings to reference Key Vault
az webapp config appsettings set \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    FLASK_ENV=production \
    WEBSITES_PORT=5000 \
    SECRET_KEY="@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT_NAME.vault.azure.net/secrets/SECRET-KEY/)" \
    DATABASE_URL="@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT_NAME.vault.azure.net/secrets/DATABASE-URL/)" \
    STRIPE_SECRET_KEY="@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT_NAME.vault.azure.net/secrets/STRIPE-SECRET-KEY/)"
```

### Step 5: Enable Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app gofap-insights \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP

# Get instrumentation key
INSIGHTS_KEY=$(az monitor app-insights component show \
  --app gofap-insights \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey -o tsv)

# Configure App Insights for webapp
az webapp config appsettings set \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY=$INSIGHTS_KEY
```

---

## Cloudflare Setup

### Step 1: Add Your Domain to Cloudflare

1. **Sign in to Cloudflare Dashboard**: https://dash.cloudflare.com/
2. **Add a site**: Enter your domain name (e.g., `gofap.gov`)
3. **Select plan**: Choose Free or Pro plan
4. **Update nameservers**: Update your domain registrar with Cloudflare nameservers
5. **Wait for activation**: Usually takes 24-48 hours

### Step 2: Configure DNS Records

```bash
# Get your Cloudflare Zone ID and API Token
CLOUDFLARE_ZONE_ID="your_zone_id"
CLOUDFLARE_API_TOKEN="your_api_token"

# Add DNS record pointing to Azure
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "CNAME",
    "name": "gofap",
    "content": "'$WEBAPP_NAME'.azurewebsites.net",
    "ttl": 1,
    "proxied": true
  }'

# Add www subdomain
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "CNAME",
    "name": "www",
    "content": "'$WEBAPP_NAME'.azurewebsites.net",
    "ttl": 1,
    "proxied": true
  }'
```

### Step 3: Configure SSL/TLS

1. **Navigate to SSL/TLS** in Cloudflare dashboard
2. **Set encryption mode**: Choose "Full (strict)"
3. **Enable Always Use HTTPS**: SSL/TLS → Edge Certificates → Always Use HTTPS
4. **Enable Automatic HTTPS Rewrites**: Turn on
5. **Minimum TLS Version**: Set to TLS 1.2

### Step 4: Configure Page Rules

Create page rules for optimal caching:

```
Rule 1: Static Assets
URL: *gofap.gov/static/*
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month
  - Browser Cache TTL: 1 day

Rule 2: API Endpoints
URL: *gofap.gov/api/*
Settings:
  - Cache Level: Bypass
  - Security Level: High

Rule 3: Admin Panel
URL: *gofap.gov/admin/*
Settings:
  - Cache Level: Bypass
  - Security Level: High
  - Browser Integrity Check: On
```

### Step 5: Configure Firewall Rules

```bash
# Block common threats
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/firewall/rules" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "filter": {
      "expression": "(cf.threat_score gt 14)",
      "paused": false
    },
    "action": "challenge",
    "description": "Challenge users with threat score > 14"
  }'
```

### Step 6: Enable Security Features

In Cloudflare Dashboard:
- **Security** → **WAF** → Enable Managed Rules
- **Security** → **DDoS** → Enable (automatic)
- **Security** → **Bot Management** → Configure based on needs
- **Speed** → **Optimization** → Enable:
  - Auto Minify (JS, CSS, HTML)
  - Brotli compression
  - Rocket Loader (optional)

---

## GitHub Setup

### Step 1: Configure Repository Secrets

Go to GitHub repository → Settings → Secrets and variables → Actions → New repository secret:

```
# Azure Credentials
AZURE_CLIENT_ID: <service-principal-client-id>
AZURE_TENANT_ID: <azure-tenant-id>
AZURE_SUBSCRIPTION_ID: <azure-subscription-id>
AZURE_RESOURCE_GROUP: gofap-rg
AZURE_KEY_VAULT_NAME: gofap-keyvault

# Azure Container Registry
AZURE_REGISTRY_LOGIN_SERVER: gofapregistry.azurecr.io
AZURE_REGISTRY_USERNAME: <acr-username>
AZURE_REGISTRY_PASSWORD: <acr-password>

# Cloudflare
CLOUDFLARE_API_TOKEN: <cloudflare-api-token>
CLOUDFLARE_ZONE_ID: <cloudflare-zone-id>
CLOUDFLARE_DNS_RECORD_ID: <dns-record-id>

# Application Secrets (stored in Key Vault, but needed for CI)
SECRET_KEY: <flask-secret-key>
DATABASE_URL: <postgres-connection-string>
STRIPE_SECRET_KEY: <stripe-secret-key>
```

### Step 2: Create Azure Service Principal

```bash
# Create service principal for GitHub Actions
az ad sp create-for-rbac \
  --name "gofap-github-actions" \
  --role contributor \
  --scopes /subscriptions/<subscription-id>/resourceGroups/$RESOURCE_GROUP \
  --sdk-auth

# Output will be JSON - save CLIENT_ID, TENANT_ID, SUBSCRIPTION_ID
```

### Step 3: Configure Branch Protection

1. Go to **Settings** → **Branches** → **Add rule**
2. **Branch name pattern**: `main` and `production`
3. Enable:
   - Require pull request reviews before merging
   - Require status checks to pass before merging
   - Require branches to be up to date before merging
   - Include administrators

---

## Deployment Process

### Initial Deployment

```bash
# Clone repository
git clone https://github.com/UniversalStandards/New-Government-agency-banking-Program.git
cd New-Government-agency-banking-Program

# Build and push initial Docker image
docker build -t $ACR_LOGIN_SERVER/gofap:latest .
az acr login --name $ACR_NAME
docker push $ACR_LOGIN_SERVER/gofap:latest

# Trigger deployment
git push origin main
```

### Automated Deployments

The GitHub Actions workflow (`.github/workflows/azure-deploy.yml`) automatically:

1. **On push to `main`**:
   - Runs tests
   - Builds Docker image
   - Deploys to staging environment
   - Runs smoke tests

2. **On push to `production`**:
   - Runs full test suite
   - Builds production Docker image
   - Deploys to production
   - Configures Cloudflare
   - Runs comprehensive health checks

### Manual Deployment

```bash
# Trigger manual deployment
gh workflow run azure-deploy.yml \
  --ref main \
  --field environment=production
```

---

## Monitoring & Troubleshooting

### View Application Logs

```bash
# Stream logs from Azure
az webapp log tail \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP

# View container logs
az webapp log download \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --log-file logs.zip
```

### Check Application Insights

1. Open Azure Portal
2. Navigate to **Application Insights** → **gofap-insights**
3. View:
   - **Live Metrics**: Real-time performance
   - **Failures**: Error tracking
   - **Performance**: Response times
   - **Availability**: Uptime monitoring

### Cloudflare Analytics

1. Open Cloudflare Dashboard
2. Navigate to **Analytics & Logs**
3. View:
   - **Traffic**: Requests, bandwidth
   - **Security**: Threats blocked
   - **Performance**: Cache hit rate

### Common Issues

#### Issue: Database connection fails

**Solution:**
```bash
# Check firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group $RESOURCE_GROUP \
  --name $POSTGRES_SERVER

# Add webapp IP if needed
WEBAPP_IP=$(az webapp show --name $WEBAPP_NAME --resource-group $RESOURCE_GROUP --query outboundIpAddresses -o tsv)
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name $POSTGRES_SERVER \
  --rule-name AllowWebApp \
  --start-ip-address $WEBAPP_IP \
  --end-ip-address $WEBAPP_IP
```

#### Issue: SSL certificate errors

**Solution:**
- Verify Cloudflare SSL mode is "Full (strict)"
- Check Azure custom domain SSL binding
- Ensure DNS records are proxied through Cloudflare

#### Issue: Static files not loading

**Solution:**
```bash
# Verify static files are in Docker image
docker run --rm $ACR_LOGIN_SERVER/gofap:latest ls -la /app/static

# Check Cloudflare cache
curl -I https://gofap.gov/static/css/style.css
```

---

## Security Checklist

- [ ] All secrets stored in Azure Key Vault
- [ ] HTTPS enforced via Cloudflare
- [ ] Firewall rules configured in Azure
- [ ] WAF enabled in Cloudflare
- [ ] Application Insights monitoring enabled
- [ ] Database backups configured
- [ ] Branch protection enabled in GitHub
- [ ] Multi-factor authentication enabled for all accounts
- [ ] Security headers configured in nginx
- [ ] Rate limiting enabled

---

## Cost Optimization

### Azure
- Use Azure Reserved Instances for 1-3 year savings
- Enable auto-scaling based on load
- Use Azure Cost Management for monitoring
- Consider Azure Hybrid Benefit if applicable

### Cloudflare
- Free tier includes CDN and basic security
- Pro tier ($20/mo) adds advanced features
- Monitor bandwidth usage

### Estimated Monthly Costs

| Service | Tier | Est. Cost |
|---------|------|-----------|
| Azure App Service | P1V2 | $75 |
| Azure PostgreSQL | B1ms | $15 |
| Azure Container Registry | Basic | $5 |
| Azure Key Vault | Standard | $3 |
| Application Insights | Basic | $10 |
| Cloudflare | Free/Pro | $0-20 |
| **Total** | | **$108-128/mo** |

---

## Maintenance

### Weekly Tasks
- Review Application Insights for errors
- Check Cloudflare analytics for security threats
- Review Azure costs

### Monthly Tasks
- Update dependencies (npm, pip)
- Review and rotate secrets
- Database backup verification
- Security patches

### Quarterly Tasks
- Full security audit
- Performance optimization review
- Cost optimization analysis
- Disaster recovery drill

---

## Support

For deployment issues:
- **Azure Support**: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade
- **Cloudflare Support**: https://support.cloudflare.com/
- **GitHub Support**: https://support.github.com/

For application issues:
- Open issue in GitHub repository
- Email: gofap@ofaps.spurs.gov
- Phone: (844) 697-7877 ext 6327

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-09  
**Next Review**: 2026-02-09
