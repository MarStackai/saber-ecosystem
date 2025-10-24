#!/usr/bin/env python3
"""
Enhanced FIT Intelligence Chatbot
Integrates FIT License data with existing commercial data for comprehensive analysis
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import re
import time
from conversation_logger import ConversationLogger
from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI
from fit_rate_mapper import FITRateMapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedFITChatbot:
    """
    Enhanced FIT Intelligence Chatbot with comprehensive data access
    """
    
    def __init__(self, openrouter_api_key: str = None):
        """Initialize enhanced chatbot"""
        self.openrouter_api_key = openrouter_api_key
        self.conversation_logger = ConversationLogger()
        
        # Initialize enhanced intelligence API
        logger.info("Initializing Enhanced FIT Intelligence API...")
        self.intelligence_api = EnhancedFITIntelligenceAPI()
        
        # Initialize FIT rate mapper for pricing queries
        logger.info("Initializing FIT Rate Mapper...")
        self.fit_rate_mapper = FITRateMapper()
        
        # Get system status for context
        self.system_status = self.intelligence_api.get_system_status()
        
        # Enhanced system context with actual data
        self.system_context = self._create_enhanced_system_context()
        
        logger.info("Enhanced FIT Chatbot initialized successfully")
    
    def _create_enhanced_system_context(self) -> str:
        """Create comprehensive system context with real data"""
        
        # Get collection counts
        collections = self.system_status.get('collections', {})
        commercial_count = collections.get('commercial_fit_sites', {}).get('document_count', 0)
        license_count = collections.get('fit_licenses_enhanced', {}).get('document_count', 0)
        
        # Get data summary if available
        data_summary = self.system_status.get('data_summary', {})
        
        context = f"""You are an Enhanced FIT Intelligence Assistant, the most comprehensive advisor for UK renewable energy investment, PPA acquisition strategy, and FIT license analysis.

ENHANCED DATABASE SCOPE:
COMMERCIAL INSTALLATIONS: {commercial_count:,} sites with operational analysis
LICENSE DATABASE: {license_count:,} FIT licenses with detailed tariff information
TOTAL DATA COVERAGE: {commercial_count + license_count:,} renewable energy records

COMMERCIAL DATA BREAKDOWN:
- Photovoltaic: 35,617+ commercial sites (2,244+ MW capacity)
- Wind: 3,206+ sites (729+ MW capacity)
- Hydro: 895+ sites (262+ MW capacity)
- Anaerobic Digestion: 438+ sites (300+ MW capacity)
- Micro CHP: 38+ sites

ENHANCED LICENSE DATA:"""

        if data_summary:
            total_mw = data_summary.get('total_capacity_mw', 0)
            avg_age = data_summary.get('average_age_years', 0)
            context += f"""
- Total Licensed Capacity: {total_mw:.1f} MW across {license_count:,} licenses
- Average Installation Age: {avg_age:.1f} years
- Technology Distribution: {data_summary.get('technology_breakdown', {})}
- Repowering Windows: {data_summary.get('repowering_window_breakdown', {})}"""

        context += """

CORE BUSINESS INTELLIGENCE CAPABILITIES:
1. COMPREHENSIVE PPA ANALYSIS: Cross-reference commercial performance with license terms to identify optimal acquisition targets
2. FIT EXPIRY INTELLIGENCE: Precise tracking of FIT license expiry dates for immediate PPA opportunities  
3. DUAL-DATA INSIGHTS: Leverage both operational performance data AND regulatory license information
4. ENHANCED PORTFOLIO MAPPING: Geographic clustering with license density analysis
5. TARIFF OPTIMIZATION: Historical FIT rates analysis to predict post-FIT revenue potential
6. REGULATORY COMPLIANCE: License status tracking and renewal implications

ENHANCED QUERY CAPABILITIES:
- "Find wind farms with FIT licenses expiring in the next 2 years over 1MW"
- "Show me solar installations with high performance but approaching FIT expiry"
- "Which regions have the highest density of commercial renewable licenses?"
- "Compare FIT tariff rates across different installation periods"
- "Identify clusters of sites requiring immediate PPA transition"

DATA QUALITY & COVERAGE:
✓ Real-time operational data from {commercial_count:,} commercial installations
✓ Complete FIT license database with {license_count:,} regulatory records
✓ Semantic search across technical specifications, location, and financial terms
✓ Cross-referenced commercial performance with license obligations
✓ Historical tariff rate analysis and expiry forecasting

BUSINESS FOCUS:
Your expertise spans both technical renewable energy operations and regulatory FIT framework knowledge. Provide actionable insights for investment decisions, acquisition strategies, and portfolio optimization based on the comprehensive dual-dataset intelligence platform."""

        return context
    
    def query_enhanced_intelligence(self, query: str) -> Dict:
        """Query the enhanced intelligence system"""
        try:
            # Use natural language query capability
            results = self.intelligence_api.natural_language_query(query, max_results=10)
            
            if 'error' in results:
                logger.error(f"Enhanced intelligence query error: {results['error']}")
                return {
                    'success': False,
                    'error': results['error'],
                    'fallback_message': "I'm having trouble accessing the enhanced intelligence system. Please try a simpler query."
                }
            
            return {
                'success': True,
                'results': results,
                'summary': self._create_query_summary(results)
            }
            
        except Exception as e:
            logger.error(f"Enhanced intelligence query exception: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_message': "The enhanced intelligence system is temporarily unavailable."
            }
    
    def _create_query_summary(self, results: Dict) -> str:
        """Create a summary of query results for the LLM"""
        try:
            insights = results.get('combined_insights', {})
            total_results = insights.get('total_results', 0)
            
            if total_results == 0:
                return "No matching records found in the database."
            
            summary_parts = [f"Found {total_results} matching records:"]
            
            # Commercial results summary
            comm_count = insights.get('commercial_count', 0)
            if comm_count > 0:
                comm_capacity = insights.get('commercial_total_capacity_mw', 0)
                comm_urgent = insights.get('commercial_urgent_opportunities', 0)
                summary_parts.append(f"- {comm_count} commercial installations ({comm_capacity:.1f} MW total)")
                if comm_urgent > 0:
                    summary_parts.append(f"  └── {comm_urgent} urgent PPA opportunities")
            
            # License results summary
            license_count = insights.get('license_count', 0)
            if license_count > 0:
                license_capacity = insights.get('license_total_capacity_mw', 0)
                license_urgent = insights.get('license_urgent_opportunities', 0)
                summary_parts.append(f"- {license_count} FIT licenses ({license_capacity:.1f} MW total)")
                if license_urgent > 0:
                    summary_parts.append(f"  └── {license_urgent} urgent/expired FIT licenses")
            
            # Technology breakdown
            tech_breakdown = insights.get('technology_breakdown', {})
            if tech_breakdown:
                top_tech = list(tech_breakdown.items())[:3]
                tech_summary = ", ".join([f"{tech}: {count}" for tech, count in top_tech])
                summary_parts.append(f"- Top technologies: {tech_summary}")
            
            # Add sample results
            all_results = []
            all_results.extend(results.get('commercial_results', [])[:3])
            all_results.extend(results.get('license_results', [])[:3])
            
            if all_results:
                summary_parts.append("\nSample matches:")
                for i, result in enumerate(all_results[:5], 1):
                    metadata = result['metadata']
                    tech = metadata.get('technology', 'Unknown')
                    
                    if 'capacity_mw' in metadata:
                        capacity = f"{metadata['capacity_mw']:.1f}MW"
                        source = "commercial"
                    else:
                        capacity = f"{metadata.get('capacity_kw', 0):.0f}kW"
                        source = "license"
                    
                    window = metadata.get('repowering_window', 'Unknown')
                    location = metadata.get('postcode', metadata.get('region', ''))
                    
                    summary_parts.append(f"  {i}. {tech} {capacity} ({window}) - {location} [{source}]")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error creating query summary: {e}")
            return f"Found {results.get('combined_insights', {}).get('total_results', 0)} results (summary unavailable)"
    
    def get_comprehensive_insights(self, technology: str = None) -> Dict:
        """Get comprehensive insights with enhanced context"""
        try:
            insights = self.intelligence_api.get_comprehensive_insights(technology)
            
            if 'error' in insights:
                return {
                    'success': False,
                    'error': insights['error']
                }
            
            # Create narrative summary
            summary = self._create_insights_summary(insights, technology)
            
            return {
                'success': True,
                'insights': insights,
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"Comprehensive insights error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_insights_summary(self, insights: Dict, technology: str = None) -> str:
        """Create narrative summary of comprehensive insights"""
        try:
            tech_name = technology or "All Technologies"
            summary_parts = [f"COMPREHENSIVE ANALYSIS - {tech_name.upper()}:"]
            
            # Commercial insights
            comm_insights = insights.get('commercial_insights', {})
            if 'error' not in comm_insights:
                comm_count = comm_insights.get('total_count', 0)
                comm_capacity = comm_insights.get('total_capacity', 0)
                comm_avg_age = comm_insights.get('average_age_years', 0)
                
                summary_parts.append(f"\nCOMMERCIAL INSTALLATIONS:")
                summary_parts.append(f"- Total Sites: {comm_count:,}")
                summary_parts.append(f"- Total Capacity: {comm_capacity:.1f} MW")
                summary_parts.append(f"- Average Age: {comm_avg_age:.1f} years")
                
                urgency = comm_insights.get('urgency_breakdown', {})
                immediate = urgency.get('IMMEDIATE', 0)
                urgent = urgency.get('URGENT', 0)
                if immediate + urgent > 0:
                    summary_parts.append(f"- Immediate/Urgent PPA Opportunities: {immediate + urgent}")
            
            # License insights
            license_insights = insights.get('license_insights', {})
            if 'error' not in license_insights:
                license_count = license_insights.get('total_count', 0)
                license_capacity = license_insights.get('total_capacity', 0)
                license_avg_age = license_insights.get('average_age_years', 0)
                license_avg_remaining = license_insights.get('average_remaining_fit_years', 0)
                
                summary_parts.append(f"\nFIT LICENSE DATA:")
                summary_parts.append(f"- Total Licenses: {license_count:,}")
                summary_parts.append(f"- Total Capacity: {license_capacity:.0f} kW ({license_capacity/1000:.1f} MW)")
                summary_parts.append(f"- Average Age: {license_avg_age:.1f} years")
                summary_parts.append(f"- Average FIT Remaining: {license_avg_remaining:.1f} years")
                
                license_urgency = license_insights.get('urgency_breakdown', {})
                expired = license_urgency.get('EXPIRED', 0)
                immediate_license = license_urgency.get('IMMEDIATE', 0)
                urgent_license = license_urgency.get('URGENT', 0)
                
                if expired > 0:
                    summary_parts.append(f"- Expired FIT Licenses: {expired}")
                if immediate_license + urgent_license > 0:
                    summary_parts.append(f"- Immediate/Urgent License Renewals: {immediate_license + urgent_license}")
            
            # Combined analysis
            combined = insights.get('combined_analysis', {})
            if combined.get('data_sources', {}).get('both_available'):
                capacity_comp = combined.get('capacity_comparison', {})
                total_capacity = capacity_comp.get('total_combined_mw', 0)
                
                summary_parts.append(f"\nCOMBINED PORTFOLIO ANALYSIS:")
                summary_parts.append(f"- Total Combined Capacity: {total_capacity:.1f} MW")
                
                urgency_comp = combined.get('urgency_comparison', {})
                total_urgent = urgency_comp.get('total_urgent_opportunities', 0)
                if total_urgent > 0:
                    summary_parts.append(f"- Total Urgent Opportunities: {total_urgent}")
                
                tech_overlap = combined.get('technology_overlap', {})
                overlap_pct = tech_overlap.get('overlap_percentage', 0)
                summary_parts.append(f"- Data Coverage Overlap: {overlap_pct:.1f}%")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error creating insights summary: {e}")
            return "Comprehensive analysis completed (summary unavailable)"
    
    def _classify_query_intent(self, user_message: str) -> dict:
        """Enhanced query intent classification"""
        import re
        msg_lower = user_message.lower()
        intent = {
            'type': 'general',
            'has_location': False,
            'has_rate_context': False,
            'is_follow_up': False,
            'needs_details': False
        }
        
        # Check for FIT rate queries (rate + context OR FIT ID queries)
        rate_keywords = ['fit rate', 'tariff rate', 'rate in', 'rate for', 'what was the fit', 'what was the rate', 'fit price']
        context_keywords = ['kw', 'mw', 'capacity', '2012', '2013', '2014', '2015', '2016', '2017', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
        fit_id_pattern = r'fit id\s*\d+'
        
        has_rate_keyword = any(keyword in msg_lower for keyword in rate_keywords)
        has_context = any(keyword in msg_lower for keyword in context_keywords)
        has_fit_id = bool(re.search(fit_id_pattern, msg_lower))
        
        if (has_rate_keyword and has_context) or has_fit_id:
            intent['type'] = 'fit_rate_lookup'
            intent['has_rate_context'] = True
        
        # Check for location-based queries
        location_indicators = ['near', 'in', 'around', 'beverly', 'london', 'manchester', 'birmingham', 'glasgow', 'postcode', 'region']
        if any(indicator in msg_lower for indicator in location_indicators):
            intent['has_location'] = True
            intent['type'] = 'location_search'
        
        # Check for follow-up/detail requests
        follow_up_indicators = ['their details', 'more details', 'give me', 'show me', 'can you provide', 'what about']
        if any(indicator in msg_lower for indicator in follow_up_indicators):
            intent['is_follow_up'] = True
            intent['needs_details'] = True
            intent['type'] = 'detail_request'
        
        # Check for general data queries
        query_indicators = ['find', 'show', 'list', 'search', 'how many', 'what sites', 'where are']
        if any(indicator in msg_lower for indicator in query_indicators):
            intent['type'] = 'data_query'
        
        return intent
    
    def _enhance_query_with_context(self, user_message: str, intent: dict) -> str:
        """Enhance query with additional context and filtering"""
        enhanced_query = user_message
        
        # For location-based queries, add geographic context
        if intent['has_location']:
            # Extract location from message
            msg_lower = user_message.lower()
            locations = {
                'beverly': 'Beverly Yorkshire East Riding HU17',
                'london': 'London Greater London',
                'manchester': 'Manchester Greater Manchester', 
                'birmingham': 'Birmingham West Midlands',
                'glasgow': 'Glasgow Scotland',
            }
            
            for location_name, full_location in locations.items():
                if location_name in msg_lower:
                    enhanced_query += f" location:{full_location}"
                    break
        
        # For detail requests, add comprehensive data request
        if intent['needs_details']:
            enhanced_query += " with full technical specifications, FIT tariff details, operational status, and commercial information"
        
        return enhanced_query
    
    def _post_process_response(self, response: str, intent: dict, context_data: str) -> str:
        """Post-process and enhance LLM response"""
        try:
            # For location searches, ensure location context is mentioned
            if intent['type'] == 'location_search' and 'beverly' in intent.get('original_query', '').lower():
                if 'beverly' not in response.lower() and 'yorkshire' not in response.lower():
                    response = response.replace('Found', 'Found near Beverly, Yorkshire:')
            
            # For detail requests, ensure comprehensive information is provided
            if intent['needs_details']:
                if len(response.split('\n')) < 5:  # Short response, likely incomplete
                    response += "\n\n📋 **Complete Technical Specifications:**\nFor detailed specifications, FIT tariff rates, and commercial analysis, please specify which installations you'd like full details for."
            
            # Add helpful context for follow-up queries
            if intent['is_follow_up']:
                response += "\n\n💡 *Ask me for more specific details about any of these installations, including FIT rates, technical specifications, or commercial opportunities.*"
            
            return response
            
        except Exception as e:
            logger.error(f"Response post-processing error: {e}")
            return response
    
    def _create_enhanced_fallback_response(self, user_message: str, intent: dict, context_data: str) -> str:
        """Create enhanced fallback response when OpenRouter is unavailable"""
        try:
            if context_data and "DATA QUERY RESULTS:" in context_data:
                # Extract and format the data results
                data_section = context_data.split("DATA QUERY RESULTS:")[1].split("\n\n")[0]
                
                if intent['type'] == 'location_search':
                    return f"**FIT Intelligence Location Search Results:**\n{data_section}\n\n*Enhanced analysis available with full API access.*"
                elif intent['needs_details']:
                    return f"**Detailed FIT Installation Information:**\n{data_section}\n\n**Available Details:**\n- FIT tariff rates and expiry dates\n- Technical specifications\n- Commercial opportunities\n- Geographic clustering analysis\n\n*Contact for comprehensive analysis.*"
                else:
                    return f"**Enhanced FIT Intelligence Results:**\n{data_section}\n\n*This analysis covers both commercial installations and FIT licenses across the UK renewable energy sector.*"
            else:
                # No data available
                if intent['type'] == 'fit_rate_lookup':
                    return "FIT rate lookup requires specific capacity (kW) and commissioning date information. Please provide both parameters for accurate rate calculation."
                elif intent['type'] == 'location_search':
                    return "Location-based search requires Enhanced FIT Intelligence system. Please ensure the system is running for geographic analysis."
                else:
                    return "Enhanced FIT Intelligence system provides comprehensive analysis of UK renewable installations. Please specify your query parameters for detailed results."
                    
        except Exception as e:
            logger.error(f"Enhanced fallback response error: {e}")
            return "FIT Intelligence system available. Please rephrase your query for optimal results."
    
    def chat(self, user_message: str) -> str:
        """Enhanced chat functionality with comprehensive data access"""
        try:
            # Log conversation start (with fallback if logger doesn't have start_conversation method)
            try:
                conversation_id = self.conversation_logger.start_conversation(user_message)
            except AttributeError:
                conversation_id = str(int(time.time()))
            
            # Enhanced query intent classification
            query_intent = self._classify_query_intent(user_message)
            
            # Handle specific FIT rate queries (must contain date/capacity keywords)
            if query_intent['type'] == 'fit_rate_lookup' and query_intent['has_rate_context']:
                logger.info("Processing specific FIT rate query...")
                fit_result = self.fit_rate_mapper.query_fit_rate(user_message)
                return fit_result
            
            context_data = ""
            
            # Handle different query types based on intent
            if query_intent['type'] in ['data_query', 'location_search', 'detail_request']:
                logger.info(f"Processing {query_intent['type']} query...")
                
                # Enhanced query with location filtering if needed
                enhanced_query = self._enhance_query_with_context(user_message, query_intent)
                
                intelligence_result = self.query_enhanced_intelligence(enhanced_query)
                
                if intelligence_result['success']:
                    context_data = f"\n\nDATA QUERY RESULTS:\n{intelligence_result['summary']}"
                    
                    # For detail requests, provide comprehensive formatting
                    if query_intent['needs_details']:
                        context_data += "\n\nDETAILED INFORMATION AVAILABLE - Please provide specific details for each matching site including FIT rates, capacities, and commercial status."
                else:
                    context_data = f"\n\nDATA QUERY NOTE: {intelligence_result['fallback_message']}"
            
            # Check for insights requests
            insights_keywords = ['insight', 'analysis', 'breakdown', 'overview', 'summary']
            if any(keyword in user_message.lower() for keyword in insights_keywords):
                # Extract technology if mentioned
                technology = None
                tech_map = {
                    'solar': 'Photovoltaic',
                    'photovoltaic': 'Photovoltaic', 
                    'pv': 'Photovoltaic',
                    'wind': 'Wind',
                    'hydro': 'Hydro',
                    'anaerobic': 'Anaerobic digestion',
                    'biogas': 'Anaerobic digestion'
                }
                
                for keyword, tech_name in tech_map.items():
                    if keyword in user_message.lower():
                        technology = tech_name
                        break
                
                insights_result = self.get_comprehensive_insights(technology)
                if insights_result['success']:
                    context_data += f"\n\nCOMPREHENSIVE INSIGHTS:\n{insights_result['summary']}"
            
            # Prepare LLM request
            messages = [
                {
                    "role": "system",
                    "content": self.system_context + context_data
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ]
            
            # Enhanced response generation with better error handling
            if self.openrouter_api_key:
                try:
                    response = self._call_openrouter(messages)
                    # Validate and enhance response
                    response = self._post_process_response(response, query_intent, context_data)
                except Exception as e:
                    logger.error(f"OpenRouter API error: {e}")
                    response = self._create_enhanced_fallback_response(user_message, query_intent, context_data)
            else:
                # Enhanced fallback response
                response = self._create_enhanced_fallback_response(user_message, query_intent, context_data)
            
            # Log conversation (with fallback if logger doesn't have log_exchange method)
            try:
                self.conversation_logger.log_exchange(
                    conversation_id, user_message, response, 
                    intelligence_used=bool(context_data),
                    data_sources_accessed=['enhanced_commercial', 'fit_licenses'] if context_data else []
                )
            except AttributeError:
                # Simple logging fallback
                logger.info(f"Chat exchange - Query: {user_message[:50]}... Response: {response[:50]}...")
            
            return response
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"I apologize, but I encountered an error processing your request: {str(e)}. Please try rephrasing your question."
    
    def _call_openrouter(self, messages: List[Dict]) -> str:
        """Call OpenRouter API"""
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "anthropic/claude-3.5-sonnet",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                logger.error(f"OpenRouter API error: {response.status_code}")
                return "I'm having trouble connecting to the language model. Please try again."
                
        except Exception as e:
            logger.error(f"OpenRouter call error: {e}")
            return "I'm experiencing technical difficulties. Please try again."
    
    def _create_fallback_response(self, user_message: str, context_data: str) -> str:
        """Create fallback response when OpenRouter is not available"""
        if context_data:
            return f"Based on the enhanced FIT intelligence database:\n{context_data}\n\nThis analysis covers both commercial installations and FIT licenses across the UK renewable energy sector."
        else:
            return "I'm ready to help with FIT intelligence queries. I have access to comprehensive data on UK renewable energy installations and FIT licenses. Please ask me about specific technologies, locations, or investment opportunities."
    
    def get_system_info(self) -> Dict:
        """Get enhanced system information"""
        return {
            'system_status': self.system_status,
            'capabilities': [
                'Natural language queries across commercial and license data',
                'Comprehensive technology insights',
                'FIT expiry analysis and PPA opportunity identification',
                'Geographic clustering and portfolio optimization',
                'Cross-referenced commercial performance and license terms'
            ],
            'data_coverage': self.system_status.get('collections', {}),
            'enhanced_features': [
                'Dual-dataset intelligence (commercial + licenses)',
                'Semantic search with vector embeddings', 
                'Real-time FIT expiry tracking',
                'Integrated tariff rate analysis'
            ]
        }

# Test the enhanced chatbot
if __name__ == "__main__":
    print("=" * 60)
    print("ENHANCED FIT INTELLIGENCE CHATBOT TEST")
    print("=" * 60)
    
    # Initialize chatbot
    chatbot = EnhancedFITChatbot()
    
    # Show system info
    system_info = chatbot.get_system_info()
    print(f"\nSystem Status:")
    for collection, info in system_info['data_coverage'].items():
        if 'document_count' in info:
            print(f"✓ {collection}: {info['document_count']:,} documents")
    
    print(f"\nCapabilities:")
    for capability in system_info['capabilities']:
        print(f"• {capability}")
    
    # Test queries
    test_queries = [
        "How many solar installations have expiring FIT tariffs?",
        "Show me wind farms over 1MW requiring immediate PPA attention",
        "What are the insights for photovoltaic installations?",
        "Find renewable energy clusters in Scotland"
    ]
    
    print(f"\nTesting sample queries:")
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        response = chatbot.chat(query)
        # Show first 200 characters of response
        print(f"Response: {response[:200]}{'...' if len(response) > 200 else ''}")
    
    print(f"\n{'='*60}")
    print("ENHANCED CHATBOT TEST COMPLETE!")
    print(f"{'='*60}")