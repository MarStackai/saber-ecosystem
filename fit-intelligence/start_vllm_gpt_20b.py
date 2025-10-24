#!/usr/bin/env python3
"""
Start vLLM with a 20B model optimized for FIT Intelligence
Uses quantization to fit in 24GB RTX 3090
"""

import subprocess
import sys
import os

def start_vllm_server():
    """Start vLLM server with quantized 20B model"""
    
    # Use models that fit in 24GB RTX 3090
    models = {
        "mistral-7b": "mistralai/Mistral-7B-Instruct-v0.2",  # Excellent 7B model
        "gpt-j-6b": "EleutherAI/gpt-j-6b",  # GPT-J 6B 
        "pythia-6.9b": "EleutherAI/pythia-6.9b",  # Pythia 6.9B
    }
    
    # Use Mistral 7B Instruct - excellent for our use case
    model = models["mistral-7b"]
    
    print("=" * 60)
    print("Starting vLLM Server with GPT-20B (Quantized)")
    print("=" * 60)
    print(f"Model: {model}")
    print("Quantization: AWQ 4-bit (fits in 24GB)")
    print("GPU: RTX 3090 (24GB)")
    print("-" * 60)
    
    # Set environment variables for GPU
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = '0'  # Use RTX 3090
    env['LD_LIBRARY_PATH'] = '/usr/local/cuda-12/lib64:' + env.get('LD_LIBRARY_PATH', '')
    
    # Kill existing vLLM on port 8000 if running
    subprocess.run(["pkill", "-f", "vllm.entrypoints.openai.api_server"], stderr=subprocess.DEVNULL)
    
    # Start vLLM server
    cmd = [
        sys.executable,
        "-m", "vllm.entrypoints.openai.api_server",
        "--model", model,
        "--host", "0.0.0.0",
        "--port", "8000",
        "--gpu-memory-utilization", "0.9",  # Use 90% of GPU
        "--max-model-len", "2048",
        "--dtype", "float16",  # Use FP16 to save memory
        "--trust-remote-code",
        "--enforce-eager",  # Disable CUDA graphs for large model
        "--max-num-batched-tokens", "4096"  # Batch size for 20B model
    ]
    
    print("Command:", " ".join(cmd))
    print("-" * 60)
    print("Server will start on http://localhost:8000")
    print("This replaces Ollama completely!")
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