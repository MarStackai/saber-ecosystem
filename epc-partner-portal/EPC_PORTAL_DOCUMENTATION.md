# Saber Renewables EPC Partner Portal - Complete Documentation

## 🚨 SYSTEM STATUS: NOT PRODUCTION READY

**CRITICAL ISSUES:**
- Invitation codes are manually hardcoded instead of dynamically synced
- Power Automate workflow generates codes but doesn't register them in the portal
- Custom domain API routing is broken
- D1 database permissions issues prevent proper invitation storage

---

## 🏗️ Architecture Overview

### Technology Stack
- **Frontend**: Next.js 15.4.4 with App Router and Edge Runtime
- **Backend**: Cloudflare Workers for API processing
- **Database**: Cloudflare D1 (SQLite-based)
- **File Storage**: Cloudflare R2 for document uploads
- **Integration**: Microsoft SharePoint via Power Automate
- **Deployment**: Cloudflare Pages for frontend, Workers for API

### Domain Configuration
- **Frontend**: `https://epc.saberrenewable.energy` (custom domain)
- **API Endpoints**: `https://saber-epc-portal.robjamescarroll.workers.dev/api/*` (worker domain)
- **Issue**: Custom domain `/api/*` routes return 404 due to routing conflicts

---

## 📊 Database Schema (Cloudflare D1)

### Primary Tables

#### `invitations` table
```sql
CREATE TABLE invitations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  auth_code TEXT UNIQUE NOT NULL,
  title TEXT,
  company_name TEXT NOT NULL,
  contact_email TEXT NOT NULL,
  notes TEXT,
  status TEXT DEFAULT 'active',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX idx_invitations_auth_code ON invitations(auth_code);
CREATE INDEX idx_invitations_status ON invitations(status);
```

#### `applications` table (97 columns)
```sql
-- Complete EPC partner application data
-- Includes company details, certifications, insurance, etc.
```

#### `draft_data` table
```sql
-- Auto-save functionality for form progress
```

#### `application_files` table
```sql
-- File upload tracking and metadata
```

### Database Bindings
```toml
# wrangler.toml
[[d1_databases]]
binding = "epc_form_data"
database_name = "epc-form-data"
database_id = "your-d1-database-id"
```

---

## 🔗 API Endpoints

### Working Endpoints (Worker Domain)

#### `/api/validate-invitation` - POST
Validates invitation codes for portal access.

**Request:**
```json
{
  "invitationCode": "FA66FDFF"
}
```

**Response (Success):**
```json
{
  "valid": true,
  "message": "Valid invitation code",
  "invitation": {
    "code": "FA66FDFF",
    "title": "Mr.",
    "companyName": "EPC Partner Company",
    "contactEmail": "partner@example.com",
    "notes": "Test invitation"
  },
  "source": "hardcoded"
}
```

#### `/api/sync-invitation` - POST
Syncs invitation from Power Automate to D1 database.

**Request:**
```json
{
  "AuthCode": "FA66FDFF",
  "Title": "Mr.",
  "CompanyName": "EPC Partner Company",
  "ContactEmail": "partner@example.com",
  "Notes": "Generated from SharePoint"
}
```

**Response (D1 Unavailable):**
```json
{
  "success": true,
  "message": "Invitation logged for processing (D1 unavailable)",
  "invitation": {
    "authCode": "FA66FDFF",
    "title": "Mr.",
    "companyName": "EPC Partner Company",
    "contactEmail": "partner@example.com",
    "notes": "Generated from SharePoint",
    "status": "logged_for_processing"
  },
  "note": "Will be manually synced when D1 is available"
}
```

### New Endpoints (Files & Ops)

#### `/api/upload-file` - POST
- Stores draft files in R2 during application drafting.
- `multipart/form-data` with `file`, `invitationCode` (8 chars), `fieldName`.
- R2 key: `draft/EPC-Applications/<CODE>/<type>/<YYYY-MM-DD>_<field>_<name>`; logs metadata to D1.`draft_files`.

#### `/api/epc-application` - POST
- Final submission — creates D1 application and migrates all draft files R2 → SharePoint (background).
- Body: `{ "submission": { "invitationCode": "ABCDEFGH" } }`.
- Creates folders: `Shared Documents/EPC Applications/<CODE>/<...>` and inserts D1.`application_files`.

#### `/api/migrate-files` - POST
- Manually re-run migration of draft files for an invitation.
- Body: `{ "invitationCode": "ABCDEFGH" }` → schedules background migration.

#### `/api/status` - GET
- Check migration/application status for an invitation.
- Query: `?invitationCode=ABCDEFGH` → returns application row, draft list, migrated files.

### Hardcoded Test Codes (Temporary Solution)
```javascript
const testCodes = {
  'TEST1234': { title: 'Mr.', companyName: 'Test Solar Solutions Ltd', contactEmail: 'test@example.com' },
  '8B8554EF': { title: 'Mr.', companyName: 'A company', contactEmail: 'rob@marstack.ai' },
  '80A3A8A3': { title: 'Ms.', companyName: 'Solar Energy Partners', contactEmail: 'contact@solarpartners.com' },
  'FA66FDFF': { title: 'Mr.', companyName: 'EPC Partner Company', contactEmail: 'partner@epccompany.com' },
  'DEMO2024': { title: 'Ms.', companyName: 'Demo Renewables Inc', contactEmail: 'demo@example.com' },
  'TEST2024': { title: 'Dr.', companyName: 'Test Energy Corp', contactEmail: 'test2024@example.com' }
};
```

---

## ☁️ Cloudflare Configuration

### Workers Configuration
```toml
# wrangler.toml
name = "saber-epc-portal"
main = "src/index.js"
compatibility_date = "2024-09-10"

[env.production]
name = "saber-epc-portal"

[[env.production.d1_databases]]
binding = "epc_form_data"
database_name = "epc-form-data"
database_id = "your-database-id"

[[env.production.r2_buckets]]
binding = "EPC_PARTNER_FILES"
bucket_name = "epc-partner-files"

[env.production.vars]
ENVIRONMENT = "production"
SHAREPOINT_CLIENT_ID = "bbbfe394-7cff-4ac9-9e01-33cbf116b930"
SHAREPOINT_TENANT = "saberrenewables.onmicrosoft.com"
```

### Pages Configuration
```json
# /tmp/epc-deploy/_routes.json
{
  "version": 1,
  "description": "Updated to allow native Pages Functions for API routes",
  "include": ["/*"],
  "exclude": ["/_next/static/*", "/api/*"]
}
```

### R2 Bucket Configuration
- **Bucket Name**: `epc-partner-files`
- **Purpose**: Store uploaded documents (certificates, insurance, etc.)
- **Access**: Private with signed URL access

---

## 🔄 Power Automate Integration

### Current Workflow (BROKEN)
1. SharePoint list item created
2. Generate 8-character invitation code
3. **MISSING**: Sync code to portal via `/api/sync-invitation`
4. Send email with code
5. User tries to use code → **FAILS** (not registered in system)

### Required Fix
Add HTTP action between steps 2 and 4:

**HTTP Action Configuration:**
- **Method**: POST
- **URL**: `https://saber-epc-portal.robjamescarroll.workers.dev/api/sync-invitation`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "AuthCode": "@{variables('InvitationCode')}",
  "Title": "@{triggerOutputs()?['body/Title']}",
  "CompanyName": "@{triggerOutputs()?['body/CompanyName']}",
  "ContactEmail": "@{triggerOutputs()?['body/ContactEmail']}",
  "Notes": "Generated from SharePoint via Power Automate"
}
```

---

## 🚀 Deployment Process

### Worker Deployment
```bash
cd /home/marstack/saber_business_ops
CLOUDFLARE_API_TOKEN=your-token npx wrangler@latest deploy --env=""
```

### Pages Deployment
```bash
CLOUDFLARE_API_TOKEN=your-token CLOUDFLARE_ACCOUNT_ID=7c1df500c062ab6ec160bdc6fd06d4b8 \
npx wrangler pages deploy /tmp/epc-deploy --project-name=saber-epc-portal --branch=main --commit-dirty=true
```

### Frontend Build Process
```bash
cd /home/marstack/saber_business_ops/epc-portal-react
npm run build
# Output goes to .next/ directory
```

---

## 🔐 Authentication & Access

### SharePoint Integration
- **Site URL**: `https://saberrenewables.sharepoint.com/sites/SaberEPCPartners`
- **Client ID**: `bbbfe394-7cff-4ac9-9e01-33cbf116b930`
- **Authentication**: Certificate-based (configured)
- **Lists**: "EPC Invitations", "EPC Onboarding"

### API Tokens
- **Cloudflare API Token**: `FY9KVO6YbWSeBbyxhWp5zbXU8qiXvVqHM9jUTdXD` (limited permissions)
- **Account ID**: `7c1df500c062ab6ec160bdc6fd06d4b8`

---

## 🐛 Known Issues & Limitations

### Critical Issues
1. **Invitation Code Management**: Codes are hardcoded instead of dynamically managed
2. **D1 Database Permissions**: API token lacks D1 write permissions
3. **Custom Domain Routing**: `/api/*` routes return 404 on `epc.saberrenewable.energy`
4. **Power Automate Integration**: Workflow doesn't sync codes before sending emails

### Workarounds in Place
- Using worker domain for API calls: `saber-epc-portal.robjamescarroll.workers.dev`
- Frontend remains on custom domain: `epc.saberrenewable.energy`
- Hardcoded validation codes for immediate testing

### Technical Debt
- Manual code addition process
- Inconsistent error handling
- Missing automated testing
- No monitoring/alerting
- Incomplete documentation

---

## 📋 Development Setup

### Local Development
```bash
# Frontend (Next.js)
cd epc-portal-react
npm run dev  # Port 3003

# Backend (Cloudflare Worker)
cd ..
npx wrangler dev --port 8787 --local

# Create D1 tables locally
npx wrangler d1 execute epc-form-data --local --file=schema.sql
```

### Environment Variables
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8787
CLOUDFLARE_API_TOKEN=your-token
CLOUDFLARE_ACCOUNT_ID=your-account-id
```

---

## 🔧 Required Fixes for Production

### 1. Fix Power Automate Workflow
- Add HTTP action to sync invitation codes before sending emails
- Test end-to-end flow: SharePoint → Power Automate → Portal → Email → User validation

### 2. Resolve D1 Database Permissions
- Update Cloudflare API token with D1 write permissions
- Test database operations in production environment
- Implement proper error handling for database failures

### 3. Fix Custom Domain API Routing
- Debug `_routes.json` configuration
- Ensure API endpoints work on `epc.saberrenewable.energy`
- Remove dependency on worker domain for API calls

### 4. Implement Proper Error Handling
- Add comprehensive logging
- Implement retry mechanisms
- Create admin dashboard for invitation management

### 5. Security & Monitoring
- Implement rate limiting
- Add request validation
- Set up monitoring and alerting
- Audit access permissions

---

## 📞 Support Information

### Key Files
- **Worker Source**: `/home/marstack/saber_business_ops/src/index.js`
- **Frontend Source**: `/home/marstack/saber_business_ops/epc-portal-react/`
- **Database Schema**: `/home/marstack/saber_business_ops/schema.sql`
- **Deployment Config**: `/home/marstack/saber_business_ops/wrangler.toml`

### Useful Commands
```bash
# View worker logs
npx wrangler tail

# Check D1 database
npx wrangler d1 execute epc-form-data --command "SELECT * FROM invitations;"

# Deploy both systems
./deploy-complete-system.sh  # (create this script)
```

### Testing Endpoints
```bash
# Test validation
curl -X POST "https://saber-epc-portal.robjamescarroll.workers.dev/api/validate-invitation" \
  -H "Content-Type: application/json" \
  -d '{"invitationCode": "TEST1234"}'

# Test sync
curl -X POST "https://saber-epc-portal.robjamescarroll.workers.dev/api/sync-invitation" \
  -H "Content-Type: application/json" \
  -d '{"AuthCode": "NEWCODE1", "CompanyName": "Test Co", "ContactEmail": "test@example.com"}'
```

---

## ⚠️ IMPORTANT DISCLAIMERS

**THIS SYSTEM IS NOT PRODUCTION READY**

- Invitation codes are manually managed (unsustainable)
- Database permissions are incomplete
- API routing has known issues
- No comprehensive error handling
- Missing automated testing
- No monitoring or alerting systems

**Do not deploy to production without addressing all critical issues listed above.**

---

*Last Updated: 2025-01-15*  
*Status: Development/Testing Only*  
*Next Review: After fixing Power Automate integration*
