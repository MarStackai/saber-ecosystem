# Azure Infrastructure Setup Guide

## Overview

This guide provides step-by-step instructions for setting up the Azure infrastructure for the Saber Business Operations Platform based on the Azure Deployment Architecture specification.

## Prerequisites

- Azure subscription with appropriate permissions
- Azure CLI installed and configured
- PowerShell 7+ installed (for PowerShell scripts)
- Appropriate Azure permissions to create resources

## Phase 1: Foundation Setup (Weeks 1-2)

### 1.1 Azure Subscription Setup

#### Management Groups Configuration

```bash
# Create management groups
az account management-group create --name "Saber-Renewable-Energy"
az account management-group create --name "Production-Environment" --parent "Saber-Renewable-Energy"
az account management-group create --name "Staging-Environment" --parent "Saber-Renewable-Energy"
az account management-group create --name "Development-Environment" --parent "Saber-Renewable-Energy"
az account management-group create --name "Shared-Services" --parent "Saber-Renewable-Energy"

# Assign subscription to management groups
az account management-group subscription add --name "Production-Environment" --subscription <your-subscription-id>
```

#### Resource Groups Creation

```bash
# Set Azure region
REGION="uksouth"

# Production Resource Groups
az group create --name "saber-prod-rg-webapp" --location $REGION
az group create --name "saber-prod-rg-database" --location $REGION
az group create --name "saber-prod-rg-storage" --location $REGION
az group create --name "saber-prod-rg-networking" --location $REGION
az group create --name "saber-prod-rg-ai" --location $REGION
az group create --name "saber-prod-rg-monitoring" --location $REGION

# Staging Resource Groups
az group create --name "saber-staging-rg-webapp" --location $REGION
az group create --name "saber-staging-rg-database" --location $REGION
az group create --name "saber-staging-rg-storage" --location $REGION
az group create --name "saber-staging-rg-networking" --location $REGION
az group create --name "saber-staging-rg-ai" --location $REGION
az group create --name "saber-staging-rg-monitoring" --location $REGION

# Development Resource Groups
az group create --name "saber-dev-rg-webapp" --location $REGION
az group create --name "saber-dev-rg-database" --location $REGION
az group create --name "saber-dev-rg-storage" --location $REGION
az group create --name "saber-dev-rg-networking" --location $REGION
az group create --name "saber-dev-rg-ai" --location $REGION
az group create --name "saber-dev-rg-monitoring" --location $REGION
```

### 1.2 Virtual Network Deployment

#### Hub and Spoke Network Topology

```bash
# Create Hub VNet
az network vnet create \
  --resource-group "saber-prod-rg-networking" \
  --name "saber-hub-vnet" \
  --address-prefix "10.0.0.0/16" \
  --location $REGION

# Create Hub Subnets
az network vnet subnet create \
  --resource-group "saber-prod-rg-networking" \
  --vnet-name "saber-hub-vnet" \
  --name "GatewaySubnet" \
  --address-prefix "10.0.0.0/24"

az network vnet subnet create \
  --resource-group "saber-prod-rg-networking" \
  --vnet-name "saber-hub-vnet" \
  --name "AzureFirewallSubnet" \
  --address-prefix "10.0.1.0/24"

az network vnet subnet create \
  --resource-group "saber-prod-rg-networking" \
  --vnet-name "saber-hub-vnet" \
  --name "SharedServicesSubnet" \
  --address-prefix "10.0.2.0/24"

az network vnet subnet create \
  --resource-group "saber-prod-rg-networking" \
  --vnet-name "saber-hub-vnet" \
  --name "ManagementSubnet" \
  --address-prefix "10.0.3.0/24"

# Create Spoke VNets
az network vnet create \
  --resource-group "saber-prod-rg-networking" \
  --name "saber-webapp-vnet" \
  --address-prefix "10.1.0.0/16" \
  --location $REGION

az network vnet create \
  --resource-group "saber-prod-rg-networking" \
  --name "saber-database-vnet" \
  --address-prefix "10.2.0.0/16" \
  --location $REGION

az network vnet create \
  --resource-group "saber-prod-rg-networking" \
  --name "saber-ai-vnet" \
  --address-prefix "10.3.0.0/16" \
  --location $REGION

az network vnet create \
  --resource-group "saber-prod-rg-networking" \
  --name "saber-storage-vnet" \
  --address-prefix "10.4.0.0/16" \
  --location $REGION

# Create VNet Peerings
az network vnet peering create \
  --resource-group "saber-prod-rg-networking" \
  --name "hub-to-webapp" \
  --vnet-name "saber-hub-vnet" \
  --remote-vnet "saber-webapp-vnet" \
  --allow-vnet-access

az network vnet peering create \
  --resource-group "saber-prod-rg-networking" \
  --name "webapp-to-hub" \
  --vnet-name "saber-webapp-vnet" \
  --remote-vnet "saber-hub-vnet" \
  --allow-vnet-access

# Repeat for other spoke VNets...
```

### 1.3 Basic Security Configuration

#### Network Security Groups

```bash
# Create NSG for Web App Subnet
az network nsg create \
  --resource-group "saber-prod-rg-networking" \
  --name "saber-webapp-nsg" \
  --location $REGION

# Add NSG rules
az network nsg rule create \
  --resource-group "saber-prod-rg-networking" \
  --nsg-name "saber-webapp-nsg" \
  --name "AllowHTTPS" \
  --protocol "Tcp" \
  --direction "Inbound" \
  --priority 1000 \
  --source-address-prefixes "*" \
  --source-port-ranges "*" \
  --destination-address-prefixes "*" \
  --destination-port-ranges "443" \
  --access "Allow"

az network nsg rule create \
  --resource-group "saber-prod-rg-networking" \
  --nsg-name "saber-webapp-nsg" \
  --name "AllowHTTP" \
  --protocol "Tcp" \
  --direction "Inbound" \
  --priority 1100 \
  --source-address-prefixes "*" \
  --source-port-ranges "*" \
  --destination-address-prefixes "*" \
  --destination-port-ranges "80" \
  --access "Allow"

# Associate NSG with subnet
az network vnet subnet update \
  --resource-group "saber-prod-rg-networking" \
  --vnet-name "saber-webapp-vnet" \
  --name "default" \
  --network-security-group "saber-webapp-nsg"

# Create similar NSGs for other subnets...
```

### 1.4 Monitoring Setup

#### Log Analytics Workspace

```bash
# Create Log Analytics Workspace
az monitor log-analytics workspace create \
  --resource-group "saber-prod-rg-monitoring" \
  --name "saber-law-prod" \
  --location $REGION

# Create Application Insights
az monitor app-insights component create \
  --resource-group "saber-prod-rg-monitoring" \
  --app "saber-appinsights-prod" \
  --location $REGION \
  --application-type "web"
```

## Phase 2: Core Infrastructure (Weeks 3-4)

### 2.1 Storage Account Setup

```bash
# Create Storage Account
az storage account create \
  --resource-group "saber-prod-rg-storage" \
  --name "saberstorageprod" \
  --location $REGION \
  --sku "Standard_RAGRS" \
  --kind "StorageV2" \
  --hierarchical-namespace true \
  --enable-large-file-share true

# Create Blob Containers
az storage container create \
  --account-name "saberstorageprod" \
  --name "documents" \
  --public-access "off"

az storage container create \
  --account-name "saberstorageprod" \
  --name "images" \
  --public-access "off"

az storage container create \
  --account-name "saberstorageprod" \
  --name "backups" \
  --public-access "off"

# Create File Shares
az storage share create \
  --account-name "saberstorageprod" \
  --name "shared-files" \
  --quota 100

az storage share create \
  --account-name "saberstorageprod" \
  --name "reports" \
  --quota 100
```

### 2.2 Database Setup

```bash
# Create SQL Server
az sql server create \
  --resource-group "saber-prod-rg-database" \
  --name "saber-sql-server-prod" \
  --location $REGION \
  --admin-user "saberadmin" \
  --admin-password "<secure-password>" \

# Create SQL Database
az sql db create \
  --resource-group "saber-prod-rg-database" \
  --server "saber-sql-server-prod" \
  --name "saber-sqldb-prod" \
  --edition "GeneralPurpose" \
  --family "Gen5" \
  --capacity 8 \
  --zone-redundant true

# Configure Firewall Rules
az sql server firewall-rule create \
  --resource-group "saber-prod-rg-database" \
  --server "saber-sql-server-prod" \
  --name "AllowAzureIPs" \
  --start-ip-address "0.0.0.0" \
  --end-ip-address "0.0.0.0"

# Create Cosmos DB Account
az cosmosdb create \
  --resource-group "saber-prod-rg-database" \
  --name "saber-cosmos-prod" \
  --locations "UKSouth=0" "UKWest=1" \
  --default-consistency-level "Session" \
  --enable-multiple-write-locations true

# Create Redis Cache
az redis create \
  --resource-group "saber-prod-rg-database" \
  --name "saber-redis-prod" \
  --location $REGION \
  --sku "Premium" \
  --vm-size "P3" \
  --enable-non-ssl-port false \
  --shard-count 3
```

### 2.3 Application Services Setup

```bash
# Create App Service Plan
az appservice plan create \
  --resource-group "saber-prod-rg-webapp" \
  --name "saber-asp-prod" \
  --location $REGION \
  --sku "P3v2" \
  --number-of-workers 4 \
  --zone-redundant true

# Create Web App
az webapp create \
  --resource-group "saber-prod-rg-webapp" \
  --name "saber-webapp-prod" \
  --plan "saber-asp-prod" \
  --runtime "NODE:18-lts"

# Configure Web App
az webapp config appsettings set \
  --resource-group "saber-prod-rg-webapp" \
  --name "saber-webapp-prod" \
  --settings "WEBSITE_NODE_DEFAULT_VERSION=18.17.1"

# Create API App
az webapp create \
  --resource-group "saber-prod-rg-webapp" \
  --name "saber-api-prod" \
  --plan "saber-asp-prod" \
  --runtime "DOTNETCORE:8.0"
```

## Phase 3: Advanced Services (Weeks 5-6)

### 3.1 AI Services Setup

```bash
# Create Cognitive Services Account
az cognitiveservices account create \
  --resource-group "saber-prod-rg-ai" \
  --name "saber-cognitive-prod" \
  --location $REGION \
  --kind "CognitiveServices" \
  --sku "S0" \
  --custom-domain "saber-cognitive-prod" \
  --yes

# Create OpenAI Service
az cognitiveservices account create \
  --resource-group "saber-prod-rg-ai" \
  --name "saber-openai-prod" \
  --location $REGION \
  --kind "OpenAI" \
  --sku "S0" \
  --yes

# Deploy GPT-4 Model
az cognitiveservices account deployment create \
  --resource-group "saber-prod-rg-ai" \
  --name "saber-openai-prod" \
  --deployment-name "gpt-4" \
  --model-name "gpt-4" \
  --model-version "0613" \
  --model-format "OpenAI" \
  --scale-capacity 10 \
  --scale-type "Standard"
```

### 3.2 Container Registry Setup

```bash
# Create Container Registry
az acr create \
  --resource-group "saber-prod-rg-ai" \
  --name "saberacrprod" \
  --location $REGION \
  --sku "Premium" \
  --enable-admin-user true

# Get ACR credentials
ACR_PASSWORD=$(az acr credential show --resource-group "saber-prod-rg-ai" --name "saberacrprod" --query "passwords[0].value" --output tsv)

# Login to ACR
az acr login --name "saberacrprod"
```

## Verification Steps

### 1. Resource Verification

```bash
# List all created resource groups
az group list --output table

# List all resources in production resource groups
az resource list --resource-group "saber-prod-rg-webapp" --output table
az resource list --resource-group "saber-prod-rg-database" --output table
az resource list --resource-group "saber-prod-rg-storage" --output table
az resource list --resource-group "saber-prod-rg-networking" --output table
az resource list --resource-group "saber-prod-rg-ai" --output table
az resource list --resource-group "saber-prod-rg-monitoring" --output table
```

### 2. Network Connectivity Verification

```bash
# Test VNet peering connections
az network vnet peering list --resource-group "saber-prod-rg-networking" --vnet-name "saber-hub-vnet" --output table

# Test NSG rules
az network nsg rule list --resource-group "saber-prod-rg-networking" --nsg-name "saber-webapp-nsg" --output table
```

### 3. Application Services Verification

```bash
# Test web app
curl https://saber-webapp-prod.azurewebsites.net

# Test API app
curl https://saber-api-prod.azurewebsites.net/health

# Check app service plan status
az appservice plan show --resource-group "saber-prod-rg-webapp" --name "saber-asp-prod" --output table
```

### 4. Database Connectivity Verification

```bash
# Test SQL Server connection
az sql db show --resource-group "saber-prod-rg-database" --server "saber-sql-server-prod" --name "saber-sqldb-prod" --output table

# Test Cosmos DB connection
az cosmosdb show --resource-group "saber-prod-rg-database" --name "saber-cosmos-prod" --output table

# Test Redis Cache connection
az redis show --resource-group "saber-prod-rg-database" --name "saber-redis-prod" --output table
```

## Next Steps

1. **Configure CI/CD Pipeline**: Set up Azure DevOps pipeline for automated deployments
2. **Implement Monitoring**: Configure detailed monitoring and alerting
3. **Security Hardening**: Implement advanced security controls
4. **Backup Configuration**: Set up automated backup policies
5. **Documentation**: Create detailed operational documentation

## Troubleshooting

### Common Issues

1. **Resource Creation Failures**: Check Azure quotas and permissions
2. **Network Connectivity Issues**: Verify VNet peering and NSG rules
3. **Database Connection Issues**: Check firewall rules and connection strings
4. **Application Deployment Issues**: Verify app service configuration and deployment settings

### Support Resources

- [Azure Documentation](https://docs.microsoft.com/azure/)
- [Azure Portal](https://portal.azure.com/)
- [Azure CLI Reference](https://docs.microsoft.com/cli/azure/)
- [Azure Status](https://status.azure.com/)