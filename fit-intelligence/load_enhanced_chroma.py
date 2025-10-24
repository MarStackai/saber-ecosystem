#!/usr/bin/env python3
"""
Load Enhanced ChromaDB with FIT License Data
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import json
import logging
from typing import List, Dict
import glob
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedChromaLoader:
    """Load processed FIT license data into ChromaDB"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
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
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        self.license_collection = None
        
    def load_processed_license_data(self, filename: str = None) -> Dict:
        """Load the most recent processed license data"""
        try:
            if filename is None:
                # Find the most recent processed file
                pattern = 'data/processed_fit_licenses_*.json'
                files = glob.glob(pattern)
                if not files:
                    raise FileNotFoundError("No processed license files found")
                filename = max(files)  # Most recent by filename
            
            logger.info(f"Loading processed license data from {filename}")
            
            with open(filename, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Loaded {data.get('total_licenses', 0)} processed licenses")
            return data
            
        except Exception as e:
            logger.error(f"Error loading processed data: {e}")
            return {}
    
    def create_license_collection(self, data: Dict, force_recreate: bool = False) -> bool:
        """Create and populate FIT license collection"""
        try:
            collection_name = "fit_licenses_enhanced"
            
            # Check if collection exists
            if not force_recreate:
                try:
                    existing_collection = self.client.get_collection(
                        name=collection_name,
                        embedding_function=self.embedding_function
                    )
                    
                    current_count = existing_collection.count()
                    expected_count = data.get('total_licenses', 0)
                    
                    if current_count == expected_count:
                        logger.info(f"Collection up to date with {current_count} documents")
                        self.license_collection = existing_collection
                        return True
                    else:
                        logger.info(f"Collection outdated ({current_count} vs {expected_count}), recreating...")
                        self.client.delete_collection(name=collection_name)
                
                except:
                    # Collection doesn't exist
                    pass
            else:
                # Force recreation
                try:
                    self.client.delete_collection(name=collection_name)
                    logger.info("Deleted existing collection for recreation")
                except:
                    pass
            
            # Create new collection
            logger.info("Creating enhanced FIT license collection...")
            collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={
                    "hnsw:space": "cosine",
                    "type": "enhanced_fit_licenses",
                    "created": datetime.now().isoformat(),
                    "source": "FIT Installation Reports Parts 1-3"
                }
            )
            
            # Populate collection
            embeddings_data = data.get('embeddings_data', [])
            if embeddings_data:
                success = self._populate_collection(collection, embeddings_data)
                if success:
                    self.license_collection = collection
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error creating license collection: {e}")
            return False
    
    def _populate_collection(self, collection, embeddings_data: List[Dict]) -> bool:
        """Populate collection with embedding data"""
        try:
            logger.info(f"Populating collection with {len(embeddings_data)} license embeddings...")
            
            batch_size = 1000
            total_items = len(embeddings_data)
            
            for i in range(0, total_items, batch_size):
                batch_end = min(i + batch_size, total_items)
                batch = embeddings_data[i:batch_end]
                
                batch_num = (i // batch_size) + 1
                total_batches = (total_items - 1) // batch_size + 1
                logger.info(f"Processing batch {batch_num}/{total_batches}")
                
                # Prepare batch data
                documents = []
                metadatas = []
                ids = []
                
                for item in batch:
                    documents.append(item['text'])
                    metadatas.append(item['metadata'])
                    ids.append(item['id'])
                
                # Add to collection
                collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
            
            final_count = collection.count()
            logger.info(f"Successfully populated collection with {final_count} documents")
            return final_count == total_items
            
        except Exception as e:
            logger.error(f"Error populating collection: {e}")
            return False
    
    def test_collection(self, n_results: int = 5) -> Dict:
        """Test the created collection with sample queries"""
        if not self.license_collection:
            return {"error": "No collection available"}
        
        try:
            test_results = {}
            
            # Basic stats
            total_docs = self.license_collection.count()
            test_results['total_documents'] = total_docs
            
            # Test semantic searches
            test_queries = [
                "large solar installations with expiring FIT",
                "wind farms requiring immediate PPA",
                "commercial photovoltaic systems over 100kW",
                "renewable energy sites in Scotland",
                "expired feed-in tariff opportunities"
            ]
            
            for query in test_queries:
                try:
                    results = self.license_collection.query(
                        query_texts=[query],
                        n_results=n_results,
                        include=['metadatas', 'distances']
                    )
                    
                    # Process results
                    formatted_results = []
                    for i in range(len(results['ids'][0])):
                        result = {
                            'fit_id': results['metadatas'][0][i].get('fit_id'),
                            'technology': results['metadatas'][0][i].get('technology'),
                            'capacity_kw': results['metadatas'][0][i].get('capacity_kw'),
                            'repowering_window': results['metadatas'][0][i].get('repowering_window'),
                            'score': 1 - results['distances'][0][i]
                        }
                        formatted_results.append(result)
                    
                    test_results[f'query_{len(test_results)}'] = {
                        'query': query,
                        'results_found': len(formatted_results),
                        'sample_results': formatted_results[:3]
                    }
                    
                except Exception as e:
                    test_results[f'query_{len(test_results)}'] = {
                        'query': query,
                        'error': str(e)
                    }
            
            return test_results
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_technology_insights(self, technology: str = None) -> Dict:
        """Get insights for specific technology"""
        if not self.license_collection:
            return {"error": "No collection available"}
        
        try:
            # Get all or filtered results
            if technology:
                results = self.license_collection.get(
                    where={"technology": {"$eq": technology}},
                    include=['metadatas']
                )
            else:
                results = self.license_collection.get(include=['metadatas'])
            
            metadatas = results['metadatas']
            
            if not metadatas:
                return {"error": f"No data found for {technology if technology else 'any technology'}"}
            
            # Calculate insights
            total_licenses = len(metadatas)
            
            # Capacity analysis
            capacities = [float(m.get('capacity_kw', 0)) for m in metadatas if m.get('capacity_kw')]
            total_capacity_kw = sum(capacities)
            
            # Age analysis
            ages = [float(m.get('age_years', 0)) for m in metadatas if m.get('age_years')]
            avg_age = sum(ages) / len(ages) if ages else 0
            
            # Remaining FIT analysis
            remaining_fits = [float(m.get('remaining_fit_years', 0)) for m in metadatas if m.get('remaining_fit_years')]
            avg_remaining = sum(remaining_fits) / len(remaining_fits) if remaining_fits else 0
            
            # Urgency breakdown
            urgency_counts = {}
            for m in metadatas:
                window = m.get('repowering_window', 'Unknown')
                urgency_counts[window] = urgency_counts.get(window, 0) + 1
            
            # Regional breakdown
            region_counts = {}
            for m in metadatas:
                region = m.get('region', 'Unknown')
                if region and region.strip():
                    region_counts[region] = region_counts.get(region, 0) + 1
            
            # Top regions
            top_regions = dict(sorted(region_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            
            return {
                'technology': technology or 'All Technologies',
                'total_licenses': total_licenses,
                'total_capacity_kw': round(total_capacity_kw, 1),
                'total_capacity_mw': round(total_capacity_kw / 1000, 1),
                'average_age_years': round(avg_age, 1),
                'average_remaining_fit_years': round(avg_remaining, 1),
                'repowering_window_breakdown': urgency_counts,
                'top_regions': top_regions,
                'licenses_with_capacity_data': len(capacities),
                'licenses_with_age_data': len(ages)
            }
            
        except Exception as e:
            logger.error(f"Error getting insights: {e}")
            return {"error": str(e)}

def main():
    """Main function to load and test enhanced ChromaDB"""
    print("=" * 60)
    print("ENHANCED CHROMADB LOADER")
    print("=" * 60)
    
    # Initialize loader
    loader = EnhancedChromaLoader()
    
    # Load processed data
    print("\n1. Loading processed license data...")
    data = loader.load_processed_license_data()
    
    if not data:
        print("✗ Failed to load processed data")
        return
    
    print(f"✓ Loaded {data.get('total_licenses', 0)} processed licenses")
    
    # Create collection
    print("\n2. Creating enhanced license collection...")
    success = loader.create_license_collection(data, force_recreate=False)
    
    if not success:
        print("✗ Failed to create collection")
        return
    
    print("✓ Enhanced license collection created successfully")
    
    # Test collection
    print("\n3. Testing collection with sample queries...")
    test_results = loader.test_collection()
    
    if 'error' in test_results:
        print(f"✗ Testing failed: {test_results['error']}")
    else:
        print(f"✓ Collection ready with {test_results['total_documents']} documents")
        
        # Show sample query results
        for key, result in test_results.items():
            if key.startswith('query_') and 'error' not in result:
                print(f"\nQuery: '{result['query']}'")
                print(f"Found {result['results_found']} results")
                
                for i, sample in enumerate(result['sample_results']):
                    print(f"  {i+1}. FIT {sample['fit_id']}: {sample['technology']} "
                          f"{sample['capacity_kw']}kW ({sample['repowering_window']})")
    
    # Get technology insights
    print("\n4. Technology insights...")
    insights = loader.get_technology_insights('Photovoltaic')
    
    if 'error' not in insights:
        print(f"Solar PV: {insights['total_licenses']} licenses, "
              f"{insights['total_capacity_mw']}MW total capacity")
        print(f"Average age: {insights['average_age_years']} years")
        print(f"Urgency breakdown: {insights['repowering_window_breakdown']}")
    
    print(f"\n{'='*60}")
    print("ENHANCED CHROMADB SYSTEM READY!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()