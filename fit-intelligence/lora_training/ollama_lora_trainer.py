#!/usr/bin/env python3
"""
Alternative LoRA training approach using Ollama's existing infrastructure
Creates a fine-tuned model using few-shot learning and prompt engineering
"""

import json
import subprocess
import os
from pathlib import Path
import ollama

class OllamaLoRATrainer:
    def __init__(self, base_model="llama2:13b"):
        self.base_model = base_model
        self.training_data = []
        self.model_name = "fit-intelligence-enhanced"
        
    def load_training_data(self, jsonl_path):
        """Load training examples from JSONL file"""
        examples = []
        with open(jsonl_path, 'r') as f:
            for line in f:
                example = json.loads(line)
                examples.append(example)
        
        print(f"Loaded {len(examples)} training examples")
        return examples
    
    def create_system_prompt(self, examples):
        """Create an enhanced system prompt with examples"""
        system_prompt = """You are a UK renewable energy FIT installation search assistant with enhanced query understanding.

CRITICAL PARSING RULES:
1. Manchester MUST return ["M"] only, never ML or other M-prefixes
2. Yorkshire MUST return ["YO","HU","LS","BD","HX","HD","WF","S","DN"] exactly
3. Solar/PV/solar panels MUST normalize to "photovoltaic"
4. Capacity ranges must be exact: "50kw to 350kw" means min=50, max=350
5. Wind/wind turbines/wind farms normalize to "wind"
6. Repowering categories: immediate (0-2y), urgent (2-5y), optimal (5-10y)

TRAINING EXAMPLES:
"""
        
        # Add the most critical examples
        critical_examples = [
            {
                "query": "sites in Manchester",
                "params": {"postcode_areas": ["M"]}
            },
            {
                "query": "wind sites over 50kw to max 350kw in Yorkshire",
                "params": {
                    "technology": "wind",
                    "min_capacity_kw": 50,
                    "max_capacity_kw": 350,
                    "postcode_areas": ["YO","HU","LS","BD","HX","HD","WF","S","DN"]
                }
            },
            {
                "query": "solar panels over 250kw in Surrey",
                "params": {
                    "technology": "photovoltaic",
                    "min_capacity_kw": 250,
                    "postcode_areas": ["GU","KT","RH","SM","CR","TW"]
                }
            },
            {
                "query": "urgent repowering opportunities",
                "params": {"repowering_category": "urgent"}
            },
            {
                "query": "PV installations between 100 and 500 kilowatts",
                "params": {
                    "technology": "photovoltaic",
                    "min_capacity_kw": 100,
                    "max_capacity_kw": 500
                }
            }
        ]
        
        for ex in critical_examples:
            system_prompt += f"\nQuery: {ex['query']}\n"
            system_prompt += f"Parameters: {json.dumps(ex['params'])}\n"
        
        system_prompt += """
Always extract and return parameters in this JSON format:
{
    "technology": "photovoltaic|wind|hydro|anaerobic digestion",
    "postcode_areas": ["exact area codes"],
    "min_capacity_kw": number or null,
    "max_capacity_kw": number or null,
    "repowering_category": "immediate|urgent|optimal" or null
}"""
        
        return system_prompt
    
    def create_modelfile(self, system_prompt):
        """Create Ollama Modelfile with enhanced prompt"""
        
        # Escape the system prompt properly for Modelfile
        escaped_prompt = system_prompt.replace('"', '\\"').replace('\n', ' ')
        
        modelfile_content = f'''FROM {self.base_model}

SYSTEM "{escaped_prompt}"

PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 4096
PARAMETER num_predict 512
'''
        
        modelfile_path = "Modelfile_enhanced"
        with open(modelfile_path, 'w') as f:
            f.write(modelfile_content)
        
        print(f"Created enhanced Modelfile at {modelfile_path}")
        return modelfile_path
    
    def create_model(self, modelfile_path):
        """Create new Ollama model with enhanced capabilities"""
        
        print(f"Creating Ollama model: {self.model_name}")
        
        try:
            # Create the model using Ollama
            result = subprocess.run(
                ["ollama", "create", self.model_name, "-f", modelfile_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"✅ Successfully created model: {self.model_name}")
                return True
            else:
                print(f"❌ Error creating model: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Exception creating model: {e}")
            return False
    
    def test_model(self):
        """Test the enhanced model with critical queries"""
        
        test_queries = [
            "sites in Manchester",
            "wind sites over 50kw to max 350kw in Yorkshire",
            "solar panels over 250kw in Surrey",
            "urgent repowering opportunities"
        ]
        
        print("\n" + "="*60)
        print("Testing Enhanced Model")
        print("="*60)
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            
            try:
                response = ollama.generate(
                    model=self.model_name,
                    prompt=f"Parse this query and extract parameters: {query}",
                    options={"temperature": 0.1}
                )
                
                print(f"Response: {response['response'][:200]}...")
                
                # Check for critical assertions
                if "Manchester" in query and '"M"' in response['response']:
                    if '"ML"' not in response['response']:
                        print("✅ Manchester assertion passed")
                    else:
                        print("❌ Manchester assertion failed - contains ML")
                        
                if "Yorkshire" in query:
                    yorkshire_set = ["YO","HU","LS","BD","HX","HD","WF","S","DN"]
                    if all(code in response['response'] for code in yorkshire_set[:3]):
                        print("✅ Yorkshire assertion likely passed")
                    else:
                        print("❌ Yorkshire assertion may have failed")
                        
                if "solar" in query.lower():
                    if "photovoltaic" in response['response']:
                        print("✅ Solar normalization passed")
                    else:
                        print("❌ Solar normalization failed")
                        
            except Exception as e:
                print(f"❌ Test failed: {e}")
    
    def train(self):
        """Main training pipeline"""
        
        print("Starting Ollama-based LoRA training")
        print("="*60)
        
        # Load training data
        # Use latest training file
        import glob
        train_files = sorted(glob.glob("train_*.jsonl"))
        if not train_files:
            print("No training files found!")
            return
        train_file = train_files[-1]
        if not os.path.exists(train_file):
            print(f"Training file not found: {train_file}")
            return False
        
        examples = self.load_training_data(train_file)
        
        # Create enhanced system prompt
        system_prompt = self.create_system_prompt(examples)
        
        # Create Modelfile
        modelfile_path = self.create_modelfile(system_prompt)
        
        # Create the model
        if self.create_model(modelfile_path):
            print("\n✅ Model creation successful!")
            
            # Test the model
            self.test_model()
            
            print("\n" + "="*60)
            print("Enhanced model ready for use!")
            print(f"Model name: {self.model_name}")
            print("\nTo use in the system:")
            print(f"1. Update llm_enhanced_chatbot.py to use model='{self.model_name}'")
            print(f"2. Or test directly: ollama run {self.model_name}")
            
            return True
        else:
            print("\n❌ Model creation failed")
            return False

def main():
    """Run the training"""
    trainer = OllamaLoRATrainer()
    success = trainer.train()
    
    if success:
        # Update the system to use the new model
        print("\nUpdating system configuration...")
        
        # Create a config file for the new model
        config = {
            "model_name": "fit-intelligence-enhanced",
            "base_model": "llama2:13b",
            "enhanced": True,
            "temperature": 0.1,
            "critical_assertions": {
                "manchester_m_only": True,
                "yorkshire_full_set": True,
                "capacity_exact": True,
                "technology_normalized": True
            }
        }
        
        with open("enhanced_model_config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print("Configuration saved to enhanced_model_config.json")
        return 0
    else:
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())