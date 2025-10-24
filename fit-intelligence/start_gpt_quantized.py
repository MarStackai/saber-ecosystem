#!/usr/bin/env python3
"""
Start vLLM with a quantized GPT model that fits in 24GB
Uses GPTQ 4-bit quantization
"""

import subprocess
import sys
import os

def start_vllm_server():
    """Start vLLM with quantized model"""
    
    # Quantized models that fit in 24GB
    models = {
        "gptq-4bit": "TheBloke/gpt-neox-20b-GPTQ",  # 4-bit quantized 20B
        "gguf": "TheBloke/GPT-NeoX-20B-GGUF",  # GGUF format
        "awq": "casperhansen/opt-30b-awq",  # 30B with AWQ (aggressive quant)
    }
    
    # Try GPTQ version
    model = models["gptq-4bit"]
    
    print("=" * 60)
    print("Starting vLLM with Quantized GPT Model")
    print("=" * 60)
    print(f"Model: {model}")
    print("Quantization: GPTQ 4-bit")
    print("GPU: RTX 3090 (24GB)")
    print("-" * 60)
    
    # Set environment variables
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = '0'
    env['LD_LIBRARY_PATH'] = '/usr/local/cuda-12/lib64:' + env.get('LD_LIBRARY_PATH', '')
    
    # Kill existing
    subprocess.run(["pkill", "-f", "vllm"], stderr=subprocess.DEVNULL)
    
    # Start with quantization
    cmd = [
        sys.executable,
        "-m", "vllm.entrypoints.openai.api_server",
        "--model", model,
        "--host", "0.0.0.0",
        "--port", "8000",
        "--quantization", "gptq",  # Enable GPTQ quantization
        "--dtype", "float16",
        "--gpu-memory-utilization", "0.9",
        "--max-model-len", "2048",
        "--trust-remote-code"
    ]
    
    print("Command:", " ".join(cmd))
    print("-" * 60)
    print("Starting server...")
    
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nStopped")
    except Exception as e:
        print(f"Error: {e}")
        print("\nTrying fallback model...")
        # Fallback to smaller model
        fallback_model = "mistralai/Mistral-7B-Instruct-v0.2"
        cmd[4] = fallback_model  # Update model in command
        cmd.remove("--quantization")  # Remove quantization
        cmd.remove("gptq")
        print(f"Starting with fallback: {fallback_model}")
        subprocess.run(cmd, env=env)

if __name__ == "__main__":
    start_vllm_server()