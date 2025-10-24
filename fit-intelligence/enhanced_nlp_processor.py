#!/usr/bin/env python3
"""
Enhanced Natural Language Processor for FIT Intelligence
Handles ANY query type with full detail extraction and intelligent responses
No limitations on query complexity or response size
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import chromadb
from chromadb.utils import embedding_functions
import pandas as pd
from collections import defaultdict

# Import conversation context
try:
    from conversation_context import enhance_query_with_context
    CONTEXT_AVAILABLE = True
except ImportError:
    CONTEXT_AVAILABLE = False
    logger.warning("Conversation context not available")

# Try to import Ollama parser
try:
    from ollama_query_parser import OllamaQueryParser
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Ollama query parser not available")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QueryIntent:
    """Comprehensive query intent analysis"""
    query_type: str  # search, aggregate, compare, analyze, export, etc.
    entities: Dict[str, Any]  # Extracted entities
    filters: Dict[str, Any]  # All filter conditions
    aggregations: List[str]  # Requested aggregations
    output_format: str  # list, summary, csv, json, table, etc.
    sort_by: Optional[str] = None
    limit: Optional[int] = None
    include_fields: List[str] = None
    geographic_scope: Optional[Dict] = None
    time_scope: Optional[Dict] = None
    comparison_type: Optional[str] = None


class EnhancedNLPProcessor:
    """Advanced NLP processor for unlimited query understanding"""
    
    def __init__(self, chroma_client=None, collection=None):
        """Initialize with ChromaDB connection"""
        if chroma_client and collection:
            self.client = chroma_client
            self.collection = collection
        else:
            self.client = chromadb.PersistentClient(path='./chroma_db')
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            self.collection = self.client.get_collection(
                name="fit_licenses_nondomestic",
                embedding_function=self.embedding_function
            )
        
        logger.info(f"Enhanced NLP Processor initialized with {self.collection.count()} records")
        
        # Initialize UK geographic data
        from uk_geographic_search import UKGeographicSearch
        self.geo_search = UKGeographicSearch(self.client, self.collection)
        
        # Initialize Ollama parser if available
        self.ollama_parser = None
        if OLLAMA_AVAILABLE:
            try:
                self.ollama_parser = OllamaQueryParser()
                if self.ollama_parser.available:
                    logger.info("✅ Ollama query parser initialized")
                else:
                    self.ollama_parser = None
            except Exception as e:
                logger.warning(f"Could not initialize Ollama parser: {e}")
                self.ollama_parser = None
    
    def process_query(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process ANY natural language query and return comprehensive results
        No limitations on complexity or response size
        Now with conversation context support for follow-up queries
        """
        # Analyze query intent
        intent = self._analyze_intent(query, session_id)
        
        # Execute based on intent
        if intent.query_type == 'aggregate':
            return self._handle_aggregation(intent)
        elif intent.query_type == 'compare':
            return self._handle_comparison(intent)
        elif intent.query_type == 'analyze':
            return self._handle_analysis(intent)
        elif intent.query_type == 'export':
            return self._handle_export(intent)
        elif intent.query_type == 'geographic':
            return self._handle_geographic(intent)
        elif intent.query_type == 'trend':
            return self._handle_trend_analysis(intent)
        elif intent.query_type == 'opportunity':
            return self._handle_opportunity_search(intent)
        else:
            return self._handle_search(intent)
    
    def _analyze_intent(self, query: str, session_id: Optional[str] = None) -> QueryIntent:
        """
        Comprehensive intent analysis with entity extraction
        Now with conversation context support
        """
        query_lower = query.lower()
        
        # Initialize intent
        intent = QueryIntent(
            query_type='search',
            entities={},
            filters={},
            aggregations=[],
            output_format='detailed_list',
            include_fields=[]
        )
        
        # Detect query type
        if any(word in query_lower for word in ['how many', 'count', 'total', 'sum', 'average', 'mean']):
            intent.query_type = 'aggregate'
        elif any(word in query_lower for word in ['compare', 'versus', 'vs', 'difference between']):
            intent.query_type = 'compare'
        elif any(word in query_lower for word in ['analyze', 'analysis', 'breakdown', 'distribution']):
            intent.query_type = 'analyze'
        elif any(word in query_lower for word in ['export', 'download', 'csv', 'excel', 'save']):
            intent.query_type = 'export'
        elif any(word in query_lower for word in ['within', 'miles of', 'near', 'around', 'radius']):
            intent.query_type = 'geographic'
        elif any(word in query_lower for word in ['trend', 'over time', 'timeline', 'progression']):
            intent.query_type = 'trend'
        elif any(word in query_lower for word in ['opportunity', 'potential', 'candidate', 'suitable for']):
            intent.query_type = 'opportunity'
        
        # Extract entities
        intent.entities = self._extract_entities(query)
        
        # Apply conversation context if available
        if CONTEXT_AVAILABLE and session_id:
            # Get the result count from previous query (we'll update this after search)
            results_count = 0
            
            # Enhance entities with conversation context
            enhanced_entities = enhance_query_with_context(
                session_id, query, intent.entities, results_count
            )
            
            # Update entities with enhanced context
            intent.entities = enhanced_entities
            
            logger.info(f"Applied conversation context for session {session_id}")
        
        # Build filters from entities
        intent.filters = self._build_filters(intent.entities)
        
        # Detect requested fields
        if 'with' in query_lower and 'details' in query_lower:
            intent.include_fields = ['all']
        elif 'fit id' in query_lower or 'fit ids' in query_lower:
            intent.include_fields.append('fit_id')
        
        # Detect output format
        if 'list' in query_lower or 'all' in query_lower:
            intent.output_format = 'detailed_list'
        elif 'summary' in query_lower:
            intent.output_format = 'summary'
        elif 'table' in query_lower:
            intent.output_format = 'table'
        elif 'csv' in query_lower:
            intent.output_format = 'csv'
        
        # Detect sorting
        if 'largest' in query_lower or 'biggest' in query_lower:
            intent.sort_by = 'capacity_desc'
        elif 'smallest' in query_lower:
            intent.sort_by = 'capacity_asc'
        elif 'newest' in query_lower or 'most recent' in query_lower:
            intent.sort_by = 'commissioned_desc'
        elif 'oldest' in query_lower:
            intent.sort_by = 'commissioned_asc'
        elif 'expiring soon' in query_lower or 'ending soon' in query_lower:
            intent.sort_by = 'fit_remaining_asc'
        
        # Detect limit (but default to no limit for full results)
        limit_match = re.search(r'(?:top|first|last)\s+(\d+)', query_lower)
        if limit_match:
            intent.limit = int(limit_match.group(1))
        elif 'all' in query_lower:
            intent.limit = None  # No limit
        
        return intent
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """
        Extract all entities from the query
        """
        entities = {}
        query_lower = query.lower()
        
        # Try Ollama parser first if available
        if self.ollama_parser:
            try:
                ollama_result = self.ollama_parser.parse_query(query)
                if ollama_result:
                    logger.info(f"Using Ollama parsed result: {ollama_result}")
                    return ollama_result
            except Exception as e:
                logger.warning(f"Ollama parsing failed, falling back to regex: {e}")
        
        # Fallback to regex-based extraction
        # Technology extraction
        tech_mapping = {
            'wind': 'Wind',
            'solar': 'Photovoltaic',
            'photovoltaic': 'Photovoltaic',
            'pv': 'Photovoltaic',
            'hydro': 'Hydro',
            'anaerobic': 'Anaerobic digestion',
            'biogas': 'Anaerobic digestion',
            'ad': 'Anaerobic digestion',
            'chp': 'Micro CHP'
        }
        
        for keyword, tech in tech_mapping.items():
            if keyword in query_lower:
                entities['technology'] = tech
                break
        
        # Location extraction (comprehensive) - case insensitive
        location_patterns = [
            r'in\s+([a-zA-Z][a-zA-Z\s]+?)(?:\s+(?:with|and|or|that|which)|$)',
            r'(?:from|at|near)\s+([a-zA-Z][a-zA-Z\s]+?)(?:\s+(?:with|and|or|that|which)|$)',
            r'([a-zA-Z][a-zA-Z\s]+?)\s+(?:area|region|district)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Capitalize properly (e.g., "ryedale" -> "Ryedale")
                entities['location'] = location.title()
                break
        
        # Capacity extraction
        capacity_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:kw|kilowatt)',
            r'(\d+(?:\.\d+)?)\s*(?:mw|megawatt)',
            r'over\s+(\d+(?:\.\d+)?)\s*(?:kw|mw)',
            r'under\s+(\d+(?:\.\d+)?)\s*(?:kw|mw)',
            r'between\s+(\d+(?:\.\d+)?)\s*and\s+(\d+(?:\.\d+)?)\s*(?:kw|mw)',
            r'larger?\s+than\s+(\d+(?:\.\d+)?)\s*(?:kw|mw)',
            r'smaller?\s+than\s+(\d+(?:\.\d+)?)\s*(?:kw|mw)',
        ]
        
        for pattern in capacity_patterns:
            match = re.search(pattern, query_lower)
            if match:
                if 'between' in pattern:
                    entities['capacity_min'] = float(match.group(1))
                    entities['capacity_max'] = float(match.group(2))
                    if 'mw' in query_lower[match.start():match.end()]:
                        entities['capacity_min'] *= 1000
                        entities['capacity_max'] *= 1000
                elif 'over' in pattern or 'larger' in pattern:
                    entities['capacity_min'] = float(match.group(1))
                    if 'mw' in query_lower[match.start():match.end()]:
                        entities['capacity_min'] *= 1000
                elif 'under' in pattern or 'smaller' in pattern:
                    entities['capacity_max'] = float(match.group(1))
                    if 'mw' in query_lower[match.start():match.end()]:
                        entities['capacity_max'] *= 1000
                else:
                    entities['capacity'] = float(match.group(1))
                    if 'mw' in query_lower[match.start():match.end()]:
                        entities['capacity'] *= 1000
                break
        
        # Date/time extraction
        year_match = re.search(r'(?:in|from|since|before|after)\s+(\d{4})', query_lower)
        if year_match:
            entities['year'] = int(year_match.group(1))
        
        # FIT expiry extraction
        if 'expiring' in query_lower or 'ending' in query_lower:
            if 'soon' in query_lower or 'urgent' in query_lower:
                entities['fit_remaining_max'] = 5
            elif 'within' in query_lower:
                years_match = re.search(r'within\s+(\d+)\s+years?', query_lower)
                if years_match:
                    entities['fit_remaining_max'] = int(years_match.group(1))
        
        # Repowering window extraction
        if 'immediate' in query_lower:
            entities['repowering_window'] = 'IMMEDIATE'
        elif 'urgent' in query_lower:
            entities['repowering_window'] = 'URGENT'
        elif 'optimal' in query_lower:
            entities['repowering_window'] = 'OPTIMAL'
        elif 'planning' in query_lower:
            entities['repowering_window'] = 'PLANNING'
        
        # Geographic radius extraction
        radius_patterns = [
            r'within\s+(\d+)\s*miles?\s+of\s+([a-zA-Z][a-zA-Z\s]+)',
            r'(\d+)\s*miles?\s+(?:from|around)\s+([a-zA-Z][a-zA-Z\s]+)',
            r'near\s+([a-zA-Z][a-zA-Z\s]+)(?:\s+within\s+(\d+)\s*miles?)?',
        ]
        
        for pattern in radius_patterns:
            match = re.search(pattern, query)
            if match:
                if 'near' in pattern:
                    entities['geo_center'] = match.group(1).strip()
                    entities['geo_radius'] = int(match.group(2)) if match.group(2) else 30
                else:
                    entities['geo_radius'] = int(match.group(1))
                    entities['geo_center'] = match.group(2).strip()
                break
        
        # Postcode extraction
        postcode_match = re.search(r'\b([A-Z]{1,2}\d{1,2}[A-Z]?(?:\s*\d[A-Z]{2})?)\b', query.upper())
        if postcode_match:
            entities['postcode'] = postcode_match.group(1)
        
        # FIT ID extraction
        fit_id_patterns = [
            r'fit\s+id\s+(\d+)',
            r'fit\s+(\d+)',
            r'(?:^|\s)(\d{4,6})(?:\s|$)',
        ]
        
        for pattern in fit_id_patterns:
            match = re.search(pattern, query_lower)
            if match:
                entities['fit_id'] = match.group(1)
                break
        
        return entities
    
    def _build_filters(self, entities: Dict) -> Dict:
        """
        Build ChromaDB filters from extracted entities
        """
        filters = {}
        
        if 'technology' in entities:
            filters['technology'] = entities['technology']
        
        if 'repowering_window' in entities:
            filters['repowering_window'] = entities['repowering_window']
        
        # Note: ChromaDB doesn't support complex numeric filters directly
        # We'll handle these in post-processing
        
        return filters
    
    def _handle_search(self, intent: QueryIntent) -> Dict[str, Any]:
        """
        Handle standard search queries with full details
        """
        # Build where clause
        where_clause = intent.filters if intent.filters else None
        
        # Get all matching records (no limit by default)
        limit = intent.limit if intent.limit else 50000
        
        if intent.entities.get('fit_id'):
            # Direct FIT ID lookup
            results = self.collection.get(
                ids=[f"fit_{intent.entities['fit_id']}"]
            )
        else:
            # General search
            results = self.collection.get(
                where=where_clause,
                limit=limit
            )
        
        # Post-process filters
        filtered_results = self._apply_post_filters(results, intent.entities)
        
        # If no results and we have location + capacity, find alternatives
        alternatives = None
        if len(filtered_results['metadatas']) == 0 and intent.entities.get('location') and intent.entities.get('target_capacity'):
            alternatives = self._find_alternatives_in_location(intent.entities)
        
        # Sort results
        sorted_results = self._sort_results(filtered_results, intent.sort_by)
        
        # Format response with alternatives if needed
        response = self._format_response(sorted_results, intent)
        if alternatives:
            response['alternatives'] = alternatives
        
        return response
    
    def _handle_geographic(self, intent: QueryIntent) -> Dict[str, Any]:
        """
        Handle geographic radius searches
        """
        if not intent.entities.get('geo_center'):
            return {'error': 'No location specified for geographic search'}
        
        # Use geographic search
        geo_results = self.geo_search.search_by_radius(
            center_location=intent.entities['geo_center'],
            radius_miles=intent.entities.get('geo_radius', 30),
            technology=intent.entities.get('technology'),
            min_capacity_kw=intent.entities.get('capacity_min'),
            max_capacity_kw=intent.entities.get('capacity_max'),
            limit=intent.limit if intent.limit else 10000
        )
        
        # Format with distance information
        formatted_results = []
        for result in geo_results:
            formatted_results.append({
                'fit_id': result['metadata'].get('fit_id'),
                'technology': result['metadata'].get('technology'),
                'capacity_kw': result['metadata'].get('capacity_kw'),
                'location': result['metadata'].get('local_authority'),
                'postcode': result['metadata'].get('postcode'),
                'distance_miles': result['distance_miles'],
                'commissioned_date': result['metadata'].get('commissioned_date'),
                'remaining_fit_years': result['metadata'].get('remaining_fit_years'),
                'repowering_window': result['metadata'].get('repowering_window'),
                'fit_rate_p_kwh': result['metadata'].get('fit_rate_p_kwh'),
                'fit_period': result['metadata'].get('fit_period'),
                'estimated_annual_fit_revenue_gbp': result['metadata'].get('estimated_annual_fit_revenue_gbp'),
                'latitude': result.get('latitude'),
                'longitude': result.get('longitude')
            })
        
        return {
            'success': True,
            'query_type': 'geographic',
            'center': intent.entities['geo_center'],
            'radius_miles': intent.entities.get('geo_radius', 30),
            'total_found': len(formatted_results),
            'results': formatted_results,
            'summary': self._generate_summary(formatted_results)
        }
    
    def _handle_aggregation(self, intent: QueryIntent) -> Dict[str, Any]:
        """
        Handle aggregation queries (count, sum, average, etc.)
        """
        # Get all matching records
        where_clause = intent.filters if intent.filters else None
        results = self.collection.get(
            where=where_clause,
            limit=50000
        )
        
        # Apply post-filters
        filtered_results = self._apply_post_filters(results, intent.entities)
        
        # Calculate aggregations
        aggregations = {}
        
        if filtered_results['metadatas']:
            df = pd.DataFrame(filtered_results['metadatas'])
            
            aggregations['total_count'] = len(df)
            
            if 'capacity_kw' in df.columns:
                aggregations['total_capacity_kw'] = df['capacity_kw'].sum()
                aggregations['total_capacity_mw'] = aggregations['total_capacity_kw'] / 1000
                aggregations['average_capacity_kw'] = df['capacity_kw'].mean()
                aggregations['min_capacity_kw'] = df['capacity_kw'].min()
                aggregations['max_capacity_kw'] = df['capacity_kw'].max()
            
            if 'technology' in df.columns:
                aggregations['by_technology'] = df['technology'].value_counts().to_dict()
            
            if 'repowering_window' in df.columns:
                aggregations['by_repowering_window'] = df['repowering_window'].value_counts().to_dict()
            
            if 'local_authority' in df.columns:
                aggregations['by_location'] = df['local_authority'].value_counts().head(10).to_dict()
            
            if 'remaining_fit_years' in df.columns:
                aggregations['average_fit_remaining'] = df['remaining_fit_years'].mean()
                aggregations['installations_expiring_5_years'] = len(df[df['remaining_fit_years'] <= 5])
        
        return {
            'success': True,
            'query_type': 'aggregation',
            'filters_applied': intent.entities,
            'aggregations': aggregations,
            'detailed_breakdown': self._generate_detailed_breakdown(filtered_results['metadatas'])
        }
    
    def _handle_analysis(self, intent: QueryIntent) -> Dict[str, Any]:
        """
        Handle analysis queries with insights
        """
        # Get data
        where_clause = intent.filters if intent.filters else None
        results = self.collection.get(
            where=where_clause,
            limit=50000
        )
        
        # Apply filters
        filtered_results = self._apply_post_filters(results, intent.entities)
        
        if not filtered_results['metadatas']:
            return {'success': False, 'message': 'No data found for analysis'}
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(filtered_results['metadatas'])
        
        analysis = {
            'total_installations': len(df),
            'insights': [],
            'opportunities': [],
            'risks': []
        }
        
        # Technology analysis
        if 'technology' in df.columns:
            tech_dist = df['technology'].value_counts()
            analysis['technology_distribution'] = tech_dist.to_dict()
            dominant_tech = tech_dist.index[0]
            analysis['insights'].append(f"{dominant_tech} dominates with {tech_dist.iloc[0]} installations ({tech_dist.iloc[0]/len(df)*100:.1f}%)")
        
        # Capacity analysis
        if 'capacity_kw' in df.columns:
            analysis['capacity_statistics'] = {
                'total_mw': df['capacity_kw'].sum() / 1000,
                'average_kw': df['capacity_kw'].mean(),
                'median_kw': df['capacity_kw'].median(),
                'std_dev_kw': df['capacity_kw'].std()
            }
            
            # Identify large installations
            large_threshold = df['capacity_kw'].quantile(0.9)
            large_sites = df[df['capacity_kw'] >= large_threshold]
            analysis['opportunities'].append(f"{len(large_sites)} large installations (>={large_threshold:.0f}kW) suitable for corporate PPAs")
        
        # FIT expiry analysis
        if 'remaining_fit_years' in df.columns:
            urgent = df[df['remaining_fit_years'] <= 5]
            optimal = df[(df['remaining_fit_years'] > 5) & (df['remaining_fit_years'] <= 10)]
            
            if len(urgent) > 0:
                analysis['risks'].append(f"{len(urgent)} installations expiring within 5 years need immediate PPA negotiations")
            
            if len(optimal) > 0:
                analysis['opportunities'].append(f"{len(optimal)} installations in optimal window (5-10 years) for PPA planning")
        
        # Geographic clustering
        if 'local_authority' in df.columns:
            location_counts = df['local_authority'].value_counts()
            top_clusters = location_counts.head(5)
            analysis['geographic_clusters'] = top_clusters.to_dict()
            analysis['insights'].append(f"Highest concentration in {top_clusters.index[0]} with {top_clusters.iloc[0]} installations")
        
        # Time-based analysis
        if 'commissioned_date' in df.columns:
            df['commissioned_date'] = pd.to_datetime(df['commissioned_date'])
            df['year_commissioned'] = df['commissioned_date'].dt.year
            yearly_trend = df.groupby('year_commissioned').size()
            peak_year = yearly_trend.idxmax()
            analysis['insights'].append(f"Peak installation year was {peak_year} with {yearly_trend[peak_year]} installations")
        
        return {
            'success': True,
            'query_type': 'analysis',
            'analysis': analysis,
            'recommendations': self._generate_recommendations(df)
        }
    
    def _handle_export(self, intent: QueryIntent) -> Dict[str, Any]:
        """
        Handle export queries - return full data in requested format
        """
        # Get all matching data
        results = self._handle_search(intent)
        
        if intent.output_format == 'csv':
            # Format as CSV-ready data
            return {
                'success': True,
                'query_type': 'export',
                'format': 'csv',
                'columns': list(results['results'][0].keys()) if results['results'] else [],
                'data': results['results'],
                'csv_string': self._to_csv(results['results'])
            }
        else:
            return results
    
    def _find_alternatives_in_location(self, entities: Dict) -> Dict:
        """
        Find what IS available in the specified location
        """
        location = entities.get('location')
        target_capacity = entities.get('target_capacity', 0)
        
        # Get all installations in the location
        location_results = self.collection.get(
            where={},
            limit=10000
        )
        
        # Filter by location only
        location_matches = []
        for i, metadata in enumerate(location_results['metadatas']):
            if location.lower() in metadata.get('local_authority', '').lower() or \
               location.lower() in metadata.get('location', '').lower():
                location_matches.append(metadata)
        
        if not location_matches:
            return {'message': f'No installations found in {location}'}
        
        # Group by technology and find closest capacities
        by_technology = {}
        for item in location_matches:
            tech = item.get('technology', 'Unknown')
            if tech not in by_technology:
                by_technology[tech] = []
            
            capacity = item.get('capacity_kw', 0)
            distance = abs(capacity - target_capacity)
            by_technology[tech].append({
                'capacity_kw': capacity,
                'distance': distance,
                'fit_id': item.get('fit_id'),
                'fit_rate': item.get('fit_rate_p_kwh')
            })
        
        # Sort each technology by closest capacity
        alternatives = {}
        for tech, items in by_technology.items():
            items.sort(key=lambda x: x['distance'])
            # Get top 3 closest
            alternatives[tech] = {
                'count': len(items),
                'closest_matches': items[:3],
                'capacity_range': {
                    'min': min(item['capacity_kw'] for item in items),
                    'max': max(item['capacity_kw'] for item in items)
                }
            }
        
        return {
            'location': location,
            'target_capacity': target_capacity,
            'total_in_location': len(location_matches),
            'by_technology': alternatives
        }
    
    def _apply_post_filters(self, results: Dict, entities: Dict) -> Dict:
        """
        Apply filters that ChromaDB can't handle directly
        """
        if not results['metadatas']:
            return results
        
        filtered_indices = []
        
        # Smart capacity matching - if specific capacity is mentioned, use range
        capacity_range_kw = 25  # ±25kW range (can be adjusted)
        
        # Check if specific capacity is mentioned (not min/max)
        if 'capacity' in entities and 'capacity_min' not in entities and 'capacity_max' not in entities:
            # Convert to range for nearest neighbor matching
            target_capacity = entities['capacity']
            entities['capacity_min'] = target_capacity - capacity_range_kw
            entities['capacity_max'] = target_capacity + capacity_range_kw
            entities['target_capacity'] = target_capacity  # Store for sorting by closest match
        
        for i, metadata in enumerate(results['metadatas']):
            include = True
            
            # Capacity filters
            if 'capacity_min' in entities:
                if metadata.get('capacity_kw', 0) < entities['capacity_min']:
                    include = False
            
            if 'capacity_max' in entities:
                if metadata.get('capacity_kw', 0) > entities['capacity_max']:
                    include = False
            
            # FIT remaining filters
            if 'fit_remaining_max' in entities:
                if metadata.get('remaining_fit_years', 100) > entities['fit_remaining_max']:
                    include = False
            
            # Location filter
            if 'location' in entities:
                location = entities['location'].lower()
                if location not in metadata.get('local_authority', '').lower() and \
                   location not in metadata.get('location', '').lower():
                    include = False
            
            # Technology filter (in case ChromaDB didn't filter it)
            if 'technology' in entities:
                if metadata.get('technology', '').lower() != entities['technology'].lower():
                    include = False
            
            # Postcode filter
            if 'postcode' in entities:
                if not metadata.get('postcode', '').startswith(entities['postcode']):
                    include = False
            
            # Postcode patterns filter (from Ollama parser)
            if 'postcode_patterns' in entities:
                postcode = metadata.get('postcode', '')
                if postcode:
                    matches_pattern = any(postcode.startswith(pattern) for pattern in entities['postcode_patterns'])
                    if not matches_pattern:
                        include = False
                else:
                    # If no postcode data, exclude it
                    include = False
            
            # Year filter
            if 'year' in entities:
                comm_date = metadata.get('commissioned_date', '')
                if comm_date and str(entities['year']) not in comm_date:
                    include = False
            
            if include:
                filtered_indices.append(i)
        
        # Sort by closest capacity match if target capacity is specified
        if 'target_capacity' in entities and filtered_indices:
            # Calculate distance from target for each result
            capacity_distances = []
            for idx in filtered_indices:
                actual_capacity = results['metadatas'][idx].get('capacity_kw', 0)
                distance = abs(actual_capacity - entities['target_capacity'])
                capacity_distances.append((idx, distance))
            
            # Sort by distance (closest first)
            capacity_distances.sort(key=lambda x: x[1])
            filtered_indices = [idx for idx, _ in capacity_distances]
        
        # Return filtered results
        return {
            'ids': [results['ids'][i] for i in filtered_indices],
            'metadatas': [results['metadatas'][i] for i in filtered_indices],
            'documents': [results['documents'][i] for i in filtered_indices] if 'documents' in results else [],
            'embeddings': [results['embeddings'][i] for i in filtered_indices] if results.get('embeddings') else []
        }
    
    def _sort_results(self, results: Dict, sort_by: Optional[str]) -> Dict:
        """
        Sort results based on specified criteria
        """
        if not sort_by or not results['metadatas']:
            return results
        
        # Create list of tuples (index, sort_value)
        sort_data = []
        
        for i, metadata in enumerate(results['metadatas']):
            if sort_by == 'capacity_desc':
                sort_value = -metadata.get('capacity_kw', 0)
            elif sort_by == 'capacity_asc':
                sort_value = metadata.get('capacity_kw', 0)
            elif sort_by == 'commissioned_desc':
                sort_value = metadata.get('commissioned_date', '')
                sort_value = -int(sort_value[:4]) if sort_value else 0
            elif sort_by == 'commissioned_asc':
                sort_value = metadata.get('commissioned_date', '')
                sort_value = int(sort_value[:4]) if sort_value else 9999
            elif sort_by == 'fit_remaining_asc':
                sort_value = metadata.get('remaining_fit_years', 100)
            else:
                sort_value = 0
            
            sort_data.append((i, sort_value))
        
        # Sort
        sort_data.sort(key=lambda x: x[1])
        sorted_indices = [x[0] for x in sort_data]
        
        # Return sorted results
        return {
            'ids': [results['ids'][i] for i in sorted_indices],
            'metadatas': [results['metadatas'][i] for i in sorted_indices],
            'documents': [results['documents'][i] for i in sorted_indices] if 'documents' in results else [],
            'embeddings': [results['embeddings'][i] for i in sorted_indices] if 'embeddings' in results else []
        }
    
    def _format_response(self, results: Dict, intent: QueryIntent) -> Dict[str, Any]:
        """
        Format response based on intent and output format
        NO LIMITATIONS on response size
        """
        formatted_results = []
        
        for i, metadata in enumerate(results['metadatas']):
            if intent.output_format == 'detailed_list' or 'all' in intent.include_fields:
                # Include ALL fields
                formatted_results.append(metadata)
            else:
                # Include requested fields
                formatted_item = {}
                if not intent.include_fields or 'fit_id' in intent.include_fields:
                    formatted_item['fit_id'] = metadata.get('fit_id')
                if not intent.include_fields or 'technology' in intent.include_fields:
                    formatted_item['technology'] = metadata.get('technology')
                if not intent.include_fields or 'capacity_kw' in intent.include_fields:
                    formatted_item['capacity_kw'] = metadata.get('capacity_kw')
                    formatted_item['capacity_mw'] = metadata.get('capacity_kw', 0) / 1000
                if not intent.include_fields or 'location' in intent.include_fields:
                    formatted_item['location'] = metadata.get('local_authority')
                    formatted_item['postcode'] = metadata.get('postcode')
                if not intent.include_fields or 'dates' in intent.include_fields:
                    formatted_item['commissioned_date'] = metadata.get('commissioned_date')
                if not intent.include_fields or 'fit' in intent.include_fields:
                    formatted_item['remaining_fit_years'] = metadata.get('remaining_fit_years')
                    formatted_item['repowering_window'] = metadata.get('repowering_window')
                    # Include FIT rate data
                    formatted_item['fit_rate_p_kwh'] = metadata.get('fit_rate_p_kwh')
                    formatted_item['fit_period'] = metadata.get('fit_period')
                    formatted_item['estimated_annual_fit_revenue_gbp'] = metadata.get('estimated_annual_fit_revenue_gbp')
                
                formatted_results.append(formatted_item)
        
        # Generate comprehensive response
        response = {
            'success': True,
            'query_type': intent.query_type,
            'total_results': len(formatted_results),
            'results': formatted_results,  # ALL results, no truncation
            'summary': self._generate_summary(formatted_results),
            'filters_applied': intent.entities,
            'output_format': intent.output_format
        }
        
        # Add analytics if there are results
        if formatted_results:
            response['analytics'] = self._generate_analytics(formatted_results)
        
        return response
    
    def _generate_summary(self, results: List[Dict]) -> Dict:
        """
        Generate comprehensive summary of results
        """
        if not results:
            return {'message': 'No results found'}
        
        summary = {
            'total_count': len(results),
            'technologies': {},
            'capacity_range': {},
            'locations': {},
            'fit_status': {}
        }
        
        # Aggregate data
        for item in results:
            # Technology counts
            tech = item.get('technology', 'Unknown')
            summary['technologies'][tech] = summary['technologies'].get(tech, 0) + 1
            
            # Capacity stats
            capacity = item.get('capacity_kw', 0)
            if 'min' not in summary['capacity_range']:
                summary['capacity_range']['min'] = capacity
                summary['capacity_range']['max'] = capacity
            else:
                summary['capacity_range']['min'] = min(summary['capacity_range']['min'], capacity)
                summary['capacity_range']['max'] = max(summary['capacity_range']['max'], capacity)
            
            # Location counts (top 10)
            location = item.get('location', 'Unknown')
            if location:
                summary['locations'][location] = summary['locations'].get(location, 0) + 1
        
        # Keep only top 10 locations
        if len(summary['locations']) > 10:
            top_locations = sorted(summary['locations'].items(), key=lambda x: x[1], reverse=True)[:10]
            summary['locations'] = dict(top_locations)
        
        # Add average capacity
        if results:
            total_capacity = sum(item.get('capacity_kw', 0) for item in results)
            summary['capacity_range']['average'] = total_capacity / len(results)
            summary['capacity_range']['total_mw'] = total_capacity / 1000
        
        return summary
    
    def _generate_analytics(self, results: List[Dict]) -> Dict:
        """
        Generate advanced analytics from results
        """
        analytics = {
            'opportunities': [],
            'risks': [],
            'insights': []
        }
        
        # Analyze FIT expiry
        expiring_soon = [r for r in results if r.get('remaining_fit_years', 100) < 5]
        if expiring_soon:
            analytics['risks'].append(f"{len(expiring_soon)} installations expiring within 5 years")
        
        # Analyze capacity distribution
        large_sites = [r for r in results if r.get('capacity_kw', 0) > 500]
        if large_sites:
            analytics['opportunities'].append(f"{len(large_sites)} large installations (>500kW) suitable for utility-scale PPAs")
        
        # Technology insights
        tech_counts = {}
        for r in results:
            tech = r.get('technology', 'Unknown')
            tech_counts[tech] = tech_counts.get(tech, 0) + 1
        
        if tech_counts:
            dominant = max(tech_counts, key=tech_counts.get)
            analytics['insights'].append(f"{dominant} is the dominant technology with {tech_counts[dominant]} installations")
        
        return analytics
    
    def _generate_recommendations(self, df: pd.DataFrame) -> List[str]:
        """
        Generate actionable recommendations from data
        """
        recommendations = []
        
        # Check for urgent actions
        if 'remaining_fit_years' in df.columns:
            urgent = df[df['remaining_fit_years'] <= 3]
            if len(urgent) > 0:
                recommendations.append(f"URGENT: Contact {len(urgent)} sites expiring within 3 years for immediate PPA negotiations")
        
        # Check for opportunities
        if 'capacity_kw' in df.columns:
            large_wind = df[(df['technology'] == 'Wind') & (df['capacity_kw'] >= 500)]
            if len(large_wind) > 0:
                recommendations.append(f"OPPORTUNITY: {len(large_wind)} large wind farms ideal for corporate renewable energy buyers")
        
        # Geographic clustering opportunities
        if 'local_authority' in df.columns:
            location_counts = df['local_authority'].value_counts()
            if location_counts.iloc[0] >= 10:
                recommendations.append(f"STRATEGY: Consider portfolio approach for {location_counts.iloc[0]} sites in {location_counts.index[0]}")
        
        return recommendations
    
    def _generate_detailed_breakdown(self, results: List[Dict]) -> Dict:
        """
        Generate detailed breakdown of results
        """
        breakdown = defaultdict(lambda: defaultdict(list))
        
        for item in results:
            tech = item.get('technology', 'Unknown')
            location = item.get('local_authority', 'Unknown')
            
            breakdown[tech][location].append({
                'fit_id': item.get('fit_id'),
                'capacity_kw': item.get('capacity_kw'),
                'remaining_years': item.get('remaining_fit_years')
            })
        
        return dict(breakdown)
    
    def _to_csv(self, data: List[Dict]) -> str:
        """
        Convert data to CSV string
        """
        if not data:
            return ""
        
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()


def test_enhanced_nlp():
    """Test the enhanced NLP processor"""
    processor = EnhancedNLPProcessor()
    
    # Test queries
    test_queries = [
        "List all wind farms in East Yorkshire with their FIT IDs",
        "How many solar installations are there over 1MW?",
        "Show me all installations expiring within 5 years",
        "Compare wind vs solar capacity in Scotland",
        "Find the largest 10 installations by capacity",
        "What's the total capacity of all renewable installations?",
        "Export all wind farms in CSV format",
        "Analyze the geographic distribution of installations",
        "Find opportunities for PPA acquisition",
        "Show me installations within 30 miles of Manchester over 500kW"
    ]
    
    for query in test_queries[:3]:  # Test first 3
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        result = processor.process_query(query)
        
        if result.get('success'):
            print(f"Found: {result.get('total_results', 0)} results")
            print(f"Query type: {result.get('query_type')}")
            
            if result.get('summary'):
                print(f"Summary: {json.dumps(result['summary'], indent=2)[:500]}...")
            
            if result.get('results') and len(result['results']) > 0:
                print(f"First 3 results:")
                for item in result['results'][:3]:
                    print(f"  - FIT {item.get('fit_id')}: {item.get('technology')}, {item.get('capacity_kw')}kW")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    test_enhanced_nlp()