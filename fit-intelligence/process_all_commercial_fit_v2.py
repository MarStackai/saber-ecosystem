#!/usr/bin/env python3
"""
Process ALL commercial (non-domestic) FIT installations across all technologies
Includes: Solar (Photovoltaic), Wind, Hydro, Anaerobic Digestion, Micro CHP
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def process_commercial_fit():
    """Process all commercial FIT installations"""
    
    print("Loading FIT data from multiple files...")
    
    all_data = []
    
    # Load each part with correct header row (row 4, 0-indexed)
    for i in range(1, 4):
        file_path = f'data/Feed-in Tariff Installation Report Part {i}.xlsx'
        print(f"  Loading {file_path}...")
        
        # Read with header at row 4
        df = pd.read_excel(file_path, header=4)
        print(f"    Found {len(df):,} installations")
        all_data.append(df)
    
    # Combine all parts
    df = pd.concat(all_data, ignore_index=True)
    print(f"\nTotal installations loaded: {len(df):,}")
    
    # Show columns
    print(f"\nColumns found: {df.columns.tolist()[:10]}...")
    
    # Filter for commercial installations only
    # Looking for 'Installation' or 'Type' columns
    install_col = None
    for col in df.columns:
        if 'Installation' in str(col):
            install_col = col
            break
    
    if install_col:
        print(f"\nFiltering by '{install_col}'...")
        print(f"Unique installation types: {df[install_col].unique()}")
        
        # Filter for non-domestic/commercial
        commercial_mask = df[install_col].str.contains(
            'Non.?Domestic|Community|Commercial', 
            case=False, 
            na=False,
            regex=True
        )
        commercial_df = df[commercial_mask]
    else:
        # If no installation type column, assume all are relevant
        print("\nWarning: No installation type column found, processing all records")
        commercial_df = df
    
    print(f"\nCommercial installations: {len(commercial_df):,}")
    
    # Analyze by technology
    if 'Technology' in commercial_df.columns:
        print("\n" + "="*60)
        print("COMMERCIAL INSTALLATIONS BY TECHNOLOGY:")
        print("="*60)
        
        tech_summary = commercial_df.groupby('Technology').agg({
            'Installed capacity': ['count', 'sum', 'mean', 'min', 'max']
        }).round(2)
        
        tech_summary.columns = ['Count', 'Total kW', 'Avg kW', 'Min kW', 'Max kW']
        tech_summary['Total MW'] = (tech_summary['Total kW'] / 1000).round(1)
        tech_summary = tech_summary.sort_values('Total MW', ascending=False)
        
        print(tech_summary)
        
        # Process and save data
        save_all_commercial_data(commercial_df)
    else:
        print("Error: Technology column not found")
    
    return commercial_df

def save_all_commercial_data(df):
    """Save all commercial FIT data with business intelligence"""
    
    print("\n" + "="*60)
    print("PROCESSING COMMERCIAL FIT DATA FOR INTELLIGENCE SYSTEM...")
    print("="*60)
    
    sites = []
    
    # Capacity factors by technology (UK averages)
    capacity_factors = {
        'Photovoltaic': 0.11,
        'Wind': 0.27,
        'Hydro': 0.38,
        'Anaerobic digestion': 0.80,
        'Micro CHP': 0.50
    }
    
    # FIT periods by technology
    fit_periods = {
        'Photovoltaic': 20,
        'Wind': 20,
        'Hydro': 20,
        'Anaerobic digestion': 20,
        'Micro CHP': 10
    }
    
    for _, row in df.iterrows():
        try:
            # Parse commissioning date
            commission_date = pd.to_datetime(row.get('Commissioning date'))
            if pd.isna(commission_date):
                commission_date = pd.to_datetime(row.get('Application date', '2015-01-01'))
            
            age_years = (datetime.now() - commission_date).days / 365.25
            
            # Get technology and FIT period
            technology = str(row.get('Technology', 'Unknown'))
            fit_period = fit_periods.get(technology, 20)
            remaining_fit = fit_period - age_years
            
            # Determine repowering window
            if remaining_fit < 0:
                window = 'EXPIRED'
            elif remaining_fit < 2:
                window = 'IMMEDIATE'
            elif remaining_fit < 5:
                window = 'URGENT'
            elif remaining_fit < 10:
                window = 'OPTIMAL'
            elif remaining_fit < 15:
                window = 'PLANNING'
            else:
                window = 'FUTURE'
            
            # Get capacity
            capacity_kw = float(row.get('Installed capacity', 0))
            capacity_mw = capacity_kw / 1000
            
            # Calculate generation and revenue
            cf = capacity_factors.get(technology, 0.20)
            annual_generation_mwh = capacity_mw * 8760 * cf
            
            # Get tariff
            tariff = float(row.get('Tariff (p/kWh) - (FiT & Export)', 0))
            annual_fit_revenue = annual_generation_mwh * 1000 * tariff / 100
            
            site = {
                'technology': technology,
                'installation_type': str(row.get('Installation', 'Unknown')),
                'capacity_kw': capacity_kw,
                'capacity_mw': capacity_mw,
                'declared_net_capacity_kw': float(row.get('Declared net capacity', capacity_kw)),
                'tariff_p_kwh': tariff,
                'commission_date': commission_date.isoformat(),
                'age_years': round(age_years, 1),
                'remaining_fit_years': round(remaining_fit, 1),
                'repowering_window': window,
                'postcode': str(row.get('PostCode ', '')).strip(),
                'local_authority': str(row.get('Local authority', '')),
                'region': str(row.get('Government office region', '')),
                'country': str(row.get('Country', '')),
                'capacity_factor': cf,
                'annual_generation_mwh': round(annual_generation_mwh, 1),
                'annual_fit_revenue_gbp': round(annual_fit_revenue, 0),
                'fit_id': str(row.get('FIT ID', ''))
            }
            
            # Add business intelligence fields
            
            # PPA readiness score (0-100)
            ppa_readiness = 0
            if window == 'EXPIRED':
                ppa_readiness = 100  # Already needs PPA
            elif window == 'IMMEDIATE':
                ppa_readiness = 90
            elif window == 'URGENT':
                ppa_readiness = 70
            elif window == 'OPTIMAL':
                ppa_readiness = 50
            elif window == 'PLANNING':
                ppa_readiness = 30
            else:
                ppa_readiness = 10
            
            site['ppa_readiness_score'] = ppa_readiness
            
            # Size category for bundling opportunities
            if capacity_kw < 50:
                site['size_category'] = 'Micro (<50kW)'
            elif capacity_kw < 250:
                site['size_category'] = 'Small (50-250kW)'
            elif capacity_kw < 1000:
                site['size_category'] = 'Medium (250kW-1MW)'
            elif capacity_kw < 5000:
                site['size_category'] = 'Large (1-5MW)'
            else:
                site['size_category'] = 'Utility (>5MW)'
            
            # Grid connection assessment
            if capacity_mw < 1:
                site['grid_category'] = 'Distribution'
            elif capacity_mw < 10:
                site['grid_category'] = 'Primary'
            else:
                site['grid_category'] = 'Transmission'
            
            # Repowering potential
            if technology == 'Photovoltaic' and age_years > 10:
                site['repowering_potential'] = 'High'
                site['potential_capacity_increase_factor'] = 1.5
            elif technology == 'Wind' and age_years > 10:
                site['repowering_potential'] = 'Very High'
                site['potential_capacity_increase_factor'] = 2.5
            elif age_years > 15:
                site['repowering_potential'] = 'Medium'
                site['potential_capacity_increase_factor'] = 1.3
            else:
                site['repowering_potential'] = 'Low'
                site['potential_capacity_increase_factor'] = 1.0
            
            sites.append(site)
            
        except Exception as e:
            continue
    
    # Create summary statistics
    summary = {
        'generated': datetime.now().isoformat(),
        'total_sites': len(sites),
        'total_capacity_mw': round(sum(s['capacity_mw'] for s in sites), 1),
        'total_annual_generation_gwh': round(sum(s['annual_generation_mwh'] for s in sites) / 1000, 1),
        'total_annual_fit_revenue_million_gbp': round(sum(s['annual_fit_revenue_gbp'] for s in sites) / 1000000, 1),
        'by_technology': {},
        'by_repowering_window': {},
        'by_size_category': {},
        'immediate_opportunities': 0,
        'expired_fits': 0
    }
    
    # Group by technology
    for tech in set(s['technology'] for s in sites):
        tech_sites = [s for s in sites if s['technology'] == tech]
        summary['by_technology'][tech] = {
            'count': len(tech_sites),
            'capacity_mw': round(sum(s['capacity_mw'] for s in tech_sites), 1),
            'avg_age_years': round(np.mean([s['age_years'] for s in tech_sites]), 1),
            'avg_remaining_fit': round(np.mean([s['remaining_fit_years'] for s in tech_sites]), 1)
        }
    
    # Group by repowering window
    for window in ['EXPIRED', 'IMMEDIATE', 'URGENT', 'OPTIMAL', 'PLANNING', 'FUTURE']:
        window_sites = [s for s in sites if s['repowering_window'] == window]
        if window_sites:
            summary['by_repowering_window'][window] = {
                'count': len(window_sites),
                'capacity_mw': round(sum(s['capacity_mw'] for s in window_sites), 1)
            }
    
    # Count immediate opportunities
    summary['immediate_opportunities'] = len([s for s in sites if s['repowering_window'] in ['IMMEDIATE', 'URGENT']])
    summary['expired_fits'] = len([s for s in sites if s['repowering_window'] == 'EXPIRED'])
    
    # Save to JSON
    output = {
        'summary': summary,
        'sites': sites
    }
    
    with open('data/all_commercial_fit.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Saved {len(sites):,} commercial sites to data/all_commercial_fit.json")
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY - ALL COMMERCIAL FIT INSTALLATIONS:")
    print("="*60)
    print(f"Total Sites: {summary['total_sites']:,}")
    print(f"Total Capacity: {summary['total_capacity_mw']:.1f} MW")
    print(f"Annual Generation: {summary['total_annual_generation_gwh']:.1f} GWh")
    print(f"Annual FIT Revenue: £{summary['total_annual_fit_revenue_million_gbp']:.1f}M")
    print(f"\nImmediate PPA Opportunities: {summary['immediate_opportunities']:,}")
    print(f"Expired FITs (need PPA now): {summary['expired_fits']:,}")
    
    print("\nBy Technology:")
    for tech, stats in sorted(summary['by_technology'].items(), 
                             key=lambda x: x[1]['capacity_mw'], 
                             reverse=True):
        print(f"  {tech}:")
        print(f"    Sites: {stats['count']:,}")
        print(f"    Capacity: {stats['capacity_mw']:.1f} MW")
        print(f"    Avg Age: {stats['avg_age_years']:.1f} years")
        print(f"    Avg FIT Remaining: {stats['avg_remaining_fit']:.1f} years")
    
    print("\nBy Repowering Window:")
    for window, stats in summary['by_repowering_window'].items():
        print(f"  {window}: {stats['count']:,} sites ({stats['capacity_mw']:.1f} MW)")

if __name__ == "__main__":
    process_commercial_fit()