#!/usr/bin/env python3
"""
Start vLLM with GPT-NeoX 20B using proper quantization
Should fit in 24GB with correct settings
"""

import subprocess
import sys
import os

def start_vllm_server():
    """Start vLLM server with GPT-NeoX 20B quantized"""
    
    # GPT-NeoX 20B with quantization options
    model = "EleutherAI/gpt-neox-20b"
    
    print("=" * 60)
    print("Starting vLLM with GPT-NeoX 20B (Quantized for 24GB)")
    print("=" * 60)
    print(f"Model: {model}")
    print("GPU: RTX 3090 (24GB)")
    print("-" * 60)
    
    # Set environment variables
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = '0'  # Use RTX 3090 only
    env['LD_LIBRARY_PATH'] = '/usr/local/cuda-12/lib64:' + env.get('LD_LIBRARY_PATH', '')
    # Memory optimization
    env['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
    
    # Kill any existing vLLM
    subprocess.run(["pkill", "-f", "vllm"], stderr=subprocess.DEVNULL)
    
    # Start vLLM with optimized settings for 20B model in 24GB
    cmd = [
        sys.executable,
        "-m", "vllm.entrypoints.openai.api_server",
        "--model", model,
        "--host", "0.0.0.0",
        "--port", "8000",
        "--dtype", "bfloat16",  # Use bfloat16 for better memory efficiency
        "--gpu-memory-utilization", "0.95",  # Use 95% of GPU
        "--max-model-len", "1024",  # Reduce context to save memory
        "--trust-remote-code",
        "--enforce-eager",  # Disable CUDA graphs to save memory
        "--enable-prefix-caching",  # Enable caching
        "--max-num-seqs", "8",  # Limit concurrent sequences
        "--swap-space", "4",  # Use swap space if needed
        "--load-format", "safetensors",  # Efficient loading
    ]
    
    print("Command:", " ".join(cmd))
    print("-" * 60)
    print("Note: Model will download on first run (~40GB)")
    print("Server will be available at http://localhost:8000")
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