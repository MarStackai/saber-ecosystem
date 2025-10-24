#!/usr/bin/env python3
"""
Add FIT rate data to existing ChromaDB records
Maps tariff codes to actual p/kWh rates based on technology, capacity, and commission date
"""

import json
import chromadb
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FITRateIntegrator:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_collection("fit_licenses_nondomestic")
        
        # Load FIT rates database
        with open('data/fit_rates_database.json', 'r') as f:
            self.fit_rates = json.load(f)
        
        # Load tariff codes database
        with open('data/fit_tariff_codes_database.json', 'r') as f:
            self.tariff_codes = json.load(f)
            
        logger.info(f"Loaded {len(self.fit_rates)} technology rate tables")
        logger.info(f"Loaded {len(self.tariff_codes)} tariff codes")
    
    def get_fit_period(self, commission_date):
        """Determine FIT period from commission date"""
        if not commission_date:
            return None
            
        try:
            if isinstance(commission_date, str):
                date = datetime.strptime(commission_date.split()[0], '%Y-%m-%d')
            else:
                date = commission_date
                
            year = date.year
            month = date.month
            
            # UK FIT periods run April to March
            if month >= 4:
                return f"{year}/{str(year+1)[2:]}"
            else:
                return f"{year-1}/{str(year)[2:]}"
        except:
            return None
    
    def get_capacity_band(self, technology, capacity_kw):
        """Determine capacity band for given technology and capacity"""
        if technology not in self.fit_rates:
            return None
            
        # Get any year's bands (they're mostly consistent)
        sample_year = list(self.fit_rates[technology].keys())[0]
        bands = self.fit_rates[technology][sample_year]
        
        # Parse band ranges and find matching one
        for band_str in bands.keys():
            if '-' in band_str:
                # Range like "100-500"
                parts = band_str.split('-')
                min_cap = float(parts[0])
                max_cap = float(parts[1])
                if min_cap <= capacity_kw <= max_cap:
                    return band_str
            elif band_str.startswith('<='):
                # Upper limit like "<=4"
                max_cap = float(band_str.replace('<=', ''))
                if capacity_kw <= max_cap:
                    return band_str
            elif band_str.startswith('>'):
                # Lower limit like ">500"
                min_cap = float(band_str.replace('>', ''))
                if capacity_kw > min_cap:
                    return band_str
                    
        return None
    
    def get_fit_rate(self, technology, capacity_kw, commission_date):
        """Get FIT rate for given parameters"""
        fit_period = self.get_fit_period(commission_date)
        if not fit_period or technology not in self.fit_rates:
            return None
            
        # Handle technology name variations
        tech_map = {
            'Wind': 'Wind',
            'Photovoltaic': 'Photovoltaic',
            'Solar Photovoltaic': 'Photovoltaic',
            'Hydro': 'Hydro',
            'Anaerobic digestion': 'Anaerobic Digestion',
            'Micro CHP': 'Micro CHP',
            'CHP': 'Micro CHP'
        }
        
        mapped_tech = tech_map.get(technology, technology)
        
        if mapped_tech not in self.fit_rates:
            return None
            
        # Get rates for the period
        if fit_period not in self.fit_rates[mapped_tech]:
            # Try to find closest period
            available_periods = sorted(self.fit_rates[mapped_tech].keys())
            # Use the last available period if commission is after all periods
            if fit_period > available_periods[-1]:
                fit_period = available_periods[-1]
            else:
                # Find closest earlier period
                for period in reversed(available_periods):
                    if period <= fit_period:
                        fit_period = period
                        break
        
        if fit_period not in self.fit_rates[mapped_tech]:
            return None
            
        # Get capacity band
        capacity_band = self.get_capacity_band(mapped_tech, capacity_kw)
        if not capacity_band:
            return None
            
        # Get the rate
        rate = self.fit_rates[mapped_tech][fit_period].get(capacity_band)
        
        return {
            'fit_rate_p_kwh': rate,
            'fit_period': fit_period,
            'capacity_band': capacity_band
        }
    
    def update_collection(self):
        """Update all records in collection with FIT rates"""
        logger.info("Fetching all records from ChromaDB...")
        
        # Get all records
        all_records = self.collection.get(limit=50000)
        
        total = len(all_records['ids'])
        logger.info(f"Processing {total:,} records...")
        
        updated_count = 0
        batch_size = 100
        
        for i in range(0, total, batch_size):
            batch_ids = all_records['ids'][i:i+batch_size]
            batch_metadatas = all_records['metadatas'][i:i+batch_size]
            
            updated_metadatas = []
            
            for metadata in batch_metadatas:
                if metadata:
                    # Get parameters
                    technology = metadata.get('technology', '')
                    capacity_kw = metadata.get('capacity_kw', 0)
                    commission_date = metadata.get('commissioned_date', '')
                    
                    # Get FIT rate
                    rate_info = self.get_fit_rate(technology, capacity_kw, commission_date)
                    
                    if rate_info and rate_info.get('fit_rate_p_kwh') is not None:
                        # Add rate information to metadata
                        metadata['fit_rate_p_kwh'] = rate_info['fit_rate_p_kwh']
                        metadata['fit_period'] = rate_info['fit_period']
                        metadata['fit_capacity_band'] = rate_info['capacity_band']
                        
                        # Calculate estimated annual revenue (assuming 25% capacity factor for wind, 10% for solar)
                        if technology == 'Wind':
                            capacity_factor = 0.25
                        elif 'Photovoltaic' in technology:
                            capacity_factor = 0.10
                        else:
                            capacity_factor = 0.15
                        
                        if capacity_kw > 0:
                            annual_generation_kwh = capacity_kw * 8760 * capacity_factor
                            annual_fit_revenue = annual_generation_kwh * rate_info['fit_rate_p_kwh'] / 100
                            
                            metadata['estimated_annual_generation_kwh'] = round(annual_generation_kwh)
                            metadata['estimated_annual_fit_revenue_gbp'] = round(annual_fit_revenue)
                        
                        updated_count += 1
                
                updated_metadatas.append(metadata)
            
            # Update batch in ChromaDB
            self.collection.update(
                ids=batch_ids,
                metadatas=updated_metadatas
            )
            
            if (i + batch_size) % 1000 == 0:
                logger.info(f"Processed {min(i + batch_size, total):,}/{total:,} records. Updated {updated_count:,} with FIT rates.")
        
        logger.info(f"Completed! Updated {updated_count:,} records with FIT rate data.")
        
        # Verify the update
        self.verify_update()
    
    def verify_update(self):
        """Verify that FIT rates were added successfully"""
        logger.info("\nVerifying FIT rate integration...")
        
        # Check a sample of records
        sample = self.collection.get(limit=10)
        
        rates_found = 0
        for metadata in sample['metadatas']:
            if metadata and 'fit_rate_p_kwh' in metadata:
                rates_found += 1
                
                # Show an example
                if rates_found == 1:
                    logger.info("\nExample record with FIT rate:")
                    logger.info(f"  FIT ID: {metadata.get('fit_id')}")
                    logger.info(f"  Technology: {metadata.get('technology')}")
                    logger.info(f"  Capacity: {metadata.get('capacity_kw', 0)/1000:.2f} MW")
                    logger.info(f"  Commission Date: {metadata.get('commissioned_date')}")
                    logger.info(f"  FIT Period: {metadata.get('fit_period')}")
                    logger.info(f"  Capacity Band: {metadata.get('fit_capacity_band')}")
                    logger.info(f"  FIT Rate: {metadata.get('fit_rate_p_kwh')} p/kWh")
                    logger.info(f"  Est. Annual Generation: {metadata.get('estimated_annual_generation_kwh', 0):,} kWh")
                    logger.info(f"  Est. Annual FIT Revenue: £{metadata.get('estimated_annual_fit_revenue_gbp', 0):,}")
        
        logger.info(f"\nFound FIT rates in {rates_found}/10 sample records")
        
        # Test specific query
        test_fit_id = "1585"  # The one we tested earlier
        test_record = self.collection.get(ids=[f"fit_{test_fit_id}"])
        
        if test_record['metadatas'] and test_record['metadatas'][0]:
            metadata = test_record['metadatas'][0]
            logger.info(f"\nFIT ID {test_fit_id} rate data:")
            logger.info(f"  Technology: {metadata.get('technology')}")
            logger.info(f"  Capacity: {metadata.get('capacity_kw', 0)/1000:.2f} MW")
            logger.info(f"  FIT Rate: {metadata.get('fit_rate_p_kwh')} p/kWh")
            logger.info(f"  Est. Annual Revenue: £{metadata.get('estimated_annual_fit_revenue_gbp', 0):,}")


def main():
    integrator = FITRateIntegrator()
    integrator.update_collection()


if __name__ == "__main__":
    main()