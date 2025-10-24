#!/usr/bin/env python3
"""
Optimized LoRA Training Script for FIT Intelligence
Configured for RTX 3090 24GB VRAM
"""

import os
import json
import torch
import logging
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check training environment"""
    logger.info("=" * 60)
    logger.info("FIT Intelligence LoRA Training Environment Check")
    logger.info("=" * 60)
    
    # GPU Check
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name()
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
        logger.info(f"✅ GPU: {device_name}")
        logger.info(f"✅ VRAM: {vram_gb:.1f} GB")
        
        if vram_gb >= 20:
            logger.info("✅ Sufficient VRAM for full training")
            return "full"
        elif vram_gb >= 10:
            logger.info("⚠️  Limited VRAM - will use 4-bit quantization")
            return "quantized"
        else:
            logger.error("❌ Insufficient VRAM for training")
            return None
    else:
        logger.error("❌ No GPU available")
        return None

def install_dependencies():
    """Install required packages"""
    logger.info("\nInstalling dependencies...")
    
    packages = [
        "transformers==4.36.0",
        "peft==0.7.0",
        "bitsandbytes==0.41.0",
        "accelerate==0.25.0",
        "trl==0.7.0",
        "datasets==2.14.0",
        "sentencepiece",
        "protobuf"
    ]
    
    import subprocess
    for package in packages:
        logger.info(f"Installing {package}...")
        subprocess.run(
            ["pip", "install", "-q", package],
            capture_output=True
        )
    
    logger.info("✅ Dependencies installed")

def prepare_training_data():
    """Prepare the training dataset"""
    logger.info("\nPreparing training data...")
    
    data_dir = Path("./lora_training_advanced")
    
    # Check if data exists
    train_file = data_dir / "train.jsonl"
    val_file = data_dir / "validation.jsonl"
    test_file = data_dir / "test.jsonl"
    
    if not all([train_file.exists(), val_file.exists(), test_file.exists()]):
        logger.error("❌ Training data not found. Run advanced_lora_training_generator.py first")
        return None
    
    # Load and count examples
    def count_lines(file_path):
        with open(file_path, 'r') as f:
            return sum(1 for _ in f)
    
    train_count = count_lines(train_file)
    val_count = count_lines(val_file)
    test_count = count_lines(test_file)
    
    logger.info(f"✅ Training examples: {train_count}")
    logger.info(f"✅ Validation examples: {val_count}")
    logger.info(f"✅ Test examples: {test_count}")
    
    return data_dir

def train_lora_model(mode="full"):
    """Train the LoRA model"""
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        TrainingArguments
    )
    from peft import (
        LoraConfig,
        get_peft_model,
        prepare_model_for_kbit_training,
        TaskType
    )
    from trl import SFTTrainer
    from datasets import Dataset
    
    logger.info("\n" + "=" * 60)
    logger.info("Starting LoRA Training")
    logger.info("=" * 60)
    
    # Model selection based on available VRAM
    if mode == "full":
        model_name = "meta-llama/Llama-3.2-3B"  # Smaller model for testing
        batch_size = 4
        gradient_accumulation = 4
    else:
        model_name = "meta-llama/Llama-3.2-1B"  # Even smaller for limited VRAM
        batch_size = 2
        gradient_accumulation = 8
    
    logger.info(f"Model: {model_name}")
    logger.info(f"Mode: {mode}")
    
    # Load model with quantization
    logger.info("\nLoading model...")
    
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    
    model = prepare_model_for_kbit_training(model)
    
    # LoRA configuration
    lora_config = LoraConfig(
        r=16,  # Lower rank for faster training
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],  # Fewer modules for testing
        lora_dropout=0.1,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    # Load training data
    logger.info("\nLoading datasets...")
    
    def load_jsonl(file_path):
        examples = []
        with open(file_path, 'r') as f:
            for line in f:
                examples.append(json.loads(line))
        return examples
    
    def format_example(example):
        """Format for Llama chat template"""
        text = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a query parser for the FIT Intelligence database.
Parse natural language queries into structured JSON filters.

Technology: Wind, Photovoltaic, Hydro, Anaerobic digestion, Micro CHP
Locations map to postcodes (Yorkshire: YO,HU,DN,HD,WF,LS,BD)
Return only valid JSON.<|eot_id|>

<|start_header_id|>user<|end_header_id|>

{example['input']}<|eot_id|>

<|start_header_id|>assistant<|end_header_id|>

{example['output']}<|eot_id|>"""
        return {"text": text}
    
    train_data = load_jsonl("./lora_training_advanced/train.jsonl")
    val_data = load_jsonl("./lora_training_advanced/validation.jsonl")
    
    # Use smaller subset for testing
    train_data = train_data[:100]  # Start with 100 examples
    val_data = val_data[:20]
    
    train_dataset = Dataset.from_list(train_data).map(format_example)
    val_dataset = Dataset.from_list(val_data).map(format_example)
    
    # Training arguments
    output_dir = "./fit-intelligence-lora-test"
    
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=1,  # Just 1 epoch for testing
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation,
        gradient_checkpointing=True,
        optim="paged_adamw_8bit",
        logging_steps=10,
        save_strategy="epoch",
        evaluation_strategy="steps",
        eval_steps=50,
        learning_rate=2e-4,
        warmup_ratio=0.1,
        bf16=True,
        tf32=True,
        max_grad_norm=0.3,
        push_to_hub=False,
        report_to="none",  # Disable wandb for testing
    )
    
    # Create trainer
    logger.info("\nInitializing trainer...")
    
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        dataset_text_field="text",
        max_seq_length=512,  # Shorter sequences for testing
        packing=False
    )
    
    # Train
    logger.info("\n" + "=" * 60)
    logger.info("Starting training...")
    logger.info("=" * 60)
    
    trainer.train()
    
    # Save model
    logger.info("\nSaving model...")
    trainer.save_model(f"{output_dir}/final")
    
    # Test the model
    test_model(model, tokenizer)
    
    logger.info("\n✅ Training completed!")
    logger.info(f"Model saved to: {output_dir}")

def test_model(model, tokenizer):
    """Test the trained model"""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Model")
    logger.info("=" * 60)
    
    test_queries = [
        "wind sites over 100kw in berkshire",
        "solar farms in Yorkshire",
        "what is the fit rate for fit id 1585"
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        
        # Format input
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a query parser for the FIT Intelligence database.
Parse natural language queries into structured JSON filters.<|eot_id|>

<|start_header_id|>user<|end_header_id|>

{query}<|eot_id|>

<|start_header_id|>assistant<|end_header_id|>"""
        
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.1,
                do_sample=True,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract JSON from response
        try:
            import re
            json_match = re.search(r'\{.*\}', response.split("assistant")[-1], re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                logger.info(f"✅ Parsed: {json.dumps(parsed, indent=2)}")
            else:
                logger.info("❌ No JSON found in response")
        except Exception as e:
            logger.info(f"❌ Parse error: {e}")

def main():
    """Main training pipeline"""
    
    logger.info("\n" + "🚀 FIT Intelligence LoRA Training Pipeline" + "\n")
    
    # Step 1: Check environment
    mode = check_environment()
    if not mode:
        logger.error("Cannot proceed without GPU")
        return
    
    # Step 2: Check data
    data_dir = prepare_training_data()
    if not data_dir:
        return
    
    # Step 3: Install dependencies
    response = input("\nInstall/update dependencies? (y/n): ")
    if response.lower() == 'y':
        install_dependencies()
    
    # Step 4: Start training
    logger.info("\n" + "=" * 60)
    logger.info("Ready to start training")
    logger.info("=" * 60)
    logger.info("\nThis test run will:")
    logger.info("  • Train on 100 examples")
    logger.info("  • Complete in ~5-10 minutes")
    logger.info("  • Validate the pipeline")
    
    response = input("\nStart training? (y/n): ")
    if response.lower() == 'y':
        train_lora_model(mode)
    else:
        logger.info("Training cancelled")

if __name__ == "__main__":
    main()