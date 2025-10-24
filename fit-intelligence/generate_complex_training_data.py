#!/usr/bin/env python3
"""
Generate Complex Training Data for Full LoRA Training
Includes multi-condition queries, financial analysis, and edge cases
"""

import json
import random
from datetime import datetime, timedelta

def generate_complex_training_data():
    """Generate comprehensive training data with complex queries"""
    
    print("Generating Complex Training Data for LoRA")
    print("=" * 60)
    
    examples = []
    
    # 1. Multi-condition queries (most important)
    multi_condition_queries = [
        {
            "input": "wind sites over 100kw in berkshire commissioned after 2015",
            "output": {
                "technology": "Wind",
                "capacity_min_kw": 100,
                "postcode_patterns": ["RG", "SL"],
                "commissioned_after": "2015-01-01"
            }
        },
        {
            "input": "solar farms between 500kw and 2MW in Yorkshire expiring within 5 years",
            "output": {
                "technology": "Photovoltaic",
                "capacity_min_kw": 500,
                "capacity_max_kw": 2000,
                "postcode_patterns": ["YO", "HU", "DN", "HD", "WF", "LS", "BD"],
                "fit_remaining_max": 5
            }
        },
        {
            "input": "hydro installations over 1MW in Scotland with FIT rate above 15p",
            "output": {
                "technology": "Hydro",
                "capacity_min_kw": 1000,
                "postcode_patterns": ["AB", "DD", "EH", "FK", "G", "IV", "KA", "KW"],
                "fit_rate_min": 15
            }
        },
        {
            "input": "wind or solar sites in Birmingham area under 50kw",
            "output": {
                "technologies": ["Wind", "Photovoltaic"],
                "capacity_max_kw": 50,
                "postcode_patterns": ["B", "CV", "DE", "DY"]
            }
        },
        {
            "input": "all renewable sites in RG17 postcode with capacity over 100kw",
            "output": {
                "postcode": "RG17",
                "capacity_min_kw": 100
            }
        }
    ]
    
    # 2. Financial analysis queries
    financial_queries = [
        {
            "input": "sites with annual revenue over £100000",
            "output": {
                "query_type": "financial",
                "metric": "annual_revenue",
                "min_value": 100000
            }
        },
        {
            "input": "compare ROI of wind vs solar in Scotland",
            "output": {
                "query_type": "comparison",
                "compare": ["Wind", "Photovoltaic"],
                "metric": "ROI",
                "postcode_patterns": ["AB", "DD", "EH", "FK", "G", "IV", "KA", "KW"]
            }
        },
        {
            "input": "top 10 highest earning solar farms",
            "output": {
                "query_type": "ranking",
                "technology": "Photovoltaic",
                "capacity_min_kw": 500,
                "sort_by": "annual_revenue",
                "limit": 10
            }
        },
        {
            "input": "sites with FIT revenue between £50k and £200k per year",
            "output": {
                "query_type": "financial",
                "metric": "annual_revenue",
                "min_value": 50000,
                "max_value": 200000
            }
        }
    ]
    
    # 3. Geographic and distance queries
    geographic_queries = [
        {
            "input": "wind farms within 30 miles of Birmingham",
            "output": {
                "query_type": "geographic",
                "technology": "Wind",
                "capacity_min_kw": 100,
                "center": "Birmingham",
                "radius_miles": 30
            }
        },
        {
            "input": "nearest solar installation to postcode RG1",
            "output": {
                "query_type": "nearest",
                "technology": "Photovoltaic",
                "reference_point": "RG1"
            }
        },
        {
            "input": "cluster analysis of wind sites in Yorkshire",
            "output": {
                "query_type": "cluster_analysis",
                "technology": "Wind",
                "postcode_patterns": ["YO", "HU", "DN", "HD", "WF", "LS", "BD"]
            }
        }
    ]
    
    # 4. Temporal and expiry queries
    temporal_queries = [
        {
            "input": "sites commissioned in 2018",
            "output": {
                "commissioned_year": 2018
            }
        },
        {
            "input": "installations expiring between 2025 and 2027",
            "output": {
                "expiry_start": "2025-01-01",
                "expiry_end": "2027-12-31"
            }
        },
        {
            "input": "sites with less than 3 years FIT remaining",
            "output": {
                "fit_remaining_max": 3
            }
        },
        {
            "input": "urgent repowering opportunities",
            "output": {
                "repowering_window": "URGENT",
                "fit_remaining_max": 2
            }
        }
    ]
    
    # 5. Aggregation and statistical queries
    aggregation_queries = [
        {
            "input": "total capacity of wind in Scotland",
            "output": {
                "query_type": "aggregation",
                "aggregation_type": "sum",
                "field": "capacity_kw",
                "technology": "Wind",
                "postcode_patterns": ["AB", "DD", "EH", "FK", "G", "IV", "KA", "KW"]
            }
        },
        {
            "input": "average FIT rate for solar farms over 1MW",
            "output": {
                "query_type": "aggregation",
                "aggregation_type": "average",
                "field": "fit_rate",
                "technology": "Photovoltaic",
                "capacity_min_kw": 1000
            }
        },
        {
            "input": "count of AD plants in England",
            "output": {
                "query_type": "aggregation",
                "aggregation_type": "count",
                "technology": "Anaerobic digestion",
                "country": "England"
            }
        }
    ]
    
    # 6. Complex boolean queries
    boolean_queries = [
        {
            "input": "wind sites over 500kw OR solar sites over 1MW in Yorkshire",
            "output": {
                "query_type": "boolean",
                "operator": "OR",
                "conditions": [
                    {"technology": "Wind", "capacity_min_kw": 500},
                    {"technology": "Photovoltaic", "capacity_min_kw": 1000}
                ],
                "postcode_patterns": ["YO", "HU", "DN", "HD", "WF", "LS", "BD"]
            }
        },
        {
            "input": "sites NOT in Scotland with capacity over 2MW",
            "output": {
                "query_type": "exclusion",
                "exclude_postcodes": ["AB", "DD", "EH", "FK", "G", "IV", "KA", "KW"],
                "capacity_min_kw": 2000
            }
        }
    ]
    
    # 7. Specific edge cases and variations
    edge_cases = [
        {
            "input": "fit 4004",
            "output": {
                "fit_id": "4004"
            }
        },
        {
            "input": "FIT ID 1585 details",
            "output": {
                "fit_id": "1585",
                "query_type": "detail"
            }
        },
        {
            "input": "show me everything in berkshire",
            "output": {
                "postcode_patterns": ["RG", "SL"]
            }
        },
        {
            "input": "2 megawatt solar farms",
            "output": {
                "technology": "Photovoltaic",
                "capacity_min_kw": 1800,
                "capacity_max_kw": 2200
            }
        },
        {
            "input": "half megawatt wind turbines in wales",
            "output": {
                "technology": "Wind",
                "capacity_min_kw": 400,
                "capacity_max_kw": 600,
                "postcode_patterns": ["CF", "LD", "LL", "NP", "SA", "SY"]
            }
        }
    ]
    
    # Combine all query types
    all_queries = (
        multi_condition_queries * 5 +  # Emphasize multi-condition
        financial_queries * 3 +
        geographic_queries * 3 +
        temporal_queries * 3 +
        aggregation_queries * 2 +
        boolean_queries * 2 +
        edge_cases * 4
    )
    
    # Generate variations of each query
    for base_query in all_queries:
        examples.append(base_query)
        
        # Generate variations
        input_text = base_query["input"]
        output_data = base_query["output"]
        
        # Variation 1: Different phrasing
        if "wind" in input_text.lower():
            variation = {
                "input": input_text.replace("wind", "wind turbine"),
                "output": output_data
            }
            examples.append(variation)
        
        if "solar" in input_text.lower():
            variation = {
                "input": input_text.replace("solar", "PV"),
                "output": output_data
            }
            examples.append(variation)
        
        # Variation 2: Question format
        if not input_text.startswith(("what", "how", "show")):
            variation = {
                "input": f"what are the {input_text}",
                "output": output_data
            }
            examples.append(variation)
    
    # Add location variations for all UK regions
    uk_regions = {
        "London": ["E", "EC", "N", "NW", "SE", "SW", "W", "WC"],
        "Manchester": ["M", "OL", "SK", "WA"],
        "Liverpool": ["L", "CH", "WA", "WN"],
        "Newcastle": ["NE", "DH", "SR", "TS"],
        "Cardiff": ["CF", "NP"],
        "Edinburgh": ["EH", "ML", "TD"],
        "Glasgow": ["G", "KA", "ML", "PA"],
        "Belfast": ["BT"],
        "Bristol": ["BS", "BA", "GL", "SN"],
        "Leeds": ["LS", "BD", "HX", "HD", "WF"]
    }
    
    for region, postcodes in uk_regions.items():
        examples.append({
            "input": f"all renewable installations in {region}",
            "output": {
                "location": region,
                "postcode_patterns": postcodes
            }
        })
        
        examples.append({
            "input": f"wind farms near {region}",
            "output": {
                "technology": "Wind",
                "capacity_min_kw": 100,
                "location": region,
                "postcode_patterns": postcodes
            }
        })
    
    # Shuffle examples
    random.shuffle(examples)
    
    # Split into train/val/test (80/10/10)
    total = len(examples)
    train_size = int(total * 0.8)
    val_size = int(total * 0.1)
    
    train_data = examples[:train_size]
    val_data = examples[train_size:train_size + val_size]
    test_data = examples[train_size + val_size:]
    
    # Save to files
    output_dir = "./lora_training_complex"
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f"{output_dir}/train.jsonl", 'w') as f:
        for item in train_data:
            f.write(json.dumps(item) + '\n')
    
    with open(f"{output_dir}/validation.jsonl", 'w') as f:
        for item in val_data:
            f.write(json.dumps(item) + '\n')
    
    with open(f"{output_dir}/test.jsonl", 'w') as f:
        for item in test_data:
            f.write(json.dumps(item) + '\n')
    
    print(f"✅ Generated {total} complex training examples")
    print(f"   Train: {len(train_data)}")
    print(f"   Validation: {len(val_data)}")
    print(f"   Test: {len(test_data)}")
    
    # Show sample complex queries
    print("\nSample Complex Queries:")
    print("-" * 40)
    for i, example in enumerate(random.sample(train_data, min(5, len(train_data))), 1):
        print(f"{i}. {example['input']}")
        print(f"   → {json.dumps(example['output'], indent=6)}")
    
    return output_dir

if __name__ == "__main__":
    output_dir = generate_complex_training_data()
    print(f"\n✅ Complex training data saved to: {output_dir}")
    print("\nReady for full LoRA training with complex queries!")