#!/bin/bash

# EPC Portal Staging Deployment Script
# This script deploys both Worker and Pages to staging environment

set -e

echo "🚀 Deploying EPC Portal to Staging Environment"
echo "=============================================="

# Load staging environment variables
if [ -f .env.staging ]; then
    export $(cat .env.staging | grep -v '^#' | xargs)
    echo "✅ Loaded staging environment variables"
else
    echo "❌ .env.staging file not found!"
    exit 1
fi

# Verify we're on staging branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "staging" ]; then
    echo "⚠️  Current branch is '$CURRENT_BRANCH', expected 'staging'"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  You have uncommitted changes"
    read -p "Continue with deployment? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📦 Deploying Cloudflare Worker to staging..."
npx wrangler deploy --env staging

echo "🏗️  Building Next.js application for staging..."
cd epc-portal-react

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm ci
fi

# Build the application
npm run build

echo "🌐 Deploying Pages to staging..."
CLOUDFLARE_API_TOKEN=$CLOUDFLARE_API_TOKEN CLOUDFLARE_ACCOUNT_ID=$CLOUDFLARE_ACCOUNT_ID \
npx wrangler pages deploy .vercel/output/static \
    --project-name=saber-epc-portal \
    --branch=staging \
    --commit-dirty=true

cd ..

echo ""
echo "🎉 Staging deployment completed successfully!"
echo "==========================================="
echo "🌐 Staging URL: https://staging-epc.saberrenewable.energy"
echo "⚙️  Worker URL: https://saber-epc-portal-staging.robjamescarroll.workers.dev"
echo "📋 Form: https://staging-epc.saberrenewable.energy/form?invitationCode=TEST001"
echo ""
echo "🧪 Testing staging deployment..."

# Simple health check
if curl -s -f "https://saber-epc-portal-staging.robjamescarroll.workers.dev/api/health" > /dev/null; then
    echo "✅ Worker health check passed"
else
    echo "❌ Worker health check failed"
fi

echo ""
echo "📝 Next steps:"
echo "1. Test the staging environment thoroughly"
echo "2. Run Playwright tests: npm run test:e2e"
echo "3. If all tests pass, merge to main for production deployment"