#!/usr/bin/env python3
"""
Check ChromaDB coverage of non-domestic FIT installations
"""

import chromadb
from chromadb.utils import embedding_functions
import pandas as pd

print("Checking ChromaDB coverage of non-domestic FIT installations...")
print("="*60)

# Initialize Chroma
client = chromadb.PersistentClient(path="./chroma_db")

# Get all collections
collections = client.list_collections()
print(f"Available collections: {[c.name for c in collections]}")

# Check each collection
for collection in collections:
    print(f"\nCollection: {collection.name}")
    print(f"  Document count: {collection.count()}")
    
    # Sample a few documents to check content
    if collection.count() > 0:
        sample = collection.get(limit=3)
        if sample['metadatas']:
            first_meta = sample['metadatas'][0]
            if 'installation_type' in first_meta:
                print(f"  Installation type: {first_meta.get('installation_type')}")
            if 'fit_id' in first_meta:
                print(f"  Sample FIT ID: {first_meta.get('fit_id')}")

print("\n" + "="*60)
print("Checking CSV files for non-domestic records...")

# Count non-domestic in each CSV
total_non_domestic = 0
all_fit_ids = set()

for part_num in [1, 2, 3]:
    csv_file = f'data/fit_part_{part_num}_clean.csv'
    print(f"\nReading {csv_file}...")
    
    df = pd.read_csv(csv_file)
    non_domestic = df[df['Installation Type'].str.contains('Non Domestic', case=False, na=False)]
    
    count = len(non_domestic)
    total_non_domestic += count
    
    # Collect all FIT IDs
    fit_ids = set(non_domestic['FIT ID'].astype(str).values)
    all_fit_ids.update(fit_ids)
    
    print(f"  Non-domestic installations: {count:,}")
    print(f"  Sample FIT IDs: {list(fit_ids)[:5]}")

print(f"\nTotal non-domestic installations across all CSVs: {total_non_domestic:,}")
print(f"Total unique FIT IDs: {len(all_fit_ids):,}")

# Check specific collection for non-domestic
print("\n" + "="*60)
print("Checking fit_licenses_nondomestic collection...")

try:
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    nondom_collection = client.get_collection(
        name="fit_licenses_nondomestic",
        embedding_function=embedding_function
    )
    
    current_count = nondom_collection.count()
    print(f"Current documents in fit_licenses_nondomestic: {current_count:,}")
    
    # Check if we have records from each part
    sample_ids_to_check = [
        ('Part 1', '10001'),  # Sample from part 1
        ('Part 2', '300001'), # Sample from part 2  
        ('Part 3', '764485')  # We know this is from part 3
    ]
    
    for part, fit_id in sample_ids_to_check:
        result = nondom_collection.get(ids=[f"fit_{fit_id}"])
        if result['ids']:
            print(f"  ✓ {part} - FIT ID {fit_id} found")
        else:
            print(f"  ✗ {part} - FIT ID {fit_id} NOT found")
    
    print(f"\nMissing records: {total_non_domestic - current_count:,}")
    
    if current_count < total_non_domestic:
        print("\n⚠️  NOT ALL non-domestic records are in ChromaDB!")
        print(f"   Need to add {total_non_domestic - current_count:,} more records")
    else:
        print("\n✓ All non-domestic records are in ChromaDB")
        
except Exception as e:
    print(f"Error accessing fit_licenses_nondomestic: {e}")
    print("Collection may not exist yet")