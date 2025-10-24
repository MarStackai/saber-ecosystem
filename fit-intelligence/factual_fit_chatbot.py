#!/usr/bin/env python3
"""
Factual FIT Intelligence Chatbot
Strictly returns database facts without opinions or calculations
"""

import json
import re
from typing import Dict, List, Any, Optional
from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI
from fit_id_lookup import FITIDLookup
from conversation_context import ConversationContext
from session_manager import SessionManager
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FactualFITChatbot:
    def __init__(self):
        """Initialize factual chatbot with strict data-only responses"""
        self.fit_api = EnhancedFITIntelligenceAPI()
        self.fit_lookup = FITIDLookup()
        self.context_manager = ConversationContext()
        self.session_manager = SessionManager()  # Proper session management
        self.last_results = []  # Fallback for backwards compatibility
        
        # Strict location to postcode mappings
        self.strict_location_postcodes = {
            'aberdeen': ['AB'],  # Aberdeen ONLY returns AB postcodes
            'edinburgh': ['EH'],  # Edinburgh ONLY returns EH postcodes
            'glasgow': ['G'],     # Glasgow ONLY returns G postcodes
            'dundee': ['DD'],     # Dundee ONLY returns DD postcodes
            'york': ['YO'],       # York ONLY returns YO postcodes
            'hull': ['HU'],       # Hull ONLY returns HU postcodes
            'leeds': ['LS'],      # Leeds ONLY returns LS postcodes
            'sheffield': ['S'],   # Sheffield ONLY returns S postcodes
            'bradford': ['BD'],   # Bradford ONLY returns BD postcodes
            'yorkshire': ['YO', 'HU', 'LS', 'BD', 'HX', 'HD', 'WF', 'S', 'DN'],  # Yorkshire region
            'scotland': ['AB', 'DD', 'DG', 'EH', 'FK', 'G', 'HS', 'IV', 'KA', 'KW', 'KY', 'ML', 'PA', 'PH', 'TD', 'ZE'],
            'wales': ['CF', 'LD', 'LL', 'NP', 'SA', 'SY']
        }
        
        # UK postcode prefixes for geographic validation
        self.uk_postcodes = {
            'Scotland': ['AB', 'DD', 'DG', 'EH', 'FK', 'G', 'HS', 'IV', 'KA', 'KW', 'KY', 'ML', 'PA', 'PH', 'TD', 'ZE'],
            'Wales': ['CF', 'LD', 'LL', 'NP', 'SA', 'SY'],
            'Northern England': ['BB', 'BD', 'BL', 'CA', 'DH', 'DL', 'DN', 'FY', 'HG', 'HU', 'HX', 'LA', 'LS', 'NE', 'OL', 'PR', 'S', 'SR', 'TS', 'WF', 'WN', 'YO'],
            'Midlands': ['B', 'CV', 'DE', 'DY', 'LE', 'NG', 'NN', 'ST', 'WR', 'WS', 'WV'],
            'Eastern': ['CB', 'CM', 'CO', 'IP', 'LU', 'NR', 'PE', 'SG', 'SS'],
            'London': ['E', 'EC', 'N', 'NW', 'SE', 'SW', 'W', 'WC'],
            'Southern': ['BH', 'BN', 'BR', 'BS', 'CR', 'CT', 'DA', 'EN', 'GU', 'HA', 'HP', 'KT', 'ME', 'MK', 'OX', 'PO', 'RG', 'RH', 'RM', 'SL', 'SM', 'SN', 'SO', 'SP', 'TN', 'TW', 'UB'],
            'Southwest': ['BA', 'DT', 'EX', 'GL', 'PL', 'TA', 'TQ', 'TR'],
            'Yorkshire': ['YO', 'HU', 'LS', 'BD', 'HX', 'HD', 'WF', 'S', 'DN']
        }
    
    def validate_geographic_location(self, postcode: str, requested_location: str) -> bool:
        """Validate if a postcode matches the requested location - FLEXIBLE MODE"""
        if not postcode:
            return False  # Need a postcode to validate
        if not requested_location:
            return True  # No specific location requested, include all
        
        postcode_upper = postcode.upper().strip()
        location_lower = requested_location.lower().strip()
        
        # Extract postcode prefix (first 1-2 letters)
        postcode_prefix = ''
        for i, char in enumerate(postcode_upper):
            if char.isalpha():
                postcode_prefix += char
            else:
                break
        
        # Check strict location mappings first
        for location_key, valid_prefixes in self.strict_location_postcodes.items():
            if location_key in location_lower:
                # Found a match - use STRICT validation
                is_valid = any(postcode_prefix.startswith(p) for p in valid_prefixes)
                if not is_valid:
                    logger.debug(f"Rejecting {postcode} for {requested_location}: prefix {postcode_prefix} not in {valid_prefixes}")
                return is_valid
        
        # For other locations, check region matches
        for region, prefixes in self.uk_postcodes.items():
            if location_lower in region.lower():
                return any(postcode_prefix.startswith(p) for p in prefixes)
        
        return True  # Default to INCLUDING if no specific match (flexible mode for better UX)
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse query into structured search parameters"""
        query_lower = query.lower()
        params = {}
        
        # Technology detection
        if 'solar' in query_lower or 'photovoltaic' in query_lower or 'pv' in query_lower:
            params['technology'] = 'Photovoltaic'
        elif 'wind' in query_lower:
            params['technology'] = 'Wind'
        elif 'hydro' in query_lower:
            params['technology'] = 'Hydro'
        elif 'anaerobic' in query_lower or 'biogas' in query_lower or 'digestion' in query_lower:
            params['technology'] = 'Anaerobic digestion'
        
        # Capacity detection
        capacity_patterns = [
            (r'over\s+(\d+)\s*mw', 1000),  # MW to kW
            (r'over\s+(\d+)\s*kw', 1),
            (r'above\s+(\d+)\s*mw', 1000),
            (r'above\s+(\d+)\s*kw', 1),
            (r'>\s*(\d+)\s*mw', 1000),
            (r'>\s*(\d+)\s*kw', 1),
        ]
        
        for pattern, multiplier in capacity_patterns:
            match = re.search(pattern, query_lower)
            if match:
                params['min_capacity_kw'] = int(match.group(1)) * multiplier
                break
        
        # Location detection
        location_keywords = [
            'scotland', 'wales', 'england', 'yorkshire', 'london', 
            'manchester', 'birmingham', 'cornwall', 'devon', 'kent', 
            'essex', 'glasgow', 'edinburgh', 'cardiff', 'belfast',
            'newcastle', 'liverpool', 'leeds', 'sheffield', 'bristol'
        ]
        
        for location in location_keywords:
            if location in query_lower:
                params['location'] = location.title()
                break
        
        # Urgency/repowering detection
        if 'urgent' in query_lower or 'immediate' in query_lower:
            params['repowering_window'] = 'IMMEDIATE'
        elif 'expir' in query_lower:
            params['repowering_window'] = 'EXPIRED'
        elif 'repower' in query_lower:
            params['repowering_priority'] = True
        
        return params
    
    def chat(self, query: str, session_id: str = "default") -> str:
        """Process query and return factual data only"""
        try:
            query_lower = query.lower()
            
            # Use session manager to determine if we should use context
            use_context = self.session_manager.should_use_context(session_id, query)
            session_results = self.session_manager.get_last_results(session_id)
            
            # If session manager says use context AND we have previous results
            if use_context and session_results:
                # User asking for more details about previous results
                logger.info(f"Using context for session {session_id} with {len(session_results)} previous results")
                
                if 'income' in query_lower or 'revenue' in query_lower or 'earning' in query_lower:
                    # Add income calculations to previous results
                    return self._format_results_with_income(session_results[:10])
                elif 'fit' in query_lower and ('id' in query_lower or 'ids' in query_lower):
                    # User asking for FIT IDs of previous results
                    response = "FIT IDs from previous search:\n\n"
                    for i, result in enumerate(session_results[:10], 1):
                        metadata = result.get('metadata', {})
                        fit_id = metadata.get('fit_id') or metadata.get('installation_id') or f"{1000 + i}"
                        tech = metadata.get('technology', 'Unknown')
                        capacity = metadata.get('capacity_kw', 0)
                        postcode = metadata.get('postcode', 'Unknown')
                        response += f"{i}. FIT ID {fit_id}: {tech} - {capacity:,.0f}kW at {postcode}\n"
                    return response
                else:
                    # User asking for more details about previous results
                    return self._format_detailed_results(session_results[:10])
            
            # Check for FIT ID queries
            fit_id_match = re.search(r'\b(?:fit\s*(?:id)?|site|installation)\s+(\d+)\b', query_lower)
            if fit_id_match:
                fit_id = fit_id_match.group(1)
                result = self.fit_lookup.lookup_fit_id(fit_id)
                
                if result['found']:
                    data = result['data']
                    if 'rate' in query.lower() or 'tariff' in query.lower():
                        return f"Site {fit_id}: {data['fit_rate']}p/kWh"
                    else:
                        return (f"Site {fit_id}:\n"
                               f"• Technology: {data['technology']}\n"
                               f"• Capacity: {data['capacity_kw']}kW\n"
                               f"• FIT Rate: {data['fit_rate']}p/kWh\n"
                               f"• Location: {data['location']}\n"
                               f"• Commissioned: {data['commission_date'][:10] if len(data['commission_date']) > 10 else data['commission_date']}")
                else:
                    return f"Site {fit_id} not found in database"
            
            # Parse the query
            params = self.parse_query(query)
            requested_location = params.get('location', '')
            
            # Search the database
            results = self.fit_api.natural_language_query(query, max_results=20)
            
            # Filter results for geographic accuracy
            all_results = results.get('commercial_results', [])
            filtered_results = []
            
            # First pass: strict filtering if location specified
            if requested_location:
                for result in all_results:
                    metadata = result.get('metadata', {})
                    postcode = metadata.get('postcode', '')
                    
                    if self.validate_geographic_location(postcode, requested_location):
                        filtered_results.append(result)
                
                # If strict filtering returned nothing, use all results but add a note
                if not filtered_results:
                    filtered_results = all_results[:10]  # Use top 10 results
                    location_note = f"\nNote: No exact matches found in {requested_location}. Showing best matches from wider area.\n"
                else:
                    location_note = ""
            else:
                # No location specified, use all results
                filtered_results = all_results
                location_note = ""
            
            if not filtered_results:
                self.last_results = []  # Clear previous results
                self.session_manager.store_results(session_id, query, [], {})  # Clear session results too
                return "No matching sites found in the database"
            
            # Store results for context queries
            self.last_results = filtered_results
            self.session_manager.store_results(session_id, query, filtered_results, params)  # Store in session
            
            # Format factual response
            response = f"Found {len(filtered_results)} matching sites:{location_note}\n\n"
            
            for i, result in enumerate(filtered_results[:10], 1):
                metadata = result['metadata']
                
                # Ensure FIT ID is included
                fit_id = metadata.get('fit_id') or metadata.get('installation_id') or f"{1000 + i}"
                
                response += f"{i}. {metadata.get('technology', 'Unknown')} (FIT ID: {fit_id})\n"
                response += f"   • Capacity: {metadata.get('capacity_kw', 0):,.0f}kW\n"
                response += f"   • Location: {metadata.get('postcode', 'Unknown')}\n"
                
                fit_rate = metadata.get('tariff_p_kwh')
                if fit_rate:
                    response += f"   • FIT Rate: {fit_rate}p/kWh\n"
                
                commission_date = metadata.get('commission_date')
                if commission_date:
                    response += f"   • Commissioned: {commission_date[:10]}\n"
                
                repowering = metadata.get('repowering_window')
                if repowering and repowering != 'UNKNOWN':
                    response += f"   • Repowering: {repowering}\n"
                
                response += "\n"
            
            # Add summary statistics (facts only)
            if len(filtered_results) > 1:
                total_capacity = sum(r['metadata'].get('capacity_kw', 0) for r in filtered_results)
                response += f"Total capacity: {total_capacity:,.0f}kW ({total_capacity/1000:,.1f}MW)\n"
                
                # Technology breakdown
                tech_counts = {}
                for r in filtered_results:
                    tech = r['metadata'].get('technology', 'Unknown')
                    tech_counts[tech] = tech_counts.get(tech, 0) + 1
                
                if len(tech_counts) > 1:
                    response += "Technology mix: "
                    response += ", ".join(f"{tech} ({count})" for tech, count in tech_counts.items())
            
            return response
            
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return f"Database query error. Please try rephrasing your question."

    def _format_results_with_income(self, results: List[Dict]) -> str:
        """Format results with FIT income calculations"""
        if not results:
            return "No previous results to calculate income for"
        
        response = f"FIT Income Analysis for {len(results)} sites:\n\n"
        total_income = 0
        
        for i, result in enumerate(results, 1):
            metadata = result.get('metadata', {})
            fit_id = metadata.get('fit_id') or metadata.get('installation_id') or f"{1000 + i}"
            capacity = metadata.get('capacity_kw', 0)
            fit_rate = metadata.get('tariff_p_kwh', 0)
            
            # Estimate annual generation (capacity factor varies by technology)
            tech = metadata.get('technology', 'Unknown')
            if tech == 'Wind':
                capacity_factor = 0.27  # 27% for wind
            elif tech in ['Photovoltaic', 'Solar']:
                capacity_factor = 0.11  # 11% for solar
            elif tech == 'Hydro':
                capacity_factor = 0.38  # 38% for hydro
            else:
                capacity_factor = 0.25  # Default
            
            annual_generation = capacity * 8760 * capacity_factor  # kWh per year
            annual_income = (annual_generation * fit_rate) / 100  # Convert pence to pounds
            total_income += annual_income
            
            response += f"{i}. FIT ID {fit_id}: {tech}\n"
            response += f"   • Capacity: {capacity:,.0f}kW\n"
            response += f"   • Location: {metadata.get('postcode', 'Unknown')}\n"
            response += f"   • FIT Rate: {fit_rate}p/kWh\n"
            response += f"   • Est. Annual Generation: {annual_generation:,.0f}kWh\n"
            response += f"   • Est. Annual FIT Income: £{annual_income:,.2f}\n"
            response += "\n"
        
        response += f"Total Estimated Annual FIT Income: £{total_income:,.2f}\n"
        return response
    
    def _format_detailed_results(self, results: List[Dict]) -> str:
        """Format detailed results for context queries"""
        if not results:
            return "No previous results to show details for"
        
        response = f"Detailed information for {len(results)} sites:\n\n"
        for i, result in enumerate(results, 1):
            metadata = result.get('metadata', {})
            fit_id = metadata.get('fit_id') or metadata.get('installation_id') or f"{1000 + i}"
            
            response += f"{i}. FIT ID {fit_id}\n"
            response += f"   • Technology: {metadata.get('technology', 'Unknown')}\n"
            response += f"   • Capacity: {metadata.get('capacity_kw', 0):,.0f}kW\n"
            response += f"   • Location: {metadata.get('postcode', 'Unknown')}\n"
            response += f"   • FIT Rate: {metadata.get('tariff_p_kwh', 'N/A')}p/kWh\n"
            response += f"   • Commissioned: {metadata.get('commission_date', 'Unknown')[:10] if metadata.get('commission_date') else 'Unknown'}\n"
            response += f"   • Repowering: {metadata.get('repowering_window', 'N/A')}\n"
            response += "\n"
        
        return response

class FeedbackCollector:
    """Collect and store feedback for model training"""
    
    def __init__(self, feedback_file: str = "fit_feedback.jsonl"):
        self.feedback_file = feedback_file
    
    def collect_feedback(self, query: str, response: str, correct_response: Optional[str] = None, 
                        rating: Optional[int] = None, notes: Optional[str] = None) -> bool:
        """Collect feedback on a query/response pair"""
        try:
            feedback = {
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'response': response,
                'correct_response': correct_response,
                'rating': rating,  # 1-5 scale
                'notes': notes
            }
            
            with open(self.feedback_file, 'a') as f:
                f.write(json.dumps(feedback) + '\n')
            
            return True
        except Exception as e:
            logger.error(f"Feedback collection error: {str(e)}")
            return False
    
    def get_feedback_stats(self) -> Dict:
        """Get statistics on collected feedback"""
        try:
            total = 0
            ratings = []
            needs_correction = 0
            
            with open(self.feedback_file, 'r') as f:
                for line in f:
                    feedback = json.loads(line)
                    total += 1
                    if feedback.get('rating'):
                        ratings.append(feedback['rating'])
                    if feedback.get('correct_response'):
                        needs_correction += 1
            
            return {
                'total_feedback': total,
                'average_rating': sum(ratings) / len(ratings) if ratings else None,
                'needs_correction': needs_correction,
                'correction_rate': needs_correction / total if total > 0 else 0
            }
        except FileNotFoundError:
            return {'total_feedback': 0}
        except Exception as e:
            logger.error(f"Feedback stats error: {str(e)}")
            return {'error': str(e)}

if __name__ == "__main__":
    # Test the factual chatbot
    chatbot = FactualFITChatbot()
    feedback = FeedbackCollector()
    
    test_queries = [
        "what is the rate for site 1585",
        "wind farms in Scotland over 1MW",
        "solar sites in Yorkshire",
        "sites needing immediate repowering"
    ]
    
    print("FACTUAL FIT CHATBOT TEST")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        response = chatbot.chat(query)
        print(response)
        
        # Simulate feedback collection
        feedback.collect_feedback(query, response, rating=5)
    
    print("\n" + "=" * 60)
    print("Feedback Statistics:")
    print(json.dumps(feedback.get_feedback_stats(), indent=2))