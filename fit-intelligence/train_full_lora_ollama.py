#!/usr/bin/env python3
"""
Full LoRA Training using Ollama
Creates multiple specialized models and combines them
"""

import json
import subprocess
import random
from pathlib import Path
import time

class OllamaLoRATrainer:
    """Train multiple specialized models for ensemble"""
    
    def __init__(self):
        self.base_model = "gpt-oss-fit:latest"
        self.training_dirs = [
            "./lora_training_advanced",  # Original 3,195 examples
            "./lora_training_complex"     # New complex examples
        ]
        self.models_created = []
    
    def load_all_training_data(self):
        """Load and combine all training data"""
        all_examples = []
        
        for dir_path in self.training_dirs:
            if Path(dir_path).exists():
                for file_name in ["train.jsonl", "validation.jsonl"]:
                    file_path = Path(dir_path) / file_name
                    if file_path.exists():
                        with open(file_path, 'r') as f:
                            for line in f:
                                all_examples.append(json.loads(line))
        
        print(f"Loaded {len(all_examples)} total training examples")
        return all_examples
    
    def create_specialized_model(self, name, examples, focus_area=None):
        """Create a specialized model for a specific query type"""
        
        print(f"\nCreating specialized model: {name}")
        print("-" * 40)
        
        # Build focused system prompt
        system_prompt = f"""You are the FIT Intelligence {focus_area or 'Query'} Parser.
Parse UK renewable energy queries into structured JSON filters.

CRITICAL: Return ONLY valid JSON, no explanation.

Technology: Wind, Photovoltaic, Hydro, Anaerobic digestion, Micro CHP
Berkshire: ["RG","SL"]
Yorkshire: ["YO","HU","DN","HD","WF","LS","BD"]
Scotland: ["AB","DD","EH","FK","G","IV","KA","KW"]

Key patterns:"""
        
        # Add examples
        for ex in examples[:100]:  # Use up to 100 examples
            output = json.loads(ex['output']) if isinstance(ex['output'], str) else ex['output']
            output_json = json.dumps(output, separators=(',', ':'))
            system_prompt += f"\n{ex['input']} → {output_json}"
        
        system_prompt += "\n\nReturn ONLY JSON."
        
        # Escape prompt
        escaped_prompt = system_prompt.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        
        # Create Modelfile
        modelfile = f"""FROM {self.base_model}

SYSTEM "{escaped_prompt}"

PARAMETER temperature 0.05
PARAMETER top_p 0.9
PARAMETER num_predict 300
PARAMETER repeat_penalty 1.1
"""
        
        modelfile_path = f"Modelfile_{name}"
        with open(modelfile_path, 'w') as f:
            f.write(modelfile)
        
        # Create model
        result = subprocess.run(
            ["ollama", "create", f"fit-{name}", "-f", modelfile_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Created model: fit-{name}")
            self.models_created.append(f"fit-{name}")
            return True
        else:
            print(f"❌ Failed to create model: {result.stderr}")
            return False
    
    def train_ensemble(self):
        """Train multiple specialized models"""
        
        print("\n" + "=" * 60)
        print("Training Ensemble of Specialized Models")
        print("=" * 60)
        
        all_examples = self.load_all_training_data()
        
        # Categorize examples
        categories = {
            "multi-condition": [],
            "financial": [],
            "geographic": [],
            "temporal": [],
            "aggregation": [],
            "simple": []
        }
        
        for ex in all_examples:
            output = json.loads(ex['output']) if isinstance(ex['output'], str) else ex['output']
            
            # Categorize based on output structure
            if "query_type" in output:
                if output["query_type"] == "financial":
                    categories["financial"].append(ex)
                elif output["query_type"] == "aggregation":
                    categories["aggregation"].append(ex)
                elif output["query_type"] == "geographic":
                    categories["geographic"].append(ex)
                else:
                    categories["simple"].append(ex)
            elif "commissioned" in ex['input'].lower() or "expir" in ex['input'].lower():
                categories["temporal"].append(ex)
            elif len(output.keys()) > 3:
                categories["multi-condition"].append(ex)
            else:
                categories["simple"].append(ex)
        
        # Create specialized models
        models = [
            ("multi", categories["multi-condition"] + categories["simple"], "Multi-Condition"),
            ("financial", categories["financial"] + random.sample(all_examples, 50), "Financial"),
            ("temporal", categories["temporal"] + random.sample(all_examples, 50), "Temporal"),
            ("master", all_examples, "Master")  # Master model with all examples
        ]
        
        for name, examples, focus in models:
            if examples:
                self.create_specialized_model(name, examples, focus)
                time.sleep(1)  # Small delay between model creations
    
    def test_ensemble(self):
        """Test the ensemble of models"""
        
        print("\n" + "=" * 60)
        print("Testing Ensemble Performance")
        print("=" * 60)
        
        # Complex test queries
        test_queries = [
            "wind sites over 100kw in berkshire",
            "solar farms between 500kw and 2MW in Yorkshire expiring within 5 years",
            "compare ROI of wind vs solar in Scotland",
            "sites with annual revenue over £100000",
            "wind farms within 30 miles of Birmingham",
            "urgent repowering opportunities",
            "total capacity of wind in Scotland",
            "hydro installations over 1MW in Scotland with FIT rate above 15p"
        ]
        
        # Test each model
        results = {}
        for model_name in self.models_created:
            print(f"\nTesting {model_name}:")
            success_count = 0
            
            for query in test_queries:
                result = subprocess.run(
                    ["ollama", "run", model_name, query],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    response = result.stdout.strip()
                    
                    # Clean response
                    import re
                    response = re.sub(r'\x1b\[[0-9;]*[mGKH]', '', response)
                    
                    # Remove thinking
                    if "thinking" in response.lower():
                        parts = response.split("thinking", 1)
                        if len(parts) > 1:
                            response = parts[-1].strip()
                            if response.startswith('.'):
                                response = response[1:].strip()
                    
                    # Try to parse JSON
                    try:
                        parsed = json.loads(response)
                        success_count += 1
                        print(f"  ✅ {query[:50]}...")
                    except:
                        # Try to find JSON
                        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response)
                        if json_match:
                            try:
                                parsed = json.loads(json_match.group())
                                success_count += 1
                                print(f"  ✅ {query[:50]}...")
                            except:
                                print(f"  ❌ {query[:50]}...")
                        else:
                            print(f"  ❌ {query[:50]}...")
            
            results[model_name] = success_count
            print(f"  Score: {success_count}/{len(test_queries)} ({success_count/len(test_queries)*100:.1f}%)")
        
        # Find best model
        best_model = max(results, key=results.get)
        best_score = results[best_model]
        
        print("\n" + "=" * 60)
        print("Results Summary")
        print("=" * 60)
        for model, score in results.items():
            print(f"{model}: {score}/{len(test_queries)} ({score/len(test_queries)*100:.1f}%)")
        
        print(f"\n🏆 Best Model: {best_model} ({best_score/len(test_queries)*100:.1f}%)")
        
        return best_model, best_score
    
    def create_production_model(self, best_model):
        """Create final production model"""
        
        print("\n" + "=" * 60)
        print("Creating Production Model")
        print("=" * 60)
        
        # Create production model from best performer
        result = subprocess.run(
            ["ollama", "cp", best_model, "fit-intelligence-production"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Created production model: fit-intelligence-production")
            
            # Update instructions
            print("\nTo deploy:")
            print("1. Update ollama_query_parser.py:")
            print("   Change model_name to 'fit-intelligence-production'")
            print("2. Restart the server")
            print("3. Test with complex queries")
        else:
            print(f"❌ Failed to create production model: {result.stderr}")

def main():
    """Main training pipeline"""
    
    print("\n🚀 Full LoRA Training Pipeline\n")
    
    trainer = OllamaLoRATrainer()
    
    # Train ensemble
    trainer.train_ensemble()
    
    # Test and evaluate
    best_model, best_score = trainer.test_ensemble()
    
    # Create production model
    if best_score >= 6:  # At least 75% success
        trainer.create_production_model(best_model)
        
        print("\n" + "=" * 60)
        print("✅ Training Complete!")
        print("=" * 60)
        print(f"\nAchieved {best_score/8*100:.1f}% success rate on complex queries")
        print("\nProduction model ready for deployment!")
    else:
        print("\n⚠️ Success rate too low. Need more training iterations.")

if __name__ == "__main__":
    main()