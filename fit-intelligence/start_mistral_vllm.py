#!/usr/bin/env python3
"""
Start vLLM with Mistral 7B for testing FIT Intelligence
"""

import subprocess
import sys
import os

def start_vllm_server():
    """Start vLLM server with Mistral 7B"""
    
    model = "mistralai/Mistral-7B-Instruct-v0.2"
    
    print("=" * 60)
    print("Starting vLLM with Mistral 7B (GPU Accelerated)")
    print("=" * 60)
    print(f"Model: {model}")
    print("GPU: RTX 3090 (24GB)")
    print("-" * 60)
    
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = '0'  # Only use RTX 3090, not M2000
    env['LD_LIBRARY_PATH'] = '/usr/local/cuda-12/lib64:' + env.get('LD_LIBRARY_PATH', '')
    env['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'  # Ensure consistent ordering
    
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
        "--tensor-parallel-size", "1"  # Explicitly use only 1 GPU
    ]
    
    print("Command:", " ".join(cmd))
    print("-" * 60)
    print("Starting server...")
    
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_vllm_server()