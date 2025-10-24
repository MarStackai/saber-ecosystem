#!/usr/bin/env python3
"""
UK Geographic Search System for FIT Installations
Provides radius-based search capabilities for the entire UK
"""

import json
import math
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import chromadb
from chromadb.utils import embedding_functions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Location:
    """Represents a geographic location"""
    postcode: str
    latitude: float
    longitude: float
    place_name: Optional[str] = None
    region: Optional[str] = None

class UKGeographicSearch:
    """Geographic search system for UK FIT installations"""
    
    # Major UK cities and towns with coordinates
    UK_LOCATIONS = {
        # England - Major Cities
        'london': {'lat': 51.5074, 'lon': -0.1278, 'region': 'Greater London'},
        'birmingham': {'lat': 52.4862, 'lon': -1.8904, 'region': 'West Midlands'},
        'manchester': {'lat': 53.4808, 'lon': -2.2426, 'region': 'North West'},
        'leeds': {'lat': 53.8008, 'lon': -1.5491, 'region': 'Yorkshire'},
        'sheffield': {'lat': 53.3811, 'lon': -1.4701, 'region': 'Yorkshire'},
        'liverpool': {'lat': 53.4084, 'lon': -2.9916, 'region': 'North West'},
        'bristol': {'lat': 51.4545, 'lon': -2.5879, 'region': 'South West'},
        'newcastle': {'lat': 54.9783, 'lon': -1.6178, 'region': 'North East'},
        'nottingham': {'lat': 52.9548, 'lon': -1.1581, 'region': 'East Midlands'},
        'southampton': {'lat': 50.9097, 'lon': -1.4044, 'region': 'South East'},
        'portsmouth': {'lat': 50.8198, 'lon': -1.0880, 'region': 'South East'},
        'leicester': {'lat': 52.6369, 'lon': -1.1398, 'region': 'East Midlands'},
        'coventry': {'lat': 52.4068, 'lon': -1.5197, 'region': 'West Midlands'},
        'oxford': {'lat': 51.7520, 'lon': -1.2577, 'region': 'South East'},
        'cambridge': {'lat': 52.2053, 'lon': 0.1218, 'region': 'East of England'},
        'brighton': {'lat': 50.8225, 'lon': -0.1372, 'region': 'South East'},
        'exeter': {'lat': 50.7184, 'lon': -3.5339, 'region': 'South West'},
        'york': {'lat': 53.9591, 'lon': -1.0815, 'region': 'Yorkshire'},
        'bath': {'lat': 51.3758, 'lon': -2.3599, 'region': 'South West'},
        'chester': {'lat': 53.1930, 'lon': -2.8930, 'region': 'North West'},
        'hull': {'lat': 53.7676, 'lon': -0.3274, 'region': 'Yorkshire'},
        'stoke': {'lat': 53.0027, 'lon': -2.1794, 'region': 'West Midlands'},
        'wolverhampton': {'lat': 52.5868, 'lon': -2.1288, 'region': 'West Midlands'},
        'plymouth': {'lat': 50.3755, 'lon': -4.1427, 'region': 'South West'},
        'derby': {'lat': 52.9225, 'lon': -1.4746, 'region': 'East Midlands'},
        'reading': {'lat': 51.4543, 'lon': -0.9781, 'region': 'South East'},
        'milton keynes': {'lat': 52.0406, 'lon': -0.7594, 'region': 'South East'},
        'gloucester': {'lat': 51.8642, 'lon': -2.2382, 'region': 'South West'},
        'peterborough': {'lat': 52.5695, 'lon': -0.2405, 'region': 'East of England'},
        'northampton': {'lat': 52.2405, 'lon': -0.9027, 'region': 'East Midlands'},
        'norwich': {'lat': 52.6309, 'lon': 1.2974, 'region': 'East of England'},
        'ipswich': {'lat': 52.0567, 'lon': 1.1482, 'region': 'East of England'},
        'luton': {'lat': 51.8787, 'lon': -0.4200, 'region': 'East of England'},
        'swindon': {'lat': 51.5558, 'lon': -1.7797, 'region': 'South West'},
        'warwick': {'lat': 52.2831, 'lon': -1.5846, 'region': 'West Midlands'},
        'guildford': {'lat': 51.2365, 'lon': -0.5703, 'region': 'South East'},
        'preston': {'lat': 53.7586, 'lon': -2.7026, 'region': 'North West'},
        'blackpool': {'lat': 53.8175, 'lon': -3.0357, 'region': 'North West'},
        'middlesbrough': {'lat': 54.5742, 'lon': -1.2350, 'region': 'North East'},
        'sunderland': {'lat': 54.9069, 'lon': -1.3838, 'region': 'North East'},
        'durham': {'lat': 54.7753, 'lon': -1.5849, 'region': 'North East'},
        'carlisle': {'lat': 54.8927, 'lon': -2.9440, 'region': 'North West'},
        'lancaster': {'lat': 54.0485, 'lon': -2.8007, 'region': 'North West'},
        
        # Yorkshire specific (important for FIT data)
        'ryedale': {'lat': 54.0833, 'lon': -0.8000, 'region': 'Yorkshire'},
        'selby': {'lat': 53.7835, 'lon': -1.0635, 'region': 'Yorkshire'},
        'beverley': {'lat': 53.8456, 'lon': -0.4270, 'region': 'Yorkshire'},
        'beverly': {'lat': 53.8456, 'lon': -0.4270, 'region': 'Yorkshire'},  # Alternative spelling
        'scarborough': {'lat': 54.2797, 'lon': -0.4005, 'region': 'Yorkshire'},
        'harrogate': {'lat': 53.9921, 'lon': -1.5418, 'region': 'Yorkshire'},
        'wakefield': {'lat': 53.6833, 'lon': -1.4977, 'region': 'Yorkshire'},
        'barnsley': {'lat': 53.5526, 'lon': -1.4797, 'region': 'Yorkshire'},
        'doncaster': {'lat': 53.5228, 'lon': -1.1285, 'region': 'Yorkshire'},
        'rotherham': {'lat': 53.4326, 'lon': -1.3635, 'region': 'Yorkshire'},
        'bradford': {'lat': 53.7950, 'lon': -1.7594, 'region': 'Yorkshire'},
        'huddersfield': {'lat': 53.6458, 'lon': -1.7850, 'region': 'Yorkshire'},
        'halifax': {'lat': 53.7276, 'lon': -1.8635, 'region': 'Yorkshire'},
        'keighley': {'lat': 53.8679, 'lon': -1.9100, 'region': 'Yorkshire'},
        'skipton': {'lat': 53.9617, 'lon': -2.0170, 'region': 'Yorkshire'},
        'ripon': {'lat': 54.1381, 'lon': -1.5241, 'region': 'Yorkshire'},
        'goole': {'lat': 53.7038, 'lon': -0.8674, 'region': 'Yorkshire'},
        'bridlington': {'lat': 54.0831, 'lon': -0.1919, 'region': 'Yorkshire'},
        
        # Scotland
        'edinburgh': {'lat': 55.9533, 'lon': -3.1883, 'region': 'Scotland'},
        'glasgow': {'lat': 55.8642, 'lon': -4.2518, 'region': 'Scotland'},
        'aberdeen': {'lat': 57.1497, 'lon': -2.0943, 'region': 'Scotland'},
        'dundee': {'lat': 56.4620, 'lon': -2.9707, 'region': 'Scotland'},
        'paisley': {'lat': 55.8456, 'lon': -4.4240, 'region': 'Scotland'},
        'stirling': {'lat': 56.1165, 'lon': -3.9369, 'region': 'Scotland'},
        'inverness': {'lat': 57.4778, 'lon': -4.2247, 'region': 'Scotland'},
        'perth': {'lat': 56.3950, 'lon': -3.4308, 'region': 'Scotland'},
        'ayr': {'lat': 55.4586, 'lon': -4.6292, 'region': 'Scotland'},
        'kilmarnock': {'lat': 55.6117, 'lon': -4.4957, 'region': 'Scotland'},
        'greenock': {'lat': 55.9563, 'lon': -4.7711, 'region': 'Scotland'},
        'dumfries': {'lat': 55.0708, 'lon': -3.6052, 'region': 'Scotland'},
        'falkirk': {'lat': 56.0019, 'lon': -3.7839, 'region': 'Scotland'},
        'dunfermline': {'lat': 56.0719, 'lon': -3.4393, 'region': 'Scotland'},
        
        # Wales
        'cardiff': {'lat': 51.4816, 'lon': -3.1791, 'region': 'Wales'},
        'swansea': {'lat': 51.6214, 'lon': -3.9436, 'region': 'Wales'},
        'newport': {'lat': 51.5842, 'lon': -2.9977, 'region': 'Wales'},
        'wrexham': {'lat': 53.0430, 'lon': -2.9925, 'region': 'Wales'},
        'barry': {'lat': 51.4052, 'lon': -3.2729, 'region': 'Wales'},
        'neath': {'lat': 51.6627, 'lon': -3.8073, 'region': 'Wales'},
        'bridgend': {'lat': 51.5043, 'lon': -3.5769, 'region': 'Wales'},
        'llanelli': {'lat': 51.6821, 'lon': -4.1625, 'region': 'Wales'},
        'merthyr tydfil': {'lat': 51.7487, 'lon': -3.3778, 'region': 'Wales'},
        'rhondda': {'lat': 51.6589, 'lon': -3.4489, 'region': 'Wales'},
        'aberystwyth': {'lat': 52.4135, 'lon': -4.0810, 'region': 'Wales'},
        'bangor': {'lat': 53.2274, 'lon': -4.1293, 'region': 'Wales'},
        'colwyn bay': {'lat': 53.2932, 'lon': -3.7280, 'region': 'Wales'},
        'rhyl': {'lat': 53.3191, 'lon': -3.4916, 'region': 'Wales'},
        'llandudno': {'lat': 53.3239, 'lon': -3.8276, 'region': 'Wales'},
        'gwynedd': {'lat': 52.8276, 'lon': -3.9207, 'region': 'Wales'},
        'powys': {'lat': 52.2928, 'lon': -3.3742, 'region': 'Wales'},
        
        # Northern Ireland
        'belfast': {'lat': 54.5973, 'lon': -5.9301, 'region': 'Northern Ireland'},
        'derry': {'lat': 54.9966, 'lon': -7.3086, 'region': 'Northern Ireland'},
        'londonderry': {'lat': 54.9966, 'lon': -7.3086, 'region': 'Northern Ireland'},
        'lisburn': {'lat': 54.5234, 'lon': -6.0353, 'region': 'Northern Ireland'},
        'newtownabbey': {'lat': 54.6598, 'lon': -5.9089, 'region': 'Northern Ireland'},
        'bangor': {'lat': 54.6534, 'lon': -5.6688, 'region': 'Northern Ireland'},
        'newry': {'lat': 54.1751, 'lon': -6.3402, 'region': 'Northern Ireland'},
        'armagh': {'lat': 54.3503, 'lon': -6.6528, 'region': 'Northern Ireland'},
        'craigavon': {'lat': 54.4471, 'lon': -6.3872, 'region': 'Northern Ireland'},
        
        # Additional regions
        'east riding': {'lat': 53.8456, 'lon': -0.4270, 'region': 'Yorkshire'},
        'east yorkshire': {'lat': 53.8456, 'lon': -0.4270, 'region': 'Yorkshire'},
    }
    
    # UK Postcode district coordinates (sample - would need full dataset)
    POSTCODE_COORDS = {
        # Yorkshire postcodes
        'YO1': {'lat': 53.9591, 'lon': -1.0815},  # York
        'YO17': {'lat': 54.0833, 'lon': -0.8000},  # Ryedale
        'YO25': {'lat': 53.9858, 'lon': -0.5270},  # Driffield
        'YO42': {'lat': 53.9144, 'lon': -0.7544},  # Pocklington
        'HU1': {'lat': 53.7676, 'lon': -0.3274},   # Hull
        'HU15': {'lat': 53.7425, 'lon': -0.5044},  # Brough
        'HU17': {'lat': 53.8456, 'lon': -0.4270},  # Beverley
        'DN6': {'lat': 53.7132, 'lon': -1.0635},   # Selby area
        'DN14': {'lat': 53.7038, 'lon': -0.8674},  # Goole
        'LS1': {'lat': 53.8008, 'lon': -1.5491},   # Leeds
        'BD1': {'lat': 53.7950, 'lon': -1.7594},   # Bradford
        'WF1': {'lat': 53.6833, 'lon': -1.4977},   # Wakefield
        'WF4': {'lat': 53.6529, 'lon': -1.3653},   # Wakefield area
        'S1': {'lat': 53.3811, 'lon': -1.4701},    # Sheffield
        'HD1': {'lat': 53.6458, 'lon': -1.7850},   # Huddersfield
        'HX1': {'lat': 53.7276, 'lon': -1.8635},   # Halifax
        
        # Wales postcodes
        'LL53': {'lat': 52.8503, 'lon': -4.4251},  # Gwynedd
        'LL14': {'lat': 53.0430, 'lon': -2.9925},  # Wrexham area
        'CF1': {'lat': 51.4816, 'lon': -3.1791},   # Cardiff
        'SA1': {'lat': 51.6214, 'lon': -3.9436},   # Swansea
        'LD3': {'lat': 51.9438, 'lon': -3.3912},   # Brecon (Powys)
        'SY4': {'lat': 52.8556, 'lon': -2.7189},   # Shrewsbury area
        
        # Scotland postcodes
        'EH1': {'lat': 55.9533, 'lon': -3.1883},   # Edinburgh
        'G1': {'lat': 55.8642, 'lon': -4.2518},    # Glasgow
        'AB10': {'lat': 57.1497, 'lon': -2.0943},  # Aberdeen
        'DD1': {'lat': 56.4620, 'lon': -2.9707},   # Dundee
        'ML11': {'lat': 55.7804, 'lon': -3.7785},  # Lanarkshire
        'KY1': {'lat': 56.1120, 'lon': -3.1657},   # Kirkcaldy
        'PA1': {'lat': 55.8456, 'lon': -4.4240},   # Paisley
        'IV1': {'lat': 57.4778, 'lon': -4.2247},   # Inverness
        
        # England - other regions
        'ME9': {'lat': 51.3683, 'lon': 0.7339},    # Sittingbourne
        'LA6': {'lat': 54.2043, 'lon': -2.6034},   # Carnforth
        'LA14': {'lat': 54.1144, 'lon': -3.2293},  # Barrow-in-Furness
        'WR2': {'lat': 52.1906, 'lon': -2.2216},   # Worcester
        'PL7': {'lat': 50.3905, 'lon': -4.0544},   # Plymouth area
        'B1': {'lat': 52.4862, 'lon': -1.8904},    # Birmingham
        'M1': {'lat': 53.4808, 'lon': -2.2426},    # Manchester
        'L1': {'lat': 53.4084, 'lon': -2.9916},    # Liverpool
        'NE1': {'lat': 54.9783, 'lon': -1.6178},   # Newcastle
        'BS1': {'lat': 51.4545, 'lon': -2.5879},   # Bristol
        'OX1': {'lat': 51.7520, 'lon': -1.2577},   # Oxford
        'CB1': {'lat': 52.2053, 'lon': 0.1218},    # Cambridge
        'SO14': {'lat': 50.9097, 'lon': -1.4044},  # Southampton
        'PO1': {'lat': 50.8198, 'lon': -1.0880},   # Portsmouth
        'BN1': {'lat': 50.8225, 'lon': -0.1372},   # Brighton
        'GU1': {'lat': 51.2365, 'lon': -0.5703},   # Guildford
        'RG1': {'lat': 51.4543, 'lon': -0.9781},   # Reading
        'MK1': {'lat': 52.0406, 'lon': -0.7594},   # Milton Keynes
        'NN1': {'lat': 52.2405, 'lon': -0.9027},   # Northampton
        'LE1': {'lat': 52.6369, 'lon': -1.1398},   # Leicester
        'NG1': {'lat': 52.9548, 'lon': -1.1581},   # Nottingham
        'DE1': {'lat': 52.9225, 'lon': -1.4746},   # Derby
        'CV1': {'lat': 52.4068, 'lon': -1.5197},   # Coventry
        'WV1': {'lat': 52.5868, 'lon': -2.1288},   # Wolverhampton
        'ST1': {'lat': 53.0027, 'lon': -2.1794},   # Stoke
        'EX1': {'lat': 50.7184, 'lon': -3.5339},   # Exeter
        'GL1': {'lat': 51.8642, 'lon': -2.2382},   # Gloucester
        'SN1': {'lat': 51.5558, 'lon': -1.7797},   # Swindon
        'BA1': {'lat': 51.3758, 'lon': -2.3599},   # Bath
        'CH1': {'lat': 53.1930, 'lon': -2.8930},   # Chester
        'PR1': {'lat': 53.7586, 'lon': -2.7026},   # Preston
        'FY1': {'lat': 53.8175, 'lon': -3.0357},   # Blackpool
        'CA1': {'lat': 54.8927, 'lon': -2.9440},   # Carlisle
        'LA1': {'lat': 54.0485, 'lon': -2.8007},   # Lancaster
        'TS1': {'lat': 54.5742, 'lon': -1.2350},   # Middlesbrough
        'SR1': {'lat': 54.9069, 'lon': -1.3838},   # Sunderland
        'DH1': {'lat': 54.7753, 'lon': -1.5849},   # Durham
        'NR1': {'lat': 52.6309, 'lon': 1.2974},    # Norwich
        'IP1': {'lat': 52.0567, 'lon': 1.1482},    # Ipswich
        'PE1': {'lat': 52.5695, 'lon': -0.2405},   # Peterborough
        'LU1': {'lat': 51.8787, 'lon': -0.4200},   # Luton
    }
    
    def __init__(self, chroma_client=None, collection=None):
        """Initialize the geographic search system"""
        if chroma_client and collection:
            # Use existing client and collection
            self.client = chroma_client
            self.collection = collection
        else:
            # Create new client
            self.client = chromadb.PersistentClient(path='./chroma_db')
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            self.collection = self.client.get_collection(
                name="fit_licenses_nondomestic",
                embedding_function=self.embedding_function
            )
        logger.info(f"Initialized geographic search with {self.collection.count()} installations")
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points on Earth
        Returns distance in miles
        """
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in miles
        r = 3959
        return r * c
    
    def get_location_coordinates(self, location_name: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for a UK location"""
        location_lower = location_name.lower().strip()
        
        # Check known locations
        if location_lower in self.UK_LOCATIONS:
            loc = self.UK_LOCATIONS[location_lower]
            return (loc['lat'], loc['lon'])
        
        # Check if it's a postcode
        postcode_upper = location_name.upper().strip()
        if postcode_upper in self.POSTCODE_COORDS:
            loc = self.POSTCODE_COORDS[postcode_upper]
            return (loc['lat'], loc['lon'])
        
        # Try partial postcode match (e.g., "YO" for York)
        for pc, coords in self.POSTCODE_COORDS.items():
            if pc.startswith(postcode_upper):
                return (coords['lat'], coords['lon'])
        
        # Try fuzzy match on location names
        for loc_name, loc_data in self.UK_LOCATIONS.items():
            if location_lower in loc_name or loc_name in location_lower:
                return (loc_data['lat'], loc_data['lon'])
        
        # Don't warn for every location
        return None
    
    def get_postcode_coordinates(self, postcode: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for a UK postcode"""
        if not postcode or postcode == 'nan' or postcode == '':
            return None
            
        postcode_upper = postcode.upper().strip()
        
        # Direct match
        if postcode_upper in self.POSTCODE_COORDS:
            loc = self.POSTCODE_COORDS[postcode_upper]
            return (loc['lat'], loc['lon'])
        
        # Try first part of postcode (e.g., "YO17 8BZ" -> "YO17")
        parts = postcode_upper.split()
        if parts and parts[0] in self.POSTCODE_COORDS:
            loc = self.POSTCODE_COORDS[parts[0]]
            return (loc['lat'], loc['lon'])
        
        # Try even shorter match (e.g., "YO17" -> "YO1")
        for pc, coords in self.POSTCODE_COORDS.items():
            if postcode_upper.startswith(pc[:2]):
                return (coords['lat'], coords['lon'])
        
        return None
    
    def search_by_radius(
        self, 
        center_location: str, 
        radius_miles: float,
        technology: Optional[str] = None,
        min_capacity_kw: Optional[float] = None,
        max_capacity_kw: Optional[float] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Search for FIT installations within a radius of a location
        
        Args:
            center_location: Name of place or postcode
            radius_miles: Search radius in miles
            technology: Filter by technology (Wind, Solar, etc.)
            min_capacity_kw: Minimum capacity in kW
            max_capacity_kw: Maximum capacity in kW
            limit: Maximum number of results
        
        Returns:
            List of installations with distance from center
        """
        # Get center coordinates
        center_coords = self.get_location_coordinates(center_location)
        if not center_coords:
            logger.error(f"Could not find coordinates for {center_location}")
            return []
        
        center_lat, center_lon = center_coords
        logger.info(f"Searching within {radius_miles} miles of {center_location} ({center_lat:.4f}, {center_lon:.4f})")
        
        # Get all records (we'll filter by distance)
        # In production, you'd want to pre-filter by a bounding box
        where_clause = {}
        if technology:
            where_clause['technology'] = technology
        
        # Get records from ChromaDB
        results = self.collection.get(
            where=where_clause if where_clause else None,
            limit=10000  # Get more initially, we'll filter by distance
        )
        
        filtered_results = []
        
        for i, metadata in enumerate(results['metadatas']):
            # Get installation coordinates
            postcode = metadata.get('postcode', '')
            coords = self.get_postcode_coordinates(postcode)
            
            if not coords:
                # Try to get from local authority
                location = metadata.get('local_authority', '')
                coords = self.get_location_coordinates(location)
            
            if not coords:
                continue
            
            inst_lat, inst_lon = coords
            
            # Calculate distance
            distance = self.haversine_distance(center_lat, center_lon, inst_lat, inst_lon)
            
            # Check if within radius
            if distance <= radius_miles:
                # Check capacity filters
                capacity = metadata.get('capacity_kw', 0)
                if min_capacity_kw and capacity < min_capacity_kw:
                    continue
                if max_capacity_kw and capacity > max_capacity_kw:
                    continue
                
                # Add distance to metadata
                result = {
                    'id': results['ids'][i],
                    'metadata': metadata,
                    'distance_miles': round(distance, 1),
                    'latitude': inst_lat,
                    'longitude': inst_lon
                }
                filtered_results.append(result)
        
        # Sort by distance
        filtered_results.sort(key=lambda x: x['distance_miles'])
        
        # Limit results
        filtered_results = filtered_results[:limit]
        
        logger.info(f"Found {len(filtered_results)} installations within {radius_miles} miles of {center_location}")
        
        return filtered_results
    
    def search_by_postcode_area(
        self,
        postcode_prefix: str,
        technology: Optional[str] = None,
        min_capacity_kw: Optional[float] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Search for installations in a postcode area"""
        where_clause = {}
        
        # Add technology filter
        if technology:
            where_clause['technology'] = technology
        
        # Query ChromaDB
        results = self.collection.get(
            where=where_clause if where_clause else None,
            limit=10000
        )
        
        filtered_results = []
        for i, metadata in enumerate(results['metadatas']):
            postcode = metadata.get('postcode', '')
            if postcode.upper().startswith(postcode_prefix.upper()):
                # Check capacity filter
                capacity = metadata.get('capacity_kw', 0)
                if min_capacity_kw and capacity < min_capacity_kw:
                    continue
                    
                filtered_results.append({
                    'id': results['ids'][i],
                    'metadata': metadata
                })
        
        logger.info(f"Found {len(filtered_results)} installations in {postcode_prefix} area")
        return filtered_results[:limit]


def test_geographic_search():
    """Test the geographic search functionality"""
    searcher = UKGeographicSearch()
    
    print("\n=== Testing UK Geographic Search ===\n")
    
    # Test 1: Search around York
    print("1. Wind farms within 30 miles of York:")
    results = searcher.search_by_radius(
        center_location="York",
        radius_miles=30,
        technology="Wind",
        limit=5
    )
    for r in results:
        meta = r['metadata']
        print(f"   - FIT {meta['fit_id']}: {meta.get('capacity_kw', 0)}kW, "
              f"{r['distance_miles']} miles away, {meta.get('postcode', 'Unknown')}")
    
    # Test 2: Large solar near Manchester
    print("\n2. Solar installations over 1MW within 50 miles of Manchester:")
    results = searcher.search_by_radius(
        center_location="Manchester",
        radius_miles=50,
        technology="Photovoltaic",
        min_capacity_kw=1000,
        limit=5
    )
    for r in results:
        meta = r['metadata']
        print(f"   - FIT {meta['fit_id']}: {meta.get('capacity_kw', 0)/1000:.1f}MW, "
              f"{r['distance_miles']} miles away, {meta.get('local_authority', 'Unknown')}")
    
    # Test 3: Search in Scotland
    print("\n3. All renewables within 40 miles of Edinburgh:")
    results = searcher.search_by_radius(
        center_location="Edinburgh",
        radius_miles=40,
        limit=5
    )
    for r in results:
        meta = r['metadata']
        print(f"   - {meta.get('technology', 'Unknown')}: {meta.get('capacity_kw', 0)}kW, "
              f"{r['distance_miles']} miles away")
    
    # Test 4: Postcode area search
    print("\n4. Installations in YO (York) postcode area:")
    results = searcher.search_by_postcode_area(
        postcode_prefix="YO",
        technology="Wind",
        limit=5
    )
    for r in results[:5]:
        meta = r['metadata']
        print(f"   - FIT {meta['fit_id']}: {meta.get('capacity_kw', 0)}kW, {meta.get('postcode', 'Unknown')}")


if __name__ == "__main__":
    test_geographic_search()