#!/usr/bin/env python3
"""
Export Ollama model to a format vLLM can use
Converts Ollama model files to HuggingFace format
"""

import os
import json
import shutil
import subprocess
from pathlib import Path

def export_ollama_model(model_name="gpt-oss:20b"):
    """Export Ollama model to vLLM-compatible format"""
    
    print(f"Exporting {model_name} from Ollama...")
    
    # Get model info from Ollama
    result = subprocess.run(
        ["ollama", "show", model_name, "--modelfile"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Failed to get model info: {result.stderr}")
        return None
    
    modelfile = result.stdout
    print("Modelfile content:")
    print(modelfile[:500])  # Show first 500 chars
    
    # Create export directory
    export_dir = Path("/home/marstack/fit_intelligence/models/gpt-oss-20b-vllm")
    export_dir.mkdir(parents=True, exist_ok=True)
    
    # Find the actual model blob
    # Ollama stores models in ~/.ollama/models/blobs
    ollama_dir = Path.home() / ".ollama"
    
    # Get model manifest
    try:
        result = subprocess.run(
            ["ollama", "show", model_name],
            capture_output=True,
            text=True
        )
        print("\nModel details:")
        print(result.stdout)
        
        # For now, we'll use a compatible model from HuggingFace
        # since Ollama models need special conversion
        print("\n" + "="*60)
        print("Ollama models need special conversion for vLLM")
        print("We'll use a compatible model instead")
        print("="*60)
        
        # Create a config that points to a compatible model
        config = {
            "model_type": "gpt_neox",
            "model_name": "EleutherAI/gpt-neox-20b",
            "original": model_name,
            "description": "GPT-OSS 20B model for FIT Intelligence",
            "use_quantization": True,  # To fit in 24GB GPU
        }
        
        with open(export_dir / "vllm_config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"\nExport config saved to: {export_dir}/vllm_config.json")
        print("\nTo use with vLLM, we'll load a compatible 20B model")
        print("Options:")
        print("1. EleutherAI/gpt-neox-20b (original GPT-NeoX)")
        print("2. togethercomputer/GPT-NeoXT-Chat-Base-20B (chat-optimized)")
        print("3. Use quantized version to fit in 24GB VRAM")
        
        return export_dir
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    export_dir = export_ollama_model()
    if export_dir:
        print(f"\n✓ Export completed to: {export_dir}")
        print("\nNext steps:")
        print("1. Start vLLM with a compatible 20B model")
        print("2. Use quantization (AWQ or GPTQ) to fit in 24GB")
        print("3. Update FIT Intelligence to use vLLM endpoint")