#!/usr/bin/env python3
"""
Start vLLM with official GPT-OSS 20B model
Optimized for 24GB RTX 3090
"""

import subprocess
import sys
import os

def start_vllm_server():
    """Start vLLM server with GPT-OSS 20B"""
    
    # Official GPT-OSS model from OpenAI
    model = "openai/gpt-oss-20b"
    
    print("=" * 60)
    print("Starting vLLM Server with GPT-OSS 20B")
    print("=" * 60)
    print(f"Model: {model}")
    print("Quantization: MXFP4 (built-in)")
    print("GPU: RTX 3090 (24GB)")
    print("Expected VRAM: ~16GB")
    print("-" * 60)
    
    # Set environment variables for GPU
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = '0'  # Use RTX 3090
    env['LD_LIBRARY_PATH'] = '/usr/local/cuda-12/lib64:' + env.get('LD_LIBRARY_PATH', '')
    
    # Kill existing vLLM if running
    subprocess.run(["pkill", "-f", "vllm"], stderr=subprocess.DEVNULL)
    
    # Start vLLM server using the simple serve command
    cmd = [
        sys.executable,
        "-m", "vllm.entrypoints.openai.api_server",
        "--model", model,
        "--host", "0.0.0.0",
        "--port", "8000",
        "--gpu-memory-utilization", "0.9",
        "--max-model-len", "4096",
        "--trust-remote-code"
    ]
    
    print("Command:", " ".join(cmd))
    print("-" * 60)
    print("Server will start on http://localhost:8000")
    print("This is the OFFICIAL GPT-OSS from OpenAI!")
    print("Replaces Ollama completely with GPU acceleration!")
    print("-" * 60)
    print("Starting server...")
    
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: If model not found, it may need special vLLM version")
        print("Try: venv/bin/vllm serve openai/gpt-oss-20b")

if __name__ == "__main__":
    start_vllm_server()