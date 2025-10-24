#!/bin/bash

# EPC Portal Test Runner Script
# This script runs Puppeteer tests for both admin and partner processes

echo "================================"
echo "EPC Portal Testing Suite"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if services are running
check_service() {
    local port=$1
    local name=$2

    if nc -z localhost $port 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $name is running on port $port"
        return 0
    else
        echo -e "${RED}✗${NC} $name is NOT running on port $port"
        return 1
    fi
}

echo "Checking services..."
echo "-------------------"

# Check if Next.js is running
check_service 4200 "Next.js Frontend"
FRONTEND_STATUS=$?

# Check if Wrangler is running
check_service 8787 "Wrangler Backend"
BACKEND_STATUS=$?

echo ""

# Warn if services are not running
if [ $FRONTEND_STATUS -ne 0 ] || [ $BACKEND_STATUS -ne 0 ]; then
    echo -e "${YELLOW}⚠ Warning: Some services are not running${NC}"
    echo "Please ensure both services are started:"
    echo "  Frontend: npm run dev (port 4200)"
    echo "  Backend: npx wrangler dev --local --port 8787"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Select test suite
echo "Select test suite to run:"
echo "1) Admin Portal Tests"
echo "2) EPC Partner Portal Tests"
echo "3) Both Test Suites"
echo "4) Quick Smoke Test"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Running Admin Portal Tests..."
        echo "============================="
        npx jest tests/puppeteer/admin-processes.test.js --verbose
        ;;
    2)
        echo ""
        echo "Running EPC Partner Portal Tests..."
        echo "==================================="
        npx jest tests/puppeteer/epc-partner-processes.test.js --verbose
        ;;
    3)
        echo ""
        echo "Running All Tests..."
        echo "===================="
        npx jest tests/puppeteer/*.test.js --verbose
        ;;
    4)
        echo ""
        echo "Running Quick Smoke Test..."
        echo "==========================="
        # Quick test to verify basic functionality
        node -e "
        const puppeteer = require('puppeteer');
        (async () => {
            const browser = await puppeteer.launch({ headless: true });
            const page = await browser.newPage();

            console.log('Testing homepage...');
            await page.goto('http://localhost:4200', { waitUntil: 'networkidle2' });
            const title = await page.title();
            console.log('  Title:', title);

            console.log('Testing admin page...');
            await page.goto('http://localhost:4200/admin', { waitUntil: 'networkidle2' });
            const adminTitle = await page.\$eval('h1', el => el.textContent).catch(() => 'Not found');
            console.log('  Admin Title:', adminTitle);

            console.log('Testing apply page...');
            await page.goto('http://localhost:4200/apply', { waitUntil: 'networkidle2' });
            const applyTitle = await page.\$eval('h2', el => el.textContent).catch(() => 'Not found');
            console.log('  Apply Title:', applyTitle);

            await browser.close();
            console.log('\\n✓ Smoke test completed');
        })().catch(console.error);
        "
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Testing completed!"