#!/bin/bash
# Start the Advanced Saber Calculator (calc-proto-cl.py)
cd /home/marstack/Projects/saber-calculator/saber-calculator
export PATH="$HOME/.local/bin:$PATH"

echo "🚀 Starting Advanced Saber Calculator..."
echo "📱 Opening at: http://localhost:8502"
echo "⭐ Features: Full Saber branding, advanced modeling, export capabilities"
echo ""

streamlit run calc-proto-cl.py --server.port 8502