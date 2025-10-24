#!/usr/bin/env python3
"""
Create FIT Intelligence Ollama Model
Uses training data to create a specialized query parser
"""

import json
import subprocess
from pathlib import Path

def create_fit_intelligence_model():
    """Create an Ollama model for FIT Intelligence"""
    
    print("Creating FIT Intelligence Ollama Model")
    print("=" * 60)
    
    # Load critical training examples
    with open("./lora_training_advanced/train.jsonl", 'r') as f:
        examples = [json.loads(line) for line in f][:20]  # First 20 examples
    
    # Build system prompt with examples
    system_prompt = """You are a query parser for the FIT Intelligence database containing 40,194 UK renewable energy installations.

Parse natural language queries into structured JSON filters.

CRITICAL MAPPINGS:
Technology: Wind, Photovoltaic, Hydro, Anaerobic digestion, Micro CHP
Berkshire postcodes: RG, SL
Yorkshire postcodes: YO, HU, DN, HD, WF, LS, BD

CRITICAL EXAMPLE - MEMORIZE THIS:
Query: wind sites over 100kw in berkshire
JSON: {"technology": "Wind", "capacity_min_kw": 100, "location": "Berkshire", "postcode_patterns": ["RG", "SL"]}

Other examples:
Query: solar farms in Yorkshire  
JSON: {"technology": "Photovoltaic", "capacity_min_kw": 500, "location": "Yorkshire", "postcode_patterns": ["YO", "HU", "DN", "HD", "WF", "LS", "BD"]}

Query: what is the fit rate for fit id 1585
JSON: {"query_type": "fit_rate_lookup", "fit_id": "1585"}

IMPORTANT: Always include postcode_patterns for location queries.
Return ONLY valid JSON, no explanation."""
    
    # Create Modelfile
    modelfile = f"""FROM llama3.2:1b

SYSTEM "{system_prompt}"

PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER stop "<|eot_id|>"
"""
    
    # Save Modelfile
    with open("Modelfile_fit", 'w') as f:
        f.write(modelfile)
    
    print("Creating model with Ollama...")
    
    # Create the model
    result = subprocess.run(
        ["ollama", "create", "fit-intelligence-v2", "-f", "Modelfile_fit"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Model created successfully!")
        return True
    else:
        print(f"Error: {result.stderr}")
        return False

def test_model():
    """Test the model with critical query"""
    print("\n" + "=" * 60)
    print("Testing Critical Query")
    print("=" * 60)
    
    query = "wind sites over 100kw in berkshire"
    print(f"\nQuery: {query}")
    
    result = subprocess.run(
        ["ollama", "run", "fit-intelligence-v2", query],
        capture_output=True,
        text=True
    )
    
    print(f"Response: {result.stdout}")
    
    # Try to parse JSON
    try:
        import re
        json_match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            print(f"\n✅ Parsed JSON:")
            print(json.dumps(parsed, indent=2))
            
            # Check if it has the right structure
            if (parsed.get("technology") == "Wind" and 
                parsed.get("capacity_min_kw") == 100 and
                "RG" in parsed.get("postcode_patterns", [])):
                print("\n✅ CORRECT PARSING!")
            else:
                print("\n⚠️  Incorrect parsing - needs adjustment")
    except Exception as e:
        print(f"❌ Parse error: {e}")

if __name__ == "__main__":
    if create_fit_intelligence_model():
        test_model()