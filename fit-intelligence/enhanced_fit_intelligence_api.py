#!/usr/bin/env python3
"""
Enhanced FIT Intelligence API
Integrates FIT License data with existing ChromaDB for comprehensive analysis
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import json
import logging
from typing import List, Dict, Optional
import glob
from datetime import datetime
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedFITIntelligenceAPI:
    """Enhanced API that combines license data with existing commercial data"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                is_persistent=True
            )
        )
        
        # Initialize embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Collections
        self.collections = {}
        self._load_collections()
        
        # License data cache
        self._license_data_cache = None
        self._load_license_data_cache()
    
    def _load_collections(self):
        """Load available collections"""
        try:
            # Try to load existing collections
            collection_names = [
                "commercial_fit_sites",           # Existing commercial data
                "fit_licenses_enhanced",          # New license data  
                "fit_licenses",                   # Fallback license collection
                "fit_licenses_nondomestic"        # Non-domestic licenses with ALL records
            ]
            
            for name in collection_names:
                try:
                    collection = self.client.get_collection(
                        name=name,
                        embedding_function=self.embedding_function
                    )
                    self.collections[name] = collection
                    logger.info(f"Loaded collection '{name}' with {collection.count()} documents")
                except Exception as e:
                    logger.debug(f"Collection '{name}' not found: {e}")
            
            logger.info(f"Loaded {len(self.collections)} collections")
            
        except Exception as e:
            logger.error(f"Error loading collections: {e}")
    
    def _load_license_data_cache(self):
        """Load processed license data for quick analysis"""
        try:
            # Find the most recent processed file
            pattern = 'data/processed_fit_licenses_*.json'
            files = glob.glob(pattern)
            if files:
                filename = max(files)
                with open(filename, 'r') as f:
                    self._license_data_cache = json.load(f)
                logger.info(f"Loaded license data cache from {filename}")
        except Exception as e:
            logger.debug(f"Could not load license data cache: {e}")
    
    def search_unified(self, query: str, n_results: int = 10, 
                      include_commercial: bool = True, 
                      include_licenses: bool = True,
                      filters: Dict = None) -> Dict:
        """
        Unified search across both commercial sites and licenses
        """
        try:
            results = {
                'query': query,
                'commercial_results': [],
                'license_results': [],
                'combined_insights': {}
            }
            
            # Convert query to lowercase for comparison
            query_lower = query.lower()
            
            # Search commercial sites
            if include_commercial and "commercial_fit_sites" in self.collections:
                commercial_results = self._search_collection(
                    self.collections["commercial_fit_sites"],
                    query, n_results, filters
                )
                results['commercial_results'] = commercial_results
            
            # Search license data
            license_collection = None
            if include_licenses:
                # Prioritize non-domestic collection for FIT ID searches
                import re
                if 'fit id' in query_lower or re.search(r'\b\d{6}\b', query):
                    # For FIT ID searches, prioritize non-domestic collection
                    if "fit_licenses_nondomestic" in self.collections:
                        license_collection = self.collections["fit_licenses_nondomestic"]
                    elif "fit_licenses_enhanced" in self.collections:
                        license_collection = self.collections["fit_licenses_enhanced"]
                    elif "fit_licenses" in self.collections:
                        license_collection = self.collections["fit_licenses"]
                else:
                    # For general searches, use enhanced or regular collections
                    if "fit_licenses_enhanced" in self.collections:
                        license_collection = self.collections["fit_licenses_enhanced"]
                    elif "fit_licenses_nondomestic" in self.collections:
                        license_collection = self.collections["fit_licenses_nondomestic"]
                    elif "fit_licenses" in self.collections:
                        license_collection = self.collections["fit_licenses"]
            
            if license_collection:
                license_results = self._search_collection(
                    license_collection, query, n_results, filters
                )
                results['license_results'] = license_results
            
            # Generate combined insights
            results['combined_insights'] = self._generate_combined_insights(
                results['commercial_results'], 
                results['license_results']
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Unified search error: {e}")
            return {
                'error': str(e),
                'commercial_results': [],
                'license_results': [],
                'combined_insights': {}
            }
    
    def _search_collection(self, collection, query: str, n_results: int, filters: Dict = None) -> List[Dict]:
        """Search a specific collection"""
        try:
            # Build where clause from filters using $and operator for multiple conditions
            where_clause = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    if key == 'min_capacity_kw':
                        conditions.append({"capacity_kw": {"$gte": value}})
                    elif key == 'max_capacity_kw':
                        conditions.append({"capacity_kw": {"$lte": value}})
                    elif key == 'min_capacity_mw':
                        conditions.append({"capacity_mw": {"$gte": value}})
                    elif key == 'max_capacity_mw':
                        conditions.append({"capacity_mw": {"$lte": value}})
                    elif key == 'technology':
                        conditions.append({"technology": value})  # Direct equality for strings
                    elif key == 'repowering_window':
                        conditions.append({"repowering_window": value})
                    elif key == 'country':
                        conditions.append({"country": value})
                    elif key == 'postcode_yorkshire':
                        # Handle Yorkshire postcode filtering in post-processing
                        # Skip adding this as a filter
                        pass
                
                # Use $and operator for multiple conditions, single condition directly
                if len(conditions) > 1:
                    where_clause = {"$and": conditions}
                elif len(conditions) == 1:
                    where_clause = conditions[0]
            
            # Perform search
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause if where_clause else None,
                include=['metadatas', 'documents', 'distances']
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    'id': results['ids'][0][i],
                    'score': 1 - results['distances'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'description': results['documents'][0][i]
                }
                formatted_results.append(result)
            
            # Apply post-processing filters that Chroma doesn't support
            if filters and 'postcode_yorkshire' in filters:
                yorkshire_postcodes = ['YO', 'HU', 'LS', 'BD', 'HX', 'HD', 'WF', 'S1', 'DN', 'NG']  # Yorkshire postcodes
                formatted_results = [
                    result for result in formatted_results
                    if any(result['metadata'].get('postcode', '').startswith(prefix) 
                          for prefix in yorkshire_postcodes)
                ]
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Collection search error: {e}")
            return []
    
    def _generate_combined_insights(self, commercial_results: List[Dict], license_results: List[Dict]) -> Dict:
        """Generate insights combining both result sets"""
        insights = {
            'total_results': len(commercial_results) + len(license_results),
            'commercial_count': len(commercial_results),
            'license_count': len(license_results),
            'data_coverage': {}
        }
        
        try:
            # Analyze commercial data
            if commercial_results:
                commercial_capacity = sum(
                    float(r['metadata'].get('capacity_mw', 0)) 
                    for r in commercial_results
                )
                insights['commercial_total_capacity_mw'] = round(commercial_capacity, 1)
                
                commercial_urgent = sum(
                    1 for r in commercial_results 
                    if r['metadata'].get('repowering_window') in ['IMMEDIATE', 'URGENT']
                )
                insights['commercial_urgent_opportunities'] = commercial_urgent
            
            # Analyze license data
            if license_results:
                license_capacity = sum(
                    float(r['metadata'].get('capacity_kw', 0)) / 1000
                    for r in license_results
                )
                insights['license_total_capacity_mw'] = round(license_capacity, 1)
                
                license_urgent = sum(
                    1 for r in license_results
                    if r['metadata'].get('repowering_window') in ['IMMEDIATE', 'URGENT', 'EXPIRED']
                )
                insights['license_urgent_opportunities'] = license_urgent
            
            # Technology breakdown
            all_results = commercial_results + license_results
            tech_counts = {}
            for result in all_results:
                tech = result['metadata'].get('technology', 'Unknown')
                tech_counts[tech] = tech_counts.get(tech, 0) + 1
            
            insights['technology_breakdown'] = dict(
                sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)
            )
            
            # Data coverage assessment
            insights['data_coverage'] = {
                'has_commercial_data': len(commercial_results) > 0,
                'has_license_data': len(license_results) > 0,
                'complementary_coverage': len(commercial_results) > 0 and len(license_results) > 0
            }
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            insights['error'] = str(e)
        
        return insights
    
    def get_comprehensive_insights(self, technology: str = None) -> Dict:
        """Get comprehensive insights across all data sources"""
        try:
            insights = {
                'technology_filter': technology,
                'commercial_insights': {},
                'license_insights': {},
                'combined_analysis': {}
            }
            
            # Commercial insights
            if "commercial_fit_sites" in self.collections:
                insights['commercial_insights'] = self._get_collection_insights(
                    self.collections["commercial_fit_sites"], technology, 'commercial'
                )
            
            # License insights
            license_collection = self.collections.get("fit_licenses_enhanced") or \
                               self.collections.get("fit_licenses")
            
            if license_collection:
                insights['license_insights'] = self._get_collection_insights(
                    license_collection, technology, 'license'
                )
            
            # Combined analysis
            insights['combined_analysis'] = self._analyze_combined_data(
                insights['commercial_insights'],
                insights['license_insights']
            )
            
            return insights
            
        except Exception as e:
            logger.error(f"Comprehensive insights error: {e}")
            return {'error': str(e)}
    
    def _get_collection_insights(self, collection, technology: str, data_type: str) -> Dict:
        """Get insights from a specific collection"""
        try:
            # Get data with optional technology filter
            if technology:
                results = collection.get(
                    where={"technology": {"$eq": technology}},
                    include=['metadatas']
                )
            else:
                # Limit to avoid memory issues
                results = collection.get(
                    include=['metadatas'],
                    limit=10000
                )
            
            metadatas = results['metadatas']
            
            if not metadatas:
                return {"error": "No data found"}
            
            # Calculate insights
            total_count = len(metadatas)
            
            # Capacity analysis
            if data_type == 'commercial':
                capacities = [float(m.get('capacity_mw', 0)) for m in metadatas]
                capacity_unit = 'MW'
            else:  # license
                capacities = [float(m.get('capacity_kw', 0)) for m in metadatas]
                capacity_unit = 'kW'
            
            total_capacity = sum(c for c in capacities if c > 0)
            avg_capacity = np.mean(capacities) if capacities else 0
            
            # Age analysis
            ages = [float(m.get('age_years', 0)) for m in metadatas if m.get('age_years')]
            avg_age = np.mean(ages) if ages else 0
            
            # FIT remaining analysis
            remaining_fits = [float(m.get('remaining_fit_years', 0)) for m in metadatas if m.get('remaining_fit_years')]
            avg_remaining = np.mean(remaining_fits) if remaining_fits else 0
            
            # Urgency analysis
            urgency_counts = {}
            for m in metadatas:
                window = m.get('repowering_window', 'Unknown')
                urgency_counts[window] = urgency_counts.get(window, 0) + 1
            
            # Technology breakdown
            tech_counts = {}
            for m in metadatas:
                tech = m.get('technology', 'Unknown')
                tech_counts[tech] = tech_counts.get(tech, 0) + 1
            
            return {
                'data_type': data_type,
                'total_count': total_count,
                'total_capacity': round(total_capacity, 1),
                'capacity_unit': capacity_unit,
                'average_capacity': round(avg_capacity, 1),
                'average_age_years': round(avg_age, 1),
                'average_remaining_fit_years': round(avg_remaining, 1),
                'urgency_breakdown': urgency_counts,
                'technology_breakdown': dict(
                    sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                ),
                'records_with_capacity': len([c for c in capacities if c > 0]),
                'records_with_age': len(ages)
            }
            
        except Exception as e:
            logger.error(f"Collection insights error: {e}")
            return {'error': str(e)}
    
    def _analyze_combined_data(self, commercial_insights: Dict, license_insights: Dict) -> Dict:
        """Analyze the relationship between commercial and license data"""
        try:
            analysis = {}
            
            # Data availability
            analysis['data_sources'] = {
                'commercial_available': 'error' not in commercial_insights,
                'license_available': 'error' not in license_insights,
                'both_available': 'error' not in commercial_insights and 'error' not in license_insights
            }
            
            if analysis['data_sources']['both_available']:
                # Scale comparison
                comm_total = commercial_insights.get('total_capacity', 0)
                license_total = license_insights.get('total_capacity', 0) / 1000  # Convert kW to MW
                
                analysis['capacity_comparison'] = {
                    'commercial_mw': comm_total,
                    'license_mw': round(license_total, 1),
                    'total_combined_mw': round(comm_total + license_total, 1)
                }
                
                # Technology overlap
                comm_techs = set(commercial_insights.get('technology_breakdown', {}).keys())
                license_techs = set(license_insights.get('technology_breakdown', {}).keys())
                
                analysis['technology_overlap'] = {
                    'common_technologies': list(comm_techs & license_techs),
                    'commercial_only': list(comm_techs - license_techs),
                    'license_only': list(license_techs - comm_techs),
                    'overlap_percentage': len(comm_techs & license_techs) / len(comm_techs | license_techs) * 100 if comm_techs | license_techs else 0
                }
                
                # Urgency comparison
                comm_urgent = sum(
                    v for k, v in commercial_insights.get('urgency_breakdown', {}).items() 
                    if k in ['IMMEDIATE', 'URGENT', 'EXPIRED']
                )
                license_urgent = sum(
                    v for k, v in license_insights.get('urgency_breakdown', {}).items() 
                    if k in ['IMMEDIATE', 'URGENT', 'EXPIRED']
                )
                
                analysis['urgency_comparison'] = {
                    'commercial_urgent': comm_urgent,
                    'license_urgent': license_urgent,
                    'total_urgent_opportunities': comm_urgent + license_urgent
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Combined analysis error: {e}")
            return {'error': str(e)}
    
    def natural_language_query(self, query: str, max_results: int = 50) -> Dict:
        """Process natural language queries across all data sources"""
        try:
            # Determine search strategy based on query
            include_commercial = True
            include_licenses = True
            
            # Parse query for data source hints
            query_lower = query.lower()
            if 'license' in query_lower or 'fit id' in query_lower:
                include_commercial = False
            elif 'commercial' in query_lower or 'site' in query_lower:
                include_licenses = False
            
            # Extract filters
            filters = self._parse_nl_filters(query)
            
            # Perform unified search
            results = self.search_unified(
                query=query,
                n_results=max_results,
                include_commercial=include_commercial,
                include_licenses=include_licenses,
                filters=filters
            )
            
            # Enhance with summary
            results['query_analysis'] = {
                'original_query': query,
                'search_strategy': {
                    'included_commercial': include_commercial,
                    'included_licenses': include_licenses
                },
                'applied_filters': filters,
                'total_results': results['combined_insights'].get('total_results', 0)
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Natural language query error: {e}")
            return {'error': str(e)}
    
    def _parse_nl_filters(self, query: str) -> Dict:
        """Parse natural language query for filters"""
        filters = {}
        query_lower = query.lower()
        
        # Technology filters
        if 'solar' in query_lower or 'photovoltaic' in query_lower or 'pv' in query_lower:
            filters['technology'] = 'Photovoltaic'
        elif 'wind' in query_lower:
            filters['technology'] = 'Wind'
        elif 'hydro' in query_lower:
            filters['technology'] = 'Hydro'
        elif 'anaerobic' in query_lower or 'biogas' in query_lower:
            filters['technology'] = 'Anaerobic digestion'
        
        # Urgency filters
        if 'urgent' in query_lower or 'immediate' in query_lower:
            filters['repowering_window'] = 'IMMEDIATE'
        elif 'expir' in query_lower:
            filters['repowering_window'] = 'EXPIRED'
        
        # Enhanced capacity filters with range support
        if 'over 1mw' in query_lower or '>1mw' in query_lower:
            filters['min_capacity_kw'] = 1000
        elif 'over 500kw' in query_lower or '>500kw' in query_lower:
            filters['min_capacity_kw'] = 500
        elif 'over 250kw' in query_lower or '>250kw' in query_lower:
            filters['min_capacity_kw'] = 250
        elif 'over 100kw' in query_lower or '>100kw' in query_lower:
            filters['min_capacity_kw'] = 100
        
        # Parse capacity ranges (e.g., "between 250 and 500kw")
        import re
        capacity_range = re.search(r'between\s+(\d+)\s+and\s+(\d+)\s*kw', query_lower)
        if capacity_range:
            min_capacity_kw = int(capacity_range.group(1))
            max_capacity_kw = int(capacity_range.group(2))
            # Convert kW to MW for commercial data comparison
            filters['min_capacity_mw'] = min_capacity_kw / 1000
            filters['max_capacity_mw'] = max_capacity_kw / 1000
            # Also keep kW for license data
            filters['min_capacity_kw'] = min_capacity_kw
            filters['max_capacity_kw'] = max_capacity_kw
        
        # Enhanced location filters
        if 'scotland' in query_lower:
            filters['country'] = 'Scotland'
        elif 'wales' in query_lower:
            filters['country'] = 'Wales'
        elif 'england' in query_lower:
            filters['country'] = 'England'
        elif 'beverly' in query_lower or 'beverley' in query_lower:
            # Beverly/Beverley is in East Riding of Yorkshire - use Yorkshire postcodes
            # Common Yorkshire postcodes: YO (York), HU (Hull), LS (Leeds), etc.
            filters['postcode_yorkshire'] = True
        
        return filters
    
    def get_system_status(self) -> Dict:
        """Get current system status and capabilities"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'collections': {},
            'capabilities': {},
            'data_summary': {}
        }
        
        # Collection status
        for name, collection in self.collections.items():
            try:
                count = collection.count()
                status['collections'][name] = {
                    'document_count': count,
                    'status': 'ready'
                }
            except Exception as e:
                status['collections'][name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Capabilities
        status['capabilities'] = {
            'unified_search': len(self.collections) > 0,
            'commercial_data': 'commercial_fit_sites' in self.collections,
            'license_data': any(name.startswith('fit_licenses') for name in self.collections),
            'natural_language_queries': True,
            'comprehensive_insights': True
        }
        
        # Data summary
        if self._license_data_cache:
            status['data_summary'] = self._license_data_cache.get('summary', {})
        
        return status

# Create Flask API
app = Flask(__name__)
enhanced_api = None

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    global enhanced_api
    if not enhanced_api:
        enhanced_api = EnhancedFITIntelligenceAPI()
    
    return jsonify(enhanced_api.get_system_status())

@app.route('/api/search', methods=['POST'])
def api_search():
    """Unified search endpoint"""
    global enhanced_api
    if not enhanced_api:
        enhanced_api = EnhancedFITIntelligenceAPI()
    
    data = request.get_json()
    query = data.get('query', '')
    max_results = data.get('max_results', 10)
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    results = enhanced_api.natural_language_query(query, max_results)
    return jsonify(results)

@app.route('/api/insights')
def api_insights():
    """Comprehensive insights endpoint"""
    global enhanced_api
    if not enhanced_api:
        enhanced_api = EnhancedFITIntelligenceAPI()
    
    technology = request.args.get('technology')
    insights = enhanced_api.get_comprehensive_insights(technology)
    return jsonify(insights)

# Test function
def test_enhanced_api():
    """Test the enhanced API functionality"""
    print("=" * 60)
    print("ENHANCED FIT INTELLIGENCE API TEST")
    print("=" * 60)
    
    # Initialize API
    api = EnhancedFITIntelligenceAPI()
    
    # Test system status
    print("\n1. System Status:")
    status = api.get_system_status()
    print(f"Collections loaded: {len(status['collections'])}")
    for name, info in status['collections'].items():
        if 'document_count' in info:
            print(f"  ✓ {name}: {info['document_count']} documents")
        else:
            print(f"  ✗ {name}: {info.get('error', 'unknown error')}")
    
    # Test natural language query
    print("\n2. Testing Natural Language Query:")
    test_query = "large solar installations with expiring FIT tariffs"
    results = api.natural_language_query(test_query, max_results=5)
    
    if 'error' not in results:
        insights = results['combined_insights']
        print(f"Query: '{test_query}'")
        print(f"Total results: {insights.get('total_results', 0)}")
        print(f"Commercial results: {insights.get('commercial_count', 0)}")
        print(f"License results: {insights.get('license_count', 0)}")
        
        # Show sample results
        for result_type in ['commercial_results', 'license_results']:
            results_list = results.get(result_type, [])
            if results_list:
                print(f"\nSample {result_type}:")
                for i, result in enumerate(results_list[:2]):
                    metadata = result['metadata']
                    capacity = metadata.get('capacity_mw', metadata.get('capacity_kw', 0))
                    unit = 'MW' if 'capacity_mw' in metadata else 'kW'
                    print(f"  {i+1}. {metadata.get('technology', 'Unknown')} "
                          f"{capacity}{unit} ({metadata.get('repowering_window', 'Unknown')})")
    else:
        print(f"Query failed: {results['error']}")
    
    # Test comprehensive insights
    print("\n3. Testing Comprehensive Insights:")
    insights = api.get_comprehensive_insights('Photovoltaic')
    
    if 'error' not in insights:
        print("Solar PV insights:")
        
        comm_insights = insights.get('commercial_insights', {})
        if 'error' not in comm_insights:
            print(f"  Commercial: {comm_insights.get('total_count', 0)} sites, "
                  f"{comm_insights.get('total_capacity', 0)} MW")
        
        license_insights = insights.get('license_insights', {})
        if 'error' not in license_insights:
            print(f"  Licenses: {license_insights.get('total_count', 0)} licenses, "
                  f"{license_insights.get('total_capacity', 0)} kW")
        
        combined = insights.get('combined_analysis', {})
        if combined.get('data_sources', {}).get('both_available'):
            capacity_comp = combined.get('capacity_comparison', {})
            print(f"  Combined capacity: {capacity_comp.get('total_combined_mw', 0)} MW")
    
    print(f"\n{'='*60}")
    print("ENHANCED API TEST COMPLETE!")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_enhanced_api()