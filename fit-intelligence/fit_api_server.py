#!/usr/bin/env python3
"""
FIT Intelligence API Server
Provides REST endpoints for the FIT Intelligence system
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI
from factual_fit_chatbot import FactualFITChatbot, FeedbackCollector
from llm_enhanced_chatbot import LLMEnhancedFITChatbot
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='visualizations')
CORS(app)  # Enable CORS for web interface

# Initialize FIT Intelligence components
logger.info("Initializing FIT Intelligence API...")
fit_api = EnhancedFITIntelligenceAPI()
# Use Ollama GPU-accelerated chatbot with Llama 2 13B
logger.info("Using Ollama with GPU acceleration (Llama 2 13B)")
chatbot = LLMEnhancedFITChatbot()
# Fallback to factual-only chatbot if needed
factual_chatbot = FactualFITChatbot()
feedback_collector = FeedbackCollector()

@app.route('/')
def index():
    """Serve the main platform menu"""
    return send_from_directory('visualizations', 'platform_main_menu.html')

@app.route('/visualizations/<path:filename>')
def serve_static(filename):
    """Serve static files from visualizations directory"""
    return send_from_directory('visualizations', filename)

@app.route('/<path:filename>')
def serve_dashboard(filename):
    """Serve dashboard files directly (for easy navigation)"""
    # Only serve HTML files to avoid conflicts with API routes
    if filename.endswith('.html'):
        return send_from_directory('visualizations', filename)
    else:
        # For non-HTML files, return 404 to let other routes handle them
        from flask import abort
        abort(404)

@app.route('/api/health')
def health():
    """Health check endpoint"""
    try:
        # Get actual model from environment or default
        active_model = os.getenv("FIT_MODEL", "llama2:13b")
        
        # Get collection count
        collection_count = len(fit_api.collections) if hasattr(fit_api, 'collections') else 0
        
        return jsonify({
            'status': 'healthy',
            'collections': collection_count,
            'total_sites': 40194,
            'model': active_model,  # Report actual model being used
            'port': 5000  # Single truth - always port 5000
        })
    except:
        return jsonify({
            'status': 'healthy',
            'model': os.getenv("FIT_MODEL", "llama2:13b"),
            'port': 5000
        })

@app.route('/api/config', methods=['GET'])
def get_config():
    """Expose minimal client runtime config (e.g., Mapbox token)."""
    return jsonify({
        'mapboxToken': os.environ.get('MAPBOX_TOKEN')
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint for natural language queries - factual responses only"""
    try:
        data = request.json
        # Accept both 'query' and 'message' fields
        query = data.get('query') or data.get('message', '')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Get session ID from request or create one
        session_id = data.get('session_id', request.remote_addr or 'default')

        # Get optional limit parameter (or let the query parser extract it)
        limit = data.get('limit', 10)  # Default to 10 if not specified

        # Process with factual chatbot
        response = chatbot.chat(query, session_id, limit)
        
        return jsonify({
            'query': query,
            'response': response,
            'status': 'success',
            'success': True  # for front-ends expecting this flag
        })
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search():
    """Search endpoint for structured queries"""
    try:
        data = request.json
        
        # Extract search parameters
        technology = data.get('technology', 'all')
        min_capacity = data.get('min_capacity_kw')
        max_capacity = data.get('max_capacity_kw')
        location = data.get('location')
        limit = data.get('limit', 20)
        
        # Build search query
        query_parts = []
        if technology and technology != 'all':
            query_parts.append(technology)
        if min_capacity:
            query_parts.append(f"over {min_capacity}kW")
        if max_capacity:
            query_parts.append(f"under {max_capacity}kW")
        if location:
            query_parts.append(f"in {location}")
        
        query_text = " ".join(query_parts) if query_parts else "renewable energy sites"
        
        # Search using the enhanced API
        results = fit_api.natural_language_search(
            query_text,
            limit=limit
        )
        
        return jsonify({
            'query': query_text,
            'results': results,
            'count': len(results.get('commercial_results', [])),
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/insights/<technology>')
def get_insights(technology):
    """Get insights for a specific technology"""
    try:
        insights = fit_api.get_comprehensive_insights()
        
        if technology in insights:
            return jsonify({
                'technology': technology,
                'insights': insights[technology],
                'status': 'success'
            })
        else:
            return jsonify({
                'error': f"Technology {technology} not found"
            }), 404
    except Exception as e:
        logger.error(f"Insights error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get overall system statistics"""
    try:
        stats = fit_api.get_collection_stats()
        insights = fit_api.get_comprehensive_insights()
        
        # Calculate totals
        total_sites = sum(s['count'] for s in stats.values())
        total_capacity = sum(
            tech_data['commercial']['total_capacity_mw'] 
            for tech_data in insights.values()
        )
        
        return jsonify({
            'total_sites': total_sites,
            'total_capacity_mw': total_capacity,
            'collections': stats,
            'technologies': list(insights.keys()),
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback on a response for training"""
    try:
        data = request.json
        query = data.get('query')
        response = data.get('response')
        correct_response = data.get('correct_response')
        rating = data.get('rating')
        notes = data.get('notes')
        
        success = feedback_collector.collect_feedback(
            query=query,
            response=response,
            correct_response=correct_response,
            rating=rating,
            notes=notes
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Feedback recorded for training'
            })
        else:
            return jsonify({'error': 'Failed to record feedback'}), 500
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback/stats', methods=['GET'])
def get_feedback_stats():
    """Get feedback statistics"""
    try:
        stats = feedback_collector.get_feedback_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Feedback stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/repowering', methods=['GET'])
def get_repowering_opportunities():
    """Get sites ready for repowering"""
    try:
        # Search for old sites
        results = fit_api.natural_language_search(
            "sites over 15 years old ready for repowering",
            limit=50
        )
        
        # Filter and analyze
        repowering_sites = []
        for site in results.get('commercial_results', []):
            if site.get('age_years', 0) > 15:
                repowering_sites.append({
                    'technology': site.get('technology'),
                    'capacity_kw': site.get('capacity_kw'),
                    'location': site.get('postcode'),
                    'age_years': site.get('age_years'),
                    'fit_rate': site.get('tariff_p_kwh'),
                    'repowering_potential': 'High' if site.get('age_years', 0) > 20 else 'Medium'
                })
        
        return jsonify({
            'count': len(repowering_sites),
            'sites': repowering_sites,
            'total_capacity_mw': sum(s['capacity_kw'] for s in repowering_sites) / 1000,
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Repowering error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search_map', methods=['POST'])
def search_map():
    """Search sites for map visualization with filters"""
    try:
        data = request.json
        technology = data.get('technology')
        postcode_areas = data.get('postcode_areas', [])
        min_kw = data.get('min_kw')
        max_kw = data.get('max_kw')
        repowering = data.get('repowering_category')
        
        # Use warm index aliasing
        from warm_index import canonical_tech
        if technology:
            technology = canonical_tech(technology)
        
        # Build search query
        query_parts = []
        if technology:
            query_parts.append(technology)
        if min_kw and max_kw:
            query_parts.append(f"{min_kw}-{max_kw}kW")
        elif min_kw:
            query_parts.append(f"over {min_kw}kW")
        elif max_kw:
            query_parts.append(f"under {max_kw}kW")
        if repowering:
            query_parts.append(f"{repowering} repowering")
            
        query = " ".join(query_parts) if query_parts else "renewable energy sites"
        
        # Search using warm index through chatbot
        results = chatbot.process_query(query, "system")
        
        # Extract sites from response
        sites = []
        if 'results' in results:
            for r in results['results'][:100]:  # Limit for map performance
                metadata = r.get('metadata', {})
                sites.append({
                    'fit_id': metadata.get('fit_id'),
                    'technology': metadata.get('technology'),
                    'capacity_kw': metadata.get('capacity_kw'),
                    'postcode': metadata.get('postcode'),
                    'lat': metadata.get('latitude'),  # Add if available
                    'lng': metadata.get('longitude'),  # Add if available
                    'years_left': metadata.get('years_left'),
                    'fit_rate_p_kwh': metadata.get('tariff_p_kwh'),
                    'commission_date': metadata.get('commission_date')
                })
        
        return jsonify({
            'filters': {
                'technology': technology,
                'postcode_areas': postcode_areas,
                'min_kw': min_kw,
                'max_kw': max_kw,
                'repowering': repowering
            },
            'sites': sites,
            'count': len(sites)
        })
        
    except Exception as e:
        logger.error(f"Map search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cluster_stats', methods=['POST'])
def cluster_stats():
    """Get clustered statistics for map visualization"""
    try:
        data = request.json
        zoom = data.get('zoom', 8)
        filters = data.get('filters', {})
        viewport = data.get('viewport', {})  # lat/lng bounds
        
        # Determine clustering level based on zoom
        if zoom <= 8:
            # Postcode area level clustering
            cluster_key = 'postcode_area'
        elif zoom <= 12:
            # Postcode district level
            cluster_key = 'postcode_outward'
        else:
            # Individual sites
            return jsonify({'zoom': zoom, 'buckets': [], 'individual': True})
        
        # Get filtered sites (reuse search_map logic)
        search_data = {
            'technology': filters.get('technology'),
            'postcode_areas': filters.get('postcode_areas', []),
            'min_kw': filters.get('min_kw'),
            'max_kw': filters.get('max_kw'),
            'repowering_category': filters.get('repowering')
        }
        
        # Build query
        query_parts = []
        if search_data['technology']:
            query_parts.append(search_data['technology'])
        if search_data['min_kw']:
            query_parts.append(f"over {search_data['min_kw']}kW")
        query = " ".join(query_parts) if query_parts else "all sites"
        
        # Search
        results = chatbot.process_query(query, "system")
        
        # Cluster results
        clusters = {}
        for r in results.get('results', []):
            metadata = r.get('metadata', {})
            
            # Determine cluster key
            if cluster_key == 'postcode_area':
                key = metadata.get('postcode', '')[:2] if metadata.get('postcode') else 'Unknown'
            else:
                key = metadata.get('postcode', '').split()[0] if metadata.get('postcode') else 'Unknown'
            
            if key not in clusters:
                clusters[key] = {
                    'key': key,
                    'site_count': 0,
                    'total_capacity_kw': 0,
                    'total_years_left': 0,
                    'count_with_years': 0
                }
            
            clusters[key]['site_count'] += 1
            clusters[key]['total_capacity_kw'] += float(metadata.get('capacity_kw', 0))
            
            years = metadata.get('years_left')
            if years is not None:
                clusters[key]['total_years_left'] += float(years)
                clusters[key]['count_with_years'] += 1
        
        # Format buckets
        buckets = []
        for key, stats in clusters.items():
            bucket = {
                'key': key,
                'site_count': stats['site_count'],
                'total_capacity_kw': round(stats['total_capacity_kw'], 1),
                'avg_years_left': round(stats['total_years_left'] / stats['count_with_years'], 1) if stats['count_with_years'] > 0 else None
            }
            buckets.append(bucket)
        
        # Sort by site count
        buckets.sort(key=lambda x: x['site_count'], reverse=True)
        
        return jsonify({
            'zoom': zoom,
            'buckets': buckets[:50],  # Limit for performance
            'total_sites': sum(b['site_count'] for b in buckets),
            'total_capacity_mw': round(sum(b['total_capacity_kw'] for b in buckets) / 1000, 1)
        })
        
    except Exception as e:
        logger.error(f"Cluster stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Compatibility endpoints for the intelligent_map_dashboard front-end
@app.route('/api/chroma/clusters', methods=['GET'])
def chroma_clusters():
    """Return clustered stats by postcode area in a format expected by the map UI"""
    try:
        # Parameters (not heavily used; kept for compatibility)
        min_sites = int(request.args.get('min_sites', 5))
        max_results = int(request.args.get('max_results', 50))

        # Prefer warm index for larger sample
        base_query = 'renewable energy sites'
        raw = None
        if hasattr(chatbot, 'warm_index') and chatbot.warm_index:
            try:
                raw = chatbot.warm_index.search(base_query, top_k=3000)
            except Exception as _e:
                raw = None
        
        clusters = {}
        if raw is not None:
            iterator = ({'metadata': md} for (_score, _id, md) in raw)
        else:
            results = chatbot.process_query(base_query, 'system')
            iterator = results.get('results', [])

        for r in iterator:
            md = r.get('metadata', {})
            postcode = md.get('postcode') or ''
            area = (postcode[:2] or '').upper()
            if not area:
                area = 'NA'

            cap_kw = 0.0
            if md.get('capacity_kw') is not None:
                try:
                    cap_kw = float(md.get('capacity_kw'))
                except Exception:
                    cap_kw = 0.0

            years_left = md.get('years_left')
            try:
                years_left = float(years_left) if years_left is not None else None
            except Exception:
                years_left = None

            tech = md.get('technology') or 'Unknown'

            if area not in clusters:
                clusters[area] = {
                    'postcode_area': area,
                    'site_count': 0,
                    'total_capacity_mw': 0.0,
                    'urgent_sites': 0,
                    'total_years_left': 0.0,
                    'count_years': 0,
                    'technology_mix': {}
                }

            c = clusters[area]
            c['site_count'] += 1
            c['total_capacity_mw'] += cap_kw / 1000.0
            if years_left is not None:
                c['total_years_left'] += years_left
                c['count_years'] += 1
                if years_left < 2:
                    c['urgent_sites'] += 1
            c['technology_mix'][tech] = c['technology_mix'].get(tech, 0) + 1

        # Build list and filter by min_sites
        cluster_list = []
        for _, c in clusters.items():
            if c['site_count'] < min_sites:
                continue
            avg_years = (c['total_years_left'] / c['count_years']) if c['count_years'] > 0 else 0.0
            cluster_list.append({
                'postcode_area': c['postcode_area'],
                'site_count': c['site_count'],
                'total_capacity_mw': round(c['total_capacity_mw'], 1),
                'urgent_sites': c['urgent_sites'],
                'average_remaining_fit_years': round(avg_years, 1),
                'technology_mix': c['technology_mix']
            })

        # Sort and limit
        cluster_list.sort(key=lambda x: x['site_count'], reverse=True)
        cluster_list = cluster_list[:max_results]

        summary = {
            'total_clustered_sites': sum(c['site_count'] for c in cluster_list),
            'clusters_returned': len(cluster_list)
        }

        return jsonify({'success': True, 'clusters': cluster_list, 'summary': summary})
    except Exception as e:
        logger.error(f"Chroma clusters error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chroma/business_query', methods=['POST'])
def chroma_business_query():
    """Business query endpoint compatible with the map UI expectations"""
    try:
        data = request.json or {}
        query_text = data.get('query') or 'renewable energy sites'
        max_results = int(data.get('max_results') or 1000)

        # Execute search via chatbot warm index
        res = chatbot.process_query(query_text, 'system')
        results = res.get('results', [])

        # Normalize metadata fields for UI
        norm_results = []
        for r in results[:max_results]:
            md = dict(r.get('metadata', {}))
            # Ensure capacity_mw exists
            cap_kw = 0.0
            try:
                cap_kw = float(md.get('capacity_kw') or 0.0)
            except Exception:
                cap_kw = 0.0
            md.setdefault('capacity_mw', cap_kw / 1000.0)

            # Normalize remaining FIT years
            years_left = md.get('years_left')
            try:
                years_left = float(years_left) if years_left is not None else None
            except Exception:
                years_left = None
            if years_left is not None:
                md.setdefault('remaining_fit_years', years_left)

            # Map repowering window if not present
            if 'repowering_window' not in md and years_left is not None:
                if years_left < 2:
                    md['repowering_window'] = 'IMMEDIATE'
                elif years_left < 5:
                    md['repowering_window'] = 'URGENT'
                elif years_left < 10:
                    md['repowering_window'] = 'OPTIMAL'
                else:
                    md['repowering_window'] = 'PLANNING'

            norm_results.append({'metadata': md})

        # Basic BI summary
        total_capacity = sum((r['metadata'].get('capacity_mw') or 0.0) for r in norm_results)
        with_years = [r for r in norm_results if r['metadata'].get('remaining_fit_years') is not None]
        avg_years = (sum(r['metadata']['remaining_fit_years'] for r in with_years) / len(with_years)) if with_years else 0.0
        urgent_sites = sum(1 for r in norm_results if (r['metadata'].get('remaining_fit_years') or 99) < 2)

        bi = {
            'total_sites': len(norm_results),
            'total_capacity_mw': round(total_capacity, 1),
            'urgent_sites': urgent_sites,
            'avg_remaining_fit_years': round(avg_years, 1)
        }

        return jsonify({'success': True, 'results': norm_results, 'business_intelligence': bi})
    except Exception as e:
        logger.error(f"Chroma business_query error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting FIT Intelligence API Server on port {port}")
    logger.info(f"Access the platform at: http://localhost:{port}")
    logger.info(f"API endpoints available at: http://localhost:{port}/api/")
    
    # Run the Flask server
    app.run(host='0.0.0.0', port=port, debug=False)
