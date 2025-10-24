#!/usr/bin/env python3
"""
UK Geographic Intelligence System
Integrates with Postcodes.io and other UK geographic APIs for renewable energy site analysis
"""

import requests
import json
import logging
from typing import Dict, List, Tuple, Optional
import math
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UKGeoIntelligence:
    """UK Geographic Intelligence for renewable energy site analysis"""
    
    def __init__(self):
        self.postcodes_base_url = "https://api.postcodes.io"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FIT-Intelligence-Platform/1.0'
        })
        
        # Cache for reducing API calls
        self.postcode_cache = {}
        self.outcode_cache = {}
        self.place_name_cache = {}
        
    def lookup_postcode(self, postcode: str) -> Dict:
        """
        Look up detailed information for a UK postcode
        Returns geographic coordinates, administrative areas, and regional data
        """
        try:
            # Clean postcode format
            postcode_clean = postcode.replace(' ', '').upper()
            
            # Check cache first
            if postcode_clean in self.postcode_cache:
                return self.postcode_cache[postcode_clean]
            
            # Call Postcodes.io API
            response = self.session.get(f"{self.postcodes_base_url}/postcodes/{postcode_clean}")
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 200:
                    result = data['result']
                    
                    geo_data = {
                        'postcode': result['postcode'],
                        'latitude': result['latitude'],
                        'longitude': result['longitude'],
                        'country': result['country'],
                        'region': result['region'],
                        'admin_district': result['admin_district'],
                        'admin_county': result['admin_county'],
                        'admin_ward': result['admin_ward'],
                        'parliamentary_constituency': result['parliamentary_constituency'],
                        'european_electoral_region': result['european_electoral_region'],
                        'primary_care_trust': result['primary_care_trust'],
                        'lsoa': result['lsoa'],  # Lower Layer Super Output Area
                        'msoa': result['msoa'],  # Middle Layer Super Output Area
                        'nuts': result['nuts'],   # Nomenclature of Territorial Units for Statistics
                        'incode': result['incode'],
                        'outcode': result['outcode'],
                        'quality': result['quality'],
                        'eastings': result['eastings'],
                        'northings': result['northings'],
                        'ccg': result['ccg'],  # Clinical Commissioning Group
                        'ced': result['ced'],  # County Electoral Division
                        'distance': None  # Will be set when calculating distances
                    }
                    
                    # Cache the result
                    self.postcode_cache[postcode_clean] = geo_data
                    
                    return geo_data
                else:
                    return {'error': f'Postcode {postcode} not found'}
            else:
                return {'error': f'API error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Postcode lookup error for {postcode}: {e}")
            return {'error': str(e)}
    
    def lookup_incomplete_postcode(self, incomplete_postcode: str) -> Dict:
        """
        Look up information for incomplete postcodes (outcodes like YO17, HX4)
        Returns approximate geographic data for the postcode area
        """
        try:
            # Clean outcode format
            outcode_clean = incomplete_postcode.replace(' ', '').upper()
            
            # Check cache first
            if outcode_clean in self.outcode_cache:
                return self.outcode_cache[outcode_clean]
            
            # Call Postcodes.io outcode API
            response = self.session.get(f"{self.postcodes_base_url}/outcodes/{outcode_clean}")
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 200:
                    result = data['result']
                    
                    geo_data = {
                        'outcode': result['outcode'],
                        'latitude': result['latitude'],
                        'longitude': result['longitude'],
                        'country': result['country'],
                        'region': result.get('region'),  # May be None for some outcodes
                        'admin_district': result.get('admin_district'),
                        'admin_county': result.get('admin_county'),
                        'eastings': result['eastings'],
                        'northings': result['northings'],
                        'postcode_type': 'incomplete_outcode',
                        'accuracy': 'approximate',  # Outcode center, not exact
                        'distance': None
                    }
                    
                    # Cache the result
                    self.outcode_cache[outcode_clean] = geo_data
                    
                    return geo_data
                else:
                    return {'error': f'Outcode {incomplete_postcode} not found'}
            else:
                return {'error': f'Outcode API error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Outcode lookup error for {incomplete_postcode}: {e}")
            return {'error': str(e)}
    
    def smart_postcode_lookup(self, postcode: str) -> Dict:
        """
        Smart postcode lookup that handles both complete and incomplete postcodes
        Automatically detects postcode format and uses appropriate API
        """
        try:
            postcode_clean = postcode.replace(' ', '').upper()
            
            # Detect postcode format
            if self._is_complete_postcode(postcode_clean):
                # Full postcode - use standard lookup
                return self.lookup_postcode(postcode_clean)
            else:
                # Incomplete postcode (outcode) - use outcode lookup
                return self.lookup_incomplete_postcode(postcode_clean)
                
        except Exception as e:
            logger.error(f"Smart postcode lookup error for {postcode}: {e}")
            return {'error': str(e)}
    
    def get_postcodes_in_outcode(self, outcode: str, limit: int = 100) -> Dict:
        """
        Get all complete postcodes within an outcode area
        Useful for finding representative postcodes from incomplete data
        """
        try:
            outcode_clean = outcode.replace(' ', '').upper()
            
            # Get nearest postcodes to the outcode center
            outcode_data = self.lookup_incomplete_postcode(outcode_clean)
            if 'error' in outcode_data:
                return outcode_data
            
            lat, lon = outcode_data['latitude'], outcode_data['longitude']
            
            # Find postcodes near the outcode center
            response = self.session.get(
                f"{self.postcodes_base_url}/postcodes",
                params={
                    'lat': lat,
                    'lon': lon,
                    'radius': 5000,  # 5km radius
                    'limit': limit
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 200:
                    # Filter to only postcodes that match the outcode
                    matching_postcodes = []
                    for result in data['result']:
                        if result['postcode'].startswith(outcode_clean):
                            matching_postcodes.append({
                                'postcode': result['postcode'],
                                'latitude': result['latitude'],
                                'longitude': result['longitude'],
                                'distance_from_center_m': result['distance']
                            })
                    
                    return {
                        'outcode': outcode_clean,
                        'center_coordinates': {'lat': lat, 'lon': lon},
                        'matching_postcodes': matching_postcodes,
                        'count': len(matching_postcodes)
                    }
                else:
                    return {'error': 'No postcodes found in outcode area'}
            else:
                return {'error': f'Postcodes in outcode API error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Postcodes in outcode error: {e}")
            return {'error': str(e)}
    
    def lookup_place_name(self, place_name: str) -> Dict:
        """
        Look up UK place name and return geographic data
        Uses Postcodes.io place name search to find postcodes
        """
        try:
            place_clean = place_name.strip().lower()
            
            # Check cache first
            if place_clean in self.place_name_cache:
                return self.place_name_cache[place_clean]
            
            # Use comprehensive UK place name mapping first
            place_mapping = self._get_place_name_mapping()
            if place_clean in place_mapping:
                postcode = place_mapping[place_clean]
                geo_data = self.smart_postcode_lookup(postcode)
                if 'error' not in geo_data:
                    geo_data['place_name'] = place_name.title()
                    geo_data['lookup_method'] = 'place_mapping'
                    self.place_name_cache[place_clean] = geo_data
                    return geo_data
            
            # Fallback: try to find postcodes containing the place name
            # This is a simplified approach - in production you'd use a proper gazetteer
            return self._search_place_by_location(place_name)
            
        except Exception as e:
            logger.error(f"Place name lookup error for {place_name}: {e}")
            return {'error': str(e)}
    
    def _get_place_name_mapping(self) -> Dict:
        """
        Comprehensive UK place name to postcode mapping
        This would be expanded with a full UK gazetteer in production
        """
        return {
            # Major cities
            'london': 'EC1A',
            'birmingham': 'B1', 
            'manchester': 'M1',
            'glasgow': 'G1',
            'liverpool': 'L1',
            'leeds': 'LS1',
            'sheffield': 'S1',
            'bristol': 'BS1',
            'edinburgh': 'EH1',
            'cardiff': 'CF1',
            'newcastle': 'NE1',
            'nottingham': 'NG1',
            'belfast': 'BT1',
            
            # Major towns
            'york': 'YO1',
            'oxford': 'OX1',
            'cambridge': 'CB1',
            'bath': 'BA1',
            'exeter': 'EX1',
            'plymouth': 'PL1',
            'brighton': 'BN1',
            'southampton': 'SO1',
            'portsmouth': 'PO1',
            'reading': 'RG1',
            'milton keynes': 'MK1',
            'coventry': 'CV1',
            'hull': 'HU1',
            'leicester': 'LE1',
            'stoke': 'ST1',
            'derby': 'DE1',
            'swansea': 'SA1',
            'aberdeen': 'AB1',
            'dundee': 'DD1',
            'inverness': 'IV1',
            
            # Renewable energy hotspots
            'cornwall': 'TR1',
            'devon': 'EX1',
            'yorkshire': 'YO1',
            'lancashire': 'PR1',
            'cumbria': 'CA1',
            'scotland': 'EH1',
            'wales': 'CF1',
            'north wales': 'LL1',
            'south wales': 'CF1',
            'west wales': 'SA1',
            'highlands': 'IV1',
            'borders': 'TD1',
            'lake district': 'CA1',
            'peak district': 'S1',
            'cotswolds': 'GL1',
            'norfolk': 'NR1',
            'suffolk': 'IP1',
            'kent': 'CT1',
            'essex': 'CM1',
            'sussex': 'BN1',
            'hampshire': 'SO1',
            'dorset': 'BH1',
            'wiltshire': 'SN1',
            'gloucestershire': 'GL1',
            'worcestershire': 'WR1',
            'warwickshire': 'CV1',
            'northamptonshire': 'NN1',
            'lincolnshire': 'LN1',
            'nottinghamshire': 'NG1',
            'derbyshire': 'DE1',
            'staffordshire': 'ST1',
            'shropshire': 'SY1',
            'herefordshire': 'HR1',
            'cheshire': 'CH1',
            'merseyside': 'L1',
            'greater manchester': 'M1',
            'west yorkshire': 'LS1',
            'south yorkshire': 'S1',
            'north yorkshire': 'YO1',
            'east yorkshire': 'YO25',
            'west midlands': 'B1',
            'east midlands': 'NG1',
            'east anglia': 'NR1',
            'south west': 'BS1',
            'south east': 'GU1',
            'north west': 'M1',
            'north east': 'NE1',
            
            # Specific renewable locations
            'beverley': 'YO17',
            'beverly': 'YO17',
            'halifax': 'HX1',
            'huddersfield': 'HD1',
            'bradford': 'BD1',
            'wakefield': 'WF1',
            'doncaster': 'DN1',
            'rotherham': 'S60',
            'barnsley': 'S70',
            'middlesbrough': 'TS1',
            'sunderland': 'SR1',
            'newcastle upon tyne': 'NE1',
            'carlisle': 'CA1',
            'preston': 'PR1',
            'blackpool': 'FY1',
            'lancaster': 'LA1',
            'chester': 'CH1',
            'warrington': 'WA1',
            'wigan': 'WN1',
            'bolton': 'BL1',
            'oldham': 'OL1',
            'rochdale': 'OL1',
            'salford': 'M1',
            'stockport': 'SK1',
            'macclesfield': 'SK10',
            'crewe': 'CW1',
            'shrewsbury': 'SY1',
            'telford': 'TF1',
            'worcester': 'WR1',
            'hereford': 'HR1',
            'gloucester': 'GL1',
            'cheltenham': 'GL50',
            'swindon': 'SN1',
            'salisbury': 'SP1',
            'winchester': 'SO23',
            'basingstoke': 'RG21',
            'guildford': 'GU1',
            'crawley': 'RH10',
            'hastings': 'TN34',
            'eastbourne': 'BN21',
            'worthing': 'BN11',
            'chichester': 'PO19',
            'newport': 'NP19',
            'wrexham': 'LL11',
            'bangor': 'LL57',
            'aberystwyth': 'SY23',
            'carmarthen': 'SA31',
            'pembroke': 'SA71',
            'tenby': 'SA70',
            'brecon': 'LD3',
            'ayr': 'KA7',
            'stirling': 'FK8',
            'perth': 'PH1',
            'fort william': 'PH33',
            'oban': 'PA34',
            'thurso': 'KW14',
            'orkney': 'KW15',
            'shetland': 'ZE1',
            'isle of wight': 'PO30',
            'guernsey': 'GY1',
            'jersey': 'JE1'
        }
    
    def _search_place_by_location(self, place_name: str) -> Dict:
        """
        Search for place name using coordinate-based approach
        This is a fallback when direct mapping isn't available
        """
        try:
            # For production, this would integrate with OS Places API or similar
            # For now, return a helpful error with suggestions
            place_mapping = self._get_place_name_mapping()
            
            # Find similar place names
            place_lower = place_name.lower()
            suggestions = []
            
            for mapped_place in place_mapping.keys():
                if place_lower in mapped_place or mapped_place in place_lower:
                    suggestions.append(mapped_place.title())
            
            error_msg = f"Place '{place_name}' not found in current mapping."
            if suggestions:
                error_msg += f" Did you mean: {', '.join(suggestions[:3])}?"
            else:
                error_msg += " Try using a major city or postcode instead."
            
            return {'error': error_msg, 'suggestions': suggestions}
            
        except Exception as e:
            return {'error': f'Place search error: {str(e)}'}
    
    def smart_location_lookup(self, location_query: str) -> Dict:
        """
        Smart location lookup that handles place names, postcodes, and coordinates
        Main entry point for all location-based queries
        """
        try:
            location_clean = location_query.strip()
            
            # Try as postcode first (complete or incomplete)
            if self._looks_like_postcode(location_clean):
                return self.smart_postcode_lookup(location_clean)
            
            # Try as place name
            place_result = self.lookup_place_name(location_clean)
            if 'error' not in place_result:
                return place_result
            
            # If place name lookup failed, return the error with suggestions
            return place_result
            
        except Exception as e:
            logger.error(f"Smart location lookup error for {location_query}: {e}")
            return {'error': str(e)}
    
    def _looks_like_postcode(self, text: str) -> bool:
        """Quick check if text looks like a UK postcode"""
        import re
        text_clean = text.replace(' ', '').upper()
        
        # UK postcode patterns
        complete_pattern = r'^[A-Z]{1,2}[0-9R][0-9A-Z]?[0-9][ABD-HJLNP-UW-Z]{2}$'
        incomplete_pattern = r'^[A-Z]{1,2}[0-9R][0-9A-Z]?$'
        
        return bool(re.match(complete_pattern, text_clean) or re.match(incomplete_pattern, text_clean))
    
    def bulk_postcode_lookup(self, postcodes: List[str]) -> Dict:
        """
        Look up multiple postcodes in a single API call (up to 100 at once)
        More efficient for processing large datasets
        """
        try:
            # Clean and validate postcodes
            clean_postcodes = [pc.replace(' ', '').upper() for pc in postcodes[:100]]
            
            # Prepare bulk request
            payload = {"postcodes": clean_postcodes}
            
            response = self.session.post(
                f"{self.postcodes_base_url}/postcodes",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                results = {}
                
                for item in data['result']:
                    if item['query'] and item['result']:
                        postcode = item['result']['postcode']
                        results[postcode] = {
                            'postcode': postcode,
                            'latitude': item['result']['latitude'],
                            'longitude': item['result']['longitude'],
                            'country': item['result']['country'],
                            'region': item['result']['region'],
                            'admin_district': item['result']['admin_district'],
                            'admin_county': item['result']['admin_county']
                        }
                        # Cache individual results
                        self.postcode_cache[postcode] = results[postcode]
                    else:
                        results[item['query']] = {'error': 'Postcode not found'}
                
                return results
            else:
                return {'error': f'Bulk API error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Bulk postcode lookup error: {e}")
            return {'error': str(e)}
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Dict:
        """
        Find the nearest postcode to given coordinates
        Useful for geographic clustering and analysis
        """
        try:
            response = self.session.get(
                f"{self.postcodes_base_url}/postcodes",
                params={'lat': latitude, 'lon': longitude}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 200 and data['result']:
                    nearest = data['result'][0]  # First result is nearest
                    return {
                        'postcode': nearest['postcode'],
                        'latitude': nearest['latitude'],
                        'longitude': nearest['longitude'],
                        'distance': nearest['distance'],
                        'country': nearest['country'],
                        'region': nearest['region'],
                        'admin_district': nearest['admin_district']
                    }
                else:
                    return {'error': 'No postcodes found near coordinates'}
            else:
                return {'error': f'Reverse geocode API error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Reverse geocode error for {latitude}, {longitude}: {e}")
            return {'error': str(e)}
    
    def calculate_distance(self, postcode1: str, postcode2: str) -> Dict:
        """
        Calculate distance between two postcodes using Haversine formula
        Essential for site clustering and logistics analysis
        Works with both complete and incomplete postcodes
        """
        try:
            # Get coordinates for both postcodes using smart lookup
            geo1 = self.smart_postcode_lookup(postcode1)
            geo2 = self.smart_postcode_lookup(postcode2)
            
            if 'error' in geo1:
                return {'error': f'Postcode 1 error: {geo1["error"]}'}
            if 'error' in geo2:
                return {'error': f'Postcode 2 error: {geo2["error"]}'}
            
            lat1, lon1 = geo1['latitude'], geo1['longitude']
            lat2, lon2 = geo2['latitude'], geo2['longitude']
            
            distance_km = self._haversine_distance(lat1, lon1, lat2, lon2)
            
            return {
                'postcode1': postcode1,
                'postcode2': postcode2,
                'distance_km': round(distance_km, 2),
                'distance_miles': round(distance_km * 0.621371, 2),
                'geo1': geo1,
                'geo2': geo2
            }
            
        except Exception as e:
            logger.error(f"Distance calculation error: {e}")
            return {'error': str(e)}
    
    def find_nearby_postcodes(self, center_postcode: str, radius_km: float = 10) -> Dict:
        """
        Find postcodes within a radius of a center postcode
        Critical for geographic clustering of renewable sites
        Works with both complete and incomplete postcodes
        """
        try:
            center_geo = self.smart_postcode_lookup(center_postcode)
            if 'error' in center_geo:
                return {'error': f'Center postcode error: {center_geo["error"]}'}
            
            lat, lon = center_geo['latitude'], center_geo['longitude']
            
            # Use Postcodes.io nearest postcodes endpoint
            response = self.session.get(
                f"{self.postcodes_base_url}/postcodes",
                params={
                    'lat': lat,
                    'lon': lon,
                    'radius': int(radius_km * 1000),  # Convert to meters
                    'limit': 100
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 200:
                    nearby = []
                    for result in data['result']:
                        if result['postcode'] != center_postcode:  # Exclude center
                            nearby.append({
                                'postcode': result['postcode'],
                                'latitude': result['latitude'],
                                'longitude': result['longitude'],
                                'distance_km': round(result['distance'] / 1000, 2),
                                'country': result['country'],
                                'region': result['region'],
                                'admin_district': result['admin_district']
                            })
                    
                    return {
                        'center_postcode': center_postcode,
                        'center_coordinates': {'lat': lat, 'lon': lon},
                        'radius_km': radius_km,
                        'nearby_postcodes': nearby,
                        'count': len(nearby)
                    }
                else:
                    return {'error': 'No nearby postcodes found'}
            else:
                return {'error': f'Nearby search API error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Nearby postcodes error: {e}")
            return {'error': str(e)}
    
    def get_regional_statistics(self, postcode: str) -> Dict:
        """
        Get comprehensive regional statistics for renewable energy planning
        Combines geographic data with regional analysis
        Works with both complete and incomplete postcodes
        """
        try:
            geo_data = self.smart_postcode_lookup(postcode)
            if 'error' in geo_data:
                return geo_data
            
            # Extract key regional identifiers
            region = geo_data.get('region', '')
            country = geo_data.get('country', '')
            admin_district = geo_data.get('admin_district', '')
            
            # Determine renewable energy potential indicators
            renewable_indicators = self._assess_renewable_potential(geo_data)
            
            return {
                'postcode': postcode,
                'geographic_data': geo_data,
                'renewable_indicators': renewable_indicators,
                'administrative_hierarchy': {
                    'country': country,
                    'region': region,
                    'admin_district': admin_district,
                    'admin_county': geo_data.get('admin_county', ''),
                    'parliamentary_constituency': geo_data.get('parliamentary_constituency', '')
                },
                'grid_reference': {
                    'eastings': geo_data.get('eastings'),
                    'northings': geo_data.get('northings')
                }
            }
            
        except Exception as e:
            logger.error(f"Regional statistics error: {e}")
            return {'error': str(e)}
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        # Earth radius in kilometers
        R = 6371.0
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance = R * c
        
        return distance
    
    def _assess_renewable_potential(self, geo_data: Dict) -> Dict:
        """
        Assess renewable energy potential based on geographic location
        This is a simplified assessment - real implementation would use weather/terrain data
        """
        try:
            lat = geo_data.get('latitude', 0)
            lon = geo_data.get('longitude', 0)
            region = geo_data.get('region', '') or ''
            country = geo_data.get('country', '') or ''
            
            # Handle None values by converting to empty strings
            region = region.lower() if region else ''
            country = country.lower() if country else ''
            
            indicators = {
                'wind_potential': 'medium',
                'solar_potential': 'medium',
                'coastal_proximity': False,
                'elevated_terrain': False,
                'grid_connectivity': 'good'
            }
            
            # Enhanced wind potential for northern regions and coastal areas
            if 'scotland' in country or 'northern' in region.lower():
                indicators['wind_potential'] = 'high'
            
            # Better solar potential for southern regions
            if lat < 52.0:  # South of Birmingham roughly
                indicators['solar_potential'] = 'good'
            elif lat > 55.0:  # North of Newcastle roughly
                indicators['solar_potential'] = 'fair'
            
            # Coastal proximity (simplified - real implementation would check distance to coast)
            coastal_regions = ['south west', 'south east', 'north west', 'north east', 'wales', 'scotland']
            if any(coastal in region.lower() for coastal in coastal_regions):
                indicators['coastal_proximity'] = True
                indicators['wind_potential'] = 'high'
            
            return indicators
            
        except Exception as e:
            logger.warning(f"Renewable potential assessment error: {e}")
            return {
                'wind_potential': 'unknown',
                'solar_potential': 'unknown',
                'coastal_proximity': False,
                'elevated_terrain': False,
                'grid_connectivity': 'unknown'
            }
    
    def _is_complete_postcode(self, postcode: str) -> bool:
        """
        Detect if postcode is complete (e.g., YO17 9AS) or incomplete (e.g., YO17)
        UK postcode format: outcode (2-4 chars) + space + incode (3 chars)
        """
        import re
        
        # Complete postcode pattern: outcode + incode
        complete_pattern = r'^[A-Z]{1,2}[0-9R][0-9A-Z]?[0-9][ABD-HJLNP-UW-Z]{2}$'
        
        # Incomplete postcode (outcode only) pattern
        incomplete_pattern = r'^[A-Z]{1,2}[0-9R][0-9A-Z]?$'
        
        if re.match(complete_pattern, postcode):
            return True
        elif re.match(incomplete_pattern, postcode):
            return False
        else:
            # Invalid format - assume incomplete and let API handle the error
            return False

# Test the system
if __name__ == "__main__":
    print("🌍 UK Geographic Intelligence System Test")
    print("=" * 50)
    
    geo_intel = UKGeoIntelligence()
    
    # Test incomplete postcodes from your FIT data
    test_incomplete_postcodes = ["YO17", "YO25", "HX4", "LD3", "PL7"]
    
    print("📍 Testing Smart Postcode Lookups (Incomplete Postcodes):")
    for postcode in test_incomplete_postcodes:
        result = geo_intel.smart_postcode_lookup(postcode)
        if 'error' not in result:
            postcode_type = result.get('postcode_type', 'complete')
            accuracy = result.get('accuracy', 'exact')
            region = result.get('region', 'Unknown region')
            admin_district = result.get('admin_district', 'Unknown district')
            print(f"✓ {postcode} ({postcode_type}, {accuracy}): {region}, {admin_district} ({result['latitude']:.4f}, {result['longitude']:.4f})")
        else:
            print(f"✗ {postcode}: {result['error']}")
    
    print("\n🔍 Testing Postcode Format Detection:")
    test_formats = ["YO17", "YO17 9AS", "HX4", "HX4 0AB", "INVALID"]
    for pc in test_formats:
        is_complete = geo_intel._is_complete_postcode(pc.replace(' ', '').upper())
        print(f"  {pc}: {'Complete' if is_complete else 'Incomplete/Invalid'}")
    
    print("\n📋 Testing Outcodes with Multiple Postcodes:")
    outcode_result = geo_intel.get_postcodes_in_outcode("YO17", limit=5)
    if 'error' not in outcode_result:
        print(f"Found {outcode_result['count']} postcodes in YO17:")
        for pc in outcode_result['matching_postcodes'][:3]:
            print(f"  - {pc['postcode']} ({pc['distance_from_center_m']}m from center)")
    
    print("\n📊 Testing Regional Statistics for YO17:")
    stats = geo_intel.get_regional_statistics("YO17")
    if 'error' not in stats:
        renewable = stats['renewable_indicators']
        print(f"Wind potential: {renewable['wind_potential']}")
        print(f"Solar potential: {renewable['solar_potential']}")
        print(f"Region: {stats['administrative_hierarchy']['region']}")
    
    print("\n📏 Testing Distance Calculation:")
    distance = geo_intel.calculate_distance("YO17", "YO25")
    if 'error' not in distance:
        print(f"Distance between YO17 and YO25: {distance['distance_km']}km ({distance['distance_miles']} miles)")
    
    print("\n🎯 Testing Nearby Postcodes Search (YO17, 20km radius):")
    nearby = geo_intel.find_nearby_postcodes("YO17", 20)
    if 'error' not in nearby:
        print(f"Found {nearby['count']} postcodes within 20km of YO17")
        for pc in nearby['nearby_postcodes'][:5]:  # Show first 5
            print(f"  - {pc['postcode']}: {pc['distance_km']}km away in {pc['admin_district']}")
    
    print("\n✅ UK Geographic Intelligence System Ready!")