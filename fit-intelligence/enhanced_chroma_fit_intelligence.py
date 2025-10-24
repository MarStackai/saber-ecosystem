#!/usr/bin/env python3
"""
Enhanced Chroma FIT Intelligence System
Integrates FIT License data with vector embeddings for comprehensive analysis
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import pandas as pd
import json
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
import os
import time
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_postcode_area(postcode):
    """Extract postcode area (letters only) from postcode"""
    m = re.match(r'([A-Z]{1,2})', str(postcode or '').upper().strip())
    return m.group(1) if m else None

def extract_postcode_outward(postcode):
    """Extract outward code from postcode"""
    m = re.match(r'([A-Z]{1,2}\d{1,2})', str(postcode or '').upper().strip())
    return m.group(1) if m else None

def normalize_technology(tech):
    """Normalize technology names"""
    t = str(tech or '').lower()
    if t in ('pv', 'photovoltaic', 'solar pv'):
        return 'solar'
    if t in ('ad', 'anaerobic digestion'):
        return 'anaerobic digestion'
    return t

class EnhancedChromaFITIntelligence:
    """
    Enhanced vector-based intelligence system that combines:
    1. Existing commercial FIT site data
    2. New FIT license data with detailed tariff information
    3. Intelligent embeddings for comprehensive analysis
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize enhanced Chroma client with FIT license integration"""
        self.persist_directory = persist_directory
        
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                is_persistent=True
            )
        )
        
        # Initialize embedding function
        logger.info("Loading sentence transformer model...")
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        logger.info("Embedding model loaded")
        
        # Collections
        self.commercial_collection_name = "commercial_fit_sites"
        self.license_collection_name = "fit_licenses"
        self.unified_collection_name = "unified_fit_intelligence"
        
        # Data storage
        self.fit_licenses = None
        self.commercial_data = None
        self.collections = {}
        
        # Load data and initialize collections
        self._load_all_data()
        self._initialize_collections()
    
    def _load_all_data(self):
        """Load both commercial and license data"""
        try:
            # Load existing commercial data
            logger.info("Loading existing commercial FIT data...")
            with open('data/all_commercial_fit.json', 'r') as f:
                self.commercial_data = json.load(f)
            logger.info(f"Loaded {len(self.commercial_data.get('sites', []))} commercial sites")
            
            # Process FIT license data
            logger.info("Processing FIT license data...")
            self.fit_licenses = self._process_fit_licenses()
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.commercial_data = {'sites': []}
            self.fit_licenses = []
    
    def _process_fit_licenses(self, max_records: int = 50000) -> List[Dict]:
        """Process FIT license data efficiently"""
        try:
            all_licenses = []
            
            # Process each part with limit to manage memory
            for part_num in [1, 2, 3]:
                if len(all_licenses) >= max_records:
                    break
                    
                filename = f'data/Feed-in Tariff Installation Report Part {part_num}.xlsx'
                logger.info(f"Processing {filename}...")
                
                try:
                    # Read header detection
                    temp_df = pd.read_excel(filename, sheet_name=0, header=None, nrows=10)
                    header_row = None
                    for idx in range(len(temp_df)):
                        row_text = ' '.join([str(cell) for cell in temp_df.iloc[idx] if pd.notna(cell)])
                        if 'FIT ID' in row_text:
                            header_row = idx
                            break
                    
                    if header_row is None:
                        logger.warning(f"No header found in {filename}")
                        continue
                    
                    # Process in chunks to manage memory
                    chunk_size = 10000
                    remaining = max_records - len(all_licenses)
                    
                    for chunk in pd.read_excel(filename, sheet_name=0, header=header_row, 
                                             chunksize=chunk_size):
                        if len(all_licenses) >= max_records:
                            break
                            
                        # Clean column names
                        chunk.columns = chunk.columns.str.strip()
                        
                        # Process chunk
                        for _, row in chunk.iterrows():
                            if len(all_licenses) >= max_records:
                                break
                                
                            license_info = self._extract_license_info(row)
                            if license_info:
                                all_licenses.append(license_info)
                        
                        logger.info(f"Processed {len(all_licenses)} licenses so far...")
                        
                        if len(all_licenses) >= remaining:
                            break
                    
                except Exception as e:
                    logger.error(f"Error processing {filename}: {e}")
                    continue
            
            logger.info(f"Successfully processed {len(all_licenses)} FIT licenses")
            return all_licenses
            
        except Exception as e:
            logger.error(f"Error in license processing: {e}")
            return []
    
    def _extract_license_info(self, row: pd.Series) -> Optional[Dict]:
        """Extract and enhance license information"""
        try:
            # Basic validation
            fit_id = row.get('FIT ID')
            if pd.isna(fit_id):
                return None
            
            # Extract core fields
            license_info = {
                'fit_id': str(int(fit_id)),
                'technology': str(row.get('Technology', '')).strip(),
                'postcode': str(row.get('PostCode ', '')).strip().upper(),
                'tariff_code': str(row.get('TariffCode', '')).strip(),
                'export_status': str(row.get('Export status', '')).strip(),
                'installation_type': str(row.get('Installation Type', '')).strip(),
                'country': str(row.get('Installation Country', '')).strip(),
                'region': str(row.get('Government Office Region', '')).strip(),
                'local_authority': str(row.get('Local Authority', '')).strip(),
            }
            
            # Capacity handling
            declared_capacity = row.get('Declared net capacity')
            installed_capacity = row.get('Installed capacity')
            
            if pd.notna(declared_capacity):
                license_info['capacity_kw'] = float(declared_capacity)
            elif pd.notna(installed_capacity):
                license_info['capacity_kw'] = float(installed_capacity)
            else:
                license_info['capacity_kw'] = 0.0
            
            license_info['capacity_mw'] = license_info['capacity_kw'] / 1000
            
            # Date handling
            commission_date = row.get('Commissioning date')
            if pd.notna(commission_date):
                try:
                    if isinstance(commission_date, str):
                        comm_dt = pd.to_datetime(commission_date)
                    else:
                        comm_dt = pd.to_datetime(commission_date)
                    
                    license_info['commission_date'] = comm_dt.isoformat()
                    
                    # Calculate derived fields
                    current_date = datetime.now()
                    age = (current_date - comm_dt).days / 365.25
                    remaining_fit = max(0, 20 - age)
                    
                    license_info['age_years'] = round(age, 1)
                    license_info['remaining_fit_years'] = round(remaining_fit, 1)
                    license_info['fit_expiry_date'] = (comm_dt + timedelta(days=20*365)).isoformat()
                    
                    # Determine repowering window
                    if remaining_fit <= 0:
                        license_info['repowering_window'] = 'EXPIRED'
                    elif remaining_fit <= 2:
                        license_info['repowering_window'] = 'IMMEDIATE'
                    elif remaining_fit <= 5:
                        license_info['repowering_window'] = 'URGENT'
                    else:
                        license_info['repowering_window'] = 'OPTIMAL'
                        
                except:
                    license_info['commission_date'] = str(commission_date)
            
            # Categorization
            capacity_kw = license_info['capacity_kw']
            if capacity_kw <= 4:
                license_info['size_category'] = 'Micro (<4kW)'
                license_info['grid_category'] = 'Single Phase'
                license_info['commercial_status'] = 'Residential'
            elif capacity_kw <= 50:
                license_info['size_category'] = 'Small (4-50kW)'
                license_info['grid_category'] = 'Single/Three Phase'
                license_info['commercial_status'] = 'Small Commercial'
            elif capacity_kw <= 250:
                license_info['size_category'] = 'Medium (50-250kW)'
                license_info['grid_category'] = 'Three Phase'
                license_info['commercial_status'] = 'Commercial'
            elif capacity_kw <= 1000:
                license_info['size_category'] = 'Large (250kW-1MW)'
                license_info['grid_category'] = 'Distribution'
                license_info['commercial_status'] = 'Large Commercial'
            else:
                license_info['size_category'] = 'Utility (>1MW)'
                license_info['grid_category'] = 'Transmission'
                license_info['commercial_status'] = 'Utility Scale'
            
            # Only include if has meaningful data
            if license_info['fit_id'] and license_info['technology']:
                return license_info
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting license info: {e}")
            return None
    
    def _initialize_collections(self):
        """Initialize all Chroma collections"""
        try:
            # Create/get collections
            self._setup_license_collection()
            self._setup_commercial_collection()
            self._setup_unified_collection()
            
        except Exception as e:
            logger.error(f"Error initializing collections: {e}")
    
    def _setup_license_collection(self):
        """Setup FIT license collection"""
        try:
            collection_name = self.license_collection_name
            
            # Check if collection exists and is current
            try:
                collection = self.client.get_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function
                )
                
                current_count = collection.count()
                expected_count = len(self.fit_licenses)
                
                if current_count != expected_count:
                    logger.info(f"License collection outdated ({current_count} vs {expected_count}), recreating...")
                    self.client.delete_collection(name=collection_name)
                    raise Exception("Force recreation")
                else:
                    logger.info(f"License collection up to date with {current_count} records")
                    self.collections[collection_name] = collection
                    return
                    
            except:
                # Create new collection
                logger.info("Creating FIT license collection...")
                collection = self.client.create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function,
                    metadata={"hnsw:space": "cosine", "type": "fit_licenses"}
                )
                
                # Populate collection
                self._populate_license_collection(collection)
                self.collections[collection_name] = collection
                
        except Exception as e:
            logger.error(f"Error setting up license collection: {e}")
    
    def _populate_license_collection(self, collection):
        """Populate license collection with enhanced embeddings"""
        try:
            logger.info(f"Populating license collection with {len(self.fit_licenses)} licenses...")
            
            batch_size = 1000
            total_licenses = len(self.fit_licenses)
            
            for i in range(0, total_licenses, batch_size):
                batch_end = min(i + batch_size, total_licenses)
                batch_licenses = self.fit_licenses[i:batch_end]
                
                logger.info(f"Processing license batch {i//batch_size + 1}/{(total_licenses-1)//batch_size + 1}")
                
                documents = []
                metadatas = []
                ids = []
                
                for license_info in batch_licenses:
                    # Create rich embedding text
                    doc_text = self._create_license_embedding_text(license_info)
                    documents.append(doc_text)
                    
                    # Create metadata with enhanced geo fields
                    metadata = license_info.copy()
                    
                    # Add exact geo fields for precise filtering
                    postcode = metadata.get('postcode', '')
                    metadata['postcode_area'] = extract_postcode_area(postcode)
                    metadata['postcode_outward'] = extract_postcode_outward(postcode)
                    metadata['postcode_prefix'] = metadata['postcode_outward'] or metadata['postcode_area']
                    
                    # Normalize technology
                    if 'technology' in metadata:
                        metadata['technology'] = normalize_technology(metadata['technology'])
                    
                    # Ensure all values are JSON serializable
                    for key, value in metadata.items():
                        if pd.isna(value) or value == 'nan':
                            metadata[key] = ''
                        elif isinstance(value, (int, float, str, bool)):
                            metadata[key] = value
                        else:
                            metadata[key] = str(value)
                    
                    metadatas.append(metadata)
                    ids.append(f"license_{license_info['fit_id']}")
                
                # Add batch to collection
                collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
            
            logger.info(f"Successfully populated license collection with {total_licenses} licenses")
            
        except Exception as e:
            logger.error(f"Error populating license collection: {e}")
    
    def _create_license_embedding_text(self, license_info: Dict) -> str:
        """Create rich embedding text for FIT license"""
        text_parts = []
        
        # Basic identification
        fit_id = license_info.get('fit_id', 'unknown')
        technology = license_info.get('technology', 'unknown technology')
        text_parts.append(f"FIT license {fit_id} for {technology.lower()}")
        
        # Technology-specific descriptions
        tech_lower = technology.lower()
        if 'photovoltaic' in tech_lower:
            text_parts.append("solar photovoltaic renewable energy system")
        elif 'wind' in tech_lower:
            text_parts.append("wind turbine renewable energy system")
        elif 'hydro' in tech_lower:
            text_parts.append("hydroelectric renewable energy system")
        elif 'anaerobic' in tech_lower:
            text_parts.append("anaerobic digestion biogas renewable energy system")
        elif 'chp' in tech_lower:
            text_parts.append("combined heat and power renewable energy system")
        
        # Capacity and scale
        capacity_kw = license_info.get('capacity_kw', 0)
        capacity_mw = license_info.get('capacity_mw', 0)
        
        if capacity_kw > 0:
            if capacity_kw <= 4:
                text_parts.append(f"{capacity_kw}kW domestic micro-generation installation")
            elif capacity_kw <= 50:
                text_parts.append(f"{capacity_kw}kW small commercial installation")
            elif capacity_kw <= 250:
                text_parts.append(f"{capacity_kw}kW medium commercial renewable energy installation")
            elif capacity_kw <= 1000:
                text_parts.append(f"{capacity_mw:.2f}MW large commercial renewable energy facility")
            else:
                text_parts.append(f"{capacity_mw:.2f}MW utility-scale renewable energy facility")
        
        # FIT status and timing
        remaining_fit = license_info.get('remaining_fit_years', 0)
        age = license_info.get('age_years', 0)
        window = license_info.get('repowering_window', '')
        
        if age > 0:
            text_parts.append(f"commissioned {age:.1f} years ago")
        
        if remaining_fit > 15:
            text_parts.append("long-term feed-in tariff benefits remaining")
        elif remaining_fit > 10:
            text_parts.append("substantial feed-in tariff benefits remaining")
        elif remaining_fit > 5:
            text_parts.append("moderate feed-in tariff benefits remaining")
        elif remaining_fit > 0:
            text_parts.append("limited feed-in tariff benefits remaining, PPA opportunity emerging")
        else:
            text_parts.append("feed-in tariff expired, requiring power purchase agreement")
        
        # Urgency context
        if window == 'EXPIRED':
            text_parts.append("FIT has expired, immediate PPA required")
        elif window == 'IMMEDIATE':
            text_parts.append("requires immediate action for PPA transition")
        elif window == 'URGENT':
            text_parts.append("urgent attention needed for PPA planning")
        elif window == 'OPTIMAL':
            text_parts.append("in optimal window for PPA negotiation")
        
        # Location context with enhanced geo fields
        postcode = license_info.get('postcode', '')
        region = license_info.get('region', '')
        country = license_info.get('country', '')
        
        # Extract area and outward codes
        area = extract_postcode_area(postcode)
        outward = extract_postcode_outward(postcode)
        
        location_parts = []
        if postcode and postcode != 'nan':
            location_parts.append(f"postcode {postcode}")
            if area:
                location_parts.append(f"{area} postcode area")
            if outward and outward != area:
                location_parts.append(f"{outward} outward code")
        if region and region != 'nan':
            location_parts.append(f"{region} region")
        if country and country != 'nan':
            location_parts.append(f"{country}")
        
        if location_parts:
            text_parts.append("located in " + ", ".join(location_parts))
        
        # Commercial status
        commercial_status = license_info.get('commercial_status', '')
        if commercial_status:
            text_parts.append(f"{commercial_status.lower()} sector installation")
        
        # Export and tariff
        export_status = license_info.get('export_status', '')
        if export_status and export_status != 'nan':
            if 'deemed' in export_status.lower():
                text_parts.append("deemed export arrangement")
            elif 'total' in export_status.lower():
                text_parts.append("total export to grid")
        
        tariff_code = license_info.get('tariff_code', '')
        if tariff_code and tariff_code != 'nan':
            text_parts.append(f"tariff code {tariff_code}")
        
        return ". ".join(text_parts) + "."
    
    def _setup_commercial_collection(self):
        """Setup existing commercial collection (if needed)"""
        try:
            collection_name = self.commercial_collection_name
            
            try:
                collection = self.client.get_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function
                )
                logger.info(f"Commercial collection exists with {collection.count()} records")
                self.collections[collection_name] = collection
            except:
                logger.info("Commercial collection not found - would need to be created separately")
                
        except Exception as e:
            logger.error(f"Error setting up commercial collection: {e}")
    
    def _setup_unified_collection(self):
        """Setup unified collection combining license and commercial data"""
        # This would combine both datasets for comprehensive analysis
        logger.info("Unified collection setup - placeholder for future enhancement")
    
    def semantic_search_licenses(self, query: str, n_results: int = 10, filters: Dict = None) -> List[Dict]:
        """Search FIT licenses using semantic similarity"""
        try:
            collection = self.collections.get(self.license_collection_name)
            if not collection:
                logger.error("License collection not available")
                return []
            
            # Build where clause from filters
            where_clause = {}
            if filters:
                for key, value in filters.items():
                    if key == 'min_capacity_kw':
                        where_clause['capacity_kw'] = {"$gte": value}
                    elif key == 'max_capacity_kw':
                        where_clause['capacity_kw'] = {"$lte": value}
                    elif key == 'technology':
                        where_clause['technology'] = {"$eq": value}
                    elif key == 'repowering_window':
                        where_clause['repowering_window'] = {"$eq": value}
                    elif key == 'country':
                        where_clause['country'] = {"$eq": value}
                    elif key == 'commercial_status':
                        where_clause['commercial_status'] = {"$eq": value}
            
            # Perform search
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause if where_clause else None,
                include=['metadatas', 'documents', 'distances']
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    'id': results['ids'][0][i],
                    'score': 1 - results['distances'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'description': results['documents'][0][i]
                }
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"License search error: {e}")
            return []
    
    def get_license_insights(self, technology: str = None) -> Dict:
        """Get insights about FIT licenses"""
        try:
            collection = self.collections.get(self.license_collection_name)
            if not collection:
                return {"error": "License collection not available"}
            
            # Get all license metadata
            all_results = collection.get(include=['metadatas'])
            licenses = all_results['metadatas']
            
            if technology:
                licenses = [l for l in licenses if l.get('technology', '').lower() == technology.lower()]
            
            if not licenses:
                return {"error": "No licenses found"}
            
            # Calculate insights
            total_licenses = len(licenses)
            total_capacity = sum(float(l.get('capacity_kw', 0)) for l in licenses)
            
            # Age analysis
            ages = [float(l.get('age_years', 0)) for l in licenses if l.get('age_years')]
            avg_age = np.mean(ages) if ages else 0
            
            # FIT remaining analysis
            remaining_fits = [float(l.get('remaining_fit_years', 0)) for l in licenses if l.get('remaining_fit_years')]
            avg_remaining = np.mean(remaining_fits) if remaining_fits else 0
            
            # Urgency analysis
            urgent_count = sum(1 for l in licenses if l.get('repowering_window') in ['IMMEDIATE', 'URGENT'])
            expired_count = sum(1 for l in licenses if l.get('repowering_window') == 'EXPIRED')
            
            # Technology breakdown
            tech_counts = {}
            for license in licenses:
                tech = license.get('technology', 'Unknown')
                tech_counts[tech] = tech_counts.get(tech, 0) + 1
            
            # Capacity bands
            capacity_bands = {'Micro': 0, 'Small': 0, 'Medium': 0, 'Large': 0, 'Utility': 0}
            for license in licenses:
                category = license.get('size_category', '')
                if 'Micro' in category:
                    capacity_bands['Micro'] += 1
                elif 'Small' in category:
                    capacity_bands['Small'] += 1
                elif 'Medium' in category:
                    capacity_bands['Medium'] += 1
                elif 'Large' in category:
                    capacity_bands['Large'] += 1
                elif 'Utility' in category:
                    capacity_bands['Utility'] += 1
            
            return {
                'technology': technology or 'All Technologies',
                'total_licenses': total_licenses,
                'total_capacity_kw': round(total_capacity, 1),
                'total_capacity_mw': round(total_capacity / 1000, 1),
                'average_age_years': round(avg_age, 1),
                'average_remaining_fit_years': round(avg_remaining, 1),
                'urgent_ppa_opportunities': urgent_count,
                'expired_fit_sites': expired_count,
                'technology_breakdown': tech_counts,
                'capacity_band_distribution': capacity_bands
            }
            
        except Exception as e:
            logger.error(f"License insights error: {e}")
            return {"error": str(e)}
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about all collections"""
        stats = {
            'enhanced_system_ready': True,
            'collections': {}
        }
        
        for name, collection in self.collections.items():
            try:
                count = collection.count()
                stats['collections'][name] = {
                    'document_count': count,
                    'embedding_model': 'all-MiniLM-L6-v2'
                }
            except:
                stats['collections'][name] = {'error': 'Collection not accessible'}
        
        return stats

# Test the enhanced system
if __name__ == "__main__":
    print("=" * 60)
    print("ENHANCED CHROMA FIT INTELLIGENCE SYSTEM")
    print("=" * 60)
    
    # Initialize enhanced system
    enhanced_intel = EnhancedChromaFITIntelligence()
    
    # Show system stats
    stats = enhanced_intel.get_collection_stats()
    print(f"\nSystem Status:")
    for collection_name, collection_stats in stats['collections'].items():
        if 'document_count' in collection_stats:
            print(f"✓ {collection_name}: {collection_stats['document_count']} documents")
        else:
            print(f"✗ {collection_name}: {collection_stats.get('error', 'Unknown error')}")
    
    # Test license search
    if 'fit_licenses' in stats['collections']:
        print(f"\nTesting license search...")
        results = enhanced_intel.semantic_search_licenses(
            "large wind farms with expiring FIT tariffs", 
            n_results=3
        )
        
        for i, result in enumerate(results):
            print(f"{i+1}. Score: {result['score']:.3f}")
            print(f"   FIT ID: {result['metadata']['fit_id']}")
            print(f"   Technology: {result['metadata']['technology']}")
            print(f"   Capacity: {result['metadata']['capacity_kw']}kW")
            print(f"   Window: {result['metadata']['repowering_window']}")
        
        # Get insights
        print(f"\nLicense insights:")
        insights = enhanced_intel.get_license_insights()
        print(f"Total licenses: {insights.get('total_licenses', 0)}")
        print(f"Total capacity: {insights.get('total_capacity_mw', 0)} MW")
        print(f"Urgent opportunities: {insights.get('urgent_ppa_opportunities', 0)}")
    
    print(f"\nEnhanced FIT Intelligence System ready!")