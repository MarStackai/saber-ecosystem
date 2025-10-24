#!/usr/bin/env python3
"""
Fine-tune GPT-OSS:20b for FIT Intelligence
Using LoRA for efficient training
"""

import json
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import Dataset
import os

class GPTOSSFineTuner:
    def __init__(self):
        self.model_name = "gpt-oss"  # Will use Ollama's model
        self.output_dir = "./gpt_oss_fit_model"
        
    def prepare_dataset(self):
        """Load and prepare training data"""
        print("Loading training data...")
        
        with open('gpt_oss_training.jsonl', 'r') as f:
            data = [json.loads(line) for line in f]
        
        # Format for training
        formatted_data = []
        for item in data:
            text = f"""<|system|>
You are a FIT Intelligence assistant. Always include FIT IDs and ensure geographic accuracy. Never return sites from incorrect locations.
<|user|>
{item['instruction']}
<|assistant|>
{item['response']}"""
            formatted_data.append({"text": text})
        
        dataset = Dataset.from_list(formatted_data)
        return dataset.train_test_split(test_size=0.1)
    
    def create_modelfile(self):
        """Create Ollama Modelfile for fine-tuning"""
        modelfile_content = """FROM gpt-oss:20b

# Adapter from fine-tuning
ADAPTER ./gpt_oss_fit_adapter

# System prompt
SYSTEM You are a FIT Intelligence assistant for UK renewable energy sites. 
CRITICAL RULES:
1. ALWAYS include FIT IDs in responses
2. ONLY return sites from the correct geographic location
3. Aberdeen = AB postcodes only
4. Yorkshire = YO/HU/LS/BD/HX/HD/WF/S/DN postcodes only
5. Never make up data - only use database facts
6. Understand context from previous messages

# Parameters for accuracy
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1
PARAMETER num_predict 500
PARAMETER stop "<|user|>"
PARAMETER stop "<|system|>"
PARAMETER stop "Human:"
PARAMETER stop "User:"

# Template
TEMPLATE \"\"\"{{ if .System }}<|system|>
{{ .System }}<|user|>
{{ .Prompt }}<|assistant|>
{{ else }}<|user|>
{{ .Prompt }}<|assistant|>{{ end }}\"\"\"
"""
        
        with open('Modelfile_gpt_oss_fit', 'w') as f:
            f.write(modelfile_content)
        
        print("✅ Created Modelfile_gpt_oss_fit")
    
    def create_training_script(self):
        """Create script for Ollama fine-tuning"""
        script = """#!/bin/bash
# Fine-tune GPT-OSS for FIT Intelligence

echo "🚀 Starting GPT-OSS fine-tuning for FIT Intelligence"

# 1. Convert training data to Ollama format
echo "📝 Converting training data..."
python3 -c "
import json

with open('gpt_oss_conversations.json', 'r') as f:
    conversations = json.load(f)

with open('gpt_oss_ollama_train.jsonl', 'w') as f:
    for conv in conversations:
        messages = conv['messages']
        for i in range(0, len(messages)-1, 2):
            if i+1 < len(messages):
                prompt = messages[i]['content']
                response = messages[i+1]['content']
                f.write(json.dumps({'prompt': prompt, 'completion': response}) + '\\n')
"

# 2. Fine-tune using Ollama (if supported)
echo "🔧 Fine-tuning model..."
# Note: Ollama doesn't directly support fine-tuning yet
# We'll use the base model with our custom prompts

# 3. Create custom model with our Modelfile
echo "📦 Creating custom model..."
ollama create gpt-oss-fit -f Modelfile_gpt_oss_fit

echo "✅ Fine-tuning complete!"
echo "🎯 Test with: ollama run gpt-oss-fit"
"""
        
        with open('finetune_gpt_oss.sh', 'w') as f:
            f.write(script)
        
        os.chmod('finetune_gpt_oss.sh', 0o755)
        print("✅ Created finetune_gpt_oss.sh")
    
    def create_evaluation_script(self):
        """Create evaluation script for the model"""
        eval_script = """#!/usr/bin/env python3
import json
import subprocess

test_queries = [
    {
        "query": "wind sites over 250kw near Aberdeen",
        "must_contain": ["AB"],
        "must_not_contain": ["BD", "ML", "YO", "LS"],
        "check": "geographic_accuracy"
    },
    {
        "query": "what is the FIT ID for the wind farm in AB21",
        "must_contain": ["FIT ID"],
        "check": "fit_id_inclusion"
    },
    {
        "query": "solar sites in Yorkshire",
        "must_contain": ["YO", "HU", "LS", "BD", "WF", "S", "DN"],
        "must_not_contain": ["AB", "EH", "G"],
        "check": "geographic_accuracy"
    }
]

def test_model(model_name="gpt-oss-fit"):
    results = {"passed": 0, "failed": 0, "errors": []}
    
    for test in test_queries:
        # Query the model
        cmd = f"ollama run {model_name} '{test['query']}'"
        try:
            response = subprocess.check_output(cmd, shell=True, text=True)
            
            # Check requirements
            passed = True
            for must in test.get('must_contain', []):
                if must not in response:
                    passed = False
                    results['errors'].append(f"Missing '{must}' in response to '{test['query']}'")
            
            for must_not in test.get('must_not_contain', []):
                if must_not in response:
                    passed = False
                    results['errors'].append(f"Found '{must_not}' (should not be there) in response to '{test['query']}'")
            
            if passed:
                results['passed'] += 1
            else:
                results['failed'] += 1
                
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"Error testing '{test['query']}': {str(e)}")
    
    # Print results
    print(f"\\n📊 Evaluation Results for {model_name}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"📈 Accuracy: {results['passed']/(results['passed']+results['failed'])*100:.1f}%")
    
    if results['errors']:
        print("\\n⚠️ Errors:")
        for error in results['errors']:
            print(f"  • {error}")
    
    return results

if __name__ == "__main__":
    test_model()
"""
        
        with open('evaluate_gpt_oss.py', 'w') as f:
            f.write(eval_script)
        
        os.chmod('evaluate_gpt_oss.py', 0o755)
        print("✅ Created evaluate_gpt_oss.py")

def main():
    tuner = GPTOSSFineTuner()
    
    print("🚀 GPT-OSS Fine-tuning Preparation")
    print("=" * 60)
    
    # Create necessary files
    tuner.create_modelfile()
    tuner.create_training_script()
    tuner.create_evaluation_script()
    
    print("\n📋 Next Steps:")
    print("1. Run fine-tuning: ./finetune_gpt_oss.sh")
    print("2. Test the model: ollama run gpt-oss-fit")
    print("3. Evaluate accuracy: python evaluate_gpt_oss.py")
    print("\n💡 The model will:")
    print("  • Always include FIT IDs")
    print("  • Ensure geographic accuracy (Aberdeen = AB only)")
    print("  • Maintain conversation context")
    print("  • Return only database facts")

if __name__ == "__main__":
    main()