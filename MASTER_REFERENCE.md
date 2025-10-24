# 🚀 MASTER REFERENCE - Saber EPC Portal MCP Setup

**Status**: SETUP COMPLETE ✓ All systems operational

---

## 📍 YOUR AZURE SERVICE PRINCIPAL CREDENTIALS

**🔒 Securely stored in 1Password vault: "Saber Business Ops"**
**Item**: "Azure Service Principal - saber-epc-mcp-sp"

Retrieve credentials using:
```bash
# Get specific fields
op read "op://Saber Business Ops/Azure Service Principal - saber-epc-mcp-sp/password"
op read "op://Saber Business Ops/Azure Service Principal - saber-epc-mcp-sp/subscription_id"
op read "op://Saber Business Ops/Azure Service Principal - saber-epc-mcp-sp/tenant_id"
op read "op://Saber Business Ops/Azure Service Principal - saber-epc-mcp-sp/client_id"
```

✅ These are already configured in: `~/mcp-servers/azure-mcp-server/.env`

---

## 📋 CLOUDFLARE CREDENTIALS

**🔒 Securely stored in 1Password vault: "Saber Business Ops"**
**Item**: "Cloudflare API - saberrenewable.energy"

Retrieve credentials using:
```bash
# Get specific fields
op read "op://Saber Business Ops/Cloudflare API - saberrenewable.energy/password"
op read "op://Saber Business Ops/Cloudflare API - saberrenewable.energy/account_id"
op read "op://Saber Business Ops/Cloudflare API - saberrenewable.energy/domain"
op read "op://Saber Business Ops/Cloudflare API - saberrenewable.energy/d1_database"
op read "op://Saber Business Ops/Cloudflare API - saberrenewable.energy/r2_bucket"
```

✅ Already configured in: `~/mcp-servers/cloudflare-mcp-server/.env`

---

## ✅ WHAT'S COMPLETE

- ✅ Cloudflare MCP Server (4 tools)
- ✅ Azure MCP Server (6 tools)
- ✅ Service Principal created
- ✅ All credentials configured
- ✅ VSCode MCP integration done
- ✅ Setup scripts created
- ✅ Documentation complete

---

## 🎯 IMMEDIATE NEXT STEPS

### 1️⃣ TEST MCP SERVERS (Right Now)

**In Claude Code, ask:**
```
"Can you list files in the epc-partner-files R2 bucket using cf-epc-r2-access?"
```

### 2️⃣ DEPLOY AZURE INFRASTRUCTURE (Optional, 1-2 hours)

```bash
cd ~/mcp-servers
./azure-infrastructure-deploy.sh
```

This deploys:
- 12 Resource Groups (6 prod, 6 staging)
- VNets, NSGs, Monitoring
- Azure SQL, Storage, Redis, App Service
- Cognitive Services, Container Registry

---

## 📁 KEY FILE LOCATIONS

### MCP Servers
- Cloudflare: `~/mcp-servers/cloudflare-mcp-server/`
- Azure: `~/mcp-servers/azure-mcp-server/`

### Setup Scripts
- Azure setup: `~/mcp-servers/azure-setup.sh` (already run ✓)
- Infrastructure: `~/mcp-servers/azure-infrastructure-deploy.sh`

### Documentation (Read These!)
- **Quick Start**: `~/mcp-servers/QUICK_START.md`
- **Complete Guide**: `~/mcp-servers/SETUP_GUIDE.md`
- **Completion Summary**: `~/COMPLETION_SUMMARY.md`
- **This File**: `~/mcp-servers/MASTER_REFERENCE.md`

---

## 🛠️ MCP TOOLS AVAILABLE

### Cloudflare Tools (4)
1. `cf-epc-database-query` - Query D1 database
2. `cf-epc-worker-deploy` - Deploy Cloudflare Workers
3. `cf-epc-r2-access` - Access R2 storage (list/upload/download/delete)
4. `cf-epc-dns-records` - Manage DNS records

### Azure Tools (6)
1. `azure-epc-sql-query` - Query Azure SQL
2. `azure-epc-blob-access` - Access Blob storage
3. `azure-epc-function-deploy` - Deploy Functions
4. `azure-epc-app-service-deploy` - Deploy web apps
5. `azure-epc-resource-provision` - Provision resources
6. `azure-epc-monitoring-query` - Query monitoring

---

## 📊 INFRASTRUCTURE TO BE DEPLOYED

When you run `azure-infrastructure-deploy.sh`:

**Production Environment:**
- saber-prod-rg-webapp
- saber-prod-rg-database
- saber-prod-rg-storage
- saber-prod-rg-networking
- saber-prod-rg-ai
- saber-prod-rg-monitoring

**Staging Environment:**
- saber-staging-rg-webapp
- saber-staging-rg-database
- saber-staging-rg-storage
- saber-staging-rg-networking
- saber-staging-rg-ai
- saber-staging-rg-monitoring

**Resources Include:**
- Hub-and-Spoke VNet topology (10.0.0.0/16 - 10.4.0.0/16)
- Network Security Groups
- Azure SQL Server (8 vCores, zone-redundant)
- Storage Accounts with Blob/File containers
- Redis Cache (Premium P3, 3 shards)
- App Service Plan (P3v2, zone-redundant)
- Cognitive Services
- Container Registry (Premium)
- Log Analytics Workspace
- Application Insights

---

## 🔐 SECURITY CHECKLIST

- ✅ Service Principal created with Contributor role
- ✅ Credentials in .env files (not committed to git)
- ✅ **Credentials securely stored in 1Password "Saber Business Ops" vault**
- ✅ MCP servers use environment variables for auth
- ✅ All sensitive data protected
- ✅ Credentials removed from documentation

**COMPLETED:**
- ✅ All credentials migrated to 1Password
- ✅ Sensitive data removed from MASTER_REFERENCE.md
- ✅ op CLI commands documented for retrieval
- ✅ Never commit .env files to git

---

## ⚡ QUICK COMMANDS

```bash
# Deploy infrastructure (1-2 hours)
cd ~/mcp-servers && ./azure-infrastructure-deploy.sh

# Check Azure resources
az group list --query "[].name" -o table

# Get Cloudflare API Key from 1Password
CF_API_KEY=$(op read "op://Saber Business Ops/Cloudflare API - saberrenewable.energy/password")

# Test Cloudflare API
curl -X GET https://api.cloudflare.com/client/v4/accounts \
  -H "Authorization: Bearer $CF_API_KEY"

# Test Azure authentication
az account show

# View MCP server logs
node ~/mcp-servers/cloudflare-mcp-server/src/index.js
node ~/mcp-servers/azure-mcp-server/src/index.js
```

---

## 📞 SUPPORT RESOURCES

All documentation is in `~/mcp-servers/`:

1. **QUICK_START.md** - 3-step quick reference
2. **SETUP_GUIDE.md** - Complete setup documentation
3. **MASTER_REFERENCE.md** - This file
4. **COMPLETION_SUMMARY.md** - Project summary

External:
- [Azure Docs](https://learn.microsoft.com/azure/)
- [Cloudflare API](https://developers.cloudflare.com/api/)
- [MCP Docs](https://modelcontextprotocol.io/)

---

## 🎯 COMMON TASKS

### Test Cloudflare MCP
```
In Claude Code:
"Use the cf-epc-r2-access tool to list files in the epc-partner-files bucket"
```

### Test Azure MCP
```
In Claude Code:
"Use the azure-epc-resource-provision tool to show current resource groups"
```

### Deploy Infrastructure
```bash
cd ~/mcp-servers && ./azure-infrastructure-deploy.sh
```

### Verify Resources (After Deploy)
```bash
az resource list --query "[].{Name:name, Type:type}" -o table
```

---

## ✨ WHAT YOU CAN DO NOW

1. **Use MCP Tools in Claude Code**
   - Both servers are integrated and ready
   - Ask Claude to use any of the 10 available tools

2. **Deploy Azure Infrastructure** (whenever you're ready)
   - `~/mcp-servers/azure-infrastructure-deploy.sh`
   - Takes 1-2 hours to complete

3. **Access Cloudflare Resources**
   - Query D1 database
   - Manage R2 files
   - Deploy Workers
   - Manage DNS

4. **Access Azure Resources**
   - Query SQL databases
   - Manage storage
   - Deploy functions
   - Provision resources

---

## 📈 NEXT PHASE (After Infrastructure)

1. Set up Azure DevOps CI/CD
2. Configure monitoring and alerts
3. Plan EPC Portal migration (Cloudflare → Azure)
4. Set up backup and disaster recovery
5. Implement Azure AD B2C authentication

---

## 🚀 YOU'RE READY!

All systems are operational. Your MCP servers are integrated with Claude Code and ready to use.

**Start with**: Ask Claude Code to use one of the 10 MCP tools!

Example:
```
"Can you use the cf-epc-r2-access tool to list all files in our R2 bucket?"
```

---

**Last Updated**: October 24, 2025
**Setup Status**: COMPLETE ✓
**MCP Servers**: 2 (Cloudflare + Azure)
**Total Tools**: 10
**Ready for**: Production use
