#!/usr/bin/env python3
"""
Update ChromaDB records with correct FIT rates based on technology, capacity, and commission date
"""

import chromadb
from fit_rate_mapper import FITRateMapper
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_fit_rates_in_chromadb():
    """Update all ChromaDB records with correct FIT rates"""
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path="chroma_db")
    
    # Initialize FIT rate mapper
    rate_mapper = FITRateMapper()
    
    # Get all collections
    collections = [
        'commercial_fit_sites',
        'fit_licenses_nondomestic',
        'fit_licenses_enhanced'
    ]
    
    for collection_name in collections:
        try:
            collection = client.get_collection(collection_name)
            logger.info(f"Processing collection: {collection_name}")
            
            # Get all records - ChromaDB doesn't support 'ids' in include anymore
            results = collection.get(include=['metadatas'])
            
            if not results['metadatas']:
                logger.info(f"No records in {collection_name}")
                continue
            
            logger.info(f"Found {len(results['metadatas'])} records in {collection_name}")
            
            # Process in batches
            batch_size = 100
            updated_count = 0
            
            for i in tqdm(range(0, len(results['metadatas']), batch_size)):
                batch_ids = []
                batch_metadatas = []
                
                for j in range(i, min(i + batch_size, len(results['metadatas']))):
                    metadata = results['metadatas'][j]
                    # IDs are returned automatically even if not in include
                    record_id = results['ids'][j] if 'ids' in results else f"id_{j}"
                    
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
                
                # Update batch in ChromaDB
                if batch_ids:
                    collection.update(
                        ids=batch_ids,
                        metadatas=batch_metadatas
                    )
                    logger.info(f"Updated {len(batch_ids)} records in batch {i//batch_size + 1}")
            
            logger.info(f"Updated {updated_count} records in {collection_name} with FIT rates")
            
        except Exception as e:
            logger.error(f"Error processing {collection_name}: {e}")
            continue
    
    logger.info("FIT rate update complete")

def verify_rates():
    """Verify that rates were updated correctly"""
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_collection('commercial_fit_sites')
    
    # Sample some records to check
    results = collection.get(limit=10, include=['metadatas'])
    
    logger.info("\nVerification - Sample Records:")
    for metadata in results['metadatas']:
        fit_id = metadata.get('fit_id')
        tech = metadata.get('technology')
        capacity = metadata.get('capacity_kw')
        rate = metadata.get('tariff_p_kwh')
        period = metadata.get('fit_period')
        band = metadata.get('capacity_band')
        
        logger.info(f"FIT {fit_id}: {tech} {capacity}kW - Rate: {rate}p/kWh (Period: {period}, Band: {band})")

if __name__ == "__main__":
    logger.info("Starting FIT rate update process...")
    update_fit_rates_in_chromadb()
    verify_rates()
    logger.info("Process complete")