#!/usr/bin/env python3
"""
Validate LoRA training data for FIT Intelligence
Ensure data quality before training
"""

import json
import random
from pathlib import Path
from collections import Counter

def validate_training_data():
    """Validate the training data quality"""
    
    print("=" * 60)
    print("FIT Intelligence Training Data Validation")
    print("=" * 60)
    
    data_dir = Path("./lora_training_advanced")
    
    # Load all data
    all_examples = []
    for split in ["train", "validation", "test"]:
        file_path = data_dir / f"{split}.jsonl"
        if not file_path.exists():
            print(f"❌ Missing {split}.jsonl")
            return
        
        with open(file_path, 'r') as f:
            examples = [json.loads(line) for line in f]
            all_examples.extend(examples)
            print(f"✅ {split}: {len(examples)} examples")
    
    print(f"\nTotal examples: {len(all_examples)}")
    
    # Validate critical queries are included
    print("\n" + "=" * 60)
    print("Critical Query Coverage")
    print("=" * 60)
    
    critical_queries = [
        "wind sites over 100kw in berkshire",
        "solar farms in Yorkshire",
        "what is the fit rate for fit id 1585",
        "sites expiring soon",
        "compare wind and solar in Birmingham"
    ]
    
    for query in critical_queries:
        found = any(query.lower() in ex['input'].lower() for ex in all_examples)
        status = "✅" if found else "❌"
        print(f"{status} {query}")
    
    # Analyze query types
    print("\n" + "=" * 60)
    print("Query Type Distribution")
    print("=" * 60)
    
    query_types = Counter()
    for ex in all_examples:
        output = ex['output']
        if isinstance(output, str):
            try:
                output = json.loads(output)
            except:
                continue
        
        # Categorize by filters used
        if 'technology' in output:
            query_types['technology'] += 1
        if 'capacity_min_kw' in output or 'capacity_max_kw' in output:
            query_types['capacity'] += 1
        if 'postcode_patterns' in output or 'location' in output:
            query_types['location'] += 1
        if 'fit_id' in output:
            query_types['fit_id'] += 1
        if 'compare' in output:
            query_types['comparison'] += 1
        if 'expiry' in output or 'commissioned' in output:
            query_types['temporal'] += 1
    
    for qtype, count in query_types.most_common():
        pct = count / len(all_examples) * 100
        print(f"  {qtype}: {count} ({pct:.1f}%)")
    
    # Check for the specific failing case
    print("\n" + "=" * 60)
    print("Specific Failing Case Check")
    print("=" * 60)
    
    failing_case = "wind sites over 100kw in berkshire"
    matching = [ex for ex in all_examples if failing_case.lower() in ex['input'].lower()]
    
    if matching:
        print(f"✅ Found {len(matching)} examples for: '{failing_case}'")
        example = matching[0]
        print(f"\nExample training pair:")
        print(f"Input: {example['input']}")
        print(f"Output: {json.dumps(json.loads(example['output']) if isinstance(example['output'], str) else example['output'], indent=2)}")
    else:
        print(f"❌ No examples found for: '{failing_case}'")
    
    # Sample random examples
    print("\n" + "=" * 60)
    print("Random Training Examples")
    print("=" * 60)
    
    for i, ex in enumerate(random.sample(all_examples, min(3, len(all_examples))), 1):
        print(f"\nExample {i}:")
        print(f"Input: {ex['input']}")
        try:
            output = json.loads(ex['output']) if isinstance(ex['output'], str) else ex['output']
            print(f"Output: {json.dumps(output, indent=2)}")
        except:
            print(f"Output: {ex['output']}")
    
    # Validate JSON structure
    print("\n" + "=" * 60)
    print("Data Quality Checks")
    print("=" * 60)
    
    invalid_count = 0
    for ex in all_examples:
        try:
            output = json.loads(ex['output']) if isinstance(ex['output'], str) else ex['output']
            # Check it's valid JSON structure
            assert isinstance(output, dict)
        except:
            invalid_count += 1
    
    if invalid_count == 0:
        print("✅ All outputs are valid JSON")
    else:
        print(f"⚠️  {invalid_count} examples have invalid JSON outputs")
    
    # Check for duplicates
    inputs = [ex['input'] for ex in all_examples]
    unique_inputs = set(inputs)
    if len(inputs) == len(unique_inputs):
        print("✅ No duplicate inputs found")
    else:
        print(f"⚠️  {len(inputs) - len(unique_inputs)} duplicate inputs found")
    
    print("\n" + "=" * 60)
    print("Validation Complete")
    print("=" * 60)
    
    if invalid_count == 0 and len(matching) > 0:
        print("\n✅ Training data is ready for LoRA fine-tuning!")
        print("✅ Critical failing query is covered in training data")
    else:
        print("\n⚠️  Some issues found - review above")

if __name__ == "__main__":
    validate_training_data()