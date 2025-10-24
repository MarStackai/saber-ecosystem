#!/usr/bin/env python3
"""
Verify complete coverage of all non-domestic installations
"""

import chromadb
from chromadb.utils import embedding_functions
import pandas as pd

print("Verifying complete coverage of non-domestic FIT installations")
print("="*60)

# Initialize Chroma
client = chromadb.PersistentClient(path="./chroma_db")
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_collection(
    name="fit_licenses_nondomestic",
    embedding_function=embedding_function
)

print(f"ChromaDB collection has {collection.count():,} documents")

# Test specific FIT IDs from each part
test_cases = [
    # Part 1 samples
    ('49464', 'Part 1'),
    ('192768', 'Part 1'),
    ('3802', 'Part 1'),
    
    # Part 2 samples
    ('364863', 'Part 2'),
    ('461806', 'Part 2'),
    ('368339', 'Part 2'),
    
    # Part 3 samples
    ('764485', 'Part 3'),
    ('654486', 'Part 3'),
    ('676166', 'Part 3')
]

print("\nVerifying sample FIT IDs from each part:")
print("-"*60)

all_found = True
for fit_id, part in test_cases:
    result = collection.get(ids=[f"fit_{fit_id}"])
    if result['ids']:
        metadata = result['metadatas'][0]
        print(f"✓ {part} - FIT ID {fit_id}: {metadata['technology']} - {metadata['capacity_kw']:.0f}kW - {metadata['location']}")
    else:
        print(f"✗ {part} - FIT ID {fit_id} NOT FOUND")
        all_found = False

print("\n" + "="*60)

# Count by data source
print("Checking data source distribution...")
sample_size = min(5000, collection.count())
sample = collection.get(limit=sample_size)

source_counts = {}
for metadata in sample['metadatas']:
    source = metadata.get('data_source', 'unknown')
    source_counts[source] = source_counts.get(source, 0) + 1

print(f"Sample of {sample_size} records shows:")
for source, count in sorted(source_counts.items()):
    estimated_total = int(count * collection.count() / sample_size)
    print(f"  {source}: ~{estimated_total:,} records")

print("\n" + "="*60)

# Summary
expected_total = 12037 + 9321 + 15077  # From CSV counts
actual_total = collection.count()

if actual_total == expected_total:
    print(f"✓ SUCCESS: All {expected_total:,} non-domestic installations are in ChromaDB!")
    print("  - Part 1: 12,037 records")
    print("  - Part 2: 9,321 records")
    print("  - Part 3: 15,077 records")
    print(f"  - Total: {expected_total:,} records")
elif actual_total > expected_total:
    print(f"⚠️  Warning: Have {actual_total:,} records but expected {expected_total:,}")
    print("  May have duplicates")
else:
    print(f"✗ Missing {expected_total - actual_total:,} records")
    print(f"  Expected: {expected_total:,}")
    print(f"  Actual: {actual_total:,}")

if all_found:
    print("\n✓ All test FIT IDs found successfully!")
else:
    print("\n✗ Some test FIT IDs were not found")