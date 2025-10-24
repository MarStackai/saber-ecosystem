#!/usr/bin/env python3
"""
Unified FIT Intelligence Server
Combines web interface with real ChromaDB data
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import logging
from datetime import datetime
import json
import os

# Import our real intelligence systems
from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI
from fit_chatbot import FITIntelligenceChatbot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='web')
CORS(app)

# Initialize the real intelligence systems
print("Initializing FIT Intelligence Systems...")
intelligence_api = EnhancedFITIntelligenceAPI()
chatbot = FITIntelligenceChatbot()

print(f"✓ ChromaDB loaded with {intelligence_api.collections.get('fit_licenses_nondomestic', {}).count() if 'fit_licenses_nondomestic' in intelligence_api.collections else 0:,} commercial installations")

# Serve HTML interfaces
@app.route('/')
def index():
    """Serve the main chat interface"""
    return send_from_directory('web', 'chat.html')

@app.route('/chat')
def chat_interface():
    """Serve the chat interface"""
    return send_from_directory('web', 'chat.html')

@app.route('/improved')
def improved_interface():
    """Serve the improved interface"""
    return send_from_directory('web', 'improved.html')

# API Endpoints
@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint using real ChromaDB data with session support"""
    try:
        data = request.json
        message = data.get('message', '')
        session_id = data.get('session_id', None)
        
        # Generate session ID if not provided
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            }), 400
        
        # Use the real chatbot with ChromaDB, passing session_id
        response = chatbot.chat(message, session_id=session_id)
        
        return jsonify({
            'success': True,
            'response': response.get('response', 'No response generated'),
            'data_source': 'ChromaDB',
            'records_found': response.get('data_points', 0),
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search', methods=['POST'])
def search():
    """Search for specific FIT installations"""
    try:
        data = request.json
        query = data.get('query', '')
        filters = data.get('filters', {})
        
        # Use natural language query
        results = intelligence_api.natural_language_query(
            query=query,
            max_results=20
        )
        
        if results:
            # Format results for frontend
            formatted_results = []
            
            # Add commercial results
            for result in results.get('commercial_results', [])[:10]:
                metadata = result['metadata']
                formatted_results.append({
                    'fit_id': metadata.get('site_id', metadata.get('fit_id', 'N/A')),
                    'technology': metadata.get('technology'),
                    'capacity_mw': metadata.get('capacity_mw', 0),
                    'location': metadata.get('location', metadata.get('postcode')),
                    'remaining_fit_years': metadata.get('remaining_fit_years', -1),
                    'repowering_window': metadata.get('repowering_window', 'UNKNOWN'),
                    'source': 'commercial'
                })
            
            # Add license results
            for result in results.get('license_results', [])[:10]:
                metadata = result['metadata']
                formatted_results.append({
                    'fit_id': metadata.get('fit_id', 'N/A'),
                    'technology': metadata.get('technology'),
                    'capacity_mw': metadata.get('capacity_kw', 0) / 1000,
                    'location': metadata.get('location', metadata.get('postcode')),
                    'remaining_fit_years': metadata.get('remaining_fit_years', -1),
                    'repowering_window': metadata.get('repowering_window', 'UNKNOWN'),
                    'source': 'license'
                })
            
            return jsonify({
                'success': True,
                'results': formatted_results,
                'total_found': len(formatted_results),
                'insights': results.get('combined_insights', {})
            })
        else:
            return jsonify({
                'success': True,
                'results': [],
                'total_found': 0,
                'message': 'No results found'
            })
            
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/fit/<fit_id>', methods=['GET'])
def get_fit_by_id(fit_id):
    """Get specific FIT installation by ID"""
    try:
        # Direct lookup in ChromaDB
        collection = intelligence_api.collections.get('fit_licenses_nondomestic')
        if collection:
            result = collection.get(ids=[f"fit_{fit_id}"])
            
            if result['ids']:
                metadata = result['metadatas'][0]
                return jsonify({
                    'success': True,
                    'data': {
                        'fit_id': metadata.get('fit_id'),
                        'technology': metadata.get('technology'),
                        'capacity_kw': metadata.get('capacity_kw'),
                        'capacity_mw': metadata.get('capacity_mw'),
                        'location': metadata.get('location'),
                        'postcode': metadata.get('postcode'),
                        'commissioned_date': metadata.get('commissioned_date'),
                        'remaining_fit_years': metadata.get('remaining_fit_years'),
                        'repowering_window': metadata.get('repowering_window'),
                        'installation_type': metadata.get('installation_type')
                    }
                })
        
        return jsonify({
            'success': False,
            'error': f'FIT ID {fit_id} not found'
        }), 404
        
    except Exception as e:
        logger.error(f"FIT lookup error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        stats = {
            'total_installations': 0,
            'by_technology': {},
            'by_repowering_window': {},
            'data_sources': []
        }
        
        # Get stats from ChromaDB
        for name, collection in intelligence_api.collections.items():
            count = collection.count()
            stats['data_sources'].append({
                'name': name,
                'count': count
            })
            
            if name == 'fit_licenses_nondomestic':
                stats['total_installations'] = count
                
                # Get ALL records for accurate counts (40k is manageable)
                all_records = collection.get(limit=50000)
                tech_counts = {}
                window_counts = {}
                
                for metadata in all_records['metadatas']:
                    tech = metadata.get('technology', 'Unknown')
                    tech_counts[tech] = tech_counts.get(tech, 0) + 1
                    
                    window = metadata.get('repowering_window', 'Unknown')
                    window_counts[window] = window_counts.get(window, 0) + 1
                
                # Use actual counts, not extrapolation
                stats['by_technology'] = tech_counts
                stats['by_repowering_window'] = window_counts
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'collections': list(intelligence_api.collections.keys()),
        'total_records': sum(c.count() for c in intelligence_api.collections.values())
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("UNIFIED FIT INTELLIGENCE SERVER")
    print("="*60)
    print(f"✓ ChromaDB connected with real data")
    print(f"✓ Web interface available at http://localhost:5000")
    print(f"✓ API endpoints ready")
    print("="*60)
    print("\nEndpoints:")
    print("  Web Interface: http://localhost:5000/")
    print("  Chat API: POST http://localhost:5000/api/chat")
    print("  Search API: POST http://localhost:5000/api/search")
    print("  FIT Lookup: GET http://localhost:5000/api/fit/<fit_id>")
    print("  Stats: GET http://localhost:5000/api/stats")
    print("\nTry: http://localhost:5000/api/fit/764485")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)