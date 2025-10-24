#!/usr/bin/env python3
"""
Create Saber Commercial Solar Dashboard
Focus on 35,617 commercial/industrial installations only - no domestic bloat
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
            return f.read()
    except:
        return '<svg></svg>'


def create_commercial_solar_dashboard():
    """Create dashboard for commercial solar only"""
    
    logo_svg = get_logo_base64()
    
    # Load commercial solar data
    with open('data/commercial_solar_fit.json', 'r') as f:
        data = json.load(f)
    
    sites = data['sites']
    stats = data['summary_stats']
    size_dist = data['size_distribution']
    repowering = data['repowering_windows']
    regional = data['regional_breakdown']
    
    logger.info(f"Creating dashboard for {len(sites):,} commercial solar sites")
    
    # Create GeoJSON
    geojson_features = []
    for site in sites:
        if site['latitude'] and site['longitude']:
            # Color based on repowering window
            color_map = {
                'IMMEDIATE': '#E74C3C',  # Red
                'URGENT': '#F39C12',     # Orange
                'OPTIMAL': '#7CC061',    # Green
                'PLANNING': '#0A5F8E',   # Blue
                'FUTURE': '#95D47E'      # Light green
            }
            
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
                    "size_category": site['size_category'],
                    "repowering_window": site['repowering_window'],
                    "annual_generation_mwh": round(site['annual_generation_mwh'], 1),
                    "color": color_map.get(site['repowering_window'], '#999999')
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
    <title>Saber Commercial Solar Intelligence | 35,617 C&I Sites</title>
    
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
        
        .window-immediate {{ background-color: #E74C3C; }}
        .window-urgent {{ background-color: #F39C12; }}
        .window-optimal {{ background-color: #7CC061; }}
        .window-planning {{ background-color: #0A5F8E; }}
        .window-future {{ background-color: #95D47E; }}
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
                            Commercial Solar Intelligence
                        </h1>
                        <p class="text-sm opacity-90 font-light">35,617 C&I Installations | No Domestic</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <a href="saber_mapbox_dashboard.html" class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg hover:bg-white/30 transition">
                        <i class="fas fa-wind mr-2"></i>Wind
                    </a>
                    <div class="text-right px-4">
                        <p class="text-3xl font-bold">2,244 MW</p>
                        <p class="text-xs opacity-90 uppercase">Commercial Only</p>
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
                    <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">C&I Sites</p>
                    <p class="text-3xl font-bold text-white">{stats['total_sites']:,}</p>
                    <p class="text-xs text-white/60 mt-1">Commercial only</p>
                </div>
                <div class="absolute top-4 right-4 text-4xl text-white/20">
                    <i class="fas fa-building"></i>
                </div>
            </div>
            
            <div class="stat-card p-5">
                <div class="relative z-10">
                    <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Total Capacity</p>
                    <p class="text-3xl font-bold text-white">{stats['total_capacity_mw']:,.0f} MW</p>
                    <p class="text-xs text-white/60 mt-1">Commercial solar</p>
                </div>
                <div class="absolute top-4 right-4 text-4xl text-white/20">
                    <i class="fas fa-bolt"></i>
                </div>
            </div>
            
            <div class="stat-card p-5">
                <div class="relative z-10">
                    <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Sites ≥100kW</p>
                    <p class="text-3xl font-bold text-white">{stats['sites_over_100kw']:,}</p>
                    <p class="text-xs text-white/60 mt-1">Large scale</p>
                </div>
                <div class="absolute top-4 right-4 text-4xl text-white/20">
                    <i class="fas fa-industry"></i>
                </div>
            </div>
            
            <div class="stat-card p-5">
                <div class="relative z-10">
                    <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Sites ≥1MW</p>
                    <p class="text-3xl font-bold text-white">{stats['sites_over_1mw']}</p>
                    <p class="text-xs text-white/60 mt-1">Utility scale</p>
                </div>
                <div class="absolute top-4 right-4 text-4xl text-white/20">
                    <i class="fas fa-chart-line"></i>
                </div>
            </div>
            
            <div class="stat-card p-5">
                <div class="relative z-10">
                    <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Avg Size</p>
                    <p class="text-3xl font-bold text-white">{stats['average_capacity_kw']:.0f} kW</p>
                    <p class="text-xs text-white/60 mt-1">Per system</p>
                </div>
                <div class="absolute top-4 right-4 text-4xl text-white/20">
                    <i class="fas fa-ruler"></i>
                </div>
            </div>
            
            <div class="stat-card p-5">
                <div class="relative z-10">
                    <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">FIT Remaining</p>
                    <p class="text-3xl font-bold text-white">{stats['average_remaining_fit']:.1f} yr</p>
                    <p class="text-xs text-white/60 mt-1">Average</p>
                </div>
                <div class="absolute top-4 right-4 text-4xl text-white/20">
                    <i class="fas fa-calendar"></i>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Main Dashboard -->
    <div class="container mx-auto px-6 py-8">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            <!-- Map Section -->
            <div class="lg:col-span-2 saber-card p-6 flex flex-col" style="height: calc(100vh - 400px); min-height: 600px;">
                <h3 class="text-xl font-bold mb-4">
                    <i class="fas fa-map-marked-alt mr-2" style="color: var(--saber-green)"></i>
                    Commercial Solar Sites by Repowering Window
                </h3>
                
                <!-- Filter Buttons -->
                <div class="flex flex-wrap gap-2 mb-4">
                    <button onclick="filterByWindow('all')" class="filter-btn px-3 py-1 bg-gray-700 text-white rounded-lg text-sm">
                        All Sites ({len(sites):,})
                    </button>
                    <button onclick="filterByWindow('IMMEDIATE')" class="filter-btn px-3 py-1 window-immediate text-white rounded-lg text-sm opacity-60">
                        Immediate ({repowering.get('IMMEDIATE', 0)})
                    </button>
                    <button onclick="filterByWindow('URGENT')" class="filter-btn px-3 py-1 window-urgent text-white rounded-lg text-sm opacity-60">
                        Urgent ({repowering.get('URGENT', 0)})
                    </button>
                    <button onclick="filterByWindow('OPTIMAL')" class="filter-btn px-3 py-1 window-optimal text-white rounded-lg text-sm opacity-60">
                        Optimal ({repowering.get('OPTIMAL', 0):,})
                    </button>
                    <button onclick="filterByWindow('PLANNING')" class="filter-btn px-3 py-1 window-planning text-white rounded-lg text-sm opacity-60">
                        Planning ({repowering.get('PLANNING', 0):,})
                    </button>
                </div>
                
                <div id="map" class="flex-grow" style="min-height: 500px;"></div>
                
                <!-- Legend -->
                <div class="mt-4 p-3 bg-gray-50 rounded-lg">
                    <div class="grid grid-cols-2 lg:grid-cols-5 gap-2 text-xs">
                        <div class="flex items-center">
                            <span class="w-3 h-3 rounded-full mr-2 window-immediate"></span>
                            <span>Immediate (<2yr FIT)</span>
                        </div>
                        <div class="flex items-center">
                            <span class="w-3 h-3 rounded-full mr-2 window-urgent"></span>
                            <span>Urgent (2-5yr FIT)</span>
                        </div>
                        <div class="flex items-center">
                            <span class="w-3 h-3 rounded-full mr-2 window-optimal"></span>
                            <span>Optimal (5-10yr FIT)</span>
                        </div>
                        <div class="flex items-center">
                            <span class="w-3 h-3 rounded-full mr-2 window-planning"></span>
                            <span>Planning (10-15yr FIT)</span>
                        </div>
                        <div class="flex items-center">
                            <span class="w-3 h-3 rounded-full mr-2 window-future"></span>
                            <span>Future (>15yr FIT)</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Stats Panel -->
            <div class="space-y-6">
                <!-- Filters Panel -->
                <div class="saber-card p-6">
                    <h3 class="text-lg font-bold mb-4">
                        <i class="fas fa-sliders-h mr-2" style="color: var(--saber-green)"></i>
                        Filters
                    </h3>
                    <div class="space-y-4">
                        <div>
                            <label class="text-sm text-gray-600 font-semibold">Capacity Range (kW)</label>
                            <div class="flex items-center space-x-2 mt-2">
                                <input type="number" id="minCapacity" placeholder="Min" 
                                       class="w-24 px-2 py-1 border rounded text-sm" value="0">
                                <span class="text-gray-500">-</span>
                                <input type="number" id="maxCapacity" placeholder="Max" 
                                       class="w-24 px-2 py-1 border rounded text-sm" value="50000">
                            </div>
                            <button onclick="applyCapacityFilter()" 
                                    class="mt-2 px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700">
                                Apply
                            </button>
                        </div>
                        <div>
                            <label class="text-sm text-gray-600 font-semibold">FIT Years Remaining</label>
                            <input type="range" id="fitSlider" min="0" max="20" step="0.5" value="20" 
                                   class="w-full mt-2" oninput="updateFitFilter(this.value)">
                            <div class="flex justify-between text-xs text-gray-500">
                                <span>0 yr</span>
                                <span id="fitValue" class="font-semibold">Max: 20 yr</span>
                                <span>20 yr</span>
                            </div>
                        </div>
                        <div>
                            <label class="text-sm text-gray-600 font-semibold">Size Category</label>
                            <div class="space-y-1 mt-2">
                                <label class="flex items-center text-xs">
                                    <input type="checkbox" class="size-filter mr-2" value="Small (10-50kW)" checked>
                                    Small (10-50kW)
                                </label>
                                <label class="flex items-center text-xs">
                                    <input type="checkbox" class="size-filter mr-2" value="Medium (50-250kW)" checked>
                                    Medium (50-250kW)
                                </label>
                                <label class="flex items-center text-xs">
                                    <input type="checkbox" class="size-filter mr-2" value="Large (250kW-1MW)" checked>
                                    Large (250kW-1MW)
                                </label>
                                <label class="flex items-center text-xs">
                                    <input type="checkbox" class="size-filter mr-2" value="Utility (1-5MW)" checked>
                                    Utility (>1MW)
                                </label>
                            </div>
                        </div>
                        <button onclick="resetFilters()" 
                                class="w-full px-3 py-1 bg-gray-500 text-white rounded text-sm hover:bg-gray-600">
                            Reset All Filters
                        </button>
                    </div>
                </div>
                
                <!-- Repowering Opportunities -->
                <div class="saber-card p-6">
                    <h3 class="text-lg font-bold mb-4">
                        <i class="fas fa-exclamation-triangle mr-2" style="color: var(--saber-green)"></i>
                        Repowering Pipeline
                    </h3>
                    <div class="space-y-3">
                        <div class="p-3 bg-red-50 rounded-lg border-l-4 border-red-500">
                            <div class="flex justify-between items-center">
                                <span class="font-semibold">Immediate Action</span>
                                <span class="text-xl font-bold">{repowering.get('IMMEDIATE', 0)}</span>
                            </div>
                            <p class="text-xs text-gray-600 mt-1">FIT expiring <2 years</p>
                        </div>
                        <div class="p-3 bg-orange-50 rounded-lg border-l-4 border-orange-500">
                            <div class="flex justify-between items-center">
                                <span class="font-semibold">Urgent</span>
                                <span class="text-xl font-bold">{repowering.get('URGENT', 0)}</span>
                            </div>
                            <p class="text-xs text-gray-600 mt-1">2-5 years remaining</p>
                        </div>
                        <div class="p-3 bg-green-50 rounded-lg border-l-4 border-green-500">
                            <div class="flex justify-between items-center">
                                <span class="font-semibold">Optimal Window</span>
                                <span class="text-xl font-bold">{repowering.get('OPTIMAL', 0):,}</span>
                            </div>
                            <p class="text-xs text-gray-600 mt-1">5-10 years - plan now</p>
                        </div>
                    </div>
                </div>
                
                <!-- Size Distribution -->
                <div class="saber-card p-6">
                    <h3 class="text-lg font-bold mb-4">
                        <i class="fas fa-chart-pie mr-2" style="color: var(--saber-green)"></i>
                        Size Distribution
                    </h3>
                    <canvas id="sizeChart" style="max-height: 250px;"></canvas>
                </div>
                
                <!-- Top Regions -->
                <div class="saber-card p-6">
                    <h3 class="text-lg font-bold mb-4">
                        <i class="fas fa-map mr-2" style="color: var(--saber-green)"></i>
                        Top Regions (MW)
                    </h3>
                    <div class="space-y-2">
                        <div class="flex justify-between items-center">
                            <span class="text-sm">South West</span>
                            <span class="font-bold">603 MW</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-sm">South East</span>
                            <span class="font-bold">301 MW</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-sm">East England</span>
                            <span class="font-bold">234 MW</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-sm">East Midlands</span>
                            <span class="font-bold">227 MW</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-sm">West Midlands</span>
                            <span class="font-bold">193 MW</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Bottom Stats -->
        <div class="grid grid-cols-1 lg:grid-cols-5 gap-6 mt-6">
            <div class="saber-card p-6 text-center">
                <p class="text-3xl font-bold text-green-600">23,097</p>
                <p class="text-sm text-gray-600 mt-1">Optimal Window Sites</p>
                <p class="text-xs text-gray-500">1,098 MW capacity</p>
            </div>
            <div class="saber-card p-6 text-center">
                <p class="text-3xl font-bold text-blue-600">11,871</p>
                <p class="text-sm text-gray-600 mt-1">Planning Phase Sites</p>
                <p class="text-xs text-gray-500">1,139 MW capacity</p>
            </div>
            <div class="saber-card p-6 text-center">
                <p class="text-3xl font-bold text-orange-600">4,445</p>
                <p class="text-sm text-gray-600 mt-1">50-250kW Sites</p>
                <p class="text-xs text-gray-500">Medium commercial</p>
            </div>
            <div class="saber-card p-6 text-center">
                <p class="text-3xl font-bold text-purple-600">649</p>
                <p class="text-sm text-gray-600 mt-1">Large Scale (>250kW)</p>
                <p class="text-xs text-gray-500">1,286 MW total</p>
            </div>
            <div class="saber-card p-6 text-center">
                <p class="text-3xl font-bold text-red-600">603</p>
                <p class="text-sm text-gray-600 mt-1">Immediate + Urgent</p>
                <p class="text-xs text-gray-500">5.3 MW ready now</p>
            </div>
        </div>
    </div>
    
    <!-- Footer -->
    <footer class="mt-12 py-8 text-white text-center saber-gradient">
        <div class="relative z-10">
            <p class="text-sm opacity-90">© 2024 Saber Renewable Energy Ltd. All rights reserved.</p>
            <p class="text-xs opacity-75 mt-2">Commercial Solar Intelligence | 35,617 C&I Sites | Zero Domestic</p>
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
        
        map.addControl(new mapboxgl.NavigationControl());
        
        // GeoJSON data
        const solarData = {json.dumps(geojson)};
        let currentFilter = 'all';
        
        map.on('load', () => {{
            // Add source with better clustering settings
            map.addSource('solar-sites', {{
                type: 'geojson',
                data: solarData,
                cluster: true,
                clusterMaxZoom: 16,  // Allow clustering up to higher zoom
                clusterRadius: 30,    // Smaller radius for less aggressive clustering
                clusterProperties: {{
                    // Calculate totals for cluster tooltips
                    'total_capacity_mw': ['+', ['get', 'capacity_mw']],
                    'avg_fit_years': ['+', ['get', 'remaining_fit_years']]
                }}
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
                        500, '#0A5F8E',
                        1000, '#044D73'
                    ],
                    'circle-radius': [
                        'step',
                        ['get', 'point_count'],
                        20, 100, 30,
                        500, 40, 1000, 50
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
            
            // Add individual points with colors based on repowering window
            map.addLayer({{
                id: 'unclustered-point',
                type: 'circle',
                source: 'solar-sites',
                filter: ['!', ['has', 'point_count']],
                paint: {{
                    'circle-color': ['get', 'color'],
                    'circle-radius': [
                        'interpolate',
                        ['linear'],
                        ['get', 'capacity_kw'],
                        0, 4,
                        100, 8,
                        1000, 12,
                        5000, 16
                    ],
                    'circle-stroke-width': 1,
                    'circle-stroke-color': '#fff'
                }}
            }});
            
            // Click handlers with improved tooltips
            map.on('click', 'clusters', (e) => {{
                const features = map.queryRenderedFeatures(e.point, {{
                    layers: ['clusters']
                }});
                const props = features[0].properties;
                const clusterId = props.cluster_id;
                const count = props.point_count;
                const totalCapacity = props.total_capacity_mw;
                const avgFit = props.avg_fit_years / count;
                
                // Show cluster tooltip
                new mapboxgl.Popup()
                    .setLngLat(features[0].geometry.coordinates)
                    .setHTML(`
                        <div class="p-2">
                            <h4 class="font-bold text-lg mb-2">Cluster Summary</h4>
                            <p><strong>Sites:</strong> ${{count}}</p>
                            <p><strong>Total Capacity:</strong> ${{totalCapacity ? totalCapacity.toFixed(1) : 'N/A'}} MW</p>
                            <p><strong>Avg FIT Remaining:</strong> ${{avgFit ? avgFit.toFixed(1) : 'N/A'}} years</p>
                            <button onclick="zoomToCluster(${{clusterId}})" 
                                    class="mt-2 px-3 py-1 bg-blue-500 text-white rounded text-xs">
                                Zoom In
                            </button>
                        </div>
                    `)
                    .addTo(map);
            }});
            
            map.on('click', 'unclustered-point', (e) => {{
                const coordinates = e.features[0].geometry.coordinates.slice();
                const props = e.features[0].properties;
                
                // Color code the popup header based on window
                const headerColor = {{
                    'IMMEDIATE': 'bg-red-500',
                    'URGENT': 'bg-orange-500',
                    'OPTIMAL': 'bg-green-500',
                    'PLANNING': 'bg-blue-500',
                    'FUTURE': 'bg-gray-500'
                }}[props.repowering_window] || 'bg-gray-500';
                
                new mapboxgl.Popup({{
                    closeButton: true,
                    closeOnClick: true,
                    maxWidth: '300px'
                }})
                    .setLngLat(coordinates)
                    .setHTML(`
                        <div>
                            <div class="${{headerColor}} text-white p-2 -m-3 mb-2 rounded-t">
                                <h4 class="font-bold">${{props.size_category}}</h4>
                            </div>
                            <div class="space-y-1 text-sm">
                                <p><strong>Postcode:</strong> ${{props.postcode}}</p>
                                <p><strong>Region:</strong> ${{props.region}}</p>
                                <p><strong>Capacity:</strong> ${{props.capacity_kw}} kW (${{props.capacity_mw.toFixed(2)}} MW)</p>
                                <p><strong>System Age:</strong> ${{props.age_years}} years</p>
                                <p><strong>FIT Remaining:</strong> ${{props.remaining_fit_years}} years</p>
                                <p><strong>Repowering Window:</strong> 
                                    <span class="px-2 py-1 text-xs text-white rounded window-${{props.repowering_window.toLowerCase()}}">
                                        ${{props.repowering_window}}
                                    </span>
                                </p>
                                <p><strong>Annual Generation:</strong> ${{props.annual_generation_mwh}} MWh</p>
                                <p class="text-xs text-gray-500 mt-2">
                                    Click cluster to zoom • ESC to close
                                </p>
                            </div>
                        </div>
                    `)
                    .addTo(map);
            }});
            
            // Cursor changes
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
        
        // Global filter state
        let filters = {{
            window: 'all',
            minCapacity: 0,
            maxCapacity: 50000,
            maxFitYears: 20,
            sizeCategories: ['Small (10-50kW)', 'Medium (50-250kW)', 'Large (250kW-1MW)', 'Utility (1-5MW)', 'Mega (>5MW)']
        }};
        
        // Apply all filters
        function applyAllFilters() {{
            let filterArray = ['all', ['!', ['has', 'point_count']]];
            
            // Window filter
            if (filters.window !== 'all') {{
                filterArray.push(['==', ['get', 'repowering_window'], filters.window]);
            }}
            
            // Capacity filter
            filterArray.push(['>=', ['get', 'capacity_kw'], filters.minCapacity]);
            filterArray.push(['<=', ['get', 'capacity_kw'], filters.maxCapacity]);
            
            // FIT years filter
            filterArray.push(['<=', ['get', 'remaining_fit_years'], filters.maxFitYears]);
            
            // Size category filter
            if (filters.sizeCategories.length > 0 && filters.sizeCategories.length < 5) {{
                filterArray.push(['in', ['get', 'size_category'], ['literal', filters.sizeCategories]]);
            }}
            
            map.setFilter('unclustered-point', filterArray);
            
            // Update cluster filter too
            map.setFilter('clusters', ['has', 'point_count']);
        }}
        
        // Window filter
        function filterByWindow(window) {{
            filters.window = window;
            
            // Update button states
            document.querySelectorAll('.filter-btn').forEach(btn => {{
                btn.classList.add('opacity-60');
            }});
            event.target.classList.remove('opacity-60');
            
            applyAllFilters();
        }}
        
        // Capacity filter
        function applyCapacityFilter() {{
            const minCap = parseFloat(document.getElementById('minCapacity').value) || 0;
            const maxCap = parseFloat(document.getElementById('maxCapacity').value) || 50000;
            
            filters.minCapacity = minCap;
            filters.maxCapacity = maxCap;
            
            applyAllFilters();
        }}
        
        // FIT years filter
        function updateFitFilter(value) {{
            filters.maxFitYears = parseFloat(value);
            document.getElementById('fitValue').textContent = `Max: ${{value}} yr`;
            applyAllFilters();
        }}
        
        // Size category filter
        function updateSizeFilters() {{
            const checkedBoxes = document.querySelectorAll('.size-filter:checked');
            filters.sizeCategories = Array.from(checkedBoxes).map(cb => cb.value);
            applyAllFilters();
        }}
        
        // Add event listeners to size checkboxes
        document.addEventListener('DOMContentLoaded', () => {{
            document.querySelectorAll('.size-filter').forEach(cb => {{
                cb.addEventListener('change', updateSizeFilters);
            }});
        }});
        
        // Reset filters
        function resetFilters() {{
            filters = {{
                window: 'all',
                minCapacity: 0,
                maxCapacity: 50000,
                maxFitYears: 20,
                sizeCategories: ['Small (10-50kW)', 'Medium (50-250kW)', 'Large (250kW-1MW)', 'Utility (1-5MW)', 'Mega (>5MW)']
            }};
            
            // Reset UI
            document.getElementById('minCapacity').value = 0;
            document.getElementById('maxCapacity').value = 50000;
            document.getElementById('fitSlider').value = 20;
            document.getElementById('fitValue').textContent = 'Max: 20 yr';
            document.querySelectorAll('.size-filter').forEach(cb => cb.checked = true);
            document.querySelectorAll('.filter-btn').forEach(btn => {{
                btn.classList.add('opacity-60');
            }});
            document.querySelector('.filter-btn').classList.remove('opacity-60');
            
            applyAllFilters();
        }}
        
        // Zoom to cluster helper
        function zoomToCluster(clusterId) {{
            map.getSource('solar-sites').getClusterExpansionZoom(
                clusterId,
                (err, zoom) => {{
                    if (err) return;
                    map.easeTo({{
                        zoom: zoom + 1  // Extra zoom to ensure unclustering
                    }});
                }}
            );
        }}
        
        // Size Distribution Chart
        const ctx = document.getElementById('sizeChart').getContext('2d');
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(list(size_dist.keys()))},
                datasets: [{{
                    data: {json.dumps(list(size_dist.values()))},
                    backgroundColor: [
                        '#E0F2E9',
                        '#95D47E',
                        '#7CC061',
                        '#0A5F8E',
                        '#044D73'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{ font: {{ size: 10 }} }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${{label}}: ${{value.toLocaleString()}} (${{percentage}}%)`;
                            }}
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
    logger.info("Creating Commercial Solar Dashboard...")
    
    dashboard_html = create_commercial_solar_dashboard()
    
    Path('visualizations').mkdir(exist_ok=True)
    with open('visualizations/saber_solar_dashboard.html', 'w') as f:
        f.write(dashboard_html)
    
    print("\n" + "="*60)
    print("COMMERCIAL SOLAR DASHBOARD CREATED")
    print("="*60)
    print("\n✅ Commercial/Industrial Solar Only:")
    print("   • 35,617 C&I installations")
    print("   • 2,244 MW total capacity")
    print("   • ZERO domestic sites")
    print("\n📊 Key Opportunities:")
    print("   • 23,097 sites in optimal window (5-10yr FIT)")
    print("   • 2,587 sites ≥100kW")
    print("   • 321 utility scale sites ≥1MW")
    print("\n📁 Dashboard: visualizations/saber_solar_dashboard.html")
    
    import webbrowser
    import os
    full_path = os.path.abspath('visualizations/saber_solar_dashboard.html')
    webbrowser.open(f"file://{full_path}")


if __name__ == "__main__":
    main()