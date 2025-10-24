#!/usr/bin/env python3
"""
Calculate financial fields for FIT installations
"""

from datetime import date, datetime
import logging
from fit_rate_mapper import FITRateMapper
from regional_capacity_calculator import REGIONAL_CAPACITY_FACTORS, POSTCODE_REGIONS
import re

logger = logging.getLogger(__name__)

# Initialize FIT rate mapper once
try:
    rate_mapper = FITRateMapper()
except Exception as e:
    logger.warning(f"Could not load FIT rate mapper: {e}")
    rate_mapper = None

def format_date(date_str):
    """Format date as MMM/YYYY without time"""
    try:
        if not date_str:
            return None
        # Parse various date formats
        date_part = str(date_str).split('T')[0]
        dt = datetime.strptime(date_part, '%Y-%m-%d')
        return dt.strftime('%b/%Y')
    except Exception:
        return str(date_str)

def get_regional_capacity_factor(technology, postcode):
    """Get regional capacity factor based on postcode"""
    try:
        # Extract postcode prefix
        match = re.match(r'([A-Z]{1,2})', postcode)
        if not match:
            return None
        
        prefix = match.group(1)
        region = POSTCODE_REGIONS.get(prefix)
        
        if not region:
            return None
        
        # Normalize technology name
        tech_map = {
            'wind': 'Wind',
            'solar': 'Photovoltaic',
            'photovoltaic': 'Photovoltaic',
            'hydro': 'Hydro',
            'anaerobic': 'Anaerobic digestion',
            'chp': 'Micro CHP'
        }
        
        tech_key = None
        for k, v in tech_map.items():
            if k in technology.lower():
                tech_key = v
                break
        
        if not tech_key:
            return None
        
        # Get regional factors
        if tech_key in REGIONAL_CAPACITY_FACTORS:
            tech_factors = REGIONAL_CAPACITY_FACTORS[tech_key]
            if region in tech_factors:
                return tech_factors[region]['cf']
            elif 'all_regions' in tech_factors:
                return tech_factors['all_regions']['cf']
        
        return None
    except Exception as e:
        logger.debug(f"Error getting regional factor: {e}")
        return None

def calculate_fit_expiry_date(commission_date):
    """Calculate FIT expiry date (20 years from commissioning)"""
    try:
        if not commission_date:
            return None
        # Handle ISO date format
        date_part = str(commission_date).split('T')[0]
        y, m, d = [int(x) for x in date_part.split('-')]
        commission = date(y, m, d)
        # FIT contracts are 20 years from commissioning
        expiry = date(commission.year + 20, commission.month, commission.day)
        return expiry.strftime('%Y-%m-%d')
    except Exception as e:
        logger.debug(f"Error calculating expiry date: {e}")
        return None

def years_left(expiry, commission_date=None):
    """Calculate years remaining on FIT contract"""
    try:
        # If no expiry date, calculate from commission date (20 year contracts)
        if not expiry and commission_date:
            expiry = calculate_fit_expiry_date(commission_date)
        
        if not expiry:
            return None
        
        # Handle ISO date format
        date_part = str(expiry).split('T')[0]
        y, m, d = [int(x) for x in date_part.split('-')]
        expiry_date = date(y, m, d)
        today = date.today()
        days_left = (expiry_date - today).days
        return max(0, round(days_left / 365.25, 1))
    except Exception as e:
        logger.debug(f"Error calculating years left: {e}")
        return None

def calculate_solar_degradation_factor(technology, years_elapsed, years_remaining):
    """Calculate degradation factor for solar PV
    Year 1: 2% degradation
    Subsequent years: 0.54% annual degradation
    """
    if not technology or 'photovoltaic' not in technology.lower():
        return 1.0  # No degradation for non-solar
    
    # Calculate cumulative degradation up to current point
    if years_elapsed <= 1:
        current_efficiency = 0.98  # 2% loss in year 1
    else:
        # 2% in year 1, then 0.54% per year
        current_efficiency = 0.98 * (0.9946 ** (years_elapsed - 1))
    
    # Calculate average efficiency over remaining years
    total_factor = 0
    for year in range(int(years_remaining)):
        year_from_commission = years_elapsed + year
        if year_from_commission <= 1:
            year_efficiency = 0.98
        else:
            year_efficiency = 0.98 * (0.9946 ** (year_from_commission - 1))
        total_factor += year_efficiency
    
    # Return average degradation factor
    return total_factor / years_remaining if years_remaining > 0 else current_efficiency

def calculate_total_remaining_value(metadata):
    """Calculate total remaining FIT value over contract period with degradation"""
    try:
        # Get base annual income
        annual = annual_income(metadata)
        
        # Calculate years remaining
        years = years_left(
            metadata.get("fit_expiry_date"),
            metadata.get("commission_date")
        )
        
        if annual is None or years is None or years <= 0:
            return None
        
        # Handle zero annual income (e.g., 2019 sites with no FIT)
        if annual == 0:
            return 0
        
        # For solar PV, apply degradation
        technology = metadata.get("technology", "")
        commission_date = metadata.get("commission_date")
        
        if 'photovoltaic' in technology.lower() and commission_date:
            # Calculate years since commissioning
            try:
                from datetime import datetime
                comm_date = datetime.strptime(str(commission_date).split('T')[0], '%Y-%m-%d')
                years_elapsed = (datetime.now() - comm_date).days / 365.25
                years_elapsed = max(0, years_elapsed)
                
                # Apply degradation factor
                degradation_factor = calculate_solar_degradation_factor(
                    technology, years_elapsed, years
                )
                total = annual * years * degradation_factor
            except:
                # Fallback to simple calculation if date parsing fails
                total = annual * years * 0.95  # Conservative estimate
        else:
            # Non-solar: simple calculation
            total = annual * years
        
        return round(total, 2)
    except Exception as e:
        logger.debug(f"Error calculating total value: {e}")
        return None

def determine_repowering_window(years_remaining):
    """Determine repowering window category"""
    if years_remaining is None:
        return None
    elif years_remaining <= 0:
        return 'EXPIRED'
    elif years_remaining <= 2:
        return 'IMMEDIATE'
    elif years_remaining <= 5:
        return 'URGENT'
    elif years_remaining <= 10:
        return 'OPTIMAL'
    else:
        return 'FUTURE'

def annual_income(metadata, use_regional=True):
    """Calculate annual income from FIT"""
    try:
        rate = metadata.get("tariff_p_kwh")
        
        # If rate is missing or zero, look it up from historical tables
        if (rate is None or float(rate or 0) == 0) and rate_mapper:
            technology = metadata.get("technology")
            capacity_kw = metadata.get("capacity_kw")
            commission_date = metadata.get("commission_date")
            
            if technology and capacity_kw and commission_date:
                # Get historical FIT rate
                rate_info = rate_mapper.get_fit_rate(technology, capacity_kw, commission_date)
                if rate_info and rate_info.get('rate_p_kwh'):
                    rate = rate_info['rate_p_kwh']
                    logger.debug(f"Using historical FIT rate: {rate}p/kWh for {technology} {capacity_kw}kW commissioned {commission_date}")
        
        generation = metadata.get("annual_gen_kwh")
        
        # If no generation data, estimate from capacity
        if generation is None:
            capacity = metadata.get("capacity_kw")
            if capacity:
                tech = str(metadata.get("technology", "")).lower()
                postcode = str(metadata.get("postcode", "")).upper()
                
                # Get regional capacity factor if requested
                if use_regional:
                    regional_cf = get_regional_capacity_factor(tech, postcode)
                else:
                    regional_cf = None
                
                # Use regional factor if available, otherwise fallback to defaults
                if regional_cf and use_regional:
                    generation = float(capacity) * 8760 * regional_cf
                elif "wind" in tech:
                    generation = float(capacity) * 8760 * 0.25
                elif "solar" in tech or "photovoltaic" in tech:
                    generation = float(capacity) * 8760 * 0.11
                elif "hydro" in tech:
                    generation = float(capacity) * 8760 * 0.40
                else:
                    generation = float(capacity) * 8760 * 0.20
        
        if generation is None:
            return None
        
        # Handle zero or missing rate (e.g., 2019 sites after FIT closed)
        if rate is None or float(rate or 0) == 0:
            return 0  # Return 0 instead of None for zero-rate sites
        
        # Convert pence to pounds
        return round((float(rate) / 100.0) * float(generation), 2)
    except Exception as e:
        logger.debug(f"Error calculating income: {e}")
        return None

def render_result_summary(metadata):
    """Render a summary result for initial search display"""
    # Get or calculate tariff rate
    tariff = metadata.get("tariff_p_kwh")
    if (tariff is None or float(tariff or 0) == 0) and rate_mapper:
        technology = metadata.get("technology")
        capacity_kw = metadata.get("capacity_kw")
        commission_date = metadata.get("commission_date")
        
        if technology and capacity_kw and commission_date:
            rate_info = rate_mapper.get_fit_rate(technology, capacity_kw, commission_date)
            if rate_info and rate_info.get('rate_p_kwh'):
                tariff = rate_info['rate_p_kwh']
    
    # Calculate regional income
    annual_regional = annual_income(metadata, use_regional=True)
    
    # Calculate repowering window
    years_remaining = years_left(
        metadata.get("fit_expiry_date"),
        metadata.get("commission_date")
    )
    window = determine_repowering_window(years_remaining)
    
    # Calculate total remaining value
    total_value = calculate_total_remaining_value(metadata)
    
    return {
        "fit_id": metadata.get("fit_id") or metadata.get("installation_id"),
        "technology": metadata.get("technology"),
        "capacity_kw": metadata.get("capacity_kw"),
        "postcode": metadata.get("postcode"),
        "commission_date": format_date(metadata.get("commission_date")),
        "tariff_p_kwh": tariff,
        "years_left": years_remaining if years_remaining is not None else 0,
        "annual_income_gbp": annual_regional,
        "total_remaining_value": total_value,
        "repowering_window": window or metadata.get("repowering_window")
    }

def render_result_detailed(metadata):
    """Render a detailed result with all financial fields for drill-down"""
    # Get or calculate tariff rate
    tariff = metadata.get("tariff_p_kwh")
    if (tariff is None or float(tariff or 0) == 0) and rate_mapper:
        technology = metadata.get("technology")
        capacity_kw = metadata.get("capacity_kw")
        commission_date = metadata.get("commission_date")
        
        if technology and capacity_kw and commission_date:
            rate_info = rate_mapper.get_fit_rate(technology, capacity_kw, commission_date)
            if rate_info and rate_info.get('rate_p_kwh'):
                tariff = rate_info['rate_p_kwh']
    
    # Calculate both standard and regional income
    annual_standard = annual_income(metadata, use_regional=False)
    annual_regional = annual_income(metadata, use_regional=True)
    
    # Calculate years left and repowering window
    years_remaining = years_left(
        metadata.get("fit_expiry_date"),
        metadata.get("commission_date")
    )
    window = determine_repowering_window(years_remaining)
    
    # Calculate total value properly using the function with degradation
    total_value = calculate_total_remaining_value(metadata)
    
    # Get regional capacity factor for display
    tech = str(metadata.get("technology", "")).lower()
    postcode = str(metadata.get("postcode", "")).upper()
    regional_cf = get_regional_capacity_factor(tech, postcode)
    
    return {
        "fit_id": metadata.get("fit_id") or metadata.get("installation_id"),
        "technology": metadata.get("technology"),
        "capacity_kw": metadata.get("capacity_kw"),
        "postcode": metadata.get("postcode"),
        "commission_date": format_date(metadata.get("commission_date")),
        "tariff_p_kwh": tariff,
        "fit_expiry_date": format_date(
            metadata.get("fit_expiry_date") or 
            calculate_fit_expiry_date(metadata.get("commission_date"))
        ),
        "years_left": years_remaining if years_remaining is not None else 0,
        "annual_income_standard": annual_standard,
        "annual_income_regional": annual_regional,
        "regional_capacity_factor": regional_cf,
        "total_remaining_value": total_value,
        "repowering_window": window or metadata.get("repowering_window")
    }

# Keep the original for backward compatibility
def render_result(metadata):
    """Render a result with all financial fields (uses summary view)"""
    return render_result_summary(metadata)