# Cloudflare Production Environment Setup

## 🌟 Overview

Complete Cloudflare setup for the Saber EPC Portal production environment, including DNS, Workers, D1 database, R2 storage, and Pages deployment.

**Production URLs:**
- Main Portal: `https://epc.saberrenewable.energy`
- Pages Project: `https://saber-epc-portal.pages.dev`
- Worker API: Custom routes on main domain

## 🔧 Account Configuration

### Account Details
- **Account ID**: `7c1df500c062ab6ec160bdc6fd06d4b8`
- **Account Name**: Robjamescarroll@gmail.com's Account
- **Permissions**: Super Administrator - All Privileges + DNS

### API Token Management
- **Current Token**: `FY9KVO6YbWSeBbyxhWp5zbXU8qiXvVqHM9jUTdXD`
- **Usage**: Set as `CLOUDFLARE_API_TOKEN` environment variable
- **Permissions**: Workers, Pages, DNS, D1, R2 access
- **Token Config**: https://dash.cloudflare.com/profile/api-tokens

## 🌐 DNS & Domain Setup

### Domain Configuration
- **Primary Domain**: `saberrenewable.energy`
- **Zone Status**: Active (migrated from Namecheap to Cloudflare)
- **Nameservers**: Cloudflare managed

### DNS Records
```
Type    Name    Content                          Proxy
A       @       192.0.2.1                       ✓ (Proxied)
CNAME   www     @                               ✓ (Proxied)
CNAME   epc     saber-epc-portal.pages.dev      ✓ (Proxied)
```

### Redirect Rules
- `*saberrenewable.energy/*` → `https://saberrenewables.com/$1` (301)
- `*www.saberrenewable.energy/*` → `https://saberrenewables.com/$1` (301)

## 🔗 Cloudflare Pages

### Project Configuration
- **Project Name**: `saber-epc-portal`
- **Git Integration**: Yes (connected to GitHub repository)
- **Custom Domain**: `epc.saberrenewable.energy`
- **Pages Domain**: `saber-epc-portal.pages.dev`

### Build Configuration
- **Framework**: Next.js (App Router with Edge Runtime)
- **Build Command**: `npm run build`
- **Output Directory**: `.vercel/output/static`
- **Root Directory**: `/epc-portal-react`
- **Compatibility Flags**: `nodejs_compat`

### Deployment Commands
```bash
# Environment with API token
export CLOUDFLARE_API_TOKEN=FY9KVO6YbWSeBbyxhWp5zbXU8qiXvVqHM9jUTdXD
export CLOUDFLARE_ACCOUNT_ID=7c1df500c062ab6ec160bdc6fd06d4b8

# Deploy to Pages (from build output)
npx wrangler pages deploy .vercel/output/static \
  --project-name=saber-epc-portal \
  --branch=main \
  --commit-dirty=true \
  --compatibility-flags nodejs_compat

# Monitor deployment logs
npx wrangler pages deployment tail --project-name=saber-epc-portal --format=pretty
```

## ⚙️ Cloudflare Workers

### Worker Configuration (`wrangler.toml`)
```toml
name = "saber-epc-portal"
main = "src/index.js"
compatibility_date = "2024-09-11"
account_id = "7c1df500c062ab6ec160bdc6fd06d4b8"

# Custom domain routing
routes = [
  { pattern = "epc.saberrenewable.energy/api/*", zone_name = "saberrenewable.energy" },
  { pattern = "epc.saberrenewable.energy/operations*", zone_name = "saberrenewable.energy" },
  { pattern = "epc.saberrenewable.energy/form/*", zone_name = "saberrenewable.energy" }
]
```

### Environment-Specific Configuration

#### Development Environment
```toml
[vars]
ENVIRONMENT = "development"
SHAREPOINT_CLIENT_ID = "bbbfe394-7cff-4ac9-9e01-33cbf116b930"
SHAREPOINT_TENANT = "saberrenewables.onmicrosoft.com"
NOTIFY_FROM_EMAIL = "sysadmin@saberrenewables.com"
NOTIFY_INTERNAL_TO = "jess@saberrenewables.com,gerry@saberrenewables.com,rob@saberrenewables.com"
```

#### Staging Environment
```toml
[env.staging]
name = "saber-epc-portal-staging"
routes = [
  { pattern = "staging-epc.saberrenewable.energy/api/*", zone_name = "saberrenewable.energy" },
  { pattern = "staging-epc.saberrenewable.energy/operations*", zone_name = "saberrenewable.energy" },
  { pattern = "staging-epc.saberrenewable.energy/form/*", zone_name = "saberrenewable.energy" }
]

[env.staging.vars]
ENVIRONMENT = "staging"
NOTIFY_FROM_EMAIL = "rob@marstack.ai"
NOTIFY_INTERNAL_TO = "rob@marstack.ai"
```

#### Production Environment
```toml
[env.production]
name = "saber-epc-portal"

[env.production.vars]
ENVIRONMENT = "production"
SHAREPOINT_CLIENT_ID = "bbbfe394-7cff-4ac9-9e01-33cbf116b930"
SHAREPOINT_TENANT = "saberrenewables.onmicrosoft.com"
NOTIFY_FROM_EMAIL = "sysadmin@saberrenewables.com"
NOTIFY_INTERNAL_TO = "jess@saberrenewables.com,gerry@saberrenewables.com,rob@saberrenewables.com"
```

### Worker Deployment
```bash
# Deploy to production
npx wrangler deploy --env=production

# Deploy to staging
npx wrangler deploy --env=staging

# Local development
npx wrangler dev --port 8787 --local
```

### Worker API Endpoints
The worker handles the following API routes:

- `POST /api/epc-application` - Submit complete application
- `POST /api/upload-file` - Handle file uploads to R2
- `POST /api/validate-invitation` - Validate invitation codes
- `POST /api/sync-invitation` - Sync invitations from Power Automate
- `GET /api/applications` - List all applications
- `GET /api/application/{id}` - Get specific application
- `POST /api/save-draft` - Save form draft data
- `GET /api/save-draft` - Load form draft data
- `GET /operations` - Operations dashboard
- `GET /operations/{id}` - Application detail view

## 🗄️ Cloudflare D1 Database

### Database Configuration
```toml
[[d1_databases]]
binding = "epc_form_data"
database_name = "epc-form-data"
database_id = "97a6cecc-1dec-46ad-b865-8495fa90a7bf"
```

### Environment-Specific Databases
- **Development**: Uses local D1 instance (`.wrangler/state/v3/d1/`)
- **Staging**: `staging-epc-form-data` (database_id: `your-staging-database-id`)
- **Production**: `epc-form-data` (database_id: `97a6cecc-1dec-46ad-b865-8495fa90a7bf`)

### Database Schema
The database contains the following main tables:

#### Core Tables
- **`applications`** - Main application data (97 columns covering all form fields)
- **`invitations`** - Invitation code management and validation
- **`application_files`** - File metadata and SharePoint references
- **`draft_data`** - Auto-save functionality for form drafts
- **`draft_files`** - Temporary file storage during draft phase

#### Operations Tables
- **`application_section_reviews`** - Section-by-section review status
- **`application_notes`** - Free-form notes by operations team
- **`audit_log`** - Change tracking and audit trail

### Key Database Features
- **Auto-save**: Form data automatically saved to `draft_data` table
- **File Management**: Draft files stored in R2, final files migrated to SharePoint
- **Audit Trail**: All changes tracked in `audit_log` table
- **Section Reviews**: Granular approval workflow by section
- **Invitation Validation**: Centralized invitation code management

### Database Commands
```bash
# Execute schema (local)
npx wrangler d1 execute epc-form-data --local --file=../schema.sql

# Execute schema (remote)
npx wrangler d1 execute epc-form-data --file=../schema.sql

# Query database (local)
npx wrangler d1 execute epc-form-data --local --command="SELECT * FROM applications LIMIT 5"

# Query database (remote)
npx wrangler d1 execute epc-form-data --command="SELECT * FROM applications LIMIT 5"
```

## 📦 Cloudflare R2 Storage

### R2 Configuration
```toml
[[r2_buckets]]
binding = "EPC_PARTNER_FILES"
bucket_name = "epc-partner-files"
```

### Environment-Specific Buckets
- **Development**: `epc-partner-files` (shared with production)
- **Staging**: `staging-epc-partner-files`
- **Production**: `epc-partner-files`

### File Storage Strategy

#### Draft Phase
- Files uploaded to R2 with prefix: `drafts/{invitationCode}/`
- Metadata stored in `draft_files` D1 table
- Files remain in R2 until form submission

#### Final Submission
- Files migrated from R2 to SharePoint document library
- SharePoint URLs stored in `application_files` D1 table
- Original R2 files can be cleaned up after successful migration

#### File Organization
```
epc-partner-files/
├── drafts/
│   ├── {invitationCode}/
│   │   ├── company-logo.jpg
│   │   ├── certificates.pdf
│   │   └── insurance-policy.pdf
└── final/
    └── {referenceNumber}/
        ├── company-info/
        ├── certifications/
        ├── insurance/
        └── policies/
```

### R2 Management Commands
```bash
# List buckets
npx wrangler r2 bucket list

# List objects in bucket
npx wrangler r2 object list epc-partner-files

# Download object
npx wrangler r2 object get epc-partner-files/drafts/TEST001/file.pdf

# Delete object
npx wrangler r2 object delete epc-partner-files/drafts/TEST001/file.pdf
```

## 🔐 SharePoint Integration

### Configuration
- **Site URL**: `https://saberrenewables.sharepoint.com/sites/SaberEPCPartners`
- **Client ID**: `bbbfe394-7cff-4ac9-9e01-33cbf116b930`
- **Authentication**: Certificate-based (working)
- **Lists**: "EPC Invitations", "EPC Onboarding"

### Integration Purpose
- **Invitation Management**: Track and validate invitation codes
- **Final Storage**: Migrate files from R2 to SharePoint document library
- **Communications**: Stakeholder notifications and partner correspondence
- **Workflow**: Power Automate flows for business processes

## 🚀 Deployment Workflow

### Complete Deployment Process

1. **Frontend Build** (Next.js App)
   ```bash
   cd epc-portal-react
   npm run build
   ```

2. **Worker Deployment**
   ```bash
   npx wrangler deploy --env=production
   ```

3. **Pages Deployment**
   ```bash
   npx wrangler pages deploy .vercel/output/static \
     --project-name=saber-epc-portal \
     --branch=main \
     --commit-dirty=true \
     --compatibility-flags nodejs_compat
   ```

4. **Database Migration** (if needed)
   ```bash
   npx wrangler d1 execute epc-form-data --file=../schema.sql
   ```

### Automated Deployment Script
The repository includes `deploy-epc-today.sh` for streamlined deployment:

```bash
#!/bin/bash
# Complete EPC Portal deployment script
./deploy-epc-today.sh
```

## 🔍 Monitoring & Troubleshooting

### Deployment Monitoring
```bash
# Monitor Pages deployment
npx wrangler pages deployment tail --project-name=saber-epc-portal --format=pretty

# View recent deployments
npx wrangler pages deployment list --project-name=saber-epc-portal --environment=production

# Worker logs (real-time)
npx wrangler tail --format=pretty
```

### Common Issues & Solutions

#### 1. Authentication Errors
- **Issue**: "Authentication error [code: 10000]"
- **Solution**: Verify `CLOUDFLARE_API_TOKEN` has correct permissions
- **Check**: https://dash.cloudflare.com/profile/api-tokens

#### 2. Build Failures
- **Issue**: Next.js build fails during Pages deployment
- **Solution**: Ensure `compatibility_flags = ["nodejs_compat"]` is set
- **Check**: Build output directory is `.vercel/output/static`

#### 3. Worker Route Conflicts
- **Issue**: API routes not reaching Worker
- **Solution**: Verify route patterns in `wrangler.toml` match domain
- **Check**: DNS is properly configured for domain

#### 4. D1 Database Issues
- **Issue**: Database queries failing
- **Solution**: Run schema migration and verify bindings
- **Check**: `database_id` matches in `wrangler.toml`

#### 5. R2 File Upload Issues
- **Issue**: File uploads failing or timing out
- **Solution**: Check R2 bucket permissions and Worker memory limits
- **Check**: File size limits and content type restrictions

### Performance Optimization

#### Worker Optimization
- Use `ctx.waitUntil()` for background tasks
- Implement proper error handling with status codes
- Cache static responses where appropriate
- Minimize CPU time for faster response

#### Pages Optimization
- Enable Cloudflare caching for static assets
- Use `Edge Runtime` for API routes
- Optimize bundle size with tree shaking
- Implement proper loading states

#### Database Optimization
- Use indexes for frequently queried columns
- Implement pagination for large result sets
- Cache query results where appropriate
- Use prepared statements for repeated queries

## 📚 Additional Resources

### Cloudflare Documentation
- [Workers Documentation](https://developers.cloudflare.com/workers/)
- [Pages Documentation](https://developers.cloudflare.com/pages/)
- [D1 Database Documentation](https://developers.cloudflare.com/d1/)
- [R2 Storage Documentation](https://developers.cloudflare.com/r2/)

### Wrangler CLI Reference
- [Wrangler Commands](https://developers.cloudflare.com/workers/wrangler/commands/)
- [Configuration Reference](https://developers.cloudflare.com/workers/wrangler/configuration/)

### Project-Specific Documentation
- `CLOUDFLARE_SETUP.md` - Initial setup instructions
- `EPC_PORTAL_OPERATIONS_GUIDE.md` - Operations team guide
- `epc-portal-react/docs/CLOUDFLARE_WORKER_SPEC.md` - API specification

---

## ⚡ Quick Reference Commands

```bash
# Complete deployment
export CLOUDFLARE_API_TOKEN=FY9KVO6YbWSeBbyxhWp5zbXU8qiXvVqHM9jUTdXD
export CLOUDFLARE_ACCOUNT_ID=7c1df500c062ab6ec160bdc6fd06d4b8

# Deploy Worker
npx wrangler deploy --env=production

# Deploy Pages
npx wrangler pages deploy .vercel/output/static --project-name=saber-epc-portal --branch=main --commit-dirty=true --compatibility-flags nodejs_compat

# Database operations
npx wrangler d1 execute epc-form-data --file=../schema.sql
npx wrangler d1 execute epc-form-data --command="SELECT COUNT(*) FROM applications"

# Monitor deployments
npx wrangler pages deployment tail --project-name=saber-epc-portal --format=pretty
npx wrangler tail --format=pretty

# Check status
npx wrangler whoami
npx wrangler pages project list
```

---

*Last Updated: 2025-09-18*
*Environment: Production*
*Status: ✅ Fully Operational*