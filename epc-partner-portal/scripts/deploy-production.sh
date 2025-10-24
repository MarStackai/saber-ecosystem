#!/bin/bash

# EPC Portal Production Deployment Script
# This script deploys both Worker and Pages to production environment

set -e

echo "🚀 Deploying EPC Portal to Production Environment"
echo "================================================"

# Load production environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
    echo "✅ Loaded production environment variables"
else
    echo "❌ .env.production file not found!"
    exit 1
fi

# Verify we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "❌ Production deployments must be from 'main' branch"
    echo "   Current branch: '$CURRENT_BRANCH'"
    exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Cannot deploy to production with uncommitted changes"
    echo "   Please commit or stash your changes first"
    exit 1
fi

# Ensure we have the latest changes
echo "📥 Fetching latest changes..."
git fetch origin main

if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
    echo "❌ Local main branch is not up to date with origin/main"
    echo "   Please pull the latest changes: git pull origin main"
    exit 1
fi

echo ""
echo "⚠️  PRODUCTION DEPLOYMENT WARNING ⚠️"
echo "===================================="
echo "This will deploy to the live production environment:"
echo "• Frontend: https://epc.saberrenewable.energy"
echo "• Worker: https://saber-epc-portal.robjamescarroll.workers.dev"
echo ""
echo "Please ensure:"
echo "✅ All tests have passed"
echo "✅ Staging environment has been thoroughly tested"
echo "✅ This deployment has been approved"
echo ""

read -p "Are you sure you want to deploy to PRODUCTION? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ Production deployment cancelled"
    exit 1
fi

echo ""
echo "📦 Deploying Cloudflare Worker to production..."
npx wrangler deploy --env production

echo "🏗️  Building Next.js application for production..."
cd epc-portal-react

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm ci
fi

# Build the application
npm run build

echo "🌐 Deploying Pages to production..."
CLOUDFLARE_API_TOKEN=$CLOUDFLARE_API_TOKEN CLOUDFLARE_ACCOUNT_ID=$CLOUDFLARE_ACCOUNT_ID \
npx wrangler pages deploy .vercel/output/static \
    --project-name=saber-epc-portal \
    --branch=main \
    --commit-dirty=true

cd ..

echo ""
echo "🎉 Production deployment completed successfully!"
echo "=============================================="
echo "🌐 Production URL: https://epc.saberrenewable.energy"
echo "⚙️  Worker URL: https://saber-epc-portal.robjamescarroll.workers.dev"
echo "📋 Form: https://epc.saberrenewable.energy/form"
echo ""
echo "🧪 Testing production deployment..."

# Simple health check
if curl -s -f "https://saber-epc-portal.robjamescarroll.workers.dev/api/health" > /dev/null; then
    echo "✅ Worker health check passed"
else
    echo "❌ Worker health check failed"
fi

# Check if the domain responds
if curl -s -f "https://epc.saberrenewable.energy" > /dev/null; then
    echo "✅ Frontend health check passed"
else
    echo "❌ Frontend health check failed"
fi

echo ""
echo "📝 Post-deployment tasks:"
echo "1. Monitor application logs for any errors"
echo "2. Test key user journeys"
echo "3. Monitor performance metrics"
echo "4. Notify stakeholders of successful deployment"
echo ""
echo "🚨 If issues are detected, run: git revert HEAD && ./scripts/deploy-production.sh"