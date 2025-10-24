#!/usr/bin/env python3
"""
Postcode enforcement for FIT Intelligence
Ensures geographic queries return only valid postcodes
"""

# Postcode prefixes by region
YORKSHIRE_PREFIXES = {"YO", "HU", "LS", "BD", "HX", "HD", "WF", "S", "DN"}
ABERDEEN_PREFIXES = {"AB"}
EDINBURGH_PREFIXES = {"EH"}
GLASGOW_PREFIXES = {"G"}
SCOTLAND_PREFIXES = {"AB", "DD", "DG", "EH", "FK", "G", "IV", "KA", "KW", "KY", 
                     "ML", "PA", "PH", "TD", "ZE"}

# Location to postcode mapping
LOCATION_POSTCODES = {
    "aberdeen": ABERDEEN_PREFIXES,
    "edinburgh": EDINBURGH_PREFIXES,
    "glasgow": GLASGOW_PREFIXES,
    "yorkshire": YORKSHIRE_PREFIXES,
    "scotland": SCOTLAND_PREFIXES,
    "dumfries": {"DG"},  # Dumfries & Galloway
    "wales": {"CF", "NP", "LL", "SA", "LD", "SY"},
}

def enforce_postcode_prefix(rows, location):
    """
    Filter rows to only include valid postcodes for the location
    
    Args:
        rows: List of result dictionaries with 'metadata' containing 'postcode' field
        location: String location name (e.g., "aberdeen", "yorkshire")
    
    Returns:
        Filtered list of rows with valid postcodes only
    """
    if not location:
        return rows
    
    location_lower = location.lower().strip()
    
    # Get valid prefixes for this location
    allowed_prefixes = LOCATION_POSTCODES.get(location_lower)
    
    if not allowed_prefixes:
        # Try partial matches
        for loc_name, prefixes in LOCATION_POSTCODES.items():
            if loc_name in location_lower or location_lower in loc_name:
                allowed_prefixes = prefixes
                break
    
    if not allowed_prefixes:
        # No location filter needed
        return rows
    
    # Convert to tuple for startswith
    prefix_tuple = tuple(allowed_prefixes)
    
    # Filter rows - handle both direct dict and nested metadata
    filtered = []
    for row in rows:
        # Handle nested metadata structure
        if 'metadata' in row:
            postcode = str(row['metadata'].get("postcode", "")).upper().strip()
        else:
            postcode = str(row.get("postcode", "")).upper().strip()
            
        if postcode and postcode.startswith(prefix_tuple):
            filtered.append(row)
    
    return filtered

def get_location_from_query(query):
    """
    Extract location from query string
    """
    query_lower = query.lower()
    
    # Check for exact matches first
    for location in LOCATION_POSTCODES.keys():
        if location in query_lower:
            return location
    
    # Check for common variations
    if "aberdeen" in query_lower:
        return "aberdeen"
    elif "yorkshire" in query_lower or "yorks" in query_lower:
        return "yorkshire"
    elif "edinburgh" in query_lower:
        return "edinburgh"
    elif "glasgow" in query_lower:
        return "glasgow"
    elif "scotland" in query_lower or "scottish" in query_lower:
        return "scotland"
    
    return None

# Test cases
if __name__ == "__main__":
    test_data = [
        {"fit_id": "123", "postcode": "AB10"},
        {"fit_id": "124", "postcode": "EH1"},
        {"fit_id": "125", "postcode": "YO1"},
        {"fit_id": "126", "postcode": "LS1"},
        {"fit_id": "127", "postcode": "ML1"},
        {"fit_id": "128", "postcode": "SW1"},
    ]
    
    print("Aberdeen filter:")
    aberdeen_results = enforce_postcode_prefix(test_data, "aberdeen")
    for r in aberdeen_results:
        print(f"  {r['fit_id']}: {r['postcode']}")
    
    print("\nYorkshire filter:")
    yorkshire_results = enforce_postcode_prefix(test_data, "yorkshire")
    for r in yorkshire_results:
        print(f"  {r['fit_id']}: {r['postcode']}")
    
    print("\nScotland filter:")
    scotland_results = enforce_postcode_prefix(test_data, "scotland")
    for r in scotland_results:
        print(f"  {r['fit_id']}: {r['postcode']}")