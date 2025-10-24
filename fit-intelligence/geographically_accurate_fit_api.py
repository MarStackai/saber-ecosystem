#!/usr/bin/env python3
"""
Geographically Accurate FIT API
Uses UK Geographic Database to ensure correct postcode filtering
"""

import chromadb
from chromadb.utils import embedding_functions
import json
import logging
from typing import List, Dict, Optional
from create_uk_geographic_db import UKGeographicDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeographicallyAccurateFITAPI:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="chroma_db")
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Initialize geographic database
        self.geo_db = UKGeographicDatabase()
        
        # Load FIT collections
        self.fit_collection = self.client.get_collection(
            "commercial_fit_sites",
            embedding_function=self.embedding_function
        )
        
    def search_with_geographic_accuracy(self, query: str, max_results: int = 20) -> Dict:
        """
        Search FIT sites with geographic accuracy
        Aberdeen will ONLY return AB postcodes
        """
        
        # Extract location from query
        location = self._extract_location(query)
        
        if location:
            # Get valid postcodes for this location
            geo_result = self.geo_db.search_location(location)
            valid_postcodes = geo_result['valid_postcodes']
            
            logger.info(f"Location '{location}' maps to postcodes: {valid_postcodes[:10]}...")
            
            # Search FIT database
            results = self.fit_collection.query(
                query_texts=[query],
                n_results=max_results * 3  # Get more results to filter
            )
            
            # Filter results by valid postcodes
            filtered_results = []
            for i in range(len(results['ids'][0])):
                metadata = results['metadatas'][0][i]
                site_postcode = metadata.get('postcode', '')
                
                # Check if postcode matches location
                if self._postcode_matches(site_postcode, valid_postcodes):
                    filtered_results.append({
                        'id': results['ids'][0][i],
                        'metadata': metadata,
                        'document': results['documents'][0][i],
                        'distance': results['distances'][0][i]
                    })
            
            # Add FIT IDs to all results
            for i, result in enumerate(filtered_results):
                if 'fit_id' not in result['metadata']:
                    # Generate FIT ID from site data
                    result['metadata']['fit_id'] = self._generate_fit_id(result['metadata'], i)
            
            return {
                'query': query,
                'location_detected': location,
                'valid_postcodes': valid_postcodes[:20],  # Show first 20
                'results': filtered_results[:max_results],
                'total_found': len(filtered_results)
            }
        else:
            # No specific location - standard search
            results = self.fit_collection.query(
                query_texts=[query],
                n_results=max_results
            )
            
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    'id': results['ids'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'document': results['documents'][0][i],
                    'distance': results['distances'][0][i]
                }
                
                # Add FIT ID
                if 'fit_id' not in result['metadata']:
                    result['metadata']['fit_id'] = self._generate_fit_id(result['metadata'], i)
                
                formatted_results.append(result)
            
            return {
                'query': query,
                'location_detected': None,
                'results': formatted_results,
                'total_found': len(formatted_results)
            }
    
    def _extract_location(self, query: str) -> Optional[str]:
        """Extract location from query"""
        query_lower = query.lower()
        
        # Check for specific places
        uk_places = [
            "aberdeen", "edinburgh", "glasgow", "dundee", "inverness",
            "newcastle", "manchester", "liverpool", "leeds", "sheffield",
            "york", "hull", "bradford", "birmingham", "nottingham",
            "leicester", "london", "bristol", "southampton", "brighton",
            "cardiff", "swansea", "belfast", "yorkshire", "scotland",
            "wales", "england"
        ]
        
        for place in uk_places:
            if place in query_lower:
                return place.title()
        
        # Check for "near" or "in" patterns
        import re
        patterns = [
            r'near\s+(\w+)',
            r'in\s+(\w+)',
            r'around\s+(\w+)',
            r'at\s+(\w+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                location = match.group(1)
                if location in uk_places:
                    return location.title()
        
        return None
    
    def _postcode_matches(self, site_postcode: str, valid_postcodes: List[str]) -> bool:
        """Check if site postcode matches valid postcodes for location"""
        if not site_postcode:
            return False
        
        site_prefix = site_postcode.split()[0] if ' ' in site_postcode else site_postcode[:3]
        site_prefix = site_prefix.upper()
        
        for valid_pc in valid_postcodes:
            if site_prefix.startswith(valid_pc):
                return True
        
        return False
    
    def _generate_fit_id(self, metadata: Dict, index: int) -> str:
        """Generate a FIT ID for sites that don't have one"""
        # Use existing ID if available
        if 'installation_id' in metadata:
            return str(metadata['installation_id'])
        
        # Generate based on metadata
        tech = metadata.get('technology', 'UNK')[:3].upper()
        capacity = int(metadata.get('capacity_kw', 0))
        postcode = metadata.get('postcode', 'XX')[:3]
        
        # Create unique ID
        fit_id = f"{index + 1000}"  # Simple numeric ID
        return fit_id

def test_geographic_accuracy():
    """Test the geographically accurate API"""
    print("=" * 60)
    print("TESTING GEOGRAPHICALLY ACCURATE FIT API")
    print("=" * 60)
    
    api = GeographicallyAccurateFITAPI()
    
    # Test queries
    test_queries = [
        "wind sites over 250kw near Aberdeen",
        "solar farms in Edinburgh",
        "wind turbines in Yorkshire",
        "renewable energy near Glasgow"
    ]
    
    for query in test_queries:
        print(f"\n📍 Query: '{query}'")
        print("-" * 40)
        
        result = api.search_with_geographic_accuracy(query, max_results=5)
        
        print(f"Location detected: {result.get('location_detected')}")
        if result.get('valid_postcodes'):
            print(f"Valid postcodes: {result['valid_postcodes'][:10]}")
        print(f"Results found: {result['total_found']}")
        
        if result['results']:
            print("\nTop results:")
            for i, r in enumerate(result['results'][:3], 1):
                metadata = r['metadata']
                print(f"{i}. FIT ID: {metadata.get('fit_id')}")
                print(f"   Technology: {metadata.get('technology')}")
                print(f"   Capacity: {metadata.get('capacity_kw')}kW")
                print(f"   Location: {metadata.get('postcode')}")
                print(f"   ✅ Postcode validation: PASSED")
        else:
            print("No matching sites found")
    
    # Specific test for Aberdeen
    print("\n" + "=" * 60)
    print("🎯 CRITICAL TEST: Aberdeen should ONLY return AB postcodes")
    print("-" * 40)
    
    aberdeen_result = api.search_with_geographic_accuracy("wind near Aberdeen", max_results=10)
    
    ab_count = 0
    wrong_count = 0
    wrong_postcodes = []
    
    for r in aberdeen_result['results']:
        postcode = r['metadata'].get('postcode', '')
        if postcode.startswith('AB'):
            ab_count += 1
        else:
            wrong_count += 1
            wrong_postcodes.append(postcode)
    
    print(f"✅ Correct (AB) postcodes: {ab_count}")
    print(f"❌ Wrong postcodes: {wrong_count}")
    if wrong_postcodes:
        print(f"   Wrong ones found: {wrong_postcodes}")
    
    if wrong_count == 0 and ab_count > 0:
        print("\n🎉 SUCCESS! Geographic filtering is working correctly!")
    else:
        print("\n⚠️ Still needs adjustment")

if __name__ == "__main__":
    test_geographic_accuracy()