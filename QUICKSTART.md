# Azure Deployment Quick Start Guide

## 🚀 Deploy GOFAP to Azure in 10 Minutes

This quick start guide gets you from zero to production deployment on Azure with Cloudflare CDN.

---

## Prerequisites (5 minutes)

1. **Install Azure CLI**
   ```bash
   # macOS
   brew install azure-cli
   
   # Windows
   winget install Microsoft.AzureCLI
   
   # Linux
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   ```

2. **Install Docker**
   - Download from https://www.docker.com/products/docker-desktop

3. **Get Cloudflare Account**
   - Sign up at https://dash.cloudflare.com/sign-up
   - Add your domain to Cloudflare

---

## Option 1: Automated Deployment (Recommended)

### One-Command Deployment

```bash
# Clone repository
git clone https://github.com/UniversalStandards/New-Government-agency-banking-Program.git
cd New-Government-agency-banking-Program

# Run deployment script
./deploy-azure.sh
```

The script will:
- ✅ Create all Azure resources
- ✅ Set up PostgreSQL database
- ✅ Configure Key Vault
- ✅ Deploy Container Registry
- ✅ Configure Application Insights
- ✅ Save credentials securely

**Time: ~5 minutes**

---

## Option 2: Manual Deployment

### Step 1: Create Resource Group (1 minute)

```bash
az login
az group create --name gofap-rg --location eastus
```

### Step 2: Deploy Infrastructure (3 minutes)

```bash
az deployment group create \
    --resource-group gofap-rg \
    --template-file azure-resources.json \
    --parameters postgresAdminPassword='YourSecurePassword123!'
```

### Step 3: Build and Push Docker Image (2 minutes)

```bash
# Get registry name from deployment output
ACR_NAME=$(az deployment group show -g gofap-rg -n azuredeploy --query properties.outputs.containerRegistryLoginServer.value -o tsv)

# Build and push
docker build -t $ACR_NAME/gofap:latest .
az acr login --name ${ACR_NAME/.azurecr.io/}
docker push $ACR_NAME/gofap:latest
```

### Step 4: Configure App Settings (1 minute)

```bash
WEBAPP_NAME="gofap-app"  # Use your actual webapp name

az webapp config appsettings set \
    --name $WEBAPP_NAME \
    --resource-group gofap-rg \
    --settings \
        FLASK_ENV=production \
        WEBSITES_PORT=5000
```

### Step 5: Verify Deployment (1 minute)

```bash
# Get webapp URL
WEBAPP_URL=$(az webapp show -g gofap-rg -n $WEBAPP_NAME --query defaultHostName -o tsv)

# Test it
curl https://$WEBAPP_URL
```

---

## Configure Cloudflare (5 minutes)

### Step 1: Add DNS Records

Go to Cloudflare Dashboard → DNS:

```
Type: CNAME
Name: @
Content: gofap-app.azurewebsites.net
Proxy: Enabled (orange cloud)
```

### Step 2: Enable SSL

Go to SSL/TLS → Overview:
- Set mode to: **Full (strict)**
- Enable: **Always Use HTTPS**

### Step 3: Create Page Rule

Go to Rules → Page Rules → Create Page Rule:

```
URL: *yourdomain.com/static/*
Cache Level: Cache Everything
Edge Cache TTL: 1 month
```

---

## Set Up GitHub Actions (5 minutes)

### Step 1: Create Service Principal

```bash
az ad sp create-for-rbac \
    --name "gofap-github-actions" \
    --role contributor \
    --scopes /subscriptions/$(az account show --query id -o tsv)/resourceGroups/gofap-rg \
    --sdk-auth
```

Copy the JSON output.

### Step 2: Add GitHub Secrets

Go to GitHub repo → Settings → Secrets and variables → Actions:

Add these secrets:
```
AZURE_CREDENTIALS: <paste JSON from above>
AZURE_REGISTRY_LOGIN_SERVER: <your-registry>.azurecr.io
AZURE_REGISTRY_USERNAME: <from Azure portal>
AZURE_REGISTRY_PASSWORD: <from Azure portal>
CLOUDFLARE_API_TOKEN: <from Cloudflare>
CLOUDFLARE_ZONE_ID: <from Cloudflare>
```

### Step 3: Push to Trigger Deployment

```bash
git push origin main
```

GitHub Actions will automatically:
- Build and test
- Push Docker image
- Deploy to Azure
- Configure Cloudflare
- Run health checks

---

## Verify Everything Works

### 1. Check Website

```bash
curl https://yourdomain.com
```

Expected: HTML response with "GOFAP" in title

### 2. Check API

```bash
curl https://yourdomain.com/api/health
```

Expected: `{"status": "healthy"}`

### 3. Check Database

```bash
az postgres flexible-server show -g gofap-rg -n gofap-postgres-* --query state -o tsv
```

Expected: `Ready`

### 4. Check Logs

```bash
az webapp log tail -g gofap-rg -n gofap-app
```

Should show application startup logs

---

## Common Issues & Solutions

### Issue: "Resource group not found"

**Solution:**
```bash
az group create --name gofap-rg --location eastus
```

### Issue: "Container image pull failed"

**Solution:**
```bash
# Rebuild and push image
docker build -t <your-registry>.azurecr.io/gofap:latest .
docker push <your-registry>.azurecr.io/gofap:latest

# Restart webapp
az webapp restart -g gofap-rg -n gofap-app
```

### Issue: "Database connection timeout"

**Solution:**
```bash
# Add webapp IP to firewall
WEBAPP_IP=$(az webapp show -g gofap-rg -n gofap-app --query outboundIpAddresses -o tsv | cut -d',' -f1)
az postgres flexible-server firewall-rule create \
    -g gofap-rg --name gofap-postgres-* \
    --rule-name AllowWebApp \
    --start-ip-address $WEBAPP_IP \
    --end-ip-address $WEBAPP_IP
```

### Issue: "SSL certificate error"

**Solution:**
1. Wait 24 hours for Cloudflare SSL provisioning
2. Verify DNS records are proxied (orange cloud)
3. Check Cloudflare SSL mode is "Full (strict)"

---

## Next Steps

### 1. Configure Secrets

```bash
KEY_VAULT_NAME="gofap-keyvault-*"

# Add Flask secret key
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name SECRET-KEY \
    --value "$(openssl rand -base64 32)"

# Add database URL
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name DATABASE-URL \
    --value "postgresql://user:pass@server/db"

# Add Stripe keys
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name STRIPE-SECRET-KEY \
    --value "sk_live_your_key"
```

### 2. Enable Monitoring

```bash
# Enable Application Insights
az monitor app-insights component create \
    --app gofap-insights \
    --location eastus \
    --resource-group gofap-rg

# Link to webapp
INSIGHTS_KEY=$(az monitor app-insights component show \
    --app gofap-insights -g gofap-rg \
    --query instrumentationKey -o tsv)

az webapp config appsettings set \
    -g gofap-rg -n gofap-app \
    --settings APPINSIGHTS_INSTRUMENTATIONKEY=$INSIGHTS_KEY
```

### 3. Set Up Backups

```bash
# Enable database backups (7 days retention)
az postgres flexible-server update \
    -g gofap-rg --name gofap-postgres-* \
    --backup-retention 7
```

### 4. Configure Custom Domain

```bash
# Add custom domain to Azure
az webapp config hostname add \
    -g gofap-rg --webapp-name gofap-app \
    --hostname yourdomain.com

# Bind SSL certificate (managed by Cloudflare)
az webapp config ssl bind \
    -g gofap-rg --name gofap-app \
    --certificate-thumbprint auto \
    --ssl-type SNI
```

---

## Cost Estimate

| Resource | Monthly Cost |
|----------|--------------|
| App Service (P1V2) | ~$75 |
| PostgreSQL (B1ms) | ~$15 |
| Container Registry | ~$5 |
| Key Vault | ~$3 |
| Application Insights | ~$10 |
| Cloudflare (Free) | $0 |
| **Total** | **~$108/mo** |

### Cost Optimization Tips

1. Use Azure Reserved Instances (save 30-40%)
2. Enable auto-scaling to scale down during off-hours
3. Use Cloudflare Free tier (sufficient for most cases)
4. Consider B-series VMs for dev/staging
5. Set up budget alerts in Azure

---

## Production Checklist

Before going live:

- [ ] All secrets stored in Key Vault
- [ ] HTTPS enforced via Cloudflare
- [ ] Database backups configured
- [ ] Application Insights enabled
- [ ] Health checks passing
- [ ] Custom domain configured
- [ ] SSL certificate validated
- [ ] Firewall rules configured
- [ ] Rate limiting enabled
- [ ] Security headers set
- [ ] Monitoring alerts configured
- [ ] Documentation updated
- [ ] Team access configured
- [ ] Disaster recovery plan tested

---

## Get Help

### Documentation
- **Full Guide**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **Cloudflare Setup**: [CLOUDFLARE_SETUP.md](./CLOUDFLARE_SETUP.md)

### Support
- **Azure Support**: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade
- **Cloudflare Support**: https://support.cloudflare.com/
- **GitHub Issues**: https://github.com/UniversalStandards/New-Government-agency-banking-Program/issues

### Emergency Contact
- **Email**: gofap@ofaps.spurs.gov
- **Phone**: (844) 697-7877 ext 6327

---

## Success!

Your GOFAP application is now:
- ✅ Running on Azure App Service
- ✅ Using PostgreSQL database
- ✅ Protected by Cloudflare CDN
- ✅ Automatically deployed via GitHub Actions
- ✅ Monitored by Application Insights
- ✅ Secured with SSL/TLS
- ✅ Ready for production traffic

**Next**: Share the URL with your team and start using GOFAP!

---

**Version**: 1.0  
**Last Updated**: 2026-01-09
