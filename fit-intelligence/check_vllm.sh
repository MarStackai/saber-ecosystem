#!/bin/bash

# Check vLLM installation status
echo "Checking vLLM installation status..."

while true; do
    if venv/bin/python3 -c "import vllm" 2>/dev/null; then
        echo "✅ vLLM is installed and ready!"
        echo "You can now switch to GPU inference."
        break
    else
        echo "⏳ Still installing vLLM... ($(date +%H:%M:%S))"
        sleep 30
    fi
done

echo ""
echo "Next steps:"
echo "1. Start vLLM server with GPU:"
echo "   venv/bin/python3 -m vllm.entrypoints.openai.api_server --model meta-llama/Llama-2-13b-hf --gpu-memory-utilization 0.9"
echo ""
echo "2. Update fit_api_server.py to use vLLMEnhancedFITChatbot"
echo ""
echo "3. Test with Aberdeen query to verify GPU acceleration"