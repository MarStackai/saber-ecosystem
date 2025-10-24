#!/bin/bash
# FIT Intelligence API Server Startup Script

echo "Starting FIT Intelligence API Server..."

# Change to project directory
cd /home/marstack/Projects/fit_intelligence

# Activate virtual environment
source venv/bin/activate

# Check if server is already running
if pgrep -f "python fit_api_server.py" > /dev/null; then
    echo "Server is already running. Stopping existing instance..."
    pkill -f "python fit_api_server.py"
    sleep 3
fi

# Start server in the background
echo "Starting server on port 5000..."
nohup python fit_api_server.py > server.log 2>&1 &

# Wait for server to start
sleep 10

# Check if server is running
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ FIT Intelligence API Server is running successfully"
    echo "🌐 Web interface: http://localhost:5000"
    echo "📊 API endpoints: http://localhost:5000/api/"
    echo "📋 Health check: http://localhost:5000/api/health"
    echo "📄 Server logs: tail -f server.log"
else
    echo "❌ Server failed to start. Check server.log for details."
    exit 1
fi