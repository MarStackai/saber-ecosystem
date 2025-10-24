#!/usr/bin/env python3
"""
Detect location changes in follow-up queries
"""

import re
from uk_postcodes import get_location_prefixes

def detect_location_change(query):
    """
    Detect if query is changing location while preserving other params
    Returns: {"region": str, "postcode_prefixes": list} or {}
    """
    s = query.lower()
    
    # Check for location change patterns
    location_patterns = [
        "and in", "what about in", "how about", "now show me",
        "and for", "and around", "what about", "now in"
    ]
    
    if any(p in s for p in location_patterns):
        # Extract the new location
        m = re.search(r'\b(?:in|around|near|for)\s+([a-z][a-z\s\-]{2,40})\??', s)
        if m:
            loc = m.group(1).strip()
            px = get_location_prefixes(loc)
            return {"region": loc, "postcode_prefixes": px}
    
    return {}

def prefixes_for(text):
    """Get postcode prefixes for a location"""
    if not text:
        return None
    return get_location_prefixes(text)