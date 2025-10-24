#!/usr/bin/env python3
"""
Generate Comprehensive Weekend Training Dataset
Full dataset with varied prompts, structured answers, and reasoning chains
Target: 50,000+ training examples for weekend training
"""

import json
import random
import itertools
from datetime import datetime, timedelta
from pathlib import Path

class WeekendDatasetGenerator:
    """Generate massive, high-quality training dataset for weekend training"""
    
    def __init__(self):
        self.technologies = ["Wind", "Photovoltaic", "Hydro", "Anaerobic digestion", "Micro CHP"]
        self.uk_regions = {
            "Scotland": {
                "postcodes": ["AB", "DD", "DH", "EH", "FK", "G", "IV", "KA", "KW", "KY", "ML", "PA", "PH", "TD", "ZE"],
                "cities": ["Edinburgh", "Glasgow", "Aberdeen", "Dundee", "Inverness", "Perth", "Stirling"]
            },
            "Wales": {
                "postcodes": ["CF", "LD", "LL", "NP", "SA", "SY"],
                "cities": ["Cardiff", "Swansea", "Newport", "Wrexham", "Bangor"]
            },
            "Northern England": {
                "postcodes": ["NE", "DH", "SR", "TS", "DL", "YO", "HU", "DN", "HD", "WF", "LS", "BD", "HX", "HG"],
                "cities": ["Newcastle", "Leeds", "Sheffield", "Hull", "York", "Bradford", "Middlesbrough"]
            },
            "Midlands": {
                "postcodes": ["B", "CV", "DE", "DY", "LE", "NG", "NN", "ST", "WS", "WV", "WR", "HR"],
                "cities": ["Birmingham", "Leicester", "Nottingham", "Derby", "Coventry", "Stoke", "Wolverhampton"]
            },
            "Southern England": {
                "postcodes": ["RG", "SL", "OX", "MK", "LU", "AL", "HP", "SG", "CM", "CO", "IP", "NR", "PE", "CB"],
                "cities": ["Reading", "Oxford", "Cambridge", "Norwich", "Milton Keynes", "Luton", "Ipswich"]
            },
            "London & Southeast": {
                "postcodes": ["E", "EC", "N", "NW", "SE", "SW", "W", "WC", "BR", "CR", "DA", "EN", "HA", "IG", "KT", "RM", "SM", "TW", "UB", "WD"],
                "cities": ["London", "Croydon", "Bromley", "Sutton", "Richmond", "Kingston", "Harrow"]
            },
            "Southwest": {
                "postcodes": ["BA", "BH", "BS", "DT", "EX", "GL", "PL", "SN", "SP", "TA", "TQ", "TR"],
                "cities": ["Bristol", "Plymouth", "Exeter", "Bath", "Gloucester", "Bournemouth", "Swindon"]
            },
            "Northwest": {
                "postcodes": ["M", "L", "CH", "WA", "WN", "PR", "FY", "LA", "BB", "BL", "OL", "SK", "CW"],
                "cities": ["Manchester", "Liverpool", "Preston", "Blackpool", "Warrington", "Chester", "Lancaster"]
            }
        }
        
        self.capacity_ranges = [
            (0, 10, "micro"),
            (10, 50, "small"),
            (50, 100, "medium"),
            (100, 500, "large"),
            (500, 1000, "utility"),
            (1000, 5000, "mega"),
            (5000, 50000, "giant")
        ]
        
        self.time_periods = [
            "commissioned before 2010",
            "commissioned between 2010 and 2015",
            "commissioned between 2015 and 2020",
            "commissioned after 2020",
            "expiring within 1 year",
            "expiring within 2 years",
            "expiring within 5 years",
            "expiring between 2025 and 2030",
            "with more than 10 years remaining",
            "with less than 3 years remaining"
        ]
        
        self.financial_conditions = [
            "with annual revenue over £50000",
            "with annual revenue over £100000",
            "with annual revenue between £25000 and £75000",
            "with FIT rate above 10p",
            "with FIT rate above 15p",
            "with FIT rate between 5p and 10p",
            "generating over 1000 MWh per year",
            "with capacity factor above 25%",
            "with ROI above 10%",
            "with payback period under 10 years"
        ]
    
    def generate_base_queries(self):
        """Generate base query patterns"""
        examples = []
        
        # 1. Simple technology queries for each region
        for tech in self.technologies:
            for region_name, region_data in self.uk_regions.items():
                # Basic query
                examples.append({
                    "input": f"{tech.lower()} installations in {region_name}",
                    "output": {
                        "technology": tech,
                        "location": region_name,
                        "postcode_patterns": region_data["postcodes"]
                    },
                    "reasoning": f"User wants {tech} installations in {region_name}. Map to technology and postcodes."
                })
                
                # With capacity
                for min_cap, max_cap, size_name in self.capacity_ranges:
                    if size_name in ["micro", "small", "medium"]:
                        examples.append({
                            "input": f"{size_name} {tech.lower()} sites in {region_name}",
                            "output": {
                                "technology": tech,
                                "capacity_min_kw": min_cap,
                                "capacity_max_kw": max_cap,
                                "location": region_name,
                                "postcode_patterns": region_data["postcodes"]
                            },
                            "reasoning": f"{size_name} indicates capacity range {min_cap}-{max_cap}kW"
                        })
                
                # Specific cities
                for city in region_data["cities"][:3]:  # Top 3 cities
                    examples.append({
                        "input": f"{tech.lower()} near {city}",
                        "output": {
                            "technology": tech,
                            "location": city,
                            "postcode_patterns": region_data["postcodes"]
                        },
                        "reasoning": f"{city} is in {region_name}, use regional postcodes"
                    })
        
        return examples
    
    def generate_complex_queries(self):
        """Generate complex multi-condition queries"""
        examples = []
        
        # Multi-condition combinations
        for tech in self.technologies:
            for region_name, region_data in random.sample(list(self.uk_regions.items()), 4):
                for time_condition in random.sample(self.time_periods, 3):
                    for financial in random.sample(self.financial_conditions, 2):
                        # Parse the conditions
                        output = {
                            "technology": tech,
                            "location": region_name,
                            "postcode_patterns": region_data["postcodes"]
                        }
                        
                        # Parse time condition
                        if "commissioned before" in time_condition:
                            year = time_condition.split()[-1]
                            output["commissioned_before"] = f"{year}-01-01"
                        elif "commissioned after" in time_condition:
                            year = time_condition.split()[-1]
                            output["commissioned_after"] = f"{year}-01-01"
                        elif "expiring within" in time_condition:
                            years = [int(s) for s in time_condition.split() if s.isdigit()][0]
                            output["fit_remaining_max"] = years
                        
                        # Parse financial condition
                        if "revenue over £" in financial:
                            amount = int(''.join(filter(str.isdigit, financial.split('£')[1])))
                            output["annual_revenue_min"] = amount
                        elif "FIT rate above" in financial:
                            rate = int(''.join(filter(str.isdigit, financial.split('above')[1])))
                            output["fit_rate_min"] = rate
                        
                        examples.append({
                            "input": f"{tech.lower()} in {region_name} {time_condition} {financial}",
                            "output": output,
                            "reasoning": f"Complex query combining technology ({tech}), location ({region_name}), temporal ({time_condition}), and financial ({financial}) conditions"
                        })
        
        return examples
    
    def generate_natural_variations(self, base_examples):
        """Generate natural language variations of queries"""
        variations = []
        
        question_starters = [
            "show me",
            "find",
            "list",
            "what are the",
            "can you find",
            "I need",
            "looking for",
            "search for",
            "get me",
            "display",
            "where are the",
            "identify"
        ]
        
        for example in base_examples:
            # Original
            variations.append(example)
            
            # Question variations
            for starter in random.sample(question_starters, 3):
                varied_input = f"{starter} {example['input']}"
                variations.append({
                    "input": varied_input,
                    "output": example["output"],
                    "reasoning": example.get("reasoning", "Same as base query with different phrasing")
                })
            
            # Informal variations
            if "wind" in example["input"].lower():
                informal = example["input"].replace("wind", "wind turbines")
                variations.append({
                    "input": informal,
                    "output": example["output"],
                    "reasoning": "Wind turbines is synonym for wind technology"
                })
            
            if "photovoltaic" in example["input"].lower():
                for alt in ["solar panels", "PV systems", "solar arrays"]:
                    informal = example["input"].replace("photovoltaic", alt)
                    variations.append({
                        "input": informal,
                        "output": example["output"],
                        "reasoning": f"{alt} is synonym for photovoltaic technology"
                    })
        
        return variations
    
    def generate_aggregation_queries(self):
        """Generate aggregation and analysis queries"""
        examples = []
        
        agg_types = [
            ("total capacity", "sum", "capacity_kw"),
            ("average size", "average", "capacity_kw"),
            ("number of", "count", None),
            ("total revenue", "sum", "annual_revenue"),
            ("average FIT rate", "average", "fit_rate"),
            ("maximum capacity", "max", "capacity_kw"),
            ("minimum capacity", "min", "capacity_kw")
        ]
        
        for tech in self.technologies:
            for region_name, region_data in self.uk_regions.items():
                for agg_phrase, agg_type, field in random.sample(agg_types, 3):
                    output = {
                        "query_type": "aggregation",
                        "aggregation_type": agg_type,
                        "technology": tech,
                        "location": region_name,
                        "postcode_patterns": region_data["postcodes"]
                    }
                    
                    if field:
                        output["field"] = field
                    
                    examples.append({
                        "input": f"{agg_phrase} of {tech.lower()} installations in {region_name}",
                        "output": output,
                        "reasoning": f"Aggregation query requiring {agg_type} calculation on {field or 'count'}"
                    })
        
        return examples
    
    def generate_comparison_queries(self):
        """Generate comparison queries"""
        examples = []
        
        metrics = ["capacity", "revenue", "efficiency", "FIT rates", "ROI", "performance"]
        
        for tech1, tech2 in itertools.combinations(self.technologies, 2):
            for region_name, region_data in random.sample(list(self.uk_regions.items()), 3):
                for metric in random.sample(metrics, 2):
                    examples.append({
                        "input": f"compare {metric} of {tech1.lower()} vs {tech2.lower()} in {region_name}",
                        "output": {
                            "query_type": "comparison",
                            "compare": [tech1, tech2],
                            "metric": metric,
                            "location": region_name,
                            "postcode_patterns": region_data["postcodes"]
                        },
                        "reasoning": f"Comparison query between {tech1} and {tech2} on {metric} metric"
                    })
        
        return examples
    
    def generate_geographic_queries(self):
        """Generate geographic and distance-based queries"""
        examples = []
        
        distances = [10, 20, 30, 50, 100]
        
        for tech in self.technologies:
            for region_name, region_data in self.uk_regions.items():
                for city in region_data["cities"][:2]:
                    for distance in random.sample(distances, 2):
                        examples.append({
                            "input": f"{tech.lower()} within {distance} miles of {city}",
                            "output": {
                                "query_type": "geographic",
                                "technology": tech,
                                "center": city,
                                "radius_miles": distance
                            },
                            "reasoning": f"Geographic radius search centered on {city} with {distance} mile radius"
                        })
                        
                        # Nearest neighbor variant
                        examples.append({
                            "input": f"nearest {tech.lower()} installation to {city}",
                            "output": {
                                "query_type": "nearest",
                                "technology": tech,
                                "reference_point": city
                            },
                            "reasoning": f"Find closest {tech} installation to {city}"
                        })
        
        return examples
    
    def generate_business_queries(self):
        """Generate business and investment queries"""
        examples = []
        
        business_scenarios = [
            {
                "input": "best repowering opportunities in {region}",
                "output": {
                    "query_type": "business_opportunity",
                    "opportunity_type": "repowering",
                    "fit_remaining_max": 5,
                    "capacity_min_kw": 100
                },
                "reasoning": "Repowering opportunities are sites with FIT expiring soon"
            },
            {
                "input": "underperforming {tech} sites in {region}",
                "output": {
                    "query_type": "performance_analysis",
                    "performance": "underperforming",
                    "capacity_factor_max": 20
                },
                "reasoning": "Underperforming sites have low capacity factors"
            },
            {
                "input": "investment opportunities in {tech} sector",
                "output": {
                    "query_type": "investment_analysis",
                    "roi_min": 8,
                    "payback_max_years": 12
                },
                "reasoning": "Investment opportunities need good ROI and reasonable payback"
            },
            {
                "input": "sites suitable for battery storage in {region}",
                "output": {
                    "query_type": "storage_opportunity",
                    "capacity_min_kw": 500,
                    "grid_connection": "adequate"
                },
                "reasoning": "Battery storage needs larger sites with good grid connections"
            }
        ]
        
        for scenario in business_scenarios:
            for tech in self.technologies:
                for region_name, region_data in random.sample(list(self.uk_regions.items()), 2):
                    input_text = scenario["input"].replace("{tech}", tech.lower()).replace("{region}", region_name)
                    output = scenario["output"].copy()
                    
                    if "{tech}" in scenario["input"]:
                        output["technology"] = tech
                    if "{region}" in scenario["input"]:
                        output["location"] = region_name
                        output["postcode_patterns"] = region_data["postcodes"]
                    
                    examples.append({
                        "input": input_text,
                        "output": output,
                        "reasoning": scenario["reasoning"]
                    })
        
        return examples
    
    def generate_specific_queries(self):
        """Generate queries for specific FIT IDs and installations"""
        examples = []
        
        # Generate realistic FIT IDs
        fit_ids = [str(random.randint(1, 50000)) for _ in range(100)]
        
        query_patterns = [
            ("fit {id}", {"fit_id": "{id}"}),
            ("FIT ID {id}", {"fit_id": "{id}"}),
            ("installation {id}", {"fit_id": "{id}"}),
            ("show me fit {id}", {"fit_id": "{id}"}),
            ("details for fit {id}", {"fit_id": "{id}", "query_type": "detail"}),
            ("what is the fit rate for fit id {id}", {"fit_id": "{id}", "query_type": "fit_rate_lookup"}),
            ("revenue for installation {id}", {"fit_id": "{id}", "query_type": "revenue_lookup"}),
            ("performance of fit {id}", {"fit_id": "{id}", "query_type": "performance_analysis"})
        ]
        
        for fit_id in fit_ids:
            pattern, output_template = random.choice(query_patterns)
            input_text = pattern.replace("{id}", fit_id)
            output = {}
            for key, value in output_template.items():
                output[key] = value.replace("{id}", fit_id)
            
            examples.append({
                "input": input_text,
                "output": output,
                "reasoning": f"Direct lookup for specific FIT ID {fit_id}"
            })
        
        return examples
    
    def generate_edge_cases(self):
        """Generate edge cases and unusual queries"""
        examples = []
        
        edge_cases = [
            {
                "input": "everything",
                "output": {},
                "reasoning": "No filters - return all installations"
            },
            {
                "input": "all renewable energy",
                "output": {},
                "reasoning": "All installations are renewable"
            },
            {
                "input": "2 megawatt solar farms",
                "output": {
                    "technology": "Photovoltaic",
                    "capacity_min_kw": 1800,
                    "capacity_max_kw": 2200
                },
                "reasoning": "2MW = 2000kW, allow some tolerance"
            },
            {
                "input": "half megawatt wind turbines",
                "output": {
                    "technology": "Wind",
                    "capacity_min_kw": 400,
                    "capacity_max_kw": 600
                },
                "reasoning": "0.5MW = 500kW, allow tolerance"
            },
            {
                "input": "100kw to 1mw installations",
                "output": {
                    "capacity_min_kw": 100,
                    "capacity_max_kw": 1000
                },
                "reasoning": "Convert MW to kW for consistency"
            },
            {
                "input": "not in scotland",
                "output": {
                    "query_type": "exclusion",
                    "exclude_postcodes": ["AB", "DD", "DH", "EH", "FK", "G", "IV", "KA", "KW", "KY", "ML", "PA", "PH", "TD", "ZE"]
                },
                "reasoning": "Exclusion query - filter out Scottish postcodes"
            },
            {
                "input": "either wind or solar",
                "output": {
                    "technologies": ["Wind", "Photovoltaic"]
                },
                "reasoning": "Multiple technology selection"
            },
            {
                "input": "excluding micro chp",
                "output": {
                    "exclude_technology": "Micro CHP"
                },
                "reasoning": "Technology exclusion"
            }
        ]
        
        examples.extend(edge_cases)
        
        # Misspellings and variations
        misspellings = [
            ("berkshire", ["berkshire", "berkshir", "berks"]),
            ("yorkshire", ["yorkshire", "yorkshir", "yorks"]),
            ("photovoltaic", ["photovoltaic", "photovoltaics", "foto-voltaic"]),
            ("anaerobic", ["anaerobic", "anerobic", "anaerobic"]),
        ]
        
        for correct, variations in misspellings:
            for variant in variations:
                if variant != correct:
                    examples.append({
                        "input": f"solar farms in {variant}",
                        "output": {
                            "technology": "Photovoltaic",
                            "capacity_min_kw": 500,
                            "location": correct.capitalize(),
                            "postcode_patterns": self.uk_regions.get("Southern England", {}).get("postcodes", [])
                        },
                        "reasoning": f"Handle misspelling: {variant} -> {correct}"
                    })
        
        return examples
    
    def save_dataset(self, examples, output_dir):
        """Save the dataset with proper splits"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Shuffle
        random.shuffle(examples)
        
        # Split 80/10/10
        total = len(examples)
        train_size = int(total * 0.8)
        val_size = int(total * 0.1)
        
        train_data = examples[:train_size]
        val_data = examples[train_size:train_size + val_size]
        test_data = examples[train_size + val_size:]
        
        # Save files
        for name, data in [("train", train_data), ("validation", val_data), ("test", test_data)]:
            file_path = Path(output_dir) / f"{name}.jsonl"
            with open(file_path, 'w') as f:
                for item in data:
                    # Format for training
                    formatted = {
                        "input": item["input"],
                        "output": json.dumps(item["output"]) if isinstance(item["output"], dict) else item["output"],
                        "reasoning": item.get("reasoning", "")
                    }
                    f.write(json.dumps(formatted) + '\n')
            
            print(f"Saved {len(data)} examples to {file_path}")
        
        return train_size, val_size, len(test_data)

def main():
    """Generate the complete weekend training dataset"""
    
    print("=" * 60)
    print("Generating Weekend Training Dataset")
    print("=" * 60)
    
    generator = WeekendDatasetGenerator()
    
    all_examples = []
    
    # Generate all types of queries
    print("\nGenerating query types:")
    
    stages = [
        ("Base queries", generator.generate_base_queries),
        ("Complex queries", generator.generate_complex_queries),
        ("Aggregation queries", generator.generate_aggregation_queries),
        ("Comparison queries", generator.generate_comparison_queries),
        ("Geographic queries", generator.generate_geographic_queries),
        ("Business queries", generator.generate_business_queries),
        ("Specific queries", generator.generate_specific_queries),
        ("Edge cases", generator.generate_edge_cases)
    ]
    
    for name, func in stages:
        print(f"  Generating {name}...")
        examples = func()
        all_examples.extend(examples)
        print(f"    Generated {len(examples)} examples")
    
    # Generate variations
    print("\n  Generating natural language variations...")
    all_examples = generator.generate_natural_variations(all_examples[:5000])  # Vary first 5000
    print(f"    Total with variations: {len(all_examples)}")
    
    # Save dataset
    output_dir = "./weekend_training_data"
    train_size, val_size, test_size = generator.save_dataset(all_examples, output_dir)
    
    print("\n" + "=" * 60)
    print("Dataset Generation Complete!")
    print("=" * 60)
    print(f"\nTotal examples: {len(all_examples):,}")
    print(f"  Training: {train_size:,}")
    print(f"  Validation: {val_size:,}")
    print(f"  Test: {test_size:,}")
    print(f"\nSaved to: {output_dir}")
    
    # Show sample
    print("\nSample examples:")
    print("-" * 40)
    for i, ex in enumerate(random.sample(all_examples[:100], 3), 1):
        print(f"\n{i}. Input: {ex['input']}")
        print(f"   Output: {json.dumps(ex['output'], indent=3)}")
        print(f"   Reasoning: {ex.get('reasoning', 'N/A')[:100]}...")
    
    print("\n✅ Ready for weekend training!")
    print("\nNext steps:")
    print("1. Run: python3 weekend_training_pipeline.py")
    print("2. Let it train for 48-72 hours")
    print("3. Monitor progress via logs")
    print("4. Deploy the final model on Monday!")

if __name__ == "__main__":
    main()