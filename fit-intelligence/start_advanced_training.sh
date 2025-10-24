#!/bin/bash

# Advanced FIT Training Pipeline Launcher
# Runs all training phases once GPT-OSS is ready

set -e

echo "========================================"
echo "🚀 FIT Advanced Training Pipeline"
echo "========================================"
echo ""

# Check if venv exists
if [ -f "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
else
    PYTHON="python3"
fi

# Function to check if GPT-OSS is available
check_gpt_oss() {
    echo "🔍 Checking for GPT-OSS model..."
    
    # Check if model exists
    if ollama list 2>/dev/null | grep -q "gpt-oss"; then
        echo "✅ GPT-OSS model found!"
        return 0
    else
        # Check if still downloading
        if ps aux | grep -q "[o]llama pull gpt-oss"; then
            echo "⏳ GPT-OSS still downloading..."
            
            # Try to get progress
            timeout 2 ollama pull gpt-oss 2>&1 | grep -E "pulling|%" | tail -1 || true
            return 1
        else
            echo "❌ GPT-OSS not found and not downloading"
            echo "   Run: ollama pull gpt-oss"
            return 1
        fi
    fi
}

# Wait for GPT-OSS if still downloading
echo "📥 Waiting for GPT-OSS download to complete..."
while ! check_gpt_oss; do
    echo "   Checking again in 30 seconds..."
    sleep 30
done

echo ""
echo "========================================"
echo "Phase 1: Generate Training Data"
echo "========================================"
echo ""

# Generate training data if not exists
if [ ! -f "fit_training_data_*.jsonl" ]; then
    echo "📝 Generating 10,000 training examples..."
    $PYTHON create_fit_training_data.py
else
    echo "✅ Training data already exists"
    ls -lh fit_training_data_*.jsonl | head -1
fi

echo ""
echo "========================================"
echo "Phase 2: Fine-tune GPT-OSS"
echo "========================================"
echo ""

echo "🔧 Starting LoRA fine-tuning..."
$PYTHON lora_finetune_gpt_oss.py --model gpt-oss --output gpt-oss-fit --test

echo ""
echo "========================================"
echo "Phase 3: Test Enhanced System"
echo "========================================"
echo ""

# Test the fine-tuned model
echo "🧪 Testing GPT-OSS with FIT database..."
cat << 'EOF' | $PYTHON
import requests
import json

test_queries = [
    "Find wind farms in Scotland over 5MW",
    "What solar sites need repowering?",
    "Show me the highest FIT rates",
    "Compare renewable capacity by region"
]

print("Testing GPT-OSS integration:\n")

for query in test_queries:
    print(f"Q: {query}")
    
    # Query the model
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gpt-oss-fit",
                "prompt": query,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "max_tokens": 200
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            answer = response.json().get('response', 'No response')
            print(f"A: {answer[:200]}...\n")
        else:
            print(f"Error: Status {response.status_code}\n")
    except Exception as e:
        print(f"Error: {e}\n")
        
        # Fallback to base model
        print("Trying base gpt-oss model...")
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "gpt-oss",
                    "prompt": f"You are an expert in renewable energy. {query}",
                    "stream": False
                },
                timeout=30
            )
            if response.status_code == 200:
                answer = response.json().get('response', 'No response')
                print(f"A: {answer[:200]}...\n")
        except:
            pass

print("\n✅ Testing complete!")
EOF

echo ""
echo "========================================"
echo "Phase 4: Launch Interactive System"
echo "========================================"
echo ""

echo "🎯 Launching GPT-OSS FIT Chatbot..."
echo "   Use Ctrl+C to exit"
echo ""

# Launch the interactive chatbot
$PYTHON gpt_oss_fit_chatbot.py

echo ""
echo "========================================"
echo "✅ Training Pipeline Complete!"
echo "========================================"
echo ""
echo "📊 Summary:"
echo "   - Training data generated"
echo "   - GPT-OSS fine-tuned for FIT domain"
echo "   - System tested and ready"
echo ""
echo "🚀 Next steps:"
echo "   1. Run chatbot: python3 gpt_oss_fit_chatbot.py"
echo "   2. Deploy API: python3 deploy_hybrid_fit_system.py"
echo "   3. Monitor performance: watch -n 1 nvidia-smi"