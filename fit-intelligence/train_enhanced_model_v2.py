#!/usr/bin/env python3
"""
Train Enhanced Model v2
Optimized for capacity+location queries with nearest neighbor understanding
"""

import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

def create_enhanced_model(iteration=1):
    """Create an enhanced model with improved training"""
    
    model_name = f"fit-intelligence-v2-{iteration}"
    training_dir = Path("enhanced_training_v2")
    
    print(f"\n{'='*60}")
    print(f"Training Enhanced Model v2: {model_name}")
    print(f"{'='*60}")
    
    # Load training examples
    train_examples = []
    with open(training_dir / "train.jsonl", 'r') as f:
        for line in f:
            train_examples.append(json.loads(line))
    
    print(f"Loaded {len(train_examples)} training examples")
    
    # Build comprehensive system prompt
    system_prompt = f"""You are FIT Intelligence Query Parser v2.
Enhanced with location-aware capacity matching and nearest neighbor understanding.

CRITICAL: Output ONLY valid JSON. No explanations or thinking.

CORE PATTERNS:
1. Capacity + Location: "330kw in ryedale" → {{"capacity":330,"location":"Ryedale","postcode_patterns":["YO17","YO18"]}}
2. Technology + Capacity + Location: "wind 500kw in scotland" → {{"technology":"Wind","capacity":500,"location":"Scotland","postcode_patterns":["AB","DD","EH"]}}
3. Ranges: "100-500kw in yorkshire" → {{"capacity_min":100,"capacity_max":500,"location":"Yorkshire","postcode_patterns":["YO","HU","DN"]}}
4. Over/Under: "over 100kw in berkshire" → {{"capacity_min":100,"location":"Berkshire","postcode_patterns":["RG","SL"]}}

TECHNOLOGY MAPPINGS:
- wind/turbine/wind farm → "Wind"
- solar/photovoltaic/pv/solar farm → "Photovoltaic"
- hydro/water → "Hydro"
- ad/anaerobic/digestion/biogas → "Anaerobic digestion"
- chp/combined heat → "Micro CHP"

UK LOCATION MAPPINGS:
- Always capitalize locations properly
- Include relevant postcode_patterns when location is specified
- Common locations: Yorkshire, Ryedale, Berkshire, Scotland, Wales, Cornwall, Devon, etc.

CAPACITY HANDLING:
- Specific capacity: "330kw" → "capacity":330
- Ranges: "100-500kw" → "capacity_min":100,"capacity_max":500
- Over: "over 100kw" → "capacity_min":100
- Under: "under 500kw" → "capacity_max":500
- MW conversion: "1.5mw" → 1500 (in kW)

QUERY TYPES:
- Simple search: Default, no query_type needed
- Geographic: "within X miles of Y" → "query_type":"geographic","geo_center":"Y","geo_radius":X
- Financial: "fit rate over X" → "query_type":"financial","fit_rate_min":X
- Aggregation: "count/total/average" → "query_type":"aggregation","aggregation_type":"count"
- Opportunity: "best roi" → "query_type":"opportunity","opportunity_type":"roi"

EXAMPLES:"""
    
    # Add training examples to prompt
    for example in train_examples[:200]:  # Limit to prevent prompt overflow
        system_prompt += f"\n{example['input']} → {example['output']}"
    
    system_prompt += "\n\nREMEMBER: Output ONLY the JSON, nothing else."
    
    # Escape the prompt
    escaped_prompt = system_prompt.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    
    # Create Modelfile with optimized parameters
    modelfile = f"""FROM gpt-oss-fit:latest

SYSTEM "{escaped_prompt}"

PARAMETER temperature 0.05
PARAMETER top_p 0.9
PARAMETER num_predict 500
PARAMETER repeat_penalty 1.1
PARAMETER mirostat 2
PARAMETER mirostat_tau 2.0
PARAMETER stop "\\n\\n"
PARAMETER stop "Explanation:"
PARAMETER stop "Note:"
"""
    
    # Save Modelfile
    modelfile_path = f"Modelfile_{model_name}"
    with open(modelfile_path, 'w') as f:
        f.write(modelfile)
    
    print(f"Created Modelfile: {modelfile_path}")
    
    # Create the model
    print(f"Creating Ollama model: {model_name}")
    result = subprocess.run(
        ["ollama", "create", model_name, "-f", modelfile_path],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ Model created successfully: {model_name}")
        return model_name
    else:
        print(f"❌ Failed to create model: {result.stderr}")
        return None

def test_model(model_name):
    """Test the model with various queries"""
    
    test_queries = [
        "330kw in ryedale",
        "wind sites over 100kw in berkshire",
        "250kw wind turbine in scotland",
        "solar farms between 100 and 500kw in devon",
        "all sites in yorkshire",
        "hydro over 200kw in wales",
        "329kw in ryedale",
        "wind 330kw in yorkshire"
    ]
    
    print(f"\n{'='*60}")
    print(f"Testing Model: {model_name}")
    print(f"{'='*60}")
    
    success_count = 0
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        
        result = subprocess.run(
            ["ollama", "run", model_name, query],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            response = result.stdout.strip()
            # Clean response
            if "thinking" in response.lower():
                response = response.split("done thinking.")[-1].strip()
            
            # Remove any non-JSON content
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response)
            if json_match:
                response = json_match.group()
            
            print(f"Response: {response}")
            
            try:
                parsed = json.loads(response)
                print("✅ Valid JSON")
                
                # Check for expected fields
                if "ryedale" in query.lower() and parsed.get("location", "").lower() == "ryedale":
                    print("✅ Location correctly extracted")
                if "330" in query and parsed.get("capacity") == 330:
                    print("✅ Capacity correctly extracted")
                if "wind" in query.lower() and parsed.get("technology") == "Wind":
                    print("✅ Technology correctly extracted")
                    
                success_count += 1
            except json.JSONDecodeError:
                print("❌ Invalid JSON")
        else:
            print(f"❌ Error: {result.stderr}")
    
    success_rate = success_count / len(test_queries) * 100
    print(f"\n{'='*60}")
    print(f"Test Results: {success_count}/{len(test_queries)} success ({success_rate:.1f}%)")
    print(f"{'='*60}")
    
    return success_rate

def main():
    """Main training process"""
    
    print("\n🚀 Enhanced Model Training v2")
    print("Focus: Capacity + Location queries with smart matching")
    
    # Train multiple iterations to find best
    best_model = None
    best_score = 0
    
    for iteration in range(1, 4):  # Train 3 iterations
        model_name = create_enhanced_model(iteration)
        
        if model_name:
            score = test_model(model_name)
            
            if score > best_score:
                best_score = score
                best_model = model_name
                print(f"🏆 New best model: {model_name} ({score:.1f}%)")
            
            time.sleep(5)  # Cool down between iterations
    
    if best_model:
        print(f"\n✅ Training Complete!")
        print(f"Best model: {best_model} ({best_score:.1f}% success)")
        
        # Create production version
        print(f"\nCreating production model...")
        result = subprocess.run(
            ["ollama", "cp", best_model, "fit-intelligence-enhanced"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Created production model: fit-intelligence-enhanced")
            print("\nTo deploy:")
            print("1. Update ollama_query_parser.py to use 'fit-intelligence-enhanced'")
            print("2. Restart the server")
            print("3. Test with complex capacity+location queries!")
        else:
            print(f"❌ Failed to create production model: {result.stderr}")
    else:
        print("❌ No successful models created")

if __name__ == "__main__":
    main()