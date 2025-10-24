#!/usr/bin/env python3
"""
FIT ID Lookup functionality
"""

import json
import chromadb
from pathlib import Path

class FITIDLookup:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="chroma_db")
        self.load_fit_data()
        
    def load_fit_data(self):
        """Load FIT data for ID lookups"""
        # Try to load from processed data
        data_files = [
            "data/processed_fit_licenses_20250821_072621.json",
            "data/all_commercial_fit.json",
            "data/commercial_sites_enhanced_with_fit.json"
        ]
        
        self.fit_records = {}
        
        for file_path in data_files:
            if Path(file_path).exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                    # Handle different data structures
                    if isinstance(data, dict):
                        if 'sites' in data:
                            # Commercial sites format
                            for site in data['sites']:
                                fit_id = site.get('fit_id') or site.get('installation_id')
                                if fit_id:
                                    self.fit_records[str(fit_id)] = site
                        elif 'licenses' in data:
                            # License format
                            for license in data['licenses']:
                                fit_id = license.get('fit_id') or license.get('installation_id')
                                if fit_id:
                                    self.fit_records[str(fit_id)] = license
                    elif isinstance(data, list):
                        for record in data:
                            fit_id = record.get('fit_id') or record.get('installation_id')
                            if fit_id:
                                self.fit_records[str(fit_id)] = record
    
    def lookup_fit_id(self, fit_id):
        """Look up a specific FIT ID"""
        fit_id_str = str(fit_id)
        
        if fit_id_str in self.fit_records:
            record = self.fit_records[fit_id_str]
            
            # Format the response
            result = {
                'fit_id': fit_id_str,
                'found': True,
                'data': {
                    'technology': record.get('technology', 'Unknown'),
                    'capacity_kw': record.get('capacity_kw') or record.get('installed_capacity_kw', 0),
                    'fit_rate': record.get('tariff_p_kwh') or record.get('fit_rate_p_kwh', 'Not available'),
                    'commission_date': record.get('commission_date') or record.get('commissioning_date', 'Unknown'),
                    'location': record.get('postcode') or record.get('location', 'Unknown'),
                    'status': record.get('status', 'Active')
                }
            }
            
            # Add FIT rate information
            if result['data']['fit_rate'] != 'Not available':
                result['message'] = f"FIT ID {fit_id_str}: {result['data']['fit_rate']}p/kWh for {result['data']['technology']} ({result['data']['capacity_kw']}kW)"
            else:
                result['message'] = f"FIT ID {fit_id_str}: {result['data']['technology']} installation, {result['data']['capacity_kw']}kW capacity"
                
            return result
        else:
            # Try searching in ChromaDB
            try:
                collection = self.client.get_collection("commercial_fit_sites")
                results = collection.query(
                    query_texts=[f"FIT ID {fit_id_str}"],
                    n_results=1
                )
                
                if results['metadatas'] and results['metadatas'][0]:
                    metadata = results['metadatas'][0][0]
                    return {
                        'fit_id': fit_id_str,
                        'found': True,
                        'data': {
                            'technology': metadata.get('technology', 'Unknown'),
                            'capacity_kw': metadata.get('capacity_kw', 0),
                            'fit_rate': metadata.get('tariff_p_kwh', 'Not available'),
                            'location': metadata.get('postcode', 'Unknown')
                        },
                        'message': f"FIT ID {fit_id_str} found in database"
                    }
            except:
                pass
            
            return {
                'fit_id': fit_id_str,
                'found': False,
                'message': f"FIT ID {fit_id_str} not found in the database. Please check the ID and try again."
            }

# Quick test
if __name__ == "__main__":
    lookup = FITIDLookup()
    
    # Test with FIT ID 1585
    result = lookup.lookup_fit_id(1585)
    print(json.dumps(result, indent=2))