#!/usr/bin/env python3
"""
Start vLLM with Llama-2-13B-chat AWQ using legacy engine
The V1 engine has issues, use V0 engine which is more stable
"""

import subprocess
import sys
import os

def start_vllm_server():
    """Start vLLM server with Llama-2-13B-chat AWQ"""
    
    model = "TheBloke/Llama-2-13B-chat-AWQ"
    
    print("=" * 60)
    print("Starting vLLM with Llama-2-13B-chat (AWQ) - Legacy Engine")
    print("=" * 60)
    print(f"Model: {model}")
    print("Quantization: AWQ (4-bit)")
    print("Engine: Legacy (V0) for stability")
    print("GPU: RTX 3090 (24GB)")
    print("-" * 60)
    
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = '0'  # Only RTX 3090
    env['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
    env['LD_LIBRARY_PATH'] = '/usr/local/cuda-12/lib64:' + env.get('LD_LIBRARY_PATH', '')
    env['VLLM_USE_V1'] = '0'  # Force legacy engine
    
    # Kill any existing vLLM
    subprocess.run(["pkill", "-f", "vllm"], stderr=subprocess.DEVNULL)
    
    cmd = [
        sys.executable,
        "-m", "vllm.entrypoints.openai.api_server",
        "--model", model,
        "--served-model-name", "fit-intel-13b-awq",
        "--quantization", "awq_marlin",  # Use optimized AWQ
        "--host", "0.0.0.0",
        "--port", "8000",
        "--gpu-memory-utilization", "0.85",
        "--max-model-len", "4096",
        "--trust-remote-code",
        "--dtype", "float16",
        "--disable-frontend-multiprocessing"  # Simpler setup
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