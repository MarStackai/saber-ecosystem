#!/usr/bin/env python3
"""
Create a professionally branded Saber Renewable Energy dashboard
"""

import pandas as pd
import json
import base64
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_logo_base64():
    """Convert SVG logo to base64 for embedding"""
    try:
        with open('Saber-logo-wob-green.svg', 'r') as f:
            svg_content = f.read()
        return svg_content
    except:
        # Return a placeholder if logo not found
        return '<svg></svg>'


def prepare_geojson_data():
    """Convert turbine data to GeoJSON format"""
    
    # Load the data
    df = pd.read_csv('data/turbine_coordinates.csv')
    
    # Parse turbine details
    df['capacity_mw'] = df['turbine_details'].apply(lambda x: eval(x)['capacity_mw'] if isinstance(x, str) else 0)
    df['location'] = df['turbine_details'].apply(lambda x: eval(x)['location'] if isinstance(x, str) else 'Unknown')
    df['age_years'] = df['turbine_details'].apply(lambda x: eval(x)['age_years'] if isinstance(x, str) else 0)
    
    # Filter UK bounds
    uk_bounds = {
        'min_lat': 49.5,
        'max_lat': 61.0,
        'min_lon': -11.0,
        'max_lon': 2.5
    }
    
    df = df[
        (df['latitude'] >= uk_bounds['min_lat']) & 
        (df['latitude'] <= uk_bounds['max_lat']) &
        (df['longitude'] >= uk_bounds['min_lon']) & 
        (df['longitude'] <= uk_bounds['max_lon'])
    ]
    
    # Create GeoJSON features
    features = []
    for _, row in df.iterrows():
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row['longitude'], row['latitude']]
            },
            "properties": {
                "id": str(row['turbine_id']),
                "score": row['overall_score'],
                "priority": row['priority'],
                "remaining_fit_years": round(row['remaining_fit_years'], 1),
                "repowering_window": row['repowering_window'],
                "capacity_mw": round(row['capacity_mw'], 3),
                "location": row['location'],
                "postcode": row['postcode'],
                "age_years": round(row['age_years'], 1)
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    # Save as JavaScript variable
    with open('visualizations/turbine_data.js', 'w') as f:
        f.write(f"const turbineData = {json.dumps(geojson, indent=2)};")
    
    logger.info(f"Created data file with {len(features)} turbines")
    return len(features)


def create_saber_dashboard():
    """Create a professionally branded Saber dashboard"""
    
    logo_svg = get_logo_base64()
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Saber Renewable Energy | Wind Repowering Intelligence Platform</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Leaflet CSS & JS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    
    <!-- Leaflet MarkerCluster -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
    <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
    
    <!-- Leaflet Heat Map -->
    <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;800&family=Source+Sans+Pro:wght@400;600&display=swap" rel="stylesheet">
    
    <style>
        /* Saber Brand Colors */
        :root {{
            --saber-blue: #044D73;
            --saber-green: #7CC061;
            --dark-blue: #091922;
            --dark-green: #0A2515;
            --gradient-dark: #0d1138;
            --saber-light-blue: #0A5F8E;
            --saber-light-green: #95D47E;
            --saber-gray: #F5F5F5;
            --saber-dark-gray: #2C3E50;
        }}
        
        /* Typography */
        h1, h2, h3 {{
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        h4, h5, h6 {{
            font-family: 'Montserrat', sans-serif;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }}
        
        body {{
            font-family: 'Source Sans Pro', sans-serif;
            font-weight: 400;
            background: linear-gradient(135deg, var(--dark-blue) 0%, var(--gradient-dark) 100%);
            min-height: 100vh;
        }}
        
        /* Energy Wave Gradient Background */
        .saber-gradient {{
            background: linear-gradient(135deg, var(--saber-blue) 0%, var(--saber-light-blue) 50%, var(--saber-blue) 100%);
            position: relative;
            overflow: hidden;
        }}
        
        .saber-gradient::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(124, 192, 97, 0.1) 0%, transparent 70%);
            animation: energyPulse 15s ease-in-out infinite;
        }}
        
        @keyframes energyPulse {{
            0%, 100% {{ transform: scale(1) rotate(0deg); opacity: 0.3; }}
            50% {{ transform: scale(1.1) rotate(180deg); opacity: 0.5; }}
        }}
        
        /* Card Styling */
        .saber-card {{
            background: rgba(255, 255, 255, 0.98);
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(124, 192, 97, 0.2);
        }}
        
        .saber-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 20px 40px rgba(124, 192, 97, 0.3);
            border-color: var(--saber-green);
        }}
        
        /* Stats Cards */
        .stat-card {{
            background: linear-gradient(135deg, rgba(4, 77, 115, 0.9) 0%, rgba(4, 77, 115, 0.8) 100%);
            border: 2px solid transparent;
            background-clip: padding-box;
            position: relative;
            color: white;
        }}
        
        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0; right: 0; bottom: 0; left: 0;
            z-index: -1;
            margin: -2px;
            border-radius: inherit;
            background: linear-gradient(135deg, var(--saber-green), var(--saber-blue));
        }}
        
        /* Map Styling */
        #map {{
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 2px solid var(--saber-blue);
        }}
        
        .leaflet-popup-content-wrapper {{
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(4, 77, 115, 0.3);
            border: 1px solid var(--saber-green);
        }}
        
        /* Custom Markers */
        .marker-urgent {{
            background: radial-gradient(circle, #FF6B6B, #C92A2A);
            border: 3px solid white;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: block;
            left: -12px;
            top: -12px;
            position: relative;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            animation: urgentPulse 2s infinite;
        }}
        
        @keyframes urgentPulse {{
            0%, 100% {{ box-shadow: 0 4px 8px rgba(201, 42, 42, 0.3); }}
            50% {{ box-shadow: 0 4px 20px rgba(201, 42, 42, 0.6); }}
        }}
        
        .marker-optimal {{
            background: radial-gradient(circle, var(--saber-green), var(--saber-light-green));
            border: 3px solid white;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: block;
            left: -12px;
            top: -12px;
            position: relative;
            box-shadow: 0 4px 8px rgba(124, 192, 97, 0.4);
        }}
        
        .marker-early {{
            background: radial-gradient(circle, #51CF66, #37B24D);
            border: 3px solid white;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: block;
            left: -12px;
            top: -12px;
            position: relative;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }}
        
        .marker-late {{
            background: radial-gradient(circle, #868E96, #495057);
            border: 3px solid white;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: block;
            left: -12px;
            top: -12px;
            position: relative;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }}
        
        /* Buttons */
        .saber-btn {{
            background: linear-gradient(135deg, var(--saber-green), var(--saber-light-green));
            color: white;
            font-family: 'Montserrat', sans-serif;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 10px 20px;
            border-radius: 8px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(124, 192, 97, 0.3);
        }}
        
        .saber-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(124, 192, 97, 0.4);
        }}
        
        .saber-btn-secondary {{
            background: linear-gradient(135deg, var(--saber-blue), var(--saber-light-blue));
            box-shadow: 0 4px 15px rgba(4, 77, 115, 0.3);
        }}
        
        .saber-btn-secondary:hover {{
            box-shadow: 0 6px 20px rgba(4, 77, 115, 0.4);
        }}
        
        /* Loading Animation */
        .energy-loader {{
            width: 60px;
            height: 60px;
            position: relative;
        }}
        
        .energy-loader::before,
        .energy-loader::after {{
            content: '';
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            border: 4px solid transparent;
            border-top-color: var(--saber-green);
            animation: energySpin 1.5s linear infinite;
        }}
        
        .energy-loader::after {{
            border-top-color: var(--saber-blue);
            animation-delay: 0.75s;
        }}
        
        @keyframes energySpin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {{
            width: 10px;
            height: 10px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--dark-blue);
            border-radius: 5px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(180deg, var(--saber-green), var(--saber-blue));
            border-radius: 5px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: linear-gradient(180deg, var(--saber-light-green), var(--saber-light-blue));
        }}
        
        /* Filter Pills */
        .filter-pill {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(124, 192, 97, 0.3);
            color: white;
            transition: all 0.3s ease;
        }}
        
        .filter-pill:hover {{
            background: rgba(124, 192, 97, 0.2);
            border-color: var(--saber-green);
            transform: scale(1.05);
        }}
        
        .filter-pill.active {{
            background: linear-gradient(135deg, var(--saber-green), var(--saber-light-green));
            border-color: transparent;
        }}
    </style>
</head>
<body>
    <!-- Header with Saber Branding -->
    <header class="saber-gradient text-white shadow-2xl relative">
        <div class="container mx-auto px-6 py-6">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-6">
                    <!-- Logo Container with proper spacing -->
                    <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4" style="min-width: 200px;">
                        {logo_svg}
                    </div>
                    <div class="border-l-2 border-white/30 pl-6">
                        <h1 class="text-2xl">Wind Repowering Intelligence</h1>
                        <p class="text-sm opacity-90 font-light">Expert Analysis for Strategic Renewable Energy Decisions</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="text-right">
                        <p class="text-2xl font-bold">7,448</p>
                        <p class="text-xs opacity-90 uppercase">Active FIT Sites</p>
                    </div>
                    <button onclick="location.reload()" class="saber-btn">
                        <i class="fas fa-sync-alt mr-2"></i>Refresh Data
                    </button>
                </div>
            </div>
        </div>
    </header>
    
    <!-- Main Dashboard -->
    <div class="container mx-auto px-6 py-8">
        <!-- Key Metrics -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4 mb-8">
            <div class="stat-card saber-card p-5">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Total Sites</p>
                        <p class="text-3xl font-bold text-white">7,172</p>
                        <p class="text-xs text-white/60 mt-1">With active FIT</p>
                    </div>
                    <div class="text-4xl text-white/30">
                        <i class="fas fa-wind"></i>
                    </div>
                </div>
            </div>
            
            <div class="stat-card saber-card p-5">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Capacity</p>
                        <p class="text-3xl font-bold text-white">770</p>
                        <p class="text-xs text-white/60 mt-1">Megawatts</p>
                    </div>
                    <div class="text-4xl text-white/30">
                        <i class="fas fa-bolt"></i>
                    </div>
                </div>
            </div>
            
            <div class="stat-card saber-card p-5">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Urgent</p>
                        <p class="text-3xl font-bold text-red-400">801</p>
                        <p class="text-xs text-white/60 mt-1">2-5 years FIT</p>
                    </div>
                    <div class="text-4xl text-red-400/30">
                        <i class="fas fa-exclamation-circle"></i>
                    </div>
                </div>
            </div>
            
            <div class="stat-card saber-card p-5">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Optimal</p>
                        <p class="text-3xl font-bold" style="color: var(--saber-light-green)">5,582</p>
                        <p class="text-xs text-white/60 mt-1">5-10 years FIT</p>
                    </div>
                    <div class="text-4xl text-white/30">
                        <i class="fas fa-bullseye"></i>
                    </div>
                </div>
            </div>
            
            <div class="stat-card saber-card p-5">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Avg FIT</p>
                        <p class="text-3xl font-bold text-white">7.0</p>
                        <p class="text-xs text-white/60 mt-1">Years remaining</p>
                    </div>
                    <div class="text-4xl text-white/30">
                        <i class="fas fa-clock"></i>
                    </div>
                </div>
            </div>
            
            <div class="stat-card saber-card p-5">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Potential</p>
                        <p class="text-3xl font-bold" style="color: var(--saber-light-green)">492</p>
                        <p class="text-xs text-white/60 mt-1">MW opportunity</p>
                    </div>
                    <div class="text-4xl text-white/30">
                        <i class="fas fa-chart-line"></i>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Main Content Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Map Section -->
            <div class="lg:col-span-2">
                <div class="saber-card p-6">
                    <div class="flex items-center justify-between mb-6">
                        <h2 class="text-xl">
                            <i class="fas fa-map-marked-alt mr-3" style="color: var(--saber-green)"></i>
                            Strategic Site Analysis
                        </h2>
                        <div class="flex space-x-2">
                            <button onclick="resetMap()" class="saber-btn-secondary px-4 py-2 rounded-lg text-white text-sm">
                                <i class="fas fa-compress-arrows-alt mr-2"></i>Reset
                            </button>
                            <button onclick="toggleClustering()" id="clusterBtn" class="saber-btn px-4 py-2 rounded-lg text-white text-sm">
                                <i class="fas fa-layer-group mr-2"></i>Clustering
                            </button>
                            <button onclick="toggleHeatmap()" id="heatmapBtn" class="saber-btn-secondary px-4 py-2 rounded-lg text-white text-sm">
                                <i class="fas fa-fire mr-2"></i>Heatmap
                            </button>
                        </div>
                    </div>
                    
                    <!-- Filter Pills -->
                    <div class="flex flex-wrap gap-3 mb-6">
                        <button onclick="filterByWindow('all')" class="filter-pill active px-4 py-2 rounded-full text-sm font-semibold">
                            All Sites (7,448)
                        </button>
                        <button onclick="filterByWindow('URGENT')" class="filter-pill px-4 py-2 rounded-full text-sm font-semibold">
                            <span class="inline-block w-2 h-2 rounded-full bg-red-500 mr-2"></span>
                            Urgent (801)
                        </button>
                        <button onclick="filterByWindow('OPTIMAL')" class="filter-pill px-4 py-2 rounded-full text-sm font-semibold">
                            <span class="inline-block w-2 h-2 rounded-full mr-2" style="background-color: var(--saber-green)"></span>
                            Optimal (5,582)
                        </button>
                        <button onclick="filterByWindow('TOO_LATE')" class="filter-pill px-4 py-2 rounded-full text-sm font-semibold">
                            <span class="inline-block w-2 h-2 rounded-full bg-gray-500 mr-2"></span>
                            Expiring (276)
                        </button>
                    </div>
                    
                    <!-- Map Container -->
                    <div id="map" class="h-[500px] lg:h-[600px] relative">
                        <div id="mapLoader" class="absolute inset-0 flex items-center justify-center bg-white/90 backdrop-blur-sm z-10 rounded-xl">
                            <div class="text-center">
                                <div class="energy-loader mb-4"></div>
                                <p class="text-gray-700 font-semibold">Loading Strategic Intelligence...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Side Panel -->
            <div class="space-y-6">
                <!-- Regional Intelligence -->
                <div class="saber-card p-6">
                    <h3 class="text-lg mb-4">
                        <i class="fas fa-chart-bar mr-2" style="color: var(--saber-green)"></i>
                        Regional Intelligence
                    </h3>
                    <div class="space-y-3">
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-sm font-semibold">Orkney Islands</span>
                                <span class="text-sm font-bold" style="color: var(--saber-blue)">770</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="h-2 rounded-full" style="width: 100%; background: linear-gradient(90deg, var(--saber-green), var(--saber-light-green))"></div>
                            </div>
                        </div>
                        
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-sm font-semibold">Aberdeenshire</span>
                                <span class="text-sm font-bold" style="color: var(--saber-blue)">524</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="h-2 rounded-full" style="width: 68%; background: linear-gradient(90deg, var(--saber-green), var(--saber-light-green))"></div>
                            </div>
                        </div>
                        
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-sm font-semibold">Cornwall</span>
                                <span class="text-sm font-bold" style="color: var(--saber-blue)">409</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="h-2 rounded-full" style="width: 53%; background: linear-gradient(90deg, var(--saber-green), var(--saber-light-green))"></div>
                            </div>
                        </div>
                        
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-sm font-semibold">Highland</span>
                                <span class="text-sm font-bold" style="color: var(--saber-blue)">208</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="h-2 rounded-full" style="width: 27%; background: linear-gradient(90deg, var(--saber-green), var(--saber-light-green))"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Priority Analysis -->
                <div class="saber-card p-6">
                    <h3 class="text-lg mb-4">
                        <i class="fas fa-chart-pie mr-2" style="color: var(--saber-green)"></i>
                        Priority Analysis
                    </h3>
                    <canvas id="priorityChart" width="400" height="180"></canvas>
                </div>
                
                <!-- Selected Site Intelligence -->
                <div id="siteInfo" class="saber-card p-6 hidden">
                    <h3 class="text-lg mb-4">
                        <i class="fas fa-info-circle mr-2" style="color: var(--saber-green)"></i>
                        Site Intelligence
                    </h3>
                    <div id="siteDetails" class="space-y-3 text-sm">
                        <!-- Populated by JavaScript -->
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Footer -->
    <footer class="mt-12 py-8 text-white text-center" style="background: var(--dark-blue)">
        <p class="text-sm opacity-80">© 2024 Saber Renewable Energy Ltd. All rights reserved.</p>
        <p class="text-xs opacity-60 mt-2">Wind Repowering Intelligence Platform | Expert • Clear • Strategic</p>
    </footer>
    
    <!-- Load turbine data -->
    <script src="turbine_data.js"></script>
    
    <!-- Main application script -->
    <script>
        let map;
        let markers = [];
        let markerCluster;
        let heatmapLayer;
        let currentFilter = 'all';
        let clusteringEnabled = true;
        let heatmapEnabled = false;
        
        // Initialize map
        function initMap() {{
            // Create map
            map = L.map('map', {{
                center: [54.5, -3.5],
                zoom: 6,
                maxZoom: 18,
                minZoom: 5
            }});
            
            // Add CartoDB Positron tiles for cleaner look
            L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                attribution: '© OpenStreetMap contributors © CARTO',
                maxZoom: 18
            }}).addTo(map);
            
            // Create marker cluster group with custom styling - less aggressive clustering
            markerCluster = L.markerClusterGroup({{
                maxClusterRadius: 30,  // Reduced from 50 for less clustering
                spiderfyOnMaxZoom: true,
                showCoverageOnHover: false,
                zoomToBoundsOnClick: true,
                disableClusteringAtZoom: 10,  // Stop clustering at zoom level 10
                iconCreateFunction: function(cluster) {{
                    const count = cluster.getChildCount();
                    let size = 'small';
                    let bgColor = 'linear-gradient(135deg, #7CC061, #95D47E)';
                    
                    if (count > 100) {{
                        size = 'large';
                        bgColor = 'linear-gradient(135deg, #044D73, #0A5F8E)';
                    }} else if (count > 50) {{
                        size = 'medium';
                        bgColor = 'linear-gradient(135deg, #0A5F8E, #044D73)';
                    }}
                    
                    return L.divIcon({{
                        html: `<div style="background: ${{bgColor}}; color: white; border-radius: 50%; 
                               width: 45px; height: 45px; display: flex; align-items: center; 
                               justify-content: center; font-weight: bold; border: 3px solid white;
                               box-shadow: 0 4px 10px rgba(4, 77, 115, 0.4); font-size: 14px;">${{count}}</div>`,
                        className: 'custom-cluster-icon',
                        iconSize: L.point(45, 45)
                    }});
                }}
            }});
            
            // Load markers
            loadMarkers();
            
            // Hide loader
            document.getElementById('mapLoader').style.display = 'none';
        }}
        
        // Load markers
        function loadMarkers() {{
            markerCluster.clearLayers();
            markers = [];
            
            turbineData.features.forEach(feature => {{
                const props = feature.properties;
                const coords = feature.geometry.coordinates;
                
                let markerClass = 'marker-late';
                if (props.repowering_window === 'URGENT') markerClass = 'marker-urgent';
                else if (props.repowering_window === 'OPTIMAL') markerClass = 'marker-optimal';
                else if (props.repowering_window === 'TOO_EARLY') markerClass = 'marker-early';
                
                const icon = L.divIcon({{
                    className: 'custom-marker',
                    html: `<span class="${{markerClass}}"></span>`,
                    iconSize: [24, 24],
                    iconAnchor: [12, 12]
                }});
                
                const marker = L.marker([coords[1], coords[0]], {{ icon: icon }});
                marker.bindPopup(createPopupContent(props));
                marker.on('click', function() {{
                    showSiteInfo(props);
                }});
                
                markers.push(marker);
                markerCluster.addLayer(marker);
            }});
            
            if (clusteringEnabled) {{
                map.addLayer(markerCluster);
            }}
        }}
        
        // Create popup content
        function createPopupContent(props) {{
            return `
                <div class="p-3">
                    <h4 class="font-bold text-lg mb-2" style="color: var(--saber-blue)">
                        Site ${{props.id}}
                    </h4>
                    <div class="space-y-2 text-sm">
                        <div><strong>Location:</strong> ${{props.location}}</div>
                        <div><strong>Capacity:</strong> ${{props.capacity_mw}} MW</div>
                        <div><strong>FIT Remaining:</strong> ${{props.remaining_fit_years}} years</div>
                        <div><strong>Repowering Score:</strong> ${{props.score.toFixed(3)}}</div>
                        <div class="pt-2 mt-2 border-t">
                            <span class="inline-block px-3 py-1 rounded-full text-xs font-bold text-white"
                                  style="background: ${{props.repowering_window === 'OPTIMAL' ? 'var(--saber-green)' : 
                                         props.repowering_window === 'URGENT' ? '#FF6B6B' : '#868E96'}}">
                                ${{props.repowering_window}}
                            </span>
                        </div>
                    </div>
                </div>
            `;
        }}
        
        // Show site info
        function showSiteInfo(props) {{
            const siteInfo = document.getElementById('siteInfo');
            const siteDetails = document.getElementById('siteDetails');
            
            siteInfo.classList.remove('hidden');
            siteDetails.innerHTML = `
                <div class="space-y-3">
                    <div class="pb-3 border-b border-gray-200">
                        <strong class="text-gray-600">Site ID:</strong>
                        <span class="font-bold" style="color: var(--saber-blue)">${{props.id}}</span>
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <p class="text-gray-600 text-xs uppercase">Location</p>
                            <p class="font-semibold">${{props.location.split(' - ')[0]}}</p>
                        </div>
                        <div>
                            <p class="text-gray-600 text-xs uppercase">Postcode</p>
                            <p class="font-semibold">${{props.postcode}}</p>
                        </div>
                        <div>
                            <p class="text-gray-600 text-xs uppercase">Capacity</p>
                            <p class="font-semibold">${{props.capacity_mw}} MW</p>
                        </div>
                        <div>
                            <p class="text-gray-600 text-xs uppercase">Age</p>
                            <p class="font-semibold">${{props.age_years}} years</p>
                        </div>
                        <div>
                            <p class="text-gray-600 text-xs uppercase">FIT Remaining</p>
                            <p class="font-semibold">${{props.remaining_fit_years}} years</p>
                        </div>
                        <div>
                            <p class="text-gray-600 text-xs uppercase">Score</p>
                            <p class="font-semibold">${{props.score.toFixed(3)}}</p>
                        </div>
                    </div>
                    <div class="pt-3 border-t border-gray-200">
                        <span class="inline-block px-3 py-1 rounded-full text-xs font-bold text-white"
                              style="background: ${{props.repowering_window === 'OPTIMAL' ? 'var(--saber-green)' : 
                                     props.repowering_window === 'URGENT' ? '#FF6B6B' : '#868E96'}}">
                            ${{props.repowering_window}}
                        </span>
                        <span class="inline-block px-3 py-1 rounded-full text-xs font-bold text-white ml-2"
                              style="background: var(--saber-blue)">
                            ${{props.priority}}
                        </span>
                    </div>
                </div>
            `;
        }}
        
        // Filter by window
        function filterByWindow(window) {{
            currentFilter = window;
            
            document.querySelectorAll('.filter-pill').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');
            
            markerCluster.clearLayers();
            markers = [];
            
            turbineData.features.forEach(feature => {{
                const props = feature.properties;
                
                if (window === 'all' || props.repowering_window === window) {{
                    const coords = feature.geometry.coordinates;
                    
                    let markerClass = 'marker-late';
                    if (props.repowering_window === 'URGENT') markerClass = 'marker-urgent';
                    else if (props.repowering_window === 'OPTIMAL') markerClass = 'marker-optimal';
                    else if (props.repowering_window === 'TOO_EARLY') markerClass = 'marker-early';
                    
                    const icon = L.divIcon({{
                        className: 'custom-marker',
                        html: `<span class="${{markerClass}}"></span>`,
                        iconSize: [24, 24],
                        iconAnchor: [12, 12]
                    }});
                    
                    const marker = L.marker([coords[1], coords[0]], {{ icon: icon }});
                    marker.bindPopup(createPopupContent(props));
                    marker.on('click', function() {{
                        showSiteInfo(props);
                    }});
                    
                    markers.push(marker);
                    markerCluster.addLayer(marker);
                }}
            }});
        }}
        
        // Toggle clustering
        function toggleClustering() {{
            clusteringEnabled = !clusteringEnabled;
            const btn = document.getElementById('clusterBtn');
            
            if (clusteringEnabled) {{
                // Remove individual markers first
                markers.forEach(marker => {{
                    if (map.hasLayer(marker)) {{
                        map.removeLayer(marker);
                    }}
                }});
                // Add clustered markers
                map.addLayer(markerCluster);
                btn.innerHTML = '<i class="fas fa-layer-group mr-2"></i>Clustering ON';
                btn.classList.remove('saber-btn-secondary');
                btn.classList.add('saber-btn');
            }} else {{
                // Remove cluster layer
                map.removeLayer(markerCluster);
                // Add individual markers
                markers.forEach(marker => {{
                    marker.addTo(map);
                }});
                btn.innerHTML = '<i class="fas fa-layer-group mr-2"></i>Clustering OFF';
                btn.classList.remove('saber-btn');
                btn.classList.add('saber-btn-secondary');
            }}
        }}
        
        // Toggle heatmap
        function toggleHeatmap() {{
            heatmapEnabled = !heatmapEnabled;
            const btn = document.getElementById('heatmapBtn');
            
            if (heatmapEnabled) {{
                const heatData = turbineData.features.map(f => [
                    f.geometry.coordinates[1],
                    f.geometry.coordinates[0],
                    f.properties.score * 100
                ]);
                
                heatmapLayer = L.heatLayer(heatData, {{
                    radius: 25,
                    blur: 15,
                    maxZoom: 10,
                    gradient: {{
                        0.0: '#27AE60',
                        0.5: '#7CC061',
                        0.7: '#F39C12',
                        1.0: '#E74C3C'
                    }}
                }}).addTo(map);
                
                btn.innerHTML = '<i class="fas fa-fire mr-2"></i>Heatmap ON';
            }} else {{
                if (heatmapLayer) {{
                    map.removeLayer(heatmapLayer);
                }}
                btn.innerHTML = '<i class="fas fa-fire mr-2"></i>Heatmap OFF';
            }}
        }}
        
        // Reset map
        function resetMap() {{
            map.setView([54.5, -3.5], 6);
        }}
        
        // Initialize priority chart
        function initPriorityChart() {{
            const ctx = document.getElementById('priorityChart').getContext('2d');
            
            const gradient1 = ctx.createLinearGradient(0, 0, 0, 200);
            gradient1.addColorStop(0, '#FF6B6B');
            gradient1.addColorStop(1, '#C92A2A');
            
            const gradient2 = ctx.createLinearGradient(0, 0, 0, 200);
            gradient2.addColorStop(0, '#7CC061');
            gradient2.addColorStop(1, '#95D47E');
            
            const gradient3 = ctx.createLinearGradient(0, 0, 0, 200);
            gradient3.addColorStop(0, '#51CF66');
            gradient3.addColorStop(1, '#37B24D');
            
            const gradient4 = ctx.createLinearGradient(0, 0, 0, 200);
            gradient4.addColorStop(0, '#868E96');
            gradient4.addColorStop(1, '#495057');
            
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: ['Urgent (2-5yr)', 'Optimal (5-10yr)', 'Too Early (>15yr)', 'Too Late (<2yr)'],
                    datasets: [{{
                        data: [801, 5582, 1, 276],
                        backgroundColor: [gradient1, gradient2, gradient3, gradient4],
                        borderWidth: 3,
                        borderColor: '#ffffff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'bottom',
                            labels: {{
                                padding: 15,
                                font: {{
                                    size: 11,
                                    family: "'Source Sans Pro', sans-serif"
                                }},
                                usePointStyle: true
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${{label}}: ${{value}} (${{percentage}}%)`;
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // Initialize on load
        document.addEventListener('DOMContentLoaded', () => {{
            initMap();
            initPriorityChart();
        }});
    </script>
</body>
</html>"""
    
    return html_content


def main():
    logger.info("Creating professionally branded Saber dashboard...")
    
    # Prepare GeoJSON data
    num_turbines = prepare_geojson_data()
    
    # Copy logo to visualizations folder if it exists
    import shutil
    if Path('Saber-logo-wob-green.svg').exists():
        shutil.copy('Saber-logo-wob-green.svg', 'visualizations/Saber-logo-wob-green.svg')
        logger.info("Logo copied to visualizations folder")
    
    # Create dashboard HTML
    dashboard_html = create_saber_dashboard()
    
    # Save dashboard
    with open('visualizations/saber_branded_dashboard.html', 'w') as f:
        f.write(dashboard_html)
    
    print("\n" + "="*60)
    print("SABER BRANDED DASHBOARD CREATED")
    print("="*60)
    print("\n🎨 Professional Branding Applied:")
    print("   ✓ Saber official colors (#044D73 blue, #7CC061 green)")
    print("   ✓ Montserrat & Source Sans Pro typography")
    print("   ✓ Energy wave gradient backgrounds")
    print("   ✓ Logo integration with proper spacing")
    print("   ✓ Expert, Strategic, Warmly Professional tone")
    print("\n✨ Design Features:")
    print("   ✓ Gradient overlays and energy animations")
    print("   ✓ Glass morphism effects on cards")
    print("   ✓ Custom styled map markers")
    print("   ✓ Professional data visualization")
    print("   ✓ Smooth transitions and hover effects")
    print(f"\n📍 {num_turbines} turbines mapped across UK")
    print("\n📁 Dashboard: visualizations/saber_branded_dashboard.html")
    print("\nTo view: open visualizations/saber_branded_dashboard.html")
    
    # Try to open automatically
    import webbrowser
    import os
    full_path = os.path.abspath('visualizations/saber_branded_dashboard.html')
    webbrowser.open(f"file://{full_path}")


if __name__ == "__main__":
    main()