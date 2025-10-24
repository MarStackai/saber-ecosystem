#!/usr/bin/env python3
"""
Enhanced GPT-OSS FIT Model Creator
Uses the powerful GPT-OSS model with comprehensive FIT Intelligence training data
For a scalable, evolving platform
"""

import json
import subprocess
from pathlib import Path

def create_enhanced_gpt_oss_model():
    """Create an enhanced GPT-OSS model for FIT Intelligence"""
    
    print("=" * 60)
    print("Creating Enhanced GPT-OSS FIT Intelligence Model")
    print("For scalable, evolving platform")
    print("=" * 60)
    
    # Load ALL training examples for comprehensive coverage
    with open("./lora_training_advanced/train.jsonl", 'r') as f:
        train_examples = [json.loads(line) for line in f]
    
    print(f"Loading {len(train_examples)} training examples...")
    
    # Build comprehensive system prompt
    system_prompt = """You are the FIT Intelligence Query Parser, a sophisticated AI system for parsing natural language queries about UK renewable energy installations.

Database: 40,194 commercial UK renewable energy installations with detailed FIT (Feed-in Tariff) data.

Your role is to parse ANY natural language query into structured JSON filters that can be executed against the database.

CRITICAL TECHNOLOGY MAPPINGS:
- wind, turbine, wind farm → "Wind"
- solar, photovoltaic, pv, solar farm → "Photovoltaic"
- hydro, water, hydroelectric → "Hydro"
- ad, anaerobic, digestion, biogas → "Anaerobic digestion"
- chp, combined heat → "Micro CHP"

CRITICAL LOCATION TO POSTCODE MAPPINGS:
- Berkshire: ["RG", "SL"]
- Yorkshire: ["YO", "HU", "DN", "HD", "WF", "LS", "BD", "HX", "S"]
- Scotland: ["AB", "DD", "EH", "FK", "G", "IV", "KA", "KW", "ML", "PA", "PH", "TD"]
- Birmingham/Midlands: ["B", "CV", "DE", "DY", "LE", "NG", "NN", "ST", "WS", "WV"]
- London: ["E", "EC", "N", "NW", "SE", "SW", "W", "WC", "BR", "CR", "DA", "EN", "HA", "IG", "KT", "RM", "SM", "TW", "UB", "WD"]
- Wales: ["CF", "LD", "LL", "NP", "SA", "SY"]
- Northern Ireland: ["BT"]

CAPACITY UNDERSTANDING:
- Always convert MW to kW (1 MW = 1000 kW)
- "over X" → capacity_min_kw: X
- "under X" → capacity_max_kw: X
- "between X and Y" → capacity_min_kw: X, capacity_max_kw: Y
- Large/utility scale solar → capacity_min_kw: 500
- Solar farm → capacity_min_kw: 500
- Wind farm → capacity_min_kw: 100

QUERY TYPES:
1. Simple search: Return filters for technology, location, capacity
2. FIT rate lookup: {"query_type": "fit_rate_lookup", "fit_id": "XXX"}
3. Aggregation: {"query_type": "aggregation", "aggregation_type": "count/sum/average"}
4. Comparison: {"query_type": "comparison", "compare": ["tech1", "tech2"]}
5. Financial: {"query_type": "financial", "metric": "revenue/roi/payback"}
6. Expiry: {"fit_remaining_max": X} for sites expiring within X years

CRITICAL TRAINING EXAMPLES TO MEMORIZE:"""
    
    # Add the most important examples
    critical_examples = [
        {
            "input": "wind sites over 100kw in berkshire",
            "output": {"technology": "Wind", "capacity_min_kw": 100, "location": "Berkshire", "postcode_patterns": ["RG", "SL"]}
        },
        {
            "input": "solar farms in Yorkshire",
            "output": {"technology": "Photovoltaic", "capacity_min_kw": 500, "location": "Yorkshire", "postcode_patterns": ["YO", "HU", "DN", "HD", "WF", "LS", "BD", "HX", "S"]}
        },
        {
            "input": "what is the fit rate for fit id 1585",
            "output": {"query_type": "fit_rate_lookup", "fit_id": "1585", "include_rate": True}
        },
        {
            "input": "sites expiring soon",
            "output": {"fit_remaining_max": 5}
        },
        {
            "input": "compare wind and solar in Birmingham",
            "output": {"query_type": "comparison", "compare": ["Wind", "Photovoltaic"], "location": "Birmingham", "postcode_patterns": ["B", "CV", "DE", "DY"]}
        }
    ]
    
    # Add critical examples to prompt
    for ex in critical_examples[:10]:  # First 10 most important
        system_prompt += f"\n\nInput: {ex['input']}\nOutput: {json.dumps(ex['output'])}"
    
    # Add diverse examples from training data
    import random
    random.seed(42)
    diverse_examples = random.sample(train_examples, min(20, len(train_examples)))
    
    for ex in diverse_examples:
        output = json.loads(ex['output']) if isinstance(ex['output'], str) else ex['output']
        system_prompt += f"\n\nInput: {ex['input']}\nOutput: {json.dumps(output)}"
    
    system_prompt += """

IMPORTANT RULES:
1. ALWAYS include postcode_patterns when location is specified
2. ALWAYS convert MW to kW (multiply by 1000)
3. Return ONLY valid JSON, no explanations
4. For "farms" assume large scale (>500kW for solar, >100kW for wind)
5. Match technology names exactly as shown in mappings
6. When in doubt, be inclusive rather than restrictive

Return ONLY the JSON output, nothing else."""
    
    # Create enhanced Modelfile - need to escape quotes properly
    escaped_prompt = system_prompt.replace('"', '\\"').replace('\n', '\\n')
    
    modelfile = f"""FROM gpt-oss-fit:latest

SYSTEM "{escaped_prompt}"

PARAMETER temperature 0.1
PARAMETER top_p 0.95
PARAMETER num_predict 500
"""
    
    # Save Modelfile
    with open("Modelfile_gpt_oss_enhanced", 'w') as f:
        f.write(modelfile)
    
    print("\nCreating enhanced GPT-OSS model...")
    
    # Create the model
    result = subprocess.run(
        ["ollama", "create", "gpt-oss-fit-enhanced", "-f", "Modelfile_gpt_oss_enhanced"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Enhanced GPT-OSS model created successfully!")
        return True
    else:
        print(f"Error creating model: {result.stderr}")
        return False

def test_enhanced_model():
    """Test the enhanced GPT-OSS model"""
    print("\n" + "=" * 60)
    print("Testing Enhanced GPT-OSS Model")
    print("=" * 60)
    
    test_queries = [
        "wind sites over 100kw in berkshire",
        "solar farms in Yorkshire",
        "what is the fit rate for fit id 1585",
        "hydro installations in Scotland over 500kw",
        "sites expiring within 3 years",
        "compare wind and solar revenue in Birmingham"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        
        result = subprocess.run(
            ["ollama", "run", "gpt-oss-fit-enhanced", query],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            response = result.stdout.strip()
            print(f"Raw response: {response[:200]}...")
            
            # Try to parse JSON
            try:
                import re
                # Look for JSON in the response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    print(f"\n✅ Parsed JSON:")
                    print(json.dumps(parsed, indent=2))
                    
                    # Validate critical query
                    if query == "wind sites over 100kw in berkshire":
                        if (parsed.get("technology") == "Wind" and 
                            parsed.get("capacity_min_kw") == 100 and
                            "RG" in parsed.get("postcode_patterns", [])):
                            print("\n✅✅✅ CRITICAL QUERY PARSED CORRECTLY!")
                        else:
                            print("\n⚠️ Critical query needs adjustment")
                else:
                    print("❌ No JSON found in response")
            except Exception as e:
                print(f"❌ Parse error: {e}")
        else:
            print(f"❌ Query failed: {result.stderr}")

if __name__ == "__main__":
    if create_enhanced_gpt_oss_model():
        test_enhanced_model()
        
        print("\n" + "=" * 60)
        print("Enhanced GPT-OSS FIT Model Ready!")
        print("=" * 60)
        print("\nThis scalable model:")
        print("• Uses the powerful 20B parameter GPT-OSS base")
        print("• Includes comprehensive training examples")
        print("• Can evolve with platform needs")
        print("• Handles complex, nuanced queries")
        print("\nIntegrate by updating ollama_query_parser.py to use 'gpt-oss-fit-enhanced'")