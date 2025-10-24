#!/usr/bin/env python3
"""
Direct test to find FIT ID 764485 in ChromaDB
"""

import chromadb
from chromadb.utils import embedding_functions

# Initialize Chroma
client = chromadb.PersistentClient(path="./chroma_db")
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Get the non-domestic collection
collection = client.get_collection(
    name="fit_licenses_nondomestic",
    embedding_function=embedding_function
)

print(f"Collection has {collection.count()} documents")

# Try direct ID lookup
print("\n1. Direct ID lookup for fit_764485:")
result = collection.get(ids=["fit_764485"])
if result['ids']:
    print("✓ Found by direct ID!")
    print(f"  Metadata: {result['metadatas'][0]}")
else:
    print("✗ Not found by direct ID")

# Try semantic search
print("\n2. Semantic search for 'FIT ID 764485':")
results = collection.query(
    query_texts=["FIT ID 764485"],
    n_results=5
)

if results['ids'][0]:
    print(f"Found {len(results['ids'][0])} results")
    for i, (id_val, metadata, distance) in enumerate(zip(
        results['ids'][0], 
        results['metadatas'][0], 
        results['distances'][0]
    )):
        fit_id = metadata.get('fit_id', 'N/A')
        if fit_id == '764485':
            print(f"✓ Found FIT ID 764485!")
            print(f"  Document ID: {id_val}")
            print(f"  Distance: {distance}")
            print(f"  Technology: {metadata.get('technology')}")
            print(f"  Capacity: {metadata.get('capacity_kw')} kW")
            print(f"  Location: {metadata.get('location')}")
            break
        else:
            print(f"  Result {i+1}: FIT ID {fit_id} (distance: {distance:.3f})")

# Try search by location
print("\n3. Search for LL53 postcode:")
results = collection.query(
    query_texts=["LL53 Wind Gwynedd"],
    n_results=10
)

if results['ids'][0]:
    for metadata in results['metadatas'][0]:
        if metadata.get('postcode') == 'LL53' and metadata.get('technology') == 'Wind':
            print(f"Found Wind installation in LL53:")
            print(f"  FIT ID: {metadata.get('fit_id')}")
            print(f"  Capacity: {metadata.get('capacity_kw')} kW")
            if metadata.get('fit_id') == '764485':
                print("  ✓ This is FIT ID 764485!")
                break