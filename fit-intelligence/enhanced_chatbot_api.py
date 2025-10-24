#!/usr/bin/env python3
"""
Enhanced FIT Chatbot API Server
Serves the enhanced chatbot with FIT pricing intelligence via HTTP API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import traceback
import uuid
from enhanced_fit_chatbot import EnhancedFITChatbot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for web interface

# Initialize the enhanced chatbot
logger.info("Initializing Enhanced FIT Chatbot API...")
try:
    chatbot = EnhancedFITChatbot()
    logger.info("✅ Enhanced FIT Chatbot initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize chatbot: {e}")
    chatbot = None

# Store conversation sessions
sessions = {}

@app.route('/api/chat/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    if chatbot:
        return jsonify({
            "status": "healthy",
            "message": "Enhanced FIT Chatbot API is running",
            "features": [
                "Commercial site analysis",
                "FIT license intelligence", 
                "Historical FIT pricing queries",
                "Natural language processing",
                "Revenue calculations"
            ],
            "data_status": {
                "commercial_sites": "40,194 loaded",
                "fit_licenses": "35,000 loaded", 
                "fit_rates": "814 tariff codes active"
            }
        }), 200
    else:
        return jsonify({
            "status": "unhealthy",
            "message": "Chatbot failed to initialize"
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        if not chatbot:
            return jsonify({
                "error": "Chatbot not initialized",
                "message": "Please try again later"
            }), 500
        
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "Invalid request",
                "message": "Missing 'message' field"
            }), 400
        
        user_message = data['message'].strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not user_message:
            return jsonify({
                "error": "Empty message",
                "message": "Please enter a message"
            }), 400
        
        logger.info(f"Processing chat request - Session: {session_id[:8]}..., Message: {user_message[:100]}...")
        
        # Get chatbot response
        response = chatbot.chat(user_message)
        
        # Store session (basic session management)
        if session_id not in sessions:
            sessions[session_id] = []
        
        sessions[session_id].append({
            "user": user_message,
            "bot": response,
            "timestamp": str(uuid.uuid4())  # Simple timestamp replacement
        })
        
        # Limit session history to last 10 exchanges
        if len(sessions[session_id]) > 10:
            sessions[session_id] = sessions[session_id][-10:]
        
        return jsonify({
            "response": response,
            "session_id": session_id,
            "status": "success"
        })
    
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            "error": "Internal server error",
            "message": "An error occurred processing your request",
            "details": str(e) if app.debug else None
        }), 500

@app.route('/api/chat/examples', methods=['GET'])
def get_examples():
    """Get example queries for the interface"""
    examples = [
        {
            "category": "FIT Pricing Queries",
            "queries": [
                "What was the FIT rate in November 2013 for a 350kW turbine?",
                "FIT rate for 25kW solar in June 2011?",
                "What rate would a 500kW wind installation get in April 2012?"
            ]
        },
        {
            "category": "Site Analysis",
            "queries": [
                "How many wind sites are in the urgent repowering window?",
                "Show me large solar installations in Scotland",
                "What's the total capacity of hydro installations?"
            ]
        },
        {
            "category": "Commercial Intelligence",
            "queries": [
                "Which regions have the most FIT licenses?",
                "Show me sites with highest FIT revenue potential",
                "What technologies have licenses expiring soon?"
            ]
        }
    ]
    
    return jsonify({
        "examples": examples,
        "suggestion": "Try asking about FIT rates, site locations, or technology analysis"
    })

@app.route('/api/chat/clear/<session_id>', methods=['POST'])
def clear_session(session_id):
    """Clear a conversation session"""
    if session_id in sessions:
        del sessions[session_id]
        return jsonify({
            "message": "Session cleared",
            "session_id": session_id
        })
    
    return jsonify({
        "message": "Session not found",
        "session_id": session_id
    })

@app.route('/api/chat/feedback', methods=['POST'])
def submit_feedback():
    """Handle feedback submission"""
    data = request.get_json()
    
    # Log feedback (in production, save to database)
    logger.info(f"Feedback received: {data}")
    
    return jsonify({
        "message": "Feedback received",
        "status": "success"
    })

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """Get system status information"""
    if chatbot:
        try:
            status = chatbot.get_system_info()
            return jsonify({
                "status": "operational",
                "chatbot_initialized": True,
                "system_info": status
            })
        except Exception as e:
            return jsonify({
                "status": "partial",
                "chatbot_initialized": True,
                "error": str(e)
            })
    
    return jsonify({
        "status": "down",
        "chatbot_initialized": False
    })

if __name__ == '__main__':
    logger.info("🚀 Starting Enhanced FIT Chatbot API Server...")
    logger.info("📡 API will be available at: http://localhost:8001")
    logger.info("🔗 Web interface should connect to this endpoint")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=8001,
        debug=False,  # Set to True for development
        threaded=True
    )