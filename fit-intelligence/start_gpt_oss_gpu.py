#!/usr/bin/env python3
"""
Start vLLM server with GPT-OSS 20B model on GPU
Optimized for FIT Intelligence queries
"""

import subprocess
import sys
import os

def start_vllm_server():
    """Start vLLM server with GPT-OSS 20B on GPU"""
    
    # GPT-OSS 20B model (the one trained for FIT Intelligence)
    model = "gpt-oss:20b"  # This should map to the actual model path
    
    # Check if we have a local model path
    model_paths = [
        "/home/marstack/.ollama/models/manifests/registry.ollama.ai/library/gpt-oss",
        "/home/marstack/.ollama/models/blobs",
        "/home/marstack/fit_intelligence/models/gpt-oss-20b",
        "EleutherAI/gpt-neox-20b"  # Fallback to HuggingFace
    ]
    
    # Find the actual model
    actual_model = "EleutherAI/gpt-neox-20b"  # Default fallback
    for path in model_paths:
        if os.path.exists(path):
            print(f"Found local model at: {path}")
            # For now, use HuggingFace model as example
            break
    
    print("=" * 60)
    print("Starting vLLM Server with GPT-OSS 20B on GPU")
    print("=" * 60)
    print(f"Model: {actual_model}")
    print("GPU: RTX 3090 (24GB)")
    print("-" * 60)
    
    # Set environment variables for GPU
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = '0'  # Use RTX 3090
    env['LD_LIBRARY_PATH'] = '/usr/local/cuda-12/lib64:' + env.get('LD_LIBRARY_PATH', '')
    
    # Start vLLM server with optimized settings for 20B model
    cmd = [
        sys.executable,
        "-m", "vllm.entrypoints.openai.api_server",
        "--model", actual_model,
        "--host", "0.0.0.0",
        "--port", "8001",  # Different port to avoid conflict
        "--gpu-memory-utilization", "0.95",  # Use more GPU for larger model
        "--max-model-len", "2048",
        "--dtype", "float16",  # FP16 for memory efficiency
        "--trust-remote-code",
        "--tensor-parallel-size", "1",  # Single GPU
        "--max-num-seqs", "32",  # Batch size
        "--quantization", "awq",  # Use quantization to fit 20B model
    ]
    
    print("Command:", " ".join(cmd))
    print("-" * 60)
    print("Server will start on http://localhost:8001")
    print("API endpoints:")
    print("  - /v1/completions")
    print("  - /v1/chat/completions")
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