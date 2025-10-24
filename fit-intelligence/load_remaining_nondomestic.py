#!/usr/bin/env python3
"""
Load remaining non-domestic FIT installations (continue from where we left off)
"""

import chromadb
from chromadb.utils import embedding_functions
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_remaining_nondomestic():
    """Load remaining non-domestic FIT installations"""
    
    # Initialize Chroma
    client = chromadb.PersistentClient(path="./chroma_db")
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    # Get existing collection
    collection = client.get_collection(
        name="fit_licenses_nondomestic",
        embedding_function=embedding_function
    )
    
    current_count = collection.count()
    logger.info(f"Current collection has {current_count:,} documents")
    
    # Get all existing IDs to avoid duplicates
    logger.info("Getting existing FIT IDs...")
    existing_ids = set()
    batch_size = 1000
    for offset in range(0, current_count, batch_size):
        batch = collection.get(limit=batch_size, offset=offset)
        for metadata in batch['metadatas']:
            existing_ids.add(metadata['fit_id'])
    
    logger.info(f"Found {len(existing_ids):,} existing FIT IDs")
    
    # Process all three parts but skip existing records
    total_added = 0
    
    for part_num in [1, 2, 3]:
        csv_file = f'data/fit_part_{part_num}_clean.csv'
        logger.info(f"\nProcessing {csv_file}...")
        
        # Read CSV
        df = pd.read_csv(csv_file)
        
        # Filter for non-domestic installations
        non_domestic = df[df['Installation Type'].str.contains('Non Domestic', case=False, na=False)]
        
        # Skip already loaded records
        non_domestic['FIT_ID_STR'] = non_domestic['FIT ID'].astype(str)
        new_records = non_domestic[~non_domestic['FIT_ID_STR'].isin(existing_ids)]
        
        logger.info(f"  Found {len(new_records)} new records to add from Part {part_num}")
        
        if len(new_records) == 0:
            continue
        
        # Rename columns
        column_mapping = {
            'PostCode ': 'Postcode',
            'Installed capacity': 'Capacity (kW)',
            'Commissioned Date': 'Commissioned Date',
            'Commissioning date': 'Commissioned Date',
            'TariffCode': 'Tariff',
            'Tariff Description': 'Tariff Description',
            'Installation Country': 'Country',
            'Government Office Region': 'Region',
            'Local Authority': 'Local Authority',
            'LLSOA Code': 'LLSOA',
            'MLSOA Code': 'MSOA',
            'Community school category': 'Community/School'
        }
        new_records = new_records.rename(columns=column_mapping)
        
        # Process in smaller batches
        documents = []
        metadatas = []
        ids = []
        
        for idx, row in new_records.iterrows():
            # Create text for embedding
            doc_text = f"""
            FIT ID: {row['FIT ID']}
            Technology: {row['Technology']}
            Capacity: {row.get('Capacity (kW)', row.get('Installed capacity', 0))} kW
            Location: {row['Local Authority']} - {row['Region']} - {row['Country']}
            Postcode: {row.get('Postcode', row.get('PostCode ', ''))}
            """
            
            # Calculate remaining FIT years
            try:
                commissioned_date = row['Commissioned Date']
                if pd.notna(commissioned_date):
                    commissioned = pd.to_datetime(commissioned_date)
                    years_old = (datetime.now() - commissioned).days / 365.25
                    remaining_fit = max(0, 20 - years_old)
                else:
                    years_old = None
                    remaining_fit = None
            except:
                years_old = None
                remaining_fit = None
            
            # Determine repowering window
            if remaining_fit is not None:
                if remaining_fit <= 0:
                    repowering_window = "EXPIRED"
                elif remaining_fit <= 2:
                    repowering_window = "IMMEDIATE"
                elif remaining_fit <= 5:
                    repowering_window = "URGENT"
                elif remaining_fit <= 10:
                    repowering_window = "OPTIMAL"
                else:
                    repowering_window = "PLANNING"
            else:
                repowering_window = "UNKNOWN"
            
            capacity_kw = row.get('Capacity (kW)', row.get('Installed capacity', 0))
            if pd.isna(capacity_kw):
                capacity_kw = 0
            else:
                capacity_kw = float(capacity_kw)
            
            metadata = {
                'fit_id': str(row['FIT ID']),
                'technology': row['Technology'],
                'capacity_kw': capacity_kw,
                'capacity_mw': capacity_kw / 1000,
                'postcode': str(row.get('Postcode', row.get('PostCode ', ''))).strip() if pd.notna(row.get('Postcode', row.get('PostCode ', ''))) else '',
                'location': f"{row['Local Authority']} - {row['Region']} - {row['Country']}",
                'region': row['Region'] if pd.notna(row['Region']) else '',
                'country': row['Country'] if pd.notna(row['Country']) else '',
                'local_authority': row['Local Authority'] if pd.notna(row['Local Authority']) else '',
                'commissioned_date': str(row['Commissioned Date']) if pd.notna(row['Commissioned Date']) else '',
                'tariff': row['Tariff'] if pd.notna(row['Tariff']) else '',
                'tariff_description': row['Tariff Description'] if pd.notna(row['Tariff Description']) else '',
                'installation_type': 'Non Domestic (Commercial)',
                'remaining_fit_years': remaining_fit if remaining_fit is not None else -1,
                'age_years': years_old if years_old is not None else -1,
                'repowering_window': repowering_window,
                'data_source': f'fit_part_{part_num}_clean.csv'
            }
            
            documents.append(doc_text)
            metadatas.append(metadata)
            ids.append(f"fit_{row['FIT ID']}")
            
            # Add in smaller batches
            if len(documents) >= 100:
                collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                total_added += len(documents)
                documents = []
                metadatas = []
                ids = []
                
                if total_added % 1000 == 0:
                    logger.info(f"    Added {total_added} records so far...")
        
        # Add remaining documents
        if documents:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            total_added += len(documents)
    
    final_count = collection.count()
    logger.info(f"\nFinal collection size: {final_count:,} documents")
    logger.info(f"Added {total_added:,} new records")
    
    # Verify
    if final_count >= 36000:
        logger.info("✓ SUCCESS: All non-domestic installations loaded!")
    else:
        logger.info(f"Still missing {36435 - final_count:,} records")

if __name__ == "__main__":
    load_remaining_nondomestic()