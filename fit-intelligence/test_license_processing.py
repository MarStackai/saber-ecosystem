#!/usr/bin/env python3
"""
Quick test of FIT license processing with small dataset
"""

import pandas as pd
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def quick_test():
    """Test processing with small sample"""
    try:
        logger.info("Quick test of license processing...")
        
        # Read just Part 1 with correct headers
        temp_df = pd.read_excel('data/Feed-in Tariff Installation Report Part 1.xlsx', 
                               sheet_name=0, header=None)
        
        # Find header row
        header_row = None
        for idx in range(min(10, len(temp_df))):
            row_text = ' '.join([str(cell) for cell in temp_df.iloc[idx] if pd.notna(cell)])
            if 'FIT ID' in row_text:
                header_row = idx
                break
        
        if header_row is None:
            logger.error("Could not find header row")
            return
            
        # Read with correct header, limit to first 1000 rows for testing
        df = pd.read_excel('data/Feed-in Tariff Installation Report Part 1.xlsx',
                          sheet_name=0, header=header_row, nrows=1000)
        
        logger.info(f"Test dataset: {len(df)} installations")
        logger.info("Columns:")
        for i, col in enumerate(df.columns):
            logger.info(f"  {i}: {col}")
        
        # Show sample data
        logger.info("\nSample data:")
        print(df[['Technology', 'Installed capacity', 'Declared net capacity', 
                 'Commissioning date', 'PostCode ', 'FIT ID']].head())
        
        # Test processing a few records
        processed_count = 0
        sample_licenses = []
        
        for idx, row in df.head(10).iterrows():
            try:
                license_info = {
                    'fit_id': str(row.get('FIT ID', '')),
                    'technology': str(row.get('Technology', '')),
                    'capacity_kw': float(row.get('Declared net capacity', 0) or 0),
                    'commission_date': str(row.get('Commissioning date', '')),
                    'postcode': str(row.get('PostCode ', '')),
                    'tariff_code': str(row.get('TariffCode', ''))
                }
                
                # Skip if missing key data
                if license_info['fit_id'] and license_info['technology']:
                    sample_licenses.append(license_info)
                    processed_count += 1
                    
            except Exception as e:
                logger.debug(f"Error processing row {idx}: {e}")
                continue
        
        logger.info(f"\nProcessed {processed_count} sample licenses:")
        for license in sample_licenses[:3]:
            logger.info(f"  FIT {license['fit_id']}: {license['technology']} "
                       f"{license['capacity_kw']}kW in {license['postcode']}")
        
        # Save sample
        output = {
            'sample_processed': datetime.now().isoformat(),
            'total_available': len(df),
            'processed_count': processed_count,
            'sample_licenses': sample_licenses
        }
        
        with open('data/sample_fit_licenses.json', 'w') as f:
            json.dump(output, f, indent=2, default=str)
            
        logger.info(f"Sample processing complete. Data saved.")
        
    except Exception as e:
        logger.error(f"Error in quick test: {e}")

if __name__ == "__main__":
    quick_test()