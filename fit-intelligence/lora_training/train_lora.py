#!/usr/bin/env python3
"""
LoRA training script for FIT Intelligence query understanding
Using safer hyperparameters per Rob's recommendations
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def create_training_prompt(example: dict) -> str:
    """Format training example for Ollama"""
    messages = example.get("messages", [])
    
    prompt = ""
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        
        if role == "system":
            prompt += f"System: {content}\n\n"
        elif role == "user":
            prompt += f"User: {content}\n\n"
        elif role == "assistant":
            prompt += f"Assistant: {content}\n\n"
    
    return prompt.strip()

def prepare_ollama_dataset(train_file: str, output_file: str):
    """Convert JSONL to Ollama training format"""
    print(f"Preparing dataset from {train_file}...")
    
    with open(train_file, 'r') as f:
        lines = f.readlines()
    
    prompts = []
    for line in lines:
        example = json.loads(line)
        prompt = create_training_prompt(example)
        prompts.append(prompt)
    
    # Save as text file for Ollama
    with open(output_file, 'w') as f:
        f.write("\n---\n".join(prompts))
    
    print(f"Prepared {len(prompts)} training examples")
    return len(prompts)

def create_modelfile(base_model: str = "llama2:13b", lora_path: str = None):
    """Create Ollama Modelfile for LoRA adapter"""
    
    modelfile_content = f"""# FIT Intelligence LoRA Model
FROM {base_model}

# System prompt for FIT query understanding
SYSTEM You are a UK renewable energy FIT installation search assistant. Parse queries to extract:
- technology: normalized to photovoltaic/wind/hydro/anaerobic digestion  
- postcode_areas: exact UK postcode area codes (e.g., M for Manchester, not ML)
- min_capacity_kw: minimum capacity in kilowatts
- max_capacity_kw: maximum capacity in kilowatts
- repowering_category: immediate/urgent/optimal based on time windows

Critical rules:
- Manchester MUST map to ["M"] only, never ML
- Yorkshire MUST map to ["YO","HU","LS","BD","HX","HD","WF","S","DN"]
- Solar/PV/solar panels MUST normalize to "photovoltaic"
- Capacity ranges must be exact (50-350kW means min=50, max=350)

Always return search parameters in JSON format.

# Temperature for consistency
PARAMETER temperature 0.1

# Context window
PARAMETER num_ctx 4096

# LoRA adapter path (if training completed)
{"ADAPTER " + lora_path if lora_path else "# ADAPTER path will be added after training"}
"""
    
    modelfile_path = "lora_training/Modelfile"
    with open(modelfile_path, 'w') as f:
        f.write(modelfile_content)
    
    print(f"Created Modelfile at {modelfile_path}")
    return modelfile_path

def train_with_ollama(config_path: str):
    """
    Train LoRA adapter using Ollama
    Note: This is a simplified version - actual Ollama LoRA training 
    would require their training API when available
    """
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print("LoRA Training Configuration:")
    print(f"  Base model: {config['model_name']}")
    print(f"  LoRA rank: {config['lora_config']['r']}")
    print(f"  Learning rate: {config['training_args']['learning_rate']}")
    print(f"  Epochs: {config['training_args']['num_train_epochs']}")
    print(f"  Batch size: {config['training_args']['per_device_train_batch_size']}")
    
    # Prepare datasets
    train_file = f"lora_training/{config['data_config']['train_file']}"
    val_file = f"lora_training/{config['data_config']['val_file']}"
    
    if not os.path.exists(train_file):
        print(f"ERROR: Training file not found: {train_file}")
        return False
    
    # Convert to Ollama format
    ollama_train = "lora_training/ollama_train.txt"
    num_examples = prepare_ollama_dataset(train_file, ollama_train)
    
    # Create initial Modelfile
    modelfile = create_modelfile(config['model_name'])
    
    print("\n" + "="*60)
    print("IMPORTANT: Ollama LoRA training steps")
    print("="*60)
    
    print("""
Since Ollama doesn't have a built-in LoRA training API yet, we'll use 
alternative approaches:

OPTION 1: Use llama.cpp with LoRA (Recommended)
------------------------------------------------
1. Export model to GGUF format
2. Use llama.cpp finetune command with our data
3. Import trained LoRA back to Ollama

Commands:
# Clone llama.cpp if not present
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && make

# Convert training data to llama.cpp format
python convert-finetune-data.py ../lora_training/train_20250827_001256.jsonl

# Fine-tune with LoRA
./finetune \\
    --model-base models/llama-2-13b.gguf \\
    --lora-out lora-adapter.bin \\
    --data finetune-data.bin \\
    --rank 16 \\
    --learning-rate 2e-5 \\
    --epochs 2 \\
    --batch 4

OPTION 2: Use HuggingFace PEFT library
---------------------------------------
1. Load Llama2 13B from HuggingFace
2. Apply LoRA with PEFT
3. Train with our dataset
4. Export to GGUF for Ollama

OPTION 3: Prompt-based fine-tuning (Immediate)
-----------------------------------------------
Create a specialized prompt template that includes
examples from our training data for few-shot learning.
This won't be as effective but can work immediately.
""")
    
    # Create a few-shot prompt template as immediate solution
    print("\nCreating few-shot prompt template for immediate use...")
    
    few_shot_template = """
Examples of correct query parsing:

Query: "sites in Manchester"
Parameters: {"postcode_areas": ["M"], "technology": null}

Query: "wind sites over 50kw to max 350kw in Yorkshire"  
Parameters: {"technology": "wind", "min_capacity_kw": 50, "max_capacity_kw": 350, "postcode_areas": ["YO","HU","LS","BD","HX","HD","WF","S","DN"]}

Query: "solar panels over 250kw"
Parameters: {"technology": "photovoltaic", "min_capacity_kw": 250}

Query: "urgent repowering opportunities"
Parameters: {"repowering_category": "urgent"}

Now parse this query:
"""
    
    with open("lora_training/few_shot_template.txt", 'w') as f:
        f.write(few_shot_template)
    
    print("Created few-shot template at lora_training/few_shot_template.txt")
    
    return True

def main():
    """Main training pipeline"""
    
    print("Starting LoRA training pipeline")
    print("=" * 60)
    
    # Load config
    config_path = "lora_training/lora_config.json"
    if not os.path.exists(config_path):
        print(f"ERROR: Config not found at {config_path}")
        return 1
    
    # Check for training data
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    train_file = f"lora_training/{config['data_config']['train_file']}"
    if not os.path.exists(train_file):
        print(f"ERROR: Training data not found at {train_file}")
        print("Run generate_lora_training.py first")
        return 1
    
    # Start training
    success = train_with_ollama(config_path)
    
    if success:
        print("\n" + "="*60)
        print("Training preparation complete!")
        print("Follow one of the options above to complete LoRA training")
        print("\nOnce trained, validate with:")
        print("  python lora_training/validate_lora.py [model_name]")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())