#!/usr/bin/env python3
"""
Technology field sanitizer for FIT Intelligence
Ensures clean, single technology values
"""

# Valid technology types
ALLOWED_TECH = {
    "solar", 
    "wind", 
    "hydro", 
    "anaerobic digestion", 
    "ad",  # Alias for anaerobic digestion
    "biomass",
    "chp",  # Combined Heat and Power
    "micro chp"
}

# Technology aliases/synonyms
TECH_ALIASES = {
    "pv": "solar",
    "photovoltaic": "solar",
    "solar pv": "solar",
    "ad": "anaerobic digestion",
    "anaerobic": "anaerobic digestion",
    "water": "hydro",
    "hydroelectric": "hydro",
    "wind turbine": "wind",
    "wind farm": "wind",
    "combined heat power": "chp"
}

def sanitize_technology(value):
    """
    Clean and validate technology field
    
    Args:
        value: Raw technology value (could be string, list, or contain pipes)
    
    Returns:
        Single valid technology string or None
    """
    if not value:
        return None
    
    # Handle pipe-separated values (e.g., "wind|solar|null")
    if isinstance(value, str) and "|" in value:
        parts = [p.strip().lower() for p in value.split("|")]
        parts = [p for p in parts if p and p != "null"]
        
        # Return first valid technology found
        for part in parts:
            # Check direct match
            if part in ALLOWED_TECH:
                return part
            # Check aliases
            if part in TECH_ALIASES:
                return TECH_ALIASES[part]
        
        return None
    
    # Handle single string value
    if isinstance(value, str):
        tech_lower = value.lower().strip()
        
        # Remove "null" strings
        if tech_lower == "null":
            return None
        
        # Check direct match
        if tech_lower in ALLOWED_TECH:
            return tech_lower
        
        # Check aliases
        if tech_lower in TECH_ALIASES:
            return TECH_ALIASES[tech_lower]
        
        # Check if contains valid tech
        for tech in ALLOWED_TECH:
            if tech in tech_lower:
                return tech
    
    return None

def extract_technology_from_query(query):
    """
    Extract technology type from natural language query
    """
    query_lower = query.lower()
    
    # Check for direct mentions
    for tech in ALLOWED_TECH:
        if tech in query_lower:
            return tech
    
    # Check aliases
    for alias, tech in TECH_ALIASES.items():
        if alias in query_lower:
            return tech
    
    return None

# Test cases
if __name__ == "__main__":
    test_values = [
        "solar",
        "Solar",
        "wind|solar|null",
        "null",
        "PV",
        "solar pv",
        "wind farm",
        "anaerobic digestion",
        "AD",
        "invalid",
        None,
        "wind|null|hydro"
    ]
    
    print("Testing technology sanitizer:")
    for val in test_values:
        result = sanitize_technology(val)
        print(f"  {str(val):25} -> {result}")