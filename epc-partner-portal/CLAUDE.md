# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Saber EPC Partner Portal is a dual-architecture system combining a public-facing Next.js application with SharePoint/Microsoft 365 backend integration for managing EPC (Engineering, Procurement, Construction) partner onboarding.

**Key Architecture Pattern**: Cloudflare-native frontend with SharePoint backend synchronization
- Frontend deploys as static export to Cloudflare Pages
- Backend APIs run as Cloudflare Workers (serverless functions in `/functions`)
- Data persistence uses Cloudflare D1 (SQLite) + R2 (object storage)
- SharePoint integration for business process management

## Port Configuration (CRITICAL)

**Port 4200** is used for all frontend development to avoid common Node.js tool conflicts.

```bash
# Frontend always runs on port 4200
cd epc-portal-react && npm run dev

# Backend Worker runs on port 8787
npx wrangler dev --local --port 8787

# Staging Worker runs on port 8788
```

This is configured in:
- `epc-portal-react/package.json` scripts
- `playwright.config.ts` for testing
- Environment files (`.env.*`)

## Development Commands

### Frontend (Next.js + React)
```bash
cd epc-portal-react

# Development server (port 4200)
npm run dev

# Build for production (static export)
npm run build

# Deploy to Cloudflare Pages
npm run deploy

# Linting
npm run lint
```

### Backend (Cloudflare Workers)
```bash
# Run local worker dev server (port 8787)
npx wrangler dev --local --port 8787

# Deploy worker to Cloudflare
npx wrangler deploy

# Deploy to staging environment
npx wrangler deploy --env staging

# Deploy to production environment
npx wrangler deploy --env production
```

### Testing
```bash
# Run all Playwright E2E tests
npx playwright test

# Run specific test environments
TEST_ENV=staging npx playwright test
TEST_ENV=production npx playwright test

# Legacy Puppeteer tests (in epc-portal-react)
npm run test:admin          # Admin portal tests
npm run test:partner        # Partner portal tests
npm run test:sharepoint     # SharePoint integration tests
npm run test:all            # All tests
```

### SharePoint Automation (PowerShell)
```bash
# Setup SharePoint backend
pwsh scripts/setup-epc-portal.ps1 -SiteUrl <url> -ClientId <id> -Tenant <tenant>

# Send partner invitations
pwsh scripts/send-epc-invitations.ps1

# Test SharePoint access
pwsh scripts/test-sharepoint-access.ps1
```

## Architecture Deep Dive

### Hybrid Static/Edge Architecture

**Next.js Configuration** (`epc-portal-react/next.config.mjs`):
- Uses `output: 'export'` for static site generation
- Static pages deployed to Cloudflare Pages
- API routes in `/src/app/api/*` become Next.js endpoints
- Functions in `/functions/api/*` become Cloudflare Workers Page Functions

**Key distinction**:
- `/src/app/api/*` routes: Next.js server components (for development)
- `/functions/api/*`: Actual Cloudflare Workers that handle production traffic
- In production, Cloudflare routes API calls to Workers, not Next.js

### Data Flow Architecture

```
User → Cloudflare Pages (Static Next.js)
     → Cloudflare Workers (/functions/api/*)
     → D1 Database (SQLite) for storage
     → R2 Buckets for file uploads
     → SharePoint API (async sync for business processes)
```

**Critical Pattern**: D1-First with SharePoint Sync
1. All form submissions go to D1 immediately (fast, reliable)
2. SharePoint sync happens asynchronously (can retry if it fails)
3. Never block user flow waiting for SharePoint
4. See `src/lib/d1.js` and `src/lib/r2.js` for helpers

### Database Schema (D1)

The D1 database has these critical tables:
- `draft_data`: Auto-save form data (invitation_code, form_data JSON, current_step)
- `applications`: Complete submitted applications (denormalized for performance)
- `application_files`: File metadata (actual files in R2)
- `partner_invitations`: Unique invitation codes for secure access

**Important**: Mock helpers exist in `src/lib/d1.js` and `src/lib/r2.js` for local development when bindings aren't available.

### File Storage (R2)

Files organized by invitation code:
```
EPC-Applications/
  {invitation-code}/
    documents/
    certificates/
    financial/
    logos/
```

See `R2Helper.generateFilePath()` in `src/lib/r2.js` for logic.

### Multi-Portal Pattern

Three distinct portal areas with different access patterns:

1. **Public Portal** (`/apply`, `/`):
   - Invitation-code based access
   - No authentication required
   - Single-use submission workflow

2. **Partner Portal** (`/partner/*`):
   - Authenticated partner access
   - View project tenders
   - Submit documents for projects
   - Authentication via invitation-based login

3. **Admin Portal** (`/admin/*`):
   - Internal staff only
   - Manage invitations
   - Review applications
   - Upload tender documents

Each portal has separate layouts and navigation (see `/src/app/[portal]/layout.jsx` files).

### SharePoint Integration

**Authentication**:
- Uses Azure AD App Registration (Client ID in `wrangler.toml`)
- Certificate-based authentication for unattended scripts
- Device login for interactive PowerShell scripts

**Data Sync Pattern**:
```
Cloudflare D1 → Primary storage (immediate)
     ↓
SharePoint Lists → Business process tracking (async sync)
     ↓
Power Automate → Notifications, approvals, workflows
```

PowerShell scripts in `/scripts` manage:
- Site provisioning (`setup-epc-portal.ps1`)
- List/library creation
- Permission management
- Invitation generation
- Data verification

## Environment Configuration

### Environment Files
- `.env.development`: Local development
- `.env.staging`: Staging environment
- `.env.production`: Production environment
- `epc-portal-react/.env.local`: Frontend-specific (not in git)

### Wrangler Configuration (`wrangler.toml`)

Three environments configured:
- Default (development): Local testing with dev databases
- `staging`: Pre-production with staging databases
- `production`: Live production environment

Each environment has separate:
- D1 database bindings
- R2 bucket bindings
- Environment variables (SHAREPOINT_CLIENT_ID, etc.)

**Critical**: Never commit secrets to `wrangler.toml`. Use Cloudflare dashboard secrets or environment variables.

## Testing Strategy

### Local E2E Testing (Playwright)
- Configuration in `playwright.config.ts`
- Tests in `/tests/e2e/`
- Automatically starts dev servers on ports 4200 and 8787
- Tests multiple browsers: Chromium, Firefox, WebKit, Mobile

### Environment Testing
```bash
# Test against local
npx playwright test

# Test against staging
TEST_ENV=staging npx playwright test

# Test against production (read-only tests only!)
TEST_ENV=production npx playwright test
```

### Legacy Puppeteer Tests
Located in `epc-portal-react/tests/puppeteer/`:
- Admin workflow tests
- Partner authentication tests
- SharePoint integration tests
- Complete end-to-end flow tests

Run via npm scripts: `npm run test:admin`, `npm run test:partner`, etc.

## Deployment Workflow

### Frontend Deployment (Cloudflare Pages)

Automatic deployment via GitHub Actions (`.github/workflows/frontend-build.yml`):
1. Build Next.js static export: `npm run build`
2. Deploy to Cloudflare Pages: `npm run deploy`
3. Pages project: `saber-epc-portal`

### Worker Deployment

Manual deployment for now:
```bash
# Staging
npx wrangler deploy --env staging

# Production (requires confirmation)
npx wrangler deploy --env production
```

Worker routes configured in `wrangler.toml`:
- `epc.saberrenewable.energy/api/*`
- `epc.saberrenewable.energy/operations/*`
- `epc.saberrenewable.energy/form/*`

### SharePoint Deployment

PowerShell scripts must be run manually by authorized users:
1. Authenticate with device login or certificate
2. Run provisioning scripts as needed
3. Verify with test scripts

## Critical Development Patterns

### 1. File API SSR Workaround

**Problem**: `File` API not available in Node.js during SSR build
**Solution**: Webpack fallback in `next.config.mjs`:
```javascript
config.resolve.fallback = {
  ...config.resolve.fallback,
  File: false,
}
```

Files are only processed client-side or in Cloudflare Workers (which have File API).

### 2. Markdoc for Documentation

Documentation pages use Markdoc (see `/src/app/docs/*.md`):
- Markdown files with frontmatter
- Custom components defined in `/src/markdoc/`
- Search temporarily disabled (check `next.config.mjs` for status)

### 3. Edge Runtime for All APIs

All API routes must use:
```javascript
export const runtime = 'edge'
```

This ensures compatibility with Cloudflare Workers runtime.

### 4. Environment Binding Access

In Cloudflare Workers functions:
```javascript
import { getRequestContext } from '@cloudflare/next-on-pages'

export async function POST(request) {
  const { env } = getRequestContext()

  // Access bindings
  const db = env.epc_form_data      // D1 database
  const files = env.EPC_PARTNER_FILES // R2 bucket
  const docs = env.EPC_DOCUMENTS     // R2 bucket
}
```

Use helper functions from `src/lib/d1.js` and `src/lib/r2.js` which handle both production bindings and development mocks.

### 5. Invitation Code Security

Invitation codes are:
- Generated server-side only
- Single-use per submission
- Validated before any data operations
- Stored in D1 `partner_invitations` table

Never expose invitation generation logic client-side.

## Common Troubleshooting

### "TypeError: File is not a constructor" during build
- This is expected during Next.js SSR build
- File handling moved to client-side or Workers only
- See webpack fallback in `next.config.mjs`

### Port 4200 already in use
- Check if previous dev server is still running
- Kill process: `lsof -ti:4200 | xargs kill -9`
- Never use ports 3000-3003 (common Node.js conflicts)

### D1/R2 bindings not available in development
- Expected behavior
- Mock helpers automatically activate (see console logs)
- Test with actual bindings using `wrangler dev --local`

### SharePoint authentication failures
- Verify Azure AD app registration exists
- Check certificate is installed (for cert auth)
- Ensure client ID matches `wrangler.toml`
- Use device login for interactive testing

## File Organization Conventions

```
epc-portal-react/
  src/
    app/              # Next.js 13+ app directory
      admin/          # Admin portal pages
      partner/        # Partner portal pages
      apply/          # Public application flow
      api/            # Next.js API routes (dev only)
      docs/           # Markdoc documentation pages
    components/       # Reusable React components
      admin/          # Admin-specific components
      partner/        # Partner-specific components
    lib/              # Shared utilities
      d1.js           # D1 database helper + mock
      r2.js           # R2 storage helper + mock
      config.js       # App configuration
  functions/          # Cloudflare Workers (production APIs)
    api/              # API endpoints (these run in production)
  tests/
    puppeteer/        # Legacy Puppeteer tests
scripts/              # PowerShell automation scripts
tests/                # Playwright E2E tests
  e2e/                # Test specs
  fixtures/           # Test data
```

## Dependencies Notes

### Critical Dependencies
- `next`: v15 with app directory
- `react`: v19
- `@cloudflare/next-on-pages`: Adapter for Cloudflare Pages
- `tailwindcss`: v4.1+ with new CSS-first architecture
- `@markdoc/next.js`: Documentation system
- `@headlessui/react`: Accessible UI components

### Development Tools
- `wrangler`: Cloudflare CLI for Workers and Pages
- `playwright`: Modern E2E testing
- `puppeteer`: Legacy E2E tests (consider migrating to Playwright)
- PowerShell 7+ with PnP.PowerShell module for SharePoint

## Code Quality Standards

Follow the strict guidelines in this file's "CLAUDE CODE GENERATION RULES" section (lines 27-130).

**Key reminders**:
1. Only modify what's explicitly requested
2. Always update package.json when adding imports
3. No placeholder values - use environment variables
4. Security: Never put secrets in client code
5. Evidence-based responses - show code when asked about implementation
6. Add intelligent logging at critical decision points
7. Clean up unused code automatically

## Version Control

- **Main branch**: Stable production code
- **Staging branch**: Pre-production testing (currently active)
- **Feature branches**: Individual features (merge to staging first)

Always test on staging before production deployment.
