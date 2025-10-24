#!/bin/bash

# Deploy to BOTH domains for redundancy

echo "================================================"
echo "🚀 Dual Domain Deployment Strategy"
echo "================================================"
echo ""
echo "Deploying to both domains for redundancy:"
echo "- Primary: epc.saberrenewables.com (while we control DNS)"
echo "- Backup: epc.saberrenewable.energy (always ours)"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check prerequisites
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git not installed${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Creating dual-domain configuration...${NC}"

# Create a version that accepts both domains
mkdir -p dual-deployment
cp -r public-deployment/* dual-deployment/

# Update JavaScript to accept both domains
cat > dual-deployment/js/config.js << 'EOF'
// Dual domain configuration
const VALID_DOMAINS = [
    'epc.saberrenewables.com',
    'epc.saberrenewable.energy'
];

const CURRENT_DOMAIN = window.location.hostname;

// Use whichever domain the user accessed
const API_ENDPOINT = `https://${CURRENT_DOMAIN}/api`;

// Validate we're on a valid domain
if (!VALID_DOMAINS.includes(CURRENT_DOMAIN)) {
    console.warn('Accessing from unexpected domain:', CURRENT_DOMAIN);
}

// SharePoint webhook (same for both)
const SHAREPOINT_WEBHOOK = 'YOUR_WEBHOOK_URL';
EOF

# Update HTML files to use relative paths
find dual-deployment -name "*.html" -exec sed -i 's|https://epc\.saberrenewable\.energy|""|g' {} \;
find dual-deployment -name "*.html" -exec sed -i 's|https://epc\.saberrenewables\.com|""|g' {} \;

echo -e "${GREEN}✓ Dual-domain configuration created${NC}"

# Create GitHub repository
echo -e "\n${YELLOW}Step 2: Setting up GitHub repository...${NC}"

cd dual-deployment
git init
git add .
git commit -m "Dual domain deployment - works on both .com and .energy"

# Check if repo exists
REPO_NAME="saber-epc-dual"
if ! gh repo view $REPO_NAME &> /dev/null 2>&1; then
    gh repo create $REPO_NAME --public --source=. --remote=origin --push \
        --description "EPC Portal - Dual domain deployment for redundancy"
    echo -e "${GREEN}✓ Repository created${NC}"
else
    git remote add origin "https://github.com/$(gh api user -q .login)/$REPO_NAME.git" 2>/dev/null || true
    git push -u origin main --force
    echo -e "${GREEN}✓ Repository updated${NC}"
fi

cd ..

# Create Cloudflare Pages configuration
echo -e "\n${YELLOW}Step 3: Creating Cloudflare configuration...${NC}"

cat > cloudflare-pages-config.json << 'EOF'
{
  "name": "saber-epc-dual",
  "production_branch": "main",
  "build_config": {
    "build_command": "",
    "destination_dir": "dual-deployment",
    "root_dir": ""
  },
  "deployment_configs": {
    "production": {
      "environment_variables": {
        "NODE_ENV": "production",
        "ACCEPT_DOMAINS": "epc.saberrenewables.com,epc.saberrenewable.energy"
      }
    }
  }
}
EOF

# Create Worker for both domains
cat > worker-dual.js << 'EOF'
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Accept both domains
    const validDomains = [
      'epc.saberrenewables.com',
      'epc.saberrenewable.energy'
    ];
    
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };
    
    // Log which domain is being used
    console.log('Request from:', url.hostname);
    
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    
    // Handle API endpoints
    if (url.pathname.startsWith('/api/')) {
      return handleAPI(request, env, corsHeaders);
    }
    
    // Serve the static site
    return env.ASSETS.fetch(request);
  }
};

async function handleAPI(request, env, headers) {
  const url = new URL(request.url);
  
  if (url.pathname === '/api/submit') {
    const data = await request.json();
    
    // Log which domain the submission came from
    data.source_domain = url.hostname;
    
    // Forward to SharePoint
    if (env.SHAREPOINT_WEBHOOK) {
      await fetch(env.SHAREPOINT_WEBHOOK, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
    }
    
    return new Response(
      JSON.stringify({ success: true, domain: url.hostname }),
      { headers: { ...headers, 'Content-Type': 'application/json' } }
    );
  }
  
  return new Response('API Endpoint', { status: 200 });
}
EOF

echo -e "${GREEN}✓ Cloudflare configuration created${NC}"

# Create deployment instructions
cat > DEPLOY_INSTRUCTIONS_DUAL.md << 'EOF'
# Dual Domain Deployment Instructions

## Why Dual Domains?
- **Primary**: epc.saberrenewables.com (public-facing, while we have DNS control)
- **Backup**: epc.saberrenewable.energy (internal/backup, always under our control)
- **Result**: Business continuity regardless of domain ownership issues

## Step 1: Add BOTH Domains to Cloudflare

### Add saberrenewables.com (if not already)
1. Cloudflare Dashboard → Add Site
2. Enter: saberrenewables.com
3. Update nameservers (you control DNS!)

### Add saberrenewable.energy
1. Cloudflare Dashboard → Add Site
2. Enter: saberrenewable.energy
3. Update nameservers at Namecheap

## Step 2: Create Cloudflare Pages Project

1. Go to Cloudflare Pages
2. Create a project → Connect to GitHub
3. Select repository: `saber-epc-dual`
4. Configure:
   - Build command: (leave empty)
   - Build output: `/dual-deployment`
5. Deploy

## Step 3: Add Custom Domains

In Cloudflare Pages project settings → Custom domains:
1. Add: epc.saberrenewables.com
2. Add: epc.saberrenewable.energy

Both will point to the same deployment!

## Step 4: Configure DNS Records

### For saberrenewables.com:
```
Type: CNAME
Name: epc
Target: saber-epc-dual.pages.dev
Proxy: On
```

### For saberrenewable.energy:
```
Type: CNAME
Name: epc
Target: saber-epc-dual.pages.dev
Proxy: On
```

## Step 5: Test Both URLs

Both should work identically:
- https://epc.saberrenewables.com (public)
- https://epc.saberrenewable.energy (backup)

Test code: ABCD1234

## Monitoring

Set up uptime monitoring for both:
- Primary URL monitoring
- Backup URL monitoring
- DNS change alerts

## If Primary Domain is Lost

1. Update marketing to use .energy
2. Notify partners of new URL
3. Business continues without interruption!
EOF

echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}✅ Dual Domain Deployment Ready!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${YELLOW}What's been created:${NC}"
echo "- Dual-domain configuration"
echo "- GitHub repository: saber-epc-dual"
echo "- Cloudflare Worker for both domains"
echo "- Deployment instructions"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Add BOTH domains to Cloudflare"
echo "2. Set up Cloudflare Pages project"
echo "3. Add both custom domains"
echo "4. Configure DNS for both"
echo ""
echo -e "${GREEN}Result:${NC}"
echo "✅ epc.saberrenewables.com (public face)"
echo "✅ epc.saberrenewable.energy (backup/internal)"
echo "Both work identically - full redundancy!"
echo ""
echo -e "${RED}Important:${NC}"
echo "Move .com to Cloudflare TODAY while you have DNS control!"