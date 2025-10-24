#!/usr/bin/env python3
"""
Start vLLM with TinyLlama for quick testing
"""

import subprocess
import sys
import os

# Kill any existing vLLM
subprocess.run(["pkill", "-f", "vllm"], stderr=subprocess.DEVNULL)

env = os.environ.copy()
env['CUDA_VISIBLE_DEVICES'] = '0'  # Only use RTX 3090, not M2000
env['LD_LIBRARY_PATH'] = '/usr/local/cuda-12/lib64:' + env.get('LD_LIBRARY_PATH', '')
env['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'  # Ensure consistent ordering

cmd = [
    sys.executable,
    "-m", "vllm.entrypoints.openai.api_server",
    "--model", "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "--host", "0.0.0.0",
    "--port", "8000",
    "--dtype", "float16",
    "--gpu-memory-utilization", "0.5",
    "--max-model-len", "2048",
    "--trust-remote-code",
    "--tensor-parallel-size", "1"  # Explicitly use only 1 GPU
]

print("Starting vLLM with TinyLlama...")
subprocess.run(cmd, env=env)