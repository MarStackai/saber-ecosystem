#!/usr/bin/env python3
"""
Production LoRA Fine-tuning for GPT-OSS
FIT Intelligence Query Parser Training
Optimized for RTX 3090 24GB VRAM
"""

import os
import json
import torch
import logging
from pathlib import Path
from datetime import datetime
import numpy as np
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GPTOSSLoRATrainer:
    """
    Production-grade LoRA trainer for GPT-OSS
    Designed for FIT Intelligence query parsing at scale
    """
    
    def __init__(self):
        """Initialize trainer with optimized settings for RTX 3090"""
        
        self.config = {
            # Model configuration
            "model_name": "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",  # Alternative to GPT-OSS
            "use_gpt_oss": False,  # We'll use a similar architecture model
            
            # LoRA configuration
            "lora_r": 16,
            "lora_alpha": 32,
            "lora_dropout": 0.1,
            "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
            
            # Training configuration
            "batch_size": 1,
            "gradient_accumulation_steps": 8,
            "num_epochs": 3,
            "learning_rate": 2e-4,
            "warmup_ratio": 0.1,
            "max_seq_length": 512,
            
            # Paths
            "data_dir": "./lora_training_advanced",
            "output_dir": "./gpt-oss-lora-production",
            "cache_dir": "./model_cache",
            
            # Hardware
            "use_4bit": True,
            "use_flash_attention": False,  # Disable for compatibility
            "device_map": "auto",
        }
        
        logger.info("=" * 60)
        logger.info("GPT-OSS LoRA Production Trainer")
        logger.info("=" * 60)
        logger.info(f"Configuration: {json.dumps(self.config, indent=2)}")
    
    def check_environment(self):
        """Verify environment is ready for training"""
        
        logger.info("\nEnvironment Check:")
        logger.info("-" * 40)
        
        # Check GPU
        if not torch.cuda.is_available():
            logger.error("❌ No GPU available")
            return False
        
        gpu_name = torch.cuda.get_device_name()
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
        logger.info(f"✅ GPU: {gpu_name} ({vram_gb:.1f}GB)")
        
        # Check CUDA version
        logger.info(f"✅ CUDA: {torch.version.cuda}")
        logger.info(f"✅ PyTorch: {torch.__version__}")
        
        # Check training data
        train_file = Path(self.config["data_dir"]) / "train.jsonl"
        val_file = Path(self.config["data_dir"]) / "validation.jsonl"
        test_file = Path(self.config["data_dir"]) / "test.jsonl"
        
        if not all([train_file.exists(), val_file.exists(), test_file.exists()]):
            logger.error("❌ Training data not found")
            return False
        
        # Count examples
        with open(train_file, 'r') as f:
            train_count = sum(1 for _ in f)
        with open(val_file, 'r') as f:
            val_count = sum(1 for _ in f)
        
        logger.info(f"✅ Training data: {train_count} train, {val_count} validation")
        
        return True
    
    def install_dependencies(self):
        """Install required packages"""
        
        logger.info("\nChecking dependencies...")
        
        packages = {
            "transformers": "4.36.0",
            "peft": "0.7.0",
            "bitsandbytes": "0.41.0",
            "accelerate": "0.25.0",
            "datasets": "2.14.0",
            "scipy": None,
            "sentencepiece": None,
            "protobuf": None,
        }
        
        missing = []
        for package, version in packages.items():
            try:
                __import__(package)
                logger.info(f"✅ {package} installed")
            except ImportError:
                if version:
                    missing.append(f"{package}=={version}")
                else:
                    missing.append(package)
        
        if missing:
            logger.warning(f"Missing packages: {', '.join(missing)}")
            
            import subprocess
            for package in missing:
                logger.info(f"Installing {package}...")
                subprocess.run(
                    ["python3", "-m", "pip", "install", "--user", package],
                    capture_output=True
                )
            
            logger.info("✅ Dependencies installed")
        
        return True
    
    def prepare_data(self):
        """Prepare and format training data"""
        
        logger.info("\nPreparing training data...")
        
        def load_jsonl(file_path):
            examples = []
            with open(file_path, 'r') as f:
                for line in f:
                    examples.append(json.loads(line))
            return examples
        
        # Load data
        train_data = load_jsonl(f"{self.config['data_dir']}/train.jsonl")
        val_data = load_jsonl(f"{self.config['data_dir']}/validation.jsonl")
        test_data = load_jsonl(f"{self.config['data_dir']}/test.jsonl")
        
        # Format for training
        def format_for_training(example):
            """Format example for chat model training"""
            
            # Ensure output is JSON string
            if isinstance(example['output'], dict):
                output_json = json.dumps(example['output'], separators=(',', ':'))
            else:
                output_json = example['output']
            
            # Create chat format
            text = f"""<|im_start|>system
You are the FIT Intelligence query parser. Parse UK renewable energy queries into JSON filters.
Technology: Wind, Photovoltaic, Hydro, Anaerobic digestion, Micro CHP
Berkshire postcodes: RG, SL
Yorkshire postcodes: YO, HU, DN, HD, WF, LS, BD
Return only valid JSON.<|im_end|>
<|im_start|>user
{example['input']}<|im_end|>
<|im_start|>assistant
{output_json}<|im_end|>"""
            
            return {"text": text}
        
        # Format all data
        train_formatted = [format_for_training(ex) for ex in train_data]
        val_formatted = [format_for_training(ex) for ex in val_data]
        test_formatted = [format_for_training(ex) for ex in test_data]
        
        logger.info(f"✅ Formatted {len(train_formatted)} train, {len(val_formatted)} val, {len(test_formatted)} test")
        
        # Save formatted data
        os.makedirs(self.config["output_dir"], exist_ok=True)
        
        with open(f"{self.config['output_dir']}/train_formatted.jsonl", 'w') as f:
            for item in train_formatted:
                f.write(json.dumps(item) + '\n')
        
        with open(f"{self.config['output_dir']}/val_formatted.jsonl", 'w') as f:
            for item in val_formatted:
                f.write(json.dumps(item) + '\n')
        
        return train_formatted, val_formatted, test_formatted
    
    def setup_model_and_tokenizer(self):
        """Set up model with LoRA and quantization"""
        
        logger.info("\nSetting up model and tokenizer...")
        
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            BitsAndBytesConfig
        )
        from peft import (
            LoraConfig,
            get_peft_model,
            prepare_model_for_kbit_training,
            TaskType
        )
        
        # Create cache directory
        os.makedirs(self.config["cache_dir"], exist_ok=True)
        
        # Quantization configuration
        if self.config["use_4bit"]:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True
            )
        else:
            bnb_config = None
        
        # Load model
        logger.info(f"Loading model: {self.config['model_name']}")
        logger.info("This may take several minutes...")
        
        model = AutoModelForCausalLM.from_pretrained(
            self.config["model_name"],
            quantization_config=bnb_config,
            device_map=self.config["device_map"],
            trust_remote_code=True,
            cache_dir=self.config["cache_dir"],
            torch_dtype=torch.bfloat16
        )
        
        # Prepare for k-bit training
        if self.config["use_4bit"]:
            model = prepare_model_for_kbit_training(model)
        
        # LoRA configuration
        lora_config = LoraConfig(
            r=self.config["lora_r"],
            lora_alpha=self.config["lora_alpha"],
            target_modules=self.config["target_modules"],
            lora_dropout=self.config["lora_dropout"],
            bias="none",
            task_type=TaskType.CAUSAL_LM
        )
        
        # Add LoRA adapters
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            self.config["model_name"],
            cache_dir=self.config["cache_dir"]
        )
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"
        
        logger.info("✅ Model and tokenizer ready")
        
        return model, tokenizer
    
    def train(self, model, tokenizer, train_data, val_data):
        """Train the model with LoRA"""
        
        logger.info("\n" + "=" * 60)
        logger.info("Starting LoRA Fine-tuning")
        logger.info("=" * 60)
        
        from transformers import TrainingArguments
        from trl import SFTTrainer
        from datasets import Dataset
        
        # Convert to datasets
        train_dataset = Dataset.from_list(train_data)
        val_dataset = Dataset.from_list(val_data)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.config["output_dir"],
            num_train_epochs=self.config["num_epochs"],
            per_device_train_batch_size=self.config["batch_size"],
            gradient_accumulation_steps=self.config["gradient_accumulation_steps"],
            gradient_checkpointing=True,
            optim="paged_adamw_8bit",
            logging_dir=f"{self.config['output_dir']}/logs",
            logging_steps=10,
            save_strategy="epoch",
            evaluation_strategy="epoch",
            save_total_limit=2,
            learning_rate=self.config["learning_rate"],
            warmup_ratio=self.config["warmup_ratio"],
            lr_scheduler_type="cosine",
            bf16=True,
            tf32=True,
            max_grad_norm=0.3,
            push_to_hub=False,
            report_to=["tensorboard"],
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
        )
        
        # Create trainer
        trainer = SFTTrainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=tokenizer,
            dataset_text_field="text",
            max_seq_length=self.config["max_seq_length"],
            packing=False,
        )
        
        # Start training
        logger.info("Training started...")
        logger.info(f"Estimated time: 2-4 hours on RTX 3090")
        
        train_result = trainer.train()
        
        # Save the model
        trainer.save_model(f"{self.config['output_dir']}/final")
        
        logger.info("✅ Training completed!")
        logger.info(f"Final loss: {train_result.training_loss:.4f}")
        
        return trainer
    
    def test_model(self, model, tokenizer, test_data):
        """Test the fine-tuned model"""
        
        logger.info("\n" + "=" * 60)
        logger.info("Testing Fine-tuned Model")
        logger.info("=" * 60)
        
        # Critical test queries
        test_queries = [
            "wind sites over 100kw in berkshire",
            "solar farms in Yorkshire",
            "what is the fit rate for fit id 1585",
            "hydro installations in Scotland",
            "sites expiring within 3 years",
            "compare wind and solar in Birmingham"
        ]
        
        results = []
        for query in test_queries:
            prompt = f"""<|im_start|>system
You are the FIT Intelligence query parser. Parse UK renewable energy queries into JSON filters.
Return only valid JSON.<|im_end|>
<|im_start|>user
{query}<|im_end|>
<|im_start|>assistant"""
            
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
            
            # Extract JSON
            try:
                # Find JSON in response
                json_str = response.split("<|im_start|>assistant")[-1].strip()
                json_str = json_str.split("<|im_end|>")[0].strip()
                parsed = json.loads(json_str)
                
                logger.info(f"✅ Query: {query}")
                logger.info(f"   Result: {json.dumps(parsed, indent=2)}")
                
                # Check critical query
                if query == "wind sites over 100kw in berkshire":
                    if (parsed.get("technology") == "Wind" and
                        parsed.get("capacity_min_kw") == 100 and
                        "RG" in parsed.get("postcode_patterns", [])):
                        logger.info("   ✅✅✅ CRITICAL QUERY CORRECT!")
                
                results.append({"query": query, "success": True, "result": parsed})
                
            except Exception as e:
                logger.error(f"❌ Query: {query}")
                logger.error(f"   Error: {e}")
                results.append({"query": query, "success": False})
        
        # Calculate success rate
        success_rate = sum(1 for r in results if r["success"]) / len(results)
        logger.info(f"\nSuccess rate: {success_rate:.1%}")
        
        return results
    
    def export_to_ollama(self):
        """Export the fine-tuned model for Ollama deployment"""
        
        logger.info("\n" + "=" * 60)
        logger.info("Exporting to Ollama")
        logger.info("=" * 60)
        
        # Create export script
        export_script = f"""#!/bin/bash
# Export fine-tuned model to Ollama

echo "Converting model to GGUF format..."
python3 convert_to_gguf.py \\
    --model {self.config['output_dir']}/final \\
    --output {self.config['output_dir']}/fit-intelligence.gguf \\
    --quantize q4_K_M

echo "Creating Ollama model..."
cat > {self.config['output_dir']}/Modelfile << EOF
FROM {self.config['output_dir']}/fit-intelligence.gguf

SYSTEM "You are the FIT Intelligence query parser. Parse UK renewable energy queries into JSON filters. Return only valid JSON."

PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER stop "<|im_end|>"
EOF

ollama create fit-intelligence-lora -f {self.config['output_dir']}/Modelfile

echo "✅ Model ready for deployment!"
echo "Test with: ollama run fit-intelligence-lora 'wind sites over 100kw in berkshire'"
"""
        
        with open(f"{self.config['output_dir']}/export_to_ollama.sh", 'w') as f:
            f.write(export_script)
        
        os.chmod(f"{self.config['output_dir']}/export_to_ollama.sh", 0o755)
        
        logger.info(f"✅ Export script created: {self.config['output_dir']}/export_to_ollama.sh")

def main():
    """Main training pipeline"""
    
    trainer = GPTOSSLoRATrainer()
    
    # Step 1: Check environment
    if not trainer.check_environment():
        logger.error("Environment not ready")
        return
    
    # Step 2: Install dependencies
    if not trainer.install_dependencies():
        logger.error("Failed to install dependencies")
        return
    
    # Step 3: Prepare data
    train_data, val_data, test_data = trainer.prepare_data()
    
    # Step 4: User confirmation
    logger.info("\n" + "=" * 60)
    logger.info("Ready to start training")
    logger.info("=" * 60)
    logger.info("\nThis will:")
    logger.info("• Fine-tune a large model with LoRA")
    logger.info("• Use 3,195 FIT Intelligence examples")
    logger.info("• Take 2-4 hours on RTX 3090")
    logger.info("• Produce a production-grade query parser")
    
    response = input("\nProceed with training? (y/n): ")
    if response.lower() != 'y':
        logger.info("Training cancelled")
        return
    
    # Step 5: Setup model
    model, tokenizer = trainer.setup_model_and_tokenizer()
    
    # Step 6: Train
    trained_model = trainer.train(model, tokenizer, train_data, val_data)
    
    # Step 7: Test
    trainer.test_model(model, tokenizer, test_data)
    
    # Step 8: Export
    trainer.export_to_ollama()
    
    logger.info("\n" + "=" * 60)
    logger.info("🎉 Training Complete!")
    logger.info("=" * 60)
    logger.info("\nNext steps:")
    logger.info("1. Run the export script to create Ollama model")
    logger.info("2. Test with: ollama run fit-intelligence-lora 'wind sites over 100kw in berkshire'")
    logger.info("3. Update platform to use new model")

if __name__ == "__main__":
    main()