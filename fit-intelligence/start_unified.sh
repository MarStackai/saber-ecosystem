#!/bin/bash
# Start the Unified FIT Intelligence Platform

echo "=================================="
echo "Starting FIT Intelligence Platform"
echo "=================================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the unified server
python3 unified_server.py