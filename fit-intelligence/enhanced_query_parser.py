#!/usr/bin/env python3
"""
Enhanced query parser with few-shot learning
Immediate solution while LoRA training is set up
"""

import json
import re
from typing import Dict, Optional, List

# Import mappings
from uk_postcodes import UK_POSTCODE_PREFIXES, REGIONS, ALL_UK_PREFIXES

# Yorkshire specific set
YORKSHIRE_AREAS = ['YO', 'HU', 'LS', 'BD', 'HX', 'HD', 'WF', 'S', 'DN']

class EnhancedQueryParser:
    """Parse queries with improved accuracy using few-shot examples"""
    
    def __init__(self):
        self.few_shot_examples = self._load_examples()
        
    def _load_examples(self) -> str:
        """Load few-shot examples for context"""
        return """
CRITICAL PARSING RULES:
1. Manchester MUST return ["M"] only, never ML or other M-prefixes
2. Yorkshire MUST return ["YO","HU","LS","BD","HX","HD","WF","S","DN"] exactly
3. Solar/PV/solar panels MUST normalize to "photovoltaic"
4. Capacity ranges must be exact: "50kw to 350kw" means min=50, max=350

EXAMPLES:

Query: "sites in Manchester"
Output: {"postcode_areas": ["M"]}

Query: "wind farms in Yorkshire"
Output: {"technology": "wind", "postcode_areas": ["YO","HU","LS","BD","HX","HD","WF","S","DN"]}

Query: "wind sites over 50kw to max 350kw"
Output: {"technology": "wind", "min_capacity_kw": 50, "max_capacity_kw": 350}

Query: "solar panels over 250kw in Surrey"
Output: {"technology": "photovoltaic", "min_capacity_kw": 250, "postcode_areas": ["GU","KT","RH","SM","CR","TW"]}

Query: "urgent repowering opportunities"
Output: {"repowering_category": "urgent"}

Query: "sites between 100 and 500 kilowatts"
Output: {"min_capacity_kw": 100, "max_capacity_kw": 500}

Query: "PV installations in Cornwall"
Output: {"technology": "photovoltaic", "postcode_areas": ["TR","PL"]}
"""
    
    def parse_technology(self, query: str) -> Optional[str]:
        """Extract and normalize technology"""
        query_lower = query.lower()
        
        # For comparative queries, don't extract single technology
        if any(word in query_lower for word in ['compar', ' vs ', ' versus ', ' and ']):
            return None  # Let market analyst handle multi-tech queries
        
        # Solar variations
        if any(term in query_lower for term in ['solar', 'pv', 'photovoltaic']):
            return 'photovoltaic'
        
        # Wind variations
        if any(term in query_lower for term in ['wind', 'turbine']):
            return 'wind'
            
        # Hydro variations
        if any(term in query_lower for term in ['hydro', 'water power']):
            return 'hydro'
            
        # Anaerobic digestion
        if any(term in query_lower for term in ['biogas', 'anaerobic', 'ad plant']):
            return 'anaerobic digestion'
            
        return None
    
    def parse_location(self, query: str) -> List[str]:
        """Extract location and return exact postcode areas"""
        query_lower = query.lower()
        
        # Critical exact matches first
        if 'manchester' in query_lower:
            return ['M']  # NEVER ML
            
        if 'yorkshire' in query_lower:
            return YORKSHIRE_AREAS  # Full set
            
        if 'aberdeen' in query_lower:
            return ['AB']  # Exact match
            
        if 'cornwall' in query_lower:
            return ['TR', 'PL']
            
        if 'surrey' in query_lower:
            return ['GU', 'KT', 'RH', 'SM', 'CR', 'TW']
            
        if 'kent' in query_lower:
            return ['BR', 'CT', 'DA', 'ME', 'TN']
            
        if 'essex' in query_lower:
            return ['CM', 'CO', 'IG', 'RM', 'SS']
            
        if 'dorset' in query_lower:
            return ['DT', 'BH']
        
        # Check other locations
        for location, prefixes in UK_POSTCODE_PREFIXES.items():
            if location.replace('_', ' ') in query_lower:
                return prefixes
        
        # Check regions
        for region, areas in REGIONS.items():
            if region.replace('_', ' ') in query_lower:
                return areas[:20] if len(areas) > 20 else areas
        
        return []
    
    def parse_years_left(self, query: str) -> Dict[str, Optional[float]]:
        """Extract years_left range from query"""
        query_lower = query.lower()
        result = {"min_years_left": None, "max_years_left": None}
        
        # Check if this is about years/FIT left
        if 'year' in query_lower and ('left' in query_lower or 'fit' in query_lower or 'remaining' in query_lower):
            # Pattern: "X to Y years"
            match = re.search(r'(\d+)\s*(?:to|-|and)\s*(\d+)\s*year', query_lower)
            if match:
                result["min_years_left"] = float(match.group(1))
                result["max_years_left"] = float(match.group(2))
                return result
        
        return result
    
    def parse_capacity(self, query: str) -> Dict[str, Optional[int]]:
        """Extract capacity range with exact parsing"""
        query_lower = query.lower()
        result = {"min_capacity_kw": None, "max_capacity_kw": None}
        
        # Convert MW to kW
        query_normalized = query_lower.replace('mw', '000kw').replace('megawatt', '000kw')
        
        # Remove the years part to avoid confusion
        # This removes patterns like "between 8 to 10 years"
        query_clean = re.sub(r'between\s+\d+\s+(?:to|and|-)\s+\d+\s+years?', '', query_normalized)
        
        # Range patterns - EXACT matching
        # Pattern: "X to max Y" or "over X to max Y"
        range_match = re.search(r'(?:over\s+)?(\d+)\s*kw?\s+to\s+max\s+(\d+)\s*kw?', query_clean)
        if range_match:
            result["min_capacity_kw"] = int(range_match.group(1))
            result["max_capacity_kw"] = int(range_match.group(2))
            return result
        
        # Pattern: "between X and Y" or "X-Y" or "X to Y" - only with kw/kilowatt
        range_match = re.search(r'between\s+(\d+)\s*(?:kw)?\s*(?:to|-|and)\s*(\d+)\s*(?:kw|kilowatt)', query_clean)
        if range_match:
            result["min_capacity_kw"] = int(range_match.group(1))
            result["max_capacity_kw"] = int(range_match.group(2))
            return result
        
        # Single bound patterns
        # Over/above/minimum - make kw optional but include in pattern
        over_match = re.search(r'(?:over|above|greater than|minimum|at least|>)\s*(\d+)\s*(?:kw|kilowatt)?', query_clean)
        if over_match:
            result["min_capacity_kw"] = int(over_match.group(1))
            
        # Under/below/maximum
        under_match = re.search(r'(?:under|below|less than|maximum|up to|<)\s*(\d+)\s*(?:kw)?', query_clean)
        if under_match:
            result["max_capacity_kw"] = int(under_match.group(1))
        
        return result
    
    def parse_repowering(self, query: str) -> Optional[str]:
        """Extract repowering window category"""
        query_lower = query.lower()
        
        if 'immediate' in query_lower:
            return 'immediate'
        elif 'urgent' in query_lower:
            return 'urgent'
        elif any(term in query_lower for term in ['optimal', 'optimum']):
            return 'optimal'
        elif 'expired' in query_lower:
            return 'expired'
            
        return None

    def parse_limit(self, query: str) -> Optional[int]:
        """Extract result limit from query like 'give me 25 wind sites'"""
        # Look for patterns like "25 wind sites", "35 sites", "first 20", etc.
        patterns = [
            r'(?:give me|show me|find|get)\s+(\d+)\s+(?:wind\s+)?sites',
            r'(\d+)\s+(?:wind\s+)?sites',
            r'first\s+(\d+)',
            r'top\s+(\d+)',
            r'(\d+)\s+results'
        ]

        query_lower = query.lower()
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                limit = int(match.group(1))
                # Cap at reasonable maximum
                return min(limit, 100)

        return None

    def parse(self, query: str) -> Dict:
        """Parse query into structured parameters"""
        params = {}
        
        # Extract technology
        tech = self.parse_technology(query)
        if tech:
            params['technology'] = tech
        
        # Extract location
        areas = self.parse_location(query)
        if areas:
            params['postcode_areas'] = areas
        
        # Extract capacity
        capacity = self.parse_capacity(query)
        if capacity['min_capacity_kw'] is not None:
            params['min_capacity_kw'] = capacity['min_capacity_kw']
        if capacity['max_capacity_kw'] is not None:
            params['max_capacity_kw'] = capacity['max_capacity_kw']
        
        # Extract years_left range
        years = self.parse_years_left(query)
        if years['min_years_left'] is not None:
            params['min_years_left'] = years['min_years_left']
        if years['max_years_left'] is not None:
            params['max_years_left'] = years['max_years_left']
        
        # Extract repowering
        repowering = self.parse_repowering(query)
        if repowering:
            params['repowering_category'] = repowering

        # Extract result limit
        limit = self.parse_limit(query)
        if limit:
            params['limit'] = limit

        return params
    
    def format_response(self, query: str, params: Dict) -> str:
        """Format response in expected style"""
        response = "I'll search for "
        
        # Technology
        if params.get('technology'):
            response += f"{params['technology']} "
        else:
            response += "renewable energy "
        
        response += "installations"
        
        # Capacity
        if params.get('min_capacity_kw') and params.get('max_capacity_kw'):
            response += f" between {params['min_capacity_kw']}kW and {params['max_capacity_kw']}kW"
        elif params.get('min_capacity_kw'):
            response += f" over {params['min_capacity_kw']}kW"
        elif params.get('max_capacity_kw'):
            response += f" under {params['max_capacity_kw']}kW"
        
        # Location
        if params.get('postcode_areas'):
            areas_str = ', '.join(params['postcode_areas'][:5])
            if len(params['postcode_areas']) > 5:
                areas_str += '...'
            response += f" in postcode areas: {areas_str}"
        
        # Repowering
        if params.get('repowering_category'):
            response += f" ({params['repowering_category']} repowering window)"
        
        response += f"\n\nSearch parameters:\n{json.dumps(params, indent=2)}"
        
        return response

# Test the parser
if __name__ == "__main__":
    parser = EnhancedQueryParser()
    
    # Critical test cases
    test_queries = [
        "sites in Manchester",
        "wind sites over 50kw to max 350kw in Yorkshire",
        "solar panels over 250kw in Surrey",
        "urgent repowering opportunities",
        "PV installations between 100 and 500 kilowatts",
        "optimal solar sites in Cornwall"
    ]
    
    print("Testing Enhanced Query Parser")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        params = parser.parse(query)
        print(f"Parsed: {json.dumps(params, indent=2)}")
        
        # Validate critical assertions
        if "Manchester" in query and params.get('postcode_areas') != ['M']:
            print("❌ FAILED: Manchester assertion")
        elif "Yorkshire" in query and params.get('postcode_areas') != YORKSHIRE_AREAS:
            print("❌ FAILED: Yorkshire assertion")
        elif "50kw to max 350kw" in query.lower() and (
            params.get('min_capacity_kw') != 50 or params.get('max_capacity_kw') != 350
        ):
            print("❌ FAILED: Capacity range assertion")
        elif "solar" in query.lower() and params.get('technology') != 'photovoltaic':
            print("❌ FAILED: Solar normalization")
        else:
            print("✅ PASSED")