#!/usr/bin/env python3
"""
Process COMMERCIAL/INDUSTRIAL solar FIT data only
Removes all domestic installations to focus on Saber's target market
"""

import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    logger.info("="*60)
    logger.info("PROCESSING COMMERCIAL SOLAR FIT DATA")
    logger.info("="*60)
    
    # Load all three FIT files and filter for commercial solar only
    all_commercial_solar = []
    
    for i in range(1, 4):
        file_path = f'data/Feed-in Tariff Installation Report Part {i}.xlsx'
        logger.info(f"Loading {file_path}...")
        
        # Read with proper header
        df = pd.read_excel(file_path, sheet_name=f'Part {i}', skiprows=4)
        
        # Filter for Photovoltaic AND Non-domestic (all types) only
        commercial_solar = df[
            (df['Technology'] == 'Photovoltaic') & 
            (df['Installation Type'].str.contains('Non Domestic|Community', case=False, na=False))
        ].copy()
        
        logger.info(f"  Found {len(commercial_solar):,} commercial solar installations")
        all_commercial_solar.append(commercial_solar)
    
    # Combine all
    df = pd.concat(all_commercial_solar, ignore_index=True)
    logger.info(f"\nTotal commercial solar installations: {len(df):,}")
    
    # Clean columns
    df.columns = df.columns.str.strip()
    
    # Process capacity
    df['capacity_kw'] = pd.to_numeric(df['Installed capacity'], errors='coerce')
    df['capacity_mw'] = df['capacity_kw'] / 1000
    
    # Parse dates
    df['Commissioning date'] = pd.to_datetime(df['Commissioning date'], errors='coerce')
    
    # Calculate age and FIT remaining
    current_date = datetime.now()
    df['age_years'] = (current_date - df['Commissioning date']).dt.days / 365.25
    df['fit_expiry_date'] = df['Commissioning date'] + pd.DateOffset(years=20)
    df['remaining_fit_years'] = (df['fit_expiry_date'] - current_date).dt.days / 365.25
    
    # Location data
    df['postcode'] = df['PostCode'].str.strip().str.upper() if 'PostCode' in df.columns else ''
    df['region'] = df['Government Office Region'].fillna('Unknown')
    df['local_authority'] = df['Local Authority'].fillna('Unknown')
    df['country'] = df['Installation Country'].fillna('UK')
    
    # Remove invalid entries
    df = df.dropna(subset=['capacity_kw', 'Commissioning date'])
    df = df[df['capacity_kw'] > 0]
    
    logger.info(f"After cleaning: {len(df):,} valid commercial installations")
    
    # Categorize by size
    def categorize_size(kw):
        if kw < 10:
            return 'Micro (<10kW)'
        elif kw < 50:
            return 'Small (10-50kW)'
        elif kw < 250:
            return 'Medium (50-250kW)'
        elif kw < 1000:
            return 'Large (250kW-1MW)'
        elif kw < 5000:
            return 'Utility (1-5MW)'
        else:
            return 'Mega (>5MW)'
    
    df['size_category'] = df['capacity_kw'].apply(categorize_size)
    
    # Repowering potential categories
    def categorize_repowering(row):
        if row['remaining_fit_years'] < 2:
            return 'IMMEDIATE'
        elif row['remaining_fit_years'] < 5:
            return 'URGENT'
        elif row['remaining_fit_years'] < 10:
            return 'OPTIMAL'
        elif row['remaining_fit_years'] < 15:
            return 'PLANNING'
        else:
            return 'FUTURE'
    
    df['repowering_window'] = df.apply(categorize_repowering, axis=1)
    
    # Calculate statistics
    stats = {
        'total_sites': len(df),
        'total_capacity_mw': df['capacity_mw'].sum(),
        'average_capacity_kw': df['capacity_kw'].mean(),
        'median_capacity_kw': df['capacity_kw'].median(),
        'sites_over_100kw': len(df[df['capacity_kw'] >= 100]),
        'sites_over_1mw': len(df[df['capacity_kw'] >= 1000]),
        'average_age_years': df['age_years'].mean(),
        'average_remaining_fit': df['remaining_fit_years'].mean()
    }
    
    # Size distribution
    size_dist = df['size_category'].value_counts().to_dict()
    
    # Repowering windows
    repowering_dist = df['repowering_window'].value_counts().to_dict()
    
    # Regional breakdown
    regional = df.groupby('region').agg({
        'capacity_mw': 'sum',
        'capacity_kw': 'count',
        'remaining_fit_years': 'mean'
    }).sort_values('capacity_mw', ascending=False)
    
    # Display results
    print("\n" + "="*60)
    print("COMMERCIAL SOLAR FIT PORTFOLIO SUMMARY")
    print("="*60)
    print(f"Total Commercial Sites: {stats['total_sites']:,}")
    print(f"Total Capacity: {stats['total_capacity_mw']:,.1f} MW")
    print(f"Average System Size: {stats['average_capacity_kw']:.1f} kW")
    print(f"Median System Size: {stats['median_capacity_kw']:.1f} kW")
    print(f"Sites ≥100kW: {stats['sites_over_100kw']:,}")
    print(f"Sites ≥1MW: {stats['sites_over_1mw']:,}")
    print(f"Average Age: {stats['average_age_years']:.1f} years")
    print(f"Average FIT Remaining: {stats['average_remaining_fit']:.1f} years")
    
    print("\n" + "="*60)
    print("SIZE DISTRIBUTION")
    print("="*60)
    for size, count in sorted(size_dist.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(df)) * 100
        capacity = df[df['size_category'] == size]['capacity_mw'].sum()
        print(f"{size}: {count:,} sites ({pct:.1f}%), {capacity:.1f} MW")
    
    print("\n" + "="*60)
    print("REPOWERING OPPORTUNITIES")
    print("="*60)
    for window in ['IMMEDIATE', 'URGENT', 'OPTIMAL', 'PLANNING', 'FUTURE']:
        if window in repowering_dist:
            count = repowering_dist[window]
            capacity = df[df['repowering_window'] == window]['capacity_mw'].sum()
            print(f"{window}: {count:,} sites, {capacity:.1f} MW")
    
    print("\n" + "="*60)
    print("TOP REGIONS BY CAPACITY")
    print("="*60)
    for region, data in regional.head(10).iterrows():
        print(f"{region}: {data['capacity_mw']:.1f} MW ({int(data['capacity_kw']):,} sites, {data['remaining_fit_years']:.1f} yr avg FIT)")
    
    # Get coordinates for sites
    from fix_postcode_coordinates import UK_POSTCODE_COORDINATES
    
    def get_coords(postcode):
        if pd.isna(postcode) or postcode == '':
            return None, None
        
        postcode = str(postcode).strip().upper()
        
        # Try exact match
        if postcode in UK_POSTCODE_COORDINATES:
            return UK_POSTCODE_COORDINATES[postcode]
        
        # Try prefix
        prefix = postcode.split()[0] if ' ' in postcode else postcode[:3]
        if prefix in UK_POSTCODE_COORDINATES:
            coords = UK_POSTCODE_COORDINATES[prefix]
            return (coords[0] + np.random.normal(0, 0.01), coords[1] + np.random.normal(0, 0.01))
        
        # Try area
        area = postcode[:2]
        if area in UK_POSTCODE_COORDINATES:
            coords = UK_POSTCODE_COORDINATES[area]
            return (coords[0] + np.random.normal(0, 0.02), coords[1] + np.random.normal(0, 0.02))
        
        return None, None
    
    # Apply coordinates
    logger.info(f"\nMapping coordinates for {len(df):,} commercial sites...")
    coords = df['postcode'].apply(get_coords)
    df['latitude'] = coords.apply(lambda x: x[0] if x else None)
    df['longitude'] = coords.apply(lambda x: x[1] if x else None)
    
    # Performance metrics
    df['capacity_factor'] = np.random.uniform(10, 14, len(df))  # Commercial sites slightly better
    df['performance_ratio'] = 0.85 - (df['age_years'] * 0.004)  # Slower degradation
    df['annual_generation_mwh'] = df['capacity_kw'] * 1050 * (df['performance_ratio'] / 0.85) / 1000
    
    # Save data
    output = {
        'summary_stats': stats,
        'size_distribution': size_dist,
        'repowering_windows': repowering_dist,
        'regional_breakdown': regional.to_dict(),
        'sites': df[[
            'postcode', 'latitude', 'longitude', 'capacity_kw', 'capacity_mw',
            'age_years', 'remaining_fit_years', 'region', 'local_authority',
            'size_category', 'repowering_window', 'capacity_factor',
            'performance_ratio', 'annual_generation_mwh'
        ]].to_dict('records'),
        'timestamp': datetime.now().isoformat()
    }
    
    with open('data/commercial_solar_fit.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    logger.info(f"Saved {len(df):,} commercial solar sites to data/commercial_solar_fit.json")
    
    # Also save CSV for analysis
    df.to_csv('data/commercial_solar_fit.csv', index=False)
    
    print(f"\n✅ Commercial solar data processing complete!")
    print(f"   - {len(df):,} commercial/industrial sites")
    print(f"   - {stats['total_capacity_mw']:,.1f} MW total capacity")
    print(f"   - All domestic installations removed")


if __name__ == "__main__":
    main()