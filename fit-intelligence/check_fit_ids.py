#!/usr/bin/env python3
"""
Check what FIT IDs exist in the Chroma database
"""

from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI
import json

# Initialize API
api = EnhancedFITIntelligenceAPI()

print("Checking FIT IDs in database...")
print("="*60)

# Search for various patterns
test_searches = [
    "764485",
    "FIT ID 764485", 
    "Gwynedd Wales",
    "LL53",  # The postcode from the dashboard
    "130kW wind"  # The capacity from the dashboard
]

for search in test_searches:
    print(f"\nSearching for: '{search}'")
    results = api.natural_language_query(search, max_results=5)
    
    if results:
        # Check commercial results
        comm_count = len(results.get('commercial_results', []))
        lic_count = len(results.get('license_results', []))
        
        print(f"  Found: {comm_count} commercial, {lic_count} license results")
        
        # Show first result from each
        if comm_count > 0:
            first_comm = results['commercial_results'][0]['metadata']
            print(f"  Commercial example:")
            print(f"    - Site ID: {first_comm.get('site_id', 'N/A')}")
            print(f"    - Tech: {first_comm.get('technology', 'N/A')}")
            print(f"    - Capacity: {first_comm.get('capacity_mw', 0)} MW")
            print(f"    - Postcode: {first_comm.get('postcode', 'N/A')}")
        
        if lic_count > 0:
            first_lic = results['license_results'][0]['metadata']
            print(f"  License example:")
            print(f"    - FIT ID: {first_lic.get('fit_id', 'N/A')}")
            print(f"    - Tech: {first_lic.get('technology', 'N/A')}")
            print(f"    - Capacity: {first_lic.get('capacity_kw', 0)} kW")
            print(f"    - Location: {first_lic.get('location', 'N/A')}")
            print(f"    - Postcode: {first_lic.get('postcode', 'N/A')}")

# Now check for ANY wind farms in Wales
print("\n" + "="*60)
print("Searching for wind farms in Wales...")
results = api.natural_language_query("wind Wales", max_results=10)

if results and 'license_results' in results:
    print(f"Found {len(results['license_results'])} wind licenses in Wales")
    
    # Check if any have similar IDs to 764485
    for result in results['license_results']:
        metadata = result['metadata']
        fit_id = metadata.get('fit_id', '')
        if '764' in str(fit_id) or '485' in str(fit_id):
            print(f"  Potential match: FIT ID {fit_id}")
            print(f"    - Location: {metadata.get('location')}")
            print(f"    - Capacity: {metadata.get('capacity_kw')} kW")
            print(f"    - Postcode: {metadata.get('postcode')}")

# Sample some actual FIT IDs from the database
print("\n" + "="*60)
print("Sample of actual FIT IDs in database:")
sample = api.natural_language_query("wind", max_results=5)
if sample and 'license_results' in sample:
    for i, result in enumerate(sample['license_results'], 1):
        metadata = result['metadata']
        print(f"{i}. FIT ID: {metadata.get('fit_id', 'N/A')} - {metadata.get('technology')} - {metadata.get('capacity_kw')}kW - {metadata.get('location')}")