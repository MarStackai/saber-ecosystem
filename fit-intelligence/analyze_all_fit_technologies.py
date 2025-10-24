#!/usr/bin/env python3
"""
Analyze ALL technologies in FIT data, not just wind
"""

import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_fit_files():
    """Analyze all FIT files for technology breakdown"""
    
    fit_files = [
        'data/Feed-in Tariff Installation Report Part 1.xlsx',
        'data/Feed-in Tariff Installation Report Part 2.xlsx',
        'data/Feed-in Tariff Installation Report Part 3.xlsx'
    ]
    
    all_data = []
    
    for file_path in fit_files:
        logger.info(f"\nAnalyzing {file_path}...")
        
        try:
            # Read Excel file - sheet names are 'Part 1', 'Part 2', 'Part 3'
            part_num = file_path.split('Part ')[-1].replace('.xlsx', '')
            sheet_name = f'Part {part_num}'
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            logger.info(f"  Loaded {len(df)} rows")
            
            # Check column names
            if all_data == []:
                logger.info(f"  Columns: {list(df.columns)[:10]}...")  # Show first 10 columns
            
            # Look for technology column - try various possible names
            tech_col = None
            for col in ['Technology', 'technology', 'Installation Type', 'installation_type', 
                       'Tariff Code', 'tariff_code', 'Technology Type', 'Type']:
                if col in df.columns:
                    tech_col = col
                    break
            
            if tech_col:
                logger.info(f"  Found technology column: '{tech_col}'")
                tech_counts = df[tech_col].value_counts()
                logger.info(f"  Technology breakdown:")
                for tech, count in tech_counts.head(10).items():
                    logger.info(f"    - {tech}: {count:,} installations")
            else:
                # Try to identify from tariff code or other columns
                logger.info("  No direct technology column found, checking tariff codes...")
                if 'Tariff Code' in df.columns:
                    tariff_counts = df['Tariff Code'].value_counts()
                    logger.info(f"  Tariff code breakdown:")
                    for tariff, count in tariff_counts.head(10).items():
                        logger.info(f"    - {tariff}: {count:,} installations")
            
            all_data.append(df)
            
        except Exception as e:
            logger.error(f"  Error reading file: {e}")
    
    if all_data:
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        logger.info(f"\n{'='*60}")
        logger.info(f"TOTAL INSTALLATIONS: {len(combined_df):,}")
        logger.info(f"{'='*60}")
        
        # Try to identify solar vs wind
        combined_df['tech_type'] = 'Unknown'
        
        # Check various columns for technology identifiers
        for col in combined_df.columns:
            if 'technology' in col.lower() or 'type' in col.lower() or 'tariff' in col.lower():
                logger.info(f"\nAnalyzing column '{col}':")
                value_counts = combined_df[col].value_counts()
                
                # Identify solar installations
                solar_keywords = ['solar', 'photovoltaic', 'pv', 'Solar', 'Photovoltaic', 'PV']
                wind_keywords = ['wind', 'Wind', 'turbine', 'Turbine']
                
                for value, count in value_counts.head(20).items():
                    if pd.notna(value):
                        value_str = str(value).lower()
                        if any(keyword.lower() in value_str for keyword in solar_keywords):
                            logger.info(f"  SOLAR: {value} = {count:,} installations")
                            combined_df.loc[combined_df[col] == value, 'tech_type'] = 'Solar'
                        elif any(keyword.lower() in value_str for keyword in wind_keywords):
                            logger.info(f"  WIND: {value} = {count:,} installations")
                            combined_df.loc[combined_df[col] == value, 'tech_type'] = 'Wind'
        
        # Summary
        tech_summary = combined_df['tech_type'].value_counts()
        logger.info(f"\n{'='*60}")
        logger.info("TECHNOLOGY SUMMARY:")
        logger.info(f"{'='*60}")
        for tech, count in tech_summary.items():
            percentage = (count / len(combined_df)) * 100
            logger.info(f"{tech}: {count:,} installations ({percentage:.1f}%)")
        
        # Check capacity distribution
        if 'Installed Capacity' in combined_df.columns or 'capacity' in combined_df.columns.str.lower():
            cap_col = None
            for col in combined_df.columns:
                if 'capacity' in col.lower():
                    cap_col = col
                    break
            
            if cap_col:
                logger.info(f"\nCAPACITY ANALYSIS (column: {cap_col}):")
                combined_df[cap_col] = pd.to_numeric(combined_df[cap_col], errors='coerce')
                
                # Separate by technology if identified
                if 'tech_type' in combined_df.columns:
                    for tech in ['Solar', 'Wind']:
                        tech_df = combined_df[combined_df['tech_type'] == tech]
                        if len(tech_df) > 0:
                            total_capacity = tech_df[cap_col].sum() / 1000  # Convert to MW if in kW
                            avg_capacity = tech_df[cap_col].mean()
                            logger.info(f"  {tech}: Total {total_capacity:.1f} MW, Avg {avg_capacity:.1f} kW")

if __name__ == "__main__":
    analyze_fit_files()