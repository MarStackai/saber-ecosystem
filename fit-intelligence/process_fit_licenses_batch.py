#!/usr/bin/env python3
"""
Batch FIT License Processor
Efficiently processes large Excel files and creates embeddings
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchFITProcessor:
    """Efficient batch processor for FIT license data"""
    
    def __init__(self, max_records: int = 100000):
        self.max_records = max_records
        self.processed_licenses = []
        
    def process_single_part(self, part_num: int, limit: int = None) -> List[Dict]:
        """Process a single part of the FIT data"""
        filename = f'data/Feed-in Tariff Installation Report Part {part_num}.xlsx'
        logger.info(f"Processing {filename}...")
        
        try:
            # Find header row
            temp_df = pd.read_excel(filename, sheet_name=0, header=None, nrows=10)
            header_row = None
            for idx in range(len(temp_df)):
                row_text = ' '.join([str(cell) for cell in temp_df.iloc[idx] if pd.notna(cell)])
                if 'FIT ID' in row_text:
                    header_row = idx
                    break
            
            if header_row is None:
                logger.warning(f"No header found in {filename}")
                return []
            
            # Read data with header (limit rows if specified)
            nrows = limit if limit else None
            df = pd.read_excel(filename, sheet_name=0, header=header_row, nrows=nrows)
            df.columns = df.columns.str.strip()
            
            logger.info(f"Read {len(df)} rows from Part {part_num}")
            
            # Process records
            licenses = []
            for idx, row in df.iterrows():
                license_info = self._extract_license_info(row)
                if license_info:
                    licenses.append(license_info)
                
                # Progress logging
                if (idx + 1) % 10000 == 0:
                    logger.info(f"Processed {idx + 1} rows, extracted {len(licenses)} valid licenses")
            
            logger.info(f"Part {part_num} complete: {len(licenses)} valid licenses from {len(df)} rows")
            return licenses
            
        except Exception as e:
            logger.error(f"Error processing Part {part_num}: {e}")
            return []
    
    def _extract_license_info(self, row: pd.Series) -> Optional[Dict]:
        """Extract and validate license information"""
        try:
            # Must have FIT ID
            fit_id = row.get('FIT ID')
            if pd.isna(fit_id):
                return None
            
            # Must have technology
            technology = row.get('Technology')
            if pd.isna(technology) or not str(technology).strip():
                return None
            
            # Basic license info
            license_info = {
                'fit_id': str(int(fit_id)),
                'technology': str(technology).strip(),
                'postcode': self._clean_string(row.get('PostCode ')),
                'tariff_code': self._clean_string(row.get('TariffCode')),
                'export_status': self._clean_string(row.get('Export status')),
                'installation_type': self._clean_string(row.get('Installation Type')),
                'country': self._clean_string(row.get('Installation Country')),
                'region': self._clean_string(row.get('Government Office Region')),
                'local_authority': self._clean_string(row.get('Local Authority')),
                'constituency': self._clean_string(row.get('Constituency')),
            }
            
            # Capacity processing
            declared_cap = row.get('Declared net capacity')
            installed_cap = row.get('Installed capacity')
            
            capacity_kw = 0.0
            if pd.notna(declared_cap) and float(declared_cap) > 0:
                capacity_kw = float(declared_cap)
            elif pd.notna(installed_cap) and float(installed_cap) > 0:
                capacity_kw = float(installed_cap)
            
            license_info['capacity_kw'] = capacity_kw
            license_info['capacity_mw'] = capacity_kw / 1000
            
            # Date processing
            comm_date = row.get('Commissioning date')
            if pd.notna(comm_date):
                try:
                    if isinstance(comm_date, str):
                        comm_dt = pd.to_datetime(comm_date, errors='coerce')
                    else:
                        comm_dt = pd.to_datetime(comm_date)
                    
                    if pd.notna(comm_dt):
                        license_info['commission_date'] = comm_dt.isoformat()
                        
                        # Calculate age and remaining FIT
                        current_date = datetime.now()
                        age_days = (current_date - comm_dt).days
                        age_years = age_days / 365.25
                        remaining_fit_years = max(0, 20 - age_years)
                        
                        license_info['age_years'] = round(age_years, 1)
                        license_info['remaining_fit_years'] = round(remaining_fit_years, 1)
                        license_info['fit_expiry_date'] = (comm_dt + timedelta(days=20*365)).isoformat()
                        
                        # Determine repowering window
                        if remaining_fit_years <= 0:
                            license_info['repowering_window'] = 'EXPIRED'
                        elif remaining_fit_years <= 2:
                            license_info['repowering_window'] = 'IMMEDIATE'
                        elif remaining_fit_years <= 5:
                            license_info['repowering_window'] = 'URGENT'
                        else:
                            license_info['repowering_window'] = 'OPTIMAL'
                    
                except Exception as date_error:
                    logger.debug(f"Date processing error for FIT {fit_id}: {date_error}")
            
            # Add categorization
            self._add_categorization(license_info)
            
            return license_info
            
        except Exception as e:
            logger.debug(f"Error extracting license info: {e}")
            return None
    
    def _clean_string(self, value) -> str:
        """Clean string values"""
        if pd.isna(value):
            return ''
        return str(value).strip()
    
    def _add_categorization(self, license_info: Dict):
        """Add size and grid categorization"""
        capacity_kw = license_info['capacity_kw']
        
        # Size categories
        if capacity_kw <= 4:
            license_info['size_category'] = 'Micro (<4kW)'
            license_info['grid_category'] = 'Single Phase'
            license_info['commercial_status'] = 'Residential'
        elif capacity_kw <= 50:
            license_info['size_category'] = 'Small (4-50kW)'
            license_info['grid_category'] = 'Single/Three Phase'
            license_info['commercial_status'] = 'Small Commercial'
        elif capacity_kw <= 250:
            license_info['size_category'] = 'Medium (50-250kW)'
            license_info['grid_category'] = 'Three Phase'
            license_info['commercial_status'] = 'Commercial'
        elif capacity_kw <= 1000:
            license_info['size_category'] = 'Large (250kW-1MW)'
            license_info['grid_category'] = 'Distribution'
            license_info['commercial_status'] = 'Large Commercial'
        else:
            license_info['size_category'] = 'Utility (>1MW)'
            license_info['grid_category'] = 'Transmission'
            license_info['commercial_status'] = 'Utility Scale'
    
    def process_all_parts(self, records_per_part: int = 30000) -> List[Dict]:
        """Process all three parts with record limits"""
        all_licenses = []
        
        for part_num in [1, 2, 3]:
            if len(all_licenses) >= self.max_records:
                break
                
            remaining = self.max_records - len(all_licenses)
            limit = min(records_per_part, remaining)
            
            part_licenses = self.process_single_part(part_num, limit=limit)
            all_licenses.extend(part_licenses)
            
            logger.info(f"Total processed so far: {len(all_licenses)} licenses")
            
            if len(all_licenses) >= self.max_records:
                break
        
        self.processed_licenses = all_licenses
        return all_licenses
    
    def create_embeddings_data(self) -> Dict:
        """Create embedding-ready data structure"""
        logger.info("Creating embeddings data...")
        
        embeddings_data = []
        
        for license_info in self.processed_licenses:
            # Create rich embedding text
            embedding_text = self._create_embedding_text(license_info)
            
            # Prepare metadata (ensure JSON serializable)
            metadata = {}
            for key, value in license_info.items():
                if pd.isna(value) or value == 'nan' or value == '':
                    metadata[key] = ''
                elif isinstance(value, (int, float, str, bool)):
                    metadata[key] = value
                else:
                    metadata[key] = str(value)
            
            embeddings_data.append({
                'id': f"license_{license_info['fit_id']}",
                'text': embedding_text,
                'metadata': metadata,
                'type': 'fit_license'
            })
        
        return {
            'processed_date': datetime.now().isoformat(),
            'total_licenses': len(self.processed_licenses),
            'embeddings_data': embeddings_data,
            'summary': self._create_summary()
        }
    
    def _create_embedding_text(self, license_info: Dict) -> str:
        """Create rich text for semantic embedding"""
        parts = []
        
        # Basic info
        fit_id = license_info['fit_id']
        technology = license_info['technology']
        parts.append(f"FIT license {fit_id} for {technology.lower()} renewable energy")
        
        # Technology specifics
        tech_lower = technology.lower()
        if 'photovoltaic' in tech_lower or 'pv' in tech_lower:
            parts.append("solar photovoltaic installation")
        elif 'wind' in tech_lower:
            parts.append("wind power generation system")
        elif 'hydro' in tech_lower:
            parts.append("hydroelectric power system")
        elif 'anaerobic' in tech_lower:
            parts.append("anaerobic digestion biogas system")
        
        # Capacity and scale
        capacity_kw = license_info['capacity_kw']
        if capacity_kw > 0:
            if capacity_kw <= 4:
                parts.append(f"{capacity_kw}kW domestic micro-generation")
            elif capacity_kw <= 50:
                parts.append(f"{capacity_kw}kW small commercial installation")
            elif capacity_kw <= 250:
                parts.append(f"{capacity_kw}kW medium commercial system")
            elif capacity_kw <= 1000:
                parts.append(f"{license_info['capacity_mw']:.2f}MW large commercial facility")
            else:
                parts.append(f"{license_info['capacity_mw']:.2f}MW utility-scale facility")
        
        # Age and FIT status
        age = license_info.get('age_years', 0)
        remaining = license_info.get('remaining_fit_years', 0)
        window = license_info.get('repowering_window', '')
        
        if age > 0:
            parts.append(f"installed {age:.1f} years ago")
        
        # FIT timing context
        if remaining > 15:
            parts.append("substantial feed-in tariff period remaining")
        elif remaining > 10:
            parts.append("good feed-in tariff period remaining")
        elif remaining > 5:
            parts.append("moderate feed-in tariff period remaining")
        elif remaining > 0:
            parts.append("limited feed-in tariff remaining, PPA opportunity")
        else:
            parts.append("feed-in tariff expired, requires PPA")
        
        # Urgency
        if window == 'EXPIRED':
            parts.append("immediate PPA action required")
        elif window == 'IMMEDIATE':
            parts.append("urgent PPA transition needed")
        elif window == 'URGENT':
            parts.append("PPA planning window open")
        
        # Location
        location_parts = []
        postcode = license_info.get('postcode', '')
        region = license_info.get('region', '')
        country = license_info.get('country', '')
        
        if postcode:
            location_parts.append(f"postcode {postcode}")
        if region:
            location_parts.append(f"{region} region")
        if country:
            location_parts.append(country)
        
        if location_parts:
            parts.append("located in " + ", ".join(location_parts))
        
        # Commercial status
        status = license_info.get('commercial_status', '')
        if status:
            parts.append(f"{status.lower()} sector")
        
        return ". ".join(parts) + "."
    
    def _create_summary(self) -> Dict:
        """Create summary statistics"""
        if not self.processed_licenses:
            return {}
        
        # Technology breakdown
        tech_counts = {}
        for license in self.processed_licenses:
            tech = license['technology']
            tech_counts[tech] = tech_counts.get(tech, 0) + 1
        
        # Capacity analysis
        capacities = [l['capacity_kw'] for l in self.processed_licenses if l['capacity_kw'] > 0]
        total_capacity_kw = sum(capacities)
        
        # Age analysis
        ages = [l['age_years'] for l in self.processed_licenses if l.get('age_years', 0) > 0]
        avg_age = np.mean(ages) if ages else 0
        
        # Urgency analysis
        window_counts = {}
        for license in self.processed_licenses:
            window = license.get('repowering_window', 'Unknown')
            window_counts[window] = window_counts.get(window, 0) + 1
        
        return {
            'total_licenses': len(self.processed_licenses),
            'total_capacity_kw': total_capacity_kw,
            'total_capacity_mw': total_capacity_kw / 1000,
            'average_age_years': round(avg_age, 1),
            'technology_breakdown': tech_counts,
            'repowering_window_breakdown': window_counts,
            'valid_licenses_with_capacity': len(capacities),
            'valid_licenses_with_age': len(ages)
        }
    
    def save_processed_data(self, filename: str = None) -> str:
        """Save processed data to file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/processed_fit_licenses_{timestamp}.json'
        
        embeddings_data = self.create_embeddings_data()
        
        with open(filename, 'w') as f:
            json.dump(embeddings_data, f, indent=2, default=str)
        
        logger.info(f"Processed data saved to {filename}")
        return filename

# Main execution
if __name__ == "__main__":
    print("=" * 60)
    print("BATCH FIT LICENSE PROCESSOR")
    print("=" * 60)
    
    # Create processor
    processor = BatchFITProcessor(max_records=50000)
    
    # Process data
    start_time = time.time()
    licenses = processor.process_all_parts(records_per_part=20000)
    processing_time = time.time() - start_time
    
    print(f"\nProcessing complete!")
    print(f"Time taken: {processing_time:.1f} seconds")
    print(f"Total licenses processed: {len(licenses)}")
    
    if licenses:
        # Save processed data
        output_file = processor.save_processed_data()
        print(f"Data saved to: {output_file}")
        
        # Show summary
        summary = processor._create_summary()
        print(f"\nSummary:")
        print(f"  Total capacity: {summary['total_capacity_mw']:.1f} MW")
        print(f"  Average age: {summary['average_age_years']} years")
        print(f"  Top technologies:")
        for tech, count in sorted(summary['technology_breakdown'].items(), 
                                key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {tech}: {count} licenses")
    else:
        print("No licenses processed successfully.")