#!/usr/bin/env python3
"""
Robust capacity range parser for FIT Intelligence
Handles: between X and Y, X-Y, X to Y, over X, under Y, with unit conversion
"""
import re

# Unit conversion to kW
UNIT = {
    "gw": 1_000_000, 
    "mw": 1_000, 
    "kw": 1, 
    "w": 0.001
}

def normalize_value(value, unit):
    """Convert any capacity value to kW"""
    return float(value) * UNIT.get((unit or "kw").lower(), 1)

def parse_capacity_range(query):
    """
    Parse capacity from natural language query
    Returns: (min_kw, max_kw) tuple, either can be None
    """
    s = query.lower()
    
    # Pattern 1: "between X and Y"
    m = re.search(r"\bbetween\s+(\d+(?:\.\d+)?)\s*(gw|mw|kw|w)?\s+and\s+(\d+(?:\.\d+)?)\s*(gw|mw|kw|w)?\b", s)
    if m:
        val1, unit1, val2, unit2 = m.groups()
        x = normalize_value(val1, unit1)
        y = normalize_value(val2, unit2)
        return (min(x, y), max(x, y))
    
    # Pattern 2: "X to Y" or "X-Y" or "X–Y"
    m = re.search(r"\b(\d+(?:\.\d+)?)\s*(gw|mw|kw|w)?\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)\s*(gw|mw|kw|w)?\b", s)
    if m:
        val1, unit1, val2, unit2 = m.groups()
        x = normalize_value(val1, unit1)
        y = normalize_value(val2, unit2)
        return (min(x, y), max(x, y))
    
    # Pattern 3: Combined "over X and less than Y" or "over X and under Y"
    m1 = re.search(r"\b(?:over|above|>=|at\s*least|minimum|min)\s+(\d+(?:\.\d+)?)\s*(gw|mw|kw|w)?\b", s)
    m2 = re.search(r"\b(?:under|below|less\s*than|<=|at\s*most|maximum|max)\s+(\d+(?:\.\d+)?)\s*(gw|mw|kw|w)?\b", s)
    if m1 and m2:
        min_val, min_unit = m1.groups()
        max_val, max_unit = m2.groups()
        return (normalize_value(min_val, min_unit), normalize_value(max_val, max_unit))
    
    # Pattern 4: "over X" / "at least X" / "minimum X" / ">= X"
    if m1:
        val, unit = m1.groups()
        return (normalize_value(val, unit), None)
    
    # Pattern 5: "under X" / "at most X" / "maximum X" / "<= X" / "less than X"
    if m2:
        val, unit = m2.groups()
        return (None, normalize_value(val, unit))
    
    # Pattern 6: Just a number with unit (exact match)
    m = re.search(r"\b(\d+(?:\.\d+)?)\s*(gw|mw|kw|w)\b", s)
    if m:
        val, unit = m.groups()
        capacity = normalize_value(val, unit)
        return (capacity, capacity)
    
    return (None, None)

# Test cases
if __name__ == "__main__":
    test_queries = [
        "solar between 150kw and 500kw",
        "wind 100-250 MW",
        "hydro 2 to 5 MW",
        "over 500kw",
        "under 1MW",
        "at least 100kw",
        "maximum 2GW",
        "250kw solar farm",
        "between 0.5MW and 1.5MW"
    ]
    
    for q in test_queries:
        min_cap, max_cap = parse_capacity_range(q)
        print(f"{q:40} -> min: {min_cap}, max: {max_cap}")