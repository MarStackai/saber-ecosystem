#!/usr/bin/env python3
"""
Complete UK postcode prefix mappings for nationwide coverage
"""

# Complete UK postcode prefixes by region/area
UK_POSTCODE_PREFIXES = {
    # ENGLAND - London
    'london': ['E', 'EC', 'N', 'NW', 'SE', 'SW', 'W', 'WC'],
    'east_london': ['E'],
    'north_london': ['N'],
    'northwest_london': ['NW'],
    'south_london': ['SE', 'SW'],
    'west_london': ['W', 'WC'],
    'central_london': ['EC', 'WC'],
    
    # ENGLAND - South East
    'brighton': ['BN'],
    'canterbury': ['CT'],
    'guildford': ['GU'],
    'medway': ['ME'],
    'oxford': ['OX'],
    'portsmouth': ['PO'],
    'reading': ['RG'],
    'slough': ['SL'],
    'southampton': ['SO'],
    'tonbridge': ['TN'],
    
    # ENGLAND - Counties (South East)
    'surrey': ['GU', 'KT', 'RH', 'SM', 'CR', 'TW'],
    'kent': ['BR', 'CT', 'DA', 'ME', 'TN'],
    'essex': ['CM', 'CO', 'IG', 'RM', 'SS'],
    'sussex': ['BN', 'RH', 'TN', 'PO'],
    'east_sussex': ['BN', 'TN'],
    'west_sussex': ['RH', 'PO', 'BN'],
    'hampshire': ['SO', 'PO', 'GU', 'RG', 'SP'],
    'berkshire': ['RG', 'SL'],
    'hertfordshire': ['AL', 'EN', 'HP', 'SG', 'WD'],
    'buckinghamshire': ['HP', 'MK', 'SL'],
    'oxfordshire': ['OX', 'RG'],
    'bedfordshire': ['LU', 'MK', 'SG'],
    
    # ENGLAND - South West
    'bath': ['BA'],
    'bournemouth': ['BH'],
    'bristol': ['BS'],
    'dorchester': ['DT'],
    'exeter': ['EX'],
    'gloucester': ['GL'],
    'plymouth': ['PL'],
    'salisbury': ['SP'],
    'swindon': ['SN'],
    'taunton': ['TA'],
    'torquay': ['TQ'],
    'truro': ['TR'],
    
    # ENGLAND - Counties (South West)
    'devon': ['EX', 'PL', 'TQ'],
    'somerset': ['BA', 'BS', 'TA'],
    'gloucestershire': ['GL', 'BS'],
    'wiltshire': ['BA', 'SN', 'SP'],
    
    # ENGLAND - East
    'cambridge': ['CB'],
    'chelmsford': ['CM'],
    'colchester': ['CO'],
    'hemel_hempstead': ['HP'],
    'ipswich': ['IP'],
    'luton': ['LU'],
    'norwich': ['NR'],
    'peterborough': ['PE'],
    'southend': ['SS'],
    'stevenage': ['SG'],
    'st_albans': ['AL'],
    
    # ENGLAND - Counties (East)
    'cambridgeshire': ['CB', 'PE'],
    'norfolk': ['NR', 'IP'],
    'suffolk': ['IP', 'CB', 'CO'],
    
    # ENGLAND - West Midlands
    'birmingham': ['B'],
    'coventry': ['CV'],
    'dudley': ['DY'],
    'hereford': ['HR'],
    'shrewsbury': ['SY'],
    'stoke': ['ST'],
    'telford': ['TF'],
    'walsall': ['WS'],
    'worcester': ['WR'],
    'wolverhampton': ['WV'],
    
    # ENGLAND - Counties (Midlands)
    'warwickshire': ['CV', 'B'],
    'worcestershire': ['WR', 'B', 'DY'],
    'staffordshire': ['ST', 'WS', 'WV', 'DE'],
    'shropshire': ['SY', 'TF', 'WV'],
    'herefordshire': ['HR', 'WR'],
    
    # ENGLAND - East Midlands
    'derby': ['DE'],
    'leicester': ['LE'],
    'lincoln': ['LN'],
    'northampton': ['NN'],
    'nottingham': ['NG'],
    
    # ENGLAND - Counties (East Midlands)
    'derbyshire': ['DE', 'S', 'SK'],
    'leicestershire': ['LE', 'CV'],
    'lincolnshire': ['LN', 'PE', 'DN'],
    'northamptonshire': ['NN', 'PE'],
    'nottinghamshire': ['NG', 'DN', 'S'],
    
    # ENGLAND - Yorkshire and Humber
    'bradford': ['BD'],
    'doncaster': ['DN'],
    'halifax': ['HX'],
    'harrogate': ['HG'],
    'huddersfield': ['HD'],
    'hull': ['HU'],
    'leeds': ['LS'],
    'sheffield': ['S'],
    'wakefield': ['WF'],
    'york': ['YO'],
    
    # ENGLAND - North West
    'blackburn': ['BB'],
    'blackpool': ['FY'],
    'bolton': ['BL'],
    'carlisle': ['CA'],
    'chester': ['CH'],
    'crewe': ['CW'],
    'lancaster': ['LA'],
    'liverpool': ['L'],
    'manchester': ['M'],
    'oldham': ['OL'],
    'preston': ['PR'],
    'stockport': ['SK'],
    'warrington': ['WA'],
    'wigan': ['WN'],
    
    # ENGLAND - Counties (North West)
    'lancashire': ['BB', 'BL', 'FY', 'LA', 'OL', 'PR'],
    'cheshire': ['CH', 'CW', 'SK', 'WA'],
    'cumbria': ['CA', 'LA'],
    'greater_manchester': ['M', 'BL', 'OL', 'SK', 'WN'],
    'merseyside': ['L', 'CH', 'WA', 'PR'],
    
    # ENGLAND - North East
    'darlington': ['DL'],
    'durham': ['DH'],
    'middlesbrough': ['TS'],
    'newcastle': ['NE'],
    'sunderland': ['SR'],
    
    # ENGLAND - Counties (North East)
    'northumberland': ['NE', 'TD'],
    'county_durham': ['DH', 'DL', 'TS'],
    'tyne_and_wear': ['NE', 'SR', 'DH'],
    
    # ENGLAND - South West
    'cornwall': ['TR', 'PL'],
    'truro': ['TR'],
    'plymouth': ['PL'],
    'exeter': ['EX'],
    'bristol': ['BS'],
    'bath': ['BA'],
    'bournemouth': ['BH'],
    'dorchester': ['DT'],
    'dorset': ['DT', 'BH'],
    'gloucester': ['GL'],
    'swindon': ['SN'],
    'taunton': ['TA'],
    'torquay': ['TQ'],
    
    # SCOTLAND
    'aberdeen': ['AB'],
    'dundee': ['DD'],
    'dumfries': ['DG'],
    'edinburgh': ['EH'],
    'falkirk': ['FK'],
    'glasgow': ['G'],
    'inverness': ['IV'],
    'kilmarnock': ['KA'],
    'kirkwall': ['KW'],
    'kirkcaldy': ['KY'],
    'motherwell': ['ML'],
    'paisley': ['PA'],
    'perth': ['PH'],
    'galashiels': ['TD'],
    'shetland': ['ZE'],
    
    # WALES
    'cardiff': ['CF'],
    'llandudno': ['LL'],
    'llandrindod': ['LD'],
    'newport': ['NP'],
    'swansea': ['SA'],
    'shrewsbury_wales': ['SY'],  # Shared with England
    
    # NORTHERN IRELAND
    'belfast': ['BT'],
}

# Regional groupings
REGIONS = {
    'scotland': ['AB', 'DD', 'DG', 'EH', 'FK', 'G', 'IV', 'KA', 'KW', 'KY', 'ML', 'PA', 'PH', 'TD', 'ZE'],
    'wales': ['CF', 'LL', 'LD', 'NP', 'SA', 'SY'],
    'northern_ireland': ['BT'],
    'london': ['E', 'EC', 'N', 'NW', 'SE', 'SW', 'W', 'WC'],
    'yorkshire': ['BD', 'DN', 'HX', 'HG', 'HD', 'HU', 'LS', 'S', 'WF', 'YO'],
    'north_west': ['BB', 'BL', 'CA', 'CH', 'CW', 'FY', 'L', 'LA', 'M', 'OL', 'PR', 'SK', 'WA', 'WN'],
    'north_east': ['DH', 'DL', 'NE', 'SR', 'TS'],
    'midlands': ['B', 'CV', 'DE', 'DY', 'HR', 'LE', 'LN', 'NG', 'NN', 'ST', 'SY', 'TF', 'WR', 'WS', 'WV'],
    'east': ['AL', 'CB', 'CM', 'CO', 'HP', 'IP', 'LU', 'NR', 'PE', 'SG', 'SS'],
    'south_east': ['BN', 'CT', 'GU', 'ME', 'OX', 'PO', 'RG', 'SL', 'SO', 'TN'],
    'south_west': ['BA', 'BH', 'BS', 'DT', 'EX', 'GL', 'PL', 'SN', 'SP', 'TA', 'TQ', 'TR'],
}

# Complete list of ALL UK postcode prefixes for validation
ALL_UK_PREFIXES = [
    'AB', 'AL', 'B', 'BA', 'BB', 'BD', 'BH', 'BL', 'BN', 'BR', 'BS', 'BT', 'CA', 'CB', 'CF', 'CH', 'CM', 'CO', 
    'CR', 'CT', 'CV', 'CW', 'DA', 'DD', 'DE', 'DG', 'DH', 'DL', 'DN', 'DT', 'DY', 'E', 'EC', 'EH', 'EN', 'EX', 
    'FK', 'FY', 'G', 'GL', 'GU', 'HA', 'HD', 'HG', 'HP', 'HR', 'HS', 'HU', 'HX', 'IG', 'IM', 'IP', 'IV', 'JE', 
    'KA', 'KT', 'KW', 'KY', 'L', 'LA', 'LD', 'LE', 'LL', 'LN', 'LS', 'LU', 'M', 'ME', 'MK', 'ML', 'N', 'NE', 
    'NG', 'NN', 'NP', 'NR', 'NW', 'OL', 'OX', 'PA', 'PE', 'PH', 'PL', 'PO', 'PR', 'RG', 'RH', 'RM', 'S', 'SA', 
    'SE', 'SG', 'SK', 'SL', 'SM', 'SN', 'SO', 'SP', 'SR', 'SS', 'ST', 'SW', 'SY', 'TA', 'TD', 'TF', 'TN', 'TQ', 
    'TR', 'TS', 'TW', 'UB', 'W', 'WA', 'WC', 'WD', 'WF', 'WN', 'WR', 'WS', 'WV', 'YO', 'ZE'
]

def get_location_prefixes(location: str) -> list:
    """
    Get postcode prefixes for a location (city, region, or country)
    Returns empty list if no specific location (searches all UK)
    """
    if not location:
        return []  # No filter = search all UK
    
    location_lower = location.lower().strip()
    
    # Check specific locations first
    if location_lower in UK_POSTCODE_PREFIXES:
        return UK_POSTCODE_PREFIXES[location_lower]
    
    # Check regions
    if location_lower in REGIONS:
        return REGIONS[location_lower]
    
    # Check country names
    if location_lower in ['uk', 'united kingdom', 'britain', 'great britain']:
        return []  # No filter = all UK
    
    if location_lower == 'england':
        # Return all English postcodes (exclude Scotland, Wales, NI)
        scotland_wales_ni = set(REGIONS['scotland'] + REGIONS['wales'] + REGIONS['northern_ireland'])
        return [p for p in ALL_UK_PREFIXES if p not in scotland_wales_ni]
    
    # Try partial matches for flexibility
    for key, prefixes in UK_POSTCODE_PREFIXES.items():
        if location_lower in key or key in location_lower:
            return prefixes
    
    for key, prefixes in REGIONS.items():
        if location_lower in key or key in location_lower:
            return prefixes
    
    # Check if it's a postcode prefix itself
    upper_location = location.upper()
    if upper_location in ALL_UK_PREFIXES:
        return [upper_location]
    
    # No match found - return empty to search all
    return []

def is_valid_uk_postcode(postcode: str) -> bool:
    """Check if a postcode starts with a valid UK prefix"""
    if not postcode:
        return False
    
    postcode_upper = postcode.upper().strip()
    
    # Check 2-letter prefixes first
    if len(postcode_upper) >= 2:
        two_letter = postcode_upper[:2]
        if two_letter in ALL_UK_PREFIXES:
            return True
    
    # Check 1-letter prefixes
    if len(postcode_upper) >= 1:
        one_letter = postcode_upper[:1]
        if one_letter in ALL_UK_PREFIXES:
            return True
    
    return False