#!/usr/bin/env python3
"""
FIT License Data Processor
Processes FIT Installation Reports and FIT Tariff data to create enhanced embeddings
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FITLicenseProcessor:
    """
    Processes FIT License data and creates intelligent embeddings
    linking licenses to their specific tariff rates and terms
    """
    
    def __init__(self):
        """Initialize the processor"""
        self.fit_installations = None
        self.fit_tariffs = None
        self.processed_licenses = None
        
    def load_fit_installation_data(self) -> pd.DataFrame:
        """Load and combine all FIT Installation Report parts"""
        try:
            logger.info("Loading FIT Installation data...")
            
            all_installations = []
            
            for part_num in [1, 2, 3]:
                filename = f'data/Feed-in Tariff Installation Report Part {part_num}.xlsx'
                logger.info(f"Loading {filename}...")
                
                try:
                    # First, read without header to inspect structure
                    temp_df = pd.read_excel(filename, sheet_name=0, header=None)
                    
                    # Find the header row by looking for "FIT ID" or similar
                    header_row = None
                    for idx in range(min(10, len(temp_df))):
                        row_text = ' '.join([str(cell) for cell in temp_df.iloc[idx] if pd.notna(cell)])
                        if 'FIT ID' in row_text or 'Extension' in row_text:
                            header_row = idx
                            break
                    
                    if header_row is not None:
                        # Read with correct header
                        df = pd.read_excel(filename, sheet_name=0, header=header_row)
                        # Clean column names
                        df.columns = df.columns.str.strip()
                    else:
                        logger.warning(f"Could not find header row in {filename}")
                        continue
                    
                    logger.info(f"Part {part_num}: {len(df)} installations")
                    logger.info(f"Columns: {list(df.columns)}")
                    
                    # Add to combined dataset
                    all_installations.append(df)
                    
                except Exception as e:
                    logger.error(f"Error reading Part {part_num}: {e}")
                    continue
            
            if all_installations:
                combined_df = pd.concat(all_installations, ignore_index=True)
                logger.info(f"Combined dataset: {len(combined_df)} total installations")
                
                # Show sample data
                logger.info("Sample installation data:")
                print(combined_df.head())
                
                self.fit_installations = combined_df
                return combined_df
            else:
                logger.error("No installation data loaded")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error loading installation data: {e}")
            return pd.DataFrame()
    
    def load_fit_tariff_data(self) -> pd.DataFrame:
        """Load and process FIT tariff table"""
        try:
            logger.info("Loading FIT tariff data...")
            
            # The tariff file needs special handling as it has header information
            df = pd.read_excel('data/feed-in_tariff_table_1_april_2010_-_31_march_2020_0.xlsx')
            
            # Find the actual data start (usually after several header rows)
            # Look for rows that contain tariff data patterns
            data_start_row = None
            for idx, row in df.iterrows():
                if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip():
                    # Check if this looks like tariff data
                    content = str(row.iloc[0]).lower()
                    if any(keyword in content for keyword in ['photovoltaic', 'wind', 'hydro', 'tariff', 'p/kwh']):
                        data_start_row = idx
                        break
            
            if data_start_row is not None:
                # Re-read with proper header
                tariff_df = pd.read_excel(
                    'data/feed-in_tariff_table_1_april_2010_-_31_march_2020_0.xlsx',
                    header=data_start_row
                )
                logger.info(f"Tariff data loaded: {len(tariff_df)} rows")
                logger.info("Tariff data sample:")
                print(tariff_df.head())
                
                self.fit_tariffs = tariff_df
                return tariff_df
            else:
                logger.error("Could not find tariff data start")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error loading tariff data: {e}")
            return pd.DataFrame()
    
    def create_license_tariff_mapping(self) -> Dict:
        """
        Create intelligent mapping between licenses and their applicable tariffs
        """
        try:
            logger.info("Creating license-tariff mapping...")
            
            if self.fit_installations is None or self.fit_installations.empty:
                logger.error("No installation data available")
                return {}
            
            # Extract key information from installations
            license_data = []
            
            for idx, installation in self.fit_installations.iterrows():
                # Extract key fields (adjust based on actual column names)
                license_info = self._extract_license_info(installation)
                if license_info:
                    license_data.append(license_info)
            
            logger.info(f"Processed {len(license_data)} license records")
            
            # Group by technology and date ranges for tariff matching
            tariff_mapping = self._match_licenses_to_tariffs(license_data)
            
            return {
                'license_count': len(license_data),
                'license_data': license_data,
                'tariff_mapping': tariff_mapping
            }
            
        except Exception as e:
            logger.error(f"Error creating mapping: {e}")
            return {}
    
    def _extract_license_info(self, installation: pd.Series) -> Optional[Dict]:
        """Extract relevant information from installation record"""
        try:
            # Note: Column names will need to be adjusted based on actual Excel structure
            # This is a template - actual column names should be determined from the data
            
            license_info = {}
            
            # Basic identification
            if 'FIT ID' in installation and pd.notna(installation['FIT ID']):
                license_info['fit_id'] = str(installation['FIT ID'])
            else:
                return None  # Skip records without FIT ID
            
            # Technology type
            technology_fields = ['Technology', 'Installation Type', 'Technology Type']
            for field in technology_fields:
                if field in installation and pd.notna(installation[field]):
                    license_info['technology'] = str(installation[field]).strip()
                    break
            
            # Capacity
            capacity_fields = ['Declared Net Capacity (kW)', 'Capacity (kW)', 'DNC (kW)', 'Capacity']
            for field in capacity_fields:
                if field in installation and pd.notna(installation[field]):
                    try:
                        capacity_kw = float(installation[field])
                        license_info['capacity_kw'] = capacity_kw
                        license_info['capacity_mw'] = capacity_kw / 1000
                        break
                    except (ValueError, TypeError):
                        continue
            
            # Commission date
            date_fields = ['Commission Date', 'Commissioning Date', 'Accreditation Date']
            for field in date_fields:
                if field in installation and pd.notna(installation[field]):
                    try:
                        # Handle various date formats
                        date_val = installation[field]
                        if isinstance(date_val, str):
                            # Parse string dates
                            commission_date = pd.to_datetime(date_val)
                        else:
                            commission_date = pd.to_datetime(date_val)
                        
                        license_info['commission_date'] = commission_date.isoformat()
                        break
                    except (ValueError, TypeError):
                        continue
            
            # Location information
            location_fields = ['Postcode', 'Post Code', 'Location']
            for field in location_fields:
                if field in installation and pd.notna(installation[field]):
                    license_info['postcode'] = str(installation[field]).strip().upper()
                    break
            
            # Export type (for tariff determination)
            export_fields = ['Export', 'Export Type', 'Tariff Type']
            for field in export_fields:
                if field in installation and pd.notna(installation[field]):
                    license_info['export_type'] = str(installation[field]).strip()
                    break
            
            return license_info if license_info else None
            
        except Exception as e:
            logger.debug(f"Error extracting license info: {e}")
            return None
    
    def _match_licenses_to_tariffs(self, license_data: List[Dict]) -> Dict:
        """Match licenses to their applicable FIT tariffs"""
        try:
            logger.info("Matching licenses to tariffs...")
            
            # This is where we would implement the complex tariff matching logic
            # based on technology, capacity bands, commission dates, etc.
            
            tariff_mapping = {}
            
            # Group licenses by key characteristics
            tech_groups = {}
            for license in license_data:
                tech = license.get('technology', 'Unknown')
                if tech not in tech_groups:
                    tech_groups[tech] = []
                tech_groups[tech].append(license)
            
            logger.info("Technology distribution:")
            for tech, licenses in tech_groups.items():
                logger.info(f"  {tech}: {len(licenses)} licenses")
                
            # For now, create basic mapping structure
            # This would be enhanced with actual tariff rate lookups
            for tech, licenses in tech_groups.items():
                tariff_mapping[tech] = {
                    'license_count': len(licenses),
                    'capacity_range': self._get_capacity_range(licenses),
                    'date_range': self._get_date_range(licenses),
                    'sample_licenses': licenses[:5]  # Store samples
                }
            
            return tariff_mapping
            
        except Exception as e:
            logger.error(f"Error matching tariffs: {e}")
            return {}
    
    def _get_capacity_range(self, licenses: List[Dict]) -> Dict:
        """Get capacity range for a group of licenses"""
        capacities = [l.get('capacity_kw', 0) for l in licenses if l.get('capacity_kw')]
        if capacities:
            return {
                'min_kw': min(capacities),
                'max_kw': max(capacities),
                'avg_kw': np.mean(capacities)
            }
        return {}
    
    def _get_date_range(self, licenses: List[Dict]) -> Dict:
        """Get commission date range for a group of licenses"""
        dates = []
        for l in licenses:
            if l.get('commission_date'):
                try:
                    dates.append(pd.to_datetime(l['commission_date']))
                except:
                    continue
        
        if dates:
            return {
                'earliest': min(dates).isoformat(),
                'latest': max(dates).isoformat(),
                'span_years': (max(dates) - min(dates)).days / 365.25
            }
        return {}
    
    def create_enhanced_embeddings(self) -> List[Dict]:
        """
        Create enhanced embeddings that include license-specific tariff information
        """
        try:
            logger.info("Creating enhanced embeddings...")
            
            if not self.processed_licenses:
                logger.error("No processed licenses available")
                return []
            
            enhanced_embeddings = []
            
            # Create embeddings for each license with rich tariff context
            for license in self.processed_licenses['license_data']:
                embedding_text = self._create_license_embedding_text(license)
                metadata = self._create_license_metadata(license)
                
                enhanced_embeddings.append({
                    'id': f"license_{license.get('fit_id', 'unknown')}",
                    'text': embedding_text,
                    'metadata': metadata,
                    'type': 'fit_license'
                })
            
            logger.info(f"Created {len(enhanced_embeddings)} enhanced embeddings")
            return enhanced_embeddings
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            return []
    
    def _create_license_embedding_text(self, license: Dict) -> str:
        """Create rich text for license embedding"""
        text_parts = []
        
        # Basic identification
        fit_id = license.get('fit_id', 'unknown')
        technology = license.get('technology', 'unknown technology')
        text_parts.append(f"FIT license {fit_id} for {technology}")
        
        # Capacity information
        if license.get('capacity_kw'):
            capacity_kw = license['capacity_kw']
            capacity_mw = license.get('capacity_mw', capacity_kw / 1000)
            
            # Add capacity band description
            if capacity_kw <= 4:
                text_parts.append(f"{capacity_kw}kW micro-generation installation")
            elif capacity_kw <= 10:
                text_parts.append(f"{capacity_kw}kW small residential installation")
            elif capacity_kw <= 50:
                text_parts.append(f"{capacity_kw}kW small commercial installation")
            elif capacity_kw <= 250:
                text_parts.append(f"{capacity_kw}kW medium commercial installation")
            elif capacity_kw <= 1000:
                text_parts.append(f"{capacity_mw:.2f}MW large commercial installation")
            else:
                text_parts.append(f"{capacity_mw:.2f}MW utility-scale installation")
        
        # Commission date context
        if license.get('commission_date'):
            try:
                comm_date = pd.to_datetime(license['commission_date'])
                year = comm_date.year
                
                # Add historical tariff context
                if year <= 2012:
                    text_parts.append(f"commissioned {year}, early high-tariff period")
                elif year <= 2015:
                    text_parts.append(f"commissioned {year}, medium tariff period")
                elif year <= 2019:
                    text_parts.append(f"commissioned {year}, lower tariff period")
                else:
                    text_parts.append(f"commissioned {year}, final tariff period")
                
                # Calculate current age and remaining FIT
                current_date = datetime.now()
                age = (current_date - comm_date).days / 365.25
                remaining_fit = max(0, 20 - age)  # FIT is 20 years
                
                if remaining_fit > 15:
                    text_parts.append("long-term FIT benefits remaining")
                elif remaining_fit > 10:
                    text_parts.append("substantial FIT benefits remaining")
                elif remaining_fit > 5:
                    text_parts.append("moderate FIT benefits remaining")
                elif remaining_fit > 0:
                    text_parts.append("limited FIT benefits remaining, PPA opportunity")
                else:
                    text_parts.append("FIT expired, requires PPA")
                    
            except:
                pass
        
        # Technology-specific details
        tech_lower = technology.lower()
        if 'photovoltaic' in tech_lower or 'solar' in tech_lower:
            text_parts.append("solar PV renewable energy system")
        elif 'wind' in tech_lower:
            text_parts.append("wind energy generation system")
        elif 'hydro' in tech_lower:
            text_parts.append("hydroelectric power system")
        elif 'anaerobic' in tech_lower:
            text_parts.append("biogas anaerobic digestion system")
        
        # Location context
        if license.get('postcode'):
            postcode = license['postcode']
            text_parts.append(f"located in {postcode} postcode area")
        
        # Export status
        if license.get('export_type'):
            export_type = license['export_type']
            if 'total' in export_type.lower():
                text_parts.append("total export to grid")
            elif 'deemed' in export_type.lower():
                text_parts.append("deemed export arrangement")
        
        return ". ".join(text_parts) + "."
    
    def _create_license_metadata(self, license: Dict) -> Dict:
        """Create metadata for license embedding"""
        metadata = license.copy()  # Start with license data
        
        # Add computed fields
        if license.get('commission_date'):
            try:
                comm_date = pd.to_datetime(license['commission_date'])
                current_date = datetime.now()
                
                age = (current_date - comm_date).days / 365.25
                remaining_fit = max(0, 20 - age)
                
                metadata.update({
                    'age_years': round(age, 1),
                    'remaining_fit_years': round(remaining_fit, 1),
                    'fit_expiry_date': (comm_date + timedelta(days=20*365)).isoformat()
                })
                
                # Repowering window
                if remaining_fit <= 0:
                    metadata['repowering_window'] = 'EXPIRED'
                elif remaining_fit <= 2:
                    metadata['repowering_window'] = 'IMMEDIATE'
                elif remaining_fit <= 5:
                    metadata['repowering_window'] = 'URGENT'
                else:
                    metadata['repowering_window'] = 'OPTIMAL'
                    
            except:
                pass
        
        # Capacity categories
        capacity_kw = license.get('capacity_kw', 0)
        if capacity_kw <= 4:
            metadata['size_category'] = 'Micro (<4kW)'
        elif capacity_kw <= 50:
            metadata['size_category'] = 'Small (4-50kW)'
        elif capacity_kw <= 250:
            metadata['size_category'] = 'Medium (50-250kW)'
        elif capacity_kw <= 1000:
            metadata['size_category'] = 'Large (250kW-1MW)'
        else:
            metadata['size_category'] = 'Utility (>1MW)'
        
        # Grid connection category
        if capacity_kw <= 16:
            metadata['grid_category'] = 'Single Phase'
        elif capacity_kw <= 100:
            metadata['grid_category'] = 'Three Phase'
        elif capacity_kw <= 1000:
            metadata['grid_category'] = 'Distribution'
        else:
            metadata['grid_category'] = 'Transmission'
        
        return metadata
    
    def process_all_data(self) -> Dict:
        """Main processing function"""
        try:
            logger.info("Starting full FIT license data processing...")
            
            # Load installation data
            installations = self.load_fit_installation_data()
            if installations.empty:
                return {'error': 'Failed to load installation data'}
            
            # Load tariff data
            tariffs = self.load_fit_tariff_data()
            # Note: tariff data processing would be more complex in practice
            
            # Create license-tariff mapping
            license_mapping = self.create_license_tariff_mapping()
            self.processed_licenses = license_mapping
            
            # Create enhanced embeddings
            enhanced_embeddings = self.create_enhanced_embeddings()
            
            # Save processed data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'data/enhanced_fit_licenses_{timestamp}.json'
            
            output_data = {
                'metadata': {
                    'processed_date': datetime.now().isoformat(),
                    'total_installations': len(installations),
                    'processed_licenses': len(license_mapping.get('license_data', [])),
                    'enhanced_embeddings': len(enhanced_embeddings)
                },
                'license_mapping': license_mapping,
                'enhanced_embeddings': enhanced_embeddings
            }
            
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
            
            logger.info(f"Processing complete. Data saved to {output_file}")
            
            return output_data
            
        except Exception as e:
            logger.error(f"Error in processing: {e}")
            return {'error': str(e)}

# Test the processor
if __name__ == "__main__":
    print("=" * 60)
    print("FIT LICENSE PROCESSOR")
    print("=" * 60)
    
    processor = FITLicenseProcessor()
    result = processor.process_all_data()
    
    if 'error' not in result:
        print(f"\n✓ Successfully processed {result['metadata']['processed_licenses']} licenses")
        print(f"✓ Created {result['metadata']['enhanced_embeddings']} enhanced embeddings")
        print(f"✓ Total installations found: {result['metadata']['total_installations']}")
    else:
        print(f"\n✗ Processing failed: {result['error']}")