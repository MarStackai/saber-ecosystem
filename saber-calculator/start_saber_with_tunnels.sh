#!/bin/bash
# Start both Saber Calculators with Cloudflare Tunnels
# =================================================

cd /home/marstack/Projects/saber-calculator/saber-calculator
export PATH="$HOME/.local/bin:$PATH"

echo "🚀 Starting Saber Calculator Suite with Cloudflare Tunnels..."
echo "============================================================="
echo ""

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on a port
kill_port() {
    local port=$1
    echo "🔄 Stopping existing service on port $port..."
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        kill $pid
        sleep 2
    fi
}

# Function to start applications
start_applications() {
    echo "📱 Starting Streamlit Applications..."
    
    # Check and clear ports if needed
    if check_port 8501; then
        kill_port 8501
    fi
    if check_port 8502; then
        kill_port 8502
    fi
    
    # Start MVP Calculator
    echo "   🔷 Starting MVP Calculator (Basic PPA modeling)..."
    streamlit run app.py --server.port 8501 --server.headless true &
    MVP_PID=$!
    sleep 3
    
    # Start Advanced Calculator
    echo "   🔶 Starting Advanced Calculator (Full Saber branding)..."
    streamlit run calc-proto-cl.py --server.port 8502 --server.headless true &
    ADVANCED_PID=$!
    sleep 3
    
    echo "   ✅ Applications started successfully!"
}

# Function to start tunnel
start_tunnel() {
    echo "🌐 Starting Cloudflare Tunnel..."
    
    # Check if tunnel is already running
    if pgrep -f "cloudflared tunnel run" > /dev/null; then
        echo "   🔄 Stopping existing tunnel..."
        pkill -f "cloudflared tunnel run"
        sleep 2
    fi
    
    echo "   🚇 Starting tunnel 'ppa-saber'..."
    cloudflared tunnel run ppa-saber &
    TUNNEL_PID=$!
    sleep 5
    
    echo "   ✅ Tunnel started successfully!"
}

# Function to display URLs
show_urls() {
    echo ""
    echo "🎉 Saber Calculator Suite is now running!"
    echo "========================================"
    echo ""
    echo "📍 Local Access:"
    echo "   MVP Calculator:      http://localhost:8501"
    echo "   Advanced Calculator: http://localhost:8502"
    echo ""
    echo "🌍 Public Access (via Cloudflare Tunnel):"
    echo "   MVP Calculator:      https://ppa.saberrenewable.energy"
    echo "   Advanced Calculator: https://ppa-advanced.saberrenewable.energy"
    echo ""
    echo "⭐ Features:"
    echo "   📊 MVP: Basic PPA modeling, 10-year projections"
    echo "   🎨 Advanced: Full Saber branding, advanced modeling, export capabilities"
    echo ""
    echo "🛑 To stop all services, run: pkill -f 'streamlit\\|cloudflared'"
    echo ""
}

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down Saber Calculator Suite..."
    if [ ! -z "$MVP_PID" ]; then kill $MVP_PID 2>/dev/null; fi
    if [ ! -z "$ADVANCED_PID" ]; then kill $ADVANCED_PID 2>/dev/null; fi
    if [ ! -z "$TUNNEL_PID" ]; then kill $TUNNEL_PID 2>/dev/null; fi
    exit 0
}

# Trap cleanup on script exit
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    start_applications
    start_tunnel
    show_urls
    
    # Keep the script running
    echo "💫 Services are running. Press Ctrl+C to stop all services."
    wait
}

# Check if script is run with --help
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Saber Calculator Suite with Cloudflare Tunnels"
    echo "=============================================="
    echo ""
    echo "This script starts both Saber calculators and exposes them via Cloudflare tunnels:"
    echo "  • MVP Calculator (app.py) on port 8501"
    echo "  • Advanced Calculator (calc-proto-cl.py) on port 8502"
    echo "  • Cloudflare tunnel 'ppa-saber' for public access"
    echo ""
    echo "Usage: $0 [--help]"
    echo ""
    echo "Public URLs:"
    echo "  https://ppa.saberrenewable.energy (MVP)"
    echo "  https://ppa-advanced.saberrenewable.energy (Advanced)"
    exit 0
fi

# Run main function
main