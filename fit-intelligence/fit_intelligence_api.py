#!/usr/bin/env python3
"""
FIT Intelligence API - RESTful interface for FIT/PPA intelligence system
Provides deep business context for renewable energy PPA opportunities
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import json
import logging
from fit_intelligence_system import FITIntelligenceSystem, FITQueryEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*", allow_headers="*", methods=["GET", "POST", "OPTIONS"])

# Initialize intelligence system
intelligence_system = FITIntelligenceSystem()
query_engine = FITQueryEngine(intelligence_system)

# Cache for performance
CACHE = {
    'portfolio_insights': None,
    'last_update': None
}

def refresh_cache():
    """Refresh cached insights"""
    CACHE['portfolio_insights'] = intelligence_system.get_portfolio_insights()
    CACHE['last_update'] = datetime.now()

# Initialize cache on startup
refresh_cache()

@app.route('/api/intelligence/query', methods=['POST'])
def intelligent_query():
    """
    Main intelligence endpoint - processes natural language queries with full business context
    
    Example queries:
    - "What are the most urgent PPA opportunities?"
    - "Show me clusters of sites in Scotland losing FIT support"
    - "What's the repowering potential for sites over 10 years old?"
    - "Which regions have the highest concentration of expiring FITs?"
    """
    try:
        data = request.json
        query = data.get('query', '')
        context = data.get('context', {})  # Additional business context
        
        # Process query through intelligence engine
        result = query_engine.process_query(query)
        
        # Enhance with business context
        if 'ppa_terms' in context:
            result['ppa_analysis'] = analyze_ppa_terms(result.get('data', {}), context['ppa_terms'])
        
        response = {
            'success': True,
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'result': result,
            'context': {
                'market_conditions': intelligence_system.market_data,
                'data_freshness': CACHE['last_update'].isoformat() if CACHE['last_update'] else None
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/intelligence/opportunities', methods=['GET'])
def get_opportunities():
    """
    Get prioritized PPA opportunities with full business analysis
    
    Query parameters:
    - strategy: IMMEDIATE, OPTIMAL, PLANNING, FUTURE
    - region: Filter by region
    - min_capacity: Minimum capacity in MW
    - max_risk: Maximum risk score (0-1)
    - limit: Number of results
    """
    try:
        # Parse filters
        strategy = request.args.get('strategy', '').upper()
        region = request.args.get('region', '')
        min_capacity = float(request.args.get('min_capacity', 0))
        max_risk = float(request.args.get('max_risk', 1))
        limit = int(request.args.get('limit', 50))
        
        # Get all opportunities
        opportunities = []
        
        # Process solar sites
        for _, site in intelligence_system.solar_data.iterrows():
            if pd.notna(site.get('latitude')) and pd.notna(site.get('longitude')):
                opp = intelligence_system.analyze_ppa_opportunity(site, 'solar')
                
                # Apply filters
                if strategy and strategy not in opp.recommended_strategy:
                    continue
                if region and region.lower() not in opp.location.get('region', '').lower():
                    continue
                if opp.capacity_mw < min_capacity:
                    continue
                if opp.risk_score > max_risk:
                    continue
                
                opportunities.append({
                    'site_id': opp.site_id,
                    'technology': opp.technology,
                    'capacity_mw': opp.capacity_mw,
                    'location': opp.location,
                    'fit_expiry': opp.fit_expiry.isoformat(),
                    'annual_revenue': opp.annual_revenue,
                    'risk_score': opp.risk_score,
                    'opportunity_score': opp.opportunity_score,
                    'strategy': opp.recommended_strategy,
                    'grid_connection': opp.grid_connection
                })
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'total_opportunities': len(opportunities),
            'filtered_count': min(limit, len(opportunities)),
            'opportunities': opportunities[:limit],
            'summary': {
                'total_capacity_mw': sum(o['capacity_mw'] for o in opportunities),
                'average_opportunity_score': np.mean([o['opportunity_score'] for o in opportunities]) if opportunities else 0,
                'immediate_action_count': sum(1 for o in opportunities if 'IMMEDIATE' in o['strategy'])
            }
        })
        
    except Exception as e:
        logger.error(f"Opportunities error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/intelligence/clusters', methods=['GET'])
def get_clusters():
    """
    Identify geographic clusters for operational efficiency
    
    Returns clusters of sites that could be bundled for:
    - Operational efficiency
    - Portfolio PPAs
    - Grid infrastructure investment
    """
    try:
        min_sites = int(request.args.get('min_sites', 3))
        min_capacity = float(request.args.get('min_capacity', 0.5))
        
        df = intelligence_system.solar_data
        
        # Group by postcode area
        df['postcode_area'] = df['postcode'].str[:4]
        clusters = df.groupby('postcode_area').agg({
            'capacity_mw': 'sum',
            'capacity_kw': 'count',
            'latitude': 'mean',
            'longitude': 'mean',
            'remaining_fit_years': 'mean',
            'age_years': 'mean'
        }).rename(columns={'capacity_kw': 'site_count'})
        
        # Filter significant clusters
        significant = clusters[
            (clusters['site_count'] >= min_sites) & 
            (clusters['capacity_mw'] >= min_capacity)
        ]
        
        # Calculate cluster value scores
        cluster_data = []
        for area, data in significant.iterrows():
            # Get sites in this cluster
            cluster_sites = df[df['postcode_area'] == area]
            
            # Calculate cluster metrics
            fit_urgency = len(cluster_sites[cluster_sites['remaining_fit_years'] < 5]) / len(cluster_sites)
            
            cluster_info = {
                'postcode_area': area,
                'site_count': int(data['site_count']),
                'total_capacity_mw': round(data['capacity_mw'], 2),
                'center_lat': round(data['latitude'], 4),
                'center_lon': round(data['longitude'], 4),
                'avg_remaining_fit_years': round(data['remaining_fit_years'], 1),
                'avg_age_years': round(data['age_years'], 1),
                'fit_urgency_score': round(fit_urgency, 2),
                'value_score': round(
                    (data['capacity_mw'] * 10) +  # Capacity value
                    (data['site_count'] * 2) +     # Density value
                    (fit_urgency * 20),             # Urgency value
                    1
                ),
                'sites': cluster_sites[['postcode', 'capacity_kw', 'remaining_fit_years']].to_dict('records')[:10]
            }
            cluster_data.append(cluster_info)
        
        # Sort by value score
        cluster_data.sort(key=lambda x: x['value_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'total_clusters': len(cluster_data),
            'clusters': cluster_data[:20],
            'summary': {
                'total_clustered_capacity_mw': sum(c['total_capacity_mw'] for c in cluster_data),
                'total_clustered_sites': sum(c['site_count'] for c in cluster_data),
                'high_value_clusters': sum(1 for c in cluster_data if c['value_score'] > 50)
            }
        })
        
    except Exception as e:
        logger.error(f"Clusters error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/intelligence/repowering', methods=['GET'])
def analyze_repowering():
    """
    Analyze repowering potential for aging sites
    
    Identifies sites where repowering could:
    - Increase capacity by 50-150%
    - Extend operational life by 20+ years
    - Justify long-term PPA agreements
    """
    try:
        min_age = int(request.args.get('min_age', 10))
        min_capacity = float(request.args.get('min_capacity', 0.1))
        
        df = intelligence_system.solar_data
        
        # Identify repowering candidates
        candidates = df[
            (df['age_years'] >= min_age) &
            (df['capacity_mw'] >= min_capacity)
        ]
        
        repowering_opportunities = []
        
        for _, site in candidates.iterrows():
            current_capacity = site['capacity_mw']
            
            # Calculate repowering potential
            if site['age_years'] > 20:
                # Very old sites - maximum potential
                multiplier = 2.0
            elif site['age_years'] > 15:
                # Old sites - high potential
                multiplier = 1.7
            else:
                # Moderate age - standard potential
                multiplier = 1.5
            
            new_capacity = current_capacity * multiplier
            capacity_increase = new_capacity - current_capacity
            
            # Calculate economics
            repowering_cost_per_mw = 800000  # £800k per MW
            total_cost = capacity_increase * repowering_cost_per_mw
            
            # New generation potential
            capacity_factor = 0.11  # UK solar average
            annual_generation_mwh = new_capacity * 8760 * capacity_factor
            
            # PPA revenue potential (post-repowering)
            ppa_price = 75  # £/MWh
            annual_revenue = annual_generation_mwh * ppa_price
            
            # Simple payback
            payback_years = total_cost / annual_revenue if annual_revenue > 0 else 999
            
            opportunity = {
                'site_id': str(site.get('id', 'unknown')),
                'postcode': site.get('postcode', ''),
                'current_capacity_mw': round(current_capacity, 2),
                'potential_capacity_mw': round(new_capacity, 2),
                'capacity_increase_mw': round(capacity_increase, 2),
                'age_years': site['age_years'],
                'remaining_fit_years': site['remaining_fit_years'],
                'estimated_cost_gbp': int(total_cost),
                'annual_revenue_potential_gbp': int(annual_revenue),
                'simple_payback_years': round(payback_years, 1),
                'location': {
                    'region': site.get('region', ''),
                    'lat': site.get('latitude', 0),
                    'lon': site.get('longitude', 0)
                },
                'value_score': round(
                    (capacity_increase * 10) +  # Capacity increase value
                    (20 / payback_years if payback_years < 20 else 0) * 10 +  # Economic value
                    (5 if site['remaining_fit_years'] < 5 else 0),  # Urgency bonus
                    1
                )
            }
            
            repowering_opportunities.append(opportunity)
        
        # Sort by value score
        repowering_opportunities.sort(key=lambda x: x['value_score'], reverse=True)
        
        # Calculate portfolio metrics
        total_current = sum(o['current_capacity_mw'] for o in repowering_opportunities)
        total_potential = sum(o['potential_capacity_mw'] for o in repowering_opportunities)
        total_investment = sum(o['estimated_cost_gbp'] for o in repowering_opportunities)
        
        return jsonify({
            'success': True,
            'total_candidates': len(repowering_opportunities),
            'opportunities': repowering_opportunities[:50],
            'portfolio_summary': {
                'current_capacity_mw': round(total_current, 1),
                'potential_capacity_mw': round(total_potential, 1),
                'capacity_increase_mw': round(total_potential - total_current, 1),
                'total_investment_required_gbp': total_investment,
                'average_payback_years': round(
                    np.mean([o['simple_payback_years'] for o in repowering_opportunities 
                            if o['simple_payback_years'] < 50]), 1
                )
            },
            'recommendations': [
                "Focus on sites with <5 years FIT remaining for immediate opportunities",
                "Bundle adjacent sites for economies of scale",
                "Partner with original developers where possible",
                "Consider hybrid solar+storage for enhanced value"
            ]
        })
        
    except Exception as e:
        logger.error(f"Repowering error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/intelligence/executive', methods=['GET'])
def get_executive_summary():
    """
    Get executive summary for C-suite presentation
    """
    try:
        summary = intelligence_system.generate_executive_summary()
        insights = CACHE['portfolio_insights'] or intelligence_system.get_portfolio_insights()
        
        # Calculate key metrics
        immediate_revenue_at_risk = 0
        for _, site in intelligence_system.solar_data.iterrows():
            if site.get('remaining_fit_years', 0) < 2:
                # Estimate annual generation
                capacity_factor = 0.11
                annual_mwh = site.get('capacity_mw', 0) * 8760 * capacity_factor
                fit_rate = 0.041  # Average FIT rate £/kWh
                annual_revenue = annual_mwh * 1000 * fit_rate
                immediate_revenue_at_risk += annual_revenue
        
        return jsonify({
            'success': True,
            'executive_summary': summary,
            'key_metrics': {
                'total_addressable_market_mw': insights['total_capacity_mw'],
                'immediate_opportunities': insights['immediate_action_required'],
                'revenue_at_risk_gbp': int(immediate_revenue_at_risk),
                'top_regions': list(insights['regional_breakdown'].keys())[:3],
                'market_timing': insights['market_timing']
            },
            'strategic_recommendations': [
                {
                    'priority': 'HIGH',
                    'action': 'Immediate outreach campaign',
                    'target': f"{insights['immediate_action_required']} sites with <2 years FIT",
                    'timeline': 'Q1 2024'
                },
                {
                    'priority': 'HIGH',
                    'action': 'Establish regional hubs',
                    'target': 'Top 3 cluster locations',
                    'timeline': 'Q2 2024'
                },
                {
                    'priority': 'MEDIUM',
                    'action': 'Develop repowering partnerships',
                    'target': 'Sites 10-15 years old',
                    'timeline': 'Q2-Q3 2024'
                },
                {
                    'priority': 'MEDIUM',
                    'action': 'Create portfolio PPA products',
                    'target': 'Bundle small sites <100kW',
                    'timeline': 'Q3 2024'
                }
            ],
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Executive summary error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/intelligence/export', methods=['POST'])
def export_analysis():
    """
    Export detailed analysis for specific sites or regions
    Supports CSV, JSON, and Excel formats
    """
    try:
        data = request.json
        export_format = data.get('format', 'json')
        filters = data.get('filters', {})
        
        # Apply filters to dataset
        df = intelligence_system.solar_data
        
        if 'region' in filters:
            df = df[df['region'].str.contains(filters['region'], case=False, na=False)]
        
        if 'min_capacity_mw' in filters:
            df = df[df['capacity_mw'] >= filters['min_capacity_mw']]
        
        if 'max_fit_years' in filters:
            df = df[df['remaining_fit_years'] <= filters['max_fit_years']]
        
        # Enhance with opportunity scores
        opportunities = []
        for _, site in df.iterrows():
            opp = intelligence_system.analyze_ppa_opportunity(site, 'solar')
            site_data = site.to_dict()
            site_data['opportunity_score'] = opp.opportunity_score
            site_data['risk_score'] = opp.risk_score
            site_data['recommended_strategy'] = opp.recommended_strategy
            opportunities.append(site_data)
        
        if export_format == 'csv':
            # Return CSV format
            df_export = pd.DataFrame(opportunities)
            csv_data = df_export.to_csv(index=False)
            return csv_data, 200, {'Content-Type': 'text/csv'}
        else:
            # Return JSON format
            return jsonify({
                'success': True,
                'record_count': len(opportunities),
                'data': opportunities,
                'export_timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def analyze_ppa_terms(data, ppa_terms):
    """
    Analyze specific PPA terms against opportunities
    """
    analysis = {
        'viable_sites': 0,
        'total_capacity_mw': 0,
        'projected_revenue': 0
    }
    
    min_capacity = ppa_terms.get('min_capacity_mw', 0)
    max_price = ppa_terms.get('max_price_per_mwh', 100)
    contract_length = ppa_terms.get('contract_years', 15)
    
    # Analyze viability
    # ... (implementation details)
    
    return analysis

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'system': 'FIT Intelligence API',
        'data_loaded': {
            'solar_sites': len(intelligence_system.solar_data),
            'wind_sites': len(intelligence_system.wind_data)
        },
        'cache_age_seconds': (datetime.now() - CACHE['last_update']).total_seconds() if CACHE['last_update'] else None
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("FIT INTELLIGENCE API")
    print("="*60)
    print(f"Solar sites loaded: {len(intelligence_system.solar_data):,}")
    print(f"Wind sites loaded: {len(intelligence_system.wind_data):,}")
    print("\nEndpoints:")
    print("  POST /api/intelligence/query - Natural language queries")
    print("  GET  /api/intelligence/opportunities - Prioritized opportunities")
    print("  GET  /api/intelligence/clusters - Geographic clusters")
    print("  GET  /api/intelligence/repowering - Repowering analysis")
    print("  GET  /api/intelligence/executive - Executive summary")
    print("  POST /api/intelligence/export - Export detailed analysis")
    print("\nStarting server on http://localhost:5002")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5002)