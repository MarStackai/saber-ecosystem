#!/usr/bin/env python3
"""
GPT-OSS LoRA Training for FIT Intelligence
Production-ready fine-tuning pipeline for scalable platform
Optimized for RTX 3090 24GB VRAM
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GPTOSSLoRATrainer:
    """
    LoRA trainer for GPT-OSS 20B model
    Designed for FIT Intelligence query parsing
    """
    
    def __init__(self):
        self.model_name = "gpt-oss"  # We'll need the actual HF model path
        self.output_dir = "./gpt-oss-fit-lora"
        self.data_dir = "./lora_training_advanced"
        
        # LoRA configuration for 24GB VRAM
        self.lora_config = {
            "r": 8,  # Lower rank for 20B model
            "alpha": 16,
            "dropout": 0.1,
            "target_modules": ["q_proj", "v_proj"],  # Minimal modules for memory
        }
        
        # Training configuration
        self.training_config = {
            "num_epochs": 2,  # Fewer epochs for large model
            "batch_size": 1,  # Small batch for 20B model
            "gradient_accumulation": 16,  # Effective batch size of 16
            "learning_rate": 5e-5,
            "warmup_steps": 100,
            "max_seq_length": 512,  # Shorter sequences for efficiency
        }
        
        logger.info("GPT-OSS LoRA Trainer initialized")
        logger.info(f"Config: LoRA r={self.lora_config['r']}, batch={self.training_config['batch_size']}")
    
    def check_environment(self):
        """Check if environment is ready for training"""
        import subprocess
        
        logger.info("=" * 60)
        logger.info("Environment Check")
        logger.info("=" * 60)
        
        # Check GPU
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name()
                vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
                logger.info(f"✅ GPU: {gpu_name} ({vram_gb:.1f}GB)")
                
                if vram_gb < 20:
                    logger.warning("⚠️ Less than 20GB VRAM - training may be challenging")
                    return False
            else:
                logger.error("❌ No GPU available")
                return False
        except ImportError:
            logger.error("❌ PyTorch not installed")
            return False
        
        # Check data
        train_file = Path(self.data_dir) / "train.jsonl"
        if not train_file.exists():
            logger.error("❌ Training data not found")
            return False
        
        with open(train_file, 'r') as f:
            count = sum(1 for _ in f)
        logger.info(f"✅ Training data: {count} examples")
        
        # Check for required packages
        required = ["transformers", "peft", "bitsandbytes", "accelerate"]
        missing = []
        for pkg in required:
            try:
                __import__(pkg)
            except ImportError:
                missing.append(pkg)
        
        if missing:
            logger.warning(f"⚠️ Missing packages: {missing}")
            logger.info("Install with:")
            logger.info(f"  pip install {' '.join(missing)}")
            return False
        
        logger.info("✅ All dependencies available")
        return True
    
    def prepare_data(self):
        """Prepare training data in GPT-OSS format"""
        logger.info("\nPreparing training data...")
        
        def load_jsonl(file_path):
            examples = []
            with open(file_path, 'r') as f:
                for line in f:
                    examples.append(json.loads(line))
            return examples
        
        # Load data
        train_data = load_jsonl(f"{self.data_dir}/train.jsonl")
        val_data = load_jsonl(f"{self.data_dir}/validation.jsonl")
        
        # Format for GPT-OSS (assuming it uses a specific template)
        def format_example(ex):
            """Format example for GPT-OSS training"""
            # GPT-OSS prompt format
            prompt = f"""Parse this UK renewable energy query into JSON filters:

Query: {ex['input']}

JSON Output:"""
            
            # Ensure output is JSON string
            if isinstance(ex['output'], dict):
                output = json.dumps(ex['output'], separators=(',', ':'))
            else:
                output = ex['output']
            
            return {
                "text": f"{prompt}\n{output}",
                "input": prompt,
                "output": output
            }
        
        # Format datasets
        train_formatted = [format_example(ex) for ex in train_data]
        val_formatted = [format_example(ex) for ex in val_data]
        
        logger.info(f"✅ Formatted {len(train_formatted)} train, {len(val_formatted)} val examples")
        
        return train_formatted, val_formatted
    
    def setup_model(self):
        """Set up GPT-OSS with LoRA and quantization"""
        logger.info("\nSetting up GPT-OSS model with LoRA...")
        
        try:
            import torch
            from transformers import (
                AutoModelForCausalLM,
                AutoTokenizer,
                BitsAndBytesConfig,
                TrainingArguments,
                Trainer
            )
            from peft import (
                LoraConfig,
                get_peft_model,
                prepare_model_for_kbit_training,
                TaskType
            )
            
            # 4-bit quantization config
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True
            )
            
            # Note: We need the actual HuggingFace model path for GPT-OSS
            # This is a placeholder - replace with actual model
            model_path = "OpenAssistant/gpt-oss-20b"  # Example path
            
            logger.info(f"Loading model: {model_path}")
            logger.info("This will take several minutes...")
            
            # Load model with quantization
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True
            )
            
            # Prepare for k-bit training
            model = prepare_model_for_kbit_training(model)
            
            # LoRA configuration
            lora_config = LoraConfig(
                r=self.lora_config["r"],
                lora_alpha=self.lora_config["alpha"],
                target_modules=self.lora_config["target_modules"],
                lora_dropout=self.lora_config["dropout"],
                bias="none",
                task_type=TaskType.CAUSAL_LM
            )
            
            # Add LoRA adapters
            model = get_peft_model(model, lora_config)
            model.print_trainable_parameters()
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            tokenizer.pad_token = tokenizer.eos_token
            tokenizer.padding_side = "right"
            
            logger.info("✅ Model setup complete")
            return model, tokenizer
            
        except Exception as e:
            logger.error(f"❌ Model setup failed: {e}")
            return None, None
    
    def train(self, model, tokenizer, train_data, val_data):
        """Train the model"""
        logger.info("\n" + "=" * 60)
        logger.info("Starting LoRA Training")
        logger.info("=" * 60)
        
        from transformers import TrainingArguments, Trainer
        from datasets import Dataset
        
        # Convert to datasets
        train_dataset = Dataset.from_list(train_data)
        val_dataset = Dataset.from_list(val_data)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=self.training_config["num_epochs"],
            per_device_train_batch_size=self.training_config["batch_size"],
            gradient_accumulation_steps=self.training_config["gradient_accumulation"],
            gradient_checkpointing=True,
            optim="paged_adamw_8bit",
            logging_steps=10,
            save_strategy="epoch",
            evaluation_strategy="epoch",
            learning_rate=self.training_config["learning_rate"],
            warmup_steps=self.training_config["warmup_steps"],
            fp16=True,
            tf32=True,
            max_grad_norm=0.3,
            push_to_hub=False,
            report_to="none",
        )
        
        # Create trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=tokenizer,
        )
        
        # Train
        logger.info("Training started - this will take 1-2 hours...")
        trainer.train()
        
        # Save model
        trainer.save_model(f"{self.output_dir}/final")
        logger.info(f"✅ Model saved to {self.output_dir}/final")
        
        return trainer
    
    def test_model(self, model, tokenizer):
        """Test the fine-tuned model"""
        logger.info("\n" + "=" * 60)
        logger.info("Testing Fine-tuned Model")
        logger.info("=" * 60)
        
        test_queries = [
            "wind sites over 100kw in berkshire",
            "solar farms in Yorkshire",
            "what is the fit rate for fit id 1585",
            "sites expiring within 3 years"
        ]
        
        results = []
        for query in test_queries:
            prompt = f"""Parse this UK renewable energy query into JSON filters:

Query: {query}

JSON Output:"""
            
            inputs = tokenizer(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=100,
                    temperature=0.1,
                    do_sample=True,
                    top_p=0.9
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract JSON
            try:
                json_str = response.split("JSON Output:")[-1].strip()
                parsed = json.loads(json_str)
                logger.info(f"✅ Query: {query}")
                logger.info(f"   Result: {json.dumps(parsed, indent=2)}")
                results.append({"query": query, "success": True, "result": parsed})
            except:
                logger.error(f"❌ Query: {query}")
                results.append({"query": query, "success": False})
        
        success_rate = sum(1 for r in results if r["success"]) / len(results)
        logger.info(f"\nSuccess rate: {success_rate:.1%}")
        
        return results
    
    def export_to_ollama(self):
        """Export the fine-tuned model for Ollama"""
        logger.info("\nExporting to Ollama format...")
        
        # Create Modelfile
        modelfile = f"""FROM {self.output_dir}/final

SYSTEM "Parse UK renewable energy queries into JSON filters. Return only valid JSON."

PARAMETER temperature 0.1
PARAMETER top_p 0.9
"""
        
        with open(f"{self.output_dir}/Modelfile", 'w') as f:
            f.write(modelfile)
        
        logger.info(f"✅ Modelfile created at {self.output_dir}/Modelfile")
        logger.info("Deploy with: ollama create gpt-oss-fit-tuned -f Modelfile")

def main():
    """Main training pipeline"""
    
    trainer = GPTOSSLoRATrainer()
    
    # Check environment
    if not trainer.check_environment():
        logger.error("Environment not ready for training")
        logger.info("\nTo proceed, you need:")
        logger.info("1. Install PyTorch with CUDA support")
        logger.info("2. Install transformers, peft, bitsandbytes, accelerate")
        logger.info("3. Ensure training data is generated")
        return
    
    # User confirmation
    logger.info("\n" + "=" * 60)
    logger.info("Ready to start GPT-OSS LoRA training")
    logger.info("=" * 60)
    logger.info("\nThis will:")
    logger.info("• Load GPT-OSS 20B model with 4-bit quantization")
    logger.info("• Train with 3,195 FIT Intelligence examples")
    logger.info("• Take approximately 1-2 hours on RTX 3090")
    logger.info("• Use ~20GB VRAM")
    
    response = input("\nProceed with training? (y/n): ")
    if response.lower() != 'y':
        logger.info("Training cancelled")
        return
    
    # Prepare data
    train_data, val_data = trainer.prepare_data()
    
    # Setup model
    model, tokenizer = trainer.setup_model()
    if not model:
        logger.error("Failed to setup model")
        return
    
    # Train
    trainer.train(model, tokenizer, train_data, val_data)
    
    # Test
    trainer.test_model(model, tokenizer)
    
    # Export
    trainer.export_to_ollama()
    
    logger.info("\n✅ Training pipeline complete!")
    logger.info("\nNext steps:")
    logger.info("1. Deploy model with Ollama")
    logger.info("2. Update ollama_query_parser.py to use new model")
    logger.info("3. Test with critical queries")

if __name__ == "__main__":
    main()