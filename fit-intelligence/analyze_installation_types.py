#!/usr/bin/env python3
"""
Analyze installation types to understand the discrepancy
"""

import pandas as pd
from collections import Counter

print("Analyzing Installation Types in CSV files")
print("="*60)

total_commercial = 0
all_commercial_fit_ids = set()

for part_num in [1, 2, 3]:
    csv_file = f'data/fit_part_{part_num}_clean.csv'
    print(f"\n{csv_file}:")
    
    df = pd.read_csv(csv_file)
    
    # Count by installation type
    install_types = df['Installation Type'].value_counts()
    print("Installation Type breakdown:")
    for install_type, count in install_types.items():
        print(f"  {install_type}: {count:,}")
    
    # Count commercial (Non Domestic + Community)
    commercial = df[df['Installation Type'].str.contains('Non Domestic|Community', case=False, na=False)]
    print(f"\nCommercial (Non Domestic + Community): {len(commercial):,}")
    
    # Get unique FIT IDs
    commercial_fit_ids = set(commercial['FIT ID'].astype(str).values)
    all_commercial_fit_ids.update(commercial_fit_ids)
    total_commercial += len(commercial)
    
    # Break down commercial
    non_domestic = df[df['Installation Type'].str.contains('Non Domestic', case=False, na=False)]
    community = df[df['Installation Type'].str.contains('Community', case=False, na=False)]
    print(f"  - Non Domestic only: {len(non_domestic):,}")
    print(f"  - Community only: {len(community):,}")

print("\n" + "="*60)
print("TOTAL ACROSS ALL 3 PARTS:")
print(f"Total commercial records (with possible duplicates): {total_commercial:,}")
print(f"Unique commercial FIT IDs: {len(all_commercial_fit_ids):,}")

# Now check what the all_commercial_fit.json was created from
print("\n" + "="*60)
print("Checking what criteria was used for all_commercial_fit.json...")

# Look at the script that created it
try:
    with open('analyze_all_commercial_fit.py', 'r') as f:
        content = f.read()
        if 'Non Domestic|Community' in content:
            print("✓ all_commercial_fit.json includes BOTH Non Domestic AND Community installations")
        elif 'Non Domestic' in content:
            print("all_commercial_fit.json includes only Non Domestic installations")
        print("\nRelevant line from analyze_all_commercial_fit.py:")
        for line in content.split('\n'):
            if 'Installation Type' in line and ('Non Domestic' in line or 'Community' in line):
                print(f"  {line.strip()}")
except Exception as e:
    print(f"Could not read analyze_all_commercial_fit.py: {e}")

print("\n" + "="*60)
print("CONCLUSION:")
print(f"1. CSV files have {len(all_commercial_fit_ids):,} unique commercial (Non Domestic + Community) FIT IDs")
print(f"2. commercial_fit_sites collection has 40,194 documents")
print(f"3. fit_licenses_nondomestic has 36,435 documents (Non Domestic only)")
print(f"\nThe difference is likely:")
print("- Community installations are included in commercial_fit_sites but not fit_licenses_nondomestic")
print("- Some duplicates or different data processing between JSON and CSV")