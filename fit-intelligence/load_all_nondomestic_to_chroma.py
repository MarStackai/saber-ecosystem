#!/usr/bin/env python3
"""
Load ALL non-domestic FIT installations into ChromaDB
This ensures we don't miss any commercial installations like FIT ID 764485
"""

import chromadb
from chromadb.utils import embedding_functions
import pandas as pd
from datetime import datetime
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_all_nondomestic():
    """Load all non-domestic FIT installations from the cleaned CSV"""
    
    logger.info("Loading ALL non-domestic FIT installations into ChromaDB...")
    
    # Initialize Chroma
    client = chromadb.PersistentClient(path="./chroma_db")
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    # Get or create collection for non-domestic licenses
    try:
        collection = client.get_collection(
            name="fit_licenses_nondomestic",
            embedding_function=embedding_function
        )
        logger.info(f"Found existing collection with {collection.count()} documents")
    except:
        collection = client.create_collection(
            name="fit_licenses_nondomestic",
            embedding_function=embedding_function
        )
        logger.info("Created new collection for non-domestic licenses")
    
    # Read the cleaned CSV
    logger.info("Reading cleaned FIT CSV...")
    df = pd.read_csv('data/fit_part_3_clean.csv')
    logger.info(f"Total rows in CSV: {len(df)}")
    
    # Filter for non-domestic installations
    non_domestic = df[df['Installation Type'].str.contains('Non Domestic', case=False, na=False)]
    logger.info(f"Found {len(non_domestic)} non-domestic installations")
    
    # Check if FIT ID 764485 is in there
    if '764485' in non_domestic['FIT ID'].astype(str).values:
        logger.info("✓ FIT ID 764485 found in non-domestic data!")
        fit_764485 = non_domestic[non_domestic['FIT ID'].astype(str) == '764485'].iloc[0]
        logger.info(f"  Technology: {fit_764485['Technology']}")
        logger.info(f"  Capacity: {fit_764485['Installed capacity']} kW")
        logger.info(f"  Postcode: {fit_764485['PostCode ']}")
        logger.info(f"  Location: {fit_764485['Local Authority']}, {fit_764485['Government Office Region']}")
    
    # Rename columns to match expected names
    column_mapping = {
        'PostCode ': 'Postcode',
        'Installed capacity': 'Capacity (kW)',
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
    
    # Prepare documents for Chroma
    documents = []
    metadatas = []
    ids = []
    
    logger.info("Processing non-domestic records for Chroma...")
    for idx, row in non_domestic.iterrows():
        # Create comprehensive text for embedding
        doc_text = f"""
        FIT ID: {row['FIT ID']}
        Technology: {row['Technology']}
        Capacity: {row['Capacity (kW)']} kW
        Location: {row['Local Authority']} - {row['Region']} - {row['Country']}
        Postcode: {row['Postcode']}
        Installation Date: {row['Commissioned Date']}
        Tariff: {row['Tariff']}
        Installation Type: Non Domestic (Commercial)
        """
        
        # Calculate remaining FIT years
        try:
            if pd.notna(row['Commissioned Date']):
                commissioned = pd.to_datetime(row['Commissioned Date'])
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
        
        metadata = {
            'fit_id': str(row['FIT ID']),
            'technology': row['Technology'],
            'capacity_kw': float(row['Capacity (kW)']) if pd.notna(row['Capacity (kW)']) else 0,
            'capacity_mw': float(row['Capacity (kW)']) / 1000 if pd.notna(row['Capacity (kW)']) else 0,
            'postcode': row['Postcode'] if pd.notna(row['Postcode']) else '',
            'location': f"{row['Local Authority']} - {row['Region']} - {row['Country']}",
            'region': row['Region'] if pd.notna(row['Region']) else '',
            'country': row['Country'] if pd.notna(row['Country']) else '',
            'local_authority': row['Local Authority'] if pd.notna(row['Local Authority']) else '',
            'commissioned_date': str(row['Commissioned Date']) if pd.notna(row['Commissioned Date']) else '',
            'tariff': row['Tariff'] if pd.notna(row['Tariff']) else '',
            'tariff_description': row['Tariff Description'] if pd.notna(row['Tariff Description']) else '',
            'installation_type': 'Non Domestic (Commercial)',
            'remaining_fit_years': remaining_fit,
            'age_years': years_old,
            'repowering_window': repowering_window,
            'community_school': row['Community/School'] if pd.notna(row['Community/School']) else '',
            'llsoa': row['LLSOA'] if pd.notna(row['LLSOA']) else '',
            'msoa': row['MSOA'] if pd.notna(row['MSOA']) else ''
        }
        
        documents.append(doc_text)
        metadatas.append(metadata)
        ids.append(f"fit_{row['FIT ID']}")
    
    # Add to Chroma in batches
    if documents:
        logger.info(f"Adding {len(documents)} non-domestic installations to Chroma...")
        
        batch_size = 500
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_meta = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            collection.upsert(
                documents=batch_docs,
                metadatas=batch_meta,
                ids=batch_ids
            )
            logger.info(f"Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
        
        logger.info("Successfully added all non-domestic records to Chroma")
        
        # Verify FIT ID 764485
        result = collection.get(ids=["fit_764485"])
        if result['ids']:
            logger.info("✓ FIT ID 764485 successfully verified in Chroma!")
            metadata = result['metadatas'][0]
            logger.info(f"  Technology: {metadata['technology']}")
            logger.info(f"  Capacity: {metadata['capacity_kw']} kW")
            logger.info(f"  Location: {metadata['location']}")
            logger.info(f"  Postcode: {metadata['postcode']}")
            logger.info(f"  Repowering Window: {metadata['repowering_window']}")
            logger.info(f"  FIT Remaining: {metadata['remaining_fit_years']:.1f} years")
        else:
            logger.warning("Failed to verify FIT ID 764485 in Chroma")
    
    logger.info(f"Collection now has {collection.count()} total documents")
    
    # Update the intelligence API to use this collection
    logger.info("\nIMPORTANT: Update enhanced_fit_intelligence_api.py to include 'fit_licenses_nondomestic' collection")

if __name__ == "__main__":
    load_all_nondomestic()