#!/usr/bin/env python3
"""
Process ALL commercial (non-domestic) FIT installations across all technologies
Includes: Solar, Wind, Hydro, Anaerobic Digestion, Micro CHP
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_fit_data():
    """Load and combine all FIT data files"""
    print("Loading FIT data from multiple files...")
    
    all_data = []
    
    for i in range(1, 4):
        file_path = f'data/Feed-in Tariff Installation Report Part {i}.xlsx'
        print(f"  Processing {file_path}...")
        
        # Read the file to find where actual data starts
        df_test = pd.read_excel(file_path, nrows=10)
        
        # Find the row with column headers (contains 'Technology' or 'Installation')
        header_row = None
        for idx in range(10):
            row_values = df_test.iloc[idx].astype(str).tolist()
            if any('Technology' in val for val in row_values) or any('Installation' in val for val in row_values):
                header_row = idx
                break
        
        if header_row is not None:
            # Read with correct header row
            df = pd.read_excel(file_path, header=header_row)
            print(f"    Found {len(df):,} rows with columns: {df.columns.tolist()[:5]}...")
            all_data.append(df)
        else:
            print(f"    Warning: Could not find header row in {file_path}")
    
    # Combine all dataframes
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"\nTotal installations loaded: {len(combined_df):,}")
        return combined_df
    else:
        print("Error: No data loaded")
        return pd.DataFrame()

def process_commercial_fit():
    """Process commercial FIT installations"""
    
    # Load data
    df = load_fit_data()
    
    if df.empty:
        return
    
    print("\nColumns found:", df.columns.tolist())
    
    # Identify the installation type column
    install_col = None
    for col in df.columns:
        if 'Installation' in col or 'Type' in col:
            install_col = col
            break
    
    if install_col:
        print(f"\nUsing column '{install_col}' for installation type")
        print(f"Installation types found: {df[install_col].unique()[:10]}")
        
        # Filter commercial only (non-domestic)
        commercial_mask = df[install_col].str.contains('Non Domestic|Non-Domestic|Community|Commercial', 
                                                       case=False, na=False)
        commercial_df = df[commercial_mask]
        
        print(f"\nCommercial installations: {len(commercial_df):,}")
        
        # Find technology column
        tech_col = None
        for col in df.columns:
            if 'Technology' in col:
                tech_col = col
                break
        
        if tech_col:
            print(f"\nTechnologies found in commercial installations:")
            tech_counts = commercial_df[tech_col].value_counts()
            print(tech_counts)
            
            # Find capacity column
            capacity_col = None
            for col in df.columns:
                if 'Capacity' in col or 'capacity' in col or 'kW' in col:
                    capacity_col = col
                    break
            
            if capacity_col:
                # Process by technology
                results = {}
                
                for tech in commercial_df[tech_col].unique():
                    if pd.notna(tech):
                        tech_df = commercial_df[commercial_df[tech_col] == tech]
                        
                        # Convert capacity to numeric
                        tech_df[capacity_col] = pd.to_numeric(tech_df[capacity_col], errors='coerce')
                        
                        total_capacity = tech_df[capacity_col].sum()
                        avg_capacity = tech_df[capacity_col].mean()
                        
                        results[tech] = {
                            'count': len(tech_df),
                            'total_capacity_kw': total_capacity,
                            'total_capacity_mw': total_capacity / 1000,
                            'average_capacity_kw': avg_capacity,
                            'min_capacity_kw': tech_df[capacity_col].min(),
                            'max_capacity_kw': tech_df[capacity_col].max()
                        }
                
                # Display results
                print("\n" + "="*60)
                print("COMMERCIAL FIT INSTALLATIONS BY TECHNOLOGY:")
                print("="*60)
                
                # Sort by total capacity
                sorted_results = sorted(results.items(), 
                                      key=lambda x: x[1]['total_capacity_mw'], 
                                      reverse=True)
                
                for tech, stats in sorted_results:
                    print(f"\n{tech}:")
                    print(f"  Sites: {stats['count']:,}")
                    print(f"  Total Capacity: {stats['total_capacity_mw']:.1f} MW")
                    print(f"  Average Size: {stats['average_capacity_kw']:.1f} kW")
                    print(f"  Range: {stats['min_capacity_kw']:.1f} - {stats['max_capacity_kw']:.1f} kW")
                
                # Save processed data
                save_commercial_data(commercial_df, df.columns)
                
                return commercial_df
            else:
                print("Error: Could not find capacity column")
        else:
            print("Error: Could not find technology column")
    else:
        print("Error: Could not find installation type column")
    
    return None

def save_commercial_data(df, all_columns):
    """Save processed commercial data to JSON"""
    
    print("\n" + "="*60)
    print("SAVING COMMERCIAL FIT DATA...")
    print("="*60)
    
    # Identify columns
    columns_map = {}
    for col in all_columns:
        col_lower = col.lower()
        if 'technology' in col_lower:
            columns_map['technology'] = col
        elif 'installation' in col_lower and 'type' in col_lower:
            columns_map['installation_type'] = col
        elif 'capacity' in col_lower:
            columns_map['capacity'] = col
        elif 'tariff' in col_lower and 'kwh' in col_lower:
            columns_map['tariff'] = col
        elif 'commission' in col_lower and 'date' in col_lower:
            columns_map['commission_date'] = col
        elif 'postcode' in col_lower:
            columns_map['postcode'] = col
        elif 'local' in col_lower and 'authority' in col_lower:
            columns_map['local_authority'] = col
        elif 'region' in col_lower:
            columns_map['region'] = col
        elif 'country' in col_lower:
            columns_map['country'] = col
    
    print(f"Column mapping: {columns_map}")
    
    # Process sites
    sites = []
    
    for _, row in df.iterrows():
        try:
            # Get base data
            site = {}
            
            # Technology
            if 'technology' in columns_map:
                site['technology'] = str(row[columns_map['technology']])
            
            # Installation type
            if 'installation_type' in columns_map:
                site['installation_type'] = str(row[columns_map['installation_type']])
            
            # Capacity
            if 'capacity' in columns_map:
                capacity = pd.to_numeric(row[columns_map['capacity']], errors='coerce')
                if pd.notna(capacity):
                    site['capacity_kw'] = float(capacity)
                    site['capacity_mw'] = float(capacity) / 1000
            
            # Tariff
            if 'tariff' in columns_map:
                tariff = pd.to_numeric(row[columns_map['tariff']], errors='coerce')
                if pd.notna(tariff):
                    site['tariff_p_kwh'] = float(tariff)
            
            # Commission date and age
            if 'commission_date' in columns_map:
                try:
                    commission_date = pd.to_datetime(row[columns_map['commission_date']])
                    site['commission_date'] = commission_date.isoformat()
                    age_years = (datetime.now() - commission_date).days / 365.25
                    site['age_years'] = age_years
                    
                    # Calculate remaining FIT based on technology
                    tech = site.get('technology', '')
                    if 'Photovoltaic' in tech or 'Solar' in tech:
                        fit_period = 20
                    elif 'Wind' in tech:
                        fit_period = 20
                    elif 'Hydro' in tech:
                        fit_period = 20
                    elif 'Anaerobic' in tech:
                        fit_period = 20
                    elif 'CHP' in tech:
                        fit_period = 10
                    else:
                        fit_period = 20
                    
                    site['remaining_fit_years'] = fit_period - age_years
                    
                    # Repowering window
                    if site['remaining_fit_years'] < 2:
                        site['repowering_window'] = 'IMMEDIATE'
                    elif site['remaining_fit_years'] < 5:
                        site['repowering_window'] = 'URGENT'
                    elif site['remaining_fit_years'] < 10:
                        site['repowering_window'] = 'OPTIMAL'
                    elif site['remaining_fit_years'] < 15:
                        site['repowering_window'] = 'PLANNING'
                    else:
                        site['repowering_window'] = 'FUTURE'
                except:
                    pass
            
            # Location data
            if 'postcode' in columns_map:
                site['postcode'] = str(row[columns_map['postcode']])
            if 'local_authority' in columns_map:
                site['local_authority'] = str(row[columns_map['local_authority']])
            if 'region' in columns_map:
                site['region'] = str(row[columns_map['region']])
            if 'country' in columns_map:
                site['country'] = str(row[columns_map['country']])
            
            # Estimate annual generation
            if 'capacity_mw' in site and 'technology' in site:
                capacity_factors = {
                    'Photovoltaic': 0.11,
                    'Wind': 0.27,
                    'Hydro': 0.38,
                    'Anaerobic': 0.80,
                    'Micro': 0.50,
                    'CHP': 0.50
                }
                
                cf = 0.20  # Default
                for key, value in capacity_factors.items():
                    if key in site['technology']:
                        cf = value
                        break
                
                site['annual_generation_mwh'] = site['capacity_mw'] * 8760 * cf
                
                if 'tariff_p_kwh' in site:
                    site['annual_fit_revenue_gbp'] = (
                        site['annual_generation_mwh'] * 1000 * site['tariff_p_kwh'] / 100
                    )
            
            sites.append(site)
            
        except Exception as e:
            continue
    
    # Create summary
    summary = {
        'generated': datetime.now().isoformat(),
        'total_sites': len(sites),
        'total_capacity_mw': sum(s.get('capacity_mw', 0) for s in sites),
        'by_technology': {}
    }
    
    # Group by technology
    tech_groups = {}
    for site in sites:
        tech = site.get('technology', 'Unknown')
        if tech not in tech_groups:
            tech_groups[tech] = []
        tech_groups[tech].append(site)
    
    for tech, tech_sites in tech_groups.items():
        summary['by_technology'][tech] = {
            'count': len(tech_sites),
            'capacity_mw': sum(s.get('capacity_mw', 0) for s in tech_sites)
        }
    
    # Save to file
    output = {
        'summary': summary,
        'sites': sites
    }
    
    with open('data/all_commercial_fit.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nSaved {len(sites):,} commercial sites to data/all_commercial_fit.json")
    
    # Print summary
    print("\nSummary by Technology:")
    for tech, stats in sorted(summary['by_technology'].items(), 
                             key=lambda x: x[1]['capacity_mw'], 
                             reverse=True):
        print(f"  {tech}: {stats['count']:,} sites, {stats['capacity_mw']:.1f} MW")

if __name__ == "__main__":
    process_commercial_fit()