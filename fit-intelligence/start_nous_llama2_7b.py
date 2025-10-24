#!/usr/bin/env python3
"""
Start vLLM with NousResearch Llama-2-7B-chat (ungated version)
Using port 8001 to test if port 8000 is the issue
"""

import subprocess
import sys
import os

def start_vllm_server():
    """Start vLLM server with NousResearch Llama-2-7B-chat"""
    
    # Ungated version of Llama-2-7B
    model = "NousResearch/Llama-2-7b-chat-hf"
    
    print("=" * 60)
    print("Starting vLLM with Llama-2-7B-chat (ungated)")
    print("=" * 60)
    print(f"Model: {model}")
    print("Size: ~13GB")
    print("Port: 8001 (testing different port)")
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
        "--port", "8001",  # Different port to test
        "--gpu-memory-utilization", "0.75",
        "--max-model-len", "2048",
        "--dtype", "float16"
    ]
    
    print("Command:", " ".join(cmd))
    print("-" * 60)
    print("Starting server...")
    print("Server will be available at http://localhost:8001")
    print("-" * 60)
    
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_vllm_server()