#!/usr/bin/env python3
"""
Generate Enhanced Training Data v2
Includes capacity+location patterns, nearest neighbor understanding,
and better location extraction
"""

import json
import random
from pathlib import Path

# UK Regions with their actual postcodes
UK_REGIONS = {
    # England - North
    "Yorkshire": ["YO", "HU", "DN", "HD", "WF", "LS", "BD", "HX", "HG"],
    "Ryedale": ["YO17", "YO18"],
    "Selby": ["YO8", "DN14"],
    "Durham": ["DH", "DL", "SR"],
    "Northumberland": ["NE", "TD"],
    "Cumbria": ["CA", "LA"],
    "Lancashire": ["LA", "BB", "PR", "FY"],
    
    # England - Midlands
    "Nottinghamshire": ["NG"],
    "Derbyshire": ["DE", "S"],
    "Leicestershire": ["LE"],
    "Birmingham": ["B"],
    "Worcestershire": ["WR", "DY"],
    
    # England - South
    "Berkshire": ["RG", "SL"],
    "Oxford": ["OX"],
    "Cambridge": ["CB"],
    "Norfolk": ["NR", "IP"],
    "Suffolk": ["IP", "CO"],
    "Kent": ["CT", "DA", "ME", "TN"],
    "Sussex": ["BN", "RH", "TN"],
    "Hampshire": ["SO", "PO", "GU", "RG"],
    
    # England - Southwest
    "Cornwall": ["TR", "PL", "EX"],
    "Devon": ["EX", "TQ", "PL"],
    "Somerset": ["BA", "BS", "TA"],
    
    # London
    "London": ["E", "EC", "N", "NW", "SE", "SW", "W", "WC"],
    
    # Scotland
    "Scotland": ["AB", "DD", "DG", "EH", "FK", "G", "HS", "IV", "KA", "KW", "KY", "ML", "PA", "PH", "TD", "ZE"],
    "Aberdeen": ["AB"],
    "Edinburgh": ["EH"],
    "Glasgow": ["G"],
    "Highland": ["IV", "PH", "KW"],
    
    # Wales
    "Wales": ["CF", "LD", "LL", "NP", "SA", "SY"],
    "Cardiff": ["CF"],
    "Swansea": ["SA"],
    
    # Northern Ireland (if needed)
    "Belfast": ["BT"]
}

def generate_training_examples():
    """Generate comprehensive training examples"""
    examples = []
    
    # 1. Capacity + Location queries (most important pattern)
    capacities = [50, 100, 150, 200, 250, 300, 330, 400, 500, 750, 1000, 1500, 2000]
    locations = ["yorkshire", "ryedale", "berkshire", "scotland", "wales", "cornwall", 
                 "suffolk", "norfolk", "devon", "cumbria", "durham", "london"]
    
    for capacity in capacities:
        for location in locations:
            # Simple capacity + location
            examples.append({
                "input": f"{capacity}kw in {location}",
                "output": json.dumps({
                    "capacity": capacity,
                    "location": location.title(),
                    "postcode_patterns": UK_REGIONS.get(location.title(), [])[:3]
                }, separators=(',', ':'))
            })
            
            # With technology
            for tech in ["wind", "solar", "hydro"]:
                tech_map = {"wind": "Wind", "solar": "Photovoltaic", "hydro": "Hydro"}
                examples.append({
                    "input": f"{capacity}kw {tech} in {location}",
                    "output": json.dumps({
                        "technology": tech_map[tech],
                        "capacity": capacity,
                        "location": location.title(),
                        "postcode_patterns": UK_REGIONS.get(location.title(), [])[:3]
                    }, separators=(',', ':'))
                })
                
                # Variations
                examples.append({
                    "input": f"{tech} {capacity}kw in {location}",
                    "output": json.dumps({
                        "technology": tech_map[tech],
                        "capacity": capacity,
                        "location": location.title(),
                        "postcode_patterns": UK_REGIONS.get(location.title(), [])[:3]
                    }, separators=(',', ':'))
                })
                
                if tech == "wind":
                    examples.append({
                        "input": f"{tech} turbine {capacity}kw in {location}",
                        "output": json.dumps({
                            "technology": "Wind",
                            "capacity": capacity,
                            "location": location.title(),
                            "postcode_patterns": UK_REGIONS.get(location.title(), [])[:3]
                        }, separators=(',', ':'))
                    })
    
    # 2. Capacity ranges with locations
    for min_cap, max_cap in [(100, 500), (500, 1000), (1000, 2000)]:
        for location in ["yorkshire", "scotland", "wales"]:
            examples.append({
                "input": f"{min_cap}-{max_cap}kw in {location}",
                "output": json.dumps({
                    "capacity_min": min_cap,
                    "capacity_max": max_cap,
                    "location": location.title(),
                    "postcode_patterns": UK_REGIONS.get(location.title(), [])[:3]
                }, separators=(',', ':'))
            })
            
            examples.append({
                "input": f"sites between {min_cap} and {max_cap}kw in {location}",
                "output": json.dumps({
                    "capacity_min": min_cap,
                    "capacity_max": max_cap,
                    "location": location.title(),
                    "postcode_patterns": UK_REGIONS.get(location.title(), [])[:3]
                }, separators=(',', ':'))
            })
    
    # 3. "Over/Under" capacity with location
    for threshold in [100, 200, 500, 1000]:
        for location in ["berkshire", "ryedale", "cornwall"]:
            examples.append({
                "input": f"over {threshold}kw in {location}",
                "output": json.dumps({
                    "capacity_min": threshold,
                    "location": location.title(),
                    "postcode_patterns": UK_REGIONS.get(location.title(), [])[:3]
                }, separators=(',', ':'))
            })
            
            examples.append({
                "input": f"wind sites over {threshold}kw in {location}",
                "output": json.dumps({
                    "technology": "Wind",
                    "capacity_min": threshold,
                    "location": location.title(),
                    "postcode_patterns": UK_REGIONS.get(location.title(), [])[:3]
                }, separators=(',', ':'))
            })
            
            examples.append({
                "input": f"under {threshold}kw in {location}",
                "output": json.dumps({
                    "capacity_max": threshold,
                    "location": location.title(),
                    "postcode_patterns": UK_REGIONS.get(location.title(), [])[:3]
                }, separators=(',', ':'))
            })
    
    # 4. Natural language variations
    natural_queries = [
        ("find 330kw installations in yorkshire", {
            "capacity": 330,
            "location": "Yorkshire",
            "postcode_patterns": ["YO", "HU", "DN"]
        }),
        ("show me wind farms around 500kw in scotland", {
            "technology": "Wind",
            "capacity": 500,
            "location": "Scotland",
            "postcode_patterns": ["AB", "DD", "EH"]
        }),
        ("I need solar sites near 250kw capacity in devon", {
            "technology": "Photovoltaic",
            "capacity": 250,
            "location": "Devon",
            "postcode_patterns": ["EX", "TQ", "PL"]
        }),
        ("what wind turbines are there at 330kw in ryedale", {
            "technology": "Wind",
            "capacity": 330,
            "location": "Ryedale",
            "postcode_patterns": ["YO17", "YO18"]
        }),
        ("looking for 100kw solar in berkshire area", {
            "technology": "Photovoltaic",
            "capacity": 100,
            "location": "Berkshire",
            "postcode_patterns": ["RG", "SL"]
        })
    ]
    
    for query, output in natural_queries:
        examples.append({
            "input": query,
            "output": json.dumps(output, separators=(',', ':'))
        })
    
    # 5. Location-only queries
    for location in ["yorkshire", "scotland", "wales", "london", "cornwall"]:
        examples.append({
            "input": f"all sites in {location}",
            "output": json.dumps({
                "location": location.title(),
                "postcode_patterns": UK_REGIONS.get(location.title(), [])[:3]
            }, separators=(',', ':'))
        })
        
        examples.append({
            "input": f"wind in {location}",
            "output": json.dumps({
                "technology": "Wind",
                "location": location.title(),
                "postcode_patterns": UK_REGIONS.get(location.title(), [])[:3]
            }, separators=(',', ':'))
        })
    
    # 6. Complex multi-condition queries
    complex_examples = [
        ("wind sites over 100kw in berkshire expiring soon", {
            "technology": "Wind",
            "capacity_min": 100,
            "location": "Berkshire",
            "postcode_patterns": ["RG", "SL"],
            "fit_remaining_max": 5
        }),
        ("large solar farms over 1mw in scotland", {
            "technology": "Photovoltaic",
            "capacity_min": 1000,
            "location": "Scotland",
            "postcode_patterns": ["AB", "DD", "EH"]
        }),
        ("hydro between 200 and 500kw in wales", {
            "technology": "Hydro",
            "capacity_min": 200,
            "capacity_max": 500,
            "location": "Wales",
            "postcode_patterns": ["CF", "LD", "LL"]
        })
    ]
    
    for query, output in complex_examples:
        examples.append({
            "input": query,
            "output": json.dumps(output, separators=(',', ':'))
        })
    
    # 7. Geographic queries with radius
    geo_examples = [
        ("within 10 miles of york", {
            "query_type": "geographic",
            "geo_center": "York",
            "geo_radius": 10
        }),
        ("sites near cambridge within 20 miles", {
            "query_type": "geographic",
            "geo_center": "Cambridge",
            "geo_radius": 20
        }),
        ("wind farms within 15 miles of edinburgh", {
            "query_type": "geographic",
            "technology": "Wind",
            "geo_center": "Edinburgh",
            "geo_radius": 15
        })
    ]
    
    for query, output in geo_examples:
        examples.append({
            "input": query,
            "output": json.dumps(output, separators=(',', ':'))
        })
    
    # 8. Financial queries
    financial_examples = [
        ("sites with fit rate over 15p", {
            "query_type": "financial",
            "fit_rate_min": 15
        }),
        ("high revenue sites over 100000 per year", {
            "query_type": "financial",
            "revenue_min": 100000
        }),
        ("best roi opportunities in yorkshire", {
            "query_type": "opportunity",
            "opportunity_type": "roi",
            "location": "Yorkshire",
            "postcode_patterns": ["YO", "HU", "DN"]
        })
    ]
    
    for query, output in financial_examples:
        examples.append({
            "input": query,
            "output": json.dumps(output, separators=(',', ':'))
        })
    
    # 9. Aggregation queries
    agg_examples = [
        ("count wind farms in scotland", {
            "query_type": "aggregation",
            "aggregation_type": "count",
            "technology": "Wind",
            "location": "Scotland",
            "postcode_patterns": ["AB", "DD", "EH"]
        }),
        ("total capacity in yorkshire", {
            "query_type": "aggregation",
            "aggregation_type": "sum",
            "field": "capacity",
            "location": "Yorkshire",
            "postcode_patterns": ["YO", "HU", "DN"]
        }),
        ("average size of solar farms", {
            "query_type": "aggregation",
            "aggregation_type": "average",
            "field": "capacity",
            "technology": "Photovoltaic"
        })
    ]
    
    for query, output in agg_examples:
        examples.append({
            "input": query,
            "output": json.dumps(output, separators=(',', ':'))
        })
    
    # Shuffle for better training
    random.shuffle(examples)
    
    return examples

def save_training_data():
    """Generate and save enhanced training data"""
    examples = generate_training_examples()
    
    # Create output directory
    output_dir = Path("enhanced_training_v2")
    output_dir.mkdir(exist_ok=True)
    
    # Split into train/validation/test (80/10/10)
    total = len(examples)
    train_size = int(total * 0.8)
    val_size = int(total * 0.1)
    
    train_examples = examples[:train_size]
    val_examples = examples[train_size:train_size + val_size]
    test_examples = examples[train_size + val_size:]
    
    # Save datasets
    for name, data in [("train", train_examples), ("validation", val_examples), ("test", test_examples)]:
        file_path = output_dir / f"{name}.jsonl"
        with open(file_path, 'w') as f:
            for example in data:
                f.write(json.dumps(example) + '\n')
        print(f"Saved {len(data)} examples to {file_path}")
    
    print(f"\nTotal examples generated: {total}")
    print("Training data includes:")
    print("- Capacity + Location patterns")
    print("- Nearest neighbor understanding")
    print("- Technology + Capacity + Location")
    print("- Geographic radius queries")
    print("- Financial and aggregation queries")
    print("- Natural language variations")
    
    # Save a sample for review
    sample_file = output_dir / "sample_examples.json"
    with open(sample_file, 'w') as f:
        json.dump(random.sample(examples, min(20, len(examples))), f, indent=2)
    print(f"\nSample saved to {sample_file}")

if __name__ == "__main__":
    save_training_data()