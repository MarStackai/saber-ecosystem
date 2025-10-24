#!/usr/bin/env python3
"""
Fix missing FIT rates for wind sites in ChromaDB
"""
import chromadb
from fit_rate_mapper import FITRateMapper
import json

def fix_missing_rates():
    """Update ChromaDB with correct FIT rates for sites missing them"""
    
    client = chromadb.PersistentClient(path='chroma_db')
    collection = client.get_collection('commercial_fit_sites')
    mapper = FITRateMapper()
    
    batch_size = 1000
    offset = 0
    total_fixed = 0
    total_checked = 0
    
    print("Fixing missing FIT rates for wind sites...")
    
    while True:
        results = collection.get(
            limit=batch_size,
            offset=offset,
            where={'technology': 'Wind'},
            include=['metadatas', 'documents']
        )
        
        if not results['metadatas']:
            break
        
        ids_to_update = []
        metadatas_to_update = []
        documents_to_update = []
        
        for i, metadata in enumerate(results['metadatas']):
            total_checked += 1
            comm_date = metadata.get('commission_date', '')
            current_tariff = float(metadata.get('tariff_p_kwh', 0))
            
            # Check FIT-era sites with zero tariff
            if comm_date >= '2010-04-01' and comm_date <= '2019-03-31' and current_tariff == 0:
                # Get the correct FIT rate
                capacity_kw = float(metadata.get('capacity_mw', 0)) * 1000
                
                if capacity_kw > 0:
                    rate_info = mapper.get_fit_rate('Wind', capacity_kw, comm_date)
                    
                    if rate_info and isinstance(rate_info, dict):
                        new_rate = rate_info.get('rate_p_kwh', 0)
                        
                        if new_rate > 0:
                            # Update metadata
                            metadata['tariff_p_kwh'] = new_rate
                            
                            # Calculate financial values
                            generation_mwh = float(metadata.get('annual_generation_mwh', 0))
                            if generation_mwh > 0:
                                annual_income = (generation_mwh * 1000 * new_rate) / 100
                                metadata['annual_income'] = annual_income
                                
                                # Calculate remaining value
                                try:
                                    comm_year = int(str(comm_date)[:4])
                                    from datetime import datetime
                                    current_year = datetime.now().year
                                    years_left = max((comm_year + 20) - current_year, 0)
                                    metadata['total_remaining_value'] = annual_income * years_left
                                except:
                                    pass
                            
                            ids_to_update.append(results['ids'][i])
                            metadatas_to_update.append(metadata)
                            documents_to_update.append(results['documents'][i] if results['documents'] else None)
                            total_fixed += 1
                            
                            if total_fixed <= 5:
                                print(f"  Fixed FIT ID {metadata.get('fit_id')}: "
                                      f"{capacity_kw:.0f}kW -> {new_rate}p/kWh "
                                      f"(£{metadata.get('annual_income', 0):,.0f}/year)")
        
        # Update the collection
        if ids_to_update:
            print(f"  Updating batch of {len(ids_to_update)} sites...")
            collection.update(
                ids=ids_to_update,
                metadatas=metadatas_to_update,
                documents=documents_to_update if documents_to_update[0] else None
            )
        
        offset += batch_size
        if len(results['metadatas']) < batch_size:
            break
        
        if total_checked % 1000 == 0:
            print(f"  Checked {total_checked} sites, fixed {total_fixed} so far...")
    
    print(f"\nCompleted: Checked {total_checked} sites, fixed {total_fixed} missing FIT rates")
    
    # Verify the fix
    print("\nVerifying site 830547...")
    results = collection.get(
        where={'fit_id': '830547'},
        include=['metadatas']
    )
    
    if results['metadatas']:
        metadata = results['metadatas'][0]
        print(f"  FIT ID: {metadata.get('fit_id')}")
        print(f"  Tariff: {metadata.get('tariff_p_kwh')}p/kWh")
        print(f"  Annual Income: £{metadata.get('annual_income', 0):,.0f}")
        print(f"  Total Remaining: £{metadata.get('total_remaining_value', 0):,.0f}")

if __name__ == "__main__":
    fix_missing_rates()