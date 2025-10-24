#!/usr/bin/env python3
"""
Start vLLM with Phi-3-mini-4k-instruct (3.8B parameters)
This model fits easily in 24GB and provides good performance
"""

import subprocess
import sys
import os

def start_vllm_server():
    """Start vLLM server with Phi-3-mini"""
    
    # Phi-3-mini is a strong 3.8B model from Microsoft
    model = "microsoft/Phi-3-mini-4k-instruct"
    
    print("=" * 60)
    print("Starting vLLM with Phi-3-mini (GPU Accelerated)")
    print("=" * 60)
    print(f"Model: {model}")
    print("Size: ~4GB (fits easily in 24GB)")
    print("GPU: RTX 3090 (24GB)")
    print("-" * 60)
    
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = '0'  # Only RTX 3090
    env['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
    env['LD_LIBRARY_PATH'] = '/usr/local/cuda-12/lib64:' + env.get('LD_LIBRARY_PATH', '')
    
    # Kill any existing vLLM
    subprocess.run(["pkill", "-f", "vllm"], stderr=subprocess.DEVNULL)
    
    cmd = [
        sys.executable,
        "-m", "vllm.entrypoints.openai.api_server",
        "--model", model,
        "--host", "0.0.0.0",
        "--port", "8000",
        "--dtype", "float16",
        "--gpu-memory-utilization", "0.9",
        "--max-model-len", "4096",
        "--trust-remote-code",
        "--tensor-parallel-size", "1"
    ]
    
    print("Command:", " ".join(cmd))
    print("-" * 60)
    print("Starting server...")
    print("This model will download on first run (~4GB)")
    
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_vllm_server()