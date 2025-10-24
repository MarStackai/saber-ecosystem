#!/usr/bin/env python3
"""
Validation script with hard gates for LoRA model
Must pass ALL tests before deployment
"""

import json
import sys
import ollama
from typing import Dict, List, Tuple

# Import postcode mappings
sys.path.append('..')
from uk_postcodes import UK_POSTCODE_PREFIXES, REGIONS

# Critical test cases that MUST pass
CRITICAL_TESTS = [
    # Geographic accuracy tests
    {
        "query": "sites in Manchester",
        "expected": {
            "postcode_areas": ["M"],
            "must_not_contain": ["ML", "MA", "MK"]
        },
        "test_name": "Manchester M-only test"
    },
    {
        "query": "wind farms in Yorkshire",
        "expected": {
            "postcode_areas": ["YO", "HU", "LS", "BD", "HX", "HD", "WF", "S", "DN"],
            "must_not_contain": ["Y", "YK"]
        },
        "test_name": "Yorkshire full set test"
    },
    {
        "query": "solar sites in Aberdeen",
        "expected": {
            "postcode_areas": ["AB"],
            "must_not_contain": ["A", "ABC", "ABD"]
        },
        "test_name": "Aberdeen AB-only test"
    },
    {
        "query": "installations in Cornwall",
        "expected": {
            "postcode_areas": ["TR", "PL"],
            "must_not_contain": ["CO", "CN"]
        },
        "test_name": "Cornwall TR/PL test"
    },
    {
        "query": "sites in Surrey",
        "expected": {
            "postcode_areas": ["GU", "KT", "RH", "SM", "CR", "TW"],
            "must_not_contain": ["SU", "SR", "SY"]
        },
        "test_name": "Surrey counties test"
    },
    
    # Capacity range tests
    {
        "query": "wind sites over 50kw to max 350kw",
        "expected": {
            "min_capacity_kw": 50,
            "max_capacity_kw": 350,
            "must_not_have": {
                "min_capacity_kw": [500, 5000, 5],
                "max_capacity_kw": [500, 3500, 35]
            }
        },
        "test_name": "Exact range 50-350kW"
    },
    {
        "query": "solar installations between 100 and 500 kilowatts",
        "expected": {
            "min_capacity_kw": 100,
            "max_capacity_kw": 500,
            "technology": "photovoltaic"
        },
        "test_name": "Range with units variation"
    },
    {
        "query": "sites larger than 1MW",
        "expected": {
            "min_capacity_kw": 1000,
            "max_capacity_kw": None
        },
        "test_name": "MW conversion test"
    },
    
    # Technology normalization tests
    {
        "query": "solar panels over 100kw",
        "expected": {
            "technology": "photovoltaic",
            "must_not_be": ["solar", "solar panels", "pv panels"]
        },
        "test_name": "Solar to photovoltaic"
    },
    {
        "query": "PV installations",
        "expected": {
            "technology": "photovoltaic"
        },
        "test_name": "PV normalization"
    },
    {
        "query": "wind turbines in Scotland",
        "expected": {
            "technology": "wind",
            "must_not_be": ["turbines", "wind turbines"]
        },
        "test_name": "Wind normalization"
    },
    
    # Repowering window tests
    {
        "query": "urgent repowering opportunities",
        "expected": {
            "repowering_category": "urgent",
            "must_not_be": ["immediate", "optimal"]
        },
        "test_name": "Urgent category"
    },
    {
        "query": "optimal solar sites needing repowering",
        "expected": {
            "repowering_category": "optimal",
            "technology": "photovoltaic"
        },
        "test_name": "Optimal with technology"
    },
    
    # Complex combined tests
    {
        "query": "urgent wind sites in Scotland 500kw to 2MW",
        "expected": {
            "technology": "wind",
            "min_capacity_kw": 500,
            "max_capacity_kw": 2000,
            "repowering_category": "urgent"
        },
        "test_name": "Complex multi-constraint"
    },
    {
        "query": "optimal solar sites in Surrey over 250kw",
        "expected": {
            "technology": "photovoltaic",
            "min_capacity_kw": 250,
            "postcode_areas_should_include": ["GU", "KT"],
            "repowering_category": "optimal"
        },
        "test_name": "Surrey solar optimal"
    }
]

def extract_parameters(response: str) -> Dict:
    """Extract parameters from model response"""
    try:
        # Look for JSON block in response
        if "Search parameters:" in response:
            json_str = response.split("Search parameters:")[1].strip()
            # Find JSON object
            if "{" in json_str:
                start = json_str.index("{")
                end = json_str.rindex("}") + 1
                json_str = json_str[start:end]
                return json.loads(json_str)
        
        # Try to find inline parameters
        params = {}
        
        # Extract technology
        if "photovoltaic" in response.lower():
            params["technology"] = "photovoltaic"
        elif "wind" in response.lower():
            params["technology"] = "wind"
        elif "hydro" in response.lower():
            params["technology"] = "hydro"
            
        # Extract capacity
        import re
        cap_match = re.search(r'(\d+)\s*(?:to|and|-)\s*(\d+)\s*kw', response.lower())
        if cap_match:
            params["min_capacity_kw"] = int(cap_match.group(1))
            params["max_capacity_kw"] = int(cap_match.group(2))
        else:
            over_match = re.search(r'over\s*(\d+)\s*kw', response.lower())
            if over_match:
                params["min_capacity_kw"] = int(over_match.group(1))
                
        # Extract postcodes
        postcode_match = re.search(r'postcode areas?:\s*\[(.*?)\]', response)
        if postcode_match:
            areas = [a.strip().strip('"\'') for a in postcode_match.group(1).split(',')]
            params["postcode_areas"] = areas
            
        # Extract repowering
        if "urgent" in response.lower():
            params["repowering_category"] = "urgent"
        elif "optimal" in response.lower():
            params["repowering_category"] = "optimal"
        elif "immediate" in response.lower():
            params["repowering_category"] = "immediate"
            
        return params
    except Exception as e:
        print(f"Error extracting parameters: {e}")
        return {}

def run_test(model_name: str, test: Dict) -> Tuple[bool, str]:
    """Run a single test case"""
    try:
        # Query the model
        response = ollama.generate(
            model=model_name,
            prompt=test["query"],
            system="""You are a UK renewable energy FIT installation search assistant. Parse queries to extract:
- technology: normalized to photovoltaic/wind/hydro/anaerobic digestion
- postcode_areas: exact UK postcode area codes (e.g., M for Manchester, not ML)
- min_capacity_kw: minimum capacity in kilowatts
- max_capacity_kw: maximum capacity in kilowatts
- repowering_category: immediate/urgent/optimal

Always return parameters in JSON format after your response.""",
            options={"temperature": 0.1}
        )
        
        # Extract parameters
        params = extract_parameters(response['response'])
        
        # Validate against expected
        errors = []
        expected = test["expected"]
        
        # Check postcode areas
        if "postcode_areas" in expected:
            if params.get("postcode_areas") != expected["postcode_areas"]:
                errors.append(f"Postcode mismatch: got {params.get('postcode_areas')}, expected {expected['postcode_areas']}")
        
        if "must_not_contain" in expected:
            for bad_code in expected["must_not_contain"]:
                if bad_code in params.get("postcode_areas", []):
                    errors.append(f"Contains forbidden postcode: {bad_code}")
        
        # Check capacity
        if "min_capacity_kw" in expected:
            if params.get("min_capacity_kw") != expected["min_capacity_kw"]:
                errors.append(f"Min capacity wrong: got {params.get('min_capacity_kw')}, expected {expected['min_capacity_kw']}")
        
        if "max_capacity_kw" in expected:
            if params.get("max_capacity_kw") != expected["max_capacity_kw"]:
                errors.append(f"Max capacity wrong: got {params.get('max_capacity_kw')}, expected {expected['max_capacity_kw']}")
        
        # Check technology
        if "technology" in expected:
            if params.get("technology") != expected["technology"]:
                errors.append(f"Technology wrong: got {params.get('technology')}, expected {expected['technology']}")
        
        if "must_not_be" in expected:
            if params.get("technology") in expected["must_not_be"]:
                errors.append(f"Technology not normalized: {params.get('technology')}")
        
        # Check repowering
        if "repowering_category" in expected:
            if params.get("repowering_category") != expected["repowering_category"]:
                errors.append(f"Repowering wrong: got {params.get('repowering_category')}, expected {expected['repowering_category']}")
        
        if errors:
            return False, f"FAILED - {', '.join(errors)}"
        else:
            return True, "PASSED"
            
    except Exception as e:
        return False, f"ERROR - {str(e)}"

def main():
    """Run all validation tests"""
    import sys
    
    model_name = sys.argv[1] if len(sys.argv) > 1 else "llama2:13b"
    
    print(f"Running LoRA validation tests on model: {model_name}")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test in CRITICAL_TESTS:
        print(f"\nTest: {test['test_name']}")
        print(f"Query: {test['query']}")
        
        success, message = run_test(model_name, test)
        
        if success:
            print(f"✅ {message}")
            passed += 1
        else:
            print(f"❌ {message}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(CRITICAL_TESTS)} tests")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED - Model ready for deployment!")
        return 0
    else:
        print(f"⚠️  {failed} TESTS FAILED - Do not deploy!")
        return 1

if __name__ == "__main__":
    sys.exit(main())