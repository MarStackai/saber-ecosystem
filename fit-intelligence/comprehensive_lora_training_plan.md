# Comprehensive LoRA Training Plan for FIT Intelligence
## Advanced Local LLM Fine-Tuning for Query Understanding

---

## Executive Summary

We're training a specialized LLM to understand and parse complex natural language queries about 40,194 UK renewable energy installations. The model will replace our current regex-based parser that fails on basic queries like "wind sites over 100kw in berkshire".

### Current Problem
- **Query**: "wind sites over 100kw in berkshire"
- **Expected**: 1 site (FIT 4004, 500kW in RG17)
- **Actual**: ALL 3,206 wind sites (no filtering)

### Solution
LoRA fine-tuning of Llama 3.1 8B to understand:
- Technology mappings (wind → Wind, solar → Photovoltaic)
- Location to postcode mapping (Berkshire → RG/SL)
- Capacity filtering (over 100kw → capacity_min_kw: 100)
- Complex multi-filter queries
- Regional calculations and FIT rates

---

## Phase 1: Data Preparation (Week 1)

### 1.1 Training Data Generation

#### A. Query Pattern Analysis
Analyze actual failed queries from our system:

```python
# Failed Query Analysis
failed_patterns = {
    "location_not_filtered": [
        "wind farms in Yorkshire",  # Returns all wind, not Yorkshire
        "solar in Berkshire",        # Returns all solar
        "hydro in Scotland"          # Returns all hydro
    ],
    "capacity_not_filtered": [
        "over 100kw",                # Ignored
        "between 100 and 500 kw",    # Not parsed
        "large installations"         # Not understood
    ],
    "combined_failures": [
        "wind over 500kw in Yorkshire",  # No filters work
        "small solar in Birmingham"      # Misses both filters
    ]
}
```

#### B. Comprehensive Training Dataset Structure

```python
# Training Example Categories
categories = {
    "basic_technology": 500 examples,
    "location_mapping": 1000 examples,
    "capacity_filtering": 500 examples,
    "combined_queries": 1000 examples,
    "fit_rate_queries": 300 examples,
    "regional_calculations": 300 examples,
    "aggregations": 200 examples,
    "comparisons": 200 examples,
    "business_queries": 500 examples
}
# Total: 4,500 training examples
```

#### C. Data Augmentation Strategy

1. **Technology Variations**
   - Wind: wind, turbine, wind farm, wind turbine, wind power
   - Solar: solar, PV, photovoltaic, solar panel, solar farm
   - Hydro: hydro, water, hydroelectric, water turbine
   - AD: anaerobic, digestion, AD, biogas
   - CHP: combined heat, CHP, cogeneration

2. **Location Variations**
   - Full names: Yorkshire, Berkshire, Scotland
   - Abbreviations: Yorks, Berks
   - Regions: North England, South East
   - Postcodes: YO17, RG17, HU15

3. **Capacity Expressions**
   - Exact: 100kW, 500 kilowatts, 1MW, 1 megawatt
   - Ranges: 100-500kW, between 100 and 500
   - Descriptive: small (<50kW), medium (50-500kW), large (>500kW)
   - Comparisons: over, under, above, below, greater than

### 1.2 Training Data Quality Control

```python
# Validation Rules for Training Data
validation_rules = {
    "technology_consistency": "Wind always maps to 'Wind' not 'wind'",
    "postcode_accuracy": "Yorkshire must include YO, HU, DN, HD, WF, LS, BD",
    "capacity_units": "Always convert to kW (1MW = 1000kW)",
    "json_validity": "All outputs must be valid JSON",
    "field_naming": "Use exact field names from database schema"
}
```

---

## Phase 2: Model Selection & Setup (Week 1-2)

### 2.1 Base Model Evaluation

#### Option A: Llama 3.1 8B (Recommended)
```yaml
Model: meta-llama/Llama-3.1-8B
Parameters: 8 billion
Context: 128k tokens
Advantages:
  - Latest Llama model with improved reasoning
  - Large context for complex queries
  - Good JSON generation
  - Excellent instruction following
Requirements:
  - VRAM: 16GB (4-bit quantized)
  - Disk: 15GB
```

#### Option B: Mistral 7B
```yaml
Model: mistralai/Mistral-7B-Instruct-v0.2
Parameters: 7 billion
Context: 32k tokens
Advantages:
  - Slightly smaller than Llama
  - Good for structured output
  - Fast inference
Requirements:
  - VRAM: 14GB (4-bit quantized)
  - Disk: 13GB
```

#### Option C: Phi-3 Mini (Budget Option)
```yaml
Model: microsoft/Phi-3-mini-4k-instruct
Parameters: 3.8 billion
Context: 4k tokens
Advantages:
  - Runs on smaller GPUs
  - Very fast inference
  - Good for simple queries
Requirements:
  - VRAM: 8GB (4-bit quantized)
  - Disk: 7GB
```

### 2.2 LoRA Configuration

```python
# Optimal LoRA Configuration for Query Parsing
lora_config = LoRAConfig(
    r=32,                    # Rank (higher = more capacity)
    lora_alpha=64,           # Scaling parameter
    target_modules=[         # Which layers to train
        "q_proj",           # Query projection
        "k_proj",           # Key projection
        "v_proj",           # Value projection
        "o_proj",           # Output projection
        "gate_proj",        # MLP layers
        "up_proj",
        "down_proj"
    ],
    lora_dropout=0.1,       # Regularization
    bias="none",            # Don't train biases
    task_type="CAUSAL_LM",  # Language modeling task
)

# Training Hyperparameters
training_args = TrainingArguments(
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,  # Effective batch size = 16
    num_train_epochs=3,
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_ratio=0.1,
    logging_steps=10,
    save_steps=100,
    eval_steps=100,
    evaluation_strategy="steps",
    save_total_limit=3,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    fp16=True,  # Mixed precision training
    optim="paged_adamw_8bit",  # Memory efficient optimizer
    report_to=["tensorboard", "wandb"],
)
```

---

## Phase 3: Training Pipeline Implementation (Week 2)

### 3.1 Complete Training Script

```python
#!/usr/bin/env python3
"""
Comprehensive LoRA Training Script for FIT Intelligence
"""

import torch
import json
from datasets import Dataset, DatasetDict
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM
import wandb

class FITQueryTrainer:
    def __init__(self, model_name="meta-llama/Llama-3.1-8B"):
        self.model_name = model_name
        
        # Weights & Biases logging
        wandb.init(project="fit-intelligence-lora")
        
        # 4-bit quantization for memory efficiency
        self.bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True
        )
        
    def prepare_model(self):
        """Load and prepare model for LoRA training"""
        # Load base model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=self.bnb_config,
            device_map="auto",
            trust_remote_code=True
        )
        
        # Prepare for k-bit training
        self.model = prepare_model_for_kbit_training(self.model)
        
        # Add LoRA adapters
        peft_config = LoraConfig(
            r=32,
            lora_alpha=64,
            target_modules=[
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ],
            lora_dropout=0.1,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        self.model = get_peft_model(self.model, peft_config)
        self.model.print_trainable_parameters()
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
    def prepare_dataset(self, train_file, eval_file):
        """Load and format training data"""
        
        def format_instruction(example):
            """Format as instruction-following"""
            prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a query parser for the FIT Intelligence database containing 40,194 UK renewable energy installations.
Parse natural language queries into structured JSON filters.

Technology mappings:
- wind/turbine → "Wind"
- solar/PV/photovoltaic → "Photovoltaic"
- hydro/water → "Hydro"
- AD/anaerobic → "Anaerobic digestion"
- CHP/combined heat → "Micro CHP"

Location to postcode mappings:
- Yorkshire: ["YO", "HU", "DN", "HD", "WF", "LS", "BD"]
- Berkshire: ["RG", "SL"]
- Scotland: ["AB", "DD", "EH", "FK", "G", "IV", "KA", "KW"]

Always return valid JSON.<|eot_id|>

<|start_header_id|>user<|end_header_id|>
{example['input']}<|eot_id|>

<|start_header_id|>assistant<|end_header_id|>
{example['output']}<|eot_id|>"""
            return {"text": prompt}
        
        # Load datasets
        with open(train_file, 'r') as f:
            train_data = [json.loads(line) for line in f]
        
        with open(eval_file, 'r') as f:
            eval_data = [json.loads(line) for line in f]
        
        # Create datasets
        train_dataset = Dataset.from_list(train_data)
        eval_dataset = Dataset.from_list(eval_data)
        
        # Format for training
        train_dataset = train_dataset.map(format_instruction)
        eval_dataset = eval_dataset.map(format_instruction)
        
        return DatasetDict({
            "train": train_dataset,
            "eval": eval_dataset
        })
    
    def train(self, output_dir="./fit-query-lora"):
        """Run training"""
        
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=4,
            gradient_checkpointing=True,
            optim="paged_adamw_8bit",
            logging_steps=10,
            save_strategy="steps",
            save_steps=100,
            evaluation_strategy="steps",
            eval_steps=100,
            learning_rate=2e-4,
            lr_scheduler_type="cosine",
            warmup_ratio=0.1,
            bf16=True,
            tf32=True,
            max_grad_norm=0.3,
            save_total_limit=3,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            report_to=["tensorboard", "wandb"],
        )
        
        # Create trainer
        trainer = SFTTrainer(
            model=self.model,
            args=training_args,
            train_dataset=self.dataset["train"],
            eval_dataset=self.dataset["eval"],
            tokenizer=self.tokenizer,
            dataset_text_field="text",
            max_seq_length=2048,
            packing=False,
        )
        
        # Train
        trainer.train()
        
        # Save final model
        trainer.save_model(f"{output_dir}/final")
        
        return trainer

# Usage
if __name__ == "__main__":
    trainer = FITQueryTrainer()
    trainer.prepare_model()
    trainer.dataset = trainer.prepare_dataset(
        "lora_training/train.jsonl",
        "lora_training/eval.jsonl"
    )
    trainer.train()
```

### 3.2 Data Split Strategy

```python
# 80/10/10 Train/Val/Test Split
total_examples = 4500
train_size = 3600  # 80%
val_size = 450     # 10%
test_size = 450    # 10%

# Stratified by query type
split_strategy = {
    "train": {
        "simple_queries": 1000,
        "complex_queries": 1500,
        "business_queries": 1100
    },
    "validation": {
        "simple_queries": 150,
        "complex_queries": 150,
        "business_queries": 150
    },
    "test": {
        "unseen_combinations": 450  # Novel query patterns
    }
}
```

---

## Phase 4: Evaluation & Testing (Week 3)

### 4.1 Evaluation Metrics

```python
# Comprehensive Evaluation Suite
evaluation_metrics = {
    "parsing_accuracy": {
        "description": "% of queries correctly parsed to JSON",
        "target": ">95%"
    },
    "field_accuracy": {
        "description": "% of JSON fields correctly extracted",
        "target": ">98%"
    },
    "postcode_mapping": {
        "description": "% of locations correctly mapped to postcodes",
        "target": ">99%"
    },
    "capacity_parsing": {
        "description": "% of capacity values correctly parsed",
        "target": ">97%"
    },
    "combined_query_success": {
        "description": "% of multi-filter queries correctly parsed",
        "target": ">90%"
    }
}
```

### 4.2 Test Cases

```python
# Critical Test Cases That Must Pass
critical_tests = [
    {
        "query": "wind sites over 100kw in berkshire",
        "expected": {
            "technology": "Wind",
            "capacity_min_kw": 100,
            "postcode_patterns": ["RG", "SL"]
        },
        "validates": "Original failing query"
    },
    {
        "query": "what is the fit rate for fit id 1585",
        "expected": {
            "query_type": "fit_rate",
            "fit_id": "1585"
        },
        "validates": "FIT rate lookup"
    },
    {
        "query": "compare wind and solar in Yorkshire",
        "expected": {
            "query_type": "comparison",
            "technologies": ["Wind", "Photovoltaic"],
            "postcode_patterns": ["YO", "HU", "DN", "HD", "WF", "LS", "BD"]
        },
        "validates": "Technology comparison"
    },
    {
        "query": "show regional adjusted revenue for all wind farms",
        "expected": {
            "technology": "Wind",
            "include_regional": true,
            "include_revenue": true
        },
        "validates": "Regional calculations"
    }
]
```

### 4.3 A/B Testing Protocol

```python
# Compare LoRA vs Current System
ab_test_protocol = {
    "test_queries": 1000,
    "metrics": {
        "success_rate": "% of queries returning correct results",
        "response_time": "Average query processing time",
        "user_satisfaction": "Based on result relevance"
    },
    "duration": "1 week",
    "rollout_strategy": {
        "week_1": "10% traffic to LoRA",
        "week_2": "50% traffic to LoRA",
        "week_3": "100% traffic to LoRA"
    }
}
```

---

## Phase 5: Deployment & Integration (Week 3-4)

### 5.1 Ollama Deployment

```bash
# Step 1: Convert to GGUF format
python convert.py fit-query-lora \
    --outfile fit-intelligence.gguf \
    --quantize q4_k_m

# Step 2: Create Modelfile
cat > Modelfile << 'EOF'
FROM fit-intelligence.gguf

SYSTEM """You are the FIT Intelligence query parser.
Database: 40,194 UK renewable installations
Task: Parse natural language to JSON filters

Key mappings:
- Technology: Wind, Photovoltaic, Hydro, Anaerobic digestion, Micro CHP
- Locations: Map to postcode prefixes
- Capacity: Always in kW

Return valid JSON only."""

PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1
PARAMETER stop "<|eot_id|>"
PARAMETER stop "</s>"
EOF

# Step 3: Create Ollama model
ollama create fit-intelligence -f Modelfile

# Step 4: Test
ollama run fit-intelligence "wind sites over 100kw in berkshire"
```

### 5.2 Python Integration

```python
# Integration with Existing System
import ollama
import json

class LoRAQueryParser:
    def __init__(self, model_name="fit-intelligence"):
        self.client = ollama.Client()
        self.model = model_name
        
    def parse_query(self, user_query: str) -> dict:
        """Parse natural language query using LoRA model"""
        
        response = self.client.generate(
            model=self.model,
            prompt=user_query,
            format="json",
            options={
                "temperature": 0.1,
                "top_p": 0.9
            }
        )
        
        try:
            # Parse JSON response
            filters = json.loads(response['response'])
            
            # Validate required fields
            self._validate_filters(filters)
            
            return {
                "success": True,
                "filters": filters
            }
        except Exception as e:
            # Fallback to regex parser
            return {
                "success": False,
                "error": str(e),
                "fallback": True
            }
    
    def _validate_filters(self, filters: dict):
        """Validate parsed filters"""
        
        # Check technology values
        valid_technologies = [
            "Wind", "Photovoltaic", "Hydro", 
            "Anaerobic digestion", "Micro CHP"
        ]
        
        if "technology" in filters:
            if filters["technology"] not in valid_technologies:
                raise ValueError(f"Invalid technology: {filters['technology']}")
        
        # Validate capacity is numeric
        if "capacity_min_kw" in filters:
            if not isinstance(filters["capacity_min_kw"], (int, float)):
                raise ValueError("Capacity must be numeric")
        
        # Validate postcode patterns
        if "postcode_patterns" in filters:
            if not isinstance(filters["postcode_patterns"], list):
                raise ValueError("Postcode patterns must be a list")

# Replace existing parser
def upgrade_nlp_processor():
    """Upgrade to LoRA-based parser"""
    
    # Backup current parser
    import shutil
    shutil.copy(
        "enhanced_nlp_processor.py",
        "enhanced_nlp_processor_backup.py"
    )
    
    # Inject LoRA parser
    lora_parser = LoRAQueryParser()
    
    # Update the NLP processor
    # ... integration code ...
```

### 5.3 Performance Monitoring

```python
# Production Monitoring
monitoring_config = {
    "metrics": {
        "query_success_rate": {
            "alert_threshold": 0.95,
            "window": "5m"
        },
        "response_time_p99": {
            "alert_threshold": 500,  # ms
            "window": "5m"
        },
        "model_errors": {
            "alert_threshold": 10,
            "window": "1h"
        }
    },
    "logging": {
        "failed_queries": "log/failed_queries.jsonl",
        "slow_queries": "log/slow_queries.jsonl",
        "successful_queries": "log/success_sample.jsonl"
    },
    "dashboards": {
        "grafana": "http://localhost:3000/dashboard/fit-lora",
        "wandb": "https://wandb.ai/fit-intelligence/lora-prod"
    }
}
```

---

## Phase 6: Continuous Improvement (Ongoing)

### 6.1 Feedback Loop

```python
# Automated Retraining Pipeline
class ContinuousLearning:
    def __init__(self):
        self.feedback_threshold = 100  # New examples before retraining
        self.accuracy_threshold = 0.95  # Minimum acceptable accuracy
        
    def collect_feedback(self):
        """Collect failed queries for retraining"""
        
        failed_queries = []
        
        # From production logs
        with open("log/failed_queries.jsonl", "r") as f:
            for line in f:
                query = json.loads(line)
                if query["manually_corrected"]:
                    failed_queries.append({
                        "input": query["original_query"],
                        "output": query["corrected_filters"]
                    })
        
        return failed_queries
    
    def trigger_retraining(self):
        """Automatically retrain when threshold reached"""
        
        new_examples = self.collect_feedback()
        
        if len(new_examples) >= self.feedback_threshold:
            # Add to training data
            with open("lora_training/feedback.jsonl", "a") as f:
                for example in new_examples:
                    f.write(json.dumps(example) + "\n")
            
            # Trigger retraining job
            self.retrain_model()
    
    def retrain_model(self):
        """Retrain with new data"""
        
        # Run training script
        subprocess.run([
            "python", "train_lora.py",
            "--resume_from_checkpoint", "latest",
            "--new_data", "lora_training/feedback.jsonl"
        ])
```

### 6.2 Version Management

```yaml
# Model Version Tracking
model_versions:
  v1.0:
    date: "2024-01-20"
    training_examples: 4500
    accuracy: 0.92
    status: "deprecated"
    
  v1.1:
    date: "2024-02-01"
    training_examples: 5500
    accuracy: 0.95
    improvements:
      - "Added regional calculations"
      - "Fixed Yorkshire postcode mapping"
    status: "production"
    
  v1.2:
    date: "2024-02-15"
    training_examples: 6500
    accuracy: 0.97
    improvements:
      - "Better capacity parsing"
      - "Multi-technology queries"
    status: "staging"
```

---

## Resource Requirements

### Hardware Requirements

```yaml
Training:
  GPU: NVIDIA RTX 3090 or better (24GB VRAM)
  RAM: 32GB minimum
  Storage: 100GB SSD
  Time: 8-12 hours for full training

Inference:
  GPU: NVIDIA RTX 3060 (12GB VRAM) or CPU
  RAM: 16GB
  Storage: 20GB
  Latency: <100ms per query
```

### Software Stack

```yaml
Core:
  - Python: 3.10+
  - PyTorch: 2.1+
  - Transformers: 4.36+
  - PEFT: 0.7+
  - Ollama: 0.1.20+

Training:
  - Unsloth: Latest
  - BitsAndBytes: 0.41+
  - Accelerate: 0.25+
  - Wandb: 0.16+

Deployment:
  - FastAPI: 0.104+
  - Redis: For caching
  - PostgreSQL: Query logs
  - Grafana: Monitoring
```

---

## Success Criteria

### Week 1 Milestone
- [ ] 4,500 training examples generated
- [ ] Base model selected and downloaded
- [ ] Training environment configured

### Week 2 Milestone
- [ ] First training run complete
- [ ] 90%+ parsing accuracy achieved
- [ ] Ollama model created

### Week 3 Milestone
- [ ] A/B testing started
- [ ] Integration with chat interface
- [ ] Performance monitoring active

### Week 4 Milestone
- [ ] 95%+ accuracy on all query types
- [ ] Full production deployment
- [ ] Feedback loop operational

### Success Metrics
- **Primary**: Fix "wind sites over 100kw in berkshire" → 1 result
- **Query Success Rate**: >95% correct parsing
- **Response Time**: <100ms inference
- **User Satisfaction**: >90% relevant results

---

## Risk Mitigation

### Technical Risks
1. **Model Hallucination**
   - Mitigation: Low temperature (0.1), strict JSON validation
   
2. **Performance Degradation**
   - Mitigation: Keep regex parser as fallback
   
3. **Memory Issues**
   - Mitigation: 4-bit quantization, gradient checkpointing

### Business Risks
1. **Incorrect Financial Calculations**
   - Mitigation: Never let model calculate, only parse
   
2. **Data Leakage**
   - Mitigation: Train only on query→filter mappings

---

## Appendix: Example Training Data

```json
{
  "instruction": "Parse this FIT database query into structured filters",
  "input": "find all wind farms over 500kW in Yorkshire that are good for repowering",
  "output": {
    "technology": "Wind",
    "capacity_min_kw": 500,
    "postcode_patterns": ["YO", "HU", "DN", "HD", "WF", "LS", "BD"],
    "location": "Yorkshire",
    "fit_remaining_max_years": 10,
    "query_intent": "repowering_opportunities"
  }
}
```

This comprehensive plan provides a production-ready path from our current broken parser to an intelligent, LoRA-powered query understanding system.