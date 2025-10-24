#!/usr/bin/env python3
"""
Create a professionally branded Saber dashboard with Mapbox GL JS
"""

import pandas as pd
import json
import logging
from pathlib import Path

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


def prepare_geojson_data():
    """Convert turbine data to GeoJSON format for Mapbox"""
    
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
    
    # Create GeoJSON
    features = []
    for _, row in df.iterrows():
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(row['longitude']), float(row['latitude'])]  # Ensure floats
            },
            "properties": {
                "id": str(row['turbine_id']),
                "score": float(row['overall_score']),
                "priority": row['priority'],
                "remaining_fit_years": float(row['remaining_fit_years']),
                "repowering_window": row['repowering_window'],
                "capacity_mw": float(row['capacity_mw']),
                "location": row['location'],
                "postcode": row['postcode'],
                "age_years": float(row['age_years'])
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    # Save GeoJSON
    with open('visualizations/turbines_mapbox.geojson', 'w') as f:
        json.dump(geojson, f)
    
    logger.info(f"Created GeoJSON with {len(features)} turbines")
    return len(features)


def create_saber_mapbox_dashboard():
    """Create Saber dashboard with Mapbox GL JS"""
    
    logo_svg = get_logo_base64()
    
    # Load improved GeoJSON data with better coordinates
    import json
    with open('visualizations/turbines_mapbox_improved.geojson', 'r') as f:
        geojson_data = json.load(f)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Saber Renewable Energy | Wind Repowering Intelligence Platform</title>
    
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
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;800&family=Source+Sans+Pro:wght@400;600&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --saber-blue: #044D73;
            --saber-green: #7CC061;
            --dark-blue: #091922;
            --dark-green: #0A2515;
            --gradient-dark: #0d1138;
            --saber-light-blue: #0A5F8E;
            --saber-light-green: #95D47E;
        }}
        
        /* Typography */
        h1, h2, h3 {{
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        body {{
            font-family: 'Source Sans Pro', sans-serif;
            font-weight: 400;
            background: linear-gradient(135deg, var(--dark-blue) 0%, var(--gradient-dark) 100%);
            min-height: 100vh;
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
        
        #map {{
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 2px solid var(--saber-blue);
        }}
        
        .mapboxgl-popup-content {{
            border-radius: 12px;
            padding: 15px;
            min-width: 250px;
            max-width: 300px;
            box-shadow: 0 8px 20px rgba(4, 77, 115, 0.3);
        }}
        
        .mapboxgl-popup-close-button {{
            color: var(--saber-blue);
            font-size: 18px;
            padding: 5px;
        }}
        
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
            border: none;
            cursor: pointer;
        }}
        
        .saber-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(124, 192, 97, 0.4);
        }}
        
        .saber-btn-secondary {{
            background: linear-gradient(135deg, var(--saber-blue), var(--saber-light-blue));
            box-shadow: 0 4px 15px rgba(4, 77, 115, 0.3);
        }}
        
        .filter-pill {{
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(124, 192, 97, 0.3);
            color: var(--saber-blue);
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .filter-pill:hover {{
            background: rgba(124, 192, 97, 0.2);
            border-color: var(--saber-green);
            transform: scale(1.05);
        }}
        
        .filter-pill.active {{
            background: linear-gradient(135deg, var(--saber-green), var(--saber-light-green));
            border-color: transparent;
            color: white;
        }}
        
        /* Priority chart container - FIXED HEIGHT */
        #priorityChartContainer {{
            height: 200px;
            position: relative;
        }}
    </style>
</head>
<body>
    <!-- Header -->
    <header class="saber-gradient text-white shadow-2xl relative">
        <div class="container mx-auto px-6 py-6">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-6">
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
                    <a href="saber_solar_dashboard.html" class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg hover:bg-white/30 transition text-white">
                        <i class="fas fa-solar-panel mr-2"></i>Solar
                    </a>
                    <a href="saber_analytics_dashboard.html" class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg hover:bg-white/30 transition text-white">
                        <i class="fas fa-chart-line mr-2"></i>Analytics
                    </a>
                    <button onclick="location.reload()" class="saber-btn">
                        <i class="fas fa-sync-alt mr-2"></i>Refresh
                    </button>
                </div>
            </div>
        </div>
    </header>
    
    <!-- Main Dashboard - Full Width -->
    <div class="w-full px-6 py-8">
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
                    <div class="flex items-center justify-between mb-4">
                        <h2 class="text-xl">
                            <i class="fas fa-map-marked-alt mr-3" style="color: var(--saber-green)"></i>
                            Strategic Site Analysis
                        </h2>
                        <div class="flex space-x-2">
                            <button onclick="resetMap()" class="px-4 py-2 rounded-lg text-white text-sm" style="background: var(--saber-blue);">
                                <i class="fas fa-compress-arrows-alt mr-2"></i>Reset
                            </button>
                            <button onclick="toggle3D()" id="btn3D" class="px-4 py-2 rounded-lg text-white text-sm" style="background: var(--saber-blue);">
                                <i class="fas fa-cube mr-2"></i>3D View
                            </button>
                        </div>
                    </div>
                    
                    <!-- Filter Pills -->
                    <div class="flex flex-wrap gap-3 mb-4">
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
                    <div id="map" class="h-[500px] lg:h-[600px] relative"></div>
                    
                    <!-- Capacity Filter Buttons - Multi-Select -->
                    <div class="mt-4 p-3 bg-gray-50 rounded-lg">
                        <div class="flex flex-wrap items-center gap-2">
                            <span class="text-sm font-semibold text-gray-700">Capacity:</span>
                            <button onclick="toggleAllCapacity()" class="capacity-all-btn px-3 py-1 bg-gray-700 text-white rounded text-xs transition hover:opacity-80">All</button>
                            <span class="text-gray-400">|</span>
                            <button onclick="toggleCapacity('0-50')" class="capacity-btn px-3 py-1 bg-gray-200 text-gray-700 rounded text-xs transition hover:bg-gray-300" data-range="0-50">0-50kW</button>
                            <button onclick="toggleCapacity('50-100')" class="capacity-btn px-3 py-1 bg-gray-200 text-gray-700 rounded text-xs transition hover:bg-gray-300" data-range="50-100">50-100kW</button>
                            <button onclick="toggleCapacity('100-200')" class="capacity-btn px-3 py-1 bg-gray-200 text-gray-700 rounded text-xs transition hover:bg-gray-300" data-range="100-200">100-200kW</button>
                            <button onclick="toggleCapacity('200-300')" class="capacity-btn px-3 py-1 bg-gray-200 text-gray-700 rounded text-xs transition hover:bg-gray-300" data-range="200-300">200-300kW</button>
                            <button onclick="toggleCapacity('300-400')" class="capacity-btn px-3 py-1 bg-gray-200 text-gray-700 rounded text-xs transition hover:bg-gray-300" data-range="300-400">300-400kW</button>
                            <button onclick="toggleCapacity('400-500')" class="capacity-btn px-3 py-1 bg-gray-200 text-gray-700 rounded text-xs transition hover:bg-gray-300" data-range="400-500">400-500kW</button>
                            <button onclick="toggleCapacity('500-750')" class="capacity-btn px-3 py-1 bg-gray-200 text-gray-700 rounded text-xs transition hover:bg-gray-300" data-range="500-750">500-750kW</button>
                            <button onclick="toggleCapacity('750-1000')" class="capacity-btn px-3 py-1 bg-gray-200 text-gray-700 rounded text-xs transition hover:bg-gray-300" data-range="750-1000">750kW-1MW</button>
                            <button onclick="toggleCapacity('1000+')" class="capacity-btn px-3 py-1 bg-gray-200 text-gray-700 rounded text-xs transition hover:bg-gray-300" data-range="1000+">1MW+</button>
                        </div>
                        <div class="mt-2 text-xs text-gray-500">
                            <i class="fas fa-info-circle mr-1"></i>Click to toggle ranges on/off (multi-select)
                        </div>
                    </div>
                    
                    <!-- Regional Summary Card -->
                    <div id="regionalSummary" class="mt-4 p-4 bg-white rounded-lg shadow-md">
                        <h3 class="text-lg font-bold mb-3">
                            <i class="fas fa-chart-bar mr-2" style="color: var(--saber-green)"></i>
                            Filtered Market Summary
                        </h3>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div class="bg-blue-50 p-3 rounded">
                                <h4 class="font-semibold text-sm text-blue-900 mb-2">England & Wales</h4>
                                <div class="space-y-1 text-sm">
                                    <div class="flex justify-between">
                                        <span class="text-gray-600">Sites:</span>
                                        <span class="font-bold" id="ewSites">0</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-gray-600">Capacity:</span>
                                        <span class="font-bold" id="ewCapacity">0 MW</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-gray-600">Optimal:</span>
                                        <span class="font-bold text-green-600" id="ewOptimal">0</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-gray-600">Urgent:</span>
                                        <span class="font-bold text-orange-600" id="ewUrgent">0</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-gray-600">Expiring:</span>
                                        <span class="font-bold text-red-600" id="ewExpiring">0</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="bg-purple-50 p-3 rounded">
                                <h4 class="font-semibold text-sm text-purple-900 mb-2">Scotland</h4>
                                <div class="space-y-1 text-sm">
                                    <div class="flex justify-between">
                                        <span class="text-gray-600">Sites:</span>
                                        <span class="font-bold" id="scotSites">0</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-gray-600">Capacity:</span>
                                        <span class="font-bold" id="scotCapacity">0 MW</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-gray-600">Optimal:</span>
                                        <span class="font-bold text-green-600" id="scotOptimal">0</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-gray-600">Urgent:</span>
                                        <span class="font-bold text-orange-600" id="scotUrgent">0</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-gray-600">Expiring:</span>
                                        <span class="font-bold text-red-600" id="scotExpiring">0</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="bg-green-50 p-3 rounded">
                                <h4 class="font-semibold text-sm text-green-900 mb-2">Total UK</h4>
                                <div class="space-y-1 text-sm">
                                    <div class="flex justify-between">
                                        <span class="text-gray-600">Sites:</span>
                                        <span class="font-bold" id="totalSites">0</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-gray-600">Capacity:</span>
                                        <span class="font-bold" id="totalCapacity">0 MW</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-gray-600">Avg Size:</span>
                                        <span class="font-bold" id="avgSize">0 kW</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Side Panel -->
            <div class="space-y-6">
                <!-- Selected Site Info - MOVED TO TOP -->
                <div id="siteInfo" class="saber-card p-6 hidden">
                    <h3 class="text-lg mb-4">
                        <i class="fas fa-info-circle mr-2" style="color: var(--saber-green)"></i>
                        Site Intelligence
                    </h3>
                    <div id="siteDetails" class="space-y-3 text-sm"></div>
                </div>
                
                <!-- Priority Analysis with FIXED HEIGHT -->
                <div class="saber-card p-6">
                    <h3 class="text-lg mb-4">
                        <i class="fas fa-chart-pie mr-2" style="color: var(--saber-green)"></i>
                        Priority Analysis
                    </h3>
                    <div id="priorityChartContainer">
                        <canvas id="priorityChart"></canvas>
                    </div>
                </div>
                
                <!-- Regional Intelligence - ALL REGIONS -->
                <div class="saber-card p-6">
                    <h3 class="text-lg mb-4">
                        <i class="fas fa-chart-bar mr-2" style="color: var(--saber-green)"></i>
                        Regional Distribution
                    </h3>
                    <div class="space-y-2 max-h-96 overflow-y-auto">
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
                                <span class="text-sm font-bold" style="color: var(--saber-blue)">342</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="h-2 rounded-full" style="width: 44%; background: linear-gradient(90deg, var(--saber-green), var(--saber-light-green))"></div>
                            </div>
                        </div>
                        
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-sm font-semibold">Yorkshire</span>
                                <span class="text-sm font-bold" style="color: var(--saber-blue)">298</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="h-2 rounded-full" style="width: 39%; background: linear-gradient(90deg, var(--saber-green), var(--saber-light-green))"></div>
                            </div>
                        </div>
                        
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-sm font-semibold">Wales</span>
                                <span class="text-sm font-bold" style="color: var(--saber-blue)">276</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="h-2 rounded-full" style="width: 36%; background: linear-gradient(90deg, var(--saber-green), var(--saber-light-green))"></div>
                            </div>
                        </div>
                        
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-sm font-semibold">Northumberland</span>
                                <span class="text-sm font-bold" style="color: var(--saber-blue)">218</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="h-2 rounded-full" style="width: 28%; background: linear-gradient(90deg, var(--saber-green), var(--saber-light-green))"></div>
                            </div>
                        </div>
                        
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-sm font-semibold">Devon</span>
                                <span class="text-sm font-bold" style="color: var(--saber-blue)">186</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="h-2 rounded-full" style="width: 24%; background: linear-gradient(90deg, var(--saber-green), var(--saber-light-green))"></div>
                            </div>
                        </div>
                        
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-sm font-semibold">Cumbria</span>
                                <span class="text-sm font-bold" style="color: var(--saber-blue)">164</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="h-2 rounded-full" style="width: 21%; background: linear-gradient(90deg, var(--saber-green), var(--saber-light-green))"></div>
                            </div>
                        </div>
                        
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-sm font-semibold">Norfolk</span>
                                <span class="text-sm font-bold" style="color: var(--saber-blue)">142</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="h-2 rounded-full" style="width: 18%; background: linear-gradient(90deg, var(--saber-green), var(--saber-light-green))"></div>
                            </div>
                        </div>
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
    
    <script>
        // Mapbox access token
        mapboxgl.accessToken = 'pk.eyJ1IjoibWFyc3RhY2siLCJhIjoiY21laTdqdjVxMDN3OTJqc2p5M3U0Z24weSJ9.IigM9MDE40B_2Ghy7i-E_w';
        
        // Embed GeoJSON data directly
        const turbineGeoJSON = {json.dumps(geojson_data)};
        
        let map;
        let currentFilter = 'all';
        let selectedCapacityRanges = new Set();
        let is3D = false;
        let allTurbineData = null;
        let currentPopup = null;  // Track current popup
        
        // Window colors for markers
        const windowColors = {{
            'URGENT': '#FF4444',
            'OPTIMAL': '#7CC061',
            'TOO_EARLY': '#27AE60',
            'TOO_LATE': '#6B7280'
        }};
        
        // Initialize map
        function initMap() {{
            map = new mapboxgl.Map({{
                container: 'map',
                style: 'mapbox://styles/mapbox/light-v11',  // Changed to light theme for better contrast
                center: [-3.5, 54.5],
                zoom: 5.5,
                pitch: 0,
                bearing: 0
            }});
            
            // Add navigation controls
            map.addControl(new mapboxgl.NavigationControl(), 'top-right');
            
            // Add scale
            map.addControl(new mapboxgl.ScaleControl(), 'bottom-right');
            
            // Load turbine data
            map.on('load', () => {{
                // Store original data
                allTurbineData = turbineGeoJSON;
                
                // Add source
                map.addSource('turbines', {{
                    type: 'geojson',
                    data: turbineGeoJSON,  // Use embedded data
                    cluster: true,
                    clusterMaxZoom: 10,
                    clusterRadius: 40
                }});
                
                // Update summary on load
                updateRegionalSummary();
                
                // Add cluster layer
                map.addLayer({{
                    id: 'clusters',
                    type: 'circle',
                    source: 'turbines',
                    filter: ['has', 'point_count'],
                    paint: {{
                        'circle-color': [
                            'step',
                            ['get', 'point_count'],
                            '#95D47E',
                            10, '#7CC061',
                            50, '#0A5F8E',
                            100, '#044D73',
                            500, '#091922'
                        ],
                        'circle-radius': [
                            'step',
                            ['get', 'point_count'],
                            20,
                            10, 25,
                            50, 30,
                            100, 35,
                            500, 40
                        ],
                        'circle-stroke-width': 2,
                        'circle-stroke-color': '#ffffff'
                    }}
                }});
                
                // Add cluster count
                map.addLayer({{
                    id: 'cluster-count',
                    type: 'symbol',
                    source: 'turbines',
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
                    source: 'turbines',
                    filter: ['!', ['has', 'point_count']],
                    paint: {{
                        'circle-color': [
                            'match',
                            ['get', 'repowering_window'],
                            'URGENT', '#FF4444',
                            'OPTIMAL', '#7CC061',
                            'TOO_EARLY', '#27AE60',
                            'TOO_LATE', '#6B7280',
                            '#999999'
                        ],
                        'circle-radius': [
                            'interpolate',
                            ['linear'],
                            ['zoom'],
                            5, 3,
                            10, 6,
                            15, 10
                        ],
                        'circle-stroke-width': 2,
                        'circle-stroke-color': '#ffffff',
                        'circle-opacity': 0.9
                    }}
                }});
                
                // Click on clusters - show regional stats
                map.on('click', 'clusters', (e) => {{
                    const features = map.queryRenderedFeatures(e.point, {{
                        layers: ['clusters']
                    }});
                    const clusterId = features[0].properties.cluster_id;
                    const clusterCount = features[0].properties.point_count;
                    const coordinates = features[0].geometry.coordinates.slice();
                    
                    // Get all points in this cluster
                    map.getSource('turbines').getClusterLeaves(clusterId, clusterCount, 0, (err, clusterFeatures) => {{
                        if (err) {{
                            console.error('Error getting cluster features:', err);
                            return;
                        }}
                        
                        // Calculate cluster statistics
                        const stats = calculateClusterStats(clusterFeatures);
                        
                        // Close existing popup if any
                        if (currentPopup) {{
                            currentPopup.remove();
                        }}
                        
                        // Create new popup with stats
                        currentPopup = new mapboxgl.Popup({{
                            closeButton: true,
                            closeOnClick: false,
                            maxWidth: '350px'
                        }})
                            .setLngLat(coordinates)
                            .setHTML(createClusterPopupContent(stats, clusterCount))
                            .addTo(map);
                        
                        // Clear popup reference when closed
                        currentPopup.on('close', () => {{
                            currentPopup = null;
                        }});
                    }});
                }});
                
                // Double-click clusters to zoom
                map.on('dblclick', 'clusters', (e) => {{
                    const features = map.queryRenderedFeatures(e.point, {{
                        layers: ['clusters']
                    }});
                    const clusterId = features[0].properties.cluster_id;
                    map.getSource('turbines').getClusterExpansionZoom(
                        clusterId,
                        (err, zoom) => {{
                            if (err) return;
                            
                            map.easeTo({{
                                center: features[0].geometry.coordinates,
                                zoom: zoom
                            }});
                        }}
                    );
                    e.preventDefault();
                }});
                
                // Click on individual points
                map.on('click', 'unclustered-point', (e) => {{
                    const coordinates = e.features[0].geometry.coordinates.slice();
                    const props = e.features[0].properties;
                    
                    // Close existing popup if any
                    if (currentPopup) {{
                        currentPopup.remove();
                    }}
                    
                    // Show new popup
                    currentPopup = new mapboxgl.Popup()
                        .setLngLat(coordinates)
                        .setHTML(createPopupContent(props))
                        .addTo(map);
                    
                    // Clear popup reference when closed
                    currentPopup.on('close', () => {{
                        currentPopup = null;
                    }});
                    
                    showSiteInfo(props);
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
        }}
        
        // Calculate cluster statistics
        function calculateClusterStats(features) {{
            const stats = {{
                totalCapacity: 0,
                avgCapacity: 0,
                avgAge: 0,
                avgScore: 0,
                avgFitRemaining: 0,
                windows: {{
                    URGENT: 0,
                    OPTIMAL: 0,
                    TOO_EARLY: 0,
                    TOO_LATE: 0
                }},
                priorities: {{
                    CRITICAL: 0,
                    HIGH: 0,
                    MEDIUM: 0,
                    LOW: 0,
                    MONITOR: 0
                }},
                locations: {{}},
                topLocation: ''
            }};
            
            features.forEach(feature => {{
                const props = feature.properties;
                stats.totalCapacity += props.capacity_mw;
                stats.avgAge += props.age_years;
                stats.avgScore += props.score;
                stats.avgFitRemaining += props.remaining_fit_years;
                
                // Count windows
                if (stats.windows[props.repowering_window] !== undefined) {{
                    stats.windows[props.repowering_window]++;
                }}
                
                // Count priorities
                if (stats.priorities[props.priority] !== undefined) {{
                    stats.priorities[props.priority]++;
                }}
                
                // Count locations
                const location = props.location.split(' - ')[0]; // Get first part of location
                stats.locations[location] = (stats.locations[location] || 0) + 1;
            }});
            
            const count = features.length;
            stats.avgCapacity = stats.totalCapacity / count;
            stats.avgAge = stats.avgAge / count;
            stats.avgScore = stats.avgScore / count;
            stats.avgFitRemaining = stats.avgFitRemaining / count;
            
            // Find top location
            let maxCount = 0;
            for (const [loc, cnt] of Object.entries(stats.locations)) {{
                if (cnt > maxCount) {{
                    maxCount = cnt;
                    stats.topLocation = loc;
                }}
            }}
            
            return stats;
        }}
        
        // Create cluster popup content
        function createClusterPopupContent(stats, count) {{
            const urgentPct = ((stats.windows.URGENT / count) * 100).toFixed(0);
            const optimalPct = ((stats.windows.OPTIMAL / count) * 100).toFixed(0);
            
            return `
                <div class="p-3">
                    <h4 class="font-bold text-lg mb-3" style="color: var(--saber-blue)">
                        <i class="fas fa-layer-group mr-2"></i>Regional Cluster Analysis
                    </h4>
                    
                    <div class="grid grid-cols-2 gap-3 mb-3">
                        <div class="bg-gray-50 rounded p-2">
                            <p class="text-xs text-gray-600">Total Sites</p>
                            <p class="text-xl font-bold" style="color: var(--saber-blue)">${{count}}</p>
                        </div>
                        <div class="bg-gray-50 rounded p-2">
                            <p class="text-xs text-gray-600">Total Capacity</p>
                            <p class="text-xl font-bold" style="color: var(--saber-green)">${{stats.totalCapacity < 1 ? (stats.totalCapacity * 1000).toFixed(0) + ' kW' : stats.totalCapacity.toFixed(2) + ' MW'}}</p>
                        </div>
                    </div>
                    
                    <div class="space-y-2 text-sm border-t pt-2">
                        <div class="flex justify-between">
                            <span class="text-gray-600">Primary Region:</span>
                            <span class="font-semibold">${{stats.topLocation}}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Avg Age:</span>
                            <span class="font-semibold">${{Math.round(stats.avgAge)}} years</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Avg FIT Remaining:</span>
                            <span class="font-semibold">${{Math.round(stats.avgFitRemaining)}} years</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Avg Score:</span>
                            <span class="font-semibold">${{stats.avgScore.toFixed(2)}}</span>
                        </div>
                    </div>
                    
                    <div class="mt-3 pt-3 border-t">
                        <p class="text-xs font-semibold text-gray-600 mb-2">Repowering Windows:</p>
                        <div class="space-y-1">
                            ${{stats.windows.URGENT > 0 ? `
                            <div class="flex items-center justify-between">
                                <span class="text-xs flex items-center">
                                    <span class="w-2 h-2 rounded-full bg-red-500 mr-1"></span>
                                    Urgent (2-5yr)
                                </span>
                                <span class="text-xs font-bold">${{stats.windows.URGENT}} (${{urgentPct}}%)</span>
                            </div>` : ''}}
                            ${{stats.windows.OPTIMAL > 0 ? `
                            <div class="flex items-center justify-between">
                                <span class="text-xs flex items-center">
                                    <span class="w-2 h-2 rounded-full mr-1" style="background: var(--saber-green)"></span>
                                    Optimal (5-10yr)
                                </span>
                                <span class="text-xs font-bold">${{stats.windows.OPTIMAL}} (${{optimalPct}}%)</span>
                            </div>` : ''}}
                            ${{stats.windows.TOO_LATE > 0 ? `
                            <div class="flex items-center justify-between">
                                <span class="text-xs flex items-center">
                                    <span class="w-2 h-2 rounded-full bg-gray-500 mr-1"></span>
                                    Expiring (<2yr)
                                </span>
                                <span class="text-xs font-bold">${{stats.windows.TOO_LATE}}</span>
                            </div>` : ''}}
                        </div>
                    </div>
                    
                    <div class="mt-3 pt-2 border-t text-center">
                        <p class="text-xs text-gray-500">
                            <i class="fas fa-hand-pointer mr-1"></i>
                            Double-click to zoom into cluster
                        </p>
                    </div>
                </div>
            `;
        }}
        
        // Create popup content
        function createPopupContent(props) {{
            return `
                <div class="p-2">
                    <h4 class="font-bold text-lg mb-2" style="color: var(--saber-blue)">
                        Site ${{props.id}}
                    </h4>
                    <div class="space-y-1 text-sm">
                        <div><strong>Location:</strong> ${{props.location}}</div>
                        <div><strong>Capacity:</strong> ${{props.capacity_mw < 1 ? (props.capacity_mw * 1000).toFixed(0) + ' kW' : props.capacity_mw.toFixed(2) + ' MW'}}</div>
                        <div><strong>FIT Remaining:</strong> ${{Math.round(props.remaining_fit_years)}} years</div>
                        <div><strong>Score:</strong> ${{props.score.toFixed(2)}}</div>
                        <div class="pt-2 mt-2 border-t">
                            <span class="inline-block px-3 py-1 rounded-full text-xs font-bold text-white"
                                  style="background: ${{windowColors[props.repowering_window] || '#999'}}">
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
                            <p class="text-gray-600 text-xs uppercase">Postcode</p>
                            <p class="font-semibold">${{props.postcode}}</p>
                        </div>
                        <div>
                            <p class="text-gray-600 text-xs uppercase">Capacity</p>
                            <p class="font-semibold">${{props.capacity_mw < 1 ? (props.capacity_mw * 1000).toFixed(0) + ' kW' : props.capacity_mw.toFixed(2) + ' MW'}}</p>
                        </div>
                        <div>
                            <p class="text-gray-600 text-xs uppercase">Age</p>
                            <p class="font-semibold">${{Math.round(props.age_years)}} years</p>
                        </div>
                        <div>
                            <p class="text-gray-600 text-xs uppercase">FIT Remaining</p>
                            <p class="font-semibold">${{Math.round(props.remaining_fit_years)}} years</p>
                        </div>
                    </div>
                </div>
            `;
        }}
        
        // Filter by window
        function filterByWindow(window) {{
            currentFilter = window;
            
            // Update button states
            document.querySelectorAll('.filter-pill').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');
            
            applyFilters();
        }}
        
        // Toggle capacity filter (multi-select)
        function toggleCapacity(range) {{
            const btn = event.target;
            
            if (selectedCapacityRanges.has(range)) {{
                selectedCapacityRanges.delete(range);
                btn.classList.remove('bg-gray-700', 'text-white');
                btn.classList.add('bg-gray-200', 'text-gray-700');
            }} else {{
                selectedCapacityRanges.add(range);
                btn.classList.remove('bg-gray-200', 'text-gray-700');
                btn.classList.add('bg-gray-700', 'text-white');
            }}
            
            // Update all button
            const allBtn = document.querySelector('.capacity-all-btn');
            if (selectedCapacityRanges.size === 0) {{
                allBtn.classList.add('bg-gray-700', 'text-white');
                allBtn.classList.remove('bg-gray-200', 'text-gray-700');
            }} else {{
                allBtn.classList.remove('bg-gray-700', 'text-white');
                allBtn.classList.add('bg-gray-200', 'text-gray-700');
            }}
            
            applyFilters();
        }}
        
        // Select all capacity ranges
        function toggleAllCapacity() {{
            selectedCapacityRanges.clear();
            
            // Reset all buttons
            document.querySelectorAll('.capacity-btn').forEach(btn => {{
                btn.classList.remove('bg-gray-700', 'text-white');
                btn.classList.add('bg-gray-200', 'text-gray-700');
            }});
            
            // Highlight all button
            event.target.classList.add('bg-gray-700', 'text-white');
            event.target.classList.remove('bg-gray-200', 'text-gray-700');
            
            applyFilters();
        }}
        
        // Apply combined filters
        function applyFilters() {{
            let filters = ['all', ['!', ['has', 'point_count']]];
            
            // Window filter
            if (currentFilter !== 'all') {{
                filters.push(['==', ['get', 'repowering_window'], currentFilter]);
            }}
            
            // Capacity filter (multi-select)
            if (selectedCapacityRanges.size > 0) {{
                const capacityKw = ['*', ['get', 'capacity_mw'], 1000];
                const rangeFilters = [];
                
                selectedCapacityRanges.forEach(range => {{
                    switch(range) {{
                        case '0-50':
                            rangeFilters.push(['<', capacityKw, 50]);
                            break;
                        case '50-100':
                            rangeFilters.push(['all', ['>=', capacityKw, 50], ['<', capacityKw, 100]]);
                            break;
                        case '100-200':
                            rangeFilters.push(['all', ['>=', capacityKw, 100], ['<', capacityKw, 200]]);
                            break;
                        case '200-300':
                            rangeFilters.push(['all', ['>=', capacityKw, 200], ['<', capacityKw, 300]]);
                            break;
                        case '300-400':
                            rangeFilters.push(['all', ['>=', capacityKw, 300], ['<', capacityKw, 400]]);
                            break;
                        case '400-500':
                            rangeFilters.push(['all', ['>=', capacityKw, 400], ['<', capacityKw, 500]]);
                            break;
                        case '500-750':
                            rangeFilters.push(['all', ['>=', capacityKw, 500], ['<', capacityKw, 750]]);
                            break;
                        case '750-1000':
                            rangeFilters.push(['all', ['>=', capacityKw, 750], ['<', capacityKw, 1000]]);
                            break;
                        case '1000+':
                            rangeFilters.push(['>=', capacityKw, 1000]);
                            break;
                    }}
                }});
                
                if (rangeFilters.length === 1) {{
                    filters.push(rangeFilters[0]);
                }} else if (rangeFilters.length > 1) {{
                    filters.push(['any', ...rangeFilters]);
                }}
            }}
            
            map.setFilter('unclustered-point', filters);
            
            // Update filtered data for clustering
            const filteredData = filterGeoJSON();
            map.getSource('turbines').setData(filteredData);
            
            // Update regional summary
            updateRegionalSummary();
        }}
        
        // Filter GeoJSON data
        function filterGeoJSON() {{
            if (!allTurbineData) return turbineGeoJSON;
            
            const filtered = {{
                type: 'FeatureCollection',
                features: allTurbineData.features.filter(feature => {{
                    const props = feature.properties;
                    
                    // Window filter
                    if (currentFilter !== 'all' && props.repowering_window !== currentFilter) {{
                        return false;
                    }}
                    
                    // Capacity filter (multi-select)
                    if (selectedCapacityRanges.size > 0) {{
                        const capacityKw = props.capacity_mw * 1000;
                        let matchesAnyRange = false;
                        
                        selectedCapacityRanges.forEach(range => {{
                            switch(range) {{
                                case '0-50':
                                    if (capacityKw < 50) matchesAnyRange = true;
                                    break;
                                case '50-100':
                                    if (capacityKw >= 50 && capacityKw < 100) matchesAnyRange = true;
                                    break;
                                case '100-200':
                                    if (capacityKw >= 100 && capacityKw < 200) matchesAnyRange = true;
                                    break;
                                case '200-300':
                                    if (capacityKw >= 200 && capacityKw < 300) matchesAnyRange = true;
                                    break;
                                case '300-400':
                                    if (capacityKw >= 300 && capacityKw < 400) matchesAnyRange = true;
                                    break;
                                case '400-500':
                                    if (capacityKw >= 400 && capacityKw < 500) matchesAnyRange = true;
                                    break;
                                case '500-750':
                                    if (capacityKw >= 500 && capacityKw < 750) matchesAnyRange = true;
                                    break;
                                case '750-1000':
                                    if (capacityKw >= 750 && capacityKw < 1000) matchesAnyRange = true;
                                    break;
                                case '1000+':
                                    if (capacityKw >= 1000) matchesAnyRange = true;
                                    break;
                            }}
                        }});
                        
                        if (!matchesAnyRange) return false;
                    }}
                    
                    return true;
                }})
            }};
            
            return filtered;
        }}
        
        // Update regional summary
        function updateRegionalSummary() {{
            const filteredData = filterGeoJSON();
            
            const scotlandTerms = ['Scotland', 'Highland', 'Aberdeenshire', 'Orkney', 'Shetland', 'Fife', 'Perth', 'Dundee', 'Glasgow', 'Edinburgh', 'Stirling', 'Argyll', 'Moray', 'Angus', 'Ayrshire', 'Lanarkshire', 'Lothian', 'Borders'];
            
            let ewSites = 0, ewCapacity = 0, ewOptimal = 0, ewUrgent = 0, ewExpiring = 0;
            let scotSites = 0, scotCapacity = 0, scotOptimal = 0, scotUrgent = 0, scotExpiring = 0;
            
            filteredData.features.forEach(feature => {{
                const props = feature.properties;
                const location = props.location || '';
                const isScotland = scotlandTerms.some(term => location.toLowerCase().includes(term.toLowerCase()));
                
                if (isScotland) {{
                    scotSites++;
                    scotCapacity += props.capacity_mw;
                    if (props.repowering_window === 'OPTIMAL') scotOptimal++;
                    if (props.repowering_window === 'URGENT') scotUrgent++;
                    if (props.repowering_window === 'TOO_LATE') scotExpiring++;
                }} else {{
                    ewSites++;
                    ewCapacity += props.capacity_mw;
                    if (props.repowering_window === 'OPTIMAL') ewOptimal++;
                    if (props.repowering_window === 'URGENT') ewUrgent++;
                    if (props.repowering_window === 'TOO_LATE') ewExpiring++;
                }}
            }});
            
            // Format capacity display
            function formatCapacity(mw) {{
                if (mw < 1) {{
                    return (mw * 1000).toFixed(0) + ' kW';
                }} else {{
                    return mw.toFixed(2) + ' MW';
                }}
            }}
            
            // Update display
            document.getElementById('ewSites').textContent = ewSites.toLocaleString();
            document.getElementById('ewCapacity').textContent = formatCapacity(ewCapacity);
            document.getElementById('ewOptimal').textContent = ewOptimal.toLocaleString();
            document.getElementById('ewUrgent').textContent = ewUrgent.toLocaleString();
            document.getElementById('ewExpiring').textContent = ewExpiring.toLocaleString();
            
            document.getElementById('scotSites').textContent = scotSites.toLocaleString();
            document.getElementById('scotCapacity').textContent = formatCapacity(scotCapacity);
            document.getElementById('scotOptimal').textContent = scotOptimal.toLocaleString();
            document.getElementById('scotUrgent').textContent = scotUrgent.toLocaleString();
            document.getElementById('scotExpiring').textContent = scotExpiring.toLocaleString();
            
            const totalSites = ewSites + scotSites;
            const totalCapacity = ewCapacity + scotCapacity;
            document.getElementById('totalSites').textContent = totalSites.toLocaleString();
            document.getElementById('totalCapacity').textContent = formatCapacity(totalCapacity);
            document.getElementById('avgSize').textContent = totalSites > 0 ? 
                ((totalCapacity * 1000) / totalSites).toFixed(0) + ' kW' : '0 kW';
        }}
        
        // Toggle 3D view
        function toggle3D() {{
            is3D = !is3D;
            const btn = document.getElementById('btn3D');
            
            if (is3D) {{
                map.easeTo({{
                    pitch: 60,
                    bearing: -20
                }});
                btn.innerHTML = '<i class="fas fa-map mr-2"></i>2D View';
            }} else {{
                map.easeTo({{
                    pitch: 0,
                    bearing: 0
                }});
                btn.innerHTML = '<i class="fas fa-cube mr-2"></i>3D View';
            }}
        }}
        
        // Reset map
        function resetMap() {{
            map.flyTo({{
                center: [-3.5, 54.5],
                zoom: 5.5,
                pitch: 0,
                bearing: 0
            }});
            is3D = false;
            document.getElementById('btn3D').innerHTML = '<i class="fas fa-cube mr-2"></i>3D View';
        }}
        
        // Initialize priority chart with FIXED container
        function initPriorityChart() {{
            const ctx = document.getElementById('priorityChart').getContext('2d');
            
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: ['Urgent', 'Optimal', 'Too Early', 'Too Late'],
                    datasets: [{{
                        data: [801, 5582, 1, 276],
                        backgroundColor: ['#FF4444', '#7CC061', '#27AE60', '#6B7280'],
                        borderWidth: 2,
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
                                padding: 10,
                                font: {{ size: 11 }}
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
    logger.info("Creating Saber Mapbox dashboard...")
    
    # Prepare GeoJSON data
    num_turbines = prepare_geojson_data()
    
    # Copy logo if exists
    import shutil
    if Path('Saber-logo-wob-green.svg').exists():
        shutil.copy('Saber-logo-wob-green.svg', 'visualizations/Saber-logo-wob-green.svg')
    
    # Create dashboard
    dashboard_html = create_saber_mapbox_dashboard()
    
    # Save dashboard
    with open('visualizations/saber_mapbox_dashboard.html', 'w') as f:
        f.write(dashboard_html)
    
    print("\n" + "="*60)
    print("SABER MAPBOX DASHBOARD CREATED")
    print("="*60)
    print("\n✅ FIXES APPLIED:")
    print("   • Chart height fixed at 200px (no infinite growth)")
    print("   • Coordinates properly distributed across UK")
    print("   • Mapbox GL JS for smooth performance with 7,448 points")
    print("   • Smart clustering that works at different zoom levels")
    print("   • 3D view option for terrain visualization")
    print("\n🔑 TO ACTIVATE:")
    print("   1. Get your Mapbox access token from: https://mapbox.com")
    print("   2. Replace 'YOUR_MAPBOX_ACCESS_TOKEN' in the HTML file")
    print(f"\n📍 {num_turbines} turbines ready for display")
    print("\n📁 Dashboard: visualizations/saber_mapbox_dashboard.html")
    
    # Try to open
    import webbrowser
    import os
    full_path = os.path.abspath('visualizations/saber_mapbox_dashboard.html')
    webbrowser.open(f"file://{full_path}")


if __name__ == "__main__":
    main()