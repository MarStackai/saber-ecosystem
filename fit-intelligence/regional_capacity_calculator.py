#!/usr/bin/env python3
"""
Regional Capacity Calculator for FIT Intelligence
Integrates regional capacity factors with existing ChromaDB data
"""

import json
import chromadb
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Regional capacity factors based on UK geographical data
REGIONAL_CAPACITY_FACTORS = {
    'Photovoltaic': {
        'south_england': {'cf': 0.120, 'range': (0.115, 0.125), 'annual_kwh_per_kwp': 1050},
        'south_east': {'cf': 0.115, 'range': (0.110, 0.120), 'annual_kwh_per_kwp': 1005},
        'east_anglia': {'cf': 0.110, 'range': (0.105, 0.115), 'annual_kwh_per_kwp': 960},
        'midlands': {'cf': 0.105, 'range': (0.100, 0.110), 'annual_kwh_per_kwp': 920},
        'wales': {'cf': 0.105, 'range': (0.100, 0.110), 'annual_kwh_per_kwp': 920},
        'northern_england': {'cf': 0.100, 'range': (0.095, 0.105), 'annual_kwh_per_kwp': 875},
        'yorkshire': {'cf': 0.100, 'range': (0.095, 0.105), 'annual_kwh_per_kwp': 875},
        'scotland_central': {'cf': 0.095, 'range': (0.090, 0.100), 'annual_kwh_per_kwp': 830},
        'scotland_highlands': {'cf': 0.090, 'range': (0.085, 0.095), 'annual_kwh_per_kwp': 790}
    },
    'Wind': {
        'scotland_highlands': {'cf': 0.35, 'range': (0.32, 0.40), 'typical_speed_ms': 8.5},
        'scotland_central': {'cf': 0.30, 'range': (0.28, 0.32), 'typical_speed_ms': 7.0},
        'northern_england': {'cf': 0.28, 'range': (0.27, 0.30), 'typical_speed_ms': 6.5},
        'yorkshire': {'cf': 0.27, 'range': (0.25, 0.29), 'typical_speed_ms': 6.3},
        'wales': {'cf': 0.27, 'range': (0.25, 0.30), 'typical_speed_ms': 6.5},
        'midlands': {'cf': 0.20, 'range': (0.18, 0.22), 'typical_speed_ms': 5.2},
        'south_west': {'cf': 0.26, 'range': (0.24, 0.28), 'typical_speed_ms': 6.2},
        'south_east': {'cf': 0.19, 'range': (0.17, 0.21), 'typical_speed_ms': 5.0},
        'east_anglia': {'cf': 0.25, 'range': (0.23, 0.27), 'typical_speed_ms': 6.0}
    },
    'Hydro': {
        'scotland_highlands': {'cf': 0.50, 'range': (0.45, 0.55)},
        'wales': {'cf': 0.45, 'range': (0.40, 0.50)},
        'lake_district': {'cf': 0.40, 'range': (0.35, 0.45)},
        'yorkshire': {'cf': 0.35, 'range': (0.30, 0.40)},
        'pennines': {'cf': 0.35, 'range': (0.30, 0.40)},
        'southern_england': {'cf': 0.30, 'range': (0.25, 0.35)}
    },
    'Anaerobic digestion': {
        'all_regions': {'cf': 0.85, 'range': (0.80, 0.90), 'availability': 0.92}
    },
    'Micro CHP': {
        'industrial': {'cf': 0.90, 'range': (0.85, 0.95), 'heat_ratio': 1.5},
        'healthcare': {'cf': 0.85, 'range': (0.80, 0.90), 'heat_ratio': 1.3},
        'commercial': {'cf': 0.65, 'range': (0.60, 0.70), 'heat_ratio': 1.2},
        'all_regions': {'cf': 0.75, 'range': (0.70, 0.80), 'heat_ratio': 1.5}
    }
}

# Enhanced postcode to region mapping for UK
POSTCODE_REGIONS = {
    # Scotland
    'AB': 'scotland_highlands', 'DD': 'scotland_central', 
    'DG': 'scotland_central', 'EH': 'scotland_central',
    'FK': 'scotland_central', 'G': 'scotland_central',
    'IV': 'scotland_highlands', 'KA': 'scotland_central',
    'KW': 'scotland_highlands', 'KY': 'scotland_central',
    'ML': 'scotland_central', 'PA': 'scotland_highlands',
    'PH': 'scotland_highlands', 'TD': 'scotland_central',
    'ZE': 'scotland_highlands',
    
    # Yorkshire & Humber
    'BD': 'yorkshire', 'DN': 'yorkshire', 'HD': 'yorkshire',
    'HG': 'yorkshire', 'HU': 'yorkshire', 'HX': 'yorkshire',
    'LS': 'yorkshire', 'S': 'yorkshire', 'WF': 'yorkshire',
    'YO': 'yorkshire',
    
    # Northern England  
    'BB': 'northern_england', 'BL': 'northern_england',
    'CA': 'northern_england', 'DH': 'northern_england', 
    'DL': 'northern_england', 'FY': 'northern_england',
    'LA': 'northern_england', 'NE': 'northern_england',
    'OL': 'northern_england', 'PR': 'northern_england',
    'SR': 'northern_england', 'TS': 'northern_england',
    
    # Midlands
    'B': 'midlands', 'CV': 'midlands', 'DE': 'midlands',
    'DY': 'midlands', 'LE': 'midlands', 'NG': 'midlands',
    'NN': 'midlands', 'ST': 'midlands', 'TF': 'midlands',
    'WR': 'midlands', 'WS': 'midlands', 'WV': 'midlands',
    
    # Wales
    'CF': 'wales', 'CH': 'wales', 'LD': 'wales',
    'LL': 'wales', 'NP': 'wales', 'SA': 'wales',
    'SY': 'wales',
    
    # East Anglia
    'CB': 'east_anglia', 'CM': 'east_anglia', 
    'CO': 'east_anglia', 'IP': 'east_anglia',
    'NR': 'east_anglia', 'PE': 'east_anglia',
    'SG': 'east_anglia',
    
    # South East (including Berkshire RG, SL)
    'AL': 'south_east', 'BN': 'south_east', 'BR': 'south_east',
    'CR': 'south_east', 'CT': 'south_east', 'DA': 'south_east',
    'E': 'south_east', 'EC': 'south_east', 'EN': 'south_east',
    'GU': 'south_east', 'HA': 'south_east', 'HP': 'south_east',
    'IG': 'south_east', 'KT': 'south_east', 'LU': 'south_east',
    'ME': 'south_east', 'MK': 'south_east', 'N': 'south_east',
    'NW': 'south_east', 'OX': 'south_east', 'RG': 'south_east',
    'RH': 'south_east', 'RM': 'south_east', 'SE': 'south_east',
    'SL': 'south_east', 'SM': 'south_east', 'SS': 'south_east',
    'SW': 'south_east', 'TN': 'south_east', 'TW': 'south_east',
    'UB': 'south_east', 'W': 'south_east', 'WC': 'south_east',
    'WD': 'south_east',
    
    # South/South West
    'BA': 'south_west', 'BH': 'south_england', 'BS': 'south_west',
    'DT': 'south_england', 'EX': 'south_west', 'GL': 'south_west',
    'PL': 'south_west', 'PO': 'south_england', 'SN': 'south_west',
    'SO': 'south_england', 'SP': 'south_england', 'TA': 'south_west',
    'TQ': 'south_west', 'TR': 'south_west'
}

@dataclass
class RegionalCalculationResult:
    """Enhanced calculation result with regional adjustments"""
    fit_id: str
    technology: str
    region: str
    capacity_kw: float
    base_capacity_factor: float  # Current simple assumption
    regional_capacity_factor: float  # Accurate regional CF
    fit_rate_p_kwh: float
    current_annual_generation_kwh: float  # Using current simple CF
    regional_annual_generation_kwh: float  # Using regional CF
    current_annual_revenue: float  # Current calculation
    regional_annual_revenue: float  # More accurate calculation
    improvement_factor: float  # How much more/less accurate
    confidence_range: Tuple[float, float]  # Min/max revenue range
    carbon_saved_tonnes: float

class RegionalCapacityCalculator:
    """
    Enhances existing FIT calculations with accurate regional capacity factors
    Integrates with existing ChromaDB data
    """
    
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_collection("fit_licenses_nondomestic")
        
        # Load FIT rates database
        with open('data/fit_rates_database.json', 'r') as f:
            self.fit_rates = json.load(f)
            
        self.hours_per_year = 8760
        self.carbon_factor = 0.233  # kgCO2/kWh UK grid average
        
        logger.info("Regional Capacity Calculator initialized")
    
    def get_region_from_postcode(self, postcode: str) -> str:
        """Map postcode to region"""
        if not postcode:
            return 'midlands'  # Default
            
        # Extract prefix
        prefix = postcode.upper().strip().replace(' ', '')[:2]
        if prefix[1].isdigit():
            prefix = prefix[0]
            
        return POSTCODE_REGIONS.get(prefix, 'midlands')
    
    def get_regional_capacity_factor(self, technology: str, region: str, 
                                    scenario: str = 'expected') -> Dict:
        """Get accurate regional capacity factor"""
        tech_factors = REGIONAL_CAPACITY_FACTORS.get(technology, {})
        
        # Handle technologies with uniform factors
        if technology == 'Anaerobic digestion':
            return tech_factors.get('all_regions', {'cf': 0.85, 'range': (0.80, 0.90)})
        elif technology == 'Micro CHP':
            return tech_factors.get('all_regions', {'cf': 0.75, 'range': (0.70, 0.80)})
        
        # Get regional factor
        regional_data = tech_factors.get(region, None)
        
        # Fallback to nearest region
        if not regional_data:
            if region == 'yorkshire' and technology == 'Photovoltaic':
                regional_data = tech_factors.get('northern_england')
            else:
                # Use national average
                regional_data = {'cf': 0.20, 'range': (0.15, 0.25)}
        
        return regional_data
    
    def calculate_with_regional_adjustment(self, fit_id: str) -> Optional[RegionalCalculationResult]:
        """
        Calculate more accurate revenue using regional capacity factors
        Compare with current simple assumptions
        """
        try:
            # Get record from ChromaDB
            record = self.collection.get(ids=[f"fit_{fit_id}"])
            
            if not record['metadatas'] or not record['metadatas'][0]:
                return None
                
            metadata = record['metadatas'][0]
            
            # Extract data
            technology = metadata.get('technology')
            capacity_kw = metadata.get('capacity_kw', 0)
            postcode = metadata.get('postcode', '')
            fit_rate = metadata.get('fit_rate_p_kwh')
            
            if not technology or capacity_kw <= 0:
                return None
            
            # Get region
            region = self.get_region_from_postcode(postcode)
            
            # Get current simple capacity factor (what we're using now)
            if technology == 'Wind':
                current_cf = 0.25
            elif 'Photovoltaic' in technology:
                current_cf = 0.10
            else:
                current_cf = 0.15
            
            # Get accurate regional capacity factor
            regional_data = self.get_regional_capacity_factor(technology, region)
            regional_cf = regional_data['cf']
            cf_range = regional_data['range']
            
            # Calculate generation and revenue
            current_generation = capacity_kw * self.hours_per_year * current_cf
            regional_generation = capacity_kw * self.hours_per_year * regional_cf
            
            # Revenue calculations
            if fit_rate:
                current_revenue = current_generation * fit_rate / 100
                regional_revenue = regional_generation * fit_rate / 100
                
                # Confidence range
                min_revenue = capacity_kw * self.hours_per_year * cf_range[0] * fit_rate / 100
                max_revenue = capacity_kw * self.hours_per_year * cf_range[1] * fit_rate / 100
            else:
                current_revenue = 0
                regional_revenue = 0
                min_revenue = 0
                max_revenue = 0
            
            # Calculate improvement factor
            if current_generation > 0:
                improvement = regional_generation / current_generation
            else:
                improvement = 1.0
            
            # Carbon savings
            carbon_saved = regional_generation * self.carbon_factor / 1000
            
            return RegionalCalculationResult(
                fit_id=fit_id,
                technology=technology,
                region=region,
                capacity_kw=capacity_kw,
                base_capacity_factor=current_cf,
                regional_capacity_factor=regional_cf,
                fit_rate_p_kwh=fit_rate or 0,
                current_annual_generation_kwh=round(current_generation),
                regional_annual_generation_kwh=round(regional_generation),
                current_annual_revenue=round(current_revenue, 2),
                regional_annual_revenue=round(regional_revenue, 2),
                improvement_factor=round(improvement, 2),
                confidence_range=(round(min_revenue, 2), round(max_revenue, 2)),
                carbon_saved_tonnes=round(carbon_saved, 1)
            )
            
        except Exception as e:
            logger.error(f"Error calculating for FIT {fit_id}: {e}")
            return None
    
    def update_all_with_regional_factors(self, batch_size: int = 100):
        """
        Update all ChromaDB records with regional capacity factors
        This adds new fields without overwriting existing ones
        """
        logger.info("Updating all records with regional capacity factors...")
        
        # Get all records
        all_records = self.collection.get(limit=50000)
        total = len(all_records['ids'])
        
        updated_count = 0
        
        for i in range(0, total, batch_size):
            batch_ids = all_records['ids'][i:i+batch_size]
            batch_metadatas = all_records['metadatas'][i:i+batch_size]
            
            updated_metadatas = []
            
            for j, metadata in enumerate(batch_metadatas):
                if metadata:
                    # Get region
                    postcode = metadata.get('postcode', '')
                    region = self.get_region_from_postcode(postcode)
                    
                    # Get regional capacity factor
                    technology = metadata.get('technology')
                    if technology:
                        regional_data = self.get_regional_capacity_factor(technology, region)
                        
                        # Add regional data to metadata
                        metadata['region'] = region
                        metadata['regional_capacity_factor'] = regional_data['cf']
                        metadata['cf_range_min'] = regional_data['range'][0]
                        metadata['cf_range_max'] = regional_data['range'][1]
                        
                        # Recalculate with regional factor
                        capacity_kw = metadata.get('capacity_kw', 0)
                        if capacity_kw > 0:
                            regional_generation = capacity_kw * self.hours_per_year * regional_data['cf']
                            metadata['regional_annual_generation_kwh'] = round(regional_generation)
                            
                            # Update revenue if FIT rate exists
                            fit_rate = metadata.get('fit_rate_p_kwh')
                            if fit_rate:
                                regional_revenue = regional_generation * fit_rate / 100
                                metadata['regional_annual_fit_revenue_gbp'] = round(regional_revenue)
                        
                        updated_count += 1
                
                updated_metadatas.append(metadata)
            
            # Update batch
            self.collection.update(
                ids=batch_ids,
                metadatas=updated_metadatas
            )
            
            if (i + batch_size) % 1000 == 0:
                logger.info(f"Processed {min(i + batch_size, total):,}/{total:,} records")
        
        logger.info(f"Updated {updated_count:,} records with regional capacity factors")
    
    def compare_technologies_for_location(self, postcode: str, capacity_kw: float) -> List[Dict]:
        """
        Compare different technologies for a specific location
        Shows which technology performs best in that region
        """
        region = self.get_region_from_postcode(postcode)
        results = []
        
        for technology in ['Photovoltaic', 'Wind', 'Hydro', 'Anaerobic digestion', 'Micro CHP']:
            regional_data = self.get_regional_capacity_factor(technology, region)
            
            # Skip if technology not viable in region
            if regional_data['cf'] == 0.20 and technology in ['Wind', 'Hydro']:
                continue
            
            annual_generation = capacity_kw * self.hours_per_year * regional_data['cf']
            
            # Get appropriate FIT rate (simplified - would need capacity band logic)
            fit_rate = 14.9  # Default rate
            
            annual_revenue = annual_generation * fit_rate / 100
            
            results.append({
                'technology': technology,
                'region': region,
                'capacity_factor': regional_data['cf'],
                'annual_generation_mwh': round(annual_generation / 1000, 1),
                'annual_revenue_gbp': round(annual_revenue, 2),
                'confidence_range': (
                    round(capacity_kw * self.hours_per_year * regional_data['range'][0] * fit_rate / 100, 2),
                    round(capacity_kw * self.hours_per_year * regional_data['range'][1] * fit_rate / 100, 2)
                )
            })
        
        # Sort by revenue
        results.sort(key=lambda x: x['annual_revenue_gbp'], reverse=True)
        
        return results


def main():
    """Test the regional calculator"""
    calculator = RegionalCapacityCalculator()
    
    # Test with FIT ID 1585 (Wind in Yorkshire)
    logger.info("\nTesting FIT ID 1585 (Wind in Ryedale, Yorkshire):")
    result = calculator.calculate_with_regional_adjustment('1585')
    
    if result:
        print(f"\nFIT ID {result.fit_id}:")
        print(f"  Technology: {result.technology}")
        print(f"  Location: {result.region}")
        print(f"  Capacity: {result.capacity_kw} kW")
        print(f"\nCapacity Factors:")
        print(f"  Current (simple): {result.base_capacity_factor * 100:.1f}%")
        print(f"  Regional (accurate): {result.regional_capacity_factor * 100:.1f}%")
        print(f"\nAnnual Generation:")
        print(f"  Current calculation: {result.current_annual_generation_kwh:,} kWh")
        print(f"  Regional calculation: {result.regional_annual_generation_kwh:,} kWh")
        print(f"\nAnnual Revenue:")
        print(f"  Current: £{result.current_annual_revenue:,}")
        print(f"  Regional: £{result.regional_annual_revenue:,}")
        print(f"  Confidence range: £{result.confidence_range[0]:,} - £{result.confidence_range[1]:,}")
        print(f"\nImprovement factor: {result.improvement_factor}x")
        print(f"Carbon saved: {result.carbon_saved_tonnes} tonnes/year")
    
    # Test technology comparison
    print("\n" + "="*60)
    print("Technology comparison for Birmingham (B1):")
    comparison = calculator.compare_technologies_for_location('B1', 335)
    
    for i, tech in enumerate(comparison, 1):
        print(f"\n{i}. {tech['technology']}:")
        print(f"   Capacity Factor: {tech['capacity_factor'] * 100:.1f}%")
        print(f"   Annual Generation: {tech['annual_generation_mwh']} MWh")
        print(f"   Annual Revenue: £{tech['annual_revenue_gbp']:,}")


if __name__ == "__main__":
    main()