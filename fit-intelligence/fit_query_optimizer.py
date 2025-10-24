#!/usr/bin/env python3
"""
Query optimization and response enhancement for FIT Intelligence
Implements metadata prefiltering, financial calculations, and context preservation
"""

from datetime import date
from typing import Dict, List, Optional, Any
import re
import logging
from uk_postcodes import get_location_prefixes, is_valid_uk_postcode

logger = logging.getLogger(__name__)

# Define Yorkshire postcode areas
YORKSHIRE_AREAS = ['YO', 'HU', 'LS', 'BD', 'HX', 'HD', 'WF', 'S', 'DN']

def extract_postcode_area(postcode):
    """Extract postcode area (letters only) from postcode"""
    m = re.match(r'([A-Z]{1,2})', str(postcode or '').upper().strip())
    return m.group(1) if m else None

def prefixes_for_region(region: str) -> Optional[List[str]]:
    """Get postcode prefixes for a region - uses comprehensive UK coverage"""
    if not region:
        return None  # No filter = search all UK
    
    prefixes = get_location_prefixes(region)
    return prefixes if prefixes else None  # Empty list means all UK

def build_where_clause(params: Dict) -> Optional[Dict]:
    """
    Build ChromaDB WHERE clause with exact area matching
    Uses postcode_area field for precise geographic filtering
    """
    where = {}
    
    # Technology filter
    if params.get('technology'):
        where['technology'] = params['technology']
    
    # Location/postcode filter - use exact area matching
    if params.get('postcode_area'):
        # Direct area provided (e.g., 'M' for Manchester)
        where['postcode_area'] = params['postcode_area'].strip().upper()
    elif params.get('location'):
        # Convert location to postcode areas
        location_lower = params['location'].lower()
        
        # Special handling for regions
        if location_lower == 'yorkshire':
            where['postcode_area'] = {'$in': YORKSHIRE_AREAS}
        else:
            # Get postcode prefixes for location
            prefixes = prefixes_for_region(params['location'])
            if prefixes:
                # Extract just the area part (letters only)
                areas = list(set(extract_postcode_area(p) for p in prefixes if p))
                areas = [a for a in areas if a]  # Filter out None values
                
                if len(areas) == 1:
                    # Single area - use equality
                    where['postcode_area'] = areas[0]
                elif areas:
                    # Multiple areas - use $in
                    where['postcode_area'] = {'$in': areas}
    elif params.get('postcode_outward'):
        # Use outward code if available
        where['postcode_outward'] = params['postcode_outward'].strip().upper()
    
    # Capacity range filter
    capacity_filter = {}
    if params.get('min_capacity_kw') is not None:
        capacity_filter['$gte'] = float(params['min_capacity_kw'])
    if params.get('max_capacity_kw') is not None:
        capacity_filter['$lte'] = float(params['max_capacity_kw'])
    if capacity_filter:
        where['capacity_kw'] = capacity_filter
    
    # FIT ID filter (for direct lookups)
    if params.get('fit_id'):
        where['fit_id'] = str(params['fit_id'])
    
    return where if where else None

def enforce_postcode_prefixes(results: List[Dict], location: str = None, areas: List[str] = None, prefixes: List[str] = None) -> List[Dict]:
    """
    Final guardrail using exact area matching to ensure correct postcodes
    """
    if not location and not areas and not prefixes:
        return results
    
    # Get allowed areas
    if areas:
        allowed_areas = [a.upper() for a in areas]
    elif location:
        location_lower = location.lower()
        if location_lower == 'yorkshire':
            allowed_areas = YORKSHIRE_AREAS
        else:
            # Get prefixes and extract areas
            prefs = prefixes_for_region(location)
            if prefs:
                allowed_areas = list(set(extract_postcode_area(p) for p in prefs if p))
                allowed_areas = [a for a in allowed_areas if a]
            else:
                allowed_areas = []
    elif prefixes:
        # Extract areas from prefixes
        allowed_areas = list(set(extract_postcode_area(p) for p in prefixes if p))
        allowed_areas = [a for a in allowed_areas if a]
    else:
        return results
    
    if not allowed_areas:
        return results
    
    # Filter results by exact area match
    filtered = []
    for result in results:
        # Handle nested metadata
        if 'metadata' in result:
            postcode = str(result['metadata'].get('postcode', '')).upper().strip()
        else:
            postcode = str(result.get('postcode', '')).upper().strip()
        
        # Extract area from postcode
        area = extract_postcode_area(postcode)
        
        # Check if area matches exactly (not startswith)
        if area and area in allowed_areas:
            filtered.append(result)
    
    return filtered

def calculate_years_left(expiry_date: str, commission_date: str = None) -> Optional[float]:
    """Calculate years remaining on FIT contract (20-year contracts)"""
    try:
        # If no expiry date but have commission date, calculate expiry (20 years)
        if not expiry_date and commission_date:
            parts = str(commission_date).split('T')[0].split('-')
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
            commission = date(year, month, day)
            expiry = date(commission.year + 20, commission.month, commission.day)
        elif expiry_date:
            # Use provided expiry date
            parts = str(expiry_date).split('T')[0].split('-')
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
            expiry = date(year, month, day)
        else:
            return None
        
        today = date.today()
        delta = expiry - today
        years = max(0, round(delta.days / 365.25, 1))
        return years
    except Exception as e:
        logger.debug(f"Error calculating years left: {e}")
        return None

def calculate_annual_income(metadata: Dict) -> Optional[float]:
    """Calculate annual income from FIT"""
    try:
        rate = metadata.get('tariff_p_kwh')
        generation = metadata.get('annual_gen_kwh') or metadata.get('estimated_annual_generation')
        
        # If no generation data, estimate from capacity
        if rate is not None and generation is None:
            capacity = metadata.get('capacity_kw')
            if capacity:
                # Rough estimate: capacity * 900 hours/year for wind, 1000 for solar
                tech = metadata.get('technology', '').lower()
                if 'wind' in tech:
                    generation = capacity * 900
                elif 'solar' in tech or 'photovoltaic' in tech:
                    generation = capacity * 1000
                else:
                    generation = capacity * 950
        
        if rate is None or generation is None:
            return None
        
        # Convert pence to pounds
        annual_income = (float(rate) / 100.0) * float(generation)
        return round(annual_income, 2)
    except Exception as e:
        logger.debug(f"Error calculating income: {e}")
        return None

def enrich_result_with_financials(result: Dict) -> Dict:
    """Add financial calculations to a result"""
    metadata = result.get('metadata', {})
    
    # Calculate additional fields - use commission date as fallback for 20-year contracts
    years_left = calculate_years_left(
        metadata.get('fit_expiry_date'),
        metadata.get('commission_date')
    )
    annual_income = calculate_annual_income(metadata)
    
    # Add calculated fields
    if years_left is not None:
        metadata['years_left'] = years_left
    if annual_income is not None:
        metadata['annual_income_gbp'] = annual_income
    
    # Calculate total remaining value if we have both
    if years_left and annual_income:
        metadata['total_remaining_value_gbp'] = round(years_left * annual_income, 2)
    
    return result

def merge_search_params(previous: Dict, new: Dict) -> Dict:
    """
    Merge previous search parameters with new ones for context preservation
    Non-null values in new params override previous
    """
    merged = dict(previous or {})
    
    for key, value in (new or {}).items():
        # Only update if new value is meaningful
        if value not in (None, [], {}, ''):
            merged[key] = value
    
    return merged

def format_result_for_display(result: Dict, include_financials: bool = True) -> Dict:
    """Format a result for display with all required fields"""
    metadata = result.get('metadata', {})
    
    formatted = {
        'fit_id': metadata.get('fit_id') or metadata.get('installation_id'),
        'technology': metadata.get('technology'),
        'capacity_kw': metadata.get('capacity_kw'),
        'postcode': metadata.get('postcode'),
        'commission_date': metadata.get('commission_date')
    }
    
    if include_financials:
        formatted.update({
            'tariff_p_kwh': metadata.get('tariff_p_kwh'),
            'fit_expiry_date': metadata.get('fit_expiry_date'),
            'years_left': metadata.get('years_left'),
            'annual_income_gbp': metadata.get('annual_income_gbp'),
            'total_remaining_value_gbp': metadata.get('total_remaining_value_gbp')
        })
    
    return formatted