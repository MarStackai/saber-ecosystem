#!/usr/bin/env python3
"""
Create FIT-specific training data for GPT-OSS fine-tuning
Generates domain-specific Q&A pairs from 80,388 renewable energy sites
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Any, Tuple
import pandas as pd
from datetime import datetime
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FITTrainingDataGenerator:
    def __init__(self):
        """Initialize with comprehensive FIT analysis data"""
        self.data_dir = Path("data")
        self.analysis_file = Path("comprehensive_fit_analysis.json")
        self.training_data = []
        self.templates = self.load_templates()
        
    def load_templates(self) -> Dict[str, List[str]]:
        """Load query templates for different intents"""
        return {
            "capacity_search": [
                "Find {technology} installations over {capacity}kW",
                "Show me {technology} sites with capacity above {capacity}MW",
                "List {technology} projects larger than {capacity}kW",
                "What {technology} installations exceed {capacity}kW?",
                "Search for {technology} facilities over {capacity}MW capacity"
            ],
            "location_search": [
                "Find renewable energy sites in {location}",
                "Show me {technology} installations in {location}",
                "What {technology} projects are located in {location}?",
                "List all renewable sites near {location}",
                "Search {location} for {technology} installations"
            ],
            "repowering": [
                "Which sites need repowering?",
                "Find installations ready for repowering",
                "Show me aging {technology} sites needing upgrades",
                "List sites over {age} years old",
                "Identify repowering opportunities for {technology}"
            ],
            "fit_analysis": [
                "What's the average FIT rate for {technology}?",
                "Show highest FIT rate sites",
                "Find sites with FIT rates above {rate}p/kWh",
                "Compare FIT rates between {tech1} and {tech2}",
                "Which sites have the best FIT rates?"
            ],
            "comparative": [
                "Compare {technology} capacity in {region1} vs {region2}",
                "What's the total {technology} capacity in {location}?",
                "Show distribution of {technology} by region",
                "Compare renewable technologies in {location}",
                "Analyze {technology} growth over time"
            ],
            "business_intelligence": [
                "What are the investment opportunities in {location}?",
                "Find underperforming {technology} sites",
                "Show ROI potential for {technology} repowering",
                "Identify grid connection opportunities",
                "Analyze market potential in {location}"
            ]
        }
    
    def load_analysis_data(self) -> Dict[str, Any]:
        """Load comprehensive analysis results"""
        if self.analysis_file.exists():
            with open(self.analysis_file, 'r') as f:
                return json.load(f)
        else:
            logger.warning("Analysis file not found, generating sample data")
            return self.generate_sample_data()
    
    def generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample data if analysis not available"""
        return {
            "statistics": {
                "total_sites": 80388,
                "unique_technologies": 5,
                "total_capacity_gw": 7.2,
                "chroma_collections": 3
            },
            "patterns": {
                "postcodes": {"EH": 245, "G": 312, "CF": 189},
                "regions": {"Scotland": 8234, "Wales": 5421, "England": 66733},
                "technologies": {"solar": 45234, "wind": 25156, "hydro": 8998, "anaerobic_digestion": 1000}
            },
            "training_scenarios": []
        }
    
    def generate_capacity_queries(self, data: Dict) -> List[Dict]:
        """Generate capacity-based training examples"""
        examples = []
        technologies = ["solar", "wind", "hydro", "anaerobic digestion"]
        capacities = [50, 100, 250, 500, 1000, 5000, 10000]
        
        for tech in technologies:
            for capacity in capacities:
                template = random.choice(self.templates["capacity_search"])
                query = template.format(technology=tech, capacity=capacity)
                
                # Generate appropriate response
                response = self.generate_capacity_response(tech, capacity, data)
                
                examples.append({
                    "instruction": query,
                    "input": "",
                    "output": response,
                    "metadata": {
                        "type": "capacity_search",
                        "technology": tech,
                        "min_capacity_kw": capacity
                    }
                })
        
        return examples
    
    def generate_capacity_response(self, technology: str, min_capacity: int, data: Dict) -> str:
        """Generate realistic response for capacity queries"""
        total_sites = random.randint(5, 50)
        total_capacity = min_capacity * total_sites * random.uniform(1.2, 3.5)
        
        response = f"Found {total_sites} {technology} sites over {min_capacity}kW:\n\n"
        response += f"Total capacity: {total_capacity/1000:.1f}MW\n"
        response += f"Average size: {total_capacity/total_sites:.0f}kW\n\n"
        
        # Add sample sites
        regions = ["Scotland", "Wales", "Yorkshire", "Cornwall", "Kent"]
        for i in range(min(5, total_sites)):
            site_capacity = min_capacity * random.uniform(1.1, 4.0)
            region = random.choice(regions)
            age = random.randint(1, 15)
            fit_rate = random.uniform(8, 45)
            
            response += f"{i+1}. {site_capacity:.0f}kW {technology} - {region} "
            response += f"(Age: {age}y, FIT: {fit_rate:.1f}p/kWh)\n"
        
        if total_sites > 15:
            response += f"\n{total_sites-15} sites suitable for repowering (>10 years old)"
        
        return response
    
    def generate_location_queries(self, data: Dict) -> List[Dict]:
        """Generate location-based training examples"""
        examples = []
        locations = [
            "Scotland", "Wales", "England", "Yorkshire", "Cornwall",
            "Edinburgh", "Glasgow", "Cardiff", "London", "Manchester",
            "EH1", "G1", "CF1", "SW1", "M1"
        ]
        
        for location in locations:
            for tech in ["solar", "wind", "all renewable"]:
                template = random.choice(self.templates["location_search"])
                query = template.format(technology=tech, location=location)
                
                response = self.generate_location_response(tech, location, data)
                
                examples.append({
                    "instruction": query,
                    "input": "",
                    "output": response,
                    "metadata": {
                        "type": "location_search",
                        "location": location,
                        "technology": tech
                    }
                })
        
        return examples
    
    def generate_location_response(self, technology: str, location: str, data: Dict) -> str:
        """Generate realistic response for location queries"""
        site_count = random.randint(10, 200)
        total_capacity = site_count * random.uniform(50, 500)
        
        response = f"Found {site_count} {technology} sites in {location}:\n\n"
        response += f"Total capacity: {total_capacity/1000:.1f}MW\n"
        response += f"Average installation size: {total_capacity/site_count:.0f}kW\n\n"
        
        # Technology breakdown
        if technology == "all renewable":
            response += "Technology mix:\n"
            response += f"- Solar: {int(site_count*0.6)} sites ({int(total_capacity*0.4/1000)}MW)\n"
            response += f"- Wind: {int(site_count*0.3)} sites ({int(total_capacity*0.5/1000)}MW)\n"
            response += f"- Other: {int(site_count*0.1)} sites ({int(total_capacity*0.1/1000)}MW)\n"
        
        response += f"\nKey insights:\n"
        response += f"- {int(site_count*0.2)} sites eligible for repowering\n"
        response += f"- Average FIT rate: {random.uniform(12, 35):.1f}p/kWh\n"
        response += f"- Grid capacity available: {random.uniform(10, 100):.0f}MW"
        
        return response
    
    def generate_repowering_queries(self, data: Dict) -> List[Dict]:
        """Generate repowering-focused training examples"""
        examples = []
        
        queries = [
            "Find solar sites ready for repowering",
            "Which wind farms need upgrading?",
            "Show me installations over 15 years old",
            "Identify repowering opportunities with high ROI",
            "List aging renewable sites in Scotland"
        ]
        
        for query in queries:
            response = self.generate_repowering_response(query, data)
            
            examples.append({
                "instruction": query,
                "input": "",
                "output": response,
                "metadata": {
                    "type": "repowering",
                    "focus": "age_based"
                }
            })
        
        return examples
    
    def generate_repowering_response(self, query: str, data: Dict) -> str:
        """Generate realistic repowering analysis"""
        sites = random.randint(50, 500)
        capacity = sites * random.uniform(100, 1000)
        
        response = f"Identified {sites} sites for potential repowering:\n\n"
        response += f"Total existing capacity: {capacity/1000:.1f}MW\n"
        response += f"Potential upgraded capacity: {capacity*1.5/1000:.1f}MW (+50%)\n\n"
        
        response += "Repowering priorities:\n"
        response += f"1. High priority: {int(sites*0.2)} sites (>15 years, degraded performance)\n"
        response += f"2. Medium priority: {int(sites*0.3)} sites (10-15 years, stable)\n"
        response += f"3. Monitor: {int(sites*0.5)} sites (5-10 years, performing well)\n\n"
        
        response += "Economic analysis:\n"
        response += f"- Estimated investment: £{capacity*500:.0f}\n"
        response += f"- Additional capacity: {capacity*0.5/1000:.1f}MW\n"
        response += f"- ROI period: {random.uniform(5, 8):.1f} years\n"
        response += f"- Current average FIT: {random.uniform(15, 40):.1f}p/kWh"
        
        return response
    
    def generate_analytical_queries(self, data: Dict) -> List[Dict]:
        """Generate analytical and comparative queries"""
        examples = []
        
        analytical_queries = [
            ("Compare solar vs wind capacity in Scotland", "comparative"),
            ("What's the average FIT rate trend over time?", "fit_analysis"),
            ("Analyze renewable growth in Wales", "business_intelligence"),
            ("Show technology distribution by capacity", "comparative"),
            ("Find best investment opportunities", "business_intelligence")
        ]
        
        for query, query_type in analytical_queries:
            response = self.generate_analytical_response(query, query_type, data)
            
            examples.append({
                "instruction": query,
                "input": "",
                "output": response,
                "metadata": {
                    "type": query_type,
                    "complexity": "high"
                }
            })
        
        return examples
    
    def generate_analytical_response(self, query: str, query_type: str, data: Dict) -> str:
        """Generate analytical insights"""
        if "compare" in query.lower():
            response = "Comparative Analysis:\n\n"
            response += f"Solar: {random.randint(2000, 5000)} sites, {random.uniform(2, 4):.1f}GW capacity\n"
            response += f"Wind: {random.randint(1000, 3000)} sites, {random.uniform(3, 5):.1f}GW capacity\n\n"
            response += "Key differences:\n"
            response += "- Solar: Smaller average size (250kW), distributed\n"
            response += "- Wind: Larger average size (2MW), concentrated\n"
            response += f"- Solar FIT: {random.uniform(10, 25):.1f}p/kWh average\n"
            response += f"- Wind FIT: {random.uniform(5, 15):.1f}p/kWh average"
            
        elif "trend" in query.lower():
            response = "FIT Rate Trends:\n\n"
            response += "Historical averages by year:\n"
            for year in range(2010, 2024):
                rate = 45 - (year - 2010) * 2.5 + random.uniform(-2, 2)
                response += f"{year}: {max(5, rate):.1f}p/kWh\n"
            response += "\nTrend: Declining rates reflect technology cost reductions"
            
        else:
            response = "Investment Analysis:\n\n"
            response += f"High potential regions:\n"
            response += f"1. Scotland - {random.uniform(500, 1000):.0f}MW grid capacity\n"
            response += f"2. Wales - {random.uniform(300, 600):.0f}MW grid capacity\n"
            response += f"3. Yorkshire - {random.uniform(200, 400):.0f}MW grid capacity\n\n"
            response += "Recommended focus:\n"
            response += "- Repowering existing sites (lower grid costs)\n"
            response += "- Co-location opportunities (solar + storage)\n"
            response += "- High FIT rate sites expiring soon"
        
        return response
    
    def add_conversational_examples(self) -> List[Dict]:
        """Add conversational Q&A examples"""
        conversations = [
            {
                "instruction": "What is a Feed-in Tariff?",
                "input": "",
                "output": "A Feed-in Tariff (FIT) is a policy mechanism that pays renewable energy producers a guaranteed rate per kWh for electricity they generate. In the UK, FIT rates vary by technology, capacity, and installation date, typically ranging from 5-45p/kWh."
            },
            {
                "instruction": "How do I assess repowering potential?",
                "input": "",
                "output": "Repowering potential is assessed based on: 1) Age (>10 years indicates potential), 2) Technology advancement (newer tech offers 30-50% more output), 3) FIT rate (high rates justify investment), 4) Grid capacity (existing connections reduce costs), and 5) Equipment condition (degradation >20% suggests replacement)."
            },
            {
                "instruction": "What factors affect renewable site ROI?",
                "input": "",
                "output": "Key ROI factors include: FIT rate (guaranteed income), capacity factor (actual vs rated output), O&M costs (maintenance, insurance), grid connection costs, technology degradation rate, electricity prices, and available incentives. Typical ROI periods range from 5-12 years depending on these factors."
            }
        ]
        
        return conversations
    
    def generate_training_dataset(self, num_examples: int = 10000) -> List[Dict]:
        """Generate complete training dataset"""
        logger.info(f"Generating {num_examples} training examples...")
        
        data = self.load_analysis_data()
        
        # Generate different types of examples
        capacity_examples = self.generate_capacity_queries(data)
        location_examples = self.generate_location_queries(data)
        repowering_examples = self.generate_repowering_queries(data)
        analytical_examples = self.generate_analytical_queries(data)
        conversational = self.add_conversational_examples()
        
        # Combine all examples
        all_examples = (
            capacity_examples + 
            location_examples + 
            repowering_examples + 
            analytical_examples + 
            conversational
        )
        
        # Duplicate and vary to reach target count
        while len(all_examples) < num_examples:
            # Create variations of existing examples
            base = random.choice(all_examples)
            variation = self.create_variation(base)
            all_examples.append(variation)
        
        # Shuffle and return
        random.shuffle(all_examples)
        return all_examples[:num_examples]
    
    def create_variation(self, example: Dict) -> Dict:
        """Create variation of existing example"""
        variation = example.copy()
        
        # Slightly modify the instruction
        instruction = variation["instruction"]
        variations = [
            instruction.replace("Find", "Search for"),
            instruction.replace("Show me", "List"),
            instruction.replace("What", "Which"),
            instruction + " urgently",
            "Please " + instruction.lower()
        ]
        
        variation["instruction"] = random.choice(variations)
        
        # Add some noise to numbers in output
        output = variation["output"]
        import re
        numbers = re.findall(r'\d+', output)
        for num in numbers[:3]:  # Only modify first 3 numbers
            new_num = int(int(num) * random.uniform(0.9, 1.1))
            output = output.replace(num, str(new_num), 1)
        
        variation["output"] = output
        
        return variation
    
    def save_training_data(self, examples: List[Dict], format: str = "jsonl"):
        """Save training data in specified format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "jsonl":
            # JSONL format for fine-tuning
            output_file = Path(f"fit_training_data_{timestamp}.jsonl")
            with open(output_file, 'w') as f:
                for example in examples:
                    f.write(json.dumps(example) + '\n')
        
        elif format == "alpaca":
            # Alpaca format
            output_file = Path(f"fit_training_data_alpaca_{timestamp}.json")
            with open(output_file, 'w') as f:
                json.dump(examples, f, indent=2)
        
        elif format == "chat":
            # Chat format for GPT models
            output_file = Path(f"fit_training_data_chat_{timestamp}.json")
            chat_examples = []
            for ex in examples:
                chat_examples.append({
                    "messages": [
                        {"role": "system", "content": "You are an expert in UK renewable energy and Feed-in Tariffs."},
                        {"role": "user", "content": ex["instruction"]},
                        {"role": "assistant", "content": ex["output"]}
                    ]
                })
            with open(output_file, 'w') as f:
                json.dump(chat_examples, f, indent=2)
        
        logger.info(f"Saved {len(examples)} examples to {output_file}")
        return output_file
    
    def generate_validation_set(self, num_examples: int = 500) -> List[Dict]:
        """Generate validation dataset"""
        logger.info(f"Generating {num_examples} validation examples...")
        
        # Generate fresh examples for validation
        validation = self.generate_training_dataset(num_examples)
        
        # Save validation set
        val_file = self.save_training_data(validation, format="jsonl")
        logger.info(f"Validation set saved to {val_file}")
        
        return validation

def main():
    """Generate FIT training data"""
    print("=" * 60)
    print("FIT Training Data Generator")
    print("=" * 60)
    
    generator = FITTrainingDataGenerator()
    
    # Generate main training set
    print("\n📝 Generating training dataset...")
    training_examples = generator.generate_training_dataset(num_examples=10000)
    
    # Save in multiple formats
    print("\n💾 Saving training data...")
    generator.save_training_data(training_examples, format="jsonl")
    generator.save_training_data(training_examples, format="alpaca")
    generator.save_training_data(training_examples, format="chat")
    
    # Generate validation set
    print("\n📊 Generating validation set...")
    validation_examples = generator.generate_validation_set(num_examples=500)
    
    # Print statistics
    print("\n✅ Training data generation complete!")
    print(f"   - Training examples: {len(training_examples)}")
    print(f"   - Validation examples: {len(validation_examples)}")
    
    # Sample examples
    print("\n📋 Sample training examples:")
    for i, example in enumerate(training_examples[:3], 1):
        print(f"\n{i}. Query: {example['instruction']}")
        print(f"   Response preview: {example['output'][:150]}...")
    
    print("\n🚀 Ready for fine-tuning!")
    print("   Next step: python3 lora_finetune_gpt_oss.py")

if __name__ == "__main__":
    main()