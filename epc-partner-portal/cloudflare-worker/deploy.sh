#!/bin/bash

# Deploy Cloudflare Worker for EPC Portal API
# Run this after signing into 1Password with: eval $(op signin)

echo "Deploying EPC Portal API Worker..."

# Get API token from 1Password
export CLOUDFLARE_API_TOKEN=$(op read "op://MCP/Cloudflare/API Token")

if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo "Error: Could not retrieve Cloudflare API token from 1Password"
    echo "Please run: eval \$(op signin)"
    exit 1
fi

# Deploy the worker
cd /home/marstack/saber_business_ops/cloudflare-worker
npx wrangler deploy

echo "Worker deployed successfully!"
echo ""
echo "API Endpoint: https://epc.saberrenewable.energy/api/submit"
echo ""
echo "Next steps:"
echo "1. Test the form at https://epc.saberrenewable.energy"
echo "2. Use invitation code: ABCD1234 (add to SharePoint if needed)"
echo "3. Check Power Automate flow runs for submissions"