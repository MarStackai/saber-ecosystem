#!/usr/bin/env python3
"""
Real Query Training System
Train on actual user queries and expected results from your FIT database
"""

import json
import torch
from pathlib import Path
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer, InputExample
from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI
import logging

logger = logging.getLogger(__name__)

class RealQueryTrainer:
    """Train model on real query patterns from your FIT database"""
    
    def __init__(self):
        self.api = EnhancedFITIntelligenceAPI()
        
    def create_real_training_data(self) -> List[Dict]:
        """Create training data from known good query-result pairs"""
        
        # Real queries that should work well
        real_queries = [
            {
                'query': 'wind sites over 250kw in yorkshire',
                'expected_technology': 'Wind',
                'expected_min_capacity': 250,
                'expected_location': 'yorkshire',
                'should_find_results': True
            },
            {
                'query': 'solar installations above 500kw',
                'expected_technology': 'Photovoltaic',
                'expected_min_capacity': 500,
                'should_find_results': True
            },
            {
                'query': 'large wind farms over 1mw',
                'expected_technology': 'Wind', 
                'expected_min_capacity': 1000,
                'should_find_results': True
            },
            {
                'query': 'wind site fit ids for sites over 250kw around beverly',
                'expected_technology': 'Wind',
                'expected_min_capacity': 250,
                'expected_location': 'beverly',
                'should_find_results': False  # We know this should return no results
            },
            {
                'query': 'solar sites over 250kw in east anglia',
                'expected_technology': 'Photovoltaic',
                'expected_min_capacity': 250,
                'expected_location': 'east anglia',
                'should_find_results': True
            },
            {
                'query': 'hydro installations in scotland',
                'expected_technology': 'Hydro',
                'expected_location': 'scotland',
                'should_find_results': True
            },
            {
                'query': 'anaerobic digestion sites over 100kw',
                'expected_technology': 'Anaerobic digestion',
                'expected_min_capacity': 100,
                'should_find_results': True
            },
            {
                'query': 'renewable sites between 250 and 500kw in cornwall',
                'expected_min_capacity': 250,
                'expected_max_capacity': 500,
                'expected_location': 'cornwall',
                'should_find_results': True
            }
        ]
        
        return real_queries
    
    def validate_current_performance(self) -> Dict:
        """Test current model performance on real queries"""
        real_queries = self.create_real_training_data()
        results = []
        
        for query_data in real_queries:
            query = query_data['query']
            
            # Test current API
            api_result = self.api.natural_language_query(query, max_results=20)
            filters_parsed = self.api._parse_nl_filters(query)
            
            # Check if parsing worked correctly
            parsing_correct = True
            issues = []
            
            if 'expected_technology' in query_data:
                expected_tech = query_data['expected_technology']
                actual_tech = filters_parsed.get('technology')
                if actual_tech != expected_tech:
                    parsing_correct = False
                    issues.append(f"Technology: expected {expected_tech}, got {actual_tech}")
            
            if 'expected_min_capacity' in query_data:
                expected_cap = query_data['expected_min_capacity']
                actual_cap = filters_parsed.get('min_capacity_kw')
                if actual_cap != expected_cap:
                    parsing_correct = False
                    issues.append(f"Min capacity: expected {expected_cap}kW, got {actual_cap}kW")
            
            # Check results
            total_results = len(api_result.get('commercial_results', [])) + len(api_result.get('license_results', []))
            found_results = total_results > 0
            should_find = query_data.get('should_find_results', True)
            
            results_correct = found_results == should_find
            
            results.append({
                'query': query,
                'filters_parsed': filters_parsed,
                'parsing_correct': parsing_correct,
                'parsing_issues': issues,
                'total_results': total_results,
                'found_results': found_results,
                'should_find_results': should_find,
                'results_correct': results_correct,
                'overall_success': parsing_correct and results_correct
            })
        
        # Calculate success rate
        success_rate = sum(1 for r in results if r['overall_success']) / len(results)
        parsing_rate = sum(1 for r in results if r['parsing_correct']) / len(results)
        
        return {
            'success_rate': success_rate,
            'parsing_success_rate': parsing_rate,
            'total_tests': len(results),
            'details': results
        }
    
    def create_improved_training_examples(self) -> List[InputExample]:
        """Create training examples to fix known issues"""
        examples = []
        
        # Capacity variations - these should be similar
        capacity_variations = [
            ("sites over 250kw", "installations above 250kw"),
            ("projects greater than 250kw", "facilities over 250kw"),
            ("sites over 250 kilowatts", "installations above 250 kW"),
            ("large sites over 250kw", "big installations above 250kw"),
            ("commercial sites over 250kw", "industrial installations above 250kw")
        ]
        
        for var1, var2 in capacity_variations:
            examples.append(InputExample(texts=[var1, var2], label=0.9))
        
        # Technology variations
        tech_variations = [
            ("wind sites", "wind installations"),
            ("wind farms", "wind projects"),
            ("solar sites", "photovoltaic installations"),
            ("solar farms", "pv sites"),
            ("hydro sites", "hydro installations"),
            ("anaerobic digestion", "biogas sites"),
            ("anaerobic digestion sites", "AD installations")
        ]
        
        for var1, var2 in tech_variations:
            examples.append(InputExample(texts=[var1, var2], label=0.9))
        
        # Location variations
        location_variations = [
            ("sites in yorkshire", "installations in yorkshire"),
            ("sites around liverpool", "installations near liverpool"),
            ("sites in east anglia", "installations in east anglia"),
            ("sites near beverly", "installations around beverly"),
            ("cornwall sites", "sites in cornwall")
        ]
        
        for var1, var2 in location_variations:
            examples.append(InputExample(texts=[var1, var2], label=0.9))
        
        # Combined query variations
        combined_variations = [
            ("wind sites over 250kw in yorkshire", "wind installations above 250kw in yorkshire"),
            ("solar sites over 250kw in east anglia", "photovoltaic installations above 250kw in east anglia"),
            ("large wind sites in scotland", "big wind installations in scotland"),
            ("wind site fit ids for sites over 250kw around beverly", "wind installation ids for projects over 250kw near beverly")
        ]
        
        for var1, var2 in combined_variations:
            examples.append(InputExample(texts=[var1, var2], label=0.9))
        
        # Negative examples - these should be dissimilar
        negative_examples = [
            ("wind sites over 250kw", "small solar installations", 0.2),
            ("sites in yorkshire", "installations in cornwall", 0.3),
            ("large wind farms", "small hydro sites", 0.1),
            ("commercial installations", "residential systems", 0.2)
        ]
        
        for text1, text2, similarity in negative_examples:
            examples.append(InputExample(texts=[text1, text2], label=similarity))
        
        return examples

def main():
    """Test current performance and suggest improvements"""
    trainer = RealQueryTrainer()
    
    print("🧪 Testing current model performance...")
    performance = trainer.validate_current_performance()
    
    print(f"\\n📊 CURRENT PERFORMANCE RESULTS:")
    print(f"Overall success rate: {performance['success_rate']:.1%}")
    print(f"Query parsing success rate: {performance['parsing_success_rate']:.1%}")
    print(f"Total tests: {performance['total_tests']}")
    
    print(f"\\n🔍 DETAILED RESULTS:")
    for result in performance['details']:
        status = "✅" if result['overall_success'] else "❌"
        print(f"{status} {result['query']}")
        if not result['parsing_correct']:
            print(f"   Parsing issues: {', '.join(result['parsing_issues'])}")
        if not result['results_correct']:
            expected = "should find" if result['should_find_results'] else "should find none"
            actual = f"found {result['total_results']}"
            print(f"   Results issue: {expected}, but {actual}")
    
    # Create improved training examples
    print(f"\\n🎯 Creating improved training examples...")
    examples = trainer.create_improved_training_examples()
    print(f"Created {len(examples)} training examples")
    
    # Save examples for training
    training_data = []
    for example in examples:
        training_data.append({
            'text1': example.texts[0],
            'text2': example.texts[1],
            'similarity': float(example.label)
        })
    
    with open('real_query_training_data.json', 'w') as f:
        json.dump({
            'performance_baseline': performance,
            'training_examples': training_data,
            'timestamp': str(torch.cuda.get_device_properties(0)) if torch.cuda.is_available() else 'CPU'
        }, f, indent=2)
    
    print(f"\\n💾 Training data saved to: real_query_training_data.json")
    print(f"\\n🚀 Ready for training! Run: python training_pipeline.py")
    
    return performance

if __name__ == "__main__":
    main()