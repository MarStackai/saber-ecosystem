#!/usr/bin/env python3
"""
FIT Rate Mapper - Maps tariff codes and dates to actual FIT rates
Enables queries like "What was the FIT rate in November 2013 for a 350kW turbine?"
"""

import json
import pandas as pd
from datetime import datetime
import re

class FITRateMapper:
    def __init__(self):
        self.load_databases()
    
    def load_databases(self):
        """Load tariff codes and rates databases"""
        with open('data/fit_tariff_codes_database.json', 'r') as f:
            self.tariff_codes = json.load(f)
        
        # Use complete rates file if available
        try:
            with open('data/fit_rates_complete.json', 'r') as f:
                self.fit_rates = json.load(f)
        except FileNotFoundError:
            with open('data/fit_rates_database.json', 'r') as f:
                self.fit_rates = json.load(f)
    
    def parse_date_to_fit_period(self, date_str):
        """Convert date to FIT period (e.g., '2013-11-15' -> '2013/14')"""
        if pd.isna(date_str):
            return None
        
        try:
            date = pd.to_datetime(date_str)
            year = date.year
            month = date.month
            
            # FIT periods run April to March
            if month >= 4:  # April onwards = start of FIT year
                return f"{year}/{str(year+1)[2:]}"
            else:  # Jan-Mar = end of previous FIT year
                return f"{year-1}/{str(year)[2:]}"
        except:
            return None
    
    def parse_capacity_band(self, capacity_kw, technology):
        """Determine capacity band from actual capacity"""
        if pd.isna(capacity_kw):
            return None
        
        # Wind capacity bands
        if technology == 'Wind':
            if capacity_kw <= 1.5:
                return '<=1.5'
            elif capacity_kw <= 15:
                return '1.5-15'
            elif capacity_kw <= 100:
                return '15-100'
            elif capacity_kw <= 500:
                return '100-500'
            else:
                return '>500'
        
        # Solar/PV capacity bands
        elif technology == 'Photovoltaic':
            if capacity_kw <= 4:
                return '<=4'
            elif capacity_kw <= 10:
                return '4-10'
            elif capacity_kw <= 50:
                return '10-50'
            elif capacity_kw <= 100:
                return '50-100'
            elif capacity_kw <= 250:
                return '100-250'
            else:
                return '250-5000'
        
        # Hydro capacity bands
        elif technology == 'Hydro':
            if capacity_kw <= 15:
                return '<=15'
            elif capacity_kw <= 100:
                return '15-100'
            elif capacity_kw <= 2000:
                return '100-2000'
            else:
                return '>2000'
        
        # Anaerobic Digestion capacity bands
        elif technology == 'Anaerobic digestion':
            if capacity_kw <= 250:
                return '<=250'
            elif capacity_kw <= 500:
                return '250-500'
            else:
                return '>500'
        
        return None
    
    def get_fit_rate(self, technology, capacity_kw, date_str):
        """Get FIT rate for given technology, capacity, and date"""
        
        # Parse inputs
        fit_period = self.parse_date_to_fit_period(date_str)
        capacity_band = self.parse_capacity_band(capacity_kw, technology)
        
        if not fit_period or not capacity_band:
            return None
        
        # Look up rate
        try:
            tech_rates = self.fit_rates.get(technology, {})
            period_rates = tech_rates.get(fit_period, {})
            rate = period_rates.get(capacity_band)
            
            return {
                'rate_p_kwh': rate,
                'fit_period': fit_period,
                'capacity_band': capacity_band,
                'technology': technology
            }
        except:
            return None
    
    def query_fit_rate(self, query_text):
        """Parse natural language query and return FIT rate"""
        
        # Check if this is a FIT ID query
        fit_id_match = re.search(r'fit\s+id\s+(\d+)', query_text.lower())
        if fit_id_match:
            fit_id = int(fit_id_match.group(1))
            return self.lookup_fit_id_rate(fit_id)
        
        # Extract date
        date_match = re.search(r'(\w+\s+\d{4})', query_text.lower())
        if date_match:
            date_str = date_match.group(1)
            # Convert month name to date
            month_year = date_str.split()
            month_names = {
                'january': '01', 'february': '02', 'march': '03', 'april': '04',
                'may': '05', 'june': '06', 'july': '07', 'august': '08',
                'september': '09', 'october': '10', 'november': '11', 'december': '12'
            }
            month_num = month_names.get(month_year[0], '01')
            parsed_date = f"{month_year[1]}-{month_num}-15"
        else:
            return "Could not parse date from query"
        
        # Extract capacity
        capacity_match = re.search(r'(\d+)\s*kw', query_text.lower())
        if capacity_match:
            capacity = float(capacity_match.group(1))
        else:
            return "Could not parse capacity from query"
        
        # Extract technology
        if 'turbine' in query_text.lower() or 'wind' in query_text.lower():
            technology = 'Wind'
        elif 'solar' in query_text.lower() or 'pv' in query_text.lower():
            technology = 'Photovoltaic'
        elif 'hydro' in query_text.lower():
            technology = 'Hydro'
        else:
            return "Could not identify technology from query"
        
        # Get rate
        result = self.get_fit_rate(technology, capacity, parsed_date)
        
        if result and result['rate_p_kwh']:
            return f"""
FIT Rate Query Result:
- Technology: {result['technology']}
- Capacity: {capacity}kW ({result['capacity_band']} band)
- Date: {date_str.title()} ({result['fit_period']} FIT period)
- Rate: {result['rate_p_kwh']}p/kWh

Annual Revenue Estimate (35% capacity factor):
£{(capacity * 8760 * 0.35 * result['rate_p_kwh'] / 100):,.0f} per year
            """.strip()
        else:
            return f"No FIT rate found for {technology} {capacity}kW in {date_str}"
    
    def lookup_fit_id_rate(self, fit_id):
        """Look up FIT rate by FIT ID from site data"""
        try:
            import pandas as pd
            
            # Convert fit_id to integer for matching
            try:
                fit_id_int = int(fit_id)
            except (ValueError, TypeError):
                return f"Invalid FIT ID format: {fit_id}"
            
            # Search for FIT ID in clean CSV files
            for i in [1, 2, 3]:
                file_path = f'data/fit_part_{i}_clean.csv'
                try:
                    df = pd.read_csv(file_path)
                    match = df[df['FIT ID'] == fit_id_int]
                    
                    if not match.empty:
                        row = match.iloc[0]
                        
                        # Extract site information
                        technology = row['Technology']
                        capacity_kw = row['Installed capacity']
                        commission_date = row['Commissioning date']
                        install_type = row['Installation Type']
                        postcode = row['PostCode ']
                        tariff_code = row['TariffCode']
                        tariff_desc = row['Tariff Description']
                        
                        # Get FIT rate
                        result = self.get_fit_rate(technology, capacity_kw, commission_date)
                        
                        if result and result.get('rate_p_kwh'):
                            return f"""
FIT ID {fit_id_int} Rate Information:
- Technology: {technology}
- Capacity: {capacity_kw}kW
- Installation Type: {install_type}
- Location: {postcode}
- Commission Date: {commission_date[:10]}
- Tariff Code: {tariff_code}
- Tariff Description: {tariff_desc}

FIT Rate Details:
- Rate: {result['rate_p_kwh']}p/kWh
- FIT Period: {result['fit_period']}
- Capacity Band: {result['capacity_band']}

Annual Revenue Estimate (35% capacity factor):
£{(capacity_kw * 8760 * 0.35 * result['rate_p_kwh'] / 100):,.0f} per year
                            """.strip()
                        else:
                            return f"""
FIT ID {fit_id_int} Found:
- Technology: {technology}
- Capacity: {capacity_kw}kW
- Installation Type: {install_type}
- Location: {postcode}
- Commission Date: {commission_date[:10]}
- Tariff Code: {tariff_code}

Note: Could not determine historical FIT rate for this installation.
                            """.strip()
                
                except Exception as e:
                    continue
            
            return f"FIT ID {fit_id} not found in the database"
            
        except Exception as e:
            return f"Error looking up FIT ID {fit_id}: {str(e)}"

# Test the example query
if __name__ == "__main__":
    mapper = FITRateMapper()
    
    # Test the example query
    query = "What was the FIT rate in November 2013 for a 350kW turbine?"
    result = mapper.query_fit_rate(query)
    print("=== TESTING FIT RATE QUERY ===")
    print(f"Query: {query}")
    print(f"\nResult:\n{result}")
    
    # Test a few more examples
    test_queries = [
        "What was the FIT rate in April 2012 for a 500kW turbine?",
        "FIT rate for 25kW solar in March 2011?",
        "What rate would a 150kW hydro get in 2012?"
    ]
    
    print("\n" + "="*60)
    print("ADDITIONAL TESTS")
    print("="*60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = mapper.query_fit_rate(query)
        print(f"Result: {result.split('Annual Revenue')[0].strip()}")