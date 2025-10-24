#!/usr/bin/env python3
"""
Direct GPT-OSS FIT Model - No thinking, just JSON
"""

import json
import subprocess

def create_direct_model():
    """Create a direct-response GPT-OSS model"""
    
    print("Creating Direct GPT-OSS FIT Model...")
    
    # Simple, direct system prompt
    system_prompt = """Parse UK renewable energy queries to JSON filters.

Technology: Wind, Photovoltaic, Hydro, Anaerobic digestion, Micro CHP
Berkshire: ["RG","SL"]
Yorkshire: ["YO","HU","DN","HD","WF","LS","BD"]

Examples:
wind sites over 100kw in berkshire -> {"technology":"Wind","capacity_min_kw":100,"postcode_patterns":["RG","SL"]}
solar farms in Yorkshire -> {"technology":"Photovoltaic","capacity_min_kw":500,"postcode_patterns":["YO","HU","DN","HD","WF","LS","BD"]}
fit id 1585 -> {"query_type":"fit_rate_lookup","fit_id":"1585"}

Return ONLY JSON. No thinking. No explanation."""
    
    # Create Modelfile
    with open("Modelfile_direct", 'w') as f:
        f.write(f"""FROM gpt-oss-fit:latest

SYSTEM '''{system_prompt}'''

PARAMETER temperature 0.1
PARAMETER top_p 0.9
""")
    
    # Create model
    result = subprocess.run(
        ["ollama", "create", "gpt-oss-fit-direct", "-f", "Modelfile_direct"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Model created")
        return True
    return False

def test_model():
    """Test the direct model"""
    
    query = "wind sites over 100kw in berkshire"
    print(f"\nTesting: {query}")
    
    result = subprocess.run(
        ["ollama", "run", "gpt-oss-fit-direct", query],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print(f"Response: {result.stdout}")
    
    try:
        # Try to parse the entire response as JSON first
        parsed = json.loads(result.stdout.strip())
        print(f"✅ Valid JSON: {json.dumps(parsed, indent=2)}")
        
        if (parsed.get("technology") == "Wind" and 
            parsed.get("capacity_min_kw") == 100 and
            "RG" in parsed.get("postcode_patterns", [])):
            print("✅✅✅ CORRECT PARSING!")
    except:
        # Try to find JSON in response
        import re
        json_match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                print(f"✅ Found JSON: {json.dumps(parsed, indent=2)}")
            except:
                print("❌ Invalid JSON")
        else:
            print("❌ No JSON found")

if __name__ == "__main__":
    if create_direct_model():
        test_model()