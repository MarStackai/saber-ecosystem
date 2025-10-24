#!/bin/bash
export CUDA_VISIBLE_DEVICES=0
export CUDA_DEVICE_ORDER=PCI_BUS_ID
export LD_LIBRARY_PATH=/usr/local/cuda-12/lib64:$LD_LIBRARY_PATH

echo "Starting vLLM with TinyLlama on RTX 3090 only..."
echo "CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"

/home/marstack/fit_intelligence/venv/bin/python -m vllm.entrypoints.openai.api_server \
    --model TinyLlama/TinyLlama-1.1B-Chat-v1.0 \
    --host 0.0.0.0 \
    --port 8000 \
    --dtype float16 \
    --gpu-memory-utilization 0.5 \
    --max-model-len 2048 \
    --trust-remote-code \
    --tensor-parallel-size 1