#!/usr/bin/env python3
"""
LLM-Enhanced FIT Chatbot with GPT-OSS
Combines GPT-OSS understanding with factual database search
"""

import json
import requests
import logging
from typing import Dict, List, Any, Optional
from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI
from session_manager import SessionManager
import re
from capacity_parser import parse_capacity_range
from postcode_filter import enforce_postcode_prefix, get_location_from_query
from technology_sanitizer import sanitize_technology
from enhanced_query_parser import EnhancedQueryParser
from fit_query_optimizer import (
    build_where_clause, enforce_postcode_prefixes, 
    enrich_result_with_financials, merge_search_params,
    format_result_for_display
)
from warm_index import WarmIndex
from location_detector import detect_location_change, prefixes_for
from financial_calculator import render_result

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class LLMEnhancedFITChatbot:
    """Hybrid chatbot using LLM for understanding, database for facts"""
    
    def __init__(self, model: str = "fit-intelligence-enhanced"):
        self.fit_api = EnhancedFITIntelligenceAPI()
        self.session_manager = SessionManager()
        self.enhanced_parser = EnhancedQueryParser()  # Add enhanced parser
        self.model = model
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Initialize warm index for reliable geo filtering
        try:
            logger.info("Initializing warm index...")
            from sentence_transformers import SentenceTransformer
            embedder = SentenceTransformer('all-MiniLM-L6-v2')
            # Use the commercial_fit_sites collection
            import chromadb
            client = chromadb.PersistentClient(path="chroma_db")
            collection = client.get_collection("commercial_fit_sites")
            self.warm_index = WarmIndex(collection, embedder)
            logger.info("Warm index ready")
            
            # Initialize market analyst for comparative queries
            from market_analyst import MarketAnalyst
            self.market_analyst = MarketAnalyst(self.warm_index)
            logger.info("Market analyst ready")
        except Exception as e:
            logger.warning(f"Could not initialize warm index: {e}")
            self.warm_index = None
        
        # Verify model is available
        if not self._check_model_availability():
            logger.warning(f"Model {model} not found or too slow, trying fallback models...")
            # Try fallback models - use available models
            for fallback in ["llama2:13b", "phi3:medium", "llama3.2:1b"]:
                if self._check_model_availability(fallback):
                    self.model = fallback
                    logger.info(f"Using fallback model: {fallback}")
                    break
            else:
                logger.warning("No suitable model found, will use fallback understanding only")
    
    def _check_model_availability(self, model: str = None) -> bool:
        """Check if a model is available in Ollama"""
        try:
            check_model = model or self.model
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                # Check both with and without :latest suffix
                return check_model in models or f"{check_model}:latest" in models
        except:
            return False
        return False
    
    def chat(self, query: str, session_id: str = "default", limit: int = 10) -> str:
        """Process query using enhanced parser + LLM for understanding and database for facts"""
        try:
            # Step 1: Get session context
            session = self.session_manager.get_session(session_id)
            
            # Step 2: Try enhanced parser first for better accuracy
            parsed_params = self.enhanced_parser.parse(query)
            if parsed_params:
                logger.info(f"Enhanced parser extracted: {parsed_params}")

                # Use limit from parsed parameters if available
                if 'limit' in parsed_params:
                    limit = parsed_params['limit']
                    logger.info(f"Using parsed limit: {limit}")

                # Build understanding from parsed params
                understanding = {
                    'is_followup': False,  # Enhanced parser handles new queries
                    'intent': 'search_new',
                    'search_params': parsed_params,
                    'reasoning': 'Parsed with enhanced accuracy'
                }
            else:
                # Fall back to LLM if parser didn't extract anything
                understanding = self._understand_with_llm(query, session)
            
            logger.info(f"Query understanding: {understanding}")
            
            # Step 3: Check for analytical queries first
            if hasattr(self, 'market_analyst') and any(word in query.lower() for word in ['compar', 'vs', 'versus', 'total', 'aggregate', 'average', 'analyz', 'analys']):
                analysis = self.market_analyst.analyze_comparative(query, parsed_params or understanding.get('search_params', {}))
                if analysis:
                    response = self.market_analyst.format_analysis_response(analysis)
                    if response:
                        # Store in session for follow-ups
                        session['last_query'] = query
                        session['last_analysis'] = analysis
                        self.session_manager.update(session_id, last_query=query, last_analysis=analysis)
                        return response
            
            # Step 4: Decide action based on understanding
            if understanding.get('is_followup') and session.get('last_results'):
                # Use previous results ONLY if they exist
                logger.info(f"Using previous {len(session['last_results'])} results for follow-up query")
                results = session['last_results']
                
                # Apply any additional processing requested
                if understanding.get('intent') == 'calculate_income':
                    return self._calculate_income_response(results, limit)
                elif understanding.get('intent') == 'get_details':
                    return self._format_detailed_response(results, limit)
                elif understanding.get('intent') == 'get_fit_ids':
                    return self._format_fit_ids_response(results, limit)
            else:
                # New search needed - but preserve context from previous queries
                new_params = understanding.get('search_params', {})
                previous_params = session.get('search_params', {})
                
                # Merge parameters to preserve context
                search_params = merge_search_params(previous_params, new_params)
                logger.info(f"Performing new search with merged params: {search_params}")
                
                # Search the database
                results = self._search_database(query, search_params, limit)
                
                # Store in session for follow-ups
                self.session_manager.store_results(session_id, query, results, search_params)
            
            # Step 4: Use LLM to format natural response
            response = self._generate_response_with_llm(query, results, understanding, limit)
            
            return response
            
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return f"I encountered an error processing your query. Please try rephrasing."
    
    def _understand_with_llm(self, query: str, session: Dict) -> Dict:
        """Use LLM to understand query intent and extract parameters"""
        
        prompt = f"""Analyze this renewable energy query and determine:
1. Is this a follow-up to previous results? Look for words like "their", "those", "these", "give me details"
2. What is the intent? (search_new, get_details, calculate_income, get_fit_ids, compare, filter_previous)
3. Extract parameters if it's a new search

Current query: "{query}"
Previous query: "{session.get('last_query', 'None')}"
Has previous results: {len(session.get('last_results', [])) > 0}

IMPORTANT: If the query says "give me all the details" or similar, this is asking for MORE DETAILS about PREVIOUS results, not a new search.

REPOWERING CATEGORIES (based on years left on FIT contract):
- "optimal" or "optimum" = sites with 5-10 years left (OPTIMAL window for planning)
- "urgent" = sites with 2-5 years left (URGENT action needed)
- "immediate" = sites with 0-2 years left (IMMEDIATE action required)
- "expired" = sites already past FIT expiry

If query mentions these terms, it's filtering by repowering status, not just describing sites.

Respond in JSON with this EXACT format (use single values, not pipe-separated):
{{
    "is_followup": true or false,
    "intent": "search_new" or "get_details" or "calculate_income" or "get_fit_ids",
    "search_params": {{
        "technology": "wind" or "solar" or "hydro" or null,
        "location": "yorkshire" or "scotland" or null,
        "min_capacity_kw": 500 or null,
        "max_capacity_kw": 1000 or null
    }},
    "reasoning": "brief explanation"
}}

Example: For "wind farms in yorkshire over 500kw":
{{
    "is_followup": false,
    "intent": "search_new",
    "search_params": {{
        "technology": "wind",
        "location": "yorkshire", 
        "min_capacity_kw": 500,
        "max_capacity_kw": null
    }},
    "reasoning": "New search for wind farms"
}}"""
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": 0.1,  # Very low for consistency
                    "stream": False,
                    "format": "json"
                },
                timeout=15  # Balanced timeout for 13B models
            )
            
            if response.status_code == 200:
                result = response.json()
                parsed = json.loads(result['response'])
                
                # Clean up malformed LLM responses with pipe separators
                if 'search_params' in parsed:
                    params = parsed['search_params']
                    
                    # Fix technology field with sanitizer
                    if 'technology' in params:
                        params['technology'] = sanitize_technology(params['technology'])
                    
                    # Fix location field with pipes or other issues
                    if 'location' in params:
                        loc_value = str(params['location'])
                        
                        # Handle pipe separators
                        if '|' in loc_value:
                            loc_value = loc_value.split('|')[0].strip()
                        
                        # Extract actual location from phrases like "north east of aberdeen over 225kw"
                        location_keywords = ['aberdeen', 'edinburgh', 'glasgow', 'yorkshire', 'scotland', 'wales']
                        for keyword in location_keywords:
                            if keyword in loc_value.lower():
                                params['location'] = keyword
                                break
                        else:
                            # Check for invalid values
                            if loc_value in ['location string', 'null', 'None'] or 'kw' in loc_value.lower():
                                params['location'] = None
                            elif len(loc_value) > 20:  # Too long to be a valid location
                                params['location'] = None
                    
                    # Fix intent field with pipes
                    if 'intent' in parsed and '|' in str(parsed['intent']):
                        parsed['intent'] = str(parsed['intent']).split('|')[0].strip()
                    
                    # Validate that we got complete capacity parsing
                    # If query mentions "less than" or "under" but max_capacity is missing, fallback
                    if ('less than' in query.lower() or 'under' in query.lower()) and \
                       'max_capacity_kw' not in params:
                        logger.info("LLM failed to parse max_capacity, using fallback")
                        return self._fallback_understanding(query, session)
                
                return parsed
            else:
                # Fallback to rule-based detection
                return self._fallback_understanding(query, session)
                
        except Exception as e:
            logger.error(f"LLM understanding failed: {e}")
            return self._fallback_understanding(query, session)
    
    def _fallback_understanding(self, query: str, session: Dict) -> Dict:
        """Rule-based fallback if LLM fails"""
        query_lower = query.lower()
        
        # Check for follow-up indicators
        followup_phrases = ['their', 'those', 'these', 'give me details', 'all the details', 
                           'more information', 'calculate income', 'fit income', 'can you give me', 
                           'the fit rate', 'years of fit', 'annual income']
        is_followup = any(phrase in query_lower for phrase in followup_phrases)
        print(f"[FALLBACK DEBUG] Query: '{query_lower}'")
        print(f"[FALLBACK DEBUG] is_followup: {is_followup}, has results: {len(session.get('last_results', [])) > 0}")
        
        # Determine intent
        intent = 'search_new'
        if 'detail' in query_lower:
            intent = 'get_details'
        elif 'income' in query_lower or 'revenue' in query_lower:
            intent = 'calculate_income'
        elif 'fit id' in query_lower:
            intent = 'get_fit_ids'
        
        # Extract search parameters
        search_params = {}
        
        # Technology
        if 'wind' in query_lower:
            search_params['technology'] = 'wind'
        elif 'solar' in query_lower or 'photovoltaic' in query_lower:
            search_params['technology'] = 'solar'
        elif 'hydro' in query_lower:
            search_params['technology'] = 'hydro'
        
        # Capacity - use robust parser
        min_cap, max_cap = parse_capacity_range(query_lower)
        print(f"[FALLBACK DEBUG] Capacity parser returned: min={min_cap}, max={max_cap}")
        if min_cap is not None:
            search_params['min_capacity_kw'] = min_cap
        if max_cap is not None:
            search_params['max_capacity_kw'] = max_cap
        print(f"[FALLBACK DEBUG] Search params after capacity: {search_params}")
        
        # Location - extract any location mentioned
        # Common UK locations and regions
        from uk_postcodes import UK_POSTCODE_PREFIXES, REGIONS
        
        # Check for specific cities/locations
        for location_name in UK_POSTCODE_PREFIXES.keys():
            if location_name.replace('_', ' ') in query_lower:
                search_params['location'] = location_name
                break
        else:
            # Check for regions
            for region_name in REGIONS.keys():
                if region_name.replace('_', ' ') in query_lower:
                    search_params['location'] = region_name
                    break
            else:
                # Check for country names
                if any(country in query_lower for country in ['england', 'scotland', 'wales', 'northern ireland']):
                    for country in ['england', 'scotland', 'wales', 'northern_ireland']:
                        if country.replace('_', ' ') in query_lower:
                            search_params['location'] = country
                            break
        
        result = {
            'is_followup': is_followup and len(session.get('last_results', [])) > 0,
            'intent': intent,
            'search_params': search_params,
            'reasoning': 'Fallback rule-based understanding'
        }
        logger.info(f"Fallback returning: {result}")
        return result
    
    def _search_database(self, query: str, params: Dict, limit: int = 10) -> List[Dict]:
        """Search using warm index for guaranteed geographic accuracy"""
        # Check for location change in follow-up
        loc_change = detect_location_change(query)
        if loc_change:
            params = merge_search_params(params, loc_change)
            logger.info(f"Detected location change: {loc_change}")
        
        # Use warm index if available
        if self.warm_index:
            # Get search parameters
            technology = sanitize_technology(params.get('technology'))
            min_kw = params.get('min_capacity_kw')
            max_kw = params.get('max_capacity_kw')
            
            # Get postcode areas for exact matching
            # Use areas directly if provided by enhanced parser
            areas = params.get('postcode_areas', [])
            
            if not areas:
                # Fall back to location-based extraction
                location = params.get('location')
                if location:
                    location_lower = location.lower()
                    if location_lower == 'yorkshire':
                        # Use Yorkshire areas from fit_query_optimizer
                        from fit_query_optimizer import YORKSHIRE_AREAS
                        areas = YORKSHIRE_AREAS
                    else:
                        # Get prefixes and extract areas
                        prefixes = prefixes_for(location)
                        if prefixes:
                            # Extract area part (letters only) from each prefix
                            from fit_query_optimizer import extract_postcode_area
                            areas = list(set(extract_postcode_area(p) for p in prefixes if p))
                            areas = [a for a in areas if a]
            
            # Add area hint to query for better vector search
            hint = ""
            if areas:
                hint = " " + " ".join([f"{a} postcode area" for a in areas[:3]])
                logger.info(f"Using postcode areas: {areas}")
            
            # Get repowering window filter
            # Use repowering_category from enhanced parser if available
            repowering_window = params.get('repowering_category')
            
            if repowering_window:
                repowering_window = repowering_window.upper()
                logger.info(f"Using repowering filter: {repowering_window}")
            else:
                # Fall back to detecting from query text
                query_lower = query.lower()
                if 'optimal' in query_lower or 'optimum' in query_lower:
                    repowering_window = 'OPTIMAL'  # 5-10 years left
                    logger.info(f"Detected OPTIMAL repowering filter")
                elif 'urgent' in query_lower:
                    repowering_window = 'URGENT'  # 2-5 years left
                    logger.info(f"Detected URGENT repowering filter")
                elif 'immediate' in query_lower:
                    repowering_window = 'IMMEDIATE'  # 0-2 years left
                    logger.info(f"Detected IMMEDIATE repowering filter")
                elif 'expired' in query_lower:
                    repowering_window = 'EXPIRED'  # Already expired
                    logger.info(f"Detected EXPIRED repowering filter")
            
            # Get years_left range from parameters
            min_years_left = params.get('min_years_left')
            max_years_left = params.get('max_years_left')
            
            if min_years_left is not None or max_years_left is not None:
                logger.info(f"Using years_left filter: {min_years_left} to {max_years_left} years")
            
            # Search with warm index using exact area matching
            results = self.warm_index.search(
                query + hint,
                areas=areas,  # Use areas instead of prefixes
                technology=technology,
                min_kw=min_kw,
                max_kw=max_kw,
                repowering_window=repowering_window,
                min_years_left=min_years_left,
                max_years_left=max_years_left,
                top_k=max(50, limit * 2)  # Use at least 50 or double the limit
            )
            
            logger.info(f"Warm index returned {len(results)} results")
            
            # Check if detailed view requested
            detailed_view = any(word in query.lower() for word in [
                'detail', 'full', 'breakdown', 'both', 'standard', 'regional', 
                'drill', 'variance', 'capacity factor'
            ])
            
            # Final area validation and render
            filtered_results = []
            for i, (score, doc_id, metadata) in enumerate(results):
                # Area filtering already done by warm index, just render
                if detailed_view:
                    from financial_calculator import render_result_detailed
                    rendered = render_result_detailed(metadata)
                    logger.info(f"Using detailed view for result {i+1}")
                else:
                    from financial_calculator import render_result_summary
                    rendered = render_result_summary(metadata)
                    logger.info(f"Using summary view for result {i+1}")
                rendered['score'] = float(score)
                filtered_results.append({'metadata': rendered})
            
            return filtered_results[:limit]
        else:
            # Fallback to original search method
            logger.warning("Warm index not available, using original search")
            return self._search_database_original(query, params)
    
    def _search_database_original(self, query: str, params: Dict) -> List[Dict]:
        """Original search method with query enhancement"""
        # Enhance query with postcode hints
        from query_enhancer import enhance_query_with_postcodes
        location = params.get('location')
        if location:
            query = enhance_query_with_postcodes(query, location)
            logger.info(f"Enhanced query: {query}")
        
        results = self.fit_api.natural_language_query(query, max_results=50)
        filtered_results = []
        for result in results.get('commercial_results', []):
            metadata = result.get('metadata', {})
            if params.get('technology'):
                if params['technology'].lower() not in metadata.get('technology', '').lower():
                    continue
            if params.get('min_capacity_kw'):
                if metadata.get('capacity_kw', 0) < params['min_capacity_kw']:
                    continue
            if params.get('max_capacity_kw'):
                if metadata.get('capacity_kw', 0) > params['max_capacity_kw']:
                    continue
            # Use financial calculator for proper financial data
            from financial_calculator import render_result
            rendered = render_result(metadata)
            filtered_results.append({'metadata': rendered})
        if params.get('location'):
            filtered_results = enforce_postcode_prefixes(filtered_results, params['location'])
        return filtered_results[:limit]

    def process_query(self, query: str, session_id: str = "system") -> Dict[str, Any]:
        """Lightweight query endpoint that returns structured results for UIs.
        It bypasses LLM response formatting and just returns vector-search results.
        """
        try:
            # Use enhanced parser to extract parameters; fall back to minimal
            parsed_params = self.enhanced_parser.parse(query) or {}
            results = self._search_database(query, parsed_params)
            # Store in session for potential follow-ups
            self.session_manager.store_results(session_id, query, results, parsed_params)
            return {"results": results, "query": query}
        except Exception as e:
            logger.error(f"process_query failed: {e}")
            return {"results": [], "error": str(e)}
    
    def _generate_response_with_llm(self, query: str, results: List[Dict], understanding: Dict, limit: int = 10) -> str:
        """Use LLM to generate natural language response"""
        
        if not results:
            return "I couldn't find any FIT installations matching your criteria."
        
        # Calculate ALL results for summary statistics
        from financial_calculator import render_result_summary
        all_results_data = []
        total_annual_income = 0
        total_capacity_mw = 0
        
        for result in results:
            metadata = result.get('metadata', {})
            formatted = render_result_summary(metadata)
            all_results_data.append(formatted)
            # Sum up totals
            if formatted.get('annual_income_gbp'):
                total_annual_income += formatted['annual_income_gbp']
            if formatted.get('capacity_kw'):
                total_capacity_mw += formatted['capacity_kw'] / 1000
        
        # Prepare results for display
        results_summary = []
        for i, formatted in enumerate(all_results_data[:limit], 1):
            formatted['number'] = i
            # Ensure FIT ID is always present
            if not formatted.get('fit_id'):
                formatted['fit_id'] = f"AUTO{1000+i}"
            results_summary.append(formatted)
        
        # Create summary statistics
        summary_stats = {
            "total_sites": len(results),
            "total_annual_income_gbp": round(total_annual_income, 2),
            "total_capacity_mw": round(total_capacity_mw, 2),
            "showing_top": min(limit, len(results))
        }
        
        prompt = f"""Generate a helpful response for this FIT database query.

User Query: "{query}"
Intent: {understanding.get('intent')}
Summary Statistics: {json.dumps(summary_stats)}

Top {min(limit, len(results))} Results (of {len(results)} total):
{json.dumps(results_summary, indent=2)}

STRICT RULES:
1. ALWAYS start with summary: "Found X sites with total annual income of £Y"
2. Only use data from the provided results
3. ALWAYS include FIT IDs for each site
4. CRITICAL: Use the EXACT years_left value from the data (e.g., if data shows years_left: 8.0, display "Years Left: 8.0")
5. If showing capacity, use format: X,XXX kW
6. Never invent data not in the results
7. FIT tariff rates in pence per kWh (e.g., "12.47p/kWh")
8. Annual income and total remaining value in pounds (e.g., "£12,345.67")
9. NEVER show "Years Left: 0" unless the data explicitly shows years_left: 0
10. If more than {limit} results, mention "Showing top {limit} of X sites"

Generate the response:"""
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": 0.1,
                    "stream": False
                },
                timeout=15  # Balanced timeout for 13B models
            )
            
            if response.status_code == 200:
                return response.json()['response']
            else:
                # Fallback to simple formatting
                return self._fallback_format_response(results, limit)
                
        except Exception as e:
            logger.error(f"LLM response generation failed: {e}")
            return self._fallback_format_response(results)
    
    def _fallback_format_response(self, results: List[Dict], limit: int = 10) -> str:
        """Simple fallback formatting if LLM fails - includes financials"""
        if not results:
            return "I couldn't find any FIT installations matching your criteria."
            
        response = f"Found {len(results)} matching sites:\n\n"
        
        for i, result in enumerate(results[:limit], 1):
            metadata = result.get('metadata', {})
            fit_id = metadata.get('fit_id') or metadata.get('installation_id') or f"AUTO{1000+i}"
            
            response += f"{i}. {metadata.get('technology', 'Unknown')} (FIT ID: {fit_id})\n"
            response += f"   • Capacity: {metadata.get('capacity_kw', 0):,.0f} kW\n"
            response += f"   • Location: {metadata.get('postcode', 'Unknown')}\n"
            response += f"   • Commissioned: {metadata.get('commission_date', 'Unknown')}\n"
            
            # Show financial data
            tariff = metadata.get('tariff_p_kwh', 0)
            response += f"   • FIT Rate: {tariff}p/kWh\n"
            
            years = metadata.get('years_left')
            if years is not None and years > 0:
                response += f"   • Years Left: {years:.1f}\n"
            elif years is not None and years <= 0:
                response += f"   • Years Left: Expired\n"
            else:
                response += f"   • Years Left: N/A (no commission date)\n"
            
            income = metadata.get('annual_income_gbp')
            if income is not None:
                response += f"   • Annual Income: £{income:,.2f}\n\n"
            else:
                response += f"   • Annual Income: N/A\n\n"
        
        return response
    
    def _calculate_income_response(self, results: List[Dict], limit: int = 10) -> str:
        """Calculate and format income for results"""
        response = "FIT Income Analysis:\n\n"
        total_income = 0
        
        for i, result in enumerate(results[:limit], 1):
            metadata = result.get('metadata', {})
            fit_id = metadata.get('fit_id') or f"AUTO{1000+i}"
            capacity = metadata.get('capacity_kw', 0)
            rate = metadata.get('tariff_p_kwh', 0)
            
            # Simple calculation (would need real capacity factors)
            annual_generation = capacity * 1000  # Simplified
            annual_income = (annual_generation * rate) / 100
            total_income += annual_income
            
            response += f"{i}. FIT ID {fit_id}: £{annual_income:,.2f}/year\n"
        
        response += f"\nTotal Annual Income: £{total_income:,.2f}"
        return response
    
    def _format_detailed_response(self, results: List[Dict], limit: int = 10) -> str:
        """Format detailed information about results with full financial data"""
        from financial_calculator import render_result_detailed
        response = "Detailed Information with Financial Analysis:\n\n"
        
        for i, result in enumerate(results[:limit], 1):
            metadata = result.get('metadata', {})
            
            # Use detailed render to get all financial fields
            detailed = render_result_detailed(metadata)
            
            fit_id = detailed.get('fit_id') or f"AUTO{1000+i}"
            response += f"{i}. FIT ID: {fit_id}\n"
            response += f"   • Technology: {detailed.get('technology', 'Unknown')}\n"
            response += f"   • Capacity: {detailed.get('capacity_kw', 0):,.0f} kW\n"
            response += f"   • Location: {detailed.get('postcode', 'Unknown')}\n"
            response += f"   • Commissioned: {detailed.get('commission_date', 'Unknown')}\n"
            response += f"   • FIT Rate: {detailed.get('tariff_p_kwh', 0)}p/kWh\n"
            response += f"   • FIT Expiry: {detailed.get('fit_expiry_date', 'N/A')}\n"
            response += f"   • Years Left: {detailed.get('years_left', 'N/A')}\n"
            standard_income = detailed.get('annual_income_standard', 0)
            regional_income = detailed.get('annual_income_regional', 0)
            total_value = detailed.get('total_remaining_value', 0)
            regional_cf = detailed.get('regional_capacity_factor')
            
            response += f"   • Standard Annual Income: £{standard_income:,.2f}" if standard_income else "   • Standard Annual Income: N/A\n"
            if not standard_income: response += "\n"
            response += f"   • Regional Annual Income: £{regional_income:,.2f}" if regional_income else "   • Regional Annual Income: N/A\n"
            if not regional_income: response += "\n"
            response += f"   • Regional Capacity Factor: {regional_cf:.2%}\n" if regional_cf else "   • Regional Capacity Factor: N/A\n"
            response += f"   • Total Remaining Value: £{total_value:,.2f}" if total_value else "   • Total Remaining Value: N/A\n"
            if not total_value: response += "\n"
            response += f"   • Repowering Window: {detailed.get('repowering_window', 'N/A')}\n\n"
        
        return response
    
    def _format_fit_ids_response(self, results: List[Dict], limit: int = 10) -> str:
        """Format just the FIT IDs"""
        response = "FIT IDs from search:\n\n"
        
        for i, result in enumerate(results[:limit], 1):
            metadata = result.get('metadata', {})
            fit_id = metadata.get('fit_id') or f"AUTO{1000+i}"
            tech = metadata.get('technology', 'Unknown')
            capacity = metadata.get('capacity_kw', 0)
            
            response += f"{i}. FIT ID {fit_id}: {tech} - {capacity:,.0f} kW\n"
        
        return response
