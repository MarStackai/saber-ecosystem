#!/usr/bin/env python3
"""
Minimal Chat Server with Mock Responses
Works without any external dependencies
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import uuid
from datetime import datetime
from urllib.parse import urlparse

# Store saved chats and sessions in memory
saved_chats = {}
sessions = {}

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
            
            # Get or create session context
            if session_id not in sessions:
                sessions[session_id] = {
                    'location': None,
                    'capacity': None,
                    'technology': None,
                    'history': []
                }
            
            context = sessions[session_id]
            context['history'].append(message)
            
            # Generate contextual response
            response = self.generate_contextual_response(message, context)
            
            result = {
                'success': True,
                'response': response,
                'session_id': session_id,
                'data_points': 42  # Mock data points
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
            sessions[new_session_id] = {
                'location': None,
                'capacity': None,
                'technology': None,
                'history': []
            }
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
    
    def generate_details_response(self, context):
        """Generate detailed response based on context"""
        cap = context.get('capacity', 100)
        loc = context.get('location', 'the area')
        tech = context.get('technology', None)
        
        # Get appropriate postcodes for the location
        location_postcodes = {
            'Yorkshire': ['YO', 'HU', 'DN', 'HD', 'LS', 'BD', 'WF'],
            'Berkshire': ['RG', 'SL'],
            'Ryedale': ['YO17', 'YO18'],
            'Cornwall': ['TR', 'PL', 'EX'],
            'Devon': ['EX', 'TQ', 'PL'],
            'Scotland': ['AB', 'DD', 'DG', 'EH', 'FK', 'G', 'HS', 'IV', 'KA', 'KW', 'KY', 'ML', 'PA', 'PH', 'TD', 'ZE']
        }
        
        postcodes = location_postcodes.get(loc, ['XX'])[0:2]  # Get first 2 postcodes for the area
        
        installations_html = []
        
        if tech == 'Wind':
            # Show only wind installations with correct postcodes
            installations_html = [
                f"""<div style="background: #f0f4ff; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <h4>💨 FIT_12345 - Wind Turbine Installation</h4>
                    <ul>
                        <li><strong>Capacity:</strong> {cap}kW</li>
                        <li><strong>Location:</strong> {loc}, {postcodes[0]}7 5AB</li>
                        <li><strong>Site Name:</strong> Greenfield Wind Farm</li>
                        <li><strong>Commissioned:</strong> March 15, 2015</li>
                        <li><strong>FIT Rate:</strong> 13.73p/kWh</li>
                        <li><strong>Remaining FIT Years:</strong> 6 years</li>
                        <li><strong>Annual Generation:</strong> ~250,000 kWh</li>
                        <li><strong>CO2 Saved:</strong> 125 tonnes/year</li>
                    </ul>
                </div>""",
                f"""<div style="background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <h4>💨 FIT_12347 - Wind Farm</h4>
                    <ul>
                        <li><strong>Capacity:</strong> {cap+10}kW</li>
                        <li><strong>Location:</strong> {loc}, {postcodes[0]}20 8TY</li>
                        <li><strong>Site Name:</strong> Hilltop Renewables</li>
                        <li><strong>Commissioned:</strong> November 3, 2014</li>
                        <li><strong>FIT Rate:</strong> 15.44p/kWh</li>
                        <li><strong>Remaining FIT Years:</strong> 5 years</li>
                        <li><strong>Annual Generation:</strong> ~275,000 kWh</li>
                        <li><strong>CO2 Saved:</strong> 137 tonnes/year</li>
                    </ul>
                </div>""",
                f"""<div style="background: #dcedc8; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <h4>🌬️ FIT_12348 - Wind Installation</h4>
                    <ul>
                        <li><strong>Capacity:</strong> {cap+25}kW</li>
                        <li><strong>Location:</strong> {loc}, {postcodes[1] if len(postcodes) > 1 else postcodes[0]}18 9XZ</li>
                        <li><strong>Site Name:</strong> Valley Wind Power</li>
                        <li><strong>Commissioned:</strong> September 8, 2016</li>
                        <li><strong>FIT Rate:</strong> 8.61p/kWh</li>
                        <li><strong>Remaining FIT Years:</strong> 7 years</li>
                        <li><strong>Annual Generation:</strong> ~312,000 kWh</li>
                        <li><strong>CO2 Saved:</strong> 156 tonnes/year</li>
                    </ul>
                </div>"""
            ]
        elif tech == 'Photovoltaic':
            # Show only solar installations with correct postcodes
            installations_html = [
                f"""<div style="background: #fff8e1; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <h4>☀️ FIT_12346 - Solar Farm</h4>
                    <ul>
                        <li><strong>Capacity:</strong> {cap-5}kW</li>
                        <li><strong>Location:</strong> {loc}, {postcodes[0]}14 2NP</li>
                        <li><strong>Site Name:</strong> Sunny Meadows Solar</li>
                        <li><strong>Commissioned:</strong> July 22, 2016</li>
                        <li><strong>FIT Rate:</strong> 4.39p/kWh</li>
                        <li><strong>Remaining FIT Years:</strong> 7 years</li>
                        <li><strong>Annual Generation:</strong> ~295,000 kWh</li>
                        <li><strong>CO2 Saved:</strong> 147 tonnes/year</li>
                    </ul>
                </div>""",
                f"""<div style="background: #fffde7; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <h4>☀️ FIT_12349 - Solar Array</h4>
                    <ul>
                        <li><strong>Capacity:</strong> {cap}kW</li>
                        <li><strong>Location:</strong> {loc}, {postcodes[0]}16 7TH</li>
                        <li><strong>Site Name:</strong> {loc} Solar Co</li>
                        <li><strong>Commissioned:</strong> April 12, 2017</li>
                        <li><strong>FIT Rate:</strong> 4.11p/kWh</li>
                        <li><strong>Remaining FIT Years:</strong> 8 years</li>
                        <li><strong>Annual Generation:</strong> ~300,000 kWh</li>
                        <li><strong>CO2 Saved:</strong> 150 tonnes/year</li>
                    </ul>
                </div>""",
                f"""<div style="background: #fff3e0; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <h4>☀️ FIT_12350 - Photovoltaic Plant</h4>
                    <ul>
                        <li><strong>Capacity:</strong> {cap+15}kW</li>
                        <li><strong>Location:</strong> {loc}, {postcodes[1] if len(postcodes) > 1 else postcodes[0]}22 4QR</li>
                        <li><strong>Site Name:</strong> Northern Solar Systems</li>
                        <li><strong>Commissioned:</strong> December 1, 2015</li>
                        <li><strong>FIT Rate:</strong> 4.59p/kWh</li>
                        <li><strong>Remaining FIT Years:</strong> 6 years</li>
                        <li><strong>Annual Generation:</strong> ~315,000 kWh</li>
                        <li><strong>CO2 Saved:</strong> 157 tonnes/year</li>
                    </ul>
                </div>"""
            ]
        else:
            # Mixed technology - show varied results
            installations_html = [
                f"""<div style="background: #f0f4ff; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <h4>💨 FIT_12345 - Wind Turbine Installation</h4>
                    <ul>
                        <li><strong>Capacity:</strong> {cap}kW</li>
                        <li><strong>Location:</strong> {loc}, {postcodes[0]}7 5AB</li>
                        <li><strong>Site Name:</strong> Greenfield Wind Farm</li>
                        <li><strong>Commissioned:</strong> March 15, 2015</li>
                        <li><strong>FIT Rate:</strong> 13.73p/kWh</li>
                        <li><strong>Remaining FIT Years:</strong> 6 years</li>
                    </ul>
                </div>""",
                f"""<div style="background: #fff8e1; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <h4>☀️ FIT_12346 - Solar Farm</h4>
                    <ul>
                        <li><strong>Capacity:</strong> {cap-5}kW</li>
                        <li><strong>Location:</strong> {loc}, {postcodes[0]}14 2NP</li>
                        <li><strong>Site Name:</strong> Sunny Meadows Solar</li>
                        <li><strong>Commissioned:</strong> July 22, 2016</li>
                        <li><strong>FIT Rate:</strong> 4.39p/kWh</li>
                        <li><strong>Remaining FIT Years:</strong> 7 years</li>
                    </ul>
                </div>"""
            ]
        
        tech_desc = tech if tech else "renewable energy"
        return f"""<h3>Detailed Information - {tech_desc} installations near {cap}kW in {loc}</h3>
        {''.join(installations_html)}
        <p><em>💡 Context preserved from your previous query about {cap}kW {tech_desc} in {loc}!</em></p>
        <p style="color: #667eea; font-size: 12px;">Note: All postcodes shown are appropriate for {loc} region.</p>"""
    
    def generate_contextual_response(self, message, context):
        """Generate a response based on message and context"""
        msg_lower = message.lower()
        
        # Check for detail requests FIRST using existing context
        detail_keywords = ['details', 'more info', 'more information', 'tell me more', 'show me more', 
                          'their details', 'fit rates', 'tariffs', 'addresses', 'postcodes', 
                          'can you give', 'give me their', 'what are their']
        is_detail_request = any(keyword in msg_lower for keyword in detail_keywords)
        
        # If it's a detail request and we have context, return details immediately
        if is_detail_request and (context.get('capacity') or context.get('location') or context.get('technology')):
            return self.generate_details_response(context)
        
        # Otherwise, extract entities from message
        capacity = None
        location = None
        technology = None
        
        # Check for capacity
        if 'kw' in msg_lower:
            import re
            capacity_match = re.search(r'(\d+)\s*kw', msg_lower)
            if capacity_match:
                capacity = int(capacity_match.group(1))
        
        # Check for locations
        locations = ['ryedale', 'yorkshire', 'berkshire', 'stevenage', 'cornwall', 'devon', 'scotland']
        for loc in locations:
            if loc in msg_lower:
                location = loc.capitalize()
                break
        
        # Check for technologies (check these BEFORE looking for other entities)
        if 'wind' in msg_lower or 'turbine' in msg_lower:
            technology = 'Wind'
        elif 'solar' in msg_lower or 'photovoltaic' in msg_lower or 'pv' in msg_lower:
            technology = 'Photovoltaic'
        elif 'hydro' in msg_lower or 'water' in msg_lower:
            technology = 'Hydro'
        
        # Check for postcode questions
        if any(phrase in msg_lower for phrase in ['is rg', 'is yo', 'is sl', 'is tr', 'postcode', 'which area', 'what area']):
            # User is asking about postcodes
            postcode_info = {
                'RG': 'Reading/Berkshire',
                'SL': 'Slough/Berkshire', 
                'YO': 'York/Yorkshire',
                'HU': 'Hull/Yorkshire',
                'DN': 'Doncaster/Yorkshire',
                'LS': 'Leeds/Yorkshire',
                'BD': 'Bradford/Yorkshire',
                'TR': 'Truro/Cornwall',
                'PL': 'Plymouth/Devon',
                'EX': 'Exeter/Devon'
            }
            
            # Find which postcode they're asking about
            for code, area in postcode_info.items():
                if code.lower() in msg_lower:
                    return f"""<h3>Postcode Information</h3>
                    <p><strong>{code}</strong> postcodes are in <strong>{area}</strong>.</p>
                    <p>You're right to question this! In the previous results, any installations showing {code} postcodes 
                    would actually be in {area.split('/')[1]}, not {context.get('location', 'the specified location')}.</p>
                    <p style="color: #667eea;">This is a demo system - real data would have accurate geographic matching.</p>"""
            
            return """<h3>UK Postcode Areas</h3>
            <p>Common UK postcode prefixes:</p>
            <ul>
                <li><strong>Yorkshire:</strong> YO (York), HU (Hull), DN (Doncaster), LS (Leeds), BD (Bradford)</li>
                <li><strong>Berkshire:</strong> RG (Reading), SL (Slough)</li>
                <li><strong>Cornwall:</strong> TR (Truro), PL (Plymouth area)</li>
                <li><strong>Devon:</strong> EX (Exeter), TQ (Torquay), PL (Plymouth)</li>
            </ul>"""
        
        # Check for corrections
        if 'i meant' in msg_lower or 'i mean' in msg_lower:
            if location:
                context['location'] = location
                return f"<h3>Understood - updating location to {location}</h3><p>I'll now search for installations in {location}. The previous context has been updated.</p>"
        
        # Check for follow-ups
        if msg_lower.startswith('what about') or msg_lower.startswith('how about'):
            # This is a follow-up, use context
            if capacity and context['location']:
                return f"""<h3>Searching for {capacity}kW installations in {context['location']}</h3>
                <p>Based on your previous query, I'm looking for installations around {capacity}kW in {context['location']}.</p>
                <ul>
                    <li><strong>Location:</strong> {context['location']}</li>
                    <li><strong>Capacity:</strong> {capacity}kW (±25kW range)</li>
                    <li><strong>Results found:</strong> 3 installations</li>
                </ul>
                <p><em>This demonstrates conversation context - I remembered you were asking about {context['location']}!</em></p>"""
            elif technology and context['location'] and context['capacity']:
                return f"""<h3>Looking for {technology} installations</h3>
                <p>Continuing from your previous query about {context['capacity']}kW in {context['location']}, now filtering for {technology} technology.</p>
                <ul>
                    <li><strong>Technology:</strong> {technology}</li>
                    <li><strong>Location:</strong> {context['location']}</li>
                    <li><strong>Capacity:</strong> {context['capacity']}kW</li>
                </ul>
                <p><em>Context preserved from previous queries!</em></p>"""
        
        # Update context with new values
        if capacity:
            context['capacity'] = capacity
        if location:
            context['location'] = location
        if technology:
            context['technology'] = technology
        
        # Generate response based on what we found
        if capacity and location:
            # Filter by technology if specified
            installations = []
            if technology == 'Wind':
                installations = [
                    f"<li><strong>FIT_12345</strong> - {capacity}kW Wind Turbine - Commissioned 2015</li>",
                    f"<li><strong>FIT_12347</strong> - {capacity+10}kW Wind Farm - Commissioned 2014</li>",
                    f"<li><strong>FIT_12348</strong> - {capacity+25}kW Wind Installation - Commissioned 2016</li>"
                ]
            elif technology == 'Photovoltaic':
                installations = [
                    f"<li><strong>FIT_12346</strong> - {capacity-5}kW Solar Farm - Commissioned 2016</li>",
                    f"<li><strong>FIT_12349</strong> - {capacity}kW Solar Array - Commissioned 2017</li>",
                    f"<li><strong>FIT_12350</strong> - {capacity+15}kW Photovoltaic Plant - Commissioned 2015</li>"
                ]
            else:
                # No specific technology - show mixed results
                installations = [
                    f"<li><strong>FIT_12345</strong> - {capacity}kW Wind Turbine - Commissioned 2015</li>",
                    f"<li><strong>FIT_12346</strong> - {capacity-5}kW Solar Farm - Commissioned 2016</li>",
                    f"<li><strong>FIT_12347</strong> - {capacity+10}kW Wind Farm - Commissioned 2014</li>"
                ]
            
            tech_desc = f"{technology} installations" if technology else "installations"
            result_count = len(installations)
            return f"""<h3>Found {result_count} {tech_desc} near {capacity}kW in {location}</h3>
            <p>Showing {technology + ' ' if technology else ''}installations with capacity ≥{capacity}kW:</p>
            <ul>
                {''.join(installations)}
            </ul>
            <p style="color: #667eea; margin-top: 15px;">💡 Ask "can you give their details" to see full information, or try follow-up questions!</p>"""
        elif location:
            return f"""<h3>Installations in {location}</h3>
            <p>I found several installations in {location}. To narrow down the results, you can specify:</p>
            <ul>
                <li>Capacity (e.g., "300kW")</li>
                <li>Technology (e.g., "wind" or "solar")</li>
                <li>Or ask follow-up questions using the context!</li>
            </ul>"""
        elif capacity:
            context_loc = context.get('location')
            if context_loc:
                return f"""<h3>Searching for {capacity}kW installations in {context_loc}</h3>
                <p>Using your previous location context ({context_loc}), I found these installations around {capacity}kW.</p>
                <p><em>This demonstrates context memory - I remembered you were interested in {context_loc}!</em></p>"""
            else:
                return f"""<h3>Installations around {capacity}kW</h3>
                <p>Please specify a location to narrow down the search, or I can show all {capacity}kW installations nationwide.</p>"""
        else:
            return """<h3>How can I help you find FIT installations?</h3>
            <p>I can search by:</p>
            <ul>
                <li><strong>Capacity:</strong> "330kW installations"</li>
                <li><strong>Location:</strong> "sites in Yorkshire"</li>
                <li><strong>Technology:</strong> "wind farms" or "solar installations"</li>
                <li><strong>Combined:</strong> "250kW wind in Ryedale"</li>
            </ul>
            <p><strong>Test conversation memory:</strong></p>
            <ul>
                <li>Ask "329kw near stevenage"</li>
                <li>Then say "stevenage i meant" (correction)</li>
                <li>Then ask "what about 300kw?" (follow-up)</li>
            </ul>"""
    
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
    port = 5555
    server = HTTPServer(('localhost', port), ChatHandler)
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║         FIT Intelligence Chat Server (Demo Mode)           ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  🌐 Chat Interface:  http://localhost:{port}/chat.html     ║
║                                                            ║
║  Features Demonstrated:                                    ║
║  ✅ Conversation memory and context                       ║
║  ✅ Save/load chat history                                ║
║  ✅ Start new conversations                               ║
║  ✅ Follow-up questions                                   ║
║  ✅ Corrections ("I meant...")                            ║
║                                                            ║
║  This is a DEMO server with mock responses.               ║
║  It demonstrates the conversation context system.          ║
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