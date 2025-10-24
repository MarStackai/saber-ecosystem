#!/usr/bin/env python3
"""
Enhance queries with postcode hints for better vector search
Simple fix that doesn't require loading all data into memory
"""

from uk_postcodes import get_location_prefixes

def enhance_query_with_postcodes(query: str, location: str = None) -> str:
    """
    Add postcode hints to query text to guide vector search
    Example: "wind farms in manchester" -> "wind farms in manchester M postcode"
    """
    if not location:
        return query
    
    prefixes = get_location_prefixes(location)
    if not prefixes:
        return query
    
    # Add first few postcode prefixes as hints
    hint = " ".join([f"{p} postcode" for p in prefixes[:3]])
    enhanced = f"{query} {hint}"
    
    return enhanced