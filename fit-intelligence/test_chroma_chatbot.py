#!/usr/bin/env python3
"""
Test script to verify FIT Chatbot is correctly using Chroma database
"""

import sys
import json
from fit_chatbot import FITIntelligenceChatbot

def test_chroma_integration():
    """Test that the chatbot correctly retrieves data from Chroma"""
    
    print("="*60)
    print("TESTING FIT CHATBOT CHROMA INTEGRATION")
    print("="*60)
    
    # Initialize chatbot (no OpenRouter key needed for testing Chroma)
    print("\n1. Initializing FIT Intelligence Chatbot...")
    chatbot = FITIntelligenceChatbot()
    
    # Show system status
    print(f"\n2. System Status:")
    print(f"   - Collections loaded: {len(chatbot.intelligence_api.collections)}")
    for name, collection in chatbot.intelligence_api.collections.items():
        print(f"   - {name}: {collection.count()} documents")
    
    # Test queries
    test_queries = [
        ("FIT ID 764485", "Testing specific FIT ID lookup"),
        ("What is FIT ID 764485?", "Natural language FIT ID query"),
        ("Show me wind farms in Gwynedd", "Geographic technology query"),
        ("Solar installations expiring soon", "Urgency-based query"),
        ("Large wind farms over 1MW", "Capacity filter query")
    ]
    
    print(f"\n3. Testing Queries:")
    print("-"*60)
    
    for query, description in test_queries:
        print(f"\nQuery: '{query}'")
        print(f"Purpose: {description}")
        
        # Analyze intent
        intent = chatbot._analyze_intent(query)
        print(f"Intent Analysis: {json.dumps(intent, indent=2)}")
        
        # Query Chroma
        results = chatbot._query_chroma_system(query, intent)
        
        if results and results.get('success'):
            print(f"✓ Results found!")
            if 'data' in results:
                # Single result (FIT ID search)
                data = results['data']
                print(f"  - Source: {results.get('source', 'unknown')}")
                print(f"  - FIT ID: {data.get('fit_id', data.get('site_id', 'N/A'))}")
                print(f"  - Technology: {data.get('technology', 'N/A')}")
                print(f"  - Capacity: {data.get('capacity_kw', 'N/A')} kW")
                print(f"  - Location: {data.get('location', data.get('postcode', 'N/A'))}")
            elif 'results' in results:
                # Multiple results
                print(f"  - Found {len(results['results'])} results")
                print(f"  - Source: {results.get('source', 'unknown')}")
                
                # Show first 3 results
                for i, result in enumerate(results['results'][:3], 1):
                    tech = result.get('technology', 'Unknown')
                    capacity = result.get('capacity_kw') or result.get('capacity_mw', 0) * 1000
                    location = result.get('location', result.get('postcode', 'Unknown'))
                    fit_id = result.get('fit_id', result.get('site_id', 'N/A'))
                    
                    print(f"  {i}. {tech} - {capacity:.0f}kW - {location} (ID: {fit_id})")
                
                # Show insights if available
                insights = results.get('combined_insights', {})
                if insights:
                    print(f"\n  Combined Insights:")
                    print(f"    - Total results: {insights.get('total_results', 0)}")
                    print(f"    - Commercial sites: {insights.get('commercial_count', 0)}")
                    print(f"    - FIT licenses: {insights.get('license_count', 0)}")
        else:
            print(f"✗ No results found")
            if results:
                print(f"  Message: {results.get('message', 'Unknown error')}")
        
        print("-"*60)
    
    # Test specific FIT ID 764485 that we know exists
    print(f"\n4. Detailed Test for FIT ID 764485:")
    print("-"*60)
    
    # Direct query to Chroma
    direct_results = chatbot.intelligence_api.natural_language_query("FIT ID 764485", max_results=5)
    
    if direct_results:
        print(f"Direct Chroma Query Results:")
        
        # Check commercial results
        if 'commercial_results' in direct_results:
            print(f"  Commercial Results: {len(direct_results['commercial_results'])}")
            for result in direct_results['commercial_results']:
                metadata = result.get('metadata', {})
                if str(metadata.get('site_id')) == '764485':
                    print(f"  ✓ Found in commercial data!")
                    print(f"    - Technology: {metadata.get('technology')}")
                    print(f"    - Capacity: {metadata.get('capacity_mw')} MW")
                    print(f"    - Location: {metadata.get('postcode')}")
        
        # Check license results
        if 'license_results' in direct_results:
            print(f"  License Results: {len(direct_results['license_results'])}")
            for result in direct_results['license_results']:
                metadata = result.get('metadata', {})
                if metadata.get('fit_id') == '764485':
                    print(f"  ✓ Found in license data!")
                    print(f"    - Technology: {metadata.get('technology')}")
                    print(f"    - Capacity: {metadata.get('capacity_kw')} kW")
                    print(f"    - Location: {metadata.get('location')}")
                    print(f"    - Postcode: {metadata.get('postcode')}")
                    print(f"    - FIT Remaining: {metadata.get('remaining_fit_years')} years")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_chroma_integration()