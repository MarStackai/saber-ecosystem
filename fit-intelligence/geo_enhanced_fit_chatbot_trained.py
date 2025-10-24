#!/usr/bin/env python3
"""
Geographic Enhanced FIT Chatbot
Integrates UK geographic intelligence with FIT data analysis for comprehensive renewable energy insights
"""

import logging
from flask import Flask, request, jsonify
import json
from enhanced_geo_fit_intelligence import EnhancedGeoFITIntelligence
from enhanced_fit_chatbot import EnhancedFITChatbot
from uk_geo_intelligence import UKGeoIntelligence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeoEnhancedFITChatbot:
    """FIT Chatbot with comprehensive UK geographic intelligence"""
    
    def __init__(self):
        self.base_chatbot = EnhancedFITChatbot()
        self.geo_intelligence = UKGeoIntelligence()
        self.geo_fit_intelligence = EnhancedGeoFITIntelligence()
        
        logger.info("Geographic Enhanced FIT Chatbot initialized")
    
    def chat(self, user_message: str) -> str:
        """Enhanced chat with geographic intelligence capabilities"""
        try:
            # Classify query intent with geographic awareness
            intent = self._classify_geographic_intent(user_message)
            
            # Route to appropriate handler
            if intent['type'] == 'geographic_search':
                return self._handle_geographic_search(user_message, intent)
            elif intent['type'] == 'regional_analysis':
                return self._handle_regional_analysis(user_message, intent)
            elif intent['type'] == 'distance_calculation':
                return self._handle_distance_calculation(user_message, intent)
            elif intent['type'] == 'site_clustering':
                return self._handle_site_clustering(user_message, intent)
            else:
                # Fall back to base chatbot for non-geographic queries
                return self.base_chatbot.chat(user_message)
                
        except Exception as e:
            logger.error(f"Geographic chat error: {e}")
            return f"I encountered an error processing your geographic query: {str(e)}"
    
    def _classify_geographic_intent(self, user_message: str) -> dict:
        """Classify query intent with geographic awareness"""
        msg_lower = user_message.lower()
        
        intent = {
            'type': 'general',
            'has_location': False,
            'has_distance': False,
            'needs_clustering': False,
            'needs_regional_analysis': False
        }
        
        # Geographic search indicators
        geo_search_indicators = [
            'near', 'around', 'close to', 'within', 'sites in', 'installations in',
            'beverly', 'beverley', 'york', 'leeds', 'hull', 'london', 'manchester'
        ]
        
        if any(indicator in msg_lower for indicator in geo_search_indicators):
            intent['type'] = 'geographic_search'
            intent['has_location'] = True
        
        # Regional analysis indicators
        regional_indicators = [
            'regional analysis', 'market analysis', 'area analysis', 
            'regional opportunities', 'market opportunities'
        ]
        
        if any(indicator in msg_lower for indicator in regional_indicators):
            intent['type'] = 'regional_analysis'
            intent['needs_regional_analysis'] = True
        
        # Distance calculation indicators
        distance_indicators = [
            'distance between', 'how far', 'miles from', 'km from',
            'travel distance', 'logistics'
        ]
        
        if any(indicator in msg_lower for indicator in distance_indicators):
            intent['type'] = 'distance_calculation'
            intent['has_distance'] = True
        
        # Clustering indicators
        cluster_indicators = [
            'clusters', 'groups of sites', 'site clusters', 
            'nearby installations', 'grouped installations'
        ]
        
        if any(indicator in msg_lower for indicator in cluster_indicators):
            intent['type'] = 'site_clustering'
            intent['needs_clustering'] = True
        
        return intent
    
    def _handle_geographic_search(self, user_message: str, intent: dict) -> str:
        """Handle geographic search queries"""
        try:
            # Extract radius if specified
            radius_km = self._extract_radius(user_message)
            
            # Perform enhanced geographic search
            result = self.geo_fit_intelligence.search_sites_by_location(
                user_message, radius_km=radius_km, max_results=20
            )
            
            if 'error' in result:
                return f"Geographic search error: {result['error']}"
            
            # Format comprehensive response
            response = self._format_geographic_search_response(result)
            return response
            
        except Exception as e:
            logger.error(f"Geographic search handler error: {e}")
            return f"Error processing geographic search: {str(e)}"
    
    def _handle_regional_analysis(self, user_message: str, intent: dict) -> str:
        """Handle regional analysis queries"""
        try:
            # Extract postcode or location
            location_info = self.geo_fit_intelligence._extract_location_from_query(user_message)
            
            if 'error' in location_info:
                return f"Could not identify location for regional analysis: {location_info['error']}"
            
            # Perform regional analysis
            radius_km = self._extract_radius(user_message, default=50)
            regional_analysis = self.geo_fit_intelligence.get_regional_fit_analysis(
                location_info['postcode'], radius_km
            )
            
            if 'error' in regional_analysis:
                return f"Regional analysis error: {regional_analysis['error']}"
            
            # Format comprehensive regional response
            response = self._format_regional_analysis_response(regional_analysis)
            return response
            
        except Exception as e:
            logger.error(f"Regional analysis handler error: {e}")
            return f"Error processing regional analysis: {str(e)}"
    
    def _handle_distance_calculation(self, user_message: str, intent: dict) -> str:
        """Handle distance calculation queries"""
        try:
            # Extract postcodes from message
            postcodes = self._extract_postcodes(user_message)
            
            if len(postcodes) < 2:
                return "Please specify two postcodes for distance calculation (e.g., 'distance between YO17 9AS and YO25 9AA')"
            
            # Calculate distance
            distance_result = self.geo_intelligence.calculate_distance(postcodes[0], postcodes[1])
            
            if 'error' in distance_result:
                return f"Distance calculation error: {distance_result['error']}"
            
            # Format response
            response = f"""
**Distance Calculation Results:**

📍 From: {postcodes[0]} ({distance_result['geo1']['region']}, {distance_result['geo1']['admin_district']})
📍 To: {postcodes[1]} ({distance_result['geo2']['region']}, {distance_result['geo2']['admin_district']})

📏 **Distance: {distance_result['distance_km']}km ({distance_result['distance_miles']} miles)**

🚗 Estimated travel time: {self._estimate_travel_time(distance_result['distance_km'])}
⚡ Suitable for shared maintenance operations: {'Yes' if distance_result['distance_km'] <= 50 else 'Consider regional hubs'}
            """.strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Distance calculation handler error: {e}")
            return f"Error calculating distance: {str(e)}"
    
    def _handle_site_clustering(self, user_message: str, intent: dict) -> str:
        """Handle site clustering analysis queries"""
        try:
            # Extract technology if specified
            technology = self._extract_technology(user_message)
            
            # Perform cluster analysis
            cluster_result = self.geo_fit_intelligence.analyze_site_clusters(
                technology=technology, min_sites=3
            )
            
            if 'error' in cluster_result:
                return f"Cluster analysis error: {cluster_result['error']}"
            
            # Format clustering response
            response = self._format_clustering_response(cluster_result)
            return response
            
        except Exception as e:
            logger.error(f"Site clustering handler error: {e}")
            return f"Error analyzing site clusters: {str(e)}"
    
    def _extract_radius(self, message: str, default: int = 20) -> int:
        """Extract radius from message, return default if not found"""
        import re
        
        # Look for patterns like "within 25km", "30 mile radius", etc.
        radius_patterns = [
            r'within\s+(\d+)\s*km',
            r'(\d+)\s*km\s+radius',
            r'within\s+(\d+)\s*mile',
            r'(\d+)\s*mile\s+radius'
        ]
        
        for pattern in radius_patterns:
            match = re.search(pattern, message.lower())
            if match:
                return int(match.group(1))
        
        return default
    
    def _extract_postcodes(self, message: str) -> list:
        """Extract postcodes and place names from message"""
        import re
        
        # First try to extract postcodes
        postcode_pattern = r'([A-Z]{1,2}[0-9R][0-9A-Z]?\s*[0-9][ABD-HJLNP-UW-Z]{2})'
        postcodes = re.findall(postcode_pattern, message.upper())
        
        if postcodes:
            return postcodes
        
        # If no postcodes found, try to extract place names from distance queries
        distance_patterns = [
            r'distance between\s+([a-zA-Z\s]+?)\s+and\s+([a-zA-Z\s]+)',
            r'from\s+([a-zA-Z\s]+?)\s+to\s+([a-zA-Z\s]+)',
            r'between\s+([a-zA-Z\s]+?)\s+and\s+([a-zA-Z\s]+)'
        ]
        
        for pattern in distance_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                place1 = match.group(1).strip()
                place2 = match.group(2).strip()
                
                # Convert place names to postcodes using smart lookup
                geo_data1 = self.geo_intelligence.smart_location_lookup(place1)
                geo_data2 = self.geo_intelligence.smart_location_lookup(place2)
                
                location_codes = []
                if 'error' not in geo_data1:
                    location_codes.append(geo_data1.get('outcode') or geo_data1.get('postcode'))
                if 'error' not in geo_data2:
                    location_codes.append(geo_data2.get('outcode') or geo_data2.get('postcode'))
                
                return location_codes
        
        return postcodes
    
    def _extract_technology(self, message: str) -> str:
        """Extract technology type from message"""
        msg_lower = message.lower()
        
        tech_mapping = {
            'wind': 'Wind',
            'solar': 'Photovoltaic',
            'photovoltaic': 'Photovoltaic',
            'pv': 'Photovoltaic',
            'hydro': 'Hydro',
            'anaerobic': 'Anaerobic digestion',
            'biogas': 'Anaerobic digestion'
        }
        
        for keyword, technology in tech_mapping.items():
            if keyword in msg_lower:
                return technology
        
        return None
    
    def _format_geographic_search_response(self, result: dict) -> str:
        """Format comprehensive geographic search response"""
        try:
            # Count actual results that passed all filters (including capacity)
            commercial_results = result.get('commercial_results', [])
            license_results = result.get('license_results', [])
            actual_total = len(commercial_results) + len(license_results)
            
            # Get original query insights for context
            total_before_filters = result['combined_insights']['total_results'] 
            
            if actual_total == 0:
                # Check if it's a capacity filtering issue
                if total_before_filters > 0:
                    return f"No renewable energy sites found matching your specific criteria (capacity/technology filters). Found {total_before_filters} sites in the area but none met your requirements."
                else:
                    return "No renewable energy sites found matching your geographic search criteria."
            
            # Build response with actual filtered counts
            response_parts = [
                f"**🌍 Geographic Search Results**",
                f"Found **{actual_total}** renewable energy sites matching your criteria:",
                f"• {len(commercial_results)} commercial installations",
                f"• {len(license_results)} FIT licenses"
            ]
            
            # Add geographic analysis if available
            if 'geographic_analysis' in result:
                geo_analysis = result['geographic_analysis']
                search_center = geo_analysis['search_center']
                
                response_parts.extend([
                    f"",
                    f"**📍 Search Area:**",
                    f"• Center: {search_center['location_name']} ({search_center['postcode']})",
                    f"• Region: {search_center['geo_data']['region']}",
                    f"• Administrative area: {search_center['geo_data']['admin_district']}"
                ])
                
                # Site distribution
                if 'site_distribution' in geo_analysis and 'error' not in geo_analysis['site_distribution']:
                    dist = geo_analysis['site_distribution']
                    response_parts.extend([
                        f"",
                        f"**📊 Site Distribution:**",
                        f"• Average distance from center: {dist['average_distance_km']}km",
                        f"• Closest site: {dist['min_distance_km']}km away",
                        f"• Furthest site: {dist['max_distance_km']}km away"
                    ])
                
                # Regional assessment
                if 'regional_assessment' in geo_analysis and 'error' not in geo_analysis['regional_assessment']:
                    assessment = geo_analysis['regional_assessment']
                    response_parts.extend([
                        f"",
                        f"**⚡ Regional Renewable Assessment:**",
                        f"• Wind potential: {assessment['renewable_potential']['wind_potential']}",
                        f"• Solar potential: {assessment['renewable_potential']['solar_potential']}",
                        f"• Total existing capacity: {assessment['existing_installations']['total_capacity_kw']:,.0f}kW",
                        f"• Market opportunity: {assessment['market_opportunity']}"
                    ])
            
            # Show sample sites
            all_sites = commercial_results + license_results
            if all_sites:
                response_parts.extend([
                    f"",
                    f"**🏗️ Sample Installations:**"
                ])
                
                for i, site in enumerate(all_sites[:5], 1):
                    meta = site.get('metadata', {})
                    tech = meta.get('technology', 'Unknown')
                    
                    # Handle FIT ID display
                    fit_id = meta.get('fit_id', 'N/A')
                    
                    # Handle capacity
                    capacity_kw = meta.get('capacity_kw', 0)
                    if isinstance(capacity_kw, (int, float)) and capacity_kw > 0:
                        if capacity_kw >= 1000:
                            capacity = f"{capacity_kw/1000:.1f}MW"
                        else:
                            capacity = f"{capacity_kw:.0f}kW"
                    else:
                        capacity = "Unknown capacity"
                    
                    postcode = meta.get('postcode', 'Location unknown')
                    
                    # Add distance if available
                    distance_info = ""
                    if 'geographic_data' in site:
                        distance_km = site['geographic_data'].get('distance_km')
                        if distance_km:
                            distance_info = f" ({distance_km}km away)"
                    
                    response_parts.append(f"  {i}. {tech} {capacity} - FIT ID: {fit_id} - {postcode}{distance_info}")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Geographic response formatting error: {e}")
            return f"Found {result['combined_insights']['total_results']} sites (formatting error: {str(e)})"
    
    def _format_regional_analysis_response(self, analysis: dict) -> str:
        """Format comprehensive regional analysis response"""
        try:
            geo_data = analysis['geographic_data']
            admin_hierarchy = geo_data['administrative_hierarchy']
            renewable_indicators = geo_data['renewable_indicators']
            
            response_parts = [
                f"**🏛️ Regional FIT Analysis Report**",
                f"",
                f"**📍 Geographic Overview:**",
                f"• Postcode: {analysis['center_postcode']}",
                f"• Region: {admin_hierarchy['region']}",
                f"• Administrative District: {admin_hierarchy['admin_district']}",
                f"• Parliamentary Constituency: {admin_hierarchy['parliamentary_constituency']}",
                f"• Analysis Radius: {analysis['analysis_radius_km']}km",
                f"",
                f"**⚡ Renewable Energy Potential:**",
                f"• Wind potential: {renewable_indicators['wind_potential'].upper()}",
                f"• Solar potential: {renewable_indicators['solar_potential'].upper()}",
                f"• Coastal proximity: {'Yes' if renewable_indicators['coastal_proximity'] else 'No'}",
                f"• Grid connectivity: {renewable_indicators['grid_connectivity']}"
            ]
            
            # Add market intelligence if available
            if 'market_intelligence' in analysis:
                market = analysis['market_intelligence']
                response_parts.extend([
                    f"",
                    f"**📊 Market Intelligence:**",
                    f"• Planning authority: {market['planning_authority']}",
                    f"• Regional postcode coverage: {market['nearby_postcode_coverage']} postcodes",
                    f"• Investment attractiveness: {market['investment_attractiveness']}"
                ])
            
            # Add opportunities if available
            if 'regional_opportunities' in analysis:
                opportunities = analysis['regional_opportunities']
                if opportunities:
                    response_parts.extend([
                        f"",
                        f"**🎯 Regional Opportunities:**"
                    ])
                    for opportunity in opportunities:
                        response_parts.append(f"• {opportunity}")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Regional analysis response formatting error: {e}")
            return f"Regional analysis completed (formatting error: {str(e)})"
    
    def _format_clustering_response(self, cluster_result: dict) -> str:
        """Format site clustering analysis response"""
        try:
            technology = cluster_result['technology']
            total_sites = cluster_result['total_sites_analyzed']
            clusters_found = cluster_result['clusters_found']
            
            response_parts = [
                f"**🗂️ Site Clustering Analysis**",
                f"",
                f"**Analysis Overview:**",
                f"• Technology focus: {technology or 'All technologies'}",
                f"• Total sites analyzed: {total_sites}",
                f"• Geographic clusters identified: {clusters_found}"
            ]
            
            if clusters_found > 0:
                analysis_summary = cluster_result['analysis_summary']
                response_parts.extend([
                    f"",
                    f"**📊 Cluster Summary:**",
                    f"• Total sites in clusters: {analysis_summary['total_sites_in_clusters']}",
                    f"• Total clustered capacity: {analysis_summary['total_capacity_kw']:,.0f}kW",
                    f"• Average cluster size: {analysis_summary['average_cluster_size']} sites",
                    f"• Largest cluster: {analysis_summary['largest_cluster']} sites"
                ])
                
                # Show individual clusters
                response_parts.extend([
                    f"",
                    f"**🏗️ Individual Clusters:**"
                ])
                
                for i, cluster in enumerate(cluster_result['clusters'][:5], 1):  # Show first 5 clusters
                    response_parts.append(
                        f"{i}. **{cluster['center_postcode']}** cluster: "
                        f"{cluster['site_count']} sites, "
                        f"{cluster['total_capacity_kw']:,.0f}kW total"
                    )
                    
                    if cluster['technologies']:
                        tech_list = ', '.join(cluster['technologies'])
                        response_parts.append(f"   Technologies: {tech_list}")
            else:
                response_parts.append(f"")
                response_parts.append(f"**ℹ️ No significant clusters found.** Sites may be too dispersed for cluster analysis.")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Clustering response formatting error: {e}")
            return f"Site clustering analysis completed (formatting error: {str(e)})"
    
    def _estimate_travel_time(self, distance_km: float) -> str:
        """Estimate travel time based on distance"""
        if distance_km <= 50:
            # Local travel - assume 40km/h average with traffic
            hours = distance_km / 40
            minutes = int(hours * 60)
            return f"~{minutes} minutes"
        else:
            # Long distance - assume 60km/h average
            hours = distance_km / 60
            if hours >= 1:
                return f"~{hours:.1f} hours"
            else:
                minutes = int(hours * 60)
                return f"~{minutes} minutes"

# Flask API for geographic enhanced chatbot
app = Flask(__name__)
chatbot = None

@app.route('/api/geo-chat/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'Geographic Enhanced FIT Chatbot'})

@app.route('/api/geo-chat/message', methods=['POST'])
def chat():
    global chatbot
    try:
        if not chatbot:
            chatbot = GeoEnhancedFITChatbot()
        
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({'status': 'error', 'error': 'Message is required'}), 400
        
        response = chatbot.chat(message)
        
        return jsonify({
            'status': 'success',
            'response': response,
            'enhanced_features': ['geographic_intelligence', 'uk_postcode_lookup', 'distance_calculation', 'site_clustering']
        })
        
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/geo-chat/capabilities', methods=['GET'])
def capabilities():
    return jsonify({
        'service': 'Geographic Enhanced FIT Chatbot',
        'capabilities': [
            'UK postcode lookup and validation',
            'Geographic search for renewable installations', 
            'Distance calculations between sites',
            'Regional renewable energy analysis',
            'Site clustering and optimization',
            'Market opportunity assessment',
            'Administrative area intelligence',
            'Logistics planning support'
        ],
        'data_sources': [
            'Postcodes.io API (free UK postcode data)',
            'FIT installation database',
            'Commercial renewable energy sites',
            'Geographic coordinate system'
        ]
    })

if __name__ == "__main__":
    print("🌍⚡ Starting Geographic Enhanced FIT Chatbot...")
    print("=" * 60)
    
    # Test the system
    test_chatbot = GeoEnhancedFITChatbot()
    
    test_queries = [
        "wind sites near beverly between 250 and 500kw",
        "regional analysis for YO17 9AS",
        "distance between YO17 9AS and YO25 9AA",
        "show me wind farm clusters in yorkshire"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: {query}")
        print("-" * 50)
        response = test_chatbot.chat(query)
        print(response[:300] + "..." if len(response) > 300 else response)
    
    print(f"\n✅ Geographic Enhanced FIT Chatbot ready!")
    print(f"🚀 Starting Flask API server...")
    
    app.run(host='0.0.0.0', port=5003, debug=False)