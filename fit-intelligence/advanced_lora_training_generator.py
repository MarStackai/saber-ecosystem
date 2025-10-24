#!/usr/bin/env python3
"""
Advanced LoRA Training Data Generator for FIT Intelligence
Implements comprehensive training plan with 4,500+ examples
"""

import json
import random
import re
import chromadb
from typing import List, Dict, Any, Tuple
from datetime import datetime
import logging
from itertools import product, combinations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedTrainingGenerator:
    """
    Generates comprehensive training data for LoRA fine-tuning
    Covers all edge cases and query patterns
    """
    
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_collection("fit_licenses_nondomestic")
        
        # Analyze actual data distribution
        self._analyze_database()
        
        # Define comprehensive mappings
        self._setup_mappings()
        
        # Track generated examples to avoid duplicates
        self.generated_examples = set()
        
    def _analyze_database(self):
        """Analyze actual database for realistic training data"""
        logger.info("Analyzing database distribution...")
        
        sample = self.collection.get(limit=1000)
        
        self.actual_technologies = set()
        self.actual_locations = set()
        self.actual_postcodes = set()
        self.capacity_distribution = []
        self.fit_ids = []
        
        for metadata in sample['metadatas']:
            if metadata:
                if metadata.get('technology'):
                    self.actual_technologies.add(metadata['technology'])
                if metadata.get('local_authority'):
                    self.actual_locations.add(metadata['local_authority'])
                if metadata.get('postcode'):
                    pc = metadata['postcode'][:2] if metadata['postcode'] else None
                    if pc:
                        self.actual_postcodes.add(pc)
                if metadata.get('capacity_kw'):
                    self.capacity_distribution.append(metadata['capacity_kw'])
                if metadata.get('fit_id'):
                    self.fit_ids.append(metadata['fit_id'])
        
        logger.info(f"Found {len(self.actual_technologies)} technologies")
        logger.info(f"Found {len(self.actual_locations)} locations")
        logger.info(f"Found {len(self.actual_postcodes)} postcode areas")
        
    def _setup_mappings(self):
        """Setup comprehensive language mappings"""
        
        # Technology synonyms
        self.tech_synonyms = {
            'Wind': [
                'wind', 'wind farm', 'wind farms', 'wind turbine', 'wind turbines',
                'turbine', 'turbines', 'wind power', 'wind energy', 'wind installation',
                'wind site', 'wind sites', 'onshore wind', 'wind generation'
            ],
            'Photovoltaic': [
                'solar', 'solar panel', 'solar panels', 'solar farm', 'solar farms',
                'photovoltaic', 'pv', 'PV', 'solar pv', 'solar power', 'solar energy',
                'solar installation', 'solar site', 'solar sites', 'solar array',
                'ground mounted solar', 'rooftop solar', 'solar generation'
            ],
            'Hydro': [
                'hydro', 'hydroelectric', 'water turbine', 'water power', 'hydro power',
                'hydropower', 'water energy', 'hydro turbine', 'hydro installation',
                'small hydro', 'micro hydro', 'run of river'
            ],
            'Anaerobic digestion': [
                'anaerobic digestion', 'AD', 'anaerobic', 'digestion', 'biogas',
                'biomass', 'bio energy', 'AD plant', 'digester', 'anaerobic digester',
                'biogas plant', 'organic waste'
            ],
            'Micro CHP': [
                'CHP', 'combined heat power', 'combined heat and power', 'cogeneration',
                'micro CHP', 'micro-CHP', 'heat and power', 'combined heat',
                'cogen', 'CHP unit', 'CHP plant'
            ]
        }
        
        # Location mappings with variations
        self.location_mappings = {
            'Yorkshire': {
                'postcodes': ['YO', 'HU', 'DN', 'HD', 'WF', 'LS', 'BD', 'HX', 'S'],
                'variations': ['Yorkshire', 'Yorks', 'North Yorkshire', 'South Yorkshire',
                              'West Yorkshire', 'East Yorkshire', 'Yorkshire and Humber']
            },
            'Berkshire': {
                'postcodes': ['RG', 'SL'],
                'variations': ['Berkshire', 'Berks', 'Royal County of Berkshire',
                              'Reading area', 'Slough area', 'West Berkshire']
            },
            'Scotland': {
                'postcodes': ['AB', 'DD', 'DG', 'EH', 'FK', 'G', 'IV', 'KA', 'KW', 'KY',
                             'ML', 'PA', 'PH', 'TD', 'ZE'],
                'variations': ['Scotland', 'Scottish', 'Highlands', 'Lowlands',
                              'Scottish Highlands', 'Central Scotland', 'North Scotland']
            },
            'Wales': {
                'postcodes': ['CF', 'LL', 'NP', 'SA', 'SY', 'LD'],
                'variations': ['Wales', 'Welsh', 'North Wales', 'South Wales',
                              'Mid Wales', 'West Wales']
            },
            'London': {
                'postcodes': ['E', 'EC', 'N', 'NW', 'SE', 'SW', 'W', 'WC'],
                'variations': ['London', 'Greater London', 'Central London',
                              'Inner London', 'Outer London', 'London area']
            },
            'Birmingham': {
                'postcodes': ['B'],
                'variations': ['Birmingham', 'Brum', 'West Midlands', 'Birmingham area']
            }
        }
        
        # Capacity descriptors
        self.capacity_descriptors = {
            'small': (0, 50),
            'medium': (50, 500),
            'large': (500, 5000),
            'very large': (5000, 50000),
            'utility scale': (1000, 50000),
            'commercial': (100, 5000),
            'industrial': (500, 10000),
            'micro': (0, 10),
            'mini': (10, 100)
        }
        
        # Query intents
        self.query_intents = [
            'find', 'show', 'list', 'get', 'search for', 'look for',
            'what are', 'which', 'display', 'return', 'give me',
            'I need', 'I want', 'show me', 'find me', 'get me'
        ]
        
        # Temporal expressions
        self.temporal_expressions = {
            'expiring soon': {'fit_remaining_max_years': 2},
            'expiring': {'fit_remaining_max_years': 5},
            'ending soon': {'fit_remaining_max_years': 3},
            'FIT ending': {'fit_remaining_max_years': 5},
            'coming off FIT': {'fit_remaining_max_years': 5},
            'recent': {'commissioned_after_year': 2020},
            'old': {'commissioned_before_year': 2015},
            'mature': {'age_min_years': 10}
        }
    
    def generate_basic_technology_queries(self, count: int = 500) -> List[Dict]:
        """Generate basic technology identification queries"""
        examples = []
        
        for tech, synonyms in self.tech_synonyms.items():
            for synonym in synonyms:
                for intent in self.query_intents[:10]:
                    query = f"{intent} all {synonym}"
                    
                    example = {
                        "instruction": "Parse this FIT database query into structured filters",
                        "input": query,
                        "output": json.dumps({
                            "technology": tech
                        }, indent=2)
                    }
                    
                    # Avoid duplicates
                    query_hash = hash(query.lower())
                    if query_hash not in self.generated_examples:
                        examples.append(example)
                        self.generated_examples.add(query_hash)
                    
                    if len(examples) >= count:
                        return examples
        
        return examples
    
    def generate_location_mapping_queries(self, count: int = 1000) -> List[Dict]:
        """Generate location to postcode mapping queries"""
        examples = []
        
        for location, data in self.location_mappings.items():
            for variation in data['variations']:
                for tech in self.actual_technologies:
                    # Simple location query
                    query = f"{tech.lower()} in {variation}"
                    example = {
                        "instruction": "Parse this FIT database query into structured filters",
                        "input": query,
                        "output": json.dumps({
                            "technology": tech,
                            "location": location,
                            "postcode_patterns": data['postcodes']
                        }, indent=2)
                    }
                    
                    query_hash = hash(query.lower())
                    if query_hash not in self.generated_examples:
                        examples.append(example)
                        self.generated_examples.add(query_hash)
                    
                    # With intent
                    for intent in random.sample(self.query_intents, 3):
                        query = f"{intent} {tech.lower()} installations in {variation}"
                        example = {
                            "instruction": "Parse this FIT database query into structured filters",
                            "input": query,
                            "output": json.dumps({
                                "technology": tech,
                                "location": location,
                                "postcode_patterns": data['postcodes']
                            }, indent=2)
                        }
                        
                        query_hash = hash(query.lower())
                        if query_hash not in self.generated_examples:
                            examples.append(example)
                            self.generated_examples.add(query_hash)
                    
                    if len(examples) >= count:
                        return examples
        
        return examples
    
    def generate_capacity_filtering_queries(self, count: int = 500) -> List[Dict]:
        """Generate capacity filtering queries with various expressions"""
        examples = []
        
        capacity_expressions = [
            ("over {}", lambda x: {"capacity_min_kw": x}),
            ("above {}", lambda x: {"capacity_min_kw": x}),
            ("greater than {}", lambda x: {"capacity_min_kw": x}),
            ("more than {}", lambda x: {"capacity_min_kw": x}),
            ("at least {}", lambda x: {"capacity_min_kw": x}),
            ("minimum {}", lambda x: {"capacity_min_kw": x}),
            ("under {}", lambda x: {"capacity_max_kw": x}),
            ("below {}", lambda x: {"capacity_max_kw": x}),
            ("less than {}", lambda x: {"capacity_max_kw": x}),
            ("up to {}", lambda x: {"capacity_max_kw": x}),
            ("maximum {}", lambda x: {"capacity_max_kw": x}),
            ("between {} and {}", lambda x, y: {"capacity_min_kw": x, "capacity_max_kw": y}),
            ("from {} to {}", lambda x, y: {"capacity_min_kw": x, "capacity_max_kw": y}),
            ("{} to {} range", lambda x, y: {"capacity_min_kw": x, "capacity_max_kw": y})
        ]
        
        # Test capacities
        test_capacities = [10, 50, 100, 250, 500, 1000, 5000]
        units = ['kw', 'kW', 'KW', 'kilowatts', 'kilowatt']
        
        for tech in self.actual_technologies:
            tech_lower = tech.lower()
            
            for expr_template, filter_func in capacity_expressions:
                for capacity in test_capacities:
                    for unit in units:
                        if '{}' in expr_template and expr_template.count('{}') == 1:
                            # Single value expression
                            expr = expr_template.format(f"{capacity}{unit}")
                            query = f"{tech_lower} {expr}"
                            
                            example = {
                                "instruction": "Parse this FIT database query into structured filters",
                                "input": query,
                                "output": json.dumps({
                                    "technology": tech,
                                    **filter_func(capacity)
                                }, indent=2)
                            }
                        elif expr_template.count('{}') == 2:
                            # Range expression
                            cap2 = capacity * 5
                            expr = expr_template.format(f"{capacity}{unit}", f"{cap2}{unit}")
                            query = f"{tech_lower} {expr}"
                            
                            example = {
                                "instruction": "Parse this FIT database query into structured filters",
                                "input": query,
                                "output": json.dumps({
                                    "technology": tech,
                                    **filter_func(capacity, cap2)
                                }, indent=2)
                            }
                        else:
                            continue
                        
                        query_hash = hash(query.lower())
                        if query_hash not in self.generated_examples:
                            examples.append(example)
                            self.generated_examples.add(query_hash)
                        
                        if len(examples) >= count:
                            return examples
        
        # Add MW conversions
        for tech in self.actual_technologies:
            for mw in [0.5, 1, 2, 5, 10]:
                query = f"{tech.lower()} over {mw}MW"
                example = {
                    "instruction": "Parse this FIT database query into structured filters",
                    "input": query,
                    "output": json.dumps({
                        "technology": tech,
                        "capacity_min_kw": mw * 1000
                    }, indent=2)
                }
                examples.append(example)
        
        return examples[:count]
    
    def generate_combined_queries(self, count: int = 1000) -> List[Dict]:
        """Generate complex multi-filter queries"""
        examples = []
        
        # The famous failing query
        examples.append({
            "instruction": "Parse this FIT database query into structured filters",
            "input": "wind sites over 100kw in berkshire",
            "output": json.dumps({
                "technology": "Wind",
                "capacity_min_kw": 100,
                "location": "Berkshire",
                "postcode_patterns": ["RG", "SL"]
            }, indent=2)
        })
        
        # Generate combinations
        for tech, tech_synonyms in self.tech_synonyms.items():
            for location, loc_data in self.location_mappings.items():
                for capacity in [50, 100, 500, 1000]:
                    # Various query patterns
                    patterns = [
                        f"{random.choice(tech_synonyms)} over {capacity}kw in {random.choice(loc_data['variations'])}",
                        f"find {random.choice(tech_synonyms)} installations above {capacity}kW in {random.choice(loc_data['variations'])}",
                        f"all {random.choice(tech_synonyms)} in {random.choice(loc_data['variations'])} with capacity over {capacity}kw",
                        f"{random.choice(loc_data['variations'])} {random.choice(tech_synonyms)} larger than {capacity}kw",
                        f"show me {random.choice(tech_synonyms)} sites in {random.choice(loc_data['variations'])} above {capacity} kilowatts"
                    ]
                    
                    for pattern in patterns:
                        example = {
                            "instruction": "Parse this FIT database query into structured filters",
                            "input": pattern,
                            "output": json.dumps({
                                "technology": tech,
                                "capacity_min_kw": capacity,
                                "location": location,
                                "postcode_patterns": loc_data['postcodes']
                            }, indent=2)
                        }
                        
                        query_hash = hash(pattern.lower())
                        if query_hash not in self.generated_examples:
                            examples.append(example)
                            self.generated_examples.add(query_hash)
                        
                        if len(examples) >= count:
                            return examples
        
        return examples
    
    def generate_fit_rate_queries(self, count: int = 300) -> List[Dict]:
        """Generate FIT rate and financial queries"""
        examples = []
        
        # FIT ID queries
        for fit_id in random.sample(self.fit_ids, min(100, len(self.fit_ids))):
            queries = [
                f"what is the fit rate for fit id {fit_id}",
                f"fit rate for {fit_id}",
                f"show me the tariff for fit {fit_id}",
                f"what's the rate for installation {fit_id}",
                f"revenue for fit id {fit_id}"
            ]
            
            for query in queries:
                example = {
                    "instruction": "Parse this FIT database query into structured filters",
                    "input": query,
                    "output": json.dumps({
                        "query_type": "fit_rate_lookup",
                        "fit_id": fit_id,
                        "include_rate": True,
                        "include_revenue": True
                    }, indent=2)
                }
                examples.append(example)
        
        # Technology rate queries
        for tech in self.actual_technologies:
            for location in list(self.location_mappings.keys())[:5]:
                query = f"what are the fit rates for {tech.lower()} in {location}"
                example = {
                    "instruction": "Parse this FIT database query into structured filters",
                    "input": query,
                    "output": json.dumps({
                        "query_type": "fit_rate_analysis",
                        "technology": tech,
                        "location": location,
                        "postcode_patterns": self.location_mappings[location]['postcodes']
                    }, indent=2)
                }
                examples.append(example)
        
        return examples[:count]
    
    def generate_regional_calculation_queries(self, count: int = 300) -> List[Dict]:
        """Generate regional capacity factor and calculation queries"""
        examples = []
        
        patterns = [
            "show regional adjusted revenue for {tech} in {location}",
            "calculate {location} capacity factors for {tech}",
            "what's the regional performance of {tech} in {location}",
            "{tech} with regional calculations in {location}",
            "compare simple vs regional revenue for {tech} in {location}"
        ]
        
        for pattern in patterns:
            for tech in self.actual_technologies:
                for location in self.location_mappings.keys():
                    query = pattern.format(tech=tech.lower(), location=location)
                    
                    example = {
                        "instruction": "Parse this FIT database query into structured filters",
                        "input": query,
                        "output": json.dumps({
                            "query_type": "regional_analysis",
                            "technology": tech,
                            "location": location,
                            "postcode_patterns": self.location_mappings[location]['postcodes'],
                            "include_regional": True,
                            "include_revenue": True
                        }, indent=2)
                    }
                    
                    examples.append(example)
                    
                    if len(examples) >= count:
                        return examples
        
        return examples
    
    def generate_aggregation_queries(self, count: int = 200) -> List[Dict]:
        """Generate aggregation and statistical queries"""
        examples = []
        
        agg_patterns = [
            ("total {tech} capacity in {location}", "sum_capacity"),
            ("count of {tech} installations in {location}", "count"),
            ("average size of {tech} in {location}", "average_capacity"),
            ("largest {tech} in {location}", "max_capacity"),
            ("smallest {tech} in {location}", "min_capacity"),
            ("how many {tech} sites in {location}", "count"),
            ("sum of all {tech} capacity in {location}", "sum_capacity")
        ]
        
        for pattern, agg_type in agg_patterns:
            for tech in self.actual_technologies:
                for location in list(self.location_mappings.keys())[:5]:
                    query = pattern.format(tech=tech.lower(), location=location)
                    
                    example = {
                        "instruction": "Parse this FIT database query into structured filters",
                        "input": query,
                        "output": json.dumps({
                            "query_type": "aggregation",
                            "aggregation_type": agg_type,
                            "technology": tech,
                            "location": location,
                            "postcode_patterns": self.location_mappings[location]['postcodes']
                        }, indent=2)
                    }
                    
                    examples.append(example)
                    
                    if len(examples) >= count:
                        return examples
        
        return examples
    
    def generate_comparison_queries(self, count: int = 200) -> List[Dict]:
        """Generate technology comparison queries"""
        examples = []
        
        comparison_patterns = [
            "compare {tech1} and {tech2} in {location}",
            "which is better {tech1} or {tech2} in {location}",
            "{tech1} vs {tech2} performance in {location}",
            "compare all technologies in {location}",
            "best technology for {location}"
        ]
        
        tech_pairs = list(combinations(list(self.actual_technologies), 2))
        
        for pattern in comparison_patterns:
            if '{tech1}' in pattern:
                for tech1, tech2 in tech_pairs[:20]:
                    for location in list(self.location_mappings.keys())[:3]:
                        query = pattern.format(
                            tech1=tech1.lower(),
                            tech2=tech2.lower(),
                            location=location
                        )
                        
                        example = {
                            "instruction": "Parse this FIT database query into structured filters",
                            "input": query,
                            "output": json.dumps({
                                "query_type": "comparison",
                                "technologies": [tech1, tech2],
                                "location": location,
                                "postcode_patterns": self.location_mappings[location]['postcodes']
                            }, indent=2)
                        }
                        
                        examples.append(example)
            else:
                for location in self.location_mappings.keys():
                    query = pattern.format(location=location)
                    
                    example = {
                        "instruction": "Parse this FIT database query into structured filters",
                        "input": query,
                        "output": json.dumps({
                            "query_type": "comparison",
                            "compare_all": True,
                            "location": location,
                            "postcode_patterns": self.location_mappings[location]['postcodes']
                        }, indent=2)
                    }
                    
                    examples.append(example)
            
            if len(examples) >= count:
                return examples
        
        return examples
    
    def generate_business_queries(self, count: int = 500) -> List[Dict]:
        """Generate business-focused queries"""
        examples = []
        
        business_patterns = [
            "{tech} sites good for repowering in {location}",
            "PPA opportunities for {tech} in {location}",
            "{tech} installations expiring soon in {location}",
            "acquisition targets {tech} {location}",
            "investment opportunities {tech} {location}",
            "sites coming off FIT in {location}",
            "{tech} with expiring subsidies in {location}",
            "repowering candidates in {location}"
        ]
        
        for pattern in business_patterns:
            for tech in self.actual_technologies:
                for location in self.location_mappings.keys():
                    query = pattern.format(tech=tech.lower(), location=location)
                    
                    example = {
                        "instruction": "Parse this FIT database query into structured filters",
                        "input": query,
                        "output": json.dumps({
                            "query_type": "business_opportunity",
                            "technology": tech if '{tech}' in pattern else None,
                            "location": location,
                            "postcode_patterns": self.location_mappings[location]['postcodes'],
                            "fit_remaining_max_years": 10,
                            "include_revenue": True,
                            "include_regional": True
                        }, indent=2)
                    }
                    
                    # Remove None values
                    output = json.loads(example["output"])
                    output = {k: v for k, v in output.items() if v is not None}
                    example["output"] = json.dumps(output, indent=2)
                    
                    examples.append(example)
                    
                    if len(examples) >= count:
                        return examples
        
        return examples
    
    def generate_edge_cases(self, count: int = 200) -> List[Dict]:
        """Generate edge cases and difficult queries"""
        examples = []
        
        edge_cases = [
            # Typos and misspellings
            ("wnd farms in yorkshir", {
                "technology": "Wind",
                "location": "Yorkshire",
                "postcode_patterns": ["YO", "HU", "DN", "HD", "WF", "LS", "BD", "HX", "S"]
            }),
            
            # Mixed units
            ("solar between 0.5MW and 2 megawatts", {
                "technology": "Photovoltaic",
                "capacity_min_kw": 500,
                "capacity_max_kw": 2000
            }),
            
            # Colloquial expressions
            ("big wind farms up north", {
                "technology": "Wind",
                "capacity_min_kw": 500,
                "location": "Northern England",
                "postcode_patterns": ["CA", "DH", "DL", "HG", "LA", "NE", "TS"]
            }),
            
            # Multiple technologies
            ("wind and solar in Scotland", {
                "technologies": ["Wind", "Photovoltaic"],
                "location": "Scotland",
                "postcode_patterns": ["AB", "DD", "DG", "EH", "FK", "G", "IV", "KA", "KW", "KY", "ML", "PA", "PH", "TD", "ZE"]
            }),
            
            # Negative queries
            ("not solar", {
                "exclude_technology": "Photovoltaic"
            }),
            
            # Very specific queries
            ("335kW wind turbine in Ryedale YO17", {
                "technology": "Wind",
                "capacity_kw": 335,
                "location": "Ryedale",
                "postcode": "YO17"
            })
        ]
        
        for input_query, output_filters in edge_cases:
            example = {
                "instruction": "Parse this FIT database query into structured filters",
                "input": input_query,
                "output": json.dumps(output_filters, indent=2)
            }
            examples.append(example)
        
        # Generate more edge cases
        while len(examples) < count:
            # Random complex query
            tech = random.choice(list(self.actual_technologies))
            location = random.choice(list(self.location_mappings.keys()))
            capacity = random.choice([50, 100, 500, 1000])
            
            # Add complexity
            complexities = [
                f"urgent {tech.lower()} over {capacity}kw in {location} for acquisition",
                f"all {tech.lower()} except those under {capacity}kw in {location}",
                f"top 10 {tech.lower()} by size in {location}",
                f"{location} {tech.lower()} commissioned after 2015 over {capacity}kw"
            ]
            
            query = random.choice(complexities)
            
            # Parse based on pattern
            output = {
                "technology": tech,
                "location": location,
                "postcode_patterns": self.location_mappings[location]['postcodes']
            }
            
            if "over" in query or "except those under" in query:
                output["capacity_min_kw"] = capacity
            if "urgent" in query or "acquisition" in query:
                output["fit_remaining_max_years"] = 5
                output["query_type"] = "business_opportunity"
            if "top 10" in query:
                output["limit"] = 10
                output["sort_by"] = "capacity_desc"
            if "after 2015" in query:
                output["commissioned_after_year"] = 2015
            
            example = {
                "instruction": "Parse this FIT database query into structured filters",
                "input": query,
                "output": json.dumps(output, indent=2)
            }
            
            examples.append(example)
        
        return examples[:count]
    
    def generate_complete_dataset(self) -> Dict[str, Any]:
        """Generate the complete training dataset"""
        logger.info("Generating comprehensive training dataset...")
        
        all_examples = []
        
        # Generate each category
        categories = [
            ("Basic Technology", self.generate_basic_technology_queries(500)),
            ("Location Mapping", self.generate_location_mapping_queries(1000)),
            ("Capacity Filtering", self.generate_capacity_filtering_queries(500)),
            ("Combined Queries", self.generate_combined_queries(1000)),
            ("FIT Rate Queries", self.generate_fit_rate_queries(300)),
            ("Regional Calculations", self.generate_regional_calculation_queries(300)),
            ("Aggregations", self.generate_aggregation_queries(200)),
            ("Comparisons", self.generate_comparison_queries(200)),
            ("Business Queries", self.generate_business_queries(500)),
            ("Edge Cases", self.generate_edge_cases(200))
        ]
        
        for category_name, examples in categories:
            logger.info(f"  {category_name}: {len(examples)} examples")
            all_examples.extend(examples)
        
        # Shuffle for better training
        random.shuffle(all_examples)
        
        # Split into train/val/test
        total = len(all_examples)
        train_size = int(total * 0.8)
        val_size = int(total * 0.1)
        
        train_data = all_examples[:train_size]
        val_data = all_examples[train_size:train_size + val_size]
        test_data = all_examples[train_size + val_size:]
        
        logger.info(f"\nTotal examples generated: {total}")
        logger.info(f"  Training: {len(train_data)}")
        logger.info(f"  Validation: {len(val_data)}")
        logger.info(f"  Test: {len(test_data)}")
        
        return {
            "train": train_data,
            "validation": val_data,
            "test": test_data,
            "statistics": {
                "total_examples": total,
                "train_size": len(train_data),
                "val_size": len(val_data),
                "test_size": len(test_data),
                "unique_queries": len(self.generated_examples)
            }
        }
    
    def save_dataset(self, output_dir: str = "./lora_training_advanced"):
        """Save the complete dataset"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        dataset = self.generate_complete_dataset()
        
        # Save each split
        for split_name, split_data in [("train", dataset["train"]), 
                                       ("validation", dataset["validation"]),
                                       ("test", dataset["test"])]:
            
            # JSONL format
            with open(f"{output_dir}/{split_name}.jsonl", 'w') as f:
                for example in split_data:
                    f.write(json.dumps(example) + '\n')
            
            # Also save as JSON for inspection
            with open(f"{output_dir}/{split_name}.json", 'w') as f:
                json.dump(split_data[:10], f, indent=2)  # First 10 for inspection
        
        # Save statistics
        with open(f"{output_dir}/statistics.json", 'w') as f:
            json.dump(dataset["statistics"], f, indent=2)
        
        logger.info(f"\nDataset saved to {output_dir}/")
        
        return dataset["statistics"]


def main():
    """Generate the advanced training dataset"""
    generator = AdvancedTrainingGenerator()
    
    print("\n" + "="*70)
    print("ADVANCED LoRA TRAINING DATA GENERATION")
    print("="*70)
    
    stats = generator.save_dataset()
    
    print("\n✅ Advanced training dataset generated successfully!")
    print(f"\nStatistics:")
    print(f"  Total Examples: {stats['total_examples']:,}")
    print(f"  Unique Queries: {stats['unique_queries']:,}")
    print(f"  Training Set: {stats['train_size']:,}")
    print(f"  Validation Set: {stats['val_size']:,}")
    print(f"  Test Set: {stats['test_size']:,}")
    
    print(f"\nFiles saved to: ./lora_training_advanced/")
    print("\nNext steps:")
    print("1. Review examples: head -5 lora_training_advanced/train.jsonl")
    print("2. Start training: python train_lora_comprehensive.py")


if __name__ == "__main__":
    main()