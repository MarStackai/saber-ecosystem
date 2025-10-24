#!/bin/bash

# Deployment script for Cloudflare Pages with existing infrastructure

echo "================================================"
echo "🚀 Saber EPC Portal - Cloudflare Deployment"
echo "================================================"
echo ""
echo "This script will deploy the EPC portal to Cloudflare"
echo "while keeping your main site on EasyWP unchanged."
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git is not installed. Please install git first.${NC}"
    exit 1
fi

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}GitHub CLI not found. Installing...${NC}"
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt update
    sudo apt install gh -y
fi

echo -e "${GREEN}✓ Prerequisites checked${NC}"

# Step 2: Initialize git repository
echo -e "\n${YELLOW}Setting up Git repository...${NC}"

if [ ! -d .git ]; then
    git init
    git add .
    git commit -m "Initial commit: EPC Partner Portal for Cloudflare"
    echo -e "${GREEN}✓ Git repository initialized${NC}"
else
    echo -e "${GREEN}✓ Git repository already exists${NC}"
fi

# Step 3: Create GitHub repository
echo -e "\n${YELLOW}Creating GitHub repository...${NC}"

# Check if already authenticated
if ! gh auth status &> /dev/null; then
    echo "Please authenticate with GitHub:"
    gh auth login
fi

# Create repository
REPO_NAME="saber-epc-portal"
if gh repo view $REPO_NAME &> /dev/null; then
    echo -e "${GREEN}✓ Repository already exists${NC}"
else
    gh repo create $REPO_NAME --public --source=. --remote=origin --push --description "EPC Partner Portal for Saber Renewables"
    echo -e "${GREEN}✓ Repository created and pushed${NC}"
fi

# Step 4: Create Cloudflare configuration
echo -e "\n${YELLOW}Creating Cloudflare configuration...${NC}"

cat > wrangler.toml << 'EOF'
name = "saber-epc-api"
main = "src/worker.js"
compatibility_date = "2024-01-01"

[env.production]
vars = { ENVIRONMENT = "production" }
routes = [
  { pattern = "epc.saberrenewable.energy/api/*", zone_name = "saberrenewable.energy" }
]

[[kv_namespaces]]
binding = "INVITATION_CODES"
id = "your-kv-namespace-id"
preview_id = "your-preview-kv-id"

[site]
bucket = "./public-deployment"
EOF

# Create worker script
mkdir -p src
cat > src/worker.js << 'EOF'
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': 'https://epc.saberrenewable.energy',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };
    
    // Handle OPTIONS request
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    
    // API: Validate invitation code
    if (url.pathname === '/api/validate-code' && request.method === 'POST') {
      const { code } = await request.json();
      
      // Check code in KV store or hardcoded list
      const validCodes = ['ABCD1234', 'SABER2024', 'EPC2025'];
      const isValid = validCodes.includes(code);
      
      return new Response(
        JSON.stringify({ valid: isValid }),
        { 
          headers: { 
            ...corsHeaders, 
            'Content-Type': 'application/json' 
          }
        }
      );
    }
    
    // API: Submit form
    if (url.pathname === '/api/submit' && request.method === 'POST') {
      const formData = await request.json();
      
      // Forward to SharePoint via Power Automate webhook
      if (env.SHAREPOINT_WEBHOOK) {
        const response = await fetch(env.SHAREPOINT_WEBHOOK, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ...formData,
            timestamp: new Date().toISOString(),
            source: 'epc.saberrenewable.energy'
          })
        });
        
        return new Response(
          JSON.stringify({ 
            success: response.ok,
            message: response.ok ? 'Application submitted successfully' : 'Submission failed'
          }),
          { 
            headers: { 
              ...corsHeaders, 
              'Content-Type': 'application/json' 
            }
          }
        );
      }
      
      // Fallback: Store in KV for later processing
      const id = crypto.randomUUID();
      await env.SUBMISSIONS.put(id, JSON.stringify(formData));
      
      return new Response(
        JSON.stringify({ 
          success: true, 
          message: 'Application received',
          id: id
        }),
        { 
          headers: { 
            ...corsHeaders, 
            'Content-Type': 'application/json' 
          }
        }
      );
    }
    
    // Default response
    return new Response('Saber EPC API', { status: 200 });
  }
};
EOF

echo -e "${GREEN}✓ Cloudflare configuration created${NC}"

# Step 5: Create deployment instructions
cat > DEPLOY_INSTRUCTIONS.md << 'EOF'
# Cloudflare Deployment Instructions

## 1. DNS Migration (Do this first!)

### In Cloudflare Dashboard:
1. Go to https://dash.cloudflare.com
2. Click "Add a Site"
3. Enter: saberrenewable.energy
4. Choose the Free plan
5. Copy the nameservers shown (e.g., xxx.ns.cloudflare.com)

### In Namecheap:
1. Login to Namecheap
2. Go to Domain List → Manage (for saberrenewable.energy)
3. Click "Nameservers" → "Custom DNS"
4. Add the Cloudflare nameservers
5. Save changes

**Wait 2-24 hours for DNS propagation**

## 2. Cloudflare Pages Setup

Once DNS is active in Cloudflare:

1. Go to Cloudflare Dashboard → Pages
2. Create a project → Connect to Git
3. Authorize GitHub and select: saber-epc-portal
4. Configure build settings:
   - Framework preset: None
   - Build command: `mkdir -p dist && cp -r public-deployment/* dist/`
   - Build output directory: `/dist`
   - Root directory: `/`
5. Add environment variables:
   - `SHAREPOINT_WEBHOOK`: (Power Automate webhook URL)
6. Save and Deploy

## 3. Add DNS Record for Subdomain

In Cloudflare DNS:
1. Go to DNS → Records
2. Add record:
   - Type: CNAME
   - Name: epc
   - Target: saber-epc-portal.pages.dev
   - Proxy status: Proxied (orange cloud)
3. Save

## 4. Deploy Worker (for API)

```bash
# Install Wrangler CLI
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Deploy worker
wrangler publish
```

## 5. Test URLs

- Main site (unchanged): https://saberrenewable.energy
- EPC Portal: https://epc.saberrenewable.energy
- API Endpoint: https://epc.saberrenewable.energy/api/validate-code

## Verification Checklist

- [ ] DNS nameservers updated in Namecheap
- [ ] Cloudflare shows "Active" for domain
- [ ] Main site still loads normally
- [ ] Cloudflare Pages project created
- [ ] Subdomain DNS record added
- [ ] EPC portal accessible at subdomain
- [ ] Form validation works with code: ABCD1234
EOF

echo -e "${GREEN}✓ Deployment instructions created${NC}"

# Step 6: Prepare public deployment files
echo -e "\n${YELLOW}Preparing deployment files...${NC}"

# Ensure public-deployment directory has all needed files
if [ ! -f public-deployment/index.html ]; then
    echo -e "${RED}Warning: public-deployment/index.html not found${NC}"
    echo "Creating placeholder..."
    mkdir -p public-deployment
    echo "<h1>EPC Portal - Coming Soon</h1>" > public-deployment/index.html
fi

# Add .gitignore
cat > .gitignore << 'EOF'
node_modules/
.env
.env.local
.wrangler/
dist/
*.log
.DS_Store
EOF

# Commit changes
git add .
git commit -m "Add Cloudflare deployment configuration" || true
git push origin main || true

echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}✅ Deployment preparation complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Read DEPLOY_INSTRUCTIONS.md"
echo "2. Migrate DNS from Namecheap to Cloudflare"
echo "3. Set up Cloudflare Pages"
echo "4. Configure SharePoint webhook"
echo ""
echo -e "${GREEN}Your main site on EasyWP will continue working unchanged.${NC}"
echo -e "${GREEN}The EPC portal will be at: https://epc.saberrenewable.energy${NC}"
echo ""
echo "GitHub Repository: https://github.com/$(gh api user -q .login)/$REPO_NAME"