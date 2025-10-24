#!/usr/bin/env python3
"""
Comprehensive FIT Data Analyzer
Analyzes all 75,194 records to extract patterns for advanced training
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Any
import chromadb
from datetime import datetime
import re
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveFITAnalyzer:
    def __init__(self):
        """Initialize analyzer with all data sources"""
        self.data_dir = Path("data")
        self.chroma_client = chromadb.PersistentClient(path="chroma_db")
        self.patterns = defaultdict(set)
        self.statistics = {}
        self.business_insights = []
        
    def load_all_data(self) -> Dict[str, Any]:
        """Load all 75,194 FIT records from various sources"""
        logger.info("Loading comprehensive FIT database...")
        
        all_data = {
            'commercial_sites': [],
            'fit_licenses': [],
            'raw_records': [],
            'chroma_collections': {}
        }
        
        # Load JSON data files
        json_files = [
            "all_commercial_fit.json",
            "commercial_sites_enhanced_with_fit.json"
        ]
        
        for json_file in json_files:
            file_path = self.data_dir / json_file
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if 'sites' in data:
                        all_data['commercial_sites'].extend(data['sites'])
                    logger.info(f"Loaded {len(data.get('sites', []))} sites from {json_file}")
        
        # Load CSV data
        csv_file = self.data_dir / "commercial_solar_fit.csv"
        if csv_file.exists():
            df = pd.read_csv(csv_file)
            all_data['raw_records'] = df.to_dict('records')
            logger.info(f"Loaded {len(df)} records from CSV")
        
        # Load ChromaDB collections
        for collection_name in self.chroma_client.list_collections():
            collection = self.chroma_client.get_collection(collection_name.name)
            all_data['chroma_collections'][collection_name.name] = collection.count()
            logger.info(f"ChromaDB collection '{collection_name.name}': {collection.count()} documents")
        
        return all_data
    
    def extract_technology_patterns(self, data: Dict[str, Any]) -> Dict[str, Set]:
        """Extract all technology variations and synonyms"""
        logger.info("Extracting technology patterns...")
        
        tech_patterns = defaultdict(set)
        tech_variations = defaultdict(list)
        
        for site in data['commercial_sites']:
            tech = site.get('technology', '').lower().strip()
            if tech:
                # Base technology
                base_tech = self._normalize_technology(tech)
                tech_patterns[base_tech].add(tech)
                
                # Capacity ranges for each technology
                capacity = site.get('capacity_kw', 0)
                if capacity > 0:
                    tech_variations[base_tech].append(capacity)
        
        # Calculate statistics for each technology
        for tech, capacities in tech_variations.items():
            if capacities:
                self.patterns[f'tech_{tech}_stats'] = {
                    'count': len(capacities),
                    'min_capacity': min(capacities),
                    'max_capacity': max(capacities),
                    'mean_capacity': np.mean(capacities),
                    'std_capacity': np.std(capacities),
                    'percentiles': {
                        25: np.percentile(capacities, 25),
                        50: np.percentile(capacities, 50),
                        75: np.percentile(capacities, 75),
                        95: np.percentile(capacities, 95)
                    }
                }
        
        return tech_patterns
    
    def extract_geographic_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all location patterns and relationships"""
        logger.info("Extracting geographic patterns...")
        
        geo_patterns = {
            'postcodes': defaultdict(list),
            'regions': defaultdict(list),
            'local_authorities': defaultdict(list),
            'countries': defaultdict(list),
            'geographic_clusters': []
        }
        
        for site in data['commercial_sites']:
            postcode = site.get('postcode', '').strip()
            region = site.get('region', '').strip()
            la = site.get('local_authority', '').strip()
            country = site.get('country', '').strip()
            
            if postcode:
                # Extract postcode area (first part)
                postcode_area = postcode.split()[0] if ' ' in postcode else postcode[:3]
                geo_patterns['postcodes'][postcode_area].append({
                    'capacity': site.get('capacity_kw', 0),
                    'technology': site.get('technology', ''),
                    'commission_date': site.get('commission_date', '')
                })
            
            if region:
                geo_patterns['regions'][region].append(site.get('capacity_kw', 0))
            if la:
                geo_patterns['local_authorities'][la].append(site.get('capacity_kw', 0))
            if country:
                geo_patterns['countries'][country].append(site.get('capacity_kw', 0))
        
        # Identify geographic clusters
        for area, sites in geo_patterns['postcodes'].items():
            if len(sites) > 10:  # Significant cluster
                total_capacity = sum(s['capacity'] for s in sites)
                tech_distribution = Counter(s['technology'] for s in sites)
                
                geo_patterns['geographic_clusters'].append({
                    'area': area,
                    'site_count': len(sites),
                    'total_capacity_mw': total_capacity / 1000,
                    'dominant_technology': tech_distribution.most_common(1)[0][0] if tech_distribution else 'Unknown',
                    'technology_mix': dict(tech_distribution)
                })
        
        return geo_patterns
    
    def extract_temporal_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract temporal patterns and trends"""
        logger.info("Extracting temporal patterns...")
        
        temporal_patterns = {
            'yearly_installations': defaultdict(list),
            'fit_period_analysis': {},
            'seasonal_patterns': defaultdict(list),
            'growth_trends': {}
        }
        
        for site in data['commercial_sites']:
            commission_date = site.get('commission_date', '')
            if commission_date:
                try:
                    date = pd.to_datetime(commission_date)
                    year = date.year
                    month = date.month
                    quarter = f"Q{(month-1)//3 + 1}"
                    
                    temporal_patterns['yearly_installations'][year].append({
                        'capacity': site.get('capacity_kw', 0),
                        'technology': site.get('technology', ''),
                        'fit_rate': site.get('tariff_p_kwh', 0)
                    })
                    
                    temporal_patterns['seasonal_patterns'][quarter].append(site.get('capacity_kw', 0))
                    
                except:
                    pass
        
        # Calculate growth trends
        years = sorted(temporal_patterns['yearly_installations'].keys())
        if len(years) > 1:
            yearly_capacities = [
                sum(s['capacity'] for s in temporal_patterns['yearly_installations'][year])
                for year in years
            ]
            
            temporal_patterns['growth_trends'] = {
                'peak_year': years[yearly_capacities.index(max(yearly_capacities))],
                'total_growth_rate': (yearly_capacities[-1] - yearly_capacities[0]) / yearly_capacities[0] if yearly_capacities[0] > 0 else 0,
                'year_over_year_growth': [
                    (yearly_capacities[i] - yearly_capacities[i-1]) / yearly_capacities[i-1] if yearly_capacities[i-1] > 0 else 0
                    for i in range(1, len(yearly_capacities))
                ]
            }
        
        return temporal_patterns
    
    def extract_business_patterns(self, data: Dict[str, Any]) -> List[Dict]:
        """Extract business intelligence patterns"""
        logger.info("Extracting business patterns...")
        
        business_patterns = []
        
        # Repowering opportunities
        old_sites = [s for s in data['commercial_sites'] 
                     if s.get('age_years', 0) > 15]
        
        if old_sites:
            total_repowering_capacity = sum(s.get('capacity_kw', 0) for s in old_sites)
            business_patterns.append({
                'pattern': 'repowering_opportunity',
                'sites_count': len(old_sites),
                'total_capacity_mw': total_repowering_capacity / 1000,
                'average_age': np.mean([s.get('age_years', 0) for s in old_sites]),
                'technologies': Counter(s.get('technology', '') for s in old_sites)
            })
        
        # High FIT rate sites
        high_fit_sites = [s for s in data['commercial_sites']
                         if s.get('tariff_p_kwh', 0) > 20]
        
        if high_fit_sites:
            business_patterns.append({
                'pattern': 'high_fit_value',
                'sites_count': len(high_fit_sites),
                'total_capacity_mw': sum(s.get('capacity_kw', 0) for s in high_fit_sites) / 1000,
                'average_fit_rate': np.mean([s.get('tariff_p_kwh', 0) for s in high_fit_sites]),
                'expiry_timeline': Counter(s.get('remaining_fit_years', 0) for s in high_fit_sites)
            })
        
        # Large installation clusters
        for region, capacities in self.patterns.get('regions', {}).items():
            if len(capacities) > 50 and sum(capacities) > 10000:  # 10MW+
                business_patterns.append({
                    'pattern': 'regional_cluster',
                    'region': region,
                    'sites_count': len(capacities),
                    'total_capacity_mw': sum(capacities) / 1000,
                    'average_size_kw': np.mean(capacities),
                    'potential': 'High density area for grid services'
                })
        
        return business_patterns
    
    def identify_data_quality_issues(self, data: Dict[str, Any]) -> Dict[str, List]:
        """Identify data quality issues and edge cases"""
        logger.info("Identifying data quality issues...")
        
        issues = {
            'missing_data': [],
            'anomalies': [],
            'inconsistencies': [],
            'edge_cases': []
        }
        
        for i, site in enumerate(data['commercial_sites']):
            # Missing critical fields
            critical_fields = ['technology', 'capacity_kw', 'postcode', 'commission_date']
            missing = [f for f in critical_fields if not site.get(f)]
            if missing:
                issues['missing_data'].append({
                    'record_id': i,
                    'missing_fields': missing
                })
            
            # Anomalies
            capacity = site.get('capacity_kw', 0)
            if capacity < 0 or capacity > 100000:  # Over 100MW is unusual
                issues['anomalies'].append({
                    'record_id': i,
                    'field': 'capacity_kw',
                    'value': capacity,
                    'reason': 'Unusual capacity value'
                })
            
            # Edge cases
            if capacity > 0 and capacity < 1:  # Sub-1kW installations
                issues['edge_cases'].append({
                    'record_id': i,
                    'type': 'micro_installation',
                    'capacity': capacity
                })
        
        return issues
    
    def generate_training_scenarios(self) -> List[Dict]:
        """Generate diverse training scenarios from patterns"""
        logger.info("Generating training scenarios...")
        
        scenarios = []
        
        # Geographic queries
        for area, sites in list(self.patterns.get('postcodes', {}).items())[:50]:
            scenarios.append({
                'query_type': 'geographic',
                'query': f"solar installations in {area}",
                'expected_results': len(sites),
                'filters': {'postcode_area': area, 'technology': 'solar'}
            })
        
        # Capacity range queries
        for tech, stats in self.patterns.items():
            if tech.startswith('tech_') and isinstance(stats, dict):
                tech_name = tech.replace('tech_', '').replace('_stats', '')
                scenarios.append({
                    'query_type': 'capacity_range',
                    'query': f"{tech_name} sites over {stats.get('percentiles', {}).get(75, 100)}kW",
                    'expected_results': stats['count'] * 0.25,  # Top 25%
                    'filters': {'technology': tech_name, 'min_capacity': stats.get('percentiles', {}).get(75, 100)}
                })
        
        # Temporal queries
        for year, sites in list(self.patterns.get('yearly_installations', {}).items())[:10]:
            scenarios.append({
                'query_type': 'temporal',
                'query': f"installations commissioned in {year}",
                'expected_results': len(sites),
                'filters': {'commission_year': year}
            })
        
        # Business intelligence queries
        scenarios.extend([
            {
                'query_type': 'business_intelligence',
                'query': "sites ready for repowering",
                'filters': {'age_years': {'$gt': 15}},
                'intent': 'identify_opportunities'
            },
            {
                'query_type': 'comparative',
                'query': "compare solar vs wind capacity in Scotland",
                'filters': {'country': 'Scotland'},
                'intent': 'technology_comparison'
            },
            {
                'query_type': 'analytical',
                'query': "highest FIT rate sites expiring next year",
                'filters': {'remaining_fit_years': {'$lte': 1}},
                'sort': 'tariff_p_kwh',
                'intent': 'urgent_opportunities'
            }
        ])
        
        return scenarios
    
    def _normalize_technology(self, tech: str) -> str:
        """Normalize technology names"""
        tech_lower = tech.lower()
        
        if 'solar' in tech_lower or 'pv' in tech_lower or 'photovoltaic' in tech_lower:
            return 'solar'
        elif 'wind' in tech_lower:
            return 'wind'
        elif 'hydro' in tech_lower:
            return 'hydro'
        elif 'anaerobic' in tech_lower or 'ad' in tech_lower or 'digestion' in tech_lower:
            return 'anaerobic_digestion'
        elif 'chp' in tech_lower or 'combined heat' in tech_lower:
            return 'chp'
        else:
            return 'other'
    
    def save_analysis_results(self):
        """Save all analysis results"""
        logger.info("Saving analysis results...")
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.statistics,
            'patterns': {k: list(v) if isinstance(v, set) else v 
                        for k, v in self.patterns.items()},
            'business_insights': self.business_insights,
            'training_scenarios': self.training_scenarios
        }
        
        output_file = Path('comprehensive_fit_analysis.json')
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        logger.info(f"Analysis saved to {output_file}")
        
        # Generate summary report
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate human-readable summary report"""
        report = []
        report.append("=" * 60)
        report.append("COMPREHENSIVE FIT DATA ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append("📊 DATABASE STATISTICS")
        report.append("-" * 40)
        for key, value in self.statistics.items():
            report.append(f"  {key}: {value}")
        report.append("")
        
        report.append("🔍 KEY PATTERNS DISCOVERED")
        report.append("-" * 40)
        pattern_count = sum(1 for k in self.patterns.keys())
        report.append(f"  Total unique patterns: {pattern_count}")
        report.append("")
        
        report.append("💡 BUSINESS INSIGHTS")
        report.append("-" * 40)
        for insight in self.business_insights[:5]:
            report.append(f"  • {insight.get('pattern', 'Unknown')}: {insight.get('sites_count', 0)} sites")
        report.append("")
        
        report.append("🎯 TRAINING OPPORTUNITIES")
        report.append("-" * 40)
        report.append(f"  Generated scenarios: {len(self.training_scenarios)}")
        report.append(f"  Query types covered: {len(set(s['query_type'] for s in self.training_scenarios))}")
        report.append("")
        
        report_text = "\n".join(report)
        
        with open('analysis_report.txt', 'w') as f:
            f.write(report_text)
        
        print(report_text)
    
    def run_comprehensive_analysis(self):
        """Run the complete analysis pipeline"""
        logger.info("Starting comprehensive FIT data analysis...")
        
        # Load all data
        data = self.load_all_data()
        
        # Calculate basic statistics
        self.statistics = {
            'total_sites': len(data['commercial_sites']),
            'unique_technologies': len(set(s.get('technology', '') for s in data['commercial_sites'])),
            'total_capacity_gw': sum(s.get('capacity_kw', 0) for s in data['commercial_sites']) / 1_000_000,
            'chroma_collections': len(data['chroma_collections']),
            'chroma_documents': sum(data['chroma_collections'].values())
        }
        
        # Extract patterns
        tech_patterns = self.extract_technology_patterns(data)
        geo_patterns = self.extract_geographic_patterns(data)
        temporal_patterns = self.extract_temporal_patterns(data)
        self.business_insights = self.extract_business_patterns(data)
        
        # Identify issues
        data_issues = self.identify_data_quality_issues(data)
        
        # Generate training scenarios
        self.training_scenarios = self.generate_training_scenarios()
        
        # Save results
        self.save_analysis_results()
        
        logger.info("Comprehensive analysis complete!")
        
        return {
            'statistics': self.statistics,
            'pattern_count': len(self.patterns),
            'business_insights_count': len(self.business_insights),
            'training_scenarios_count': len(self.training_scenarios),
            'data_quality_issues': len(data_issues['missing_data']) + len(data_issues['anomalies'])
        }

def main():
    """Run the comprehensive data analysis"""
    analyzer = ComprehensiveFITAnalyzer()
    results = analyzer.run_comprehensive_analysis()
    
    print("\n🎉 Analysis Complete!")
    print(f"  • Analyzed {results['statistics']['total_sites']} sites")
    print(f"  • Discovered {results['pattern_count']} unique patterns")
    print(f"  • Generated {results['training_scenarios_count']} training scenarios")
    print(f"  • Identified {results['business_insights_count']} business insights")
    
    print("\nNext steps:")
    print("1. Review comprehensive_fit_analysis.json for detailed patterns")
    print("2. Use patterns to generate advanced training data")
    print("3. Implement multi-model ensemble based on discovered patterns")

if __name__ == "__main__":
    main()