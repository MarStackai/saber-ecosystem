#!/usr/bin/env python3
"""
Simple FIT Query System
Focus on accurate data retrieval, not sales complexity
"""

import json
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleFITQuery:
    """
    Simple, accurate FIT data query system
    No sales complexity - just clean data access
    """
    
    def __init__(self):
        self.data_fields = [
            "fit_id",
            "technology", 
            "capacity_kw",
            "location",
            "postcode",
            "commissioned_date",
            "fit_rate",
            "remaining_years"
        ]
        logger.info("Simple FIT Query System initialized")
    
    def query(self, request: str) -> Dict:
        """
        Simple query processing
        Returns: Raw data, no sales interpretation
        """
        # Parse the basic request
        filters = self._extract_filters(request)
        
        # Return data structure
        return {
            "query": request,
            "filters_applied": filters,
            "results": self._get_mock_results(filters),
            "count": len(self._get_mock_results(filters))
        }
    
    def _extract_filters(self, request: str) -> Dict:
        """Extract basic filters from request"""
        filters = {}
        request_lower = request.lower()
        
        # Technology
        if "wind" in request_lower:
            filters["technology"] = "Wind"
        elif "solar" in request_lower:
            filters["technology"] = "Photovoltaic"
        elif "hydro" in request_lower:
            filters["technology"] = "Hydro"
        
        # Capacity
        import re
        capacity_match = re.search(r'(\d+)\s*kw', request_lower)
        if capacity_match:
            filters["capacity_kw"] = int(capacity_match.group(1))
        
        # Location
        locations = ["yorkshire", "berkshire", "cornwall", "devon", "scotland"]
        for loc in locations:
            if loc in request_lower:
                filters["location"] = loc.capitalize()
                break
        
        return filters
    
    def _get_mock_results(self, filters: Dict) -> List[Dict]:
        """Return mock FIT data based on filters"""
        # Simple mock data - in production this queries the database
        mock_data = [
            {
                "fit_id": "FIT_12345",
                "technology": filters.get("technology", "Wind"),
                "capacity_kw": filters.get("capacity_kw", 100),
                "location": filters.get("location", "Yorkshire"),
                "postcode": "YO1 1AA",
                "commissioned_date": "2015-03-15",
                "fit_rate": 13.73,
                "remaining_years": 6
            }
        ]
        
        return mock_data


def main():
    """
    Simple demonstration of basic FIT querying
    No sales complexity, just data
    """
    system = SimpleFITQuery()
    
    test_queries = [
        "wind sites 100kw in yorkshire",
        "solar installations in berkshire",
        "hydro projects in scotland"
    ]
    
    print("\n" + "="*60)
    print("SIMPLE FIT QUERY SYSTEM")
    print("Focus: Accurate Data Retrieval")
    print("="*60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = system.query(query)
        print(f"Filters: {result['filters_applied']}")
        print(f"Results: {result['count']} found")
        for item in result['results']:
            print(f"  - {item['fit_id']}: {item['capacity_kw']}kW {item['technology']} in {item['location']}")
    
    print("\n" + "="*60)
    print("This is the correct approach:")
    print("1. Focus on accurate FIT data retrieval")
    print("2. Simple, maintainable code")
    print("3. No unnecessary AI complexity")
    print("4. Clear, predictable behavior")
    print("="*60)


if __name__ == "__main__":
    main()