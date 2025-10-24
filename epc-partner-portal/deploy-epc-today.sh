#!/bin/bash

# Deploy EPC Portal to epc.saberrenewable.energy TODAY

echo "================================================"
echo "🚀 EPC Portal Deployment"
echo "   Target: epc.saberrenewable.energy"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DOMAIN="saberrenewable.energy"
SUBDOMAIN="epc"
FULL_URL="https://$SUBDOMAIN.$DOMAIN"

echo -e "${YELLOW}Deployment Configuration:${NC}"
echo -e "Main domain: ${BLUE}$DOMAIN${NC} (will redirect to .com)"
echo -e "EPC Portal: ${GREEN}$SUBDOMAIN.$DOMAIN${NC} (internal app)"
echo ""

# Step 1: Prepare deployment files
echo -e "${YELLOW}Step 1: Preparing files...${NC}"

# Ensure files use correct domain
if [ -d "public-deployment" ]; then
    find public-deployment -type f -name "*.html" -exec \
        sed -i "s/saberrenewables\.com/$DOMAIN/g" {} \; 2>/dev/null || true
    echo -e "${GREEN}✓ Files prepared${NC}"
else
    echo -e "${GREEN}✓ Using existing epc-form directory${NC}"
fi

# Step 2: Initialize Git
echo -e "\n${YELLOW}Step 2: Setting up Git repository...${NC}"

if [ ! -d .git ]; then
    git init
    git add .
    git commit -m "Initial commit: EPC Portal for $SUBDOMAIN.$DOMAIN"
    echo -e "${GREEN}✓ Git initialized${NC}"
else
    git add .
    git commit -m "Update: EPC Portal for $SUBDOMAIN.$DOMAIN" || true
    echo -e "${GREEN}✓ Git updated${NC}"
fi

# Step 3: Create/Update GitHub repo
echo -e "\n${YELLOW}Step 3: GitHub repository...${NC}"

REPO_NAME="saber-epc-portal"

# Check if gh is authenticated
if ! gh auth status &> /dev/null; then
    echo "Please authenticate with GitHub:"
    gh auth login
fi

# Create or update repo
if ! gh repo view $REPO_NAME &> /dev/null; then
    gh repo create $REPO_NAME \
        --public \
        --source=. \
        --remote=origin \
        --push \
        --description "EPC Partner Portal for Saber Renewables"
    echo -e "${GREEN}✓ Repository created${NC}"
else
    git remote add origin "https://github.com/$(gh api user -q .login)/$REPO_NAME.git" 2>/dev/null || true
    git branch -M main
    git push -u origin main --force
    echo -e "${GREEN}✓ Repository updated${NC}"
fi

# Step 4: Create Cloudflare instructions
echo -e "\n${YELLOW}Step 4: Creating Cloudflare setup instructions...${NC}"

cat > CLOUDFLARE_SETUP.md << EOF
# Cloudflare Setup Instructions

## 1. Add saberrenewable.energy to Cloudflare

1. Go to: https://dash.cloudflare.com
2. Click "Add Site"
3. Enter: saberrenewable.energy
4. Select Free plan
5. Copy the nameservers shown

## 2. Update Namecheap Nameservers

1. Login to Namecheap
2. Domain List → Manage (saberrenewable.energy)
3. Nameservers → Custom DNS
4. Add Cloudflare nameservers
5. Save (wait 2-24 hours for propagation)

## 3. Configure DNS in Cloudflare

### Add these DNS records:

| Type  | Name | Content                    | Proxy |
|-------|------|----------------------------|-------|
| A     | @    | 192.0.2.1                 | ✓     |
| CNAME | www  | @                         | ✓     |
| CNAME | epc  | saber-epc-portal.pages.dev| ✓     |

## 4. Create Redirect Page Rules

1. Go to Rules → Page Rules
2. Create Page Rule:
   - URL: *saberrenewable.energy/*
   - Setting: Forwarding URL (301)
   - Target: https://saberrenewables.com/\$1
3. Create another:
   - URL: *www.saberrenewable.energy/*
   - Setting: Forwarding URL (301)
   - Target: https://saberrenewables.com/\$1

## 5. Set up Cloudflare Pages

1. Go to Workers & Pages → Create Application → Pages
2. Connect to Git → Select: $REPO_NAME
3. Configuration:
   - Framework preset: None
   - Build command: \`echo "No build needed"\`
   - Build output directory: \`public-deployment\` or \`epc-form\`
4. Save and Deploy

## 6. Add Custom Domain

1. In Pages project → Custom domains
2. Add: epc.saberrenewable.energy
3. It will auto-configure since DNS is already set

## Results

✅ https://saberrenewable.energy → Redirects to saberrenewables.com
✅ https://epc.saberrenewable.energy → EPC Portal
✅ Test with code: ABCD1234
EOF

echo -e "${GREEN}✓ Instructions created${NC}"

# Step 5: Create test file
echo -e "\n${YELLOW}Step 5: Creating test file...${NC}"

mkdir -p public-deployment
cat > public-deployment/test.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>EPC Portal - Test Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            text-align: center;
        }
        h1 { color: #044D73; }
        .status { 
            padding: 20px;
            background: #e8f5e9;
            border-radius: 5px;
            margin: 20px 0;
        }
        a {
            display: inline-block;
            margin: 10px;
            padding: 10px 20px;
            background: #044D73;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 EPC Portal Deployment Test</h1>
        <div class="status">
            <strong>✅ Cloudflare Pages is working!</strong><br>
            URL: $FULL_URL
        </div>
        <a href="/epc/apply.html">Go to Application Form</a>
        <a href="/epc/form.html">Go to Main Form</a>
        <p>Test Code: <strong>ABCD1234</strong></p>
    </div>
</body>
</html>
EOF

git add .
git commit -m "Add test page" || true
git push origin main || true

echo -e "${GREEN}✓ Test file created${NC}"

# Final summary
echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✅ Deployment Preparation Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${YELLOW}What's Ready:${NC}"
echo "✓ GitHub Repo: https://github.com/$(gh api user -q .login)/$REPO_NAME"
echo "✓ Files prepared for $SUBDOMAIN.$DOMAIN"
echo "✓ Cloudflare instructions in CLOUDFLARE_SETUP.md"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Add saberrenewable.energy to Cloudflare"
echo "2. Update nameservers at Namecheap"
echo "3. Configure DNS records"
echo "4. Set up redirect page rules"
echo "5. Connect Cloudflare Pages to GitHub"
echo ""
echo -e "${GREEN}Final Result:${NC}"
echo "• https://saberrenewable.energy → Redirects to .com"
echo "• https://epc.saberrenewable.energy → EPC Portal ✅"
echo ""
echo -e "${BLUE}Read CLOUDFLARE_SETUP.md for detailed instructions${NC}"