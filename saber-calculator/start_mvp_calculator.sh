#!/bin/bash
# Start the MVP Saber Calculator (app.py)
cd /home/marstack/Projects/saber-calculator/saber-calculator
export PATH="$HOME/.local/bin:$PATH"

echo "🚀 Starting MVP Saber Calculator..."
echo "📱 Opening at: http://localhost:8501"
echo "⭐ Features: Basic PPA modeling, 10-year projections"
echo ""

streamlit run app.py --server.port 8501