#!/usr/bin/env python3
"""
LoRA Training Pipeline for FIT Intelligence
Trains a local LLM to understand FIT database queries with proper filtering
"""

import json
import os
import re
import chromadb
from typing import List, Dict, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoRATrainingPipeline:
    """
    Complete pipeline for LoRA fine-tuning
    Generates data from actual queries and results
    """
    
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_collection("fit_licenses_nondomestic")
        
        # Load a sample to understand data structure
        self.sample_data = self.collection.get(limit=100)
        
        # Get unique values for training diversity
        self._analyze_data_distribution()
        
    def _analyze_data_distribution(self):
        """Analyze the data to create realistic training examples"""
        self.technologies = set()
        self.locations = set()
        self.postcodes = set()
        self.capacity_ranges = []
        
        for metadata in self.sample_data['metadatas']:
            if metadata:
                if metadata.get('technology'):
                    self.technologies.add(metadata['technology'])
                if metadata.get('local_authority'):
                    self.locations.add(metadata['local_authority'])
                if metadata.get('postcode'):
                    self.postcodes.add(metadata['postcode'][:2])  # Prefix only
                if metadata.get('capacity_kw'):
                    self.capacity_ranges.append(metadata['capacity_kw'])
        
        logger.info(f"Found {len(self.technologies)} technologies")
        logger.info(f"Found {len(self.locations)} locations")
        logger.info(f"Found {len(self.postcodes)} postcode areas")
    
    def generate_training_from_real_queries(self) -> List[Dict]:
        """
        Generate training data from real query patterns
        Based on actual user needs and common mistakes
        """
        training_examples = []
        
        # Real query patterns that failed
        failed_queries = [
            {
                "input": "wind sites over 100kw in berkshire",
                "current_behavior": "Returns all 3,206 wind sites",
                "correct_output": {
                    "technology": "Wind",
                    "capacity_min_kw": 100,
                    "postcode_patterns": ["RG", "SL"],
                    "location": "Berkshire"
                }
            },
            {
                "input": "Find wind farms in East Yorkshire",
                "current_behavior": "Returns all wind farms",
                "correct_output": {
                    "technology": "Wind",
                    "postcode_patterns": ["HU", "YO"],
                    "location": "East Yorkshire"
                }
            },
            {
                "input": "solar farms over 500kW in Yorkshire",
                "current_behavior": "No filtering applied",
                "correct_output": {
                    "technology": "Photovoltaic",
                    "capacity_min_kw": 500,
                    "postcode_patterns": ["YO", "HU", "DN", "HD", "WF", "LS", "BD"],
                    "location": "Yorkshire"
                }
            }
        ]
        
        # Convert to training format
        for example in failed_queries:
            training_examples.append({
                "instruction": "Parse this FIT database query into structured filters",
                "input": example["input"],
                "output": json.dumps(example["correct_output"], indent=2)
            })
        
        # Generate variations for each technology and location
        for tech in self.technologies:
            for location in list(self.locations)[:20]:  # Top 20 locations
                # Capacity query
                training_examples.append({
                    "instruction": "Parse this FIT database query into structured filters",
                    "input": f"{tech.lower()} installations over 100kW in {location}",
                    "output": json.dumps({
                        "technology": tech,
                        "capacity_min_kw": 100,
                        "location": location
                    }, indent=2)
                })
                
                # FIT rate query
                training_examples.append({
                    "instruction": "Parse this FIT database query into structured filters",
                    "input": f"what is the fit rate for {tech.lower()} in {location}",
                    "output": json.dumps({
                        "query_type": "fit_rate",
                        "technology": tech,
                        "location": location
                    }, indent=2)
                })
                
                # Regional revenue query
                training_examples.append({
                    "instruction": "Parse this FIT database query into structured filters",
                    "input": f"show regional adjusted revenue for {tech.lower()} in {location}",
                    "output": json.dumps({
                        "query_type": "regional_revenue",
                        "technology": tech,
                        "location": location,
                        "include_regional": True
                    }, indent=2)
                })
        
        # FIT ID queries
        for i in range(1, 100):
            fit_id = str(i * 100)  # Sample FIT IDs
            training_examples.append({
                "instruction": "Parse this FIT database query into structured filters",
                "input": f"what is the fit rate for fit id {fit_id}",
                "output": json.dumps({
                    "query_type": "fit_id_lookup",
                    "fit_id": fit_id,
                    "include_rate": True
                }, indent=2)
            })
        
        # Complex multi-filter queries
        complex_queries = [
            "wind farms over 500kW in Yorkshire with FIT expiring soon",
            "solar installations between 100 and 500 kW in the midlands",
            "all renewable installations in Scotland with regional capacity factors",
            "compare wind and solar performance in Birmingham",
            "best technology for 335kW installation in Berkshire"
        ]
        
        for query in complex_queries:
            # Parse manually for training
            output = self._parse_complex_query(query)
            training_examples.append({
                "instruction": "Parse this FIT database query into structured filters",
                "input": query,
                "output": json.dumps(output, indent=2)
            })
        
        return training_examples
    
    def _parse_complex_query(self, query: str) -> Dict:
        """Parse complex queries for training examples"""
        query_lower = query.lower()
        result = {}
        
        # Technology detection
        if 'wind' in query_lower:
            result['technology'] = 'Wind'
        elif 'solar' in query_lower or 'photovoltaic' in query_lower:
            result['technology'] = 'Photovoltaic'
        
        # Capacity parsing
        if 'over' in query_lower:
            # Extract number after 'over'
            match = re.search(r'over\s+(\d+)', query_lower)
            if match:
                result['capacity_min_kw'] = int(match.group(1))
        
        if 'between' in query_lower:
            match = re.search(r'between\s+(\d+)\s+and\s+(\d+)', query_lower)
            if match:
                result['capacity_min_kw'] = int(match.group(1))
                result['capacity_max_kw'] = int(match.group(2))
        
        # Location parsing
        location_mappings = {
            'yorkshire': {'postcode_patterns': ['YO', 'HU', 'DN', 'HD', 'WF', 'LS', 'BD']},
            'berkshire': {'postcode_patterns': ['RG', 'SL']},
            'midlands': {'postcode_patterns': ['B', 'CV', 'DE', 'DY', 'LE', 'NG']},
            'scotland': {'postcode_patterns': ['AB', 'DD', 'EH', 'FK', 'G', 'IV', 'KA', 'KW']},
            'birmingham': {'postcode_patterns': ['B']}
        }
        
        for location, data in location_mappings.items():
            if location in query_lower:
                result['location'] = location.title()
                result.update(data)
                break
        
        # Special query types
        if 'expiring' in query_lower:
            result['fit_remaining_max_years'] = 5
        if 'compare' in query_lower:
            result['query_type'] = 'comparison'
        if 'best' in query_lower:
            result['query_type'] = 'optimization'
        if 'regional' in query_lower or 'capacity factor' in query_lower:
            result['include_regional'] = True
        
        return result
    
    def create_ollama_modelfile(self) -> str:
        """
        Create Modelfile for Ollama deployment
        """
        modelfile_content = """# FIT Intelligence Query Parser
# Based on Llama 3.1 8B fine-tuned for FIT database queries

FROM llama3.1:8b

# System prompt
SYSTEM \"\"\"You are a query parser for the FIT Intelligence database containing 40,194 UK renewable energy installations.

Your task is to parse natural language queries into structured JSON filters.

Key mappings:
- Wind/wind turbine/wind farm -> technology: "Wind"
- Solar/photovoltaic/PV -> technology: "Photovoltaic"  
- Hydro/water -> technology: "Hydro"
- AD/anaerobic/digestion -> technology: "Anaerobic digestion"
- CHP/combined heat -> technology: "Micro CHP"

Locations to postcodes:
- Yorkshire: YO, HU, DN, HD, WF, LS, BD
- Berkshire: RG, SL
- Scotland: AB, DD, EH, FK, G, IV, KA, KW
- Birmingham/Midlands: B, CV, DE, DY, LE, NG

Always return valid JSON with appropriate filters.\"\"\"

# Temperature for consistent parsing
PARAMETER temperature 0.1
PARAMETER top_p 0.9

# Template for responses
TEMPLATE \"\"\"
{{ .System }}

User Query: {{ .Prompt }}

Parsed JSON:
\"\"\"
"""
        return modelfile_content
    
    def save_training_data(self, output_dir: str = "./lora_training"):
        """Save all training data and configuration files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate training data
        logger.info("Generating training examples...")
        training_data = self.generate_training_from_real_queries()
        
        # Save in different formats
        # JSONL format for fine-tuning
        with open(f"{output_dir}/fit_queries.jsonl", 'w') as f:
            for example in training_data:
                f.write(json.dumps(example) + '\n')
        
        # Alpaca format for some trainers
        alpaca_data = []
        for example in training_data:
            alpaca_data.append({
                "instruction": example["instruction"],
                "input": example["input"],
                "output": example["output"]
            })
        
        with open(f"{output_dir}/fit_queries_alpaca.json", 'w') as f:
            json.dump(alpaca_data, f, indent=2)
        
        # Save Modelfile
        with open(f"{output_dir}/Modelfile", 'w') as f:
            f.write(self.create_ollama_modelfile())
        
        # Save training script
        self._save_training_script(output_dir)
        
        logger.info(f"Saved {len(training_data)} training examples to {output_dir}")
        
        return len(training_data)
    
    def _save_training_script(self, output_dir: str):
        """Save the training script for running LoRA fine-tuning"""
        script_content = """#!/bin/bash
# LoRA Fine-tuning Script for FIT Intelligence

# Install requirements
pip install unsloth torch transformers datasets

# Run training
python -c "
from unsloth import FastLanguageModel
import torch
from transformers import TrainingArguments
from trl import SFTTrainer
from datasets import load_dataset

# Load base model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name='unsloth/llama-3-8b-bnb-4bit',
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

# Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj'],
    lora_alpha=16,
    lora_dropout=0,
    bias='none',
    use_gradient_checkpointing=True,
    random_state=3407,
)

# Load dataset
dataset = load_dataset('json', data_files='fit_queries.jsonl')

# Training arguments
training_args = TrainingArguments(
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    warmup_steps=5,
    max_steps=100,
    learning_rate=2e-4,
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    logging_steps=1,
    optim='adamw_8bit',
    output_dir='./fit_lora_model',
)

# Trainer
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset['train'],
    dataset_text_field='input',
    max_seq_length=512,
    args=training_args,
)

# Train
trainer.train()

# Save
model.save_pretrained('fit_intelligence_lora')
print('Training complete! Model saved to fit_intelligence_lora')
"

echo "Training complete! Now create Ollama model:"
echo "ollama create fit-intelligence -f Modelfile"
"""
        
        script_path = f"{output_dir}/train_lora.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        logger.info(f"Training script saved to {script_path}")


def main():
    """Run the LoRA training pipeline"""
    pipeline = LoRATrainingPipeline()
    
    logger.info("="*60)
    logger.info("FIT Intelligence LoRA Training Pipeline")
    logger.info("="*60)
    
    # Save training data
    num_examples = pipeline.save_training_data()
    
    print(f"\n✅ Training pipeline ready!")
    print(f"   Generated {num_examples} training examples")
    print(f"   Training data saved to ./lora_training/")
    print(f"\nNext steps:")
    print("1. Review training data: cat lora_training/fit_queries.jsonl | head")
    print("2. Run training: ./lora_training/train_lora.sh")
    print("3. Deploy with Ollama: ollama create fit-intelligence -f lora_training/Modelfile")
    print("4. Test: ollama run fit-intelligence 'wind sites over 100kw in berkshire'")


if __name__ == "__main__":
    main()