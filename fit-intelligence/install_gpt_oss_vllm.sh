#!/bin/bash

echo "==========================================="
echo "Installing vLLM with GPT-OSS Support"
echo "==========================================="

# Activate virtual environment
source venv/bin/activate

# Install special vLLM version with GPT-OSS support
echo "Installing vLLM 0.10.1+gptoss..."
pip install --pre vllm==0.10.1+gptoss \
    --extra-index-url https://wheels.vllm.ai/gpt-oss/ \
    --extra-index-url https://download.pytorch.org/whl/nightly/cu128 \
    --index-strategy unsafe-best-match

echo ""
echo "Installation complete!"
echo ""
echo "To start GPT-OSS 20B server (fits in 24GB):"
echo "  vllm serve openai/gpt-oss-20b"
echo ""
echo "The model is MXFP4 quantized and optimized for inference"
echo "==========================================="