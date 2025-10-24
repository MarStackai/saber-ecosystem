# EPC Portal Deployment Guide

## Overview

This document describes the deployment process for the Saber EPC Portal across development, staging, and production environments. The portal consists of a Cloudflare Worker (backend API) and Cloudflare Pages (Next.js frontend).

## Environment Structure

### Development
- **URL**: http://localhost:3001 (frontend), http://localhost:8787 (API)
- **Purpose**: Local development and testing
- **Branch**: `development`

### Staging
- **URL**: https://staging-epc.saberrenewable.energy
- **Purpose**: Pre-production testing and validation
- **Branch**: `staging`
- **Worker**: `saber-epc-portal-staging`
- **Pages**: https://staging.saber-epc-portal.pages.dev

### Production
- **URL**: https://epc.saberrenewable.energy
- **Purpose**: Live production environment
- **Branch**: `main`
- **Worker**: `saber-epc-portal`
- **Pages**: https://saber-epc-portal.pages.dev

## Environment Configuration

### Environment Files

The project uses environment-specific configuration files:

- `.env.development` - Development environment variables
- `.env.staging` - Staging environment variables
- `.env.production` - Production environment variables
- `.env.example` - Template for environment files

**Note**: These files are gitignored to protect sensitive data. Use `.env.example` as a template.

### Key Environment Variables

```bash
# Environment identifier
ENVIRONMENT=development|staging|production

# API URLs
API_URL=<environment-specific-api-url>
FRONTEND_URL=<environment-specific-frontend-url>
WORKER_URL=<environment-specific-worker-url>

# Cloudflare Configuration
CLOUDFLARE_ACCOUNT_ID=<your-account-id>
CLOUDFLARE_API_TOKEN=<your-api-token>

# Database and Storage (environment-specific)
D1_DATABASE_ID=<d1-database-id>
R2_BUCKET_PARTNER_FILES=<r2-bucket-name>
R2_BUCKET_DOCUMENTS=<r2-bucket-name>
```

## Deployment Scripts

### Quick Deployment

Use the provided deployment scripts for easy deployment:

```bash
# Development (local)
./scripts/deploy-dev.sh

# Staging
./scripts/deploy-staging.sh

# Production (requires confirmation)
./scripts/deploy-production.sh
```

### Manual Deployment

#### Deploy Worker

```bash
# Staging
npx wrangler deploy --env staging

# Production
npx wrangler deploy --env production
```

#### Deploy Frontend (Pages)

```bash
# Build the application
cd epc-portal-react
npm run build

# Deploy to staging
npx wrangler pages deploy .vercel/output/static \
  --project-name=saber-epc-portal \
  --branch=staging \
  --commit-dirty=true

# Deploy to production
npx wrangler pages deploy .vercel/output/static \
  --project-name=saber-epc-portal \
  --branch=main \
  --commit-dirty=true
```

## Manual Configuration Required

### 1. Worker Routes (Cloudflare Dashboard)

Due to API token limitations, Worker routes must be configured manually in the Cloudflare dashboard:

#### Staging Routes
1. Go to Cloudflare Dashboard → Workers & Pages → `saber-epc-portal-staging`
2. Go to Settings → Triggers → Routes
3. Add these routes:
   - `staging-epc.saberrenewable.energy/api/*`
   - `staging-epc.saberrenewable.energy/operations/*`
   - `staging-epc.saberrenewable.energy/form/*`

#### Production Routes
1. Go to Cloudflare Dashboard → Workers & Pages → `saber-epc-portal`
2. Go to Settings → Triggers → Routes
3. Add these routes:
   - `epc.saberrenewable.energy/api/*`
   - `epc.saberrenewable.energy/operations/*`
   - `epc.saberrenewable.energy/form/*`

### 2. Custom Domains (Pages)

Configure custom domains for the Pages deployment:

#### Staging Domain
1. Go to Cloudflare Dashboard → Workers & Pages → `saber-epc-portal`
2. Go to Custom domains
3. Add: `staging-epc.saberrenewable.energy`
4. Configure to point to staging branch

#### Production Domain
1. Go to Cloudflare Dashboard → Workers & Pages → `saber-epc-portal`
2. Go to Custom domains
3. Add: `epc.saberrenewable.energy`
4. Configure to point to main branch

## GitHub Actions CI/CD

The project includes GitHub Actions workflows for automated deployment:

### Staging Deployment (`.github/workflows/deploy-staging.yml`)
- Triggers on push to `staging` branch
- Automatically deploys Worker and Pages to staging
- Runs health checks after deployment

### Production Deployment (`.github/workflows/deploy-production.yml`)
- Triggers on push to `main` branch
- Automatically deploys Worker and Pages to production
- Runs comprehensive health checks

### Required GitHub Secrets
Configure these secrets in your GitHub repository:
- `CLOUDFLARE_API_TOKEN` - API token with necessary permissions
- `CLOUDFLARE_ACCOUNT_ID` - Your Cloudflare account ID

## Git Workflow

### Branch Strategy

```
main (production)
├── staging (staging environment)
└── development (active development)
```

### Deployment Flow

1. **Development**: Work on `development` branch
2. **Staging**: Merge `development` → `staging` for testing
3. **Production**: Merge `staging` → `main` for production release

### Example Workflow

```bash
# Start new feature
git checkout development
git pull origin development

# Make changes and commit
git add .
git commit -m "Add new feature"

# Deploy to staging
git checkout staging
git merge development
git push origin staging
# Automatic deployment via GitHub Actions

# After testing, deploy to production
git checkout main
git merge staging
git push origin main
# Automatic deployment via GitHub Actions
```

## Troubleshooting

### Common Issues

#### Worker Routes Not Working
- **Issue**: API calls return 404 or wrong Worker responds
- **Solution**: Manually configure routes in Cloudflare dashboard (see Manual Configuration section)

#### API Token Permission Errors
- **Issue**: "Authentication error [code: 10000]" during deployment
- **Solution**: Ensure API token has these permissions:
  - Account: Workers Scripts Edit, D1 Edit, R2 Edit, Pages Edit
  - Zone: Workers Routes Edit, DNS Edit
  - User: User Details Read

#### Pages Custom Domain Not Working
- **Issue**: staging-epc.saberrenewable.energy not responding
- **Solution**: Add custom domain in Cloudflare Pages settings

### Verification Steps

After deployment, verify the environment:

```bash
# Check Worker health
curl https://staging-epc.saberrenewable.energy/api/health

# Check frontend
curl -I https://staging-epc.saberrenewable.energy

# Check specific API endpoint
curl https://staging-epc.saberrenewable.energy/api/admin/projects
```

## Rollback Procedures

### Quick Rollback

```bash
# Revert last commit
git revert HEAD
git push origin <branch>

# Or reset to specific commit
git reset --hard <commit-hash>
git push --force-with-lease origin <branch>
```

### Manual Rollback

1. Go to Cloudflare Dashboard → Workers & Pages
2. Select the deployment
3. Go to Deployments tab
4. Select previous working deployment
5. Click "Rollback to this deployment"

## Monitoring

### View Logs

```bash
# Tail Worker logs (staging)
npx wrangler tail --env staging

# Tail Worker logs (production)
npx wrangler tail --env production
```

### Performance Monitoring

- Cloudflare Dashboard → Analytics → Workers
- Monitor request counts, errors, and performance metrics
- Set up alerts for error thresholds

## Security Notes

1. **Never commit** `.env` files with real values
2. **Use GitHub Secrets** for CI/CD sensitive data
3. **Rotate API tokens** regularly
4. **Review permissions** before deployment
5. **Test in staging** before production deployment

## Support

For deployment issues:
1. Check this documentation
2. Review error logs in Cloudflare dashboard
3. Check GitHub Actions logs for CI/CD failures
4. Contact system administrator if issues persist

---

*Last Updated: September 2025*
*Version: 1.0*