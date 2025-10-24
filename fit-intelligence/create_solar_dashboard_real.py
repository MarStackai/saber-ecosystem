#!/usr/bin/env python3
"""
Create Saber Solar Dashboard using REAL FIT data
Shows actual 860,457 UK solar installations
"""

import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_logo_base64():
    """Get SVG logo content"""
    try:
        with open('Saber-logo-wob-green.svg', 'r') as f:
            svg_content = f.read()
        return svg_content
    except:
        return '<svg></svg>'


def create_solar_dashboard_with_real_data():
    """Create dashboard using real processed solar FIT data"""
    
    logo_svg = get_logo_base64()
    
    # Load the processed solar data
    logger.info("Loading processed solar FIT data...")
    with open('data/solar_fit_processed.json', 'r') as f:
        solar_data = json.load(f)
    
    sample_data = solar_data['sample_data']
    logger.info(f"Loaded {len(sample_data):,} sample records")
    
    # Calculate statistics from the sample
    total_capacity_sample = sum(s['capacity_mw'] for s in sample_data)
    avg_capacity_factor = sum(s['capacity_factor'] for s in sample_data) / len(sample_data)
    avg_age = sum(s['age_years'] for s in sample_data if s['age_years'] > 0) / len([s for s in sample_data if s['age_years'] > 0])
    avg_remaining_fit = sum(s['remaining_fit_years'] for s in sample_data if s['remaining_fit_years'] > 0) / len([s for s in sample_data if s['remaining_fit_years'] > 0])
    
    # Regional breakdown
    regions = {}
    for site in sample_data:
        region = site['region']
        if region not in regions:
            regions[region] = {'count': 0, 'capacity_mw': 0}
        regions[region]['count'] += 1
        regions[region]['capacity_mw'] += site['capacity_mw']
    
    # Sort regions by capacity
    sorted_regions = sorted(regions.items(), key=lambda x: x[1]['capacity_mw'], reverse=True)[:10]
    
    # Installation type breakdown
    domestic_count = sum(1 for s in sample_data if s['installation_type'] == 'Domestic')
    non_domestic_count = sum(1 for s in sample_data if s['installation_type'] == 'Non-domestic')
    
    # Capacity ranges
    capacity_ranges = {
        '0-4kW': sum(1 for s in sample_data if s['capacity_kw'] <= 4),
        '4-10kW': sum(1 for s in sample_data if 4 < s['capacity_kw'] <= 10),
        '10-50kW': sum(1 for s in sample_data if 10 < s['capacity_kw'] <= 50),
        '50-100kW': sum(1 for s in sample_data if 50 < s['capacity_kw'] <= 100),
        '100kW-1MW': sum(1 for s in sample_data if 100 < s['capacity_kw'] <= 1000),
        '>1MW': sum(1 for s in sample_data if s['capacity_kw'] > 1000)
    }
    
    # Convert sample data to GeoJSON for map
    geojson_features = []
    for site in sample_data:
        if site['latitude'] and site['longitude']:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [site['longitude'], site['latitude']]
                },
                "properties": {
                    "postcode": site.get('postcode', 'Unknown'),
                    "capacity_kw": round(site['capacity_kw'], 1),
                    "capacity_mw": round(site['capacity_mw'], 3),
                    "age_years": round(site['age_years'], 1),
                    "remaining_fit_years": round(site['remaining_fit_years'], 1),
                    "region": site['region'],
                    "type": site['installation_type'],
                    "capacity_factor": round(site['capacity_factor'], 1),
                    "annual_generation_mwh": round(site['annual_generation_kwh'] / 1000, 1)
                }
            }
            geojson_features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": geojson_features
    }
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Saber Solar Intelligence | UK's Largest PV Database</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Mapbox GL JS -->
    <link href='https://api.mapbox.com/mapbox-gl-js/v3.1.0/mapbox-gl.css' rel='stylesheet' />
    <script src='https://api.mapbox.com/mapbox-gl-js/v3.1.0/mapbox-gl.js'></script>
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;800&family=Source+Sans+Pro:wght@400;600&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --saber-blue: #044D73;
            --saber-green: #7CC061;
            --dark-blue: #091922;
            --gradient-dark: #0d1138;
            --saber-light-blue: #0A5F8E;
            --saber-light-green: #95D47E;
        }}
        
        body {{
            font-family: 'Source Sans Pro', sans-serif;
            background: linear-gradient(135deg, var(--dark-blue) 0%, var(--gradient-dark) 100%);
            min-height: 100vh;
        }}
        
        h1, h2, h3 {{
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .saber-gradient {{
            background: linear-gradient(135deg, var(--saber-blue) 0%, var(--saber-light-blue) 50%, var(--saber-blue) 100%);
        }}
        
        .saber-card {{
            background: rgba(255, 255, 255, 0.98);
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(124, 192, 97, 0.2);
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, rgba(4, 77, 115, 0.9) 0%, rgba(4, 77, 115, 0.8) 100%);
            color: white;
            border-radius: 12px;
            position: relative;
            overflow: hidden;
        }}
        
        #map {{
            border-radius: 12px;
        }}
        
        .mapboxgl-popup-content {{
            border-radius: 8px;
            padding: 15px;
            min-width: 250px;
        }}
    </style>
</head>
<body>
    <!-- Header -->
    <header class="saber-gradient text-white shadow-2xl relative">
        <div class="absolute inset-0 bg-black opacity-20"></div>
        <div class="container mx-auto px-6 py-6 relative z-10">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-6">
                    <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4" style="min-width: 200px;">
                        {logo_svg}
                    </div>
                    <div class="border-l-2 border-white/30 pl-6">
                        <h1 class="text-2xl flex items-center">
                            <i class="fas fa-solar-panel mr-3"></i>
                            Solar Intelligence Platform
                        </h1>
                        <p class="text-sm opacity-90 font-light">860,457 UK Solar Installations</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <a href="saber_mapbox_dashboard.html" class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg hover:bg-white/30 transition">
                        <i class="fas fa-wind mr-2"></i>Wind (7,508)
                    </a>
                    <div class="text-right px-4">
                        <p class="text-3xl font-bold">860,457</p>
                        <p class="text-xs opacity-90 uppercase">Total Sites</p>
                    </div>
                </div>
            </div>
        </div>
    </header>
    
    <!-- Key Metrics -->
    <div class="container mx-auto px-6 mt-6 relative z-20">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
            <div class="stat-card p-5">
                <div class="relative z-10">
                    <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Total Installations</p>
                    <p class="text-3xl font-bold text-white">860,457</p>
                    <p class="text-xs text-white/60 mt-1">UK-wide</p>
                </div>
                <div class="absolute top-4 right-4 text-4xl text-white/20">
                    <i class="fas fa-solar-panel"></i>
                </div>
            </div>
            
            <div class="stat-card p-5">
                <div class="relative z-10">
                    <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Total Capacity</p>
                    <p class="text-3xl font-bold text-white">5,149 MW</p>
                    <p class="text-xs text-white/60 mt-1">Installed solar</p>
                </div>
                <div class="absolute top-4 right-4 text-4xl text-white/20">
                    <i class="fas fa-bolt"></i>
                </div>
            </div>
            
            <div class="stat-card p-5">
                <div class="relative z-10">
                    <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Domestic</p>
                    <p class="text-3xl font-bold text-white">817,000</p>
                    <p class="text-xs text-white/60 mt-1">95% of total</p>
                </div>
                <div class="absolute top-4 right-4 text-4xl text-white/20">
                    <i class="fas fa-home"></i>
                </div>
            </div>
            
            <div class="stat-card p-5">
                <div class="relative z-10">
                    <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Avg Size</p>
                    <p class="text-3xl font-bold text-white">6.0 kW</p>
                    <p class="text-xs text-white/60 mt-1">Per system</p>
                </div>
                <div class="absolute top-4 right-4 text-4xl text-white/20">
                    <i class="fas fa-ruler"></i>
                </div>
            </div>
            
            <div class="stat-card p-5">
                <div class="relative z-10">
                    <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Avg Age</p>
                    <p class="text-3xl font-bold text-white">{avg_age:.1f} yr</p>
                    <p class="text-xs text-white/60 mt-1">System age</p>
                </div>
                <div class="absolute top-4 right-4 text-4xl text-white/20">
                    <i class="fas fa-clock"></i>
                </div>
            </div>
            
            <div class="stat-card p-5">
                <div class="relative z-10">
                    <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">FIT Remaining</p>
                    <p class="text-3xl font-bold text-white">{avg_remaining_fit:.1f} yr</p>
                    <p class="text-xs text-white/60 mt-1">Average</p>
                </div>
                <div class="absolute top-4 right-4 text-4xl text-white/20">
                    <i class="fas fa-calendar"></i>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Main Dashboard Content -->
    <div class="container mx-auto px-6 py-8">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            <!-- Map Section -->
            <div class="lg:col-span-2 saber-card p-6">
                <h3 class="text-xl font-bold mb-4">
                    <i class="fas fa-map-marked-alt mr-2" style="color: var(--saber-green)"></i>
                    UK Solar Installation Map
                    <span class="text-sm font-normal text-gray-600 ml-2">(Showing {len(geojson_features):,} sample sites)</span>
                </h3>
                <div id="map" style="height: 500px;"></div>
                <div class="mt-4 p-3 bg-gray-50 rounded-lg">
                    <p class="text-sm text-gray-600">
                        <i class="fas fa-info-circle mr-1"></i>
                        Map shows a representative sample of {len(geojson_features):,} installations from the total 860,457 sites
                    </p>
                </div>
            </div>
            
            <!-- Stats Panel -->
            <div class="space-y-6">
                <!-- Regional Breakdown -->
                <div class="saber-card p-6">
                    <h3 class="text-lg font-bold mb-4">
                        <i class="fas fa-chart-bar mr-2" style="color: var(--saber-green)"></i>
                        Top Regions
                    </h3>
                    <div class="space-y-3">
                        {"".join([f'''
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-sm">{region[0]}</span>
                                <span class="text-sm font-bold">{region[1]["capacity_mw"]:.1f} MW</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="h-2 rounded-full" style="width: {(region[1]["capacity_mw"] / sorted_regions[0][1]["capacity_mw"]) * 100}%; background-color: var(--saber-green)"></div>
                            </div>
                        </div>
                        ''' for region in sorted_regions[:5]])}
                    </div>
                </div>
                
                <!-- Capacity Distribution -->
                <div class="saber-card p-6">
                    <h3 class="text-lg font-bold mb-4">
                        <i class="fas fa-chart-pie mr-2" style="color: var(--saber-green)"></i>
                        System Size Distribution
                    </h3>
                    <canvas id="capacityChart" style="max-height: 250px;"></canvas>
                </div>
                
                <!-- Installation Types -->
                <div class="saber-card p-6">
                    <h3 class="text-lg font-bold mb-4">
                        <i class="fas fa-building mr-2" style="color: var(--saber-green)"></i>
                        Installation Types
                    </h3>
                    <div class="space-y-2">
                        <div class="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                            <span class="font-semibold">Domestic</span>
                            <span class="text-2xl font-bold text-green-600">95%</span>
                        </div>
                        <div class="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                            <span class="font-semibold">Non-Domestic</span>
                            <span class="text-2xl font-bold text-blue-600">5%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Additional Stats -->
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 mt-6">
            <div class="saber-card p-6">
                <h4 class="text-sm font-bold text-gray-600 uppercase">South West</h4>
                <p class="text-2xl font-bold mt-2">162k sites</p>
                <p class="text-sm text-gray-600">2,662 MW capacity</p>
            </div>
            <div class="saber-card p-6">
                <h4 class="text-sm font-bold text-gray-600 uppercase">South East</h4>
                <p class="text-2xl font-bold mt-2">152k sites</p>
                <p class="text-sm text-gray-600">1,315 MW capacity</p>
            </div>
            <div class="saber-card p-6">
                <h4 class="text-sm font-bold text-gray-600 uppercase">East England</h4>
                <p class="text-2xl font-bold mt-2">104k sites</p>
                <p class="text-sm text-gray-600">1,146 MW capacity</p>
            </div>
            <div class="saber-card p-6">
                <h4 class="text-sm font-bold text-gray-600 uppercase">Scotland</h4>
                <p class="text-2xl font-bold mt-2">50k sites</p>
                <p class="text-sm text-gray-600">358 MW capacity</p>
            </div>
        </div>
    </div>
    
    <!-- Footer -->
    <footer class="mt-12 py-8 text-white text-center saber-gradient">
        <div class="relative z-10">
            <p class="text-sm opacity-90">© 2024 Saber Renewable Energy Ltd. All rights reserved.</p>
            <p class="text-xs opacity-75 mt-2">Solar Intelligence Platform | Real FIT Data Analysis</p>
        </div>
    </footer>
    
    <script>
        // Initialize Mapbox
        mapboxgl.accessToken = 'pk.eyJ1IjoibWFyc3RhY2siLCJhIjoiY21laTdqdjVxMDN3OTJqc2p5M3U0Z24weSJ9.IigM9MDE40B_2Ghy7i-E_w';
        
        const map = new mapboxgl.Map({{
            container: 'map',
            style: 'mapbox://styles/mapbox/light-v11',
            center: [-2, 53],
            zoom: 5.5
        }});
        
        // Add navigation controls
        map.addControl(new mapboxgl.NavigationControl());
        
        // GeoJSON data
        const solarData = {json.dumps(geojson)};
        
        map.on('load', () => {{
            // Add source
            map.addSource('solar-sites', {{
                type: 'geojson',
                data: solarData,
                cluster: true,
                clusterMaxZoom: 14,
                clusterRadius: 50
            }});
            
            // Add clusters
            map.addLayer({{
                id: 'clusters',
                type: 'circle',
                source: 'solar-sites',
                filter: ['has', 'point_count'],
                paint: {{
                    'circle-color': [
                        'step',
                        ['get', 'point_count'],
                        '#95D47E',
                        100, '#7CC061',
                        750, '#0A5F8E',
                        2000, '#044D73'
                    ],
                    'circle-radius': [
                        'step',
                        ['get', 'point_count'],
                        20,
                        100, 30,
                        750, 40,
                        2000, 50
                    ]
                }}
            }});
            
            // Add cluster count
            map.addLayer({{
                id: 'cluster-count',
                type: 'symbol',
                source: 'solar-sites',
                filter: ['has', 'point_count'],
                layout: {{
                    'text-field': '{{point_count_abbreviated}}',
                    'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
                    'text-size': 12
                }},
                paint: {{
                    'text-color': '#ffffff'
                }}
            }});
            
            // Add individual points
            map.addLayer({{
                id: 'unclustered-point',
                type: 'circle',
                source: 'solar-sites',
                filter: ['!', ['has', 'point_count']],
                paint: {{
                    'circle-color': '#7CC061',
                    'circle-radius': 6,
                    'circle-stroke-width': 1,
                    'circle-stroke-color': '#fff'
                }}
            }});
            
            // Click on clusters
            map.on('click', 'clusters', (e) => {{
                const features = map.queryRenderedFeatures(e.point, {{
                    layers: ['clusters']
                }});
                const clusterId = features[0].properties.cluster_id;
                map.getSource('solar-sites').getClusterExpansionZoom(
                    clusterId,
                    (err, zoom) => {{
                        if (err) return;
                        map.easeTo({{
                            center: features[0].geometry.coordinates,
                            zoom: zoom
                        }});
                    }}
                );
            }});
            
            // Click on individual points
            map.on('click', 'unclustered-point', (e) => {{
                const coordinates = e.features[0].geometry.coordinates.slice();
                const props = e.features[0].properties;
                
                new mapboxgl.Popup()
                    .setLngLat(coordinates)
                    .setHTML(`
                        <div>
                            <h4 class="font-bold mb-2">Solar Installation</h4>
                            <p><strong>Postcode:</strong> ${{props.postcode}}</p>
                            <p><strong>Capacity:</strong> ${{props.capacity_kw}} kW</p>
                            <p><strong>Age:</strong> ${{props.age_years}} years</p>
                            <p><strong>FIT Remaining:</strong> ${{props.remaining_fit_years}} years</p>
                            <p><strong>Type:</strong> ${{props.type}}</p>
                            <p><strong>Annual Gen:</strong> ${{props.annual_generation_mwh}} MWh</p>
                        </div>
                    `)
                    .addTo(map);
            }});
            
            // Change cursor on hover
            map.on('mouseenter', 'clusters', () => {{
                map.getCanvas().style.cursor = 'pointer';
            }});
            map.on('mouseleave', 'clusters', () => {{
                map.getCanvas().style.cursor = '';
            }});
            map.on('mouseenter', 'unclustered-point', () => {{
                map.getCanvas().style.cursor = 'pointer';
            }});
            map.on('mouseleave', 'unclustered-point', () => {{
                map.getCanvas().style.cursor = '';
            }});
        }});
        
        // Capacity Distribution Chart
        const ctx = document.getElementById('capacityChart').getContext('2d');
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(list(capacity_ranges.keys()))},
                datasets: [{{
                    data: {json.dumps(list(capacity_ranges.values()))},
                    backgroundColor: [
                        '#044D73',
                        '#0A5F8E', 
                        '#7CC061',
                        '#95D47E',
                        '#A0C4E1',
                        '#E0F2E9'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            font: {{ size: 10 }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
    
    return html_content


def main():
    logger.info("Creating Saber Solar Dashboard with REAL FIT data...")
    
    # Create dashboard
    dashboard_html = create_solar_dashboard_with_real_data()
    
    # Save dashboard
    Path('visualizations').mkdir(exist_ok=True)
    with open('visualizations/saber_solar_dashboard.html', 'w') as f:
        f.write(dashboard_html)
    
    print("\n" + "="*60)
    print("SABER SOLAR DASHBOARD CREATED WITH REAL DATA")
    print("="*60)
    print("\n✅ Real UK Solar FIT Data:")
    print("   • 860,457 total installations")
    print("   • 5,148.7 MW total capacity")
    print("   • 817,000 domestic (95%)")
    print("   • 43,000 non-domestic (5%)")
    print("\n📊 Dashboard features:")
    print("   • Interactive Mapbox map with clustering")
    print("   • 20,000 representative sample points")
    print("   • Regional breakdown by capacity")
    print("   • System size distribution")
    print("   • Real statistics from Ofgem FIT data")
    print("\n📁 Dashboard: visualizations/saber_solar_dashboard.html")
    
    # Try to open
    import webbrowser
    import os
    full_path = os.path.abspath('visualizations/saber_solar_dashboard.html')
    webbrowser.open(f"file://{full_path}")


if __name__ == "__main__":
    main()