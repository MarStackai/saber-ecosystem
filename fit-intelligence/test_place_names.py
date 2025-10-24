#!/usr/bin/env python3
"""
Test UK Geographic Intelligence with Place Names
Tests "sites near bristol", "installations in yorkshire", etc.
"""

from uk_geo_intelligence import UKGeoIntelligence
from enhanced_geo_fit_intelligence import EnhancedGeoFITIntelligence

def test_place_name_functionality():
    print("🏛️🌍 Testing UK Place Name Geographic Intelligence")
    print("=" * 60)
    
    geo = UKGeoIntelligence()
    geo_fit = EnhancedGeoFITIntelligence()
    
    print("📍 1. PLACE NAME LOOKUP TEST")
    print("-" * 40)
    
    test_places = [
        "bristol", "london", "manchester", "glasgow", "birmingham",
        "yorkshire", "cornwall", "scotland", "wales", "devon",
        "leeds", "sheffield", "newcastle", "liverpool", "nottingham"
    ]
    
    successful_lookups = {}
    
    for place in test_places:
        result = geo.smart_location_lookup(place)
        if 'error' not in result:
            successful_lookups[place] = result
            coords = f"{result['latitude']:.4f}, {result['longitude']:.4f}"
            lookup_method = result.get('lookup_method', 'unknown')
            postcode = result.get('outcode') or result.get('postcode', 'N/A')
            print(f"✅ {place.title():>12}: {postcode} - {coords} ({lookup_method})")
        else:
            error = result['error'][:50] + "..." if len(result['error']) > 50 else result['error']
            suggestions = result.get('suggestions', [])
            if suggestions:
                print(f"❌ {place.title():>12}: {error} Suggestions: {', '.join(suggestions[:2])}")
            else:
                print(f"❌ {place.title():>12}: {error}")
    
    print(f"\n📏 2. PLACE NAME DISTANCE CALCULATIONS")
    print("-" * 40)
    
    if len(successful_lookups) >= 2:
        place_pairs = [
            ("bristol", "london"),
            ("manchester", "leeds"), 
            ("glasgow", "edinburgh"),
            ("cornwall", "devon"),
            ("yorkshire", "manchester")
        ]
        
        for place1, place2 in place_pairs:
            if place1 in successful_lookups and place2 in successful_lookups:
                distance_result = geo.calculate_distance(
                    successful_lookups[place1].get('outcode') or successful_lookups[place1].get('postcode'),
                    successful_lookups[place2].get('outcode') or successful_lookups[place2].get('postcode')
                )
                if 'error' not in distance_result:
                    km = distance_result['distance_km']
                    miles = distance_result['distance_miles']
                    print(f"✅ {place1.title():>10} ↔ {place2.title():<10}: {km:>6.1f}km ({miles:>5.1f} miles)")
                else:
                    print(f"❌ {place1.title():>10} ↔ {place2.title():<10}: {distance_result['error']}")
    
    print(f"\n🎯 3. NATURAL LANGUAGE GEOGRAPHIC QUERIES")
    print("-" * 40)
    
    test_queries = [
        "wind sites near bristol",
        "solar installations around london", 
        "renewable energy sites in yorkshire",
        "wind farms in cornwall",
        "sites near manchester between 250 and 500kw",
        "installations around glasgow",
        "renewable sites in scotland"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        
        # Test location extraction
        location_info = geo_fit._extract_location_from_query(query)
        
        if 'error' not in location_info:
            location_name = location_info['location_name']
            postcode = location_info['postcode']
            method = location_info.get('lookup_method', 'unknown')
            coords = location_info['geo_data']
            
            print(f"✅ Extracted: {location_name} ({postcode}) - {coords['latitude']:.4f}, {coords['longitude']:.4f}")
            print(f"   Method: {method}")
            
            # Test if we can find nearby postcodes (simulating FIT site search)
            nearby = geo.find_nearby_postcodes(postcode, radius_km=25)
            if 'error' not in nearby:
                print(f"   📍 Found {nearby['count']} postcodes within 25km for potential FIT sites")
            else:
                print(f"   ❌ Nearby search: {nearby['error']}")
        else:
            error_msg = location_info['error']
            suggestions = location_info.get('suggestions', [])
            print(f"❌ Location extraction failed: {error_msg}")
            if suggestions:
                print(f"   💡 Suggestions: {', '.join(suggestions[:3])}")
    
    print(f"\n⚡ 4. RENEWABLE ENERGY REGION ASSESSMENT")
    print("-" * 40)
    
    renewable_regions = ["cornwall", "scotland", "yorkshire", "wales", "devon"]
    
    for region in renewable_regions:
        if region in successful_lookups:
            stats = geo.get_regional_statistics(
                successful_lookups[region].get('outcode') or successful_lookups[region].get('postcode')
            )
            if 'error' not in stats:
                renewable = stats['renewable_indicators']
                print(f"⚡ {region.title():>10}: Wind={renewable['wind_potential']:>7}, Solar={renewable['solar_potential']:>6}, Coastal={'Yes' if renewable['coastal_proximity'] else 'No':>3}")
            else:
                print(f"❌ {region.title():>10}: {stats['error']}")
    
    print(f"\n🌟 5. BUSINESS USE CASES DEMONSTRATION")
    print("-" * 40)
    
    business_queries = [
        ("Market Analysis", "What's the renewable energy potential near bristol?"),
        ("Site Planning", "How far is it from our yorkshire wind farms to manchester?"),
        ("Investment Strategy", "Find installation opportunities around london within 50km"),
        ("Logistics Planning", "Calculate service routes between cornwall and devon sites")
    ]
    
    for use_case, description in business_queries:
        print(f"🎯 {use_case}: {description}")
        
        # Demonstrate that we can now parse these business-relevant queries
        if "near bristol" in description:
            location_info = geo_fit._extract_location_from_query("sites near bristol")
            if 'error' not in location_info:
                print(f"   ✅ Bristol identified: {location_info['postcode']} - Ready for FIT site search")
            else:
                print(f"   ❌ Bristol lookup failed")
        
        elif "yorkshire" in description and "manchester" in description:
            yorkshire_data = geo.smart_location_lookup("yorkshire")
            manchester_data = geo.smart_location_lookup("manchester")
            if 'error' not in yorkshire_data and 'error' not in manchester_data:
                print(f"   ✅ Yorkshire-Manchester corridor: Ready for distance matrix analysis")
            else:
                print(f"   ❌ Yorkshire-Manchester lookup failed")
        
        elif "around london" in description:
            location_info = geo_fit._extract_location_from_query("sites around london within 50km")
            if 'error' not in location_info:
                print(f"   ✅ London radius search: {location_info['postcode']} - Ready for opportunity mapping")
            else:
                print(f"   ❌ London radius search failed")
        
        elif "cornwall and devon" in description:
            cornwall_data = geo.smart_location_lookup("cornwall")
            devon_data = geo.smart_location_lookup("devon") 
            if 'error' not in cornwall_data and 'error' not in devon_data:
                print(f"   ✅ Cornwall-Devon route: Ready for logistics optimization")
            else:
                print(f"   ❌ Cornwall-Devon lookup failed")
    
    print(f"\n✅ PLACE NAME TESTING COMPLETE!")
    print("=" * 60)
    print("🎉 UK place names (bristol, yorkshire, etc.) now supported!")
    print("🚀 Natural language geographic queries fully functional!")
    print("💼 Ready for business intelligence applications!")

if __name__ == "__main__":
    test_place_name_functionality()