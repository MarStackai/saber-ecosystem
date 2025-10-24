#!/usr/bin/env python3
"""
Generate LoRA training data from FIT database for query understanding
"""

import json
import random
from typing import List, Dict, Any
import chromadb
from datetime import datetime

class LoRATrainingDataGenerator:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_collection("fit_licenses_nondomestic")
        
        # Get sample data to understand the structure
        self.sample_data = self.collection.get(limit=100)
        
        # UK regions and their postcodes
        self.regions = {
            "Yorkshire": ["YO", "HU", "DN", "HD", "WF", "LS", "BD", "HX", "S"],
            "Berkshire": ["RG", "SL"],
            "Cornwall": ["TR", "PL"],
            "Scotland": ["AB", "DD", "EH", "FK", "G", "IV", "KA", "KW", "KY", "ML", "PA", "PH", "TD", "ZE"],
            "Wales": ["CF", "LL", "NP", "SA", "SY", "LD"],
            "East Anglia": ["CB", "CM", "CO", "IP", "NR", "PE", "SG"],
            "London": ["E", "EC", "N", "NW", "SE", "SW", "W", "WC"],
            "North West": ["BB", "BL", "CA", "CH", "CW", "FY", "L", "LA", "M", "OL", "PR", "SK", "WA", "WN"],
            "South West": ["BA", "BH", "BS", "DT", "EX", "GL", "PL", "SN", "SP", "TA", "TQ", "TR"],
            "Midlands": ["B", "CV", "DE", "DY", "LE", "NG", "NN", "ST", "WR", "WS", "WV"],
        }
        
        # Technology types in the database
        self.technologies = ["Wind", "Photovoltaic", "Hydro", "Anaerobic digestion", "Micro CHP"]
        
        # Capacity descriptors
        self.capacity_descriptors = {
            "small": (0, 50),
            "medium": (50, 500),
            "large": (500, 5000),
            "very large": (5000, 50000),
            "utility scale": (1000, 50000),
        }
        
    def generate_training_examples(self, num_examples: int = 1000) -> List[Dict[str, Any]]:
        """Generate diverse training examples for LoRA fine-tuning"""
        examples = []
        
        # Query templates
        templates = [
            # Simple location queries
            ("wind farms in {location}", "location_tech"),
            ("solar installations in {location}", "location_tech"),
            ("{technology} sites in {location}", "location_tech"),
            
            # Capacity queries
            ("{technology} over {capacity}kw", "capacity_tech"),
            ("{size} {technology} installations", "size_tech"),
            ("{technology} between {min_capacity} and {max_capacity} kw", "range_tech"),
            
            # Combined queries
            ("{size} {technology} in {location}", "combined"),
            ("{technology} over {capacity}kw in {location}", "combined_specific"),
            ("all {technology} farms in {location} over {capacity}kw", "combined_all"),
            
            # Expiry queries
            ("{technology} expiring soon", "expiry"),
            ("{technology} in {location} expiring within {years} years", "expiry_location"),
            ("urgent {technology} opportunities in {location}", "urgent"),
            
            # Aggregation queries
            ("total {technology} capacity in {location}", "aggregate"),
            ("count of {technology} installations", "count"),
            ("average size of {technology} in {location}", "average"),
            
            # Geographic queries
            ("wind farms within {radius} miles of {location}", "geographic"),
            ("{technology} near {postcode}", "postcode"),
            
            # Business queries
            ("best repowering opportunities in {location}", "business"),
            ("{technology} sites with FIT ending in {year}", "fit_ending"),
            ("largest {technology} installations", "top_n"),
        ]
        
        for _ in range(num_examples):
            template, query_type = random.choice(templates)
            example = self._create_example(template, query_type)
            if example:
                examples.append(example)
        
        return examples
    
    def _create_example(self, template: str, query_type: str) -> Dict[str, Any]:
        """Create a single training example"""
        
        # Randomly select parameters
        location = random.choice(list(self.regions.keys()))
        technology = random.choice(self.technologies)
        size_name, (min_cap, max_cap) = random.choice(list(self.capacity_descriptors.items()))
        capacity = random.randint(50, 5000)
        min_capacity = random.randint(50, 1000)
        max_capacity = random.randint(min_capacity + 100, 5000)
        years = random.choice([1, 2, 3, 5, 10])
        year = random.randint(2024, 2035)
        radius = random.choice([5, 10, 20, 30, 50])
        postcode = random.choice(self.regions[location]) + str(random.randint(1, 99))
        
        # Fill in the template
        query = template.format(
            location=location,
            technology=technology.lower(),
            size=size_name,
            capacity=capacity,
            min_capacity=min_capacity,
            max_capacity=max_capacity,
            years=years,
            year=year,
            radius=radius,
            postcode=postcode
        )
        
        # Generate the structured output based on query type
        output = {
            "action": "search",
            "filters": {}
        }
        
        if "{technology}" in template:
            output["filters"]["technology"] = technology
        
        if "{location}" in template:
            output["filters"]["location"] = location
            output["filters"]["postcode_patterns"] = self.regions[location]
        
        if "{capacity}" in template:
            output["filters"]["capacity_min_kw"] = capacity
        
        if "{size}" in template:
            output["filters"]["capacity_min_kw"] = min_cap
            output["filters"]["capacity_max_kw"] = max_cap
        
        if "{min_capacity}" in template and "{max_capacity}" in template:
            output["filters"]["capacity_min_kw"] = min_capacity
            output["filters"]["capacity_max_kw"] = max_capacity
        
        if "expiring" in query or "{years}" in template:
            output["filters"]["fit_remaining_max_years"] = years
        
        if "{year}" in template:
            output["filters"]["fit_end_year"] = year
        
        if "{radius}" in template:
            output["filters"]["radius_miles"] = radius
            output["filters"]["center_location"] = location
        
        if "{postcode}" in template:
            output["filters"]["postcode"] = postcode
        
        # Set action type
        if "total" in query or "count" in query or "average" in query:
            output["action"] = "aggregate"
            output["aggregation_type"] = "total" if "total" in query else "count" if "count" in query else "average"
        elif "near" in query or "within" in query:
            output["action"] = "geographic_search"
        elif "opportunities" in query or "repowering" in query:
            output["action"] = "business_analysis"
        
        return {
            "instruction": "Parse this FIT database query into structured filters",
            "input": query,
            "output": json.dumps(output, indent=2)
        }
    
    def save_training_data(self, examples: List[Dict], filename: str = "lora_training_data.jsonl"):
        """Save training data in JSONL format for LoRA fine-tuning"""
        with open(filename, 'w') as f:
            for example in examples:
                f.write(json.dumps(example) + '\n')
        print(f"Saved {len(examples)} training examples to {filename}")
    
    def generate_test_queries(self) -> List[str]:
        """Generate test queries to evaluate the model"""
        test_queries = [
            "wind sites over 100kw in berkshire",
            "large solar farms in Yorkshire",
            "all hydro installations in Scotland",
            "wind turbines expiring within 2 years",
            "solar panels over 500kw in East Anglia",
            "total wind capacity in Wales",
            "count of anaerobic digestion sites",
            "wind farms within 20 miles of York",
            "best repowering opportunities in Cornwall",
            "photovoltaic installations ending FIT in 2025",
            "small wind turbines in the Midlands",
            "utility scale solar in the South West",
            "average size of wind farms in Scotland",
            "hydro sites near AB42",
            "urgent opportunities for wind acquisition",
        ]
        return test_queries


def main():
    generator = LoRATrainingDataGenerator()
    
    # Generate training examples
    print("Generating LoRA training data...")
    training_examples = generator.generate_training_examples(1000)
    
    # Save training data
    generator.save_training_data(training_examples)
    
    # Show some examples
    print("\nSample training examples:")
    for example in training_examples[:3]:
        print(f"\nQuery: {example['input']}")
        print(f"Parsed Output: {example['output']}")
    
    # Generate test queries
    test_queries = generator.generate_test_queries()
    print(f"\n{len(test_queries)} test queries generated for evaluation")


if __name__ == "__main__":
    main()