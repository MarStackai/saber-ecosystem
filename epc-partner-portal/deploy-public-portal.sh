#!/bin/bash

# Deploy EPC Portal to PUBLIC domain (saberrenewables.com)

echo "================================================"
echo "🌐 Deploy EPC Portal to saberrenewables.com"
echo "================================================"

# Configuration
PUBLIC_DOMAIN="saberrenewables.com"
PRIVATE_DOMAIN="saberrenewable.energy"
REPO_NAME="saber-epc-public"

# Update all references to use public domain
echo "📝 Updating domain references..."
cp -r public-deployment public-deployment-prod
find public-deployment-prod -type f \( -name "*.html" -o -name "*.js" \) -exec \
    sed -i "s/saberrenewable\.energy/$PUBLIC_DOMAIN/g" {} \;

# Update API endpoints to use public domain
sed -i "s/epc\.saberrenewable\.energy/epc\.$PUBLIC_DOMAIN/g" public-deployment-prod/epc/*.html

# Create GitHub repository for public portal
echo "🐙 Setting up GitHub repository..."
cd public-deployment-prod
git init
git add .
git commit -m "EPC Portal for public domain"

# Create public repo
if ! gh repo view $REPO_NAME &> /dev/null; then
    gh repo create $REPO_NAME --public --source=. --remote=origin --push
fi

# Create Cloudflare Pages configuration
cat > .cloudflare-pages.json << EOF
{
  "projectName": "saber-epc-public",
  "productionBranch": "main",
  "buildCommand": "echo 'No build needed'",
  "buildDirectory": ".",
  "envVars": {
    "DOMAIN": "$PUBLIC_DOMAIN",
    "API_ENDPOINT": "https://epc.$PUBLIC_DOMAIN/api"
  }
}
EOF

git add .cloudflare-pages.json
git commit -m "Add Cloudflare Pages config"
git push origin main

echo ""
echo "✅ Public portal ready for deployment!"
echo ""
echo "Next steps:"
echo "1. Go to Cloudflare Dashboard"
echo "2. Add domain: $PUBLIC_DOMAIN"
echo "3. Create Pages project linked to: $REPO_NAME"
echo "4. Add CNAME record: epc → saber-epc-public.pages.dev"
echo ""
echo "Portal will be available at: https://epc.$PUBLIC_DOMAIN"
echo "Test code: ABCD1234"

cd ..