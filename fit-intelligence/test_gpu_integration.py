#!/usr/bin/env python3
"""
Test GPU-accelerated Ollama with FIT Intelligence
"""

import requests
import json
from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI

def test_with_gpu_ollama():
    """Test FIT queries using GPU-accelerated Ollama"""
    
    api = EnhancedFITIntelligenceAPI()
    
    test_queries = [
        {
            "query": "wind sites near aberdeen over 225kw",
            "expected": "Should find sites with AB postcodes and capacity > 225kW"
        },
        {
            "query": "solar installations in Yorkshire between 150kw and 500kw", 
            "expected": "Should find sites in Yorkshire postcodes (YO, LS, etc.) with 150-500kW"
        }
    ]
    
    for test in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {test['query']}")
        print(f"Expected: {test['expected']}")
        print('-'*60)
        
        # Step 1: Use Ollama to understand the query
        prompt = f"""Extract search parameters from this FIT query and return as JSON:
Query: "{test['query']}"

Return JSON with:
- technology: wind/solar/hydro or null
- min_capacity_kw: number or null
- max_capacity_kw: number or null  
- location: city/region name or null

JSON:"""
        
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama2:13b',
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.1,
                    'num_predict': 200
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            llm_output = response.json().get('response', '')
            print(f"LLM Understanding:\n{llm_output}\n")
            
            # Try to parse JSON
            try:
                # Extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
                if json_match:
                    params = json.loads(json_match.group())
                    print(f"Parsed params: {params}\n")
                    
                    # Step 2: Search database with parameters
                    # Use the right postcode based on location
                    postcode_map = {
                        'aberdeen': 'AB',
                        'edinburgh': 'EH',
                        'yorkshire': ['YO', 'LS', 'BD', 'HX', 'HD', 'WF', 'S', 'DN', 'HU']
                    }
                    
                    location = params.get('location', '').lower()
                    search_query = f"{params.get('technology', '')} {location}"
                    
                    # Search all collections
                    all_results = []
                    for collection_name, collection in api.collections.items():
                        query_result = collection.query(
                            query_texts=[search_query],
                            n_results=100
                        )
                        
                        if query_result['ids'] and query_result['ids'][0]:
                            for i, doc_id in enumerate(query_result['ids'][0]):
                                metadata = query_result['metadatas'][0][i] if query_result['metadatas'] else {}
                                
                                # Filter by parameters
                                keep = True
                                
                                # Technology filter
                                if params.get('technology'):
                                    tech = metadata.get('technology', '').lower()
                                    if params['technology'].lower() not in tech:
                                        keep = False
                                
                                # Capacity filter
                                capacity = metadata.get('capacity_kw', 0)
                                if params.get('min_capacity_kw') and capacity < params['min_capacity_kw']:
                                    keep = False
                                if params.get('max_capacity_kw') and capacity > params['max_capacity_kw']:
                                    keep = False
                                    
                                # Location filter (postcode-based)
                                if location in postcode_map:
                                    postcode = metadata.get('postcode', '')
                                    expected_prefixes = postcode_map[location]
                                    if isinstance(expected_prefixes, str):
                                        expected_prefixes = [expected_prefixes]
                                    
                                    if not any(postcode.startswith(prefix) for prefix in expected_prefixes):
                                        keep = False
                                
                                if keep:
                                    all_results.append(metadata)
                    
                    # Show results
                    print(f"Found {len(all_results)} matching sites:")
                    for r in all_results[:5]:
                        print(f"  FIT {r.get('fit_id')}: {r.get('site_name', 'Unknown')} ({r.get('postcode')}) - {r.get('capacity_kw')}kW")
                    
            except Exception as e:
                print(f"Error parsing LLM response: {e}")
        else:
            print(f"Error calling Ollama: {response.status_code}")

if __name__ == "__main__":
    test_with_gpu_ollama()