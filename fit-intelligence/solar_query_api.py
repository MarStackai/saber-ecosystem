#!/usr/bin/env python3
"""
Solar Query API - Backend service for AI chat to query Pinecone database
Provides real-time analysis of 35,617 commercial solar sites
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
from datetime import datetime
import os
# from pinecone import Pinecone, ServerlessSpec  # Not needed for local data
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*", allow_headers="*", methods=["GET", "POST", "OPTIONS"])  # Enable CORS for all origins

# Load the commercial solar data
def load_solar_data():
    """Load the processed commercial solar data"""
    try:
        with open('data/commercial_solar_fit.json', 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data['sites'])
        logger.info(f"Loaded {len(df):,} commercial solar sites")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Global data cache
SOLAR_DATA = load_solar_data()

@app.route('/api/query', methods=['POST'])
def query_solar_data():
    """
    Main query endpoint that handles natural language queries about solar data
    Returns detailed analytics based on the question
    """
    try:
        data = request.json
        query = data.get('query', '').lower()
        
        # Initialize response
        response = {
            'success': True,
            'query': query,
            'timestamp': datetime.now().isoformat()
        }
        
        # Parse query intent and parameters
        filters = parse_query_filters(query)
        
        # Apply filters to dataset
        filtered_df = apply_filters(SOLAR_DATA.copy(), filters)
        
        # Generate comprehensive analytics
        analytics = generate_analytics(filtered_df, filters)
        
        # Add natural language summary
        analytics['summary'] = generate_summary(analytics, filters, query)
        
        response['data'] = analytics
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def parse_query_filters(query):
    """Parse natural language query to extract filters"""
    filters = {}
    
    # Region detection
    scotland_terms = ['scotland', 'scottish', 'highland', 'aberdeenshire', 'orkney', 
                     'shetland', 'fife', 'perth', 'dundee', 'glasgow', 'edinburgh']
    if any(term in query for term in scotland_terms):
        filters['region'] = 'Scotland'
    
    # Capacity range detection
    capacity_patterns = [
        ('between 250 and 500', (250, 500)),
        ('250-500kw', (250, 500)),
        ('250 to 500', (250, 500)),
        ('500-750kw', (500, 750)),
        ('500 to 750', (500, 750)),
        ('750-1000kw', (750, 1000)),
        ('750kw to 1mw', (750, 1000)),
        ('over 1mw', (1000, float('inf'))),
        ('over 500kw', (500, float('inf'))),
        ('under 100kw', (0, 100)),
        ('below 50kw', (0, 50))
    ]
    
    for pattern, (min_kw, max_kw) in capacity_patterns:
        if pattern in query:
            filters['capacity_min'] = min_kw
            filters['capacity_max'] = max_kw
            break
    
    # Repowering window detection
    window_terms = {
        'immediate': 'IMMEDIATE',
        'urgent': 'URGENT',
        'optimal': 'OPTIMAL',
        'planning': 'PLANNING',
        'future': 'FUTURE'
    }
    
    for term, window in window_terms.items():
        if term in query:
            filters['repowering_window'] = window
            break
    
    # Age detection
    age_patterns = [
        ('older than 15', (15, float('inf'))),
        ('over 15 years', (15, float('inf'))),
        ('under 5 years', (0, 5)),
        ('between 5 and 10 years', (5, 10)),
        ('5-10 years old', (5, 10))
    ]
    
    for pattern, (min_age, max_age) in age_patterns:
        if pattern in query:
            filters['age_min'] = min_age
            filters['age_max'] = max_age
            break
    
    # FIT remaining detection
    if 'fit expiring' in query or 'fit ending' in query:
        filters['fit_max'] = 2
    elif 'fit remaining' in query:
        if 'under 5' in query:
            filters['fit_max'] = 5
        elif 'over 10' in query:
            filters['fit_min'] = 10
    
    return filters

def apply_filters(df, filters):
    """Apply parsed filters to dataframe"""
    filtered = df.copy()
    
    # Region filter
    if 'region' in filters:
        if filters['region'] == 'Scotland':
            scotland_regions = ['Scotland', 'Highland', 'Aberdeenshire', 'Orkney', 
                              'Shetland', 'Fife', 'Perth and Kinross']
            filtered = filtered[filtered['region'].str.contains('|'.join(scotland_regions), na=False)]
        else:
            filtered = filtered[filtered['region'] == filters['region']]
    
    # Capacity filter
    if 'capacity_min' in filters:
        filtered = filtered[filtered['capacity_kw'] >= filters['capacity_min']]
    if 'capacity_max' in filters:
        if filters['capacity_max'] != float('inf'):
            filtered = filtered[filtered['capacity_kw'] < filters['capacity_max']]
    
    # Repowering window filter
    if 'repowering_window' in filters:
        filtered = filtered[filtered['repowering_window'] == filters['repowering_window']]
    
    # Age filter
    if 'age_min' in filters:
        filtered = filtered[filtered['age_years'] >= filters['age_min']]
    if 'age_max' in filters:
        if filters['age_max'] != float('inf'):
            filtered = filtered[filtered['age_years'] < filters['age_max']]
    
    # FIT remaining filter
    if 'fit_min' in filters:
        filtered = filtered[filtered['remaining_fit_years'] >= filters['fit_min']]
    if 'fit_max' in filters:
        filtered = filtered[filtered['remaining_fit_years'] <= filters['fit_max']]
    
    return filtered

def generate_analytics(df, filters):
    """Generate comprehensive analytics from filtered data"""
    analytics = {
        'total_sites': len(df),
        'total_capacity_mw': df['capacity_mw'].sum() if len(df) > 0 else 0,
        'filters_applied': filters
    }
    
    if len(df) == 0:
        return analytics
    
    # Basic stats
    analytics['statistics'] = {
        'average_capacity_kw': df['capacity_kw'].mean(),
        'median_capacity_kw': df['capacity_kw'].median(),
        'average_age_years': df['age_years'].mean(),
        'average_fit_remaining': df['remaining_fit_years'].mean(),
        'total_annual_generation_mwh': df['annual_generation_mwh'].sum()
    }
    
    # Capacity breakdown
    capacity_ranges = [
        (0, 50, '0-50kW'),
        (50, 100, '50-100kW'),
        (100, 250, '100-250kW'),
        (250, 500, '250-500kW'),
        (500, 750, '500-750kW'),
        (750, 1000, '750-1000kW'),
        (1000, float('inf'), '1000kW+')
    ]
    
    analytics['by_capacity'] = {}
    for min_kw, max_kw, label in capacity_ranges:
        mask = (df['capacity_kw'] >= min_kw) & (df['capacity_kw'] < max_kw)
        subset = df[mask]
        analytics['by_capacity'][label] = {
            'count': len(subset),
            'total_capacity_mw': subset['capacity_mw'].sum(),
            'percentage': (len(subset) / len(df) * 100) if len(df) > 0 else 0
        }
    
    # Regional breakdown
    analytics['by_region'] = {}
    for region in df['region'].unique():
        subset = df[df['region'] == region]
        analytics['by_region'][region] = {
            'count': len(subset),
            'total_capacity_mw': subset['capacity_mw'].sum(),
            'average_capacity_kw': subset['capacity_kw'].mean(),
            'percentage': (len(subset) / len(df) * 100)
        }
    
    # Sort regions by count
    analytics['by_region'] = dict(sorted(
        analytics['by_region'].items(), 
        key=lambda x: x[1]['count'], 
        reverse=True
    )[:10])  # Top 10 regions
    
    # Repowering windows
    analytics['by_repowering_window'] = {}
    for window in df['repowering_window'].unique():
        subset = df[df['repowering_window'] == window]
        analytics['by_repowering_window'][window] = {
            'count': len(subset),
            'total_capacity_mw': subset['capacity_mw'].sum(),
            'percentage': (len(subset) / len(df) * 100)
        }
    
    # Top postcodes
    postcode_counts = df.groupby('postcode').agg({
        'capacity_mw': 'sum',
        'capacity_kw': 'count'
    }).rename(columns={'capacity_kw': 'count'})
    
    top_postcodes = postcode_counts.nlargest(10, 'count')
    analytics['top_postcodes'] = {
        idx: {'count': row['count'], 'capacity_mw': row['capacity_mw']}
        for idx, row in top_postcodes.iterrows()
    }
    
    return analytics

def generate_summary(analytics, filters, query):
    """Generate natural language summary of results"""
    total = analytics['total_sites']
    capacity = analytics.get('total_capacity_mw', 0)
    
    # Build filter description
    filter_desc = []
    if 'region' in filters:
        filter_desc.append(f"in {filters['region']}")
    if 'capacity_min' in filters and 'capacity_max' in filters:
        if filters['capacity_max'] == float('inf'):
            filter_desc.append(f"over {filters['capacity_min']}kW")
        else:
            filter_desc.append(f"between {filters['capacity_min']}-{filters['capacity_max']}kW")
    if 'repowering_window' in filters:
        filter_desc.append(f"with {filters['repowering_window']} repowering window")
    if 'age_min' in filters or 'age_max' in filters:
        if 'age_min' in filters and 'age_max' in filters:
            filter_desc.append(f"aged {filters['age_min']}-{filters['age_max']} years")
        elif 'age_min' in filters:
            filter_desc.append(f"over {filters['age_min']} years old")
        else:
            filter_desc.append(f"under {filters['age_max']} years old")
    
    filter_text = " ".join(filter_desc) if filter_desc else "across all UK"
    
    summary = f"Found {total:,} commercial solar sites {filter_text} "
    summary += f"with total capacity of {capacity:.1f} MW."
    
    if total > 0 and 'statistics' in analytics:
        stats = analytics['statistics']
        summary += f"\n\nAverage capacity: {stats['average_capacity_kw']:.1f}kW"
        summary += f"\nAverage age: {stats['average_age_years']:.1f} years"
        summary += f"\nAverage FIT remaining: {stats['average_fit_remaining']:.1f} years"
        summary += f"\nTotal annual generation: {stats['total_annual_generation_mwh']:.0f} MWh"
    
    return summary

@app.route('/api/stats', methods=['GET'])
def get_overall_stats():
    """Get overall dataset statistics"""
    return jsonify({
        'total_sites': len(SOLAR_DATA),
        'total_capacity_mw': SOLAR_DATA['capacity_mw'].sum(),
        'regions': SOLAR_DATA['region'].nunique(),
        'average_capacity_kw': SOLAR_DATA['capacity_kw'].mean(),
        'data_timestamp': SOLAR_DATA.iloc[0].get('timestamp', 'Unknown') if len(SOLAR_DATA) > 0 else None
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'data_loaded': len(SOLAR_DATA) > 0,
        'sites_count': len(SOLAR_DATA)
    })

@app.route('/api/geojson', methods=['GET'])
def get_solar_geojson():
    """Get all solar sites as GeoJSON for map display"""
    features = []
    
    color_map = {
        'IMMEDIATE': '#E74C3C',
        'URGENT': '#F39C12',
        'OPTIMAL': '#7CC061',
        'PLANNING': '#0A5F8E',
        'FUTURE': '#95D47E'
    }
    
    for _, site in SOLAR_DATA.iterrows():
        # Skip sites with invalid coordinates
        if pd.notna(site['latitude']) and pd.notna(site['longitude']):
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(site['longitude']), float(site['latitude'])]
                },
                "properties": {
                    "postcode": str(site.get('postcode', 'Unknown')),
                    "capacity_kw": float(site['capacity_kw']),
                    "capacity_mw": float(site['capacity_mw']),
                    "age_years": float(site['age_years']),
                    "remaining_fit_years": float(site['remaining_fit_years']),
                    "region": str(site['region']),
                    "size_category": str(site['size_category']),
                    "repowering_window": str(site['repowering_window']),
                    "annual_generation_mwh": float(site['annual_generation_mwh']),
                    "color": color_map.get(site['repowering_window'], '#999999')
                }
            }
            features.append(feature)
    
    return jsonify({
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "total_sites": len(features),
            "generated": datetime.now().isoformat()
        }
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("SOLAR QUERY API SERVER")
    print("="*60)
    print(f"Loaded {len(SOLAR_DATA):,} commercial solar sites")
    print("\nEndpoints:")
    print("  POST /api/query - Natural language queries")
    print("  GET  /api/stats - Overall statistics")
    print("  GET  /api/health - Health check")
    print("\nStarting server on http://localhost:5001")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5001)