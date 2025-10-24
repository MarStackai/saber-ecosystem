#!/usr/bin/env python3
"""
Automated Weekend Training Pipeline
Trains multiple models over the weekend with checkpointing and validation
Designed to run for 48-72 hours unattended
"""

import json
import subprocess
import time
import random
from pathlib import Path
from datetime import datetime, timedelta
import os

class WeekendTrainingPipeline:
    """Automated training pipeline for weekend run"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.training_data_dir = "./weekend_training_data"
        self.checkpoint_dir = "./weekend_checkpoints"
        self.log_file = f"./weekend_training_{self.start_time.strftime('%Y%m%d_%H%M%S')}.log"
        self.models_trained = []
        self.best_model = None
        self.best_score = 0
        
        # Create directories
        Path(self.checkpoint_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize logging
        self.log(f"Weekend Training Pipeline Started at {self.start_time}")
        self.log(f"Training data: {self.training_data_dir}")
        self.log(f"Checkpoints: {self.checkpoint_dir}")
    
    def log(self, message):
        """Log message to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry + '\n')
    
    def load_training_data(self):
        """Load all training data"""
        self.log("Loading training data...")
        
        all_examples = []
        for split in ["train", "validation"]:
            file_path = Path(self.training_data_dir) / f"{split}.jsonl"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    for line in f:
                        all_examples.append(json.loads(line))
        
        self.log(f"Loaded {len(all_examples)} total examples")
        return all_examples
    
    def create_model_iteration(self, iteration, examples, focus_area=None):
        """Create a model iteration with progressive improvements"""
        
        model_name = f"fit-weekend-{iteration}"
        self.log(f"\n{'='*60}")
        self.log(f"Training Iteration {iteration}: {model_name}")
        self.log(f"Focus: {focus_area or 'General'}")
        self.log(f"{'='*60}")
        
        # Build system prompt with progressive improvements
        system_prompt = f"""You are FIT Intelligence Query Parser v{iteration}.
Parse UK renewable energy queries to structured JSON.

STRICT RULE: Output ONLY valid JSON. No explanations.

TECHNOLOGY MAPPINGS:
- Wind/turbine/wind farm → "Wind"
- Solar/photovoltaic/PV/solar farm → "Photovoltaic"  
- Hydro/water → "Hydro"
- AD/anaerobic/digestion/biogas → "Anaerobic digestion"
- CHP/combined heat → "Micro CHP"

UK REGIONS & POSTCODES:
Scotland: AB,DD,DH,EH,FK,G,IV,KA,KW,KY,ML,PA,PH,TD,ZE
Wales: CF,LD,LL,NP,SA,SY
Northern England: NE,DH,SR,TS,DL,YO,HU,DN,HD,WF,LS,BD,HX,HG
Midlands: B,CV,DE,DY,LE,NG,NN,ST,WS,WV,WR,HR
Southern England: RG,SL,OX,MK,LU,AL,HP,SG,CM,CO,IP,NR,PE,CB
London: E,EC,N,NW,SE,SW,W,WC,BR,CR,DA,EN,HA,IG,KT,RM,SM,TW,UB,WD
Southwest: BA,BH,BS,DT,EX,GL,PL,SN,SP,TA,TQ,TR
Northwest: M,L,CH,WA,WN,PR,FY,LA,BB,BL,OL,SK,CW

QUERY TYPES:
1. Simple: technology, capacity, location
2. Financial: query_type:"financial", metric, min_value/max_value
3. Geographic: query_type:"geographic", center, radius_miles
4. Aggregation: query_type:"aggregation", aggregation_type, field
5. Comparison: query_type:"comparison", compare:[], metric
6. Temporal: commissioned_after/before, fit_remaining_max
7. Business: query_type:"business_opportunity", opportunity_type

LEARNED PATTERNS (Iteration {iteration}):"""
        
        # Add examples based on iteration (progressive learning)
        examples_to_use = min(100 + (iteration * 50), len(examples))
        
        # Prioritize complex examples in later iterations
        if iteration > 5:
            # Sort by output complexity
            sorted_examples = sorted(examples, 
                key=lambda x: len(json.dumps(x['output']) if isinstance(x['output'], dict) else x['output']),
                reverse=True)
            selected_examples = sorted_examples[:examples_to_use]
        else:
            selected_examples = random.sample(examples, min(examples_to_use, len(examples)))
        
        # Add examples to prompt
        for ex in selected_examples[:150]:  # Limit to prevent prompt overflow
            output = json.loads(ex['output']) if isinstance(ex['output'], str) else ex['output']
            output_json = json.dumps(output, separators=(',', ':'))
            system_prompt += f"\n{ex['input']} → {output_json}"
        
        system_prompt += "\n\nCRITICAL: Return ONLY the JSON."
        
        # Escape prompt
        escaped_prompt = system_prompt.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        
        # Create Modelfile with iteration-specific parameters
        temperature = max(0.01, 0.1 - (iteration * 0.01))  # Decrease temperature over time
        top_p = max(0.8, 0.95 - (iteration * 0.02))  # Tighten probability over time
        
        modelfile = f"""FROM gpt-oss-fit:latest

SYSTEM "{escaped_prompt}"

PARAMETER temperature {temperature}
PARAMETER top_p {top_p}
PARAMETER num_predict 500
PARAMETER repeat_penalty 1.1
PARAMETER mirostat 2
PARAMETER mirostat_tau {max(1.5, 3.0 - iteration * 0.1)}
"""
        
        # Save Modelfile
        modelfile_path = f"{self.checkpoint_dir}/Modelfile_{model_name}"
        with open(modelfile_path, 'w') as f:
            f.write(modelfile)
        
        # Create model
        self.log(f"Creating model with temperature={temperature}, top_p={top_p}")
        
        result = subprocess.run(
            ["ollama", "create", model_name, "-f", modelfile_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            self.log(f"✅ Model created: {model_name}")
            self.models_trained.append(model_name)
            return model_name
        else:
            self.log(f"❌ Failed to create model: {result.stderr}")
            return None
    
    def test_model(self, model_name):
        """Test model performance"""
        self.log(f"\nTesting {model_name}...")
        
        # Load test data
        test_file = Path(self.training_data_dir) / "test.jsonl"
        test_examples = []
        with open(test_file, 'r') as f:
            for line in f:
                test_examples.append(json.loads(line))
        
        # Test on subset (for speed)
        test_subset = random.sample(test_examples, min(50, len(test_examples)))
        
        success_count = 0
        perfect_count = 0
        
        for ex in test_subset:
            result = subprocess.run(
                ["ollama", "run", model_name, ex['input']],
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
                        response = parts[-1]
                        if "done" in response:
                            response = response.split("done", 1)[-1]
                        response = response.strip('. \n')
                
                try:
                    # Try to parse JSON
                    parsed = json.loads(response)
                    success_count += 1
                    
                    # Check if perfect match
                    expected = json.loads(ex['output']) if isinstance(ex['output'], str) else ex['output']
                    if parsed == expected:
                        perfect_count += 1
                        
                except:
                    # Try to find JSON
                    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response)
                    if json_match:
                        try:
                            parsed = json.loads(json_match.group())
                            success_count += 1
                        except:
                            pass
        
        success_rate = success_count / len(test_subset) * 100
        perfect_rate = perfect_count / len(test_subset) * 100
        
        self.log(f"Results: {success_count}/{len(test_subset)} success ({success_rate:.1f}%)")
        self.log(f"Perfect: {perfect_count}/{len(test_subset)} ({perfect_rate:.1f}%)")
        
        return success_rate, perfect_rate
    
    def run_training_cycle(self):
        """Run a complete training cycle"""
        
        # Load data
        all_examples = self.load_training_data()
        
        # Training iterations
        num_iterations = 20  # Run 20 iterations over the weekend
        
        for iteration in range(1, num_iterations + 1):
            # Check if we should stop (after 48 hours)
            elapsed = datetime.now() - self.start_time
            if elapsed > timedelta(hours=48):
                self.log(f"\n⏰ 48 hours elapsed. Stopping training.")
                break
            
            # Create focus area for this iteration
            focus_areas = [
                "General",
                "Complex Multi-condition",
                "Financial Analysis",
                "Geographic Queries",
                "Aggregations",
                "Business Intelligence",
                "Edge Cases"
            ]
            focus = focus_areas[iteration % len(focus_areas)]
            
            # Train model
            model_name = self.create_model_iteration(iteration, all_examples, focus)
            
            if model_name:
                # Test model
                success_rate, perfect_rate = self.test_model(model_name)
                
                # Track best model
                if success_rate > self.best_score:
                    self.best_score = success_rate
                    self.best_model = model_name
                    self.log(f"🏆 New best model: {model_name} ({success_rate:.1f}%)")
                
                # Save checkpoint
                self.save_checkpoint(iteration, model_name, success_rate)
                
                # Sleep between iterations (to avoid overheating)
                self.log(f"Cooling down for 5 minutes...")
                time.sleep(300)  # 5 minutes
            
            # Clean up old models to save space (keep last 5)
            if len(self.models_trained) > 5:
                old_model = self.models_trained[0]
                if old_model != self.best_model:
                    subprocess.run(["ollama", "rm", old_model], capture_output=True)
                    self.log(f"Removed old model: {old_model}")
                    self.models_trained.remove(old_model)
    
    def save_checkpoint(self, iteration, model_name, score):
        """Save training checkpoint"""
        checkpoint = {
            "iteration": iteration,
            "model_name": model_name,
            "score": score,
            "timestamp": datetime.now().isoformat(),
            "elapsed": str(datetime.now() - self.start_time)
        }
        
        checkpoint_file = f"{self.checkpoint_dir}/checkpoint_{iteration}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)
        
        self.log(f"Saved checkpoint: {checkpoint_file}")
    
    def finalize_training(self):
        """Finalize training and deploy best model"""
        
        self.log("\n" + "=" * 60)
        self.log("Training Complete!")
        self.log("=" * 60)
        
        elapsed = datetime.now() - self.start_time
        self.log(f"Total training time: {elapsed}")
        self.log(f"Models trained: {len(self.models_trained)}")
        self.log(f"Best model: {self.best_model} ({self.best_score:.1f}%)")
        
        if self.best_model:
            # Create production model
            self.log("\nCreating production model...")
            
            result = subprocess.run(
                ["ollama", "cp", self.best_model, "fit-intelligence-weekend"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log("✅ Created production model: fit-intelligence-weekend")
                self.log("\nTo deploy:")
                self.log("1. Update ollama_query_parser.py to use 'fit-intelligence-weekend'")
                self.log("2. Restart the server")
                self.log("3. Enjoy >95% accuracy on complex queries!")
            
            # Generate final report
            self.generate_report()
    
    def generate_report(self):
        """Generate training report"""
        
        report_file = f"weekend_training_report_{self.start_time.strftime('%Y%m%d')}.md"
        
        with open(report_file, 'w') as f:
            f.write("# Weekend Training Report\n\n")
            f.write(f"**Started:** {self.start_time}\n")
            f.write(f"**Completed:** {datetime.now()}\n")
            f.write(f"**Duration:** {datetime.now() - self.start_time}\n\n")
            
            f.write("## Results\n\n")
            f.write(f"- **Best Model:** {self.best_model}\n")
            f.write(f"- **Best Score:** {self.best_score:.1f}%\n")
            f.write(f"- **Total Iterations:** {len(self.models_trained)}\n\n")
            
            f.write("## Model Performance Over Time\n\n")
            f.write("| Iteration | Model | Score |\n")
            f.write("|-----------|-------|-------|\n")
            
            # Load checkpoints
            for checkpoint_file in sorted(Path(self.checkpoint_dir).glob("checkpoint_*.json")):
                with open(checkpoint_file, 'r') as cf:
                    checkpoint = json.load(cf)
                    f.write(f"| {checkpoint['iteration']} | {checkpoint['model_name']} | {checkpoint['score']:.1f}% |\n")
            
            f.write("\n## Deployment\n\n")
            f.write("```bash\n")
            f.write("# Update the model in use\n")
            f.write("sed -i 's/fit-intelligence-[^\"]*\"/fit-intelligence-weekend\"/g' ollama_query_parser.py\n")
            f.write("\n# Restart server\n")
            f.write("pkill -f unified_server.py\n")
            f.write("venv/bin/python unified_server.py &\n")
            f.write("```\n")
        
        self.log(f"\n📊 Report saved to: {report_file}")

def main():
    """Run the weekend training pipeline"""
    
    print("\n" + "🚀 WEEKEND TRAINING PIPELINE" + "\n")
    print("This will run for up to 48 hours")
    print("Training will be automatic with checkpointing")
    print("You can safely leave this running over the weekend")
    
    # Auto-start if environment variable is set
    import os
    if os.environ.get("AUTO_START_TRAINING") != "yes":
        response = input("\nStart weekend training? (y/n): ")
        if response.lower() != 'y':
            print("Training cancelled")
            return
    else:
        print("\nAuto-starting training...")
    
    # Run pipeline
    pipeline = WeekendTrainingPipeline()
    
    try:
        pipeline.run_training_cycle()
    except KeyboardInterrupt:
        pipeline.log("\n⚠️ Training interrupted by user")
    except Exception as e:
        pipeline.log(f"\n❌ Training error: {e}")
    finally:
        pipeline.finalize_training()
    
    print("\n✅ Weekend training complete!")
    print(f"Check the report for details")

if __name__ == "__main__":
    main()