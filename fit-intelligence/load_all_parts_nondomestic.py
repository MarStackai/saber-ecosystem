#!/usr/bin/env python3
"""
Load ALL non-domestic FIT installations from all three CSV parts into ChromaDB
This ensures complete coverage of all commercial installations
"""

import chromadb
from chromadb.utils import embedding_functions
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_all_parts_nondomestic():
    """Load all non-domestic FIT installations from all three CSV parts"""
    
    logger.info("Loading ALL non-domestic FIT installations from all parts into ChromaDB...")
    
    # Initialize Chroma
    client = chromadb.PersistentClient(path="./chroma_db")
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    # Delete existing collection to start fresh with all data
    try:
        client.delete_collection(name="fit_licenses_nondomestic")
        logger.info("Deleted existing collection to reload with complete data")
    except:
        pass
    
    # Create new collection
    collection = client.create_collection(
        name="fit_licenses_nondomestic",
        embedding_function=embedding_function
    )
    logger.info("Created new collection for ALL non-domestic licenses")
    
    # Process all three parts
    all_documents = []
    all_metadatas = []
    all_ids = []
    
    for part_num in [1, 2, 3]:
        csv_file = f'data/fit_part_{part_num}_clean.csv'
        logger.info(f"\nProcessing {csv_file}...")
        
        # Read CSV
        df = pd.read_csv(csv_file)
        logger.info(f"  Total rows: {len(df)}")
        
        # Filter for non-domestic installations
        non_domestic = df[df['Installation Type'].str.contains('Non Domestic', case=False, na=False)]
        logger.info(f"  Non-domestic installations: {len(non_domestic)}")
        
        # Rename columns to match expected names
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
        non_domestic = non_domestic.rename(columns=column_mapping)
        
        # Process each record
        for idx, row in non_domestic.iterrows():
            # Create comprehensive text for embedding
            doc_text = f"""
            FIT ID: {row['FIT ID']}
            Technology: {row['Technology']}
            Capacity: {row.get('Capacity (kW)', row.get('Installed capacity', 0))} kW
            Location: {row['Local Authority']} - {row['Region']} - {row['Country']}
            Postcode: {row.get('Postcode', row.get('PostCode ', ''))}
            Installation Date: {row['Commissioned Date']}
            Tariff: {row['Tariff']}
            Installation Type: Non Domestic (Commercial)
            Part: {part_num}
            """
            
            # Calculate remaining FIT years
            try:
                commissioned_date = row['Commissioned Date']
                if pd.notna(commissioned_date):
                    commissioned = pd.to_datetime(commissioned_date)
                    years_old = (datetime.now() - commissioned).days / 365.25
                    remaining_fit = max(0, 20 - years_old)  # Assume 20 year FIT period
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
            
            # Get capacity value
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
                'community_school': row.get('Community/School', '') if pd.notna(row.get('Community/School', '')) else '',
                'llsoa': row.get('LLSOA', '') if pd.notna(row.get('LLSOA', '')) else '',
                'msoa': row.get('MSOA', '') if pd.notna(row.get('MSOA', '')) else '',
                'data_source': f'fit_part_{part_num}_clean.csv'
            }
            
            all_documents.append(doc_text)
            all_metadatas.append(metadata)
            all_ids.append(f"fit_{row['FIT ID']}")
        
        logger.info(f"  Processed {len(non_domestic)} records from Part {part_num}")
    
    # Add all to Chroma in batches
    total_records = len(all_documents)
    logger.info(f"\nAdding {total_records:,} total non-domestic installations to Chroma...")
    
    batch_size = 500
    for i in range(0, total_records, batch_size):
        batch_docs = all_documents[i:i+batch_size]
        batch_meta = all_metadatas[i:i+batch_size]
        batch_ids = all_ids[i:i+batch_size]
        
        collection.upsert(
            documents=batch_docs,
            metadatas=batch_meta,
            ids=batch_ids
        )
        
        if (i + batch_size) % 5000 == 0 or i + batch_size >= total_records:
            logger.info(f"  Progress: {min(i + batch_size, total_records):,}/{total_records:,} records added")
    
    logger.info("Successfully added all non-domestic records to Chroma")
    
    # Verify some known FIT IDs
    test_ids = [
        ('764485', 'Part 3'),  # We know this one
        ('49464', 'Part 1'),   # From Part 1
        ('364863', 'Part 2')   # From Part 2
    ]
    
    logger.info("\nVerifying sample FIT IDs...")
    for fit_id, part in test_ids:
        result = collection.get(ids=[f"fit_{fit_id}"])
        if result['ids']:
            metadata = result['metadatas'][0]
            logger.info(f"  ✓ {part} - FIT ID {fit_id}: {metadata['technology']} - {metadata['capacity_kw']}kW - {metadata['location']}")
        else:
            logger.warning(f"  ✗ {part} - FIT ID {fit_id} not found")
    
    final_count = collection.count()
    logger.info(f"\nFinal collection size: {final_count:,} documents")
    
    if final_count >= 36000:  # Should be around 36,435
        logger.info("✓ SUCCESS: All non-domestic installations loaded into ChromaDB!")
    else:
        logger.warning(f"⚠️  Warning: Expected ~36,435 records but only have {final_count:,}")

if __name__ == "__main__":
    load_all_parts_nondomestic()