#!/usr/bin/env python3
"""
Start vLLM with Llama-2-13B-chat AWQ quantized
Perfect for structured extraction at temp=0.1
Fits comfortably in RTX 3090 24GB
"""

import subprocess
import sys
import os

def start_vllm_server():
    """Start vLLM server with Llama-2-13B-chat AWQ"""
    
    # AWQ quantized version for 24GB GPU
    model = "TheBloke/Llama-2-13B-chat-AWQ"
    
    print("=" * 60)
    print("Starting vLLM with Llama-2-13B-chat (AWQ Quantized)")
    print("=" * 60)
    print(f"Model: {model}")
    print("Quantization: AWQ (4-bit)")
    print("Size: ~7GB (fits comfortably in 24GB)")
    print("GPU: RTX 3090 (24GB)")
    print("-" * 60)
    
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = '0'  # Only RTX 3090, not M2000
    env['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
    env['LD_LIBRARY_PATH'] = '/usr/local/cuda-12/lib64:' + env.get('LD_LIBRARY_PATH', '')
    
    # Kill any existing vLLM servers
    subprocess.run(["pkill", "-f", "vllm"], stderr=subprocess.DEVNULL)
    
    cmd = [
        sys.executable,
        "-m", "vllm.entrypoints.openai.api_server",
        "--model", model,
        "--served-model-name", "fit-intel-13b-awq",
        "--quantization", "awq",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--gpu-memory-utilization", "0.80",  # Conservative for stability
        "--max-model-len", "4096",
        "--trust-remote-code",
        "--dtype", "float16",
        "--tensor-parallel-size", "1"
    ]
    
    print("Command:", " ".join(cmd))
    print("-" * 60)
    print("Starting server...")
    print("Model will download on first run (~7GB)")
    print("Server will be available at http://localhost:8000")
    print("-" * 60)
    
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_vllm_server()