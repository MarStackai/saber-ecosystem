#!/usr/bin/env python3
"""
Quick update of FIT rates in ChromaDB - processes first 1000 records as test
"""

import chromadb
from fit_rate_mapper import FITRateMapper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def quick_update():
    # Initialize
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_collection('commercial_fit_sites')
    rate_mapper = FITRateMapper()
    
    # Get first 1000 records
    logger.info("Getting first 1000 records...")
    results = collection.get(limit=1000, include=['metadatas'])
    
    updated_count = 0
    batch_ids = []
    batch_metadatas = []
    
    for i, metadata in enumerate(results['metadatas']):
        record_id = results['ids'][i]
        
        # Get current values
        technology = metadata.get('technology')
        capacity_kw = metadata.get('capacity_kw')
        commission_date = metadata.get('commission_date')
        current_rate = metadata.get('tariff_p_kwh', 0)
        
        # Skip if already has a non-zero rate
        if current_rate and float(current_rate) > 0:
            continue
        
        # Look up correct FIT rate
        if technology and capacity_kw and commission_date:
            rate_info = rate_mapper.get_fit_rate(
                technology, 
                float(capacity_kw), 
                commission_date
            )
            
            if rate_info and rate_info.get('rate_p_kwh'):
                # Update metadata with new rate
                metadata['tariff_p_kwh'] = rate_info['rate_p_kwh']
                metadata['fit_period'] = rate_info['fit_period']
                metadata['capacity_band'] = rate_info['capacity_band']
                
                batch_ids.append(record_id)
                batch_metadatas.append(metadata)
                updated_count += 1
                
                if updated_count % 10 == 0:
                    logger.info(f"Prepared {updated_count} updates...")
    
    # Update in ChromaDB
    if batch_ids:
        logger.info(f"Updating {len(batch_ids)} records in ChromaDB...")
        collection.update(
            ids=batch_ids,
            metadatas=batch_metadatas
        )
    
    logger.info(f"Updated {updated_count} records with FIT rates")
    
    # Verify
    logger.info("\nVerifying updates...")
    results = collection.get(limit=10, include=['metadatas'])
    
    for metadata in results['metadatas'][:5]:
        fit_id = metadata.get('fit_id')
        rate = metadata.get('tariff_p_kwh')
        period = metadata.get('fit_period')
        band = metadata.get('capacity_band')
        logger.info(f"FIT {fit_id}: Rate={rate}p/kWh, Period={period}, Band={band}")

if __name__ == "__main__":
    quick_update()