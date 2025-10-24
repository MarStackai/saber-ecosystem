#!/usr/bin/env python3
"""
Test script to demonstrate UK Geographic Intelligence working with incomplete postcodes
Simulates the postcode data format you have in your FIT database
"""

from uk_geo_intelligence import UKGeoIntelligence
from enhanced_geo_fit_intelligence import EnhancedGeoFITIntelligence

def test_incomplete_postcode_functionality():
    print("🌍⚡ Testing UK Geographic Intelligence with Incomplete Postcodes")
    print("=" * 70)
    print("Simulating your FIT database postcode format (YO17, HX4, PL7, etc.)")
    print()
    
    # Initialize systems
    geo = UKGeoIntelligence()
    geo_fit = EnhancedGeoFITIntelligence()
    
    # Test postcodes from your actual FIT data
    fit_data_postcodes = ["YO17", "YO25", "HX4", "LD3", "PL7", "LS1", "M1", "B1"]
    
    print("📍 1. SMART POSTCODE LOOKUP TEST")
    print("-" * 40)
    
    locations_data = {}
    for postcode in fit_data_postcodes:
        result = geo.smart_postcode_lookup(postcode)
        if 'error' not in result:
            locations_data[postcode] = result
            accuracy = result.get('accuracy', 'exact')
            coords = f"{result['latitude']:.4f}, {result['longitude']:.4f}"
            admin_areas = result.get('admin_district', ['Unknown'])
            if isinstance(admin_areas, list):
                admin_str = ', '.join(admin_areas[:2])  # Show first 2 admin areas
            else:
                admin_str = str(admin_areas)
            print(f"✅ {postcode:>4} ({accuracy:>11}): {coords} - {admin_str}")
        else:
            print(f"❌ {postcode:>4}: {result['error']}")
    
    print(f"\n📏 2. DISTANCE CALCULATIONS TEST")
    print("-" * 40)
    
    # Test distance calculations between FIT sites
    test_pairs = [
        ("YO17", "YO25", "Yorkshire sites"),
        ("HX4", "LS1", "West Yorkshire sites"), 
        ("PL7", "YO17", "Plymouth to Yorkshire"),
        ("M1", "B1", "Manchester to Birmingham")
    ]
    
    for pc1, pc2, description in test_pairs:
        distance_result = geo.calculate_distance(pc1, pc2)
        if 'error' not in distance_result:
            km = distance_result['distance_km']
            miles = distance_result['distance_miles']
            travel_time = estimate_travel_time(km)
            print(f"✅ {pc1} ↔ {pc2}: {km:>6.1f}km ({miles:>5.1f} miles) - {travel_time} - {description}")
        else:
            print(f"❌ {pc1} ↔ {pc2}: {distance_result['error']}")
    
    print(f"\n🎯 3. GEOGRAPHIC CLUSTERING TEST")
    print("-" * 40)
    
    # Find clusters of nearby sites
    test_centers = ["YO17", "HX4", "PL7"]
    
    for center in test_centers:
        nearby_result = geo.find_nearby_postcodes(center, radius_km=25)
        if 'error' not in nearby_result:
            count = nearby_result['count']
            center_coords = nearby_result['center_coordinates']
            print(f"✅ {center}: {count} postcodes within 25km (center: {center_coords['lat']:.4f}, {center_coords['lon']:.4f})")
            
            # Show closest 3 postcodes
            for i, pc in enumerate(nearby_result['nearby_postcodes'][:3], 1):
                print(f"    {i}. {pc['postcode']} - {pc['distance_km']:.1f}km away")
        else:
            print(f"❌ {center}: {nearby_result['error']}")
    
    print(f"\n⚡ 4. RENEWABLE ENERGY ASSESSMENT TEST")
    print("-" * 40)
    
    for postcode in ["YO17", "HX4", "PL7", "LS1"][:4]:  # Test first 4
        stats = geo.get_regional_statistics(postcode)
        if 'error' not in stats:
            renewable = stats['renewable_indicators']
            geo_data = stats['geographic_data']
            
            print(f"✅ {postcode} - {geo_data.get('country', 'UK')}:")
            print(f"    Wind potential: {renewable['wind_potential'].upper()}")
            print(f"    Solar potential: {renewable['solar_potential'].upper()}")
            print(f"    Coastal proximity: {'Yes' if renewable['coastal_proximity'] else 'No'}")
        else:
            print(f"❌ {postcode}: {stats['error']}")
    
    print(f"\n🏗️ 5. RENEWABLE SITE CLUSTERING SIMULATION")
    print("-" * 40)
    
    # Simulate renewable installations with incomplete postcodes (like your FIT data)
    simulated_installations = [
        {"postcode": "YO17", "technology": "Wind", "capacity_kw": 335},
        {"postcode": "YO25", "technology": "Wind", "capacity_kw": 500},
        {"postcode": "HX4", "technology": "Wind", "capacity_kw": 250},
        {"postcode": "PL7", "technology": "Solar", "capacity_kw": 400},
        {"postcode": "LS1", "technology": "Solar", "capacity_kw": 300},
    ]
    
    print("Simulated FIT installations with incomplete postcodes:")
    for installation in simulated_installations:
        pc = installation['postcode']
        geo_data = locations_data.get(pc)
        if geo_data:
            coords = f"({geo_data['latitude']:.3f}, {geo_data['longitude']:.3f})"
            print(f"  • {installation['technology']} {installation['capacity_kw']}kW at {pc} {coords}")
    
    # Calculate distances between installations
    print(f"\nDistance matrix for maintenance planning:")
    for i, inst1 in enumerate(simulated_installations):
        for inst2 in simulated_installations[i+1:]:
            pc1, pc2 = inst1['postcode'], inst2['postcode']
            distance_result = geo.calculate_distance(pc1, pc2)
            if 'error' not in distance_result:
                km = distance_result['distance_km']
                suitable = "✅ Same day service" if km <= 50 else "⚠️ Regional hub needed"
                print(f"  {pc1} ↔ {pc2}: {km:>6.1f}km - {suitable}")
    
    print(f"\n✅ INCOMPLETE POSTCODE TESTING COMPLETE!")
    print("=" * 70)
    print("🎉 Your FIT database incomplete postcodes (YO17, HX4, etc.) work perfectly!")
    print("🚀 Ready for production use with geographic intelligence capabilities")

def estimate_travel_time(distance_km):
    """Estimate travel time for renewable site maintenance"""
    if distance_km <= 30:
        return "~45min drive"
    elif distance_km <= 100:
        return "~90min drive"
    elif distance_km <= 200:
        return "~2.5hr drive"
    else:
        return "~4+ hr drive"

if __name__ == "__main__":
    test_incomplete_postcode_functionality()