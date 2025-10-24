#!/usr/bin/env python3
"""
Analyze ALL commercial FIT technologies - not just solar
Excludes domestic installations
"""

import pandas as pd
import json
from datetime import datetime

# Load the FIT data from multiple files
print("Loading FIT data from multiple files...")
dfs = []
for i in range(1, 4):
    file_path = f'data/Feed-in Tariff Installation Report Part {i}.xlsx'
    print(f"  Loading {file_path}...")
    df_part = pd.read_excel(file_path)
    dfs.append(df_part)
    
df = pd.concat(dfs, ignore_index=True)
print(f"Total installations loaded: {len(df):,}")

# Filter out domestic installations - keep only commercial
print("\nFiltering commercial installations only...")
commercial_df = df[df['Installation Type'].str.contains('Non Domestic|Community', case=False, na=False)]

print(f"Total commercial installations: {len(commercial_df):,}")
print(f"Total commercial capacity: {commercial_df['Installed capacity'].sum()/1000:.1f} MW")

# Analyze by technology
print("\n" + "="*60)
print("COMMERCIAL INSTALLATIONS BY TECHNOLOGY:")
print("="*60)

tech_summary = commercial_df.groupby('Technology').agg({
    'Installed capacity': ['count', 'sum', 'mean'],
    'Tariff (p/kWh) - (FiT & Export)': 'mean'
}).round(2)

tech_summary.columns = ['Count', 'Total kW', 'Avg kW', 'Avg Tariff']
tech_summary['Total MW'] = (tech_summary['Total kW'] / 1000).round(1)

# Sort by total capacity
tech_summary = tech_summary.sort_values('Total MW', ascending=False)

print(tech_summary)

# Detailed breakdown
print("\n" + "="*60)
print("DETAILED TECHNOLOGY ANALYSIS:")
print("="*60)

for tech in commercial_df['Technology'].unique():
    tech_df = commercial_df[commercial_df['Technology'] == tech]
    
    print(f"\n{tech}:")
    print(f"  Sites: {len(tech_df):,}")
    print(f"  Total Capacity: {tech_df['Installed capacity'].sum()/1000:.1f} MW")
    print(f"  Average Size: {tech_df['Installed capacity'].mean():.1f} kW")
    print(f"  Size Range: {tech_df['Installed capacity'].min():.1f} - {tech_df['Installed capacity'].max():.1f} kW")
    
    # Size distribution
    size_bins = [0, 10, 50, 100, 250, 500, 1000, 5000, 50000]
    size_labels = ['0-10kW', '10-50kW', '50-100kW', '100-250kW', '250-500kW', '500-1000kW', '1-5MW', '>5MW']
    tech_df['size_category'] = pd.cut(tech_df['Installed capacity'], bins=size_bins, labels=size_labels)
    size_dist = tech_df['size_category'].value_counts().sort_index()
    
    print("  Size Distribution:")
    for category, count in size_dist.items():
        if count > 0:
            print(f"    {category}: {count} sites")

# Check installation types to ensure we're getting all commercial
print("\n" + "="*60)
print("INSTALLATION TYPES IN COMMERCIAL DATA:")
print("="*60)
print(commercial_df['Installation Type'].value_counts())

# Save all commercial data
print("\n" + "="*60)
print("SAVING ALL COMMERCIAL FIT DATA...")
print("="*60)

# Process all commercial installations
commercial_sites = []

for _, row in commercial_df.iterrows():
    # Calculate age and remaining FIT
    commission_date = pd.to_datetime(row['Commissioning date'])
    age_years = (datetime.now() - commission_date).days / 365.25
    
    # FIT periods by technology
    if row['Technology'] == 'Photovoltaic':
        fit_period = 20
    elif row['Technology'] in ['Wind', 'Hydro']:
        fit_period = 20
    elif row['Technology'] == 'Anaerobic digestion':
        fit_period = 20
    elif row['Technology'] == 'Micro CHP':
        fit_period = 10
    else:
        fit_period = 20  # Default
    
    remaining_fit = fit_period - age_years
    
    # Determine repowering window
    if remaining_fit < 2:
        window = 'IMMEDIATE'
    elif remaining_fit < 5:
        window = 'URGENT'
    elif remaining_fit < 10:
        window = 'OPTIMAL'
    elif remaining_fit < 15:
        window = 'PLANNING'
    else:
        window = 'FUTURE'
    
    site = {
        'technology': row['Technology'],
        'installation_type': row['Installation Type'],
        'capacity_kw': row['Installed capacity'],
        'capacity_mw': row['Installed capacity'] / 1000,
        'tariff_p_kwh': row['Tariff (p/kWh) - (FiT & Export)'],
        'commissioning_date': commission_date.isoformat(),
        'age_years': age_years,
        'remaining_fit_years': remaining_fit,
        'repowering_window': window,
        'postcode': row['Postcode'],
        'local_authority': row['Local authority'],
        'government_office_region': row['Government office region'],
        'country': row['Country']
    }
    
    # Estimate annual generation by technology
    capacity_factors = {
        'Photovoltaic': 0.11,
        'Wind': 0.27,
        'Hydro': 0.38,
        'Anaerobic digestion': 0.80,
        'Micro CHP': 0.50
    }
    
    cf = capacity_factors.get(row['Technology'], 0.20)
    site['annual_generation_mwh'] = site['capacity_mw'] * 8760 * cf
    site['annual_fit_revenue_gbp'] = site['annual_generation_mwh'] * 1000 * site['tariff_p_kwh'] / 100
    
    commercial_sites.append(site)

# Save to JSON
output_data = {
    'generated': datetime.now().isoformat(),
    'total_sites': len(commercial_sites),
    'total_capacity_mw': sum(s['capacity_mw'] for s in commercial_sites),
    'technologies': list(commercial_df['Technology'].unique()),
    'sites': commercial_sites
}

with open('data/all_commercial_fit.json', 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"Saved {len(commercial_sites):,} commercial sites to data/all_commercial_fit.json")

# Summary by technology for the new file
tech_counts = {}
for site in commercial_sites:
    tech = site['technology']
    if tech not in tech_counts:
        tech_counts[tech] = {'count': 0, 'capacity_mw': 0}
    tech_counts[tech]['count'] += 1
    tech_counts[tech]['capacity_mw'] += site['capacity_mw']

print("\nFinal Summary:")
for tech, data in sorted(tech_counts.items(), key=lambda x: x[1]['capacity_mw'], reverse=True):
    print(f"  {tech}: {data['count']:,} sites, {data['capacity_mw']:.1f} MW")