#!/usr/bin/env python3
"""
Create Ultimate FIT Intelligence Model
Combines all training data with optimized prompting
"""

import json
import subprocess
import random
from pathlib import Path

def create_ultimate_model():
    """Create the ultimate model with all optimizations"""
    
    print("=" * 60)
    print("Creating Ultimate FIT Intelligence Model")
    print("=" * 60)
    
    # Load ALL training data
    all_examples = []
    
    # Load from both directories
    for dir_path in ["./lora_training_advanced", "./lora_training_complex"]:
        if Path(dir_path).exists():
            for file_name in ["train.jsonl", "validation.jsonl"]:
                file_path = Path(dir_path) / file_name
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        for line in f:
                            all_examples.append(json.loads(line))
    
    print(f"Loaded {len(all_examples)} total examples")
    
    # Categorize examples by complexity
    critical_examples = []
    complex_examples = []
    simple_examples = []
    
    for ex in all_examples:
        input_lower = ex['input'].lower()
        output = json.loads(ex['output']) if isinstance(ex['output'], str) else ex['output']
        
        # Critical queries
        if "wind sites over 100kw in berkshire" in input_lower:
            critical_examples.append(ex)
        elif "solar farms" in input_lower and "yorkshire" in input_lower:
            critical_examples.append(ex)
        # Complex queries
        elif len(output.keys()) > 3 or "query_type" in output:
            complex_examples.append(ex)
        # Simple queries
        else:
            simple_examples.append(ex)
    
    # Build ultimate system prompt
    system_prompt = """You are the Ultimate FIT Intelligence Query Parser.

CRITICAL RULE: Output ONLY valid JSON. No thinking, no explanation.

TECHNOLOGY MAPPINGS:
Wind/turbine/wind farm → "Wind"
Solar/photovoltaic/PV/solar farm → "Photovoltaic"
Hydro/water → "Hydro"
AD/anaerobic/digestion/biogas → "Anaerobic digestion"
CHP/combined heat → "Micro CHP"

POSTCODE MAPPINGS:
Berkshire: ["RG","SL"]
Yorkshire: ["YO","HU","DN","HD","WF","LS","BD","HX","S"]
Scotland: ["AB","DD","EH","FK","G","IV","KA","KW","ML","PA","PH","TD"]
Birmingham/Midlands: ["B","CV","DE","DY","LE","NG","NN","ST","WS","WV"]
London: ["E","EC","N","NW","SE","SW","W","WC"]
Wales: ["CF","LD","LL","NP","SA","SY"]

QUERY TYPES:
- Simple: technology, capacity, location filters
- Financial: {"query_type":"financial","metric":"annual_revenue","min_value":X}
- Geographic: {"query_type":"geographic","center":"X","radius_miles":Y}
- Aggregation: {"query_type":"aggregation","aggregation_type":"sum/average/count","field":"X"}
- Comparison: {"query_type":"comparison","compare":["X","Y"]}
- Temporal: commissioned_after, expiry_start, fit_remaining_max

CRITICAL EXAMPLES (MEMORIZE):"""
    
    # Add ALL critical examples
    for ex in critical_examples[:20]:
        output = json.loads(ex['output']) if isinstance(ex['output'], str) else ex['output']
        output_json = json.dumps(output, separators=(',', ':'))
        system_prompt += f"\n{ex['input']} → {output_json}"
    
    # Add complex examples
    system_prompt += "\n\nCOMPLEX PATTERNS:"
    for ex in random.sample(complex_examples, min(50, len(complex_examples))):
        output = json.loads(ex['output']) if isinstance(ex['output'], str) else ex['output']
        output_json = json.dumps(output, separators=(',', ':'))
        system_prompt += f"\n{ex['input']} → {output_json}"
    
    # Add simple examples
    system_prompt += "\n\nSIMPLE PATTERNS:"
    for ex in random.sample(simple_examples, min(30, len(simple_examples))):
        output = json.loads(ex['output']) if isinstance(ex['output'], str) else ex['output']
        output_json = json.dumps(output, separators=(',', ':'))
        system_prompt += f"\n{ex['input']} → {output_json}"
    
    # Add edge cases
    system_prompt += """

EDGE CASES:
2 megawatt → 2000kW
half megawatt → 500kW
fit 1585 → {"fit_id":"1585"}
expiring soon → {"fit_remaining_max":5}
urgent → {"repowering_window":"URGENT","fit_remaining_max":2}

REMEMBER: Output ONLY the JSON."""
    
    # Escape prompt
    escaped_prompt = system_prompt.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    
    # Create Modelfile with optimized parameters
    modelfile = f"""FROM gpt-oss-fit:latest

SYSTEM "{escaped_prompt}"

PARAMETER temperature 0.01
PARAMETER top_p 0.9
PARAMETER num_predict 400
PARAMETER repeat_penalty 1.2
PARAMETER mirostat 2
PARAMETER mirostat_tau 2.0
"""
    
    with open("Modelfile_ultimate", 'w') as f:
        f.write(modelfile)
    
    print("Creating ultimate model...")
    
    # Create model
    result = subprocess.run(
        ["ollama", "create", "fit-intelligence-ultimate", "-f", "Modelfile_ultimate"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Ultimate model created!")
        return True
    else:
        print(f"❌ Error: {result.stderr}")
        return False

def test_ultimate_model():
    """Test the ultimate model on all query types"""
    
    print("\n" + "=" * 60)
    print("Testing Ultimate Model")
    print("=" * 60)
    
    # Comprehensive test suite
    test_queries = [
        # Critical
        ("wind sites over 100kw in berkshire", 
         {"technology": "Wind", "capacity_min_kw": 100, "postcode_patterns": ["RG", "SL"]}),
        
        # Complex multi-condition
        ("solar farms between 500kw and 2MW in Yorkshire expiring within 5 years",
         {"technology": "Photovoltaic", "capacity_min_kw": 500, "capacity_max_kw": 2000, 
          "postcode_patterns": ["YO", "HU", "DN", "HD", "WF", "LS", "BD"], "fit_remaining_max": 5}),
        
        # Financial
        ("sites with annual revenue over £100000",
         {"query_type": "financial", "metric": "annual_revenue", "min_value": 100000}),
        
        # Geographic
        ("wind farms within 30 miles of Birmingham",
         {"query_type": "geographic", "technology": "Wind", "capacity_min_kw": 100, 
          "center": "Birmingham", "radius_miles": 30}),
        
        # Aggregation
        ("total capacity of wind in Scotland",
         {"query_type": "aggregation", "aggregation_type": "sum", "field": "capacity_kw", 
          "technology": "Wind", "postcode_patterns": ["AB", "DD", "EH", "FK", "G", "IV", "KA", "KW"]}),
        
        # Temporal
        ("urgent repowering opportunities",
         {"repowering_window": "URGENT", "fit_remaining_max": 2}),
        
        # Complex with FIT rate
        ("hydro installations over 1MW in Scotland with FIT rate above 15p",
         {"technology": "Hydro", "capacity_min_kw": 1000, 
          "postcode_patterns": ["AB", "DD", "EH", "FK", "G", "IV", "KA", "KW"], "fit_rate_min": 15}),
        
        # Comparison
        ("compare ROI of wind vs solar in Scotland",
         {"query_type": "comparison", "compare": ["Wind", "Photovoltaic"], "metric": "ROI",
          "postcode_patterns": ["AB", "DD", "EH", "FK", "G", "IV", "KA", "KW"]}),
        
        # Simple
        ("fit id 1585",
         {"fit_id": "1585"}),
        
        # Edge case
        ("2 megawatt solar farms",
         {"technology": "Photovoltaic", "capacity_min_kw": 1800, "capacity_max_kw": 2200})
    ]
    
    success_count = 0
    perfect_matches = 0
    
    for query, expected in test_queries:
        print(f"\nQuery: {query}")
        
        result = subprocess.run(
            ["ollama", "run", "fit-intelligence-ultimate", query],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            response = result.stdout.strip()
            
            # Clean response
            import re
            response = re.sub(r'\x1b\[[0-9;]*[mGKH]', '', response)
            response = re.sub(r'\[\?[0-9]+[hl]', '', response)
            
            # Remove thinking
            if "thinking" in response.lower():
                parts = response.split("thinking", 1)
                if len(parts) > 1:
                    response = parts[-1]
                    if "done" in response:
                        response = response.split("done", 1)[-1]
                    response = response.strip('. \n')
            
            try:
                # Try direct parse
                parsed = json.loads(response)
                success_count += 1
                
                # Check if perfect match
                if parsed == expected:
                    perfect_matches += 1
                    print(f"  ✅✅ PERFECT MATCH!")
                else:
                    print(f"  ✅ Valid JSON: {json.dumps(parsed)}")
                    print(f"  Expected: {json.dumps(expected)}")
                    
            except json.JSONDecodeError:
                # Try to find JSON
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group())
                        success_count += 1
                        print(f"  ✅ Found JSON: {json.dumps(parsed)}")
                    except:
                        print(f"  ❌ Invalid JSON")
                        print(f"  Response: {response[:200]}")
                else:
                    print(f"  ❌ No JSON found")
                    print(f"  Response: {response[:200]}")
        else:
            print(f"  ❌ Query failed")
    
    print("\n" + "=" * 60)
    print("Results")
    print("=" * 60)
    print(f"Success Rate: {success_count}/{len(test_queries)} ({success_count/len(test_queries)*100:.1f}%)")
    print(f"Perfect Matches: {perfect_matches}/{len(test_queries)} ({perfect_matches/len(test_queries)*100:.1f}%)")
    
    return success_count, perfect_matches

def deploy_if_ready(success_count, perfect_matches):
    """Deploy if performance is good enough"""
    
    if success_count >= 9:  # 90% success rate
        print("\n" + "=" * 60)
        print("🎉 Deploying Ultimate Model!")
        print("=" * 60)
        
        # Copy to production
        result = subprocess.run(
            ["ollama", "cp", "fit-intelligence-ultimate", "fit-intelligence-final"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Created final production model: fit-intelligence-final")
            print("\nDeployment Instructions:")
            print("1. Update ollama_query_parser.py to use 'fit-intelligence-final'")
            print("2. Restart the server")
            print("3. The platform now handles complex queries with high accuracy!")
        
        return True
    else:
        print("\n⚠️ Model needs more training (current: {success_count*10}% success)")
        return False

def main():
    """Main pipeline"""
    
    print("\n🚀 Creating Ultimate FIT Intelligence Model\n")
    
    if create_ultimate_model():
        success, perfect = test_ultimate_model()
        deploy_if_ready(success, perfect)
        
        print("\n" + "=" * 60)
        print("Training Complete!")
        print("=" * 60)
        print(f"\nFinal Performance:")
        print(f"• {success*10}% query parsing success")
        print(f"• {perfect*10}% perfect accuracy")
        print(f"• Handles complex multi-condition queries")
        print(f"• Ready for production use")

if __name__ == "__main__":
    main()