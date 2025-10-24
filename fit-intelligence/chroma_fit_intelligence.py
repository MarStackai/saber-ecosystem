#!/usr/bin/env python3
"""
Chroma-based FIT Intelligence System
Uses vector embeddings for semantic search across all commercial renewable energy assets
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import pandas as pd
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import datetime
import logging
from typing import List, Dict, Optional
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaFITIntelligence:
    """
    Vector-based intelligence system for FIT/PPA analysis
    Uses Chroma DB with local embeddings for semantic search
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize Chroma client with local persistence"""
        self.persist_directory = persist_directory
        
        # Initialize Chroma client with local persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                is_persistent=True
            )
        )
        
        # Initialize sentence transformer embedding function
        logger.info("Loading sentence transformer model...")
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        logger.info("Embedding model loaded")
        
        # Collection for FIT sites
        self.collection_name = "commercial_fit_sites"
        self.collection = None
        
        # Load and process data
        self.fit_data = self._load_fit_data()
        self._initialize_collection()
    
    def _load_fit_data(self) -> pd.DataFrame:
        """Load all commercial FIT data"""
        try:
            with open('data/all_commercial_fit.json', 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data['sites'])
            logger.info(f"Loaded {len(df):,} commercial FIT sites")
            
            # Log technology breakdown
            tech_counts = df['technology'].value_counts()
            for tech, count in tech_counts.items():
                logger.info(f"  {tech}: {count:,} sites")
            
            return df
        except Exception as e:
            logger.error(f"Error loading FIT data: {e}")
            return pd.DataFrame()
    
    def _initialize_collection(self):
        """Initialize or get existing Chroma collection"""
        try:
            # Try to get existing collection
            self.collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Found existing collection with {self.collection.count()} documents")
            
            # Check if we need to update
            if self.collection.count() != len(self.fit_data):
                logger.info("Collection size mismatch, recreating...")
                self.client.delete_collection(name=self.collection_name)
                self._create_collection()
            
        except Exception:
            # Collection doesn't exist, create it
            logger.info("Creating new collection...")
            self._create_collection()
    
    # Remove the old embedding function - now using Chroma's built-in
    
    def _create_collection(self):
        """Create and populate Chroma collection"""
        logger.info("Creating Chroma collection...")
        
        # Create collection
        self.collection = self.client.create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Process sites in batches
        batch_size = 1000
        total_sites = len(self.fit_data)
        
        for i in range(0, total_sites, batch_size):
            batch_end = min(i + batch_size, total_sites)
            batch_df = self.fit_data.iloc[i:batch_end]
            
            logger.info(f"Processing batch {i//batch_size + 1}/{(total_sites-1)//batch_size + 1}")
            
            # Generate rich text descriptions for embedding
            documents = []
            metadatas = []
            ids = []
            
            for idx, site in batch_df.iterrows():
                # Create rich text description for semantic search
                doc_text = self._create_site_description(site)
                documents.append(doc_text)
                
                # Metadata for filtering and retrieval
                metadata = {
                    'technology': str(site.get('technology', '')),
                    'capacity_mw': float(site.get('capacity_mw', 0)),
                    'capacity_kw': float(site.get('capacity_kw', 0)),
                    'age_years': float(site.get('age_years', 0)),
                    'remaining_fit_years': float(site.get('remaining_fit_years', 0)),
                    'repowering_window': str(site.get('repowering_window', '')),
                    'postcode': str(site.get('postcode', '')),
                    'region': str(site.get('region', '')),
                    'country': str(site.get('country', '')),
                    'local_authority': str(site.get('local_authority', '')),
                    'tariff_p_kwh': float(site.get('tariff_p_kwh', 0)),
                    'annual_generation_mwh': float(site.get('annual_generation_mwh', 0)),
                    'annual_fit_revenue_gbp': float(site.get('annual_fit_revenue_gbp', 0)),
                    'ppa_readiness_score': float(site.get('ppa_readiness_score', 0)),
                    'size_category': str(site.get('size_category', '')),
                    'grid_category': str(site.get('grid_category', '')),
                    'repowering_potential': str(site.get('repowering_potential', '')),
                    'commission_date': str(site.get('commission_date', '')),
                    'fit_id': str(site.get('fit_id', ''))
                }
                metadatas.append(metadata)
                ids.append(f"site_{idx}")
            
            # Add batch to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        
        logger.info(f"Successfully indexed {total_sites:,} sites in Chroma")
    
    def _create_site_description(self, site: pd.Series) -> str:
        """Create rich text description for semantic embedding"""
        
        # Basic info
        tech = site.get('technology', 'Unknown')
        capacity = site.get('capacity_mw', 0)
        age = site.get('age_years', 0)
        remaining_fit = site.get('remaining_fit_years', 0)
        window = site.get('repowering_window', '')
        
        # Location
        postcode = site.get('postcode', '')
        region = site.get('region', '')
        country = site.get('country', '')
        local_auth = site.get('local_authority', '')
        
        # Financial
        tariff = site.get('tariff_p_kwh', 0)
        annual_revenue = site.get('annual_fit_revenue_gbp', 0)
        
        # Categories
        size_cat = site.get('size_category', '')
        grid_cat = site.get('grid_category', '')
        repower_pot = site.get('repowering_potential', '')
        
        # Create rich description
        desc_parts = []
        
        # Technology and capacity
        desc_parts.append(f"{tech} renewable energy installation")
        desc_parts.append(f"{capacity:.2f} MW capacity")
        desc_parts.append(f"{size_cat} installation")
        
        # Age and FIT status
        desc_parts.append(f"{age:.1f} years old")
        if remaining_fit > 0:
            desc_parts.append(f"{remaining_fit:.1f} years of FIT remaining")
            if remaining_fit < 2:
                desc_parts.append("urgent PPA opportunity")
            elif remaining_fit < 5:
                desc_parts.append("immediate PPA potential")
            elif remaining_fit < 10:
                desc_parts.append("optimal PPA timing window")
        else:
            desc_parts.append("expired FIT requiring immediate PPA")
        
        # Repowering window
        if window == 'IMMEDIATE':
            desc_parts.append("requires immediate action for PPA transition")
        elif window == 'URGENT':
            desc_parts.append("urgent attention needed for PPA planning")
        elif window == 'OPTIMAL':
            desc_parts.append("in optimal window for PPA negotiation")
        elif window == 'EXPIRED':
            desc_parts.append("FIT has expired, needs PPA now")
        
        # Location details
        location_parts = []
        if postcode:
            location_parts.append(f"postcode {postcode}")
        if local_auth:
            location_parts.append(f"in {local_auth}")
        if region:
            location_parts.append(f"{region} region")
        if country:
            location_parts.append(f"{country}")
        
        if location_parts:
            desc_parts.append("located " + ", ".join(location_parts))
        
        # Financial aspects
        if annual_revenue > 0:
            desc_parts.append(f"generating £{annual_revenue:,.0f} annual FIT revenue")
        if tariff > 0:
            desc_parts.append(f"receiving {tariff:.2f}p/kWh FIT rate")
        
        # Grid and repowering
        if grid_cat:
            desc_parts.append(f"{grid_cat.lower()} grid connection")
        
        if repower_pot and repower_pot != 'Low':
            desc_parts.append(f"{repower_pot.lower()} repowering potential")
        
        # Technology-specific details
        if tech == 'Photovoltaic':
            desc_parts.append("solar PV technology")
        elif tech == 'Wind':
            desc_parts.append("wind energy generation")
        elif tech == 'Hydro':
            desc_parts.append("hydroelectric power")
        elif tech == 'Anaerobic digestion':
            desc_parts.append("biogas anaerobic digestion plant")
        elif tech == 'Micro CHP':
            desc_parts.append("combined heat and power system")
        
        return ". ".join(desc_parts) + "."
    
    def semantic_search(self, query: str, n_results: int = 10, filters: Dict = None) -> List[Dict]:
        """
        Perform semantic search across all FIT sites
        """
        try:
            # Build where clause from filters
            where_clause = {}
            if filters:
                for key, value in filters.items():
                    if key == 'min_capacity_mw':
                        where_clause['capacity_mw'] = {"$gte": value}
                    elif key == 'max_capacity_mw':
                        where_clause['capacity_mw'] = {"$lte": value}
                    elif key == 'technology':
                        where_clause['technology'] = {"$eq": value}
                    elif key == 'repowering_window':
                        where_clause['repowering_window'] = {"$eq": value}
                    elif key == 'min_remaining_fit':
                        where_clause['remaining_fit_years'] = {"$gte": value}
                    elif key == 'max_remaining_fit':
                        where_clause['remaining_fit_years'] = {"$lte": value}
                    elif key == 'region':
                        where_clause['region'] = {"$eq": value}
                    elif key == 'country':
                        where_clause['country'] = {"$eq": value}
            
            # Perform search
            results = self.collection.query(
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
                    'score': 1 - results['distances'][0][i],  # Convert distance to similarity
                    'metadata': results['metadatas'][0][i],
                    'description': results['documents'][0][i]
                }
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def get_technology_insights(self, technology: str = None) -> Dict:
        """Get insights for specific technology or all technologies"""
        try:
            if technology:
                results = self.collection.query(
                    query_texts=[f"{technology} renewable energy installations"],
                    n_results=10000,
                    where={"technology": {"$eq": technology}},
                    include=['metadatas']
                )
                sites = [r for r in results['metadatas'][0]]
            else:
                # Get all sites
                all_results = self.collection.get(include=['metadatas'])
                sites = all_results['metadatas']
            
            if not sites:
                return {"error": "No sites found"}
            
            # Calculate insights
            total_sites = len(sites)
            total_capacity = sum(s['capacity_mw'] for s in sites)
            avg_age = np.mean([s['age_years'] for s in sites])
            avg_remaining_fit = np.mean([s['remaining_fit_years'] for s in sites])
            
            # Urgency analysis
            urgent_sites = [s for s in sites if s['remaining_fit_years'] < 2]
            immediate_sites = [s for s in sites if s['repowering_window'] == 'IMMEDIATE']
            
            # Regional breakdown
            regions = {}
            for site in sites:
                region = site['region']
                if region not in regions:
                    regions[region] = {'count': 0, 'capacity_mw': 0}
                regions[region]['count'] += 1
                regions[region]['capacity_mw'] += site['capacity_mw']
            
            return {
                'technology': technology or 'All Technologies',
                'total_sites': total_sites,
                'total_capacity_mw': round(total_capacity, 1),
                'average_age_years': round(avg_age, 1),
                'average_remaining_fit_years': round(avg_remaining_fit, 1),
                'urgent_ppa_opportunities': len(urgent_sites),
                'immediate_action_sites': len(immediate_sites),
                'regional_breakdown': dict(sorted(regions.items(), 
                                                key=lambda x: x[1]['capacity_mw'], 
                                                reverse=True)[:5])
            }
            
        except Exception as e:
            logger.error(f"Insights error: {e}")
            return {"error": str(e)}
    
    def find_clusters(self, min_sites: int = 5, radius_km: float = 10) -> List[Dict]:
        """Find geographic clusters of sites for operational efficiency"""
        # For now, use postcode prefix clustering
        # TODO: Implement proper geospatial clustering
        
        try:
            all_results = self.collection.get(include=['metadatas'])
            sites = all_results['metadatas']
            
            # Group by postcode prefix (first 3-4 characters)
            clusters = {}
            for site in sites:
                postcode = site.get('postcode', '')
                if len(postcode) >= 3:
                    prefix = postcode[:4] if len(postcode) > 3 else postcode[:3]
                    
                    if prefix not in clusters:
                        clusters[prefix] = []
                    clusters[prefix].append(site)
            
            # Filter significant clusters
            significant_clusters = []
            for prefix, cluster_sites in clusters.items():
                if len(cluster_sites) >= min_sites:
                    total_capacity = sum(s['capacity_mw'] for s in cluster_sites)
                    avg_remaining_fit = np.mean([s['remaining_fit_years'] for s in cluster_sites])
                    urgent_count = sum(1 for s in cluster_sites if s['remaining_fit_years'] < 5)
                    
                    tech_mix = {}
                    for site in cluster_sites:
                        tech = site['technology']
                        tech_mix[tech] = tech_mix.get(tech, 0) + 1
                    
                    significant_clusters.append({
                        'postcode_area': prefix,
                        'site_count': len(cluster_sites),
                        'total_capacity_mw': round(total_capacity, 1),
                        'average_remaining_fit_years': round(avg_remaining_fit, 1),
                        'urgent_sites': urgent_count,
                        'technology_mix': tech_mix,
                        'opportunity_score': len(cluster_sites) * 2 + total_capacity * 5 + urgent_count * 10
                    })
            
            # Sort by opportunity score
            significant_clusters.sort(key=lambda x: x['opportunity_score'], reverse=True)
            
            return significant_clusters[:20]
            
        except Exception as e:
            logger.error(f"Clustering error: {e}")
            return []
    
    def natural_language_query(self, query: str, max_results: int = 10) -> Dict:
        """
        Process natural language queries about the FIT portfolio
        """
        try:
            # Extract filters from natural language
            filters = self._parse_nl_filters(query)
            
            # Perform semantic search
            results = self.semantic_search(query, n_results=max_results, filters=filters)
            
            # Generate summary
            if results:
                total_capacity = sum(r['metadata']['capacity_mw'] for r in results)
                avg_score = np.mean([r['score'] for r in results])
                tech_counts = {}
                window_counts = {}
                
                for r in results:
                    tech = r['metadata']['technology']
                    window = r['metadata']['repowering_window']
                    tech_counts[tech] = tech_counts.get(tech, 0) + 1
                    window_counts[window] = window_counts.get(window, 0) + 1
                
                summary = {
                    'query': query,
                    'results_found': len(results),
                    'total_capacity_mw': round(total_capacity, 1),
                    'average_relevance_score': round(avg_score, 3),
                    'technology_breakdown': tech_counts,
                    'repowering_window_breakdown': window_counts,
                    'filters_applied': filters
                }
            else:
                summary = {
                    'query': query,
                    'results_found': 0,
                    'message': 'No matching sites found'
                }
            
            return {
                'summary': summary,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"NL Query error: {e}")
            return {'error': str(e)}
    
    def _parse_nl_filters(self, query: str) -> Dict:
        """Extract filters from natural language query"""
        filters = {}
        query_lower = query.lower()
        
        # Technology filters
        if 'solar' in query_lower or 'photovoltaic' in query_lower:
            filters['technology'] = 'Photovoltaic'
        elif 'wind' in query_lower:
            filters['technology'] = 'Wind'
        elif 'hydro' in query_lower:
            filters['technology'] = 'Hydro'
        elif 'anaerobic' in query_lower or 'biogas' in query_lower:
            filters['technology'] = 'Anaerobic digestion'
        elif 'chp' in query_lower:
            filters['technology'] = 'Micro CHP'
        
        # Urgency filters
        if 'urgent' in query_lower or 'immediate' in query_lower:
            filters['max_remaining_fit'] = 2
        elif 'expir' in query_lower:
            filters['max_remaining_fit'] = 0
        
        # Capacity filters
        if 'over 1mw' in query_lower or '>1mw' in query_lower:
            filters['min_capacity_mw'] = 1.0
        elif 'over 5mw' in query_lower or '>5mw' in query_lower:
            filters['min_capacity_mw'] = 5.0
        elif 'under 1mw' in query_lower or '<1mw' in query_lower:
            filters['max_capacity_mw'] = 1.0
        
        # Region filters
        if 'scotland' in query_lower:
            filters['country'] = 'Scotland'
        elif 'wales' in query_lower:
            filters['country'] = 'Wales'
        elif 'england' in query_lower:
            filters['country'] = 'England'
        
        return filters
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the Chroma collection"""
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'collection_name': self.collection_name,
                'persist_directory': self.persist_directory,
                'embedding_model': 'all-MiniLM-L6-v2'
            }
        except Exception as e:
            return {'error': str(e)}

# Test the system
if __name__ == "__main__":
    print("Initializing Chroma FIT Intelligence System...")
    
    # Initialize system
    chroma_intel = ChromaFITIntelligence()
    
    print(f"\n{chroma_intel.get_collection_stats()}")
    
    # Test semantic search
    print("\nTesting semantic search...")
    results = chroma_intel.semantic_search("urgent wind farms needing PPA", n_results=5)
    
    for i, result in enumerate(results[:3]):
        print(f"\n{i+1}. Score: {result['score']:.3f}")
        print(f"   Technology: {result['metadata']['technology']}")
        print(f"   Capacity: {result['metadata']['capacity_mw']:.1f} MW")
        print(f"   FIT Remaining: {result['metadata']['remaining_fit_years']:.1f} years")
        print(f"   Window: {result['metadata']['repowering_window']}")
    
    # Test natural language query
    print("\nTesting natural language query...")
    nl_result = chroma_intel.natural_language_query("Show me solar sites in Scotland over 1MW")
    print(f"Found {nl_result['summary']['results_found']} matching sites")
    
    # Test technology insights
    print("\nTechnology insights...")
    insights = chroma_intel.get_technology_insights('Wind')
    print(f"Wind: {insights['total_sites']} sites, {insights['total_capacity_mw']} MW")
    
    print("\nChroma FIT Intelligence System ready!")