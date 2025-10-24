# 🏗️ Saber Domain Architecture - Public vs Private

## Domain Strategy

### Public Domain: `saberrenewables.com`
**Purpose**: Customer-facing, marketing, public services
- Main website (WordPress on EasyWP)
- EPC Partner Portal: `epc.saberrenewables.com`
- Public APIs
- Marketing pages

### Private Domain: `saberrenewable.energy`
**Purpose**: Internal business operations, private apps
- FIT Intelligence: `fit.saberrenewable.energy`
- Business Ops Tools: `ops.saberrenewable.energy`
- Internal SharePoint Integration: `sharepoint.saberrenewable.energy`
- Dev/Staging: `dev.saberrenewable.energy`
- Analytics Dashboard: `analytics.saberrenewable.energy`

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  PUBLIC FACING                           │
│              saberrenewables.com                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  www.saberrenewables.com      → Marketing Site (WP)    │
│  epc.saberrenewables.com      → Partner Portal         │
│  api.saberrenewables.com      → Public APIs            │
│  blog.saberrenewables.com     → Content/Blog           │
│                                                         │
│  Hosting: EasyWP + Cloudflare Pages                    │
│  Access: Public (no auth required)                     │
│                                                         │
└─────────────────────────────────────────────────────────┘

                            │
                            │ Data Flow
                            ▼

┌─────────────────────────────────────────────────────────┐
│                  PRIVATE INTERNAL                        │
│              saberrenewable.energy                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  fit.saberrenewable.energy       → FIT Intelligence    │
│  ops.saberrenewable.energy       → Business Ops Portal │
│  crm.saberrenewable.energy       → CRM System          │
│  sharepoint.saberrenewable.energy → SP Integration     │
│  analytics.saberrenewable.energy  → Internal Analytics │
│  dev.saberrenewable.energy       → Development/Testing │
│                                                         │
│  Hosting: Cloudflare (Zero Trust required)             │
│  Access: Authenticated employees only                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: Set Up Cloudflare for Both Domains

#### Public Domain (saberrenewables.com)
```bash
# Keep on EasyWP for main site
# Use Cloudflare for:
- DNS management
- CDN/caching
- DDoS protection
- Subdomains via Pages
```

#### Private Domain (saberrenewable.energy)
```bash
# Full Cloudflare setup:
- Cloudflare Zero Trust for authentication
- Cloudflare Pages for apps
- Cloudflare Workers for APIs
- Cloudflare Access for security
```

### Phase 2: Deploy Public EPC Portal

```bash
# Deploy to epc.saberrenewables.com
cd /home/marstack/saber_business_ops

# Update configuration for public domain
sed -i 's/saberrenewable.energy/saberrenewables.com/g' public-deployment/*.html

# Create public deployment
git init
git add .
git commit -m "EPC Portal for public domain"
gh repo create saber-epc-public --public --push
```

### Phase 3: Configure Private Apps

#### Cloudflare Zero Trust Setup
```javascript
// wrangler.toml for private apps
name = "saber-private-apps"
compatibility_date = "2024-01-01"

[[routes]]
pattern = "*.saberrenewable.energy/*"
zone_name = "saberrenewable.energy"

[env.production]
vars = { 
  ENVIRONMENT = "production",
  REQUIRE_AUTH = "true"
}

[[access]]
name = "Saber Internal Apps"
domain = "saberrenewable.energy"
aud = "your-access-aud"
```

#### FIT Intelligence Deployment
```bash
# Deploy to fit.saberrenewable.energy
mkdir -p private-apps/fit-intelligence
cp -r /path/to/fit-intelligence/* private-apps/fit-intelligence/

# Configure authentication
cat > private-apps/fit-intelligence/_middleware.js << 'EOF'
export async function onRequest(context) {
  // Verify Cloudflare Access JWT
  const jwt = context.request.headers.get('CF-Access-JWT-Assertion');
  
  if (!jwt) {
    return new Response('Unauthorized', { status: 401 });
  }
  
  // Verify JWT with Cloudflare Access
  const isValid = await verifyJWT(jwt, context.env);
  
  if (!isValid) {
    return new Response('Invalid token', { status: 403 });
  }
  
  return context.next();
}
EOF
```

### Phase 4: SharePoint Integration Hub

```javascript
// Private SharePoint integration at sharepoint.saberrenewable.energy
export default {
  async fetch(request, env) {
    // This is PRIVATE - only accessible internally
    
    const url = new URL(request.url);
    
    // Sync EPC data from public to SharePoint
    if (url.pathname === '/sync/epc-submissions') {
      const submissions = await env.KV_SUBMISSIONS.list();
      
      for (const key of submissions.keys) {
        const data = await env.KV_SUBMISSIONS.get(key.name);
        await forwardToSharePoint(data, env);
        await env.KV_SUBMISSIONS.delete(key.name);
      }
      
      return new Response('Synced ' + submissions.keys.length + ' submissions');
    }
    
    // Get SharePoint data for internal dashboards
    if (url.pathname === '/api/dashboard-data') {
      const data = await getSharePointData(env);
      return Response.json(data);
    }
    
    return new Response('SharePoint Integration Hub');
  }
};
```

## Security Configuration

### Public Domain Security
```yaml
# epc.saberrenewables.com
Security Level: Medium
SSL: Full (Strict)
WAF: Enabled
Rate Limiting: 100 req/min
CORS: Allow specific origins
```

### Private Domain Security
```yaml
# *.saberrenewable.energy
Security Level: High
SSL: Full (Strict)
WAF: Enabled + Custom Rules
Rate Limiting: 50 req/min
Zero Trust: Required
Access Policy: Email ends with @saberrenewables.com
MFA: Required
Session Duration: 8 hours
```

## Cloudflare Zero Trust Setup

### Step 1: Enable Access
```
1. Cloudflare Dashboard → Zero Trust
2. Access → Applications → Add Application
3. Self-hosted application
4. Application domain: *.saberrenewable.energy
5. Application name: Saber Internal Apps
```

### Step 2: Configure Policy
```
Policy name: Saber Employees
Action: Allow
Include:
  - Emails ending in: @saberrenewables.com
  - Specific emails: [contractor@email.com]
Require:
  - Multi-factor authentication
```

### Step 3: Add Applications
```
fit.saberrenewable.energy → FIT Intelligence
ops.saberrenewable.energy → Business Operations
analytics.saberrenewable.energy → Analytics Dashboard
dev.saberrenewable.energy → Development Environment
```

## Deployment Scripts

### Public Deployment (Customer-facing)
```bash
#!/bin/bash
# deploy-public.sh

DOMAIN="saberrenewables.com"
SUBDOMAIN="epc"

echo "Deploying to $SUBDOMAIN.$DOMAIN (PUBLIC)"

# Update URLs in files
find public-deployment -type f -name "*.html" -exec \
  sed -i "s/saberrenewable.energy/$DOMAIN/g" {} \;

# Deploy to Cloudflare Pages
wrangler pages publish public-deployment \
  --project-name="saber-epc-public" \
  --branch=main

echo "Public portal live at: https://$SUBDOMAIN.$DOMAIN"
```

### Private Deployment (Internal)
```bash
#!/bin/bash
# deploy-private.sh

DOMAIN="saberrenewable.energy"

echo "Deploying private apps to $DOMAIN (INTERNAL)"

# Deploy each private app
for APP in fit ops analytics; do
  echo "Deploying $APP.$DOMAIN..."
  
  wrangler pages publish private-apps/$APP \
    --project-name="saber-$APP-internal" \
    --branch=main
    
  # Apply Zero Trust policy
  cloudflare access app update \
    --domain="$APP.$DOMAIN" \
    --policy="saber-employees-only"
done

echo "Private apps deployed with Zero Trust protection"
```

## Benefits of This Architecture

### Separation of Concerns
- **Public**: Marketing, partners, customers
- **Private**: Internal tools, sensitive data, operations

### Security
- Public domain has standard security
- Private domain has Zero Trust + MFA
- No accidental exposure of internal tools

### Management
- Clear distinction between public/private
- Different deployment pipelines
- Separate monitoring and analytics

### Cost Efficiency
- Both domains on Cloudflare (mostly free)
- Single WordPress instance for public site
- All internal apps on serverless (pay per use)

## Quick Setup Commands

```bash
# 1. Add both domains to Cloudflare
cloudflare-add-site saberrenewables.com
cloudflare-add-site saberrenewable.energy

# 2. Configure Zero Trust for private domain
cloudflare-zero-trust setup saberrenewable.energy

# 3. Deploy public EPC portal
./deploy-public.sh

# 4. Deploy private apps
./deploy-private.sh

# 5. Test access
curl https://epc.saberrenewables.com  # Should work
curl https://fit.saberrenewable.energy  # Should require auth
```

## Monitoring & Maintenance

### Public Domain Monitoring
- Google Analytics for traffic
- Cloudflare Analytics for performance
- Uptime monitoring for availability

### Private Domain Monitoring
- Cloudflare Zero Trust logs for access
- Worker analytics for usage
- SharePoint integration status

## Disaster Recovery

### If saberrenewables.com is lost:
- Public site affected
- Move to backup domain quickly

### If saberrenewable.energy is lost:
- Internal tools affected
- Team can't access ops tools
- Have backup access methods ready

---

## Summary

**Public** (`saberrenewables.com`):
- Customer-facing
- No authentication
- Marketing & partners

**Private** (`saberrenewable.energy`):
- Internal operations
- Zero Trust required
- Business tools & integrations

This gives you the best of both worlds - professional public presence and secure internal operations!