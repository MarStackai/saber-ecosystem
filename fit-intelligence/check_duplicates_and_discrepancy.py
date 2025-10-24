#!/usr/bin/env python3
"""
Check for duplicates and investigate the discrepancy in counts
"""

import chromadb
from chromadb.utils import embedding_functions
import pandas as pd
import json
from collections import Counter

print("Investigating duplicates and count discrepancy")
print("="*60)

# Initialize Chroma
client = chromadb.PersistentClient(path="./chroma_db")

# Check all collections
collections_info = {}
for collection in client.list_collections():
    count = collection.count()
    collections_info[collection.name] = count
    print(f"{collection.name}: {count:,} documents")

print("\n" + "="*60)
print("Checking commercial_fit_sites collection (40,194 documents)...")

# Get the commercial collection
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

commercial_collection = client.get_collection(
    name="commercial_fit_sites",
    embedding_function=embedding_function
)

print(f"Commercial collection has {commercial_collection.count():,} documents")

# Sample to check what's in commercial collection
sample = commercial_collection.get(limit=10)
print("\nSample from commercial_fit_sites:")
for i, metadata in enumerate(sample['metadatas'][:5], 1):
    print(f"{i}. Tech: {metadata.get('technology', 'N/A')}, "
          f"Capacity: {metadata.get('capacity_mw', 0):.2f} MW, "
          f"Site ID: {metadata.get('site_id', 'N/A')}, "
          f"Postcode: {metadata.get('postcode', 'N/A')}")

# Check the JSON file that feeds commercial collection
print("\n" + "="*60)
print("Checking source data...")

try:
    with open('data/all_commercial_fit.json', 'r') as f:
        commercial_data = json.load(f)
    print(f"all_commercial_fit.json has {len(commercial_data.get('sites', []))} sites")
    
    # Check technologies in JSON
    tech_counts = Counter()
    for site in commercial_data['sites']:
        tech_counts[site.get('technology', 'Unknown')] += 1
    
    print("\nTechnology breakdown in all_commercial_fit.json:")
    for tech, count in tech_counts.most_common():
        print(f"  {tech}: {count:,}")
        
except Exception as e:
    print(f"Error reading all_commercial_fit.json: {e}")

print("\n" + "="*60)
print("Checking for duplicates in fit_licenses_nondomestic...")

nondom_collection = client.get_collection(
    name="fit_licenses_nondomestic",
    embedding_function=embedding_function
)

# Get all FIT IDs to check for duplicates
print(f"Analyzing {nondom_collection.count():,} documents for duplicates...")

all_fit_ids = []
all_doc_ids = []
batch_size = 1000
total = nondom_collection.count()

for offset in range(0, total, batch_size):
    batch = nondom_collection.get(limit=batch_size, offset=offset)
    for doc_id, metadata in zip(batch['ids'], batch['metadatas']):
        fit_id = metadata.get('fit_id', 'unknown')
        all_fit_ids.append(fit_id)
        all_doc_ids.append(doc_id)
    
    if offset % 5000 == 0:
        print(f"  Processed {offset:,}/{total:,} documents...")

# Check for duplicates
fit_id_counts = Counter(all_fit_ids)
duplicates = {fit_id: count for fit_id, count in fit_id_counts.items() if count > 1}

if duplicates:
    print(f"\n⚠️ Found {len(duplicates)} FIT IDs with duplicates:")
    for fit_id, count in list(duplicates.items())[:10]:
        print(f"  FIT ID {fit_id}: appears {count} times")
else:
    print("\n✓ No duplicate FIT IDs found")

# Check document ID duplicates
doc_id_counts = Counter(all_doc_ids)
doc_duplicates = {doc_id: count for doc_id, count in doc_id_counts.items() if count > 1}

if doc_duplicates:
    print(f"\n⚠️ Found {len(doc_duplicates)} duplicate document IDs:")
    for doc_id, count in list(doc_duplicates.items())[:10]:
        print(f"  Doc ID {doc_id}: appears {count} times")
else:
    print("✓ No duplicate document IDs found")

print("\n" + "="*60)
print("Checking CSV files for total non-domestic count...")

# Count unique FIT IDs across all CSVs
all_csv_fit_ids = set()
for part_num in [1, 2, 3]:
    csv_file = f'data/fit_part_{part_num}_clean.csv'
    df = pd.read_csv(csv_file)
    non_domestic = df[df['Installation Type'].str.contains('Non Domestic', case=False, na=False)]
    fit_ids = set(non_domestic['FIT ID'].astype(str).values)
    all_csv_fit_ids.update(fit_ids)
    print(f"Part {part_num}: {len(non_domestic):,} non-domestic records, {len(fit_ids):,} unique FIT IDs")

print(f"\nTotal unique non-domestic FIT IDs across all CSVs: {len(all_csv_fit_ids):,}")

print("\n" + "="*60)
print("SUMMARY:")
print(f"1. commercial_fit_sites collection: {collections_info.get('commercial_fit_sites', 0):,} documents")
print(f"2. fit_licenses_nondomestic collection: {collections_info.get('fit_licenses_nondomestic', 0):,} documents")
print(f"3. CSV files have {len(all_csv_fit_ids):,} unique non-domestic FIT IDs")
print(f"\nDiscrepancy: {collections_info.get('commercial_fit_sites', 0) - len(all_csv_fit_ids):,} extra records in commercial_fit_sites")
print("\nPossible reasons for discrepancy:")
print("- commercial_fit_sites may include Community installations (not just Non Domestic)")
print("- commercial_fit_sites may include synthetic/test data")
print("- commercial_fit_sites may have duplicates")
print("- Data sources may be different (JSON vs CSV)")