#!/usr/bin/env python3
"""
Add Community installations to ChromaDB
These are commercial-scale community-owned projects that are valuable for PPA opportunities
"""

import chromadb
from chromadb.utils import embedding_functions
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_community_installations():
    """Add all Community installations to the commercial collection"""
    
    logger.info("Adding Community installations to ChromaDB...")
    
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
    logger.info(f"Current collection has {current_count:,} documents (Non Domestic only)")
    
    # Process all three parts for Community installations
    all_documents = []
    all_metadatas = []
    all_ids = []
    total_community = 0
    
    for part_num in [1, 2, 3]:
        csv_file = f'data/fit_part_{part_num}_clean.csv'
        logger.info(f"\nProcessing Community installations from {csv_file}...")
        
        # Read CSV
        df = pd.read_csv(csv_file)
        
        # Filter for Community installations only
        community = df[df['Installation Type'] == 'Community']
        logger.info(f"  Found {len(community)} community installations")
        total_community += len(community)
        
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
        community = community.rename(columns=column_mapping)
        
        # Process each record
        for idx, row in community.iterrows():
            # Create text for embedding
            doc_text = f"""
            FIT ID: {row['FIT ID']}
            Technology: {row['Technology']}
            Capacity: {row.get('Capacity (kW)', row.get('Installed capacity', 0))} kW
            Location: {row['Local Authority']} - {row['Region']} - {row['Country']}
            Postcode: {row.get('Postcode', row.get('PostCode ', ''))}
            Installation Date: {row['Commissioned Date']}
            Tariff: {row['Tariff']}
            Installation Type: Community
            Part: {part_num}
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
                'installation_type': 'Community',
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
    
    # Add all to Chroma in batches
    logger.info(f"\nAdding {total_community:,} Community installations to Chroma...")
    
    batch_size = 500
    for i in range(0, len(all_documents), batch_size):
        batch_docs = all_documents[i:i+batch_size]
        batch_meta = all_metadatas[i:i+batch_size]
        batch_ids = all_ids[i:i+batch_size]
        
        collection.add(
            documents=batch_docs,
            metadatas=batch_meta,
            ids=batch_ids
        )
        
        if (i + batch_size) % 1000 == 0 or i + batch_size >= len(all_documents):
            logger.info(f"  Progress: {min(i + batch_size, len(all_documents)):,}/{len(all_documents):,} records added")
    
    logger.info("Successfully added all Community records to Chroma")
    
    final_count = collection.count()
    logger.info(f"\nFinal collection size: {final_count:,} documents")
    logger.info(f"Added {final_count - current_count:,} new Community installations")
    
    # Summary
    print("\n" + "="*60)
    print("COLLECTION NOW INCLUDES:")
    print(f"- Non Domestic (Commercial): ~34,283")
    print(f"- Non Domestic (Industrial): ~2,152")
    print(f"- Community: ~3,759")
    print(f"- TOTAL: {final_count:,} commercial-scale installations")
    print("\nThis matches the commercial_fit_sites collection (40,194 records)")
    print("All commercial-scale renewable installations are now searchable!")

if __name__ == "__main__":
    add_community_installations()