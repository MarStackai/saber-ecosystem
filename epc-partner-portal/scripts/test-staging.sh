#!/bin/bash

# Test Staging Environment Script
# This script runs tests against the staging environment

set -e

echo "🧪 Testing Staging Environment"
echo "=============================="
echo "URL: https://staging-epc.saberrenewable.energy"
echo ""

# Check if Playwright is installed
if ! npx playwright --version > /dev/null 2>&1; then
    echo "Installing Playwright..."
    npm install -D @playwright/test
    npx playwright install --with-deps
fi

# Export environment variables
export TEST_ENV=staging
export PLAYWRIGHT_BASE_URL=https://staging-epc.saberrenewable.energy

echo "🌐 Testing API endpoints..."
echo "----------------------------"

# Test Worker health
echo -n "Worker health check: "
if curl -s -f https://staging-epc.saberrenewable.energy/api/health > /dev/null 2>&1; then
    echo "✅ Passed"
else
    echo "⚠️  Not implemented or failed"
fi

# Test admin API (should return 401 or 200)
echo -n "Admin API check: "
response=$(curl -s -o /dev/null -w "%{http_code}" https://staging-epc.saberrenewable.energy/api/admin/projects)
if [ "$response" -eq 401 ] || [ "$response" -eq 200 ]; then
    echo "✅ Passed (status: $response)"
else
    echo "❌ Failed (status: $response)"
fi

# Test frontend
echo -n "Frontend check: "
if curl -s -f https://staging-epc.saberrenewable.energy > /dev/null 2>&1; then
    echo "✅ Passed"
else
    echo "❌ Failed"
fi

echo ""
echo "🎭 Running Playwright tests..."
echo "----------------------------"

# Run Playwright tests
TEST_ENV=staging npx playwright test --reporter=list

echo ""
echo "📊 Performance check..."
echo "----------------------------"

# Measure response time
response_time=$(curl -o /dev/null -s -w '%{time_total}' https://staging-epc.saberrenewable.energy)
echo "Homepage response time: ${response_time}s"

# Check if response time is acceptable
if (( $(echo "$response_time < 3" | bc -l) )); then
    echo "✅ Performance: Excellent (<3s)"
elif (( $(echo "$response_time < 5" | bc -l) )); then
    echo "⚠️  Performance: Acceptable (3-5s)"
else
    echo "❌ Performance: Poor (>5s)"
fi

echo ""
echo "✨ Staging tests completed!"
echo ""
echo "View detailed Playwright report:"
echo "npx playwright show-report"