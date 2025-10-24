#!/usr/bin/env python3
"""
Check the exact installation type values in the CSV files
"""

import pandas as pd
from collections import Counter

print("Checking exact Installation Type values")
print("="*60)

all_installation_types = Counter()

for part_num in [1, 2, 3]:
    csv_file = f'data/fit_part_{part_num}_clean.csv'
    print(f"\nAnalyzing {csv_file}...")
    
    df = pd.read_csv(csv_file)
    
    # Get all unique installation types
    install_types = df['Installation Type'].value_counts()
    
    print(f"Unique Installation Types in Part {part_num}:")
    for install_type, count in install_types.items():
        print(f"  '{install_type}': {count:,}")
        all_installation_types[install_type] += count
    
    # Check if any rows have both Community and Industrial
    print(f"\nChecking for overlap...")
    
    # Look for different patterns
    community_rows = df[df['Installation Type'].str.contains('Community', case=False, na=False)]
    industrial_rows = df[df['Installation Type'].str.contains('Industrial', case=False, na=False)]
    non_domestic_commercial = df[df['Installation Type'] == 'Non Domestic (Commercial)']
    non_domestic_industrial = df[df['Installation Type'] == 'Non Domestic (Industrial)']
    
    print(f"  Rows containing 'Community': {len(community_rows):,}")
    print(f"  Rows containing 'Industrial': {len(industrial_rows):,}")
    print(f"  Rows exactly 'Non Domestic (Commercial)': {len(non_domestic_commercial):,}")
    print(f"  Rows exactly 'Non Domestic (Industrial)': {len(non_domestic_industrial):,}")
    
    # Get unique values for Community rows
    if len(community_rows) > 0:
        community_types = community_rows['Installation Type'].unique()
        print(f"\n  Unique values for Community rows:")
        for ct in community_types:
            count = len(community_rows[community_rows['Installation Type'] == ct])
            print(f"    '{ct}': {count:,}")

print("\n" + "="*60)
print("TOTAL ACROSS ALL PARTS:")
print("-"*60)
for install_type, count in all_installation_types.most_common():
    print(f"'{install_type}': {count:,}")

print("\n" + "="*60)
print("SUMMARY:")
print("-"*60)

domestic_total = all_installation_types.get('Domestic', 0)
non_domestic_commercial = all_installation_types.get('Non Domestic (Commercial)', 0)
non_domestic_industrial = all_installation_types.get('Non Domestic (Industrial)', 0)
community = all_installation_types.get('Community', 0)

print(f"1. Domestic: {domestic_total:,}")
print(f"2. Non Domestic (Commercial): {non_domestic_commercial:,}")
print(f"3. Non Domestic (Industrial): {non_domestic_industrial:,}")
print(f"4. Community: {community:,}")
print(f"\nTotal Non Domestic: {non_domestic_commercial + non_domestic_industrial:,}")
print(f"Total Commercial (Non Domestic + Community): {non_domestic_commercial + non_domestic_industrial + community:,}")

print("\nANSWER: Community installations are a SEPARATE category, not part of Industrial.")