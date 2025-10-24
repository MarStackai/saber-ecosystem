#!/usr/bin/env python3
"""
Start vLLM server with GPU acceleration
Uses a smaller model for testing
"""

import subprocess
import sys
import os

def start_vllm_server():
    """Start vLLM server with GPU"""
    
    # Use TinyLlama for quick testing (1.1B parameters, fits easily in GPU)
    model = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    
    print("=" * 60)
    print("Starting vLLM Server with GPU Acceleration")
    print("=" * 60)
    print(f"Model: {model}")
    print("GPU: RTX 3090 (24GB)")
    print("-" * 60)
    
    # Set environment variables for GPU
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = '0'  # Use RTX 3090
    
    # Start vLLM server
    cmd = [
        sys.executable,
        "-m", "vllm.entrypoints.openai.api_server",
        "--model", model,
        "--host", "0.0.0.0",
        "--port", "8000",
        "--gpu-memory-utilization", "0.8",  # Use 80% of GPU memory
        "--max-model-len", "2048",
        "--dtype", "float16",  # Use FP16 for speed
        "--trust-remote-code",
    ]
    
    print("Command:", " ".join(cmd))
    print("-" * 60)
    print("Server will start on http://localhost:8000")
    print("API endpoints:")
    print("  - /v1/completions")
    print("  - /v1/models")
    print("  - /health")
    print("-" * 60)
    print("Starting server...")
    
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_vllm_server()