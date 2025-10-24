#!/usr/bin/env python3
"""
vLLM-Enhanced FIT Chatbot with GPU Acceleration
Uses vLLM for fast GPU inference with proper parameter extraction
"""

import json
import requests
import logging
from typing import Dict, List, Any, Optional
from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI
from session_manager import SessionManager
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VLLMEnhancedFITChatbot:
    """Hybrid chatbot using vLLM on GPU for fast inference"""
    
    def __init__(self, model: str = "TheBloke/Llama-2-13B-GPTQ", vllm_url: str = "http://localhost:8000"):
        self.fit_api = EnhancedFITIntelligenceAPI()
        self.session_manager = SessionManager()
        self.model = model
        self.vllm_url = vllm_url
        
        logger.info(f"Initialized vLLM chatbot with model: {model}")
        logger.info(f"vLLM server: {vllm_url}")
    
    def chat(self, query: str, session_id: str = "default") -> str:
        """Process query using vLLM for understanding and database for facts"""
        try:
            # Step 1: Get session context
            session = self.session_manager.get_session(session_id)
            
            # Step 2: Use vLLM to understand the query
            understanding = self._understand_with_vllm(query, session)
            logger.info(f"vLLM Understanding: {understanding}")
            
            # Step 3: Decide action based on understanding
            if understanding.get('is_followup') and session.get('last_results'):
                # Use previous results ONLY if they exist
                logger.info(f"Using previous {len(session['last_results'])} results for follow-up query")
                results = session['last_results']
                
                # Apply any additional processing requested
                if understanding.get('intent') == 'calculate_income':
                    return self._calculate_income_response(results)
                elif understanding.get('intent') == 'get_details':
                    return self._format_detailed_response(results)
                elif understanding.get('intent') == 'get_fit_ids':
                    return self._format_fit_ids_response(results)
            else:
                # New search needed
                search_params = understanding.get('search_params', {})
                logger.info(f"Performing new search with params: {search_params}")
                
                # Search the database
                results = self._search_database(query, search_params)
                
                # Store in session for follow-ups
                self.session_manager.store_results(session_id, query, results, search_params)
            
            # Step 4: Format response
            response = self._format_response(results, understanding)
            
            return response
            
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return f"I encountered an error processing your query. Please try rephrasing."
    
    def _understand_with_vllm(self, query: str, session: Dict) -> Dict:
        """Use vLLM to understand query intent and extract parameters"""
        
        prompt = f"""You are an AI assistant for the UK Feed-in Tariff (FIT) intelligence system.
Analyze this renewable energy query and extract search parameters.

Current query: "{query}"
Previous query: "{session.get('last_query', 'None')}"
Has previous results: {len(session.get('last_results', [])) > 0}

IMPORTANT RULES:
1. If query contains "give me all the details" or "their details", set is_followup=true
2. For Aberdeen, set location="aberdeen" (NOT "north of aberdeen")
3. For capacity ranges like "between 150kw and 500kw", extract BOTH numbers
4. Always use single values, never pipe-separated

Respond in JSON format:
{{
    "is_followup": false,
    "intent": "search_new",
    "search_params": {{
        "technology": "wind",
        "location": "aberdeen",
        "min_capacity_kw": 150,
        "max_capacity_kw": 500
    }},
    "reasoning": "New search for wind farms"
}}"""
        
        try:
            response = requests.post(
                f"{self.vllm_url}/v1/completions",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": 0.1,
                    "max_tokens": 200,
                    "stop": ["}}", "\n\n"]
                },
                timeout=2  # Fast with GPU!
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result['choices'][0]['text']
                # Extract JSON from response
                json_start = text.find('{')
                if json_start >= 0:
                    json_str = text[json_start:]
                    # Ensure closing brace
                    if not json_str.rstrip().endswith('}'):
                        json_str += '}'
                    return json.loads(json_str)
            
            # Fallback to rule-based
            return self._fallback_understanding(query, session)
                
        except Exception as e:
            logger.error(f"vLLM understanding failed: {e}")
            return self._fallback_understanding(query, session)
    
    def _fallback_understanding(self, query: str, session: Dict) -> Dict:
        """Rule-based fallback if vLLM fails"""
        query_lower = query.lower()
        
        # Check for follow-up indicators
        followup_phrases = ['their', 'those', 'these', 'give me details', 'all the details']
        is_followup = any(phrase in query_lower for phrase in followup_phrases)
        
        # Determine intent
        intent = 'search_new'
        if 'detail' in query_lower:
            intent = 'get_details'
        elif 'income' in query_lower:
            intent = 'calculate_income'
        elif 'fit id' in query_lower:
            intent = 'get_fit_ids'
        
        # Extract search parameters
        search_params = {}
        
        # Technology
        if 'wind' in query_lower:
            search_params['technology'] = 'wind'
        elif 'solar' in query_lower:
            search_params['technology'] = 'solar'
        elif 'hydro' in query_lower:
            search_params['technology'] = 'hydro'
        
        # Capacity - handle ranges properly
        capacity_pattern = r'between\s+(\d+)\s*(?:kw|mw)?\s+and\s+(\d+)\s*(?:kw|mw)'
        range_match = re.search(capacity_pattern, query_lower)
        if range_match:
            min_cap = int(range_match.group(1))
            max_cap = int(range_match.group(2))
            if 'mw' in query_lower[range_match.start():range_match.end()]:
                min_cap *= 1000
                max_cap *= 1000
            search_params['min_capacity_kw'] = min_cap
            search_params['max_capacity_kw'] = max_cap
        else:
            # Single capacity value
            capacity_match = re.search(r'(\d+)\s*(?:kw|mw)', query_lower)
            if capacity_match:
                capacity = int(capacity_match.group(1))
                if 'mw' in query_lower:
                    capacity *= 1000
                if 'over' in query_lower or 'above' in query_lower:
                    search_params['min_capacity_kw'] = capacity
                else:
                    search_params['max_capacity_kw'] = capacity
        
        # Location
        locations = {
            'aberdeen': 'aberdeen',
            'edinburgh': 'edinburgh',
            'glasgow': 'glasgow',
            'yorkshire': 'yorkshire',
            'scotland': 'scotland',
            'wales': 'wales'
        }
        
        for keyword, location_value in locations.items():
            if keyword in query_lower:
                search_params['location'] = location_value
                break
        
        return {
            'is_followup': is_followup and len(session.get('last_results', [])) > 0,
            'intent': intent,
            'search_params': search_params,
            'reasoning': 'Fallback rule-based understanding'
        }
    
    def _search_database(self, query: str, params: Dict) -> List[Dict]:
        """Search the ChromaDB database"""
        results = self.fit_api.natural_language_query(query, max_results=50)
        
        logger.info(f"Database returned {len(results.get('commercial_results', []))} results")
        logger.info(f"Filtering with params: {params}")
        
        filtered_results = []
        for result in results.get('commercial_results', []):
            metadata = result.get('metadata', {})
            
            # Apply filters
            if params.get('technology'):
                if params['technology'].lower() not in metadata.get('technology', '').lower():
                    continue
            
            if params.get('min_capacity_kw'):
                if metadata.get('capacity_kw', 0) < params['min_capacity_kw']:
                    continue
            
            if params.get('max_capacity_kw'):
                if metadata.get('capacity_kw', 0) > params['max_capacity_kw']:
                    continue
            
            if params.get('location'):
                location = params['location'].lower()
                postcode = metadata.get('postcode', '').lower()
                
                # Map location names to postcode prefixes
                location_mappings = {
                    'aberdeen': ['ab'],
                    'edinburgh': ['eh'],
                    'glasgow': ['g'],
                    'yorkshire': ['yo', 'hu', 'ls', 'bd', 'hx', 'hd', 'wf', 's', 'dn'],
                    'wales': ['cf', 'np', 'll', 'sa', 'ld', 'sy'],
                    'scotland': ['ab', 'dd', 'dg', 'eh', 'fk', 'g', 'hs', 'iv', 'ka', 'kw', 'ky', 'ml', 'pa', 'ph', 'td', 'ze']
                }
                
                if location in location_mappings:
                    valid_prefixes = location_mappings[location]
                    if not any(postcode.startswith(prefix) for prefix in valid_prefixes):
                        continue
                elif location not in postcode:
                    continue
            
            filtered_results.append(result)
        
        return filtered_results[:10]
    
    def _format_response(self, results: List[Dict], understanding: Dict) -> str:
        """Format response based on results"""
        
        if not results:
            return "I couldn't find any FIT installations matching your criteria."
        
        response = f"Found {len(results)} matching sites:\n\n"
        
        for i, result in enumerate(results[:10], 1):
            metadata = result.get('metadata', {})
            fit_id = metadata.get('fit_id') or metadata.get('installation_id') or f"AUTO{1000+i}"
            
            response += f"{i}. {metadata.get('technology', 'Unknown')} (FIT ID: {fit_id})\n"
            response += f"   • Capacity: {metadata.get('capacity_kw', 0):,.0f} kW\n"
            response += f"   • Location: {metadata.get('postcode', 'Unknown')}\n"
            response += f"   • Commissioned: {metadata.get('commission_date', 'Unknown')}\n\n"
        
        return response
    
    def _calculate_income_response(self, results: List[Dict]) -> str:
        """Calculate and format income for results"""
        response = "FIT Income Analysis:\n\n"
        total_income = 0
        
        for i, result in enumerate(results[:10], 1):
            metadata = result.get('metadata', {})
            fit_id = metadata.get('fit_id') or f"AUTO{1000+i}"
            capacity = metadata.get('capacity_kw', 0)
            rate = metadata.get('tariff_p_kwh', 0)
            
            # Simple calculation
            annual_generation = capacity * 1000
            annual_income = (annual_generation * rate) / 100
            total_income += annual_income
            
            response += f"{i}. FIT ID {fit_id}: £{annual_income:,.2f}/year\n"
        
        response += f"\nTotal Annual Income: £{total_income:,.2f}"
        return response
    
    def _format_detailed_response(self, results: List[Dict]) -> str:
        """Format detailed information about results"""
        response = "Detailed Information:\n\n"
        
        for i, result in enumerate(results[:10], 1):
            metadata = result.get('metadata', {})
            fit_id = metadata.get('fit_id') or f"AUTO{1000+i}"
            
            response += f"{i}. FIT ID: {fit_id}\n"
            response += f"   • Technology: {metadata.get('technology', 'Unknown')}\n"
            response += f"   • Capacity: {metadata.get('capacity_kw', 0):,.0f} kW\n"
            response += f"   • Location: {metadata.get('postcode', 'Unknown')}\n"
            response += f"   • Commissioned: {metadata.get('commission_date', 'Unknown')}\n"
            response += f"   • FIT Rate: {metadata.get('tariff_p_kwh', 0)}p/kWh\n"
            response += f"   • Repowering Window: {metadata.get('repowering_window', 'N/A')}\n\n"
        
        return response
    
    def _format_fit_ids_response(self, results: List[Dict]) -> str:
        """Format just the FIT IDs"""
        response = "FIT IDs from search:\n\n"
        
        for i, result in enumerate(results[:10], 1):
            metadata = result.get('metadata', {})
            fit_id = metadata.get('fit_id') or f"AUTO{1000+i}"
            tech = metadata.get('technology', 'Unknown')
            capacity = metadata.get('capacity_kw', 0)
            
            response += f"{i}. FIT ID {fit_id}: {tech} - {capacity:,.0f} kW\n"
        
        return response