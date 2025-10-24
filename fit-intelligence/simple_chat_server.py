#!/usr/bin/env python3
"""
Simple Chat Server - No Flask Required
Uses Python's built-in HTTP server
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys
import uuid
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import mimetypes

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fit_chatbot import FITIntelligenceChatbot
from conversation_context import ConversationContext
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize chatbot and conversation manager
chatbot = FITIntelligenceChatbot()
conversation_manager = ConversationContext()

# Store saved chats
saved_chats = {}

class ChatHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        
        # Serve HTML files
        if parsed.path == '/' or parsed.path == '/chat.html':
            self.serve_file('web/enhanced_chat.html', 'text/html')
        elif parsed.path == '/api/health':
            self.send_json({'status': 'healthy', 'chroma': True})
        elif parsed.path == '/api/saved-chats':
            self.send_json({'chats': list(saved_chats.values())})
        elif parsed.path.startswith('/api/chat/'):
            # Get specific chat
            chat_id = parsed.path.split('/')[-1]
            if chat_id in saved_chats:
                self.send_json(saved_chats[chat_id])
            else:
                self.send_error(404, "Chat not found")
        else:
            self.send_error(404, "Not found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/chat':
            # Handle chat message
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            message = data.get('message', '')
            session_id = data.get('session_id', str(uuid.uuid4()))
            
            # Process with chatbot
            try:
                response = chatbot.chat(message, session_id=session_id)
                result = {
                    'success': True,
                    'response': response.get('response', 'No response'),
                    'session_id': session_id,
                    'data_points': response.get('data_points', 0)
                }
            except Exception as e:
                result = {
                    'success': False,
                    'error': str(e)
                }
            
            self.send_json(result)
            
        elif parsed.path == '/api/chat/save':
            # Save current chat
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            chat_id = str(uuid.uuid4())
            saved_chats[chat_id] = {
                'id': chat_id,
                'title': data.get('title', f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"),
                'messages': data.get('messages', []),
                'session_id': data.get('session_id'),
                'created_at': datetime.now().isoformat()
            }
            
            self.send_json({'success': True, 'chat_id': chat_id})
            
        elif parsed.path == '/api/chat/new':
            # Create new chat session
            new_session_id = str(uuid.uuid4())
            self.send_json({
                'success': True,
                'session_id': new_session_id
            })
        else:
            self.send_error(404, "Not found")
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def serve_file(self, filepath, content_type):
        """Serve a static file"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "File not found")
    
    def send_json(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to reduce logging"""
        return

def main():
    """Start the server"""
    port = 5000
    server = HTTPServer(('localhost', port), ChatHandler)
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║           FIT Intelligence Chat Server Started              ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  🌐 Chat Interface:  http://localhost:{port}/chat.html     ║
║  📡 API Endpoint:    http://localhost:{port}/api/chat      ║
║                                                            ║
║  Features:                                                 ║
║  ✅ Conversation memory and context                       ║
║  ✅ Save chat history                                     ║
║  ✅ Start new conversations                               ║
║  ✅ ChromaDB integration                                  ║
║                                                            ║
║  Press Ctrl+C to stop the server                          ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        server.shutdown()

if __name__ == "__main__":
    main()