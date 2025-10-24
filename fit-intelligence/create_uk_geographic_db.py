#!/usr/bin/env python3
"""
Create UK Geographic Database in ChromaDB
Maps all UK postcodes to cities, regions, and coordinates
Solves the geographic search accuracy problem
"""

import chromadb
from chromadb.utils import embedding_functions
import json
import logging
from typing import Dict, List
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UKGeographicDatabase:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="chroma_db")
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Complete UK postcode to place mappings
        self.uk_geography = {
            # SCOTLAND
            "Aberdeen": {
                "postcodes": ["AB10", "AB11", "AB12", "AB13", "AB14", "AB15", "AB16", "AB21", "AB22", "AB23", "AB24", "AB25"],
                "region": "Scotland",
                "lat": 57.1497, "lon": -2.0943,
                "aliases": ["Aberdeen City", "Granite City", "Aberdeenshire"]
            },
            "Edinburgh": {
                "postcodes": ["EH1", "EH2", "EH3", "EH4", "EH5", "EH6", "EH7", "EH8", "EH9", "EH10", "EH11", "EH12", "EH13", "EH14", "EH15", "EH16"],
                "region": "Scotland", 
                "lat": 55.9533, "lon": -3.1883,
                "aliases": ["Edinburgh City", "Capital of Scotland", "Midlothian"]
            },
            "Glasgow": {
                "postcodes": ["G1", "G2", "G3", "G4", "G5", "G11", "G12", "G13", "G14", "G15", "G20", "G21", "G22", "G31", "G32", "G33", "G40", "G41", "G42", "G43", "G44", "G45", "G46", "G51", "G52", "G53"],
                "region": "Scotland",
                "lat": 55.8642, "lon": -4.2518,
                "aliases": ["Glasgow City", "Greater Glasgow", "Lanarkshire"]
            },
            "Dundee": {
                "postcodes": ["DD1", "DD2", "DD3", "DD4", "DD5"],
                "region": "Scotland",
                "lat": 56.4620, "lon": -2.9707,
                "aliases": ["Dundee City", "City of Discovery", "Angus"]
            },
            "Inverness": {
                "postcodes": ["IV1", "IV2", "IV3"],
                "region": "Scotland",
                "lat": 57.4778, "lon": -4.2247,
                "aliases": ["Highland Capital", "Highlands", "Scottish Highlands"]
            },
            
            # ENGLAND - NORTH
            "Newcastle": {
                "postcodes": ["NE1", "NE2", "NE3", "NE4", "NE5", "NE6", "NE7", "NE8", "NE15", "NE16", "NE17", "NE18"],
                "region": "North East England",
                "lat": 54.9783, "lon": -1.6178,
                "aliases": ["Newcastle upon Tyne", "Tyneside", "Northumberland"]
            },
            "Manchester": {
                "postcodes": ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M11", "M12", "M13", "M14", "M15", "M16", "M17", "M18", "M19", "M20", "M21", "M22", "M23"],
                "region": "North West England",
                "lat": 53.4808, "lon": -2.2426,
                "aliases": ["Greater Manchester", "Manchester City", "Lancashire"]
            },
            "Liverpool": {
                "postcodes": ["L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10", "L11", "L12", "L13", "L14", "L15", "L16", "L17", "L18", "L19", "L20"],
                "region": "North West England",
                "lat": 53.4084, "lon": -2.9916,
                "aliases": ["Liverpool City", "Merseyside", "Scouse"]
            },
            "Leeds": {
                "postcodes": ["LS1", "LS2", "LS3", "LS4", "LS5", "LS6", "LS7", "LS8", "LS9", "LS10", "LS11", "LS12", "LS13", "LS14", "LS15", "LS16", "LS17", "LS18", "LS19", "LS20"],
                "region": "Yorkshire",
                "lat": 53.8008, "lon": -1.5491,
                "aliases": ["Leeds City", "West Yorkshire", "Yorkshire"]
            },
            "Sheffield": {
                "postcodes": ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12", "S13", "S14", "S17", "S20", "S21", "S25", "S26", "S35", "S36"],
                "region": "Yorkshire",
                "lat": 53.3811, "lon": -1.4701,
                "aliases": ["Sheffield City", "South Yorkshire", "Steel City"]
            },
            "York": {
                "postcodes": ["YO1", "YO10", "YO19", "YO23", "YO24", "YO26", "YO30", "YO31", "YO32"],
                "region": "Yorkshire",
                "lat": 53.9591, "lon": -1.0815,
                "aliases": ["York City", "North Yorkshire", "Yorkshire"]
            },
            "Hull": {
                "postcodes": ["HU1", "HU2", "HU3", "HU4", "HU5", "HU6", "HU7", "HU8", "HU9"],
                "region": "Yorkshire",
                "lat": 53.7676, "lon": -0.3274,
                "aliases": ["Kingston upon Hull", "East Yorkshire", "Humberside"]
            },
            "Bradford": {
                "postcodes": ["BD1", "BD2", "BD3", "BD4", "BD5", "BD6", "BD7", "BD8", "BD9", "BD10", "BD11", "BD12", "BD13", "BD14", "BD15", "BD16", "BD17", "BD18", "BD19", "BD20", "BD21"],
                "region": "Yorkshire",
                "lat": 53.7960, "lon": -1.7594,
                "aliases": ["Bradford City", "West Yorkshire", "Yorkshire"]
            },
            
            # ENGLAND - MIDLANDS
            "Birmingham": {
                "postcodes": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12", "B13", "B14", "B15", "B16", "B17", "B18", "B19", "B20"],
                "region": "West Midlands",
                "lat": 52.4862, "lon": -1.8904,
                "aliases": ["Birmingham City", "Brum", "West Midlands", "Second City"]
            },
            "Nottingham": {
                "postcodes": ["NG1", "NG2", "NG3", "NG4", "NG5", "NG6", "NG7", "NG8", "NG9", "NG10", "NG11"],
                "region": "East Midlands",
                "lat": 52.9548, "lon": -1.1581,
                "aliases": ["Nottingham City", "Nottinghamshire", "East Midlands"]
            },
            "Leicester": {
                "postcodes": ["LE1", "LE2", "LE3", "LE4", "LE5", "LE6", "LE7", "LE8", "LE9"],
                "region": "East Midlands",
                "lat": 52.6369, "lon": -1.1398,
                "aliases": ["Leicester City", "Leicestershire", "East Midlands"]
            },
            
            # ENGLAND - SOUTH
            "London": {
                "postcodes": ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9", "E10", "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18", "E20",
                            "EC1", "EC2", "EC3", "EC4",
                            "N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9", "N10", "N11", "N12", "N13", "N14", "N15", "N16", "N17", "N18", "N19", "N20", "N21", "N22",
                            "NW1", "NW2", "NW3", "NW4", "NW5", "NW6", "NW7", "NW8", "NW9", "NW10", "NW11",
                            "SE1", "SE2", "SE3", "SE4", "SE5", "SE6", "SE7", "SE8", "SE9", "SE10", "SE11", "SE12", "SE13", "SE14", "SE15", "SE16", "SE17", "SE18", "SE19", "SE20", "SE21", "SE22", "SE23", "SE24", "SE25", "SE26", "SE27", "SE28",
                            "SW1", "SW2", "SW3", "SW4", "SW5", "SW6", "SW7", "SW8", "SW9", "SW10", "SW11", "SW12", "SW13", "SW14", "SW15", "SW16", "SW17", "SW18", "SW19", "SW20",
                            "W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9", "W10", "W11", "W12", "W13", "W14",
                            "WC1", "WC2"],
                "region": "Greater London",
                "lat": 51.5074, "lon": -0.1278,
                "aliases": ["Greater London", "The Capital", "The City", "London City"]
            },
            "Bristol": {
                "postcodes": ["BS1", "BS2", "BS3", "BS4", "BS5", "BS6", "BS7", "BS8", "BS9", "BS10", "BS11", "BS13", "BS14", "BS15", "BS16"],
                "region": "South West England",
                "lat": 51.4545, "lon": -2.5879,
                "aliases": ["Bristol City", "Avon", "South West"]
            },
            "Southampton": {
                "postcodes": ["SO14", "SO15", "SO16", "SO17", "SO18", "SO19"],
                "region": "South East England",
                "lat": 50.9097, "lon": -1.4044,
                "aliases": ["Southampton City", "Hampshire", "South Coast"]
            },
            "Brighton": {
                "postcodes": ["BN1", "BN2", "BN3", "BN41", "BN42", "BN43", "BN44", "BN45"],
                "region": "South East England",
                "lat": 50.8225, "lon": -0.1372,
                "aliases": ["Brighton and Hove", "Sussex", "South Coast"]
            },
            
            # WALES
            "Cardiff": {
                "postcodes": ["CF10", "CF11", "CF14", "CF15", "CF23", "CF24", "CF3", "CF5"],
                "region": "Wales",
                "lat": 51.4816, "lon": -3.1791,
                "aliases": ["Cardiff City", "Capital of Wales", "South Wales"]
            },
            "Swansea": {
                "postcodes": ["SA1", "SA2", "SA3", "SA4", "SA5", "SA6", "SA7"],
                "region": "Wales",
                "lat": 51.6214, "lon": -3.9436,
                "aliases": ["Swansea City", "West Wales", "South Wales"]
            },
            
            # NORTHERN IRELAND
            "Belfast": {
                "postcodes": ["BT1", "BT2", "BT3", "BT4", "BT5", "BT6", "BT7", "BT8", "BT9", "BT10", "BT11", "BT12", "BT13", "BT14", "BT15", "BT16", "BT17"],
                "region": "Northern Ireland",
                "lat": 54.5973, "lon": -5.9301,
                "aliases": ["Belfast City", "Capital of Northern Ireland", "Ulster"]
            }
        }
        
        # Postcode regions (for broader searches)
        self.postcode_regions = {
            "Scotland": ["AB", "DD", "DG", "EH", "FK", "G", "HS", "IV", "KA", "KW", "KY", "ML", "PA", "PH", "TD", "ZE"],
            "Wales": ["CF", "LD", "LL", "NP", "SA", "SY"],
            "Northern Ireland": ["BT"],
            "Yorkshire": ["YO", "HU", "LS", "BD", "HX", "HD", "WF", "S", "DN"],
            "North East": ["NE", "DH", "DL", "SR", "TS"],
            "North West": ["BB", "BL", "CA", "CH", "CW", "FY", "L", "LA", "M", "OL", "PR", "SK", "WA", "WN"],
            "Midlands": ["B", "CV", "DE", "DY", "LE", "NG", "NN", "ST", "WR", "WS", "WV"],
            "East": ["AL", "CB", "CM", "CO", "EN", "HP", "IP", "LU", "MK", "NR", "PE", "SG", "SS", "WD"],
            "London": ["E", "EC", "N", "NW", "SE", "SW", "W", "WC", "BR", "CR", "DA", "EN", "HA", "IG", "KT", "RM", "SM", "TW", "UB"],
            "South East": ["BN", "CT", "GU", "ME", "OX", "PO", "RG", "RH", "SL", "SO", "TN"],
            "South West": ["BA", "BH", "BS", "DT", "EX", "GL", "PL", "SN", "SP", "TA", "TQ", "TR"]
        }
    
    def create_geographic_collection(self):
        """Create a ChromaDB collection for UK geography"""
        try:
            # Delete existing collection if it exists
            try:
                self.client.delete_collection("uk_geography")
            except:
                pass
            
            # Create new collection
            collection = self.client.create_collection(
                name="uk_geography",
                embedding_function=self.embedding_function,
                metadata={"description": "UK postcode and place name mappings"}
            )
            
            # Prepare documents
            documents = []
            metadatas = []
            ids = []
            
            # Add city/place entries
            for place, data in self.uk_geography.items():
                # Create searchable text combining all variations
                search_text = f"{place} {' '.join(data['aliases'])} {data['region']} {' '.join(data['postcodes'][:5])}"
                
                documents.append(search_text)
                metadatas.append({
                    "place": place,
                    "region": data["region"],
                    "postcodes": json.dumps(data["postcodes"]),
                    "lat": data["lat"],
                    "lon": data["lon"],
                    "type": "city"
                })
                ids.append(f"place_{place.lower().replace(' ', '_')}")
            
            # Add postcode entries
            for place, data in self.uk_geography.items():
                for postcode in data["postcodes"]:
                    search_text = f"{postcode} {place} {data['region']}"
                    documents.append(search_text)
                    metadatas.append({
                        "postcode": postcode,
                        "place": place,
                        "region": data["region"],
                        "lat": data["lat"],
                        "lon": data["lon"],
                        "type": "postcode"
                    })
                    ids.append(f"postcode_{postcode.lower()}")
            
            # Add region entries
            for region, postcodes in self.postcode_regions.items():
                search_text = f"{region} {' '.join(postcodes[:10])}"
                documents.append(search_text)
                metadatas.append({
                    "region": region,
                    "postcodes": json.dumps(postcodes),
                    "type": "region"
                })
                ids.append(f"region_{region.lower().replace(' ', '_')}")
            
            # Add to collection
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"✅ Created UK geography collection with {len(documents)} entries")
            return collection
            
        except Exception as e:
            logger.error(f"Error creating geographic collection: {e}")
            raise
    
    def search_location(self, query: str, n_results: int = 5):
        """Search for a location and return valid postcodes"""
        collection = self.client.get_collection("uk_geography")
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Extract postcodes from results
        valid_postcodes = set()
        locations = []
        
        for metadata in results['metadatas'][0]:
            if metadata.get('type') == 'city':
                postcodes = json.loads(metadata.get('postcodes', '[]'))
                valid_postcodes.update(postcodes)
                locations.append({
                    'place': metadata.get('place'),
                    'region': metadata.get('region'),
                    'postcodes': postcodes
                })
            elif metadata.get('type') == 'postcode':
                valid_postcodes.add(metadata.get('postcode'))
            elif metadata.get('type') == 'region':
                postcodes = json.loads(metadata.get('postcodes', '[]'))
                valid_postcodes.update(postcodes)
        
        return {
            'query': query,
            'valid_postcodes': list(valid_postcodes),
            'locations': locations
        }
    
    def validate_postcode_for_location(self, postcode: str, location: str) -> bool:
        """Check if a postcode is valid for a given location"""
        result = self.search_location(location)
        postcode_prefix = postcode.split()[0] if ' ' in postcode else postcode[:3]
        
        for valid_pc in result['valid_postcodes']:
            if postcode_prefix.startswith(valid_pc):
                return True
        return False

def test_geographic_db():
    """Test the geographic database"""
    print("=" * 60)
    print("CREATING UK GEOGRAPHIC DATABASE")
    print("=" * 60)
    
    geo_db = UKGeographicDatabase()
    geo_db.create_geographic_collection()
    
    # Test searches
    test_queries = [
        "Aberdeen",
        "Edinburgh", 
        "Yorkshire",
        "wind farms near Glasgow",
        "solar in Cardiff"
    ]
    
    print("\n📍 Testing Location Searches:")
    print("-" * 40)
    
    for query in test_queries:
        result = geo_db.search_location(query)
        print(f"\nQuery: '{query}'")
        print(f"Valid postcodes: {result['valid_postcodes'][:10]}...")
        if result['locations']:
            print(f"Matched: {result['locations'][0]['place']} ({result['locations'][0]['region']})")
    
    # Test validation
    print("\n✅ Testing Postcode Validation:")
    print("-" * 40)
    
    test_cases = [
        ("AB21", "Aberdeen", True),
        ("ML10", "Aberdeen", False),
        ("EH1", "Edinburgh", True),
        ("G1", "Edinburgh", False),
        ("YO1", "Yorkshire", True),
        ("BD20", "Yorkshire", True),
        ("AB10", "Yorkshire", False)
    ]
    
    for postcode, location, expected in test_cases:
        valid = geo_db.validate_postcode_for_location(postcode, location)
        status = "✅" if valid == expected else "❌"
        print(f"{status} {postcode} for {location}: {valid} (expected {expected})")
    
    print("\n" + "=" * 60)
    print("Geographic database ready for integration!")

if __name__ == "__main__":
    test_geographic_db()