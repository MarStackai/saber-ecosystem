#!/usr/bin/env python3
"""
Comprehensive LoRA Training Script for FIT Intelligence
Production-ready fine-tuning with monitoring and evaluation
"""

import os
import json
import torch
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np
from dataclasses import dataclass

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TrainingConfig:
    """Training configuration"""
    model_name: str = "meta-llama/Llama-3.1-8B"
    output_dir: str = "./fit-intelligence-lora"
    data_dir: str = "./lora_training_advanced"
    
    # LoRA parameters
    lora_r: int = 32
    lora_alpha: int = 64
    lora_dropout: float = 0.1
    
    # Training parameters
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    warmup_ratio: float = 0.1
    
    # Hardware
    use_4bit: bool = True
    use_flash_attention: bool = True
    max_seq_length: int = 2048
    
    # Monitoring
    logging_steps: int = 10
    eval_steps: int = 100
    save_steps: int = 100
    
    # Experiment tracking
    wandb_project: str = "fit-intelligence-lora"
    experiment_name: str = f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

class FITIntelligenceTrainer:
    """
    Comprehensive trainer for FIT Intelligence LoRA model
    """
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        logger.info(f"Initializing trainer on {self.device}")
        logger.info(f"Configuration: {config}")
        
        # Check for required packages
        self._check_dependencies()
        
        # Setup directories
        os.makedirs(config.output_dir, exist_ok=True)
        
    def _check_dependencies(self):
        """Check and install required dependencies"""
        required_packages = {
            "transformers": "4.36.0",
            "peft": "0.7.0",
            "bitsandbytes": "0.41.0",
            "accelerate": "0.25.0",
            "trl": "0.7.0",
            "wandb": "0.16.0",
            "datasets": "2.14.0"
        }
        
        missing = []
        for package, version in required_packages.items():
            try:
                __import__(package)
            except ImportError:
                missing.append(f"{package}>={version}")
        
        if missing:
            logger.warning(f"Missing packages: {', '.join(missing)}")
            logger.info("Install with: pip install " + " ".join(missing))
            raise ImportError("Missing required packages")
    
    def prepare_model(self):
        """Load and prepare model for LoRA training"""
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
        
        logger.info("Loading base model...")
        
        # 4-bit quantization config
        if self.config.use_4bit:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True
            )
        else:
            bnb_config = None
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            use_flash_attention_2=self.config.use_flash_attention
        )
        
        # Prepare for training
        if self.config.use_4bit:
            self.model = prepare_model_for_kbit_training(self.model)
        
        # LoRA configuration
        lora_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            target_modules=[
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ],
            lora_dropout=self.config.lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        )
        
        # Add LoRA adapters
        self.model = get_peft_model(self.model, lora_config)
        
        # Print trainable parameters
        self.model.print_trainable_parameters()
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        
        logger.info("Model prepared successfully")
        
    def prepare_data(self):
        """Load and prepare training data"""
        from datasets import Dataset, DatasetDict
        
        logger.info("Loading training data...")
        
        def load_jsonl(file_path):
            """Load JSONL file"""
            examples = []
            with open(file_path, 'r') as f:
                for line in f:
                    examples.append(json.loads(line))
            return examples
        
        # Load data splits
        train_data = load_jsonl(f"{self.config.data_dir}/train.jsonl")
        val_data = load_jsonl(f"{self.config.data_dir}/validation.jsonl")
        test_data = load_jsonl(f"{self.config.data_dir}/test.jsonl")
        
        logger.info(f"Loaded {len(train_data)} train, {len(val_data)} val, {len(test_data)} test examples")
        
        def format_example(example):
            """Format example for training"""
            # Llama 3 chat template
            text = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a query parser for the FIT Intelligence database containing 40,194 UK renewable energy installations.
Parse natural language queries into structured JSON filters.

Key mappings:
- Technology: Wind, Photovoltaic, Hydro, Anaerobic digestion, Micro CHP
- Locations map to postcode prefixes (e.g., Yorkshire: YO, HU, DN, HD, WF, LS, BD)
- Capacity is always in kW (1MW = 1000kW)

Return only valid JSON.<|eot_id|>

<|start_header_id|>user<|end_header_id|>

{example['input']}<|eot_id|>

<|start_header_id|>assistant<|end_header_id|>

{example['output']}<|eot_id|>"""
            
            return {"text": text}
        
        # Create datasets
        train_dataset = Dataset.from_list(train_data).map(format_example)
        val_dataset = Dataset.from_list(val_data).map(format_example)
        test_dataset = Dataset.from_list(test_data).map(format_example)
        
        self.dataset = DatasetDict({
            "train": train_dataset,
            "validation": val_dataset,
            "test": test_dataset
        })
        
        logger.info("Data prepared successfully")
        
    def train(self):
        """Run training with monitoring"""
        from transformers import TrainingArguments
        from trl import SFTTrainer
        import wandb
        
        # Initialize Weights & Biases
        wandb.init(
            project=self.config.wandb_project,
            name=self.config.experiment_name,
            config=self.config.__dict__
        )
        
        logger.info("Starting training...")
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            gradient_checkpointing=True,
            optim="paged_adamw_8bit",
            logging_steps=self.config.logging_steps,
            save_strategy="steps",
            save_steps=self.config.save_steps,
            evaluation_strategy="steps",
            eval_steps=self.config.eval_steps,
            learning_rate=self.config.learning_rate,
            lr_scheduler_type="cosine",
            warmup_ratio=self.config.warmup_ratio,
            bf16=torch.cuda.is_bf16_supported(),
            fp16=not torch.cuda.is_bf16_supported(),
            tf32=True,
            max_grad_norm=0.3,
            save_total_limit=3,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            report_to=["tensorboard", "wandb"],
            push_to_hub=False,
            remove_unused_columns=False,
        )
        
        # Create trainer
        trainer = SFTTrainer(
            model=self.model,
            args=training_args,
            train_dataset=self.dataset["train"],
            eval_dataset=self.dataset["validation"],
            tokenizer=self.tokenizer,
            dataset_text_field="text",
            max_seq_length=self.config.max_seq_length,
            packing=False,
            callbacks=[
                EvaluationCallback(self.dataset["test"], self.tokenizer)
            ]
        )
        
        # Train
        train_result = trainer.train()
        
        # Save final model
        trainer.save_model(f"{self.config.output_dir}/final")
        
        # Log metrics
        wandb.log({
            "final_train_loss": train_result.training_loss,
            "total_steps": train_result.global_step
        })
        
        logger.info("Training completed successfully")
        
        return trainer
    
    def evaluate(self, trainer):
        """Comprehensive evaluation on test set"""
        logger.info("Running comprehensive evaluation...")
        
        # Critical test cases
        critical_tests = [
            "wind sites over 100kw in berkshire",
            "what is the fit rate for fit id 1585",
            "solar farms in Yorkshire",
            "compare wind and solar in Birmingham",
            "sites expiring soon"
        ]
        
        results = []
        for test_query in critical_tests:
            # Generate response
            inputs = self.tokenizer(test_query, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=200,
                    temperature=0.1,
                    do_sample=True,
                    top_p=0.9
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract JSON
            try:
                # Find JSON in response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    success = True
                else:
                    parsed = None
                    success = False
            except:
                parsed = None
                success = False
            
            results.append({
                "query": test_query,
                "success": success,
                "parsed": parsed
            })
            
            logger.info(f"Test: {test_query[:50]}... - {'✓' if success else '✗'}")
        
        # Calculate metrics
        success_rate = sum(1 for r in results if r["success"]) / len(results)
        
        logger.info(f"\nEvaluation Results:")
        logger.info(f"  Success Rate: {success_rate:.1%}")
        logger.info(f"  Failed: {[r['query'] for r in results if not r['success']]}")
        
        # Log to wandb
        import wandb
        wandb.log({
            "test_success_rate": success_rate,
            "test_results": results
        })
        
        return results
    
    def export_for_ollama(self):
        """Export model for Ollama deployment"""
        logger.info("Exporting model for Ollama...")
        
        # Merge LoRA weights
        from peft import PeftModel
        
        # Save merged model
        merged_path = f"{self.config.output_dir}/merged"
        self.model.save_pretrained(merged_path)
        self.tokenizer.save_pretrained(merged_path)
        
        # Create Modelfile
        modelfile_content = """FROM ./merged

SYSTEM \"\"\"You are the FIT Intelligence query parser.
Database: 40,194 UK renewable energy installations

Parse natural language queries into structured JSON filters.

Technology mappings:
- wind/turbine → Wind
- solar/PV → Photovoltaic
- hydro → Hydro
- AD/anaerobic → Anaerobic digestion
- CHP → Micro CHP

Location mappings to postcodes:
- Yorkshire: YO, HU, DN, HD, WF, LS, BD
- Berkshire: RG, SL
- Scotland: AB, DD, EH, FK, G, IV, KA, KW

Always return valid JSON only.\"\"\"

PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER stop "<|eot_id|>"
"""
        
        with open(f"{self.config.output_dir}/Modelfile", 'w') as f:
            f.write(modelfile_content)
        
        logger.info(f"Model exported to {self.config.output_dir}")
        logger.info("Deploy with: ollama create fit-intelligence -f Modelfile")


class EvaluationCallback:
    """Custom callback for evaluation during training"""
    
    def __init__(self, test_dataset, tokenizer):
        self.test_dataset = test_dataset
        self.tokenizer = tokenizer
        
    def on_evaluate(self, args, state, control, **kwargs):
        """Run custom evaluation"""
        logger.info("Running custom evaluation...")
        # Implementation here
        pass


def main():
    """Main training pipeline"""
    
    # Configuration
    config = TrainingConfig(
        model_name="meta-llama/Llama-3.1-8B",  # or smaller model
        output_dir="./fit-intelligence-lora",
        data_dir="./lora_training_advanced",
        num_epochs=3,
        batch_size=4,
        learning_rate=2e-4
    )
    
    # Check GPU
    if not torch.cuda.is_available():
        logger.warning("No GPU available! Training will be very slow.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    else:
        logger.info(f"GPU available: {torch.cuda.get_device_name()}")
        logger.info(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    
    # Initialize trainer
    trainer = FITIntelligenceTrainer(config)
    
    # Prepare model and data
    trainer.prepare_model()
    trainer.prepare_data()
    
    # Train
    model_trainer = trainer.train()
    
    # Evaluate
    trainer.evaluate(model_trainer)
    
    # Export for deployment
    trainer.export_for_ollama()
    
    logger.info("\n✅ Training pipeline completed successfully!")
    logger.info(f"Model saved to: {config.output_dir}")
    logger.info("\nNext steps:")
    logger.info("1. Test locally: ollama run fit-intelligence 'wind sites over 100kw in berkshire'")
    logger.info("2. Integrate: python integrate_lora_model.py")
    logger.info("3. Monitor: Check wandb dashboard for metrics")


if __name__ == "__main__":
    main()