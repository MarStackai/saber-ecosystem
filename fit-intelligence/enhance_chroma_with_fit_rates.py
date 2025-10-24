#!/usr/bin/env python3
"""
Enhance Chroma Database with FIT Rate Data
Integrates FIT pricing information into existing commercial sites and licenses
"""

import json
import pandas as pd
from datetime import datetime
import logging
from fit_rate_mapper import FITRateMapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaFITEnhancer:
    def __init__(self):
        self.fit_mapper = FITRateMapper()
        self.enhanced_sites = []
        self.enhanced_licenses = []
    
    def enhance_commercial_sites(self):
        """Enhance existing commercial sites with FIT rate data"""
        logger.info("Loading commercial sites data...")
        
        with open('data/all_commercial_fit.json', 'r') as f:
            data = json.load(f)
        
        sites = data.get('sites', [])
        logger.info(f"Enhancing {len(sites):,} commercial sites with FIT rates...")
        
        enhanced_count = 0
        
        for site in sites:
            try:
                # Get site data
                technology = site.get('technology', '')
                capacity_kw = site.get('capacity_kw', 0)
                commission_date = site.get('commission_date', '')
                
                # Get FIT rate
                fit_info = self.fit_mapper.get_fit_rate(technology, capacity_kw, commission_date)
                
                if fit_info and fit_info.get('rate_p_kwh'):
                    # Add FIT rate information to site
                    site['fit_rate_p_kwh'] = fit_info['rate_p_kwh']
                    site['fit_period'] = fit_info['fit_period']
                    site['fit_capacity_band'] = fit_info['capacity_band']
                    
                    # Calculate annual FIT revenue
                    if 'annual_generation_mwh' in site:
                        annual_generation_kwh = site['annual_generation_mwh'] * 1000
                        site['annual_fit_revenue_gbp'] = annual_generation_kwh * fit_info['rate_p_kwh'] / 100
                    
                    # Create enhanced document text for Chroma embeddings
                    site['chroma_document'] = self.create_site_document(site)
                    enhanced_count += 1
                
                self.enhanced_sites.append(site)
                
            except Exception as e:
                logger.debug(f"Error enhancing site: {e}")
                self.enhanced_sites.append(site)
        
        logger.info(f"Enhanced {enhanced_count:,} sites with FIT rate data")
        return self.enhanced_sites
    
    def enhance_fit_licenses(self):
        """Enhance FIT licenses with potential FIT rate data"""
        logger.info("Loading FIT licenses data...")
        
        # Load processed license data
        try:
            # Look for license data files
            license_files = [
                'data/processed_fit_licenses_20250821_072621.json',
                'data/all_fit_licenses.json',
                'data/fit_licenses_enhanced.json'
            ]
            
            licenses = []
            for file_path in license_files:
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            licenses = data
                            logger.info(f"Loaded {len(licenses):,} licenses from {file_path}")
                            break
                        elif isinstance(data, dict) and 'licenses' in data:
                            licenses = data['licenses']
                            logger.info(f"Loaded {len(licenses):,} licenses from {file_path}")
                            break
                except FileNotFoundError:
                    continue
            
            if not licenses:
                logger.warning("No license data found")
                return []
            
            enhanced_count = 0
            
            for license_data in licenses:
                try:
                    # Extract license info (structure may vary)
                    technology = license_data.get('Technology', license_data.get('technology', ''))
                    capacity_mw = license_data.get('capacity_mw', license_data.get('Capacity_MW', 0))
                    capacity_kw = capacity_mw * 1000 if capacity_mw else 0
                    
                    # Use grant date or application date for FIT period
                    grant_date = license_data.get('grant_date', license_data.get('application_date', ''))
                    
                    if technology and capacity_kw and grant_date:
                        # Get potential FIT rate if developed
                        fit_info = self.fit_mapper.get_fit_rate(technology, capacity_kw, grant_date)
                        
                        if fit_info and fit_info.get('rate_p_kwh'):
                            # Add potential FIT information
                            license_data['potential_fit_rate_p_kwh'] = fit_info['rate_p_kwh']
                            license_data['potential_fit_period'] = fit_info['fit_period']
                            license_data['potential_fit_capacity_band'] = fit_info['capacity_band']
                            
                            # Calculate potential annual FIT revenue
                            if capacity_kw:
                                # Estimate annual generation based on technology
                                capacity_factors = {
                                    'Wind': 0.27,
                                    'Photovoltaic': 0.11, 
                                    'Hydro': 0.38,
                                    'Anaerobic digestion': 0.80
                                }
                                
                                cf = capacity_factors.get(technology, 0.25)
                                annual_generation_kwh = capacity_kw * 8760 * cf
                                license_data['potential_annual_fit_revenue_gbp'] = (
                                    annual_generation_kwh * fit_info['rate_p_kwh'] / 100
                                )
                            
                            # Create enhanced document text for Chroma embeddings
                            license_data['chroma_document'] = self.create_license_document(license_data)
                            enhanced_count += 1
                    
                    self.enhanced_licenses.append(license_data)
                    
                except Exception as e:
                    logger.debug(f"Error enhancing license: {e}")
                    self.enhanced_licenses.append(license_data)
            
            logger.info(f"Enhanced {enhanced_count:,} licenses with potential FIT rate data")
            
        except Exception as e:
            logger.error(f"Error loading license data: {e}")
        
        return self.enhanced_licenses
    
    def create_site_document(self, site):
        """Create enhanced document text for Chroma embedding"""
        
        # Base information
        tech = site.get('technology', 'Unknown')
        capacity = site.get('capacity_kw', 0)
        location = f"{site.get('postcode', '')} {site.get('region', '')}".strip()
        
        # FIT information
        fit_rate = site.get('fit_rate_p_kwh', 0)
        fit_period = site.get('fit_period', '')
        annual_revenue = site.get('annual_fit_revenue_gbp', 0)
        
        # Repowering context
        remaining_years = site.get('remaining_fit_years', 0)
        repowering_window = site.get('repowering_window', 'UNKNOWN')
        
        # Age and commissioning
        age = site.get('age_years', 0)
        commission_date = site.get('commission_date', '')
        
        document = f"""
{tech} installation of {capacity:.0f}kW capacity located in {location}.
Commissioned {commission_date[:10]} ({age:.1f} years old).
FIT rate: {fit_rate}p/kWh from {fit_period} tariff period.
Annual FIT revenue: £{annual_revenue:,.0f} per year.
Remaining FIT years: {remaining_years:.1f}, repowering window: {repowering_window}.
Commercial {tech.lower()} site with established revenue stream and repowering opportunity.
        """.strip()
        
        return document
    
    def create_license_document(self, license_data):
        """Create enhanced document text for license Chroma embedding"""
        
        # Base information
        tech = license_data.get('Technology', license_data.get('technology', 'Unknown'))
        capacity_mw = license_data.get('capacity_mw', license_data.get('Capacity_MW', 0))
        location = license_data.get('location', license_data.get('postcode', ''))
        
        # Potential FIT information
        potential_rate = license_data.get('potential_fit_rate_p_kwh', 0)
        potential_period = license_data.get('potential_fit_period', '')
        potential_revenue = license_data.get('potential_annual_fit_revenue_gbp', 0)
        
        # License details
        status = license_data.get('status', 'Unknown')
        grant_date = license_data.get('grant_date', license_data.get('application_date', ''))
        
        document = f"""
{tech} license for {capacity_mw:.1f}MW capacity in {location}.
License granted {grant_date[:10]}, status: {status}.
Potential FIT rate: {potential_rate}p/kWh from {potential_period} tariff period if developed.
Potential annual FIT revenue: £{potential_revenue:,.0f} per year.
Undeveloped {tech.lower()} license with commercial FIT potential and development opportunity.
        """.strip()
        
        return document
    
    def save_enhanced_data(self):
        """Save enhanced data to files"""
        
        # Save enhanced sites
        if self.enhanced_sites:
            enhanced_sites_data = {
                'enhanced_timestamp': datetime.now().isoformat(),
                'total_sites': len(self.enhanced_sites),
                'sites_with_fit_rates': len([s for s in self.enhanced_sites if s.get('fit_rate_p_kwh')]),
                'sites': self.enhanced_sites
            }
            
            with open('data/commercial_sites_enhanced_with_fit.json', 'w') as f:
                json.dump(enhanced_sites_data, f, indent=2)
            
            logger.info(f"Saved {len(self.enhanced_sites):,} enhanced sites")
        
        # Save enhanced licenses
        if self.enhanced_licenses:
            enhanced_licenses_data = {
                'enhanced_timestamp': datetime.now().isoformat(),
                'total_licenses': len(self.enhanced_licenses),
                'licenses_with_fit_potential': len([l for l in self.enhanced_licenses if l.get('potential_fit_rate_p_kwh')]),
                'licenses': self.enhanced_licenses
            }
            
            with open('data/fit_licenses_enhanced_with_rates.json', 'w') as f:
                json.dump(enhanced_licenses_data, f, indent=2)
            
            logger.info(f"Saved {len(self.enhanced_licenses):,} enhanced licenses")

def main():
    """Main enhancement process"""
    enhancer = ChromaFITEnhancer()
    
    # Enhance commercial sites
    logger.info("=== ENHANCING COMMERCIAL SITES ===")
    enhancer.enhance_commercial_sites()
    
    # Enhance licenses
    logger.info("=== ENHANCING FIT LICENSES ===")
    enhancer.enhance_fit_licenses()
    
    # Save enhanced data
    logger.info("=== SAVING ENHANCED DATA ===")
    enhancer.save_enhanced_data()
    
    logger.info("✅ FIT rate enhancement complete!")

if __name__ == "__main__":
    main()