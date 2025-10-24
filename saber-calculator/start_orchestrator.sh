#!/bin/bash

# Saber Calculator Orchestrator Startup Script
# ===========================================

echo "🚀 Starting Saber Calculator Orchestrator..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "orchestrator.py" ]; then
    echo "❌ orchestrator.py not found. Please run this from the project directory."
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
if ! python3 -c "import psutil" 2>/dev/null; then
    echo "Installing required packages..."
    pip3 install psutil requests
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [ACTION] [SERVICES...]"
    echo ""
    echo "Actions:"
    echo "  run          Run the orchestrator (default)"
    echo "  start        Start specified services"
    echo "  stop         Stop specified services"
    echo "  restart      Restart specified services"
    echo "  status       Show status of all services"
    echo ""
    echo "Services:"
    echo "  streamlit    Streamlit web application"
    echo "  ai_agent     AI agent service"
    echo "  monitor      System monitoring service"
    echo ""
    echo "Options:"
    echo "  --no-monitor Disable automatic service monitoring"
    echo "  --daemon     Run in background"
    echo ""
    echo "Examples:"
    echo "  $0                           # Start streamlit with monitoring"
    echo "  $0 run streamlit ai_agent    # Start specific services"
    echo "  $0 status                    # Show status"
    echo "  $0 stop                      # Stop all services"
}

# Parse arguments
ACTION="run"
SERVICES=""
MONITOR_FLAG=""
DAEMON_FLAG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        --no-monitor)
            MONITOR_FLAG="--no-monitor"
            shift
            ;;
        --daemon)
            DAEMON_FLAG="--daemon"
            shift
            ;;
        run|start|stop|restart|status)
            ACTION="$1"
            shift
            ;;
        streamlit|ai_agent|monitor)
            SERVICES="$SERVICES $1"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Build command
CMD="python3 orchestrator.py $ACTION $MONITOR_FLAG $DAEMON_FLAG"
if [ ! -z "$SERVICES" ]; then
    CMD="$CMD --services$SERVICES"
fi

echo "🎯 Executing: $CMD"
echo ""

# Run the orchestrator
if [ "$DAEMON_FLAG" = "--daemon" ]; then
    nohup $CMD > orchestrator.log 2>&1 &
    echo "✅ Orchestrator started in background (PID: $!)"
    echo "📝 Check orchestrator.log for output"
else
    exec $CMD
fi
