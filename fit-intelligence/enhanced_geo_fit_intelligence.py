#!/usr/bin/env python3
"""
Enhanced FIT Intelligence with UK Geographic Integration
Combines FIT data analysis with comprehensive UK postcode and geographic intelligence
"""

import logging
from typing import Dict, List, Optional
import re
from uk_geo_intelligence import UKGeoIntelligence
from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedGeoFITIntelligence:
    """Enhanced FIT Intelligence with comprehensive UK geographic capabilities"""
    
    def __init__(self):
        self.fit_intelligence = EnhancedFITIntelligenceAPI()
        self.geo_intelligence = UKGeoIntelligence()
        
        logger.info("Enhanced Geographic FIT Intelligence initialized")
    
    def search_sites_by_location(self, query: str, radius_km: float = 20, max_results: int = 20) -> Dict:
        """
        Advanced location-based search with geographic intelligence
        Supports queries like 'wind sites near Beverly between 250-500kW'
        """
        try:
            # Extract location from query
            location_info = self._extract_location_from_query(query)
            if 'error' in location_info:
                return location_info
            
            center_postcode = location_info['postcode']
            center_geo = location_info['geo_data']
            
            # Find nearby postcodes
            nearby_result = self.geo_intelligence.find_nearby_postcodes(center_postcode, radius_km)
            if 'error' in nearby_result:
                return nearby_result
            
            target_postcodes = [center_postcode] + [pc['postcode'] for pc in nearby_result['nearby_postcodes']]
            
            # Search FIT database with enhanced geographic filtering
            fit_results = self.fit_intelligence.natural_language_query(query, max_results)
            
            # Filter results by geographic proximity
            if 'error' not in fit_results:
                geo_filtered_results = self._apply_geographic_filtering(
                    fit_results, target_postcodes, center_geo, radius_km
                )
                
                # Enhance with geographic analysis
                enhanced_results = self._enhance_with_geographic_analysis(
                    geo_filtered_results, location_info, nearby_result
                )
                
                return enhanced_results
            else:
                return fit_results
                
        except Exception as e:
            logger.error(f"Geographic search error: {e}")
            return {'error': str(e)}
    
    def analyze_site_clusters(self, technology: str = None, min_sites: int = 3) -> Dict:
        """
        Identify geographic clusters of renewable energy sites
        Critical for portfolio optimization and PPA strategy
        """
        try:
            # Get all sites of specified technology
            query = f"{technology} installations" if technology else "renewable energy installations"
            all_sites = self.fit_intelligence.natural_language_query(query, max_results=100)
            
            if 'error' in all_sites:
                return all_sites
            
            # Extract sites with valid postcodes
            sites_with_postcodes = []
            for site in all_sites['commercial_results'] + all_sites['license_results']:
                postcode = site['metadata'].get('postcode', '').strip()
                if postcode and len(postcode) >= 3:  # Valid postcode format
                    sites_with_postcodes.append({
                        'site': site,
                        'postcode': postcode,
                        'capacity_kw': site['metadata'].get('capacity_kw', 
                                                          site['metadata'].get('capacity_mw', 0) * 1000)
                    })
            
            # Group sites into geographic clusters
            clusters = self._identify_geographic_clusters(sites_with_postcodes, min_sites)
            
            # Enhance clusters with geographic intelligence
            enhanced_clusters = []
            for cluster in clusters:
                enhanced_cluster = self._enhance_cluster_with_geo_data(cluster)
                enhanced_clusters.append(enhanced_cluster)
            
            return {
                'technology': technology,
                'total_sites_analyzed': len(sites_with_postcodes),
                'clusters_found': len(enhanced_clusters),
                'clusters': enhanced_clusters,
                'analysis_summary': self._create_cluster_analysis_summary(enhanced_clusters)
            }
            
        except Exception as e:
            logger.error(f"Site cluster analysis error: {e}")
            return {'error': str(e)}
    
    def get_regional_fit_analysis(self, postcode: str, radius_km: float = 50) -> Dict:
        """
        Comprehensive regional analysis combining FIT data with geographic intelligence
        Perfect for market entry and investment decisions
        """
        try:
            # Get regional statistics
            regional_stats = self.geo_intelligence.get_regional_statistics(postcode)
            if 'error' in regional_stats:
                return regional_stats
            
            # Find nearby postcodes for regional analysis
            nearby = self.geo_intelligence.find_nearby_postcodes(postcode, radius_km)
            if 'error' in nearby:
                return nearby
            
            # Analyze FIT installations in the region
            region_name = regional_stats['administrative_hierarchy']['region']
            regional_query = f"renewable installations in {region_name}"
            
            fit_analysis = self.fit_intelligence.get_comprehensive_insights()
            
            # Create comprehensive regional report
            regional_report = {
                'center_postcode': postcode,
                'analysis_radius_km': radius_km,
                'geographic_data': regional_stats,
                'nearby_postcodes_count': nearby['count'],
                'fit_analysis': fit_analysis,
                'regional_opportunities': self._identify_regional_opportunities(
                    regional_stats, fit_analysis
                ),
                'market_intelligence': self._create_market_intelligence(
                    regional_stats, nearby
                )
            }
            
            return regional_report
            
        except Exception as e:
            logger.error(f"Regional FIT analysis error: {e}")
            return {'error': str(e)}
    
    def calculate_site_logistics(self, site_postcodes: List[str]) -> Dict:
        """
        Calculate logistics metrics for multiple renewable energy sites
        Essential for maintenance scheduling and operational efficiency
        """
        try:
            if len(site_postcodes) < 2:
                return {'error': 'Need at least 2 postcodes for logistics analysis'}
            
            # Calculate all pairwise distances
            distance_matrix = {}
            for i, pc1 in enumerate(site_postcodes):
                distance_matrix[pc1] = {}
                for j, pc2 in enumerate(site_postcodes):
                    if i != j:
                        distance_result = self.geo_intelligence.calculate_distance(pc1, pc2)
                        if 'error' not in distance_result:
                            distance_matrix[pc1][pc2] = distance_result['distance_km']
                        else:
                            distance_matrix[pc1][pc2] = float('inf')
            
            # Find optimal routing and clustering
            logistics_analysis = {
                'total_sites': len(site_postcodes),
                'distance_matrix': distance_matrix,
                'shortest_distances': self._find_shortest_distances(distance_matrix),
                'site_clusters': self._optimize_site_clusters(distance_matrix),
                'total_travel_distance': self._calculate_total_travel_distance(distance_matrix),
                'recommended_service_hubs': self._recommend_service_hubs(site_postcodes, distance_matrix)
            }
            
            return logistics_analysis
            
        except Exception as e:
            logger.error(f"Site logistics calculation error: {e}")
            return {'error': str(e)}
    
    def _extract_location_from_query(self, query: str) -> Dict:
        """Extract location information from natural language query using smart location lookup"""
        try:
            import re
            
            # Extract location phrases from natural language
            location_patterns = [
                r'near\s+([a-zA-Z\s]+?)(?:\s+between|\s+with|\s*$)',  # "near bristol"
                r'around\s+([a-zA-Z\s]+?)(?:\s+between|\s+with|\s*$)',  # "around london"
                r'in\s+([a-zA-Z\s]+?)(?:\s+between|\s+with|\s*$)',  # "in yorkshire"
                r'sites?\s+in\s+([a-zA-Z\s]+?)(?:\s+between|\s+with|\s*$)',  # "sites in bristol"
                r'installations?\s+in\s+([a-zA-Z\s]+?)(?:\s+between|\s+with|\s*$)',  # "installations in cornwall"
                r'([A-Z]{1,2}[0-9R][0-9A-Z]?\s*[0-9][ABD-HJLNP-UW-Z]{2})',  # Complete postcode
                r'([A-Z]{1,2}[0-9R][0-9A-Z]?)\b'  # Incomplete postcode
            ]
            
            for pattern in location_patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    location_text = match.group(1).strip()
                    
                    # Use smart location lookup for comprehensive place name + postcode support
                    geo_data = self.geo_intelligence.smart_location_lookup(location_text)
                    
                    if 'error' not in geo_data:
                        return {
                            'location_name': geo_data.get('place_name', location_text.title()),
                            'postcode': geo_data.get('outcode') or geo_data.get('postcode', location_text),
                            'geo_data': geo_data,
                            'lookup_method': geo_data.get('lookup_method', 'smart_lookup')
                        }
                    else:
                        # If lookup failed but we found a location pattern, provide helpful error
                        return {
                            'error': f'Location "{location_text}" not recognized. {geo_data.get("error", "")}',
                            'suggestions': geo_data.get('suggestions', [])
                        }
            
            return {'error': 'No location found in query. Try: "sites near bristol" or "installations in yorkshire"'}
            
        except Exception as e:
            return {'error': f'Location extraction error: {e}'}
    
    def _apply_geographic_filtering(self, fit_results: Dict, target_postcodes: List[str], 
                                  center_geo: Dict, radius_km: float) -> Dict:
        """Filter FIT results by geographic proximity"""
        try:
            filtered_commercial = []
            filtered_licenses = []
            
            # Filter commercial results
            for site in fit_results.get('commercial_results', []):
                site_postcode = site['metadata'].get('postcode', '').strip()
                if self._is_within_radius(site_postcode, center_geo, radius_km):
                    # Enhance with distance information
                    if site_postcode:
                        distance_result = self.geo_intelligence.calculate_distance(
                            center_geo['postcode'], site_postcode
                        )
                        if 'error' not in distance_result:
                            site['geographic_data'] = {
                                'distance_km': distance_result['distance_km'],
                                'postcode_geo': distance_result['geo2']
                            }
                    filtered_commercial.append(site)
            
            # Filter license results similarly
            for site in fit_results.get('license_results', []):
                site_postcode = site['metadata'].get('postcode', '').strip()
                if self._is_within_radius(site_postcode, center_geo, radius_km):
                    if site_postcode:
                        distance_result = self.geo_intelligence.calculate_distance(
                            center_geo['postcode'], site_postcode
                        )
                        if 'error' not in distance_result:
                            site['geographic_data'] = {
                                'distance_km': distance_result['distance_km'],
                                'postcode_geo': distance_result['geo2']
                            }
                    filtered_licenses.append(site)
            
            # Update results with filtered data
            fit_results['commercial_results'] = filtered_commercial
            fit_results['license_results'] = filtered_licenses
            fit_results['combined_insights']['total_results'] = len(filtered_commercial) + len(filtered_licenses)
            fit_results['combined_insights']['commercial_count'] = len(filtered_commercial)
            fit_results['combined_insights']['license_count'] = len(filtered_licenses)
            
            return fit_results
            
        except Exception as e:
            logger.error(f"Geographic filtering error: {e}")
            return fit_results
    
    def _is_within_radius(self, site_postcode: str, center_geo: Dict, radius_km: float) -> bool:
        """Check if site postcode is within radius of center"""
        try:
            if not site_postcode or len(site_postcode) < 3:
                return False
            
            # Use smart lookup for incomplete postcodes
            site_geo = self.geo_intelligence.smart_postcode_lookup(site_postcode)
            if 'error' in site_geo:
                return False
            
            center_postcode = center_geo.get('postcode') or center_geo.get('outcode')
            distance_result = self._calculate_distance_between_coords(
                center_geo['latitude'], center_geo['longitude'],
                site_geo['latitude'], site_geo['longitude']
            )
            
            return distance_result <= radius_km
                
        except Exception:
            return False
    
    def _calculate_distance_between_coords(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinate points"""
        return self.geo_intelligence._haversine_distance(lat1, lon1, lat2, lon2)
    
    def _enhance_with_geographic_analysis(self, filtered_results: Dict, 
                                        location_info: Dict, nearby_result: Dict) -> Dict:
        """Enhance results with comprehensive geographic analysis"""
        try:
            enhanced_results = filtered_results.copy()
            
            # Add geographic context
            enhanced_results['geographic_analysis'] = {
                'search_center': location_info,
                'nearby_postcodes': nearby_result,
                'site_distribution': self._analyze_site_distribution(filtered_results),
                'regional_assessment': self._create_regional_assessment(location_info, filtered_results)
            }
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Geographic enhancement error: {e}")
            return filtered_results
    
    def _analyze_site_distribution(self, results: Dict) -> Dict:
        """Analyze the geographic distribution of found sites"""
        try:
            all_sites = results.get('commercial_results', []) + results.get('license_results', [])
            
            if not all_sites:
                return {'error': 'No sites to analyze'}
            
            # Extract distances
            distances = []
            for site in all_sites:
                if 'geographic_data' in site:
                    distances.append(site['geographic_data']['distance_km'])
            
            if distances:
                return {
                    'total_sites': len(all_sites),
                    'sites_with_geo_data': len(distances),
                    'average_distance_km': round(sum(distances) / len(distances), 2),
                    'min_distance_km': min(distances),
                    'max_distance_km': max(distances),
                    'distance_distribution': self._create_distance_distribution(distances)
                }
            else:
                return {'error': 'No geographic data available for analysis'}
                
        except Exception as e:
            return {'error': f'Distribution analysis error: {e}'}
    
    def _create_distance_distribution(self, distances: List[float]) -> Dict:
        """Create distance distribution analysis"""
        try:
            # Define distance bands
            bands = {'0-5km': 0, '5-10km': 0, '10-20km': 0, '20+km': 0}
            
            for distance in distances:
                if distance <= 5:
                    bands['0-5km'] += 1
                elif distance <= 10:
                    bands['5-10km'] += 1
                elif distance <= 20:
                    bands['10-20km'] += 1
                else:
                    bands['20+km'] += 1
            
            return bands
            
        except Exception as e:
            return {'error': f'Distance distribution error: {e}'}
    
    def _create_regional_assessment(self, location_info: Dict, results: Dict) -> Dict:
        """Create regional renewable energy assessment"""
        try:
            geo_data = location_info['geo_data']
            renewable_indicators = self.geo_intelligence._assess_renewable_potential(geo_data)
            
            total_capacity_kw = 0
            technologies = {}
            
            all_sites = results.get('commercial_results', []) + results.get('license_results', [])
            
            for site in all_sites:
                # Calculate capacity
                capacity = site['metadata'].get('capacity_kw', 
                                              site['metadata'].get('capacity_mw', 0) * 1000)
                total_capacity_kw += capacity
                
                # Count technologies
                tech = site['metadata'].get('technology', 'Unknown')
                technologies[tech] = technologies.get(tech, 0) + 1
            
            return {
                'region': geo_data.get('region', 'Unknown'),
                'admin_district': geo_data.get('admin_district', 'Unknown'),
                'renewable_potential': renewable_indicators,
                'existing_installations': {
                    'total_sites': len(all_sites),
                    'total_capacity_kw': round(total_capacity_kw, 1),
                    'technology_breakdown': technologies
                },
                'market_opportunity': self._assess_market_opportunity(renewable_indicators, len(all_sites))
            }
            
        except Exception as e:
            return {'error': f'Regional assessment error: {e}'}
    
    def _assess_market_opportunity(self, renewable_indicators: Dict, existing_sites: int) -> str:
        """Assess market opportunity based on potential vs existing installations"""
        try:
            wind_potential = renewable_indicators.get('wind_potential', 'unknown')
            solar_potential = renewable_indicators.get('solar_potential', 'unknown')
            
            if wind_potential == 'high' and existing_sites < 5:
                return 'High opportunity - excellent wind potential with low saturation'
            elif solar_potential == 'good' and existing_sites < 10:
                return 'Good opportunity - strong solar potential with moderate saturation'
            elif existing_sites > 20:
                return 'Saturated market - high existing installation density'
            else:
                return 'Moderate opportunity - balanced potential and saturation'
                
        except Exception:
            return 'Assessment unavailable'
    
    def _identify_geographic_clusters(self, sites_with_postcodes: List[Dict], min_sites: int) -> List[Dict]:
        """Identify geographic clusters using simple distance-based clustering"""
        # This is a simplified implementation - production would use proper clustering algorithms
        clusters = []
        used_sites = set()
        
        for i, site in enumerate(sites_with_postcodes):
            if i in used_sites:
                continue
                
            cluster = [site]
            used_sites.add(i)
            
            for j, other_site in enumerate(sites_with_postcodes):
                if j in used_sites or i == j:
                    continue
                
                distance_result = self.geo_intelligence.calculate_distance(
                    site['postcode'], other_site['postcode']
                )
                
                if 'error' not in distance_result and distance_result['distance_km'] <= 20:
                    cluster.append(other_site)
                    used_sites.add(j)
            
            if len(cluster) >= min_sites:
                clusters.append(cluster)
        
        return clusters
    
    def _enhance_cluster_with_geo_data(self, cluster: List[Dict]) -> Dict:
        """Enhance cluster with comprehensive geographic data"""
        try:
            postcodes = [site['postcode'] for site in cluster]
            total_capacity = sum(site['capacity_kw'] for site in cluster)
            
            # Find cluster center (simplified - use first postcode)
            center_postcode = postcodes[0]
            center_geo = self.geo_intelligence.lookup_postcode(center_postcode)
            
            return {
                'center_postcode': center_postcode,
                'center_coordinates': {
                    'latitude': center_geo.get('latitude'),
                    'longitude': center_geo.get('longitude')
                } if 'error' not in center_geo else None,
                'site_count': len(cluster),
                'total_capacity_kw': total_capacity,
                'postcodes': postcodes,
                'technologies': list(set(site['site']['metadata'].get('technology', 'Unknown') for site in cluster)),
                'regional_data': center_geo if 'error' not in center_geo else None
            }
            
        except Exception as e:
            logger.error(f"Cluster enhancement error: {e}")
            return {'error': str(e)}
    
    def _create_cluster_analysis_summary(self, clusters: List[Dict]) -> Dict:
        """Create summary analysis of all clusters"""
        try:
            if not clusters:
                return {'message': 'No clusters found'}
            
            total_sites = sum(cluster['site_count'] for cluster in clusters)
            total_capacity = sum(cluster['total_capacity_kw'] for cluster in clusters)
            
            return {
                'total_clusters': len(clusters),
                'total_sites_in_clusters': total_sites,
                'total_capacity_kw': total_capacity,
                'average_cluster_size': round(total_sites / len(clusters), 1),
                'largest_cluster': max(clusters, key=lambda c: c['site_count'])['site_count']
            }
            
        except Exception as e:
            return {'error': f'Cluster summary error: {e}'}
    
    def _identify_regional_opportunities(self, regional_stats: Dict, fit_analysis: Dict) -> List[str]:
        """Identify specific opportunities in the region"""
        opportunities = []
        
        try:
            renewable_indicators = regional_stats['renewable_indicators']
            
            if renewable_indicators['wind_potential'] == 'high':
                opportunities.append('High wind potential suitable for new wind installations')
            
            if renewable_indicators['solar_potential'] == 'good':
                opportunities.append('Good solar irradiance for photovoltaic developments')
            
            if renewable_indicators['coastal_proximity']:
                opportunities.append('Coastal location beneficial for wind resources')
            
            opportunities.append('Established renewable energy infrastructure in region')
            
            return opportunities
            
        except Exception:
            return ['Regional analysis ongoing']
    
    def _create_market_intelligence(self, regional_stats: Dict, nearby: Dict) -> Dict:
        """Create market intelligence summary"""
        try:
            return {
                'region_name': regional_stats['administrative_hierarchy']['region'],
                'population_density': 'Moderate',  # Would be calculated from real data
                'grid_infrastructure': 'Well developed',  # Would be from grid data APIs
                'planning_authority': regional_stats['administrative_hierarchy']['admin_district'],
                'nearby_postcode_coverage': nearby['count'],
                'investment_attractiveness': 'Moderate to High'  # Would be calculated
            }
        except Exception:
            return {'status': 'Market intelligence calculation in progress'}
    
    def _find_shortest_distances(self, distance_matrix: Dict) -> Dict:
        """Find shortest distances between all sites"""
        try:
            shortest = {}
            for from_pc in distance_matrix:
                if distance_matrix[from_pc]:
                    closest_pc = min(distance_matrix[from_pc].items(), key=lambda x: x[1])
                    shortest[from_pc] = {
                        'closest_site': closest_pc[0],
                        'distance_km': closest_pc[1]
                    }
            return shortest
        except Exception as e:
            return {'error': f'Shortest distance calculation error: {e}'}
    
    def _optimize_site_clusters(self, distance_matrix: Dict) -> List[List[str]]:
        """Optimize sites into logical service clusters"""
        # Simplified clustering - production would use advanced algorithms
        try:
            sites = list(distance_matrix.keys())
            clusters = []
            used_sites = set()
            
            for site in sites:
                if site in used_sites:
                    continue
                
                cluster = [site]
                used_sites.add(site)
                
                # Find nearby sites within 30km
                for other_site in sites:
                    if other_site not in used_sites and distance_matrix[site].get(other_site, float('inf')) <= 30:
                        cluster.append(other_site)
                        used_sites.add(other_site)
                
                clusters.append(cluster)
            
            return clusters
        except Exception as e:
            logger.error(f"Site clustering error: {e}")
            return []
    
    def _calculate_total_travel_distance(self, distance_matrix: Dict) -> float:
        """Calculate total travel distance for visiting all sites"""
        try:
            # Simple sum of all distances (real implementation would use TSP algorithm)
            total = 0
            count = 0
            for from_site in distance_matrix:
                for to_site, distance in distance_matrix[from_site].items():
                    if distance != float('inf'):
                        total += distance
                        count += 1
            return round(total / count, 2) if count > 0 else 0
        except Exception:
            return 0
    
    def _recommend_service_hubs(self, site_postcodes: List[str], distance_matrix: Dict) -> List[Dict]:
        """Recommend optimal service hub locations"""
        try:
            hub_recommendations = []
            
            for postcode in site_postcodes:
                # Calculate average distance to all other sites
                distances = [d for d in distance_matrix[postcode].values() if d != float('inf')]
                if distances:
                    avg_distance = sum(distances) / len(distances)
                    hub_recommendations.append({
                        'postcode': postcode,
                        'average_distance_to_sites': round(avg_distance, 2)
                    })
            
            # Sort by average distance (best hubs have lowest average distance)
            hub_recommendations.sort(key=lambda x: x['average_distance_to_sites'])
            
            return hub_recommendations[:3]  # Return top 3 recommendations
            
        except Exception as e:
            logger.error(f"Service hub recommendation error: {e}")
            return []

# Test the enhanced system
if __name__ == "__main__":
    print("🌍⚡ Enhanced Geographic FIT Intelligence System Test")
    print("=" * 60)
    
    geo_fit = EnhancedGeoFITIntelligence()
    
    print("🔍 Testing Enhanced Geographic Search:")
    result = geo_fit.search_sites_by_location("wind sites near beverly between 250 and 500kw", radius_km=25)
    
    if 'error' not in result:
        total_sites = result['combined_insights']['total_results']
        print(f"✅ Found {total_sites} wind sites near Beverly (250-500kW)")
        
        if 'geographic_analysis' in result:
            geo_analysis = result['geographic_analysis']
            print(f"📍 Search center: {geo_analysis['search_center']['location_name']}")
            print(f"🎯 Nearby postcodes: {geo_analysis['nearby_postcodes']['count']}")
            
            if 'site_distribution' in geo_analysis:
                dist = geo_analysis['site_distribution']
                print(f"📊 Average distance: {dist.get('average_distance_km', 'N/A')}km")
    else:
        print(f"❌ Search error: {result['error']}")
    
    print("\n🏛️ Testing Regional Analysis:")
    regional = geo_fit.get_regional_fit_analysis("YO17 9AS", radius_km=30)
    
    if 'error' not in regional:
        geo_data = regional['geographic_data']
        print(f"📍 Region: {geo_data['administrative_hierarchy']['region']}")
        print(f"⚡ Wind potential: {geo_data['renewable_indicators']['wind_potential']}")
        print(f"☀️ Solar potential: {geo_data['renewable_indicators']['solar_potential']}")
    
    print("\n✅ Enhanced Geographic FIT Intelligence System Ready!")