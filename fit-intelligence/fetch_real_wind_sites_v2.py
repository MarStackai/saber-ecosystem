#!/usr/bin/env python3
"""
Fetch real wind sites from ChromaDB and create GeoJSON with financial data
Properly handles pre-FIT sites (before April 1, 2010)
"""
import chromadb
import json
from datetime import datetime

def get_uk_coordinates(postcode):
    """Get approximate UK coordinates from postcode"""
    postcode_coords = {
        'AB': (-2.1, 57.1),  # Aberdeen
        'AL': (-0.3, 51.8),  # St Albans
        'B': (-1.9, 52.5),   # Birmingham
        'BA': (-2.4, 51.3),  # Bath
        'BB': (-2.5, 53.7),  # Blackburn
        'BD': (-1.75, 53.8), # Bradford
        'BH': (-2.0, 50.7),  # Bournemouth
        'BL': (-2.4, 53.6),  # Bolton
        'BN': (-0.1, 50.8),  # Brighton
        'BR': (0.0, 51.4),   # Bromley
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
        'ME': (0.5, 51.4),   # Medway
        'MK': (-0.8, 52.0),  # Milton Keynes
        'ML': (-3.9, 55.8),  # Motherwell
        'N': (-0.1, 51.55),  # North London
        'NE': (-1.6, 55.0),  # Newcastle
        'NG': (-1.2, 52.95), # Nottingham
        'NN': (-0.9, 52.2),  # Northampton
        'NP': (-3.0, 51.6),  # Newport
        'NR': (1.3, 52.6),   # Norwich
        'NW': (-0.2, 51.55), # Northwest London
        'OL': (-2.1, 53.5),  # Oldham
        'OX': (-1.3, 51.8),  # Oxford
        'PA': (-5.0, 56.4),  # Paisley
        'PE': (-0.2, 52.6),  # Peterborough
        'PH': (-3.4, 56.4),  # Perth
        'PL': (-4.1, 50.4),  # Plymouth
        'PO': (-1.1, 50.8),  # Portsmouth
        'PR': (-2.7, 53.8),  # Preston
        'RG': (-0.98, 51.45),# Reading
        'RH': (-0.1, 51.1),  # Redhill
        'RM': (0.2, 51.6),   # Romford
        'S': (-1.47, 53.38), # Sheffield
        'SA': (-3.9, 51.6),  # Swansea
        'SE': (0.0, 51.45),  # Southeast London
        'SG': (-0.2, 51.9),  # Stevenage
        'SK': (-2.0, 53.4),  # Stockport
        'SL': (-0.6, 51.5),  # Slough
        'SM': (-0.2, 51.4),  # Sutton
        'SN': (-1.8, 51.6),  # Swindon
        'SO': (-1.4, 50.9),  # Southampton
        'SP': (-1.8, 51.1),  # Salisbury
        'SR': (-1.4, 54.9),  # Sunderland
        'SS': (0.7, 51.6),   # Southend
        'ST': (-2.2, 53.0),  # Stoke
        'SW': (-0.15, 51.45),# Southwest London
        'SY': (-2.7, 52.7),  # Shrewsbury
        'TA': (-3.1, 51.0),  # Taunton
        'TD': (-2.5, 55.6),  # Galashiels
        'TF': (-2.5, 52.7),  # Telford
        'TN': (0.3, 51.1),   # Tunbridge
        'TQ': (-3.5, 50.5),  # Torquay
        'TR': (-5.0, 50.3),  # Truro
        'TS': (-1.2, 54.6),  # Middlesbrough
        'TW': (-0.3, 51.45), # Twickenham
        'UB': (-0.4, 51.5),  # Uxbridge
        'W': (-0.2, 51.5),   # West London
        'WA': (-2.5, 53.4),  # Warrington
        'WC': (-0.12, 51.52),# West Central London
        'WD': (-0.4, 51.65), # Watford
        'WF': (-1.5, 53.7),  # Wakefield
        'WN': (-2.6, 53.5),  # Wigan
        'WR': (-2.2, 52.2),  # Worcester
        'WS': (-2.0, 52.6),  # Walsall
        'WV': (-2.1, 52.6),  # Wolverhampton
        'YO': (-1.1, 54.0),  # York
        'ZE': (-1.2, 60.2),  # Shetland
        'NAN': (0.1, 51.5)   # Default to London for unknown
    }
    
    if not postcode:
        return None, None
        
    prefix = postcode[:2].upper() if len(postcode) >= 2 else postcode.upper()
    if prefix in postcode_coords:
        lon, lat = postcode_coords[prefix]
        # Add small random variation
        import random
        lon += random.uniform(-0.1, 0.1)
        lat += random.uniform(-0.05, 0.05)
        return lon, lat
    
    # Try single letter
    prefix = postcode[0].upper() if postcode else 'NAN'
    if prefix in postcode_coords:
        lon, lat = postcode_coords[prefix]
        import random
        lon += random.uniform(-0.1, 0.1)
        lat += random.uniform(-0.05, 0.05)
        return lon, lat
        
    return postcode_coords.get('NAN')

def determine_scheme_type(commission_date):
    """Determine if site is FIT, ROC or unknown"""
    if not commission_date:
        return 'UNKNOWN'
    
    # FIT scheme started April 1, 2010
    if commission_date < '2010-04-01':
        return 'ROC'  # Renewable Obligation Certificate
    elif commission_date <= '2019-03-31':
        return 'FIT'  # Feed-in Tariff
    else:
        return 'POST-FIT'  # After FIT closed

def get_all_wind_sites():
    """Fetch all wind sites from ChromaDB with financial data"""
    client = chromadb.PersistentClient(path='chroma_db')
    collection = client.get_collection('commercial_fit_sites')
    
    batch_size = 5000
    offset = 0
    features = []
    
    # Statistics
    stats = {
        'total': 0,
        'fit': 0,
        'roc': 0,
        'unknown': 0,
        'with_financials': 0,
        'without_financials': 0
    }
    
    while True:
        results = collection.get(
            limit=batch_size,
            offset=offset,
            where={'technology': 'Wind'},
            include=['metadatas']
        )
        
        if not results['metadatas']:
            break
            
        for metadata in results['metadatas']:
            stats['total'] += 1
            
            # Get basic data
            postcode = str(metadata.get('postcode', '')).strip()
            if not postcode or postcode == 'nan':
                postcode = 'NAN'
                
            # Get coordinates
            lon, lat = get_uk_coordinates(postcode)
            if not lon or not lat:
                continue
            
            # Calculate years remaining and age
            commission_date = metadata.get('commission_date', '')
            if commission_date:
                try:
                    comm_year = int(str(commission_date)[:4])
                    expiry_year = comm_year + 20
                    current_year = datetime.now().year
                    years_left = max(expiry_year - current_year, 0)
                    age_years = current_year - comm_year
                except:
                    years_left = 0
                    age_years = 0
            else:
                years_left = 0
                age_years = 0
            
            # Determine repowering window
            if years_left <= 0:
                window = 'EXPIRED'
                priority = 'LOW'
            elif years_left <= 2:
                window = 'IMMEDIATE'
                priority = 'CRITICAL'
            elif years_left <= 5:
                window = 'URGENT'
                priority = 'HIGH'
            elif years_left <= 10:
                window = 'OPTIMAL'
                priority = 'MEDIUM'
            else:
                window = 'TOO_EARLY'
                priority = 'LOW'
            
            # Determine scheme type
            scheme = determine_scheme_type(commission_date)
            if scheme == 'FIT':
                stats['fit'] += 1
            elif scheme == 'ROC':
                stats['roc'] += 1
            else:
                stats['unknown'] += 1
            
            # Get financial data
            tariff = float(metadata.get('tariff_p_kwh', 0))
            generation_mwh = float(metadata.get('annual_generation_mwh', 0))
            
            # For ROC sites, estimate value (ROCs typically worth ~£45-55/MWh)
            if scheme == 'ROC' and generation_mwh > 0:
                # Estimate ROC value at £50/MWh
                annual_income = generation_mwh * 50  # £50 per MWh
                total_value = annual_income * max(years_left, 0)
                tariff_display = 0  # No FIT tariff
                income_type = 'ROC'
            elif tariff > 0 and generation_mwh > 0:
                annual_income = (generation_mwh * 1000 * tariff) / 100
                total_value = annual_income * max(years_left, 0)
                tariff_display = tariff
                income_type = 'FIT'
                stats['with_financials'] += 1
            else:
                annual_income = 0
                total_value = 0
                tariff_display = tariff
                income_type = 'NONE'
                stats['without_financials'] += 1
                
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "id": str(metadata.get('fit_id', 'Unknown')),
                    "score": 0.75,
                    "priority": priority,
                    "remaining_fit_years": years_left,
                    "repowering_window": window,
                    "capacity_mw": float(metadata.get('capacity_mw', 0)),
                    "location": f"{postcode} - UK",
                    "postcode": postcode,
                    "age_years": age_years,
                    "tariff_p_kwh": tariff_display,
                    "annual_income": annual_income,
                    "total_remaining_value": total_value,
                    "annual_generation_mwh": generation_mwh,
                    "scheme_type": scheme,
                    "income_type": income_type,
                    "commission_date": commission_date[:10] if commission_date else 'Unknown'
                }
            }
            features.append(feature)
        
        offset += batch_size
        if len(results['metadatas']) < batch_size:
            break
    
    print(f"\nStatistics:")
    print(f"  Total wind sites: {stats['total']}")
    print(f"  FIT sites (Apr 2010 - Mar 2019): {stats['fit']}")
    print(f"  ROC sites (pre-Apr 2010): {stats['roc']}")
    print(f"  Unknown/Post-FIT: {stats['unknown']}")
    print(f"  Sites with financial data: {stats['with_financials']}")
    print(f"  Sites without financial data: {stats['without_financials']}")
    
    return features

def main():
    print("Fetching real wind sites from ChromaDB...")
    features = get_all_wind_sites()
    
    # Sort by total remaining value
    features.sort(key=lambda x: x['properties'].get('total_remaining_value', 0), reverse=True)
    
    print(f"\nFound {len(features)} wind sites with UK coordinates")
    
    # Save to file
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    with open('wind_sites_with_roc_data.json', 'w') as f:
        json.dump(geojson, f)
    
    print(f"Saved {len(features)} sites to wind_sites_with_roc_data.json")
    
    # Display top sites
    print("\nTop 10 sites by value:")
    for i, feature in enumerate(features[:10]):
        props = feature['properties']
        scheme = props.get('scheme_type', 'UNKNOWN')
        income_type = props.get('income_type', 'NONE')
        print(f"  {props['id']}: {props['postcode']} - {props['capacity_mw']:.2f}MW - "
              f"£{props.get('annual_income', 0):,.0f}/year ({income_type}) - {scheme} scheme")

if __name__ == "__main__":
    main()