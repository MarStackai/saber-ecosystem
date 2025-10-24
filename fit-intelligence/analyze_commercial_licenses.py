#!/usr/bin/env python3
"""
Analyze the breakdown of commercial vs domestic licenses
"""

import json
import logging
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_license_breakdown():
    """Analyze commercial vs domestic breakdown"""
    try:
        # Load processed license data
        with open('data/processed_fit_licenses_20250821_072621.json', 'r') as f:
            data = json.load(f)
        
        embeddings_data = data.get('embeddings_data', [])
        logger.info(f"Total processed licenses: {len(embeddings_data)}")
        
        # Analyze installation types
        installation_types = []
        commercial_statuses = []
        size_categories = []
        technologies = []
        capacities = []
        
        for item in embeddings_data:
            metadata = item['metadata']
            
            inst_type = metadata.get('installation_type', '')
            installation_types.append(inst_type)
            
            comm_status = metadata.get('commercial_status', '')
            commercial_statuses.append(comm_status)
            
            size_cat = metadata.get('size_category', '')
            size_categories.append(size_cat)
            
            tech = metadata.get('technology', '')
            technologies.append(tech)
            
            capacity_kw = metadata.get('capacity_kw', 0)
            capacities.append(capacity_kw)
        
        # Count installation types
        installation_type_counts = Counter(installation_types)
        logger.info("\nInstallation Type Breakdown:")
        for inst_type, count in installation_type_counts.most_common():
            logger.info(f"  {inst_type}: {count:,} ({count/len(embeddings_data)*100:.1f}%)")
        
        # Count commercial statuses
        commercial_status_counts = Counter(commercial_statuses)
        logger.info("\nCommercial Status Breakdown:")
        for status, count in commercial_status_counts.most_common():
            logger.info(f"  {status}: {count:,}")
        
        # Count size categories
        size_category_counts = Counter(size_categories)
        logger.info("\nSize Category Breakdown:")
        for size, count in size_category_counts.most_common():
            logger.info(f"  {size}: {count:,}")
        
        # Filter for non-domestic only
        non_domestic = [
            item for item in embeddings_data 
            if 'Non Domestic' in item['metadata'].get('installation_type', '') or
               item['metadata'].get('commercial_status') in ['Small Commercial', 'Commercial', 'Large Commercial', 'Utility Scale']
        ]
        
        logger.info(f"\n{'='*60}")
        logger.info(f"NON-DOMESTIC LICENSES ANALYSIS")
        logger.info(f"{'='*60}")
        logger.info(f"Total Non-Domestic Licenses: {len(non_domestic):,}")
        
        # Analyze non-domestic capacities
        non_domestic_capacities = [item['metadata'].get('capacity_kw', 0) for item in non_domestic]
        total_non_domestic_capacity = sum(non_domestic_capacities)
        
        logger.info(f"Total Non-Domestic Capacity: {total_non_domestic_capacity:,.0f} kW ({total_non_domestic_capacity/1000:.1f} MW)")
        
        # Non-domestic technology breakdown
        non_domestic_technologies = [item['metadata'].get('technology', '') for item in non_domestic]
        non_domestic_tech_counts = Counter(non_domestic_technologies)
        
        logger.info(f"\nNon-Domestic Technology Breakdown:")
        for tech, count in non_domestic_tech_counts.most_common():
            tech_capacity = sum([
                item['metadata'].get('capacity_kw', 0) 
                for item in non_domestic 
                if item['metadata'].get('technology') == tech
            ])
            logger.info(f"  {tech}: {count:,} licenses ({tech_capacity/1000:.1f} MW)")
        
        # Size distribution of non-domestic
        non_domestic_sizes = [item['metadata'].get('size_category', '') for item in non_domestic]
        non_domestic_size_counts = Counter(non_domestic_sizes)
        
        logger.info(f"\nNon-Domestic Size Distribution:")
        for size, count in non_domestic_size_counts.most_common():
            logger.info(f"  {size}: {count:,}")
        
        # Commercial vs other breakdown
        domestic_count = len(embeddings_data) - len(non_domestic)
        logger.info(f"\n{'='*60}")
        logger.info(f"FINAL BREAKDOWN")
        logger.info(f"{'='*60}")
        logger.info(f"✓ Non-Domestic (Commercial): {len(non_domestic):,} licenses")
        logger.info(f"✓ Domestic/Residential: {domestic_count:,} licenses")
        logger.info(f"✓ Total Processed: {len(embeddings_data):,} licenses")
        logger.info(f"✓ Commercial Percentage: {len(non_domestic)/len(embeddings_data)*100:.1f}%")
        
        return {
            'total_licenses': len(embeddings_data),
            'non_domestic_licenses': len(non_domestic),
            'domestic_licenses': domestic_count,
            'non_domestic_capacity_mw': total_non_domestic_capacity / 1000,
            'non_domestic_technologies': dict(non_domestic_tech_counts)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing licenses: {e}")
        return {}

if __name__ == "__main__":
    print("=" * 60)
    print("FIT LICENSE COMMERCIAL ANALYSIS")
    print("=" * 60)
    
    results = analyze_license_breakdown()
    
    if results:
        print(f"\n🎯 KEY FINDINGS:")
        print(f"   Commercial licenses for analysis: {results['non_domestic_licenses']:,}")
        print(f"   Commercial capacity: {results['non_domestic_capacity_mw']:.1f} MW")
        print(f"   Focus dataset size: {results['non_domestic_licenses']:,} non-domestic installations")