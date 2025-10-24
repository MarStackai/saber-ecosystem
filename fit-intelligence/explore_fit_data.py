#!/usr/bin/env python3
"""
Explore the new FIT License data and existing tariff structure
"""

import pandas as pd
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def explore_fit_tariff_data():
    """Examine the existing FIT tariff table"""
    try:
        # Read the FIT tariff table
        logger.info("Reading FIT tariff table...")
        fit_df = pd.read_excel('data/feed-in_tariff_table_1_april_2010_-_31_march_2020_0.xlsx')
        
        logger.info(f"FIT Tariff table shape: {fit_df.shape}")
        logger.info("Columns:")
        for col in fit_df.columns:
            logger.info(f"  - {col}")
        
        # Show sample data
        logger.info("\nFirst 5 rows:")
        print(fit_df.head())
        
        # Show data types
        logger.info("\nData types:")
        print(fit_df.dtypes)
        
        return fit_df
        
    except Exception as e:
        logger.error(f"Error reading FIT tariff data: {e}")
        return None

def explore_fit_installation_reports():
    """Examine the FIT Installation Reports (Parts 1-3)"""
    try:
        parts_data = {}
        
        for part_num in [1, 2, 3]:
            filename = f'data/Feed-in Tariff Installation Report Part {part_num}.xlsx'
            logger.info(f"Reading {filename}...")
            
            try:
                # Try to read with different sheet names/indices
                xl_file = pd.ExcelFile(filename)
                logger.info(f"  Sheet names: {xl_file.sheet_names}")
                
                # Read the first sheet
                part_df = pd.read_excel(filename, sheet_name=0)
                logger.info(f"  Shape: {part_df.shape}")
                logger.info("  Columns:")
                for col in part_df.columns:
                    logger.info(f"    - {col}")
                
                parts_data[f'part_{part_num}'] = part_df
                
                # Show sample data for first part
                if part_num == 1:
                    logger.info("\nSample data from Part 1:")
                    print(part_df.head())
                    
            except Exception as e:
                logger.error(f"Error reading Part {part_num}: {e}")
                continue
        
        return parts_data
        
    except Exception as e:
        logger.error(f"Error exploring installation reports: {e}")
        return {}

def analyze_existing_commercial_data():
    """Analyze the existing commercial FIT data structure"""
    try:
        logger.info("Analyzing existing commercial FIT data...")
        
        with open('data/all_commercial_fit.json', 'r') as f:
            data = json.load(f)
        
        # Show structure
        logger.info(f"Data keys: {list(data.keys())}")
        
        if 'sites' in data:
            sites = data['sites']
            logger.info(f"Number of sites: {len(sites)}")
            
            if sites:
                sample_site = sites[0]
                logger.info("Sample site structure:")
                for key, value in sample_site.items():
                    logger.info(f"  {key}: {value} ({type(value).__name__})")
        
        return data
        
    except Exception as e:
        logger.error(f"Error analyzing commercial data: {e}")
        return None

def main():
    """Main exploration function"""
    print("=" * 60)
    print("EXPLORING FIT DATA SOURCES")
    print("=" * 60)
    
    # 1. Explore existing FIT tariff table
    print("\n1. FIT TARIFF TABLE")
    print("-" * 40)
    fit_tariff_df = explore_fit_tariff_data()
    
    # 2. Explore FIT Installation Reports
    print("\n2. FIT INSTALLATION REPORTS")
    print("-" * 40)
    installation_data = explore_fit_installation_reports()
    
    # 3. Analyze existing commercial data
    print("\n3. EXISTING COMMERCIAL DATA")
    print("-" * 40)
    commercial_data = analyze_existing_commercial_data()
    
    print("\n" + "=" * 60)
    print("EXPLORATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()