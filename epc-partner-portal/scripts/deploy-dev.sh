#!/bin/bash

# EPC Portal Development Deployment Script
# This script starts local development servers for both frontend and backend

set -e

echo "🚀 Starting EPC Portal Development Environment"
echo "=============================================="

# Load development environment variables
if [ -f .env.development ]; then
    export $(cat .env.development | grep -v '^#' | xargs)
    echo "✅ Loaded development environment variables"
else
    echo "❌ .env.development file not found!"
    exit 1
fi

# Check if ports are available
if lsof -Pi :3001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 3001 is already in use"
    read -p "Kill existing process? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pkill -f "next dev" || true
        sleep 2
    fi
fi

if lsof -Pi :8787 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8787 is already in use"
    read -p "Kill existing process? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pkill -f "wrangler dev" || true
        sleep 2
    fi
fi

# Start Cloudflare Worker (backend)
echo "🔧 Starting Cloudflare Worker on port 8787..."
npx wrangler dev --local --port 8787 &
WORKER_PID=$!

# Wait for worker to start
sleep 3

# Start Next.js frontend
echo "🌐 Starting Next.js frontend on port 3001..."
cd epc-portal-react
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "🎉 Development environment started successfully!"
echo "================================================"
echo "📱 Frontend: http://localhost:3001"
echo "⚙️  Worker API: http://localhost:8787"
echo "📋 Form: http://localhost:3001/form?invitationCode=TEST001"
echo "🔧 Admin: http://localhost:3001/admin"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to handle cleanup
cleanup() {
    echo ""
    echo "🛑 Stopping development servers..."
    kill $WORKER_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    pkill -f "next dev" 2>/dev/null || true
    pkill -f "wrangler dev" 2>/dev/null || true
    echo "✅ Development environment stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for processes
wait