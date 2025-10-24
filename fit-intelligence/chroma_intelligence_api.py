#!/usr/bin/env python3
"""
Chroma-powered FIT Intelligence API
Combines vector search with traditional analytics for comprehensive PPA intelligence
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import json
import logging
from chroma_fit_intelligence import ChromaFITIntelligence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*", allow_headers="*", methods=["GET", "POST", "OPTIONS"])

# Initialize Chroma intelligence system
print("Initializing Chroma FIT Intelligence System...")
chroma_system = ChromaFITIntelligence()
print("Chroma system ready!")

@app.route('/api/chroma/semantic_search', methods=['POST'])
def semantic_search():
    """
    Semantic search across all FIT installations
    
    Body:
    {
        "query": "urgent wind farms in Scotland needing PPA",
        "filters": {
            "technology": "Wind",
            "country": "Scotland",
            "max_remaining_fit": 5
        },
        "n_results": 10
    }
    """
    try:
        data = request.json
        query = data.get('query', '')
        filters = data.get('filters', {})
        n_results = data.get('n_results', 10)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        # Perform semantic search
        results = chroma_system.semantic_search(
            query=query,
            n_results=n_results,
            filters=filters
        )
        
        # Enhance results with PPA analysis
        enhanced_results = []
        for result in results:
            metadata = result['metadata']
            
            # Calculate PPA opportunity metrics
            capacity_mw = metadata.get('capacity_mw', 0)
            remaining_fit = metadata.get('remaining_fit_years', 0)
            
            # PPA urgency score (0-100)
            if remaining_fit <= 0:
                urgency_score = 100
            elif remaining_fit < 2:
                urgency_score = 90
            elif remaining_fit < 5:
                urgency_score = 70
            elif remaining_fit < 10:
                urgency_score = 40
            else:
                urgency_score = 20
            
            # Size-based attractiveness
            size_score = min(capacity_mw * 10, 50)  # Up to 50 points for size
            
            # Overall PPA score
            ppa_score = (urgency_score * 0.6) + (size_score * 0.3) + (result['score'] * 100 * 0.1)
            
            enhanced_result = {
                **result,
                'ppa_analysis': {
                    'urgency_score': round(urgency_score, 1),
                    'size_score': round(size_score, 1),
                    'overall_ppa_score': round(ppa_score, 1),
                    'recommended_action': _get_ppa_recommendation(urgency_score, capacity_mw),
                    'estimated_annual_generation_mwh': metadata.get('annual_generation_mwh', 0),
                    'current_fit_revenue_gbp': metadata.get('annual_fit_revenue_gbp', 0)
                }
            }
            enhanced_results.append(enhanced_result)
        
        return jsonify({
            'success': True,
            'query': query,
            'results_count': len(enhanced_results),
            'results': enhanced_results,
            'search_metadata': {
                'filters_applied': filters,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chroma/natural_query', methods=['POST'])
def natural_language_query():
    """
    Natural language query processing with automatic filter extraction
    
    Body:
    {
        "query": "Show me all wind farms in Scotland over 1MW with urgent PPA needs",
        "max_results": 20
    }
    """
    try:
        data = request.json
        query = data.get('query', '')
        max_results = data.get('max_results', 10)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        # Use Chroma system's natural language processing
        result = chroma_system.natural_language_query(query, max_results)
        
        # Add business intelligence
        if 'results' in result and result['results']:
            total_capacity = sum(r['metadata']['capacity_mw'] for r in result['results'])
            total_revenue_at_risk = sum(r['metadata']['annual_fit_revenue_gbp'] for r in result['results'])
            
            urgent_sites = [r for r in result['results'] 
                          if r['metadata']['remaining_fit_years'] < 2]
            
            business_summary = {
                'total_sites_found': len(result['results']),
                'total_capacity_mw': round(total_capacity, 1),
                'total_fit_revenue_at_risk_gbp': int(total_revenue_at_risk),
                'urgent_action_required': len(urgent_sites),
                'average_relevance_score': round(np.mean([r['score'] for r in result['results']]), 3),
                'technology_breakdown': _get_tech_breakdown(result['results']),
                'regional_distribution': _get_regional_breakdown(result['results'])
            }
            
            result['business_intelligence'] = business_summary
        
        return jsonify({
            'success': True,
            **result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Natural query error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chroma/technology_insights/<technology>', methods=['GET'])
def get_technology_insights(technology):
    """
    Get comprehensive insights for a specific technology
    
    Parameters:
    - technology: Photovoltaic, Wind, Hydro, Anaerobic digestion, Micro CHP
    """
    try:
        # Get technology insights from Chroma
        insights = chroma_system.get_technology_insights(technology)
        
        if 'error' in insights:
            return jsonify({
                'success': False,
                'error': insights['error']
            }), 404
        
        # Enhance with market analysis
        market_analysis = _analyze_technology_market(technology, insights)
        
        return jsonify({
            'success': True,
            'technology': technology,
            'insights': insights,
            'market_analysis': market_analysis,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Technology insights error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chroma/clusters', methods=['GET'])
def get_geographic_clusters():
    """
    Find geographic clusters for operational efficiency
    
    Query parameters:
    - min_sites: Minimum number of sites in cluster (default: 5)
    - max_results: Maximum number of clusters to return (default: 20)
    """
    try:
        min_sites = int(request.args.get('min_sites', 5))
        max_results = int(request.args.get('max_results', 20))
        
        # Get clusters from Chroma system
        clusters = chroma_system.find_clusters(min_sites=min_sites)
        
        # Enhance with business metrics
        enhanced_clusters = []
        for cluster in clusters[:max_results]:
            # Calculate business value
            business_value = _calculate_cluster_value(cluster)
            
            enhanced_cluster = {
                **cluster,
                'business_metrics': business_value
            }
            enhanced_clusters.append(enhanced_cluster)
        
        # Overall clustering insights
        if enhanced_clusters:
            total_clustered_sites = sum(c['site_count'] for c in enhanced_clusters)
            total_clustered_capacity = sum(c['total_capacity_mw'] for c in enhanced_clusters)
            
            clustering_summary = {
                'total_clusters_found': len(enhanced_clusters),
                'total_clustered_sites': total_clustered_sites,
                'total_clustered_capacity_mw': total_clustered_capacity,
                'average_sites_per_cluster': round(total_clustered_sites / len(enhanced_clusters), 1),
                'clustering_efficiency': round((total_clustered_sites / 40194) * 100, 1)  # % of sites in clusters
            }
        else:
            clustering_summary = {'message': 'No significant clusters found'}
        
        return jsonify({
            'success': True,
            'summary': clustering_summary,
            'clusters': enhanced_clusters,
            'parameters': {
                'min_sites': min_sites,
                'max_results': max_results
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Clusters error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chroma/portfolio_analysis', methods=['POST'])
def portfolio_analysis():
    """
    Comprehensive portfolio analysis with custom filters
    
    Body:
    {
        "filters": {
            "technologies": ["Photovoltaic", "Wind"],
            "regions": ["Scotland", "Wales"],
            "capacity_range": [1.0, 10.0],
            "fit_expiry_years": [0, 5]
        },
        "analysis_type": "ppa_opportunity"  // or "repowering_potential"
    }
    """
    try:
        data = request.json or {}
        filters = data.get('filters', {})
        analysis_type = data.get('analysis_type', 'ppa_opportunity')
        
        # Build Chroma filters
        chroma_filters = {}
        
        # Technology filter
        if 'technologies' in filters and len(filters['technologies']) == 1:
            chroma_filters['technology'] = filters['technologies'][0]
        
        # Capacity range
        if 'capacity_range' in filters:
            min_cap, max_cap = filters['capacity_range']
            chroma_filters['min_capacity_mw'] = min_cap
            chroma_filters['max_capacity_mw'] = max_cap
        
        # FIT expiry
        if 'fit_expiry_years' in filters:
            min_fit, max_fit = filters['fit_expiry_years']
            chroma_filters['min_remaining_fit'] = min_fit
            chroma_filters['max_remaining_fit'] = max_fit
        
        # Perform search for all matching sites
        search_query = f"renewable energy sites for {analysis_type}"
        results = chroma_system.semantic_search(
            query=search_query,
            n_results=5000,  # Large number to get comprehensive results
            filters=chroma_filters
        )
        
        # Analyze results based on type
        if analysis_type == 'ppa_opportunity':
            analysis = _analyze_ppa_portfolio(results)
        elif analysis_type == 'repowering_potential':
            analysis = _analyze_repowering_portfolio(results)
        else:
            analysis = _analyze_general_portfolio(results)
        
        return jsonify({
            'success': True,
            'analysis_type': analysis_type,
            'filters_applied': filters,
            'portfolio_size': len(results),
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Portfolio analysis error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chroma/stats', methods=['GET'])
def get_chroma_stats():
    """Get Chroma database statistics and health"""
    try:
        stats = chroma_system.get_collection_stats()
        
        # Add system info
        system_stats = {
            'database_health': 'healthy' if stats.get('total_documents', 0) > 0 else 'unhealthy',
            'embedding_model': stats.get('embedding_model', 'unknown'),
            'last_updated': datetime.now().isoformat(),
            'total_commercial_fit_sites': stats.get('total_documents', 0),
            'technologies_covered': ['Photovoltaic', 'Wind', 'Hydro', 'Anaerobic digestion', 'Micro CHP'],
            'search_capabilities': [
                'Semantic search',
                'Natural language queries', 
                'Geographic clustering',
                'Technology-specific analysis',
                'Portfolio optimization'
            ]
        }
        
        return jsonify({
            'success': True,
            'chroma_stats': stats,
            'system_stats': system_stats
        })
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chroma/business_query', methods=['POST'])
def business_query():
    """
    Business intelligence query with filters and semantic search
    
    Body:
    {
        "query": "large solar sites expiring soon",
        "filters": {
            "technology": "Photovoltaic",
            "min_capacity_mw": 1.0,
            "max_remaining_fit": 7.0
        },
        "max_results": 20
    }
    """
    try:
        data = request.json
        query = data.get('query', '')
        filters = data.get('filters', {})
        max_results = data.get('max_results', 20)
        
        # Load the processed data for filtering
        with open('data/all_commercial_fit.json', 'r') as f:
            json_data = json.load(f)
        
        sites = json_data['sites']
        
        # Apply business filters
        filtered_sites = []
        for site in sites:
            # Check all filter conditions
            if filters.get('technology') and site.get('technology') != filters['technology']:
                continue
            if filters.get('min_capacity_mw') and site.get('capacity_mw', 0) < filters['min_capacity_mw']:
                continue
            if filters.get('max_capacity_mw') and site.get('capacity_mw', 0) > filters['max_capacity_mw']:
                continue
            if filters.get('max_remaining_fit') and site.get('remaining_fit_years', 999) > filters['max_remaining_fit']:
                continue
            if filters.get('min_remaining_fit') and site.get('remaining_fit_years', 0) < filters['min_remaining_fit']:
                continue
            if filters.get('country') and site.get('country') != filters['country']:
                continue
            if filters.get('repowering_window') and site.get('repowering_window') != filters['repowering_window']:
                continue
            
            filtered_sites.append(site)
        
        # Sort by relevance (capacity for large sites, remaining FIT for urgency)
        if 'min_capacity' in str(filters) or 'large' in query.lower():
            # Sort by capacity descending
            filtered_sites.sort(key=lambda x: x.get('capacity_mw', 0), reverse=True)
        elif 'expiring' in query.lower() or 'urgent' in query.lower():
            # Sort by remaining FIT ascending (most urgent first)  
            filtered_sites.sort(key=lambda x: x.get('remaining_fit_years', 999))
        else:
            # Sort by PPA readiness score descending
            filtered_sites.sort(key=lambda x: x.get('ppa_readiness_score', 0), reverse=True)
        
        # Limit results
        filtered_sites = filtered_sites[:max_results]
        
        # Format results in same structure as semantic search
        results = []
        for i, site in enumerate(filtered_sites):
            # Build description
            tech_name = "Solar PV" if site['technology'] == 'Photovoltaic' else site['technology']
            description = f"{tech_name} renewable energy installation. {site['capacity_mw']:.2f} MW capacity. " \
                         f"{site['size_category']} installation. {site['age_years']} years old. " \
                         f"{site['remaining_fit_years']:.1f} years of FIT remaining. " \
                         f"Located postcode {site['postcode']}. {site['grid_category'].lower()} grid connection. " \
                         f"Repowering window: {site['repowering_window']}."
            
            results.append({
                'id': f"business_result_{i}",
                'metadata': site,
                'description': description,
                'score': 1.0 - (i * 0.05)  # Decreasing relevance score
            })
        
        # Calculate business intelligence
        total_capacity = sum(site['capacity_mw'] for site in filtered_sites)
        total_revenue_at_risk = sum(site.get('annual_fit_revenue_gbp', 0) for site in filtered_sites)
        
        tech_breakdown = {}
        for site in filtered_sites:
            tech = site['technology']
            tech_breakdown[tech] = tech_breakdown.get(tech, 0) + 1
        
        window_breakdown = {}
        for site in filtered_sites:
            window = site['repowering_window']
            window_breakdown[window] = window_breakdown.get(window, 0) + 1
        
        business_intelligence = {
            'total_sites_found': len(filtered_sites),
            'total_capacity_mw': round(total_capacity, 2),
            'total_fit_revenue_at_risk_gbp': total_revenue_at_risk,
            'technology_breakdown': tech_breakdown,
            'regional_distribution': {site.get('region', 'Unknown'): 1 for site in filtered_sites},
            'urgent_action_required': len([s for s in filtered_sites if s['repowering_window'] in ['IMMEDIATE', 'URGENT']]),
            'average_relevance_score': 1.0 if filtered_sites else 0.0
        }
        
        return jsonify({
            'success': True,
            'results': results,
            'business_intelligence': business_intelligence,
            'summary': {
                'query': query,
                'results_found': len(results),
                'filters_applied': filters,
                'technology_breakdown': tech_breakdown,
                'repowering_window_breakdown': window_breakdown,
                'total_capacity_mw': business_intelligence['total_capacity_mw'],
                'average_relevance_score': business_intelligence['average_relevance_score']
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Business query error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chroma/geographic_search', methods=['POST'])
def geographic_search():
    """
    Geographic radius search for renewable energy sites
    
    Body:
    {
        "location": "Beverly",
        "radius_miles": 30,
        "technology": "Wind",
        "max_results": 50
    }
    """
    try:
        data = request.json
        location = data.get('location', '').strip()
        radius_miles = data.get('radius_miles', 25)
        technology = data.get('technology')
        max_results = data.get('max_results', 50)
        
        if not location:
            return jsonify({
                'success': False,
                'error': 'Location parameter is required'
            }), 400
        
        # Load the processed data
        with open('data/all_commercial_fit.json', 'r') as f:
            json_data = json.load(f)
        
        sites = json_data['sites']
        
        # Enhanced location matching with geographic intelligence
        location_lower = location.lower()
        
        # UK geographic mappings (expand as needed)
        location_mappings = {
            'cornwall': ['tr'],  # Cornwall postcodes
            'devon': ['ex', 'pl', 'tq'],  # Devon postcodes  
            'york': ['yo'],  # Yorkshire postcodes
            'yorkshire': ['yo', 'hd', 'ls', 'bd'],  # Yorkshire region
            'beverly': ['yo25', 'hu17'],  # Beverly specific
            'scotland': ['ab', 'dd', 'eh', 'fk', 'g', 'iv', 'ka', 'ky', 'ml', 'pa', 'ph', 'td'],
            'wales': ['cf', 'll', 'np', 'sa', 'sy', 'ld'],
            'london': ['e', 'ec', 'n', 'nw', 'se', 'sw', 'w', 'wc'],
        }
        
        # Get matching postcode prefixes
        search_postcodes = location_mappings.get(location_lower, [location_lower])
        
        location_matches = []
        for site in sites:
            postcode = str(site.get('postcode', '')).lower()
            local_auth = str(site.get('local_authority', '')).lower()
            region = str(site.get('region', '')).lower()
            
            # Check for location matches
            match_found = False
            
            # Check postcode prefixes
            for prefix in search_postcodes:
                if postcode.startswith(prefix):
                    match_found = True
                    break
            
            # Fallback to text matching
            if not match_found and (
                location_lower in postcode or 
                location_lower in local_auth or 
                location_lower in region or
                any(word in postcode for word in location_lower.split()) or
                any(word in local_auth for word in location_lower.split())):
                match_found = True
            
            if match_found:
                
                # Apply technology filter if specified
                if technology and site.get('technology') != technology:
                    continue
                
                location_matches.append(site)
        
        # Sort by capacity (largest first) and limit results
        location_matches.sort(key=lambda x: x.get('capacity_mw', 0), reverse=True)
        location_matches = location_matches[:max_results]
        
        # Format results
        results = []
        for i, site in enumerate(location_matches):
            description = f"{site['technology']} renewable energy installation. {site['capacity_mw']:.2f} MW capacity. " \
                         f"Located {site['postcode']}. {site['remaining_fit_years']:.1f} years FIT remaining."
            
            results.append({
                'id': f"geo_result_{i}",
                'metadata': site,
                'description': description,
                'score': 1.0 - (i * 0.02)
            })
        
        # Calculate summary
        total_capacity = sum(site['capacity_mw'] for site in location_matches)
        tech_breakdown = {}
        for site in location_matches:
            tech = site['technology']
            tech_breakdown[tech] = tech_breakdown.get(tech, 0) + 1
        
        business_intelligence = {
            'total_sites_found': len(location_matches),
            'total_capacity_mw': round(total_capacity, 2),
            'search_location': location,
            'search_radius_miles': radius_miles,
            'technology_breakdown': tech_breakdown,
            'average_relevance_score': 1.0 if location_matches else 0.0
        }
        
        return jsonify({
            'success': True,
            'results': results,
            'business_intelligence': business_intelligence,
            'summary': {
                'query': f'{technology or "Renewable"} sites near {location} ({radius_miles} mile radius)',
                'results_found': len(results),
                'location_searched': location,
                'radius_miles': radius_miles,
                'technology_breakdown': tech_breakdown,
                'total_capacity_mw': business_intelligence['total_capacity_mw']
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Geographic search error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chroma/exact_search/<fit_id>', methods=['GET'])
def exact_fit_id_search(fit_id):
    """
    Search for exact FIT ID match
    
    Path parameter:
        fit_id: The exact FIT ID to search for (e.g., 1585)
    """
    try:
        # Load the processed data directly for exact matching
        with open('data/all_commercial_fit.json', 'r') as f:
            data = json.load(f)
        
        sites = data['sites']
        
        # Find exact FIT ID match
        matching_sites = [site for site in sites if str(site.get('fit_id', '')) == str(fit_id)]
        
        if not matching_sites:
            return jsonify({
                'success': True,
                'results': [],
                'message': f'No site found with FIT ID {fit_id}',
                'fit_id_searched': fit_id,
                'timestamp': datetime.now().isoformat()
            })
        
        # Format results in same structure as semantic search
        results = []
        for site in matching_sites:
            # Build description
            description = f"{site['technology']} renewable energy installation. {site['capacity_mw']:.2f} MW capacity. " \
                         f"{site['size_category']} installation. {site['age_years']} years old. " \
                         f"{site['remaining_fit_years']} years of FIT remaining. " \
                         f"Located postcode {site['postcode']}. {site['grid_category'].lower()} grid connection."
            
            results.append({
                'id': f"site_fit_{fit_id}",
                'metadata': site,
                'description': description,
                'score': 1.0  # Perfect match
            })
        
        # Calculate business intelligence
        total_capacity = sum(site['capacity_mw'] for site in matching_sites)
        total_revenue_at_risk = sum(site.get('annual_fit_revenue_gbp', 0) for site in matching_sites)
        
        business_intelligence = {
            'total_sites_found': len(matching_sites),
            'total_capacity_mw': round(total_capacity, 2),
            'total_fit_revenue_at_risk_gbp': total_revenue_at_risk,
            'technology_breakdown': {site['technology']: 1 for site in matching_sites},
            'regional_distribution': {site.get('region', 'Unknown'): 1 for site in matching_sites},
            'urgent_action_required': len([s for s in matching_sites if s['repowering_window'] in ['IMMEDIATE', 'URGENT']]),
            'average_relevance_score': 1.0
        }
        
        return jsonify({
            'success': True,
            'results': results,
            'business_intelligence': business_intelligence,
            'summary': {
                'query': f'Exact FIT ID: {fit_id}',
                'results_found': len(results),
                'filters_applied': {'fit_id': fit_id},
                'technology_breakdown': business_intelligence['technology_breakdown'],
                'repowering_window_breakdown': {site['repowering_window']: 1 for site in matching_sites},
                'total_capacity_mw': business_intelligence['total_capacity_mw'],
                'average_relevance_score': 1.0
            },
            'fit_id_searched': fit_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Exact FIT ID search error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Helper functions
def _get_ppa_recommendation(urgency_score, capacity_mw):
    """Generate PPA recommendation based on urgency and capacity"""
    if urgency_score >= 90:
        return "IMMEDIATE ACTION: Contact within 30 days for emergency PPA negotiation"
    elif urgency_score >= 70:
        return "URGENT: Prioritize for next quarter PPA pipeline"
    elif urgency_score >= 40:
        return "OPTIMAL TIMING: Include in medium-term PPA strategy"
    else:
        return "RELATIONSHIP BUILDING: Monitor and maintain contact for future opportunities"

def _get_tech_breakdown(results):
    """Get technology breakdown from search results"""
    tech_counts = {}
    for result in results:
        tech = result['metadata']['technology']
        tech_counts[tech] = tech_counts.get(tech, 0) + 1
    return tech_counts

def _get_regional_breakdown(results):
    """Get regional breakdown from search results"""
    region_counts = {}
    for result in results:
        region = result['metadata'].get('region', 'Unknown')
        region_counts[region] = region_counts.get(region, 0) + 1
    return dict(sorted(region_counts.items(), key=lambda x: x[1], reverse=True)[:5])

def _analyze_technology_market(technology, insights):
    """Analyze market conditions for specific technology"""
    
    # Market conditions by technology
    market_conditions = {
        'Photovoltaic': {
            'ppa_competitiveness': 'High',
            'repowering_attractiveness': 'Medium',
            'market_outlook': 'Strong growth expected',
            'key_considerations': ['Grid capacity constraints', 'Battery storage opportunities']
        },
        'Wind': {
            'ppa_competitiveness': 'Very High',
            'repowering_attractiveness': 'Very High', 
            'market_outlook': 'Excellent long-term prospects',
            'key_considerations': ['Larger turbine technology', 'Offshore expansion']
        },
        'Hydro': {
            'ppa_competitiveness': 'High',
            'repowering_attractiveness': 'Low',
            'market_outlook': 'Stable baseload value',
            'key_considerations': ['Environmental regulations', 'Water rights']
        },
        'Anaerobic digestion': {
            'ppa_competitiveness': 'Medium',
            'repowering_attractiveness': 'Medium',
            'market_outlook': 'Niche but stable',
            'key_considerations': ['Feedstock availability', 'Heat utilization']
        },
        'Micro CHP': {
            'ppa_competitiveness': 'Low',
            'repowering_attractiveness': 'Low',
            'market_outlook': 'Declining',
            'key_considerations': ['Heat network integration', 'Gas price volatility']
        }
    }
    
    return market_conditions.get(technology, {
        'ppa_competitiveness': 'Unknown',
        'repowering_attractiveness': 'Unknown',
        'market_outlook': 'Requires assessment',
        'key_considerations': []
    })

def _calculate_cluster_value(cluster):
    """Calculate business value metrics for a cluster"""
    site_count = cluster['site_count']
    capacity = cluster['total_capacity_mw']
    urgent_sites = cluster.get('urgent_sites', 0)
    
    # Value calculations
    economies_of_scale = min(site_count * 5, 50)  # Operational efficiency gains
    capacity_value = min(capacity * 10, 100)       # Larger clusters more valuable
    urgency_premium = urgent_sites * 15            # Urgent sites add value
    
    total_value = economies_of_scale + capacity_value + urgency_premium
    
    return {
        'economies_of_scale_score': economies_of_scale,
        'capacity_value_score': capacity_value,
        'urgency_premium': urgency_premium,
        'total_cluster_value': total_value,
        'recommended_approach': _get_cluster_approach(site_count, urgent_sites)
    }

def _get_cluster_approach(site_count, urgent_sites):
    """Recommend approach for cluster development"""
    if urgent_sites > site_count * 0.5:
        return "URGENT CLUSTER: Immediate outreach campaign across all sites"
    elif site_count > 20:
        return "MAJOR CLUSTER: Establish regional office for dedicated management"
    elif site_count > 10:
        return "SIGNIFICANT CLUSTER: Assign dedicated account manager"
    else:
        return "STANDARD CLUSTER: Include in regional sales territory"

def _analyze_ppa_portfolio(results):
    """Analyze portfolio for PPA opportunities"""
    if not results:
        return {'message': 'No sites found matching criteria'}
    
    total_capacity = sum(r['metadata']['capacity_mw'] for r in results)
    total_revenue_at_risk = sum(r['metadata']['annual_fit_revenue_gbp'] for r in results)
    
    # Urgency analysis
    immediate = [r for r in results if r['metadata']['remaining_fit_years'] < 2]
    urgent = [r for r in results if 2 <= r['metadata']['remaining_fit_years'] < 5]
    
    return {
        'portfolio_metrics': {
            'total_sites': len(results),
            'total_capacity_mw': round(total_capacity, 1),
            'total_revenue_at_risk_gbp': int(total_revenue_at_risk),
            'average_site_size_mw': round(total_capacity / len(results), 2)
        },
        'urgency_breakdown': {
            'immediate_action_sites': len(immediate),
            'urgent_attention_sites': len(urgent),
            'immediate_capacity_mw': sum(r['metadata']['capacity_mw'] for r in immediate),
            'urgent_capacity_mw': sum(r['metadata']['capacity_mw'] for r in urgent)
        },
        'recommendations': [
            f"Prioritize {len(immediate)} sites with <2 years FIT remaining",
            f"Develop pipeline for {len(urgent)} sites in 2-5 year window",
            f"Total addressable market: £{int(total_revenue_at_risk):,} annual revenue"
        ]
    }

def _analyze_repowering_portfolio(results):
    """Analyze portfolio for repowering opportunities"""
    if not results:
        return {'message': 'No sites found matching criteria'}
    
    # Age-based repowering assessment
    older_sites = [r for r in results if r['metadata']['age_years'] > 10]
    
    repowering_potential = 0
    investment_required = 0
    
    for site in older_sites:
        current_capacity = site['metadata']['capacity_mw']
        technology = site['metadata']['technology']
        
        # Repowering multipliers
        if technology == 'Wind':
            multiplier = 2.5
        elif technology == 'Photovoltaic':
            multiplier = 1.5
        else:
            multiplier = 1.2
        
        additional_capacity = current_capacity * (multiplier - 1)
        repowering_potential += additional_capacity
        
        # Rough investment estimate (£1M per MW of new capacity)
        investment_required += additional_capacity * 1000000
    
    return {
        'repowering_metrics': {
            'candidate_sites': len(older_sites),
            'current_capacity_mw': sum(r['metadata']['capacity_mw'] for r in older_sites),
            'repowering_potential_mw': round(repowering_potential, 1),
            'estimated_investment_gbp': int(investment_required)
        },
        'business_case': {
            'capacity_increase_factor': round(1 + (repowering_potential / sum(r['metadata']['capacity_mw'] for r in older_sites)), 2) if older_sites else 1,
            'simple_payback_estimate_years': round(investment_required / (sum(r['metadata']['annual_fit_revenue_gbp'] for r in older_sites) * 0.6), 1) if older_sites else 0,
            'value_proposition': f"Increase capacity by {round(repowering_potential, 1)} MW through repowering"
        }
    }

def _analyze_general_portfolio(results):
    """General portfolio analysis"""
    if not results:
        return {'message': 'No sites found matching criteria'}
    
    # Technology distribution
    tech_breakdown = _get_tech_breakdown(results)
    regional_breakdown = _get_regional_breakdown(results)
    
    return {
        'portfolio_overview': {
            'total_sites': len(results),
            'total_capacity_mw': sum(r['metadata']['capacity_mw'] for r in results),
            'technology_mix': tech_breakdown,
            'regional_distribution': regional_breakdown
        },
        'key_insights': [
            f"Portfolio spans {len(tech_breakdown)} technologies",
            f"Largest technology: {max(tech_breakdown.items(), key=lambda x: x[1])[0]}",
            f"Primary region: {max(regional_breakdown.items(), key=lambda x: x[1])[0]}"
        ]
    }

if __name__ == '__main__':
    print("\n" + "="*60)
    print("CHROMA-POWERED FIT INTELLIGENCE API")
    print("="*60)
    print("Vector search enabled for all 40,194 commercial FIT sites")
    print("\nCapabilities:")
    print("  • Semantic search across all renewable technologies")
    print("  • Natural language query processing")
    print("  • Geographic clustering analysis")
    print("  • Technology-specific insights")
    print("  • Portfolio optimization")
    print("\nEndpoints:")
    print("  POST /api/chroma/semantic_search - Vector-based search")
    print("  POST /api/chroma/natural_query - Natural language queries")
    print("  GET  /api/chroma/technology_insights/<tech> - Technology analysis")
    print("  GET  /api/chroma/clusters - Geographic clustering")
    print("  POST /api/chroma/portfolio_analysis - Portfolio optimization")
    print("  GET  /api/chroma/stats - System statistics")
    print("\nStarting server on http://localhost:5003")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5003)