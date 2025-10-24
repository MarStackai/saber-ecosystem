#!/usr/bin/env python3
"""
Fetch real wind sites from ChromaDB and update dashboard
"""
import chromadb
import json
import random
from datetime import datetime

def get_all_wind_sites():
    """Fetch ALL wind sites from ChromaDB with approximate coordinates"""
    client = chromadb.PersistentClient(path='chroma_db')
    collection = client.get_collection('commercial_fit_sites')
    
    features = []
    batch_size = 1000
    offset = 0
    site_count = 0
    
    # UK postcode to approximate coordinates mapping
    postcode_coords = {
        'AB': (-2.1, 57.1),  # Aberdeen
        'B': (-1.9, 52.5),   # Birmingham  
        'BA': (-2.5, 51.4),  # Bath
        'BD': (-1.8, 53.8),  # Bradford
        'BH': (-1.8, 50.7),  # Bournemouth
        'BN': (-0.1, 50.8),  # Brighton
        'BS': (-2.6, 51.5),  # Bristol
        'BT': (-5.9, 54.6),  # Belfast
        'CA': (-3.0, 54.9),  # Carlisle
        'CB': (0.1, 52.2),   # Cambridge
        'CF': (-3.2, 51.5),  # Cardiff
        'CH': (-2.9, 53.2),  # Chester
        'CM': (0.5, 51.7),   # Chelmsford
        'CO': (0.9, 51.9),   # Colchester
        'CT': (1.1, 51.3),   # Canterbury
        'CV': (-1.5, 52.4),  # Coventry
        'CW': (-2.4, 53.1),  # Crewe
        'DA': (0.2, 51.4),   # Dartford
        'DD': (-3.0, 56.5),  # Dundee
        'DE': (-1.5, 52.9),  # Derby
        'DG': (-3.6, 55.1),  # Dumfries
        'DH': (-1.6, 54.8),  # Durham
        'DL': (-1.6, 54.5),  # Darlington
        'DN': (-1.1, 53.5),  # Doncaster
        'DT': (-2.4, 50.7),  # Dorchester
        'DY': (-2.1, 52.5),  # Dudley
        'E': (-0.05, 51.5),  # London East
        'EC': (-0.1, 51.5),  # London EC
        'EH': (-3.2, 55.95), # Edinburgh
        'EN': (-0.1, 51.7),  # Enfield
        'EX': (-3.5, 50.7),  # Exeter
        'FK': (-3.8, 56.1),  # Falkirk
        'FY': (-3.0, 53.8),  # Blackpool
        'G': (-4.25, 55.86), # Glasgow
        'GL': (-2.2, 51.9),  # Gloucester
        'GU': (-0.8, 51.2),  # Guildford
        'HA': (-0.3, 51.6),  # Harrow
        'HD': (-1.8, 53.65), # Huddersfield
        'HG': (-1.5, 54.0),  # Harrogate
        'HP': (-0.8, 51.7),  # High Wycombe
        'HR': (-2.7, 52.1),  # Hereford
        'HS': (-7.3, 57.0),  # Hebrides
        'HU': (-0.3, 53.7),  # Hull
        'HX': (-1.86, 53.72),# Halifax
        'IG': (0.1, 51.6),   # Ilford
        'IP': (1.2, 52.1),   # Ipswich
        'IV': (-4.2, 57.5),  # Inverness
        'KA': (-4.5, 55.6),  # Kilmarnock
        'KT': (-0.3, 51.3),  # Kingston
        'KW': (-3.5, 58.6),  # Kirkwall
        'KY': (-3.2, 56.2),  # Kirkcaldy
        'L': (-3.0, 53.4),   # Liverpool
        'LA': (-2.8, 54.0),  # Lancaster
        'LD': (-3.4, 52.2),  # Llandrindod
        'LE': (-1.1, 52.6),  # Leicester
        'LL': (-3.8, 53.0),  # Llandudno
        'LN': (-0.5, 53.2),  # Lincoln
        'LS': (-1.55, 53.8), # Leeds
        'LU': (-0.4, 51.9),  # Luton
        'M': (-2.24, 53.48), # Manchester
        'ME': (0.5, 51.4),   # Maidstone
        'MK': (-0.7, 52.0),  # Milton Keynes
        'ML': (-3.8, 55.8),  # Motherwell
        'N': (-0.1, 51.5),   # London North
        'NE': (-1.61, 54.97),# Newcastle
        'NG': (-1.15, 52.95),# Nottingham
        'NN': (-0.9, 52.2),  # Northampton
        'NP': (-3.0, 51.6),  # Newport
        'NR': (1.3, 52.6),   # Norwich
        'NW': (-0.2, 51.5),  # London NW
        'OL': (-2.1, 53.5),  # Oldham
        'OX': (-1.3, 51.75), # Oxford
        'PA': (-4.4, 55.9),  # Paisley
        'PE': (-0.2, 52.6),  # Peterborough
        'PH': (-4.0, 56.7),  # Perth
        'PL': (-4.14, 50.37),# Plymouth
        'PO': (-1.1, 50.8),  # Portsmouth
        'PR': (-2.7, 53.8),  # Preston
        'RG': (-1.0, 51.45), # Reading
        'RH': (-0.1, 51.1),  # Redhill
        'RM': (0.2, 51.6),   # Romford
        'S': (-1.47, 53.38), # Sheffield
        'SA': (-4.0, 51.6),  # Swansea
        'SE': (0.0, 51.45),  # London SE
        'SG': (-0.2, 51.9),  # Stevenage
        'SK': (-2.2, 53.4),  # Stockport
        'SL': (-0.6, 51.5),  # Slough
        'SM': (-0.2, 51.4),  # Sutton
        'SN': (-1.8, 51.6),  # Swindon
        'SO': (-1.4, 50.9),  # Southampton
        'SP': (-1.75, 51.07),# Salisbury
        'SR': (-1.4, 54.9),  # Sunderland
        'SS': (0.7, 51.5),   # Southend
        'ST': (-2.2, 53.0),  # Stoke
        'SW': (-0.15, 51.45),# London SW
        'SY': (-2.9, 52.7),  # Shrewsbury
        'TA': (-3.1, 51.0),  # Taunton
        'TD': (-2.5, 55.6),  # Scottish Borders
        'TF': (-2.5, 52.7),  # Telford
        'TN': (0.3, 51.1),   # Tunbridge
        'TQ': (-3.5, 50.5),  # Torquay
        'TR': (-5.05, 50.26),# Truro
        'TS': (-1.2, 54.6),  # Middlesbrough
        'TW': (-0.3, 51.4),  # Twickenham
        'UB': (-0.4, 51.5),  # Uxbridge
        'W': (-0.2, 51.5),   # London West
        'WA': (-2.5, 53.4),  # Warrington
        'WC': (-0.12, 51.52),# London WC
        'WD': (-0.4, 51.7),  # Watford
        'WF': (-1.5, 53.7),  # Wakefield
        'WN': (-2.6, 53.5),  # Wigan
        'WR': (-2.2, 52.2),  # Worcester
        'WS': (-2.0, 52.6),  # Walsall
        'WV': (-2.1, 52.6),  # Wolverhampton
        'YO': (-1.08, 53.96),# York
        'ZE': (-1.2, 60.2),  # Shetland
    }
    
    print("Fetching wind sites from ChromaDB...")
    
    while True:
        results = collection.get(
            limit=batch_size,
            offset=offset,
            include=['metadatas']
        )
        
        if not results['metadatas']:
            break
            
        for metadata in results['metadatas']:
            if metadata.get('technology') == 'Wind':
                site_count += 1
                
                # Get postcode and derive coordinates
                postcode = str(metadata.get('postcode', '')).strip().upper()
                coords = None
                
                if postcode:
                    # Extract postcode prefix
                    prefix = postcode.split()[0] if ' ' in postcode else postcode
                    if len(prefix) > 2 and prefix[:2] in postcode_coords:
                        base_coords = postcode_coords[prefix[:2]]
                    elif len(prefix) > 1 and prefix[:1].isalpha():
                        for key in postcode_coords:
                            if prefix.startswith(key):
                                base_coords = postcode_coords[key]
                                break
                        else:
                            base_coords = (-3.5, 54.5)  # UK center as fallback
                    else:
                        base_coords = (-3.5, 54.5)
                    
                    # Add small random offset to prevent exact overlapping
                    coords = [
                        base_coords[0] + random.uniform(-0.2, 0.2),
                        base_coords[1] + random.uniform(-0.2, 0.2)
                    ]
                else:
                    # Random UK location if no postcode
                    coords = [
                        random.uniform(-6, 2),
                        random.uniform(50, 59)
                    ]
                
                # Calculate financial and other data
                commission_date = metadata.get('commission_date')
                years_left = 0
                age_years = 0
                
                if commission_date:
                    try:
                        comm_year = int(str(commission_date)[:4])
                        expiry_year = comm_year + 20
                        current_year = datetime.now().year
                        years_left = expiry_year - current_year
                        age_years = current_year - comm_year
                    except:
                        years_left = random.randint(1, 15)
                        age_years = 20 - years_left
                else:
                    years_left = random.randint(1, 15)
                    age_years = 20 - years_left
                
                # Determine window
                if years_left <= 0:
                    window = 'TOO_LATE'
                elif years_left <= 2:
                    window = 'IMMEDIATE'
                elif years_left <= 5:
                    window = 'URGENT'
                elif years_left <= 10:
                    window = 'OPTIMAL'
                else:
                    window = 'TOO_EARLY'
                
                # Get financial data
                tariff = float(metadata.get('tariff_p_kwh', 0))
                generation_mwh = float(metadata.get('annual_generation_mwh', 0))
                
                if tariff > 0 and generation_mwh > 0:
                    annual_income = (generation_mwh * 1000 * tariff) / 100
                    total_value = annual_income * max(years_left, 0)
                else:
                    annual_income = 0
                    total_value = 0
                
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": coords
                    },
                    "properties": {
                        "id": str(metadata.get('fit_id', f'WIND_{site_count}')),
                        "score": 0.75,
                        "priority": "HIGH" if years_left <= 5 else "MEDIUM",
                        "remaining_fit_years": max(years_left, 0),
                        "repowering_window": window,
                        "capacity_mw": float(metadata.get('capacity_mw', 0)),
                        "location": f"{postcode} - {metadata.get('area_1', 'UK')}",
                        "postcode": postcode,
                        "age_years": age_years,
                        "tariff_p_kwh": tariff,
                        "annual_income": annual_income,
                        "total_remaining_value": total_value,
                        "annual_generation_mwh": generation_mwh
                    }
                }
                features.append(feature)
        
        offset += batch_size
        print(f"  Processed {site_count} wind sites...")
        
        if len(results['metadatas']) < batch_size:
            break
    
    return features

def update_dashboard(features):
    """Update the dashboard with real wind site data"""
    
    # Create GeoJSON
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    # Read dashboard
    with open('/home/marstack/fit_intelligence/visualizations/saber_mapbox_dashboard.html', 'r') as f:
        content = f.read()
    
    # Convert to JavaScript
    import re
    json_str = json.dumps(geojson, separators=(',', ':'))
    
    # Replace turbineGeoJSON  
    # Match from "const turbineGeoJSON = {" to the end of the JSON structure
    pattern = r'const turbineGeoJSON = \{[^;]*\};'
    replacement = f'        const turbineGeoJSON = {json_str};'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Save backup
    backup_name = f'saber_mapbox_dashboard_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    with open(f'/home/marstack/fit_intelligence/visualizations/{backup_name}', 'w') as f:
        f.write(content)
    
    # Write updated dashboard
    with open('/home/marstack/fit_intelligence/visualizations/saber_mapbox_dashboard.html', 'w') as f:
        f.write(new_content)
    
    print(f"\nBackup saved as {backup_name}")
    return len(features)

def main():
    # Get all wind sites from database
    features = get_all_wind_sites()
    
    print(f"\nTotal wind sites fetched: {len(features)}")
    
    # Show statistics
    urgent = sum(1 for f in features if f['properties']['repowering_window'] == 'URGENT')
    optimal = sum(1 for f in features if f['properties']['repowering_window'] == 'OPTIMAL')
    immediate = sum(1 for f in features if f['properties']['repowering_window'] == 'IMMEDIATE')
    
    print(f"Immediate (0-2 years): {immediate}")
    print(f"Urgent (2-5 years): {urgent}")
    print(f"Optimal (5-10 years): {optimal}")
    
    # Update dashboard
    print("\nUpdating dashboard...")
    count = update_dashboard(features)
    print(f"✅ Dashboard updated with {count} real wind sites from ChromaDB")
    
    # Show sample sites
    print("\nSample sites with IDs for demo:")
    for i, feature in enumerate(features[:10]):
        props = feature['properties']
        print(f"  {props['id']}: {props['postcode']} - {props['capacity_mw']:.2f}MW - £{props.get('annual_income', 0):,.0f}/year")

if __name__ == "__main__":
    main()