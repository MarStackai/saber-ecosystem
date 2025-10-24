#!/usr/bin/env python3
"""
Create Saber Commercial Solar Dashboard V2
Matches wind dashboard UI with cohesive design
"""

import json
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

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
    """Create dashboard matching wind UI"""
    
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
        # Skip sites with invalid coordinates
        if site['latitude'] and site['longitude'] and not (pd.isna(site['latitude']) or pd.isna(site['longitude'])):
            color_map = {
                'IMMEDIATE': '#E74C3C',
                'URGENT': '#F39C12',
                'OPTIMAL': '#7CC061',
                'PLANNING': '#0A5F8E',
                'FUTURE': '#95D47E'
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
    <title>Saber Renewable Energy | Commercial Solar Intelligence Platform</title>
    
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
        
        /* Priority chart container */
        #priorityChartContainer {{
            height: 200px;
            position: relative;
        }}
        
        /* Table styles */
        .data-table {{
            width: 100%;
            font-size: 0.875rem;
        }}
        
        .data-table th {{
            background: linear-gradient(135deg, var(--saber-blue), var(--saber-light-blue));
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .data-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .data-table tbody tr:hover {{
            background: rgba(124, 192, 97, 0.1);
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
        <div class="container mx-auto px-6 py-6">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-6">
                    <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4" style="min-width: 200px;">
                        {logo_svg}
                    </div>
                    <div class="border-l-2 border-white/30 pl-6">
                        <h1 class="text-2xl">Commercial Solar Intelligence</h1>
                        <p class="text-sm opacity-90 font-light">35,617 C&I Installations • Zero Domestic</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="text-right">
                        <p class="text-2xl font-bold">{stats['total_sites']:,}</p>
                        <p class="text-xs opacity-90 uppercase">Commercial Sites</p>
                    </div>
                    <a href="saber_mapbox_dashboard.html" class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg hover:bg-white/30 transition text-white">
                        <i class="fas fa-wind mr-2"></i>Wind
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
                        <p class="text-3xl font-bold text-white">{stats['total_sites']:,}</p>
                        <p class="text-xs text-white/60 mt-1">Commercial only</p>
                    </div>
                    <div class="text-4xl text-white/30">
                        <i class="fas fa-solar-panel"></i>
                    </div>
                </div>
            </div>
            
            <div class="stat-card saber-card p-5">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Total Capacity</p>
                        <p class="text-3xl font-bold text-white">{stats['total_capacity_mw']:,.0f} MW</p>
                        <p class="text-xs text-white/60 mt-1">Installed solar</p>
                    </div>
                    <div class="text-4xl text-white/30">
                        <i class="fas fa-bolt"></i>
                    </div>
                </div>
            </div>
            
            <div class="stat-card saber-card p-5">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Immediate</p>
                        <p class="text-3xl font-bold text-white">{repowering.get('IMMEDIATE', 0) + repowering.get('URGENT', 0)}</p>
                        <p class="text-xs text-white/60 mt-1">Need action</p>
                    </div>
                    <div class="text-4xl text-white/30">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                </div>
            </div>
            
            <div class="stat-card saber-card p-5">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Optimal</p>
                        <p class="text-3xl font-bold text-white">{repowering.get('OPTIMAL', 0):,}</p>
                        <p class="text-xs text-white/60 mt-1">5-10yr window</p>
                    </div>
                    <div class="text-4xl text-white/30">
                        <i class="fas fa-bullseye"></i>
                    </div>
                </div>
            </div>
            
            <div class="stat-card saber-card p-5">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Sites ≥100kW</p>
                        <p class="text-3xl font-bold text-white">{stats['sites_over_100kw']:,}</p>
                        <p class="text-xs text-white/60 mt-1">Large scale</p>
                    </div>
                    <div class="text-4xl text-white/30">
                        <i class="fas fa-industry"></i>
                    </div>
                </div>
            </div>
            
            <div class="stat-card saber-card p-5">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Avg FIT Left</p>
                        <p class="text-3xl font-bold text-white">{stats['average_remaining_fit']:.1f} yr</p>
                        <p class="text-xs text-white/60 mt-1">Remaining</p>
                    </div>
                    <div class="text-4xl text-white/30">
                        <i class="fas fa-clock"></i>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Main Content Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <!-- Map Section (3/4 width) -->
            <div class="lg:col-span-3">
                <div class="saber-card p-6">
                    <div class="flex items-center justify-between mb-4">
                        <h2 class="text-xl">
                            <i class="fas fa-map-marked-alt mr-2" style="color: var(--saber-green)"></i>
                            UK Commercial Solar Map
                        </h2>
                        <div class="flex space-x-2">
                            <button onclick="resetMap()" class="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm transition">
                                <i class="fas fa-home mr-1"></i>Reset View
                            </button>
                        </div>
                    </div>
                    
                    <!-- Filter Pills -->
                    <div class="flex flex-wrap gap-2 mb-4">
                        <span class="text-sm text-gray-600 self-center font-semibold">Repowering Window:</span>
                        <button onclick="filterByWindow('all')" class="filter-pill px-4 py-2 rounded-lg text-sm active">
                            All ({len(sites):,})
                        </button>
                        <button onclick="filterByWindow('IMMEDIATE')" class="filter-pill px-4 py-2 rounded-lg text-sm">
                            Immediate ({repowering.get('IMMEDIATE', 0)})
                        </button>
                        <button onclick="filterByWindow('URGENT')" class="filter-pill px-4 py-2 rounded-lg text-sm">
                            Urgent ({repowering.get('URGENT', 0)})
                        </button>
                        <button onclick="filterByWindow('OPTIMAL')" class="filter-pill px-4 py-2 rounded-lg text-sm">
                            Optimal ({repowering.get('OPTIMAL', 0):,})
                        </button>
                        <button onclick="filterByWindow('PLANNING')" class="filter-pill px-4 py-2 rounded-lg text-sm">
                            Planning ({repowering.get('PLANNING', 0):,})
                        </button>
                    </div>
                    
                    <!-- Capacity Filters -->
                    <div class="flex items-center gap-4 mb-4">
                        <span class="text-sm text-gray-600 font-semibold">Capacity Range:</span>
                        <div class="flex flex-wrap gap-2">
                            <button onclick="toggleCapacityRange(0, 50, this)" class="filter-pill capacity-filter px-3 py-1 rounded text-xs" data-min="0" data-max="50">
                                <50kW
                            </button>
                            <button onclick="toggleCapacityRange(50, 250, this)" class="filter-pill capacity-filter px-3 py-1 rounded text-xs" data-min="50" data-max="250">
                                50-250kW
                            </button>
                            <button onclick="toggleCapacityRange(250, 500, this)" class="filter-pill capacity-filter px-3 py-1 rounded text-xs" data-min="250" data-max="500">
                                250-500kW
                            </button>
                            <button onclick="toggleCapacityRange(500, 750, this)" class="filter-pill capacity-filter px-3 py-1 rounded text-xs" data-min="500" data-max="750">
                                500-750kW
                            </button>
                            <button onclick="toggleCapacityRange(750, 1000, this)" class="filter-pill capacity-filter px-3 py-1 rounded text-xs" data-min="750" data-max="1000">
                                750kW-1MW
                            </button>
                            <button onclick="toggleCapacityRange(1000, 50000, this)" class="filter-pill capacity-filter px-3 py-1 rounded text-xs" data-min="1000" data-max="50000">
                                >1MW
                            </button>
                            <button onclick="toggleCapacityRange(0, 50000, this)" class="filter-pill capacity-filter px-3 py-1 rounded text-xs active" data-min="0" data-max="50000">
                                All Sizes
                            </button>
                        </div>
                    </div>
                    
                    <div id="map" style="height: 600px;"></div>
                </div>
                
                <!-- Regional Site Statistics -->
                <div class="saber-card p-6 mt-6">
                    <h3 class="text-lg mb-4">
                        <i class="fas fa-chart-bar mr-2" style="color: var(--saber-green)"></i>
                        Regional Site Statistics
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
                                    <span class="text-gray-600">Immediate:</span>
                                    <span class="font-bold text-red-600" id="ewImmediate">0</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-gray-600">Urgent:</span>
                                    <span class="font-bold text-orange-600" id="ewUrgent">0</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-gray-600">Optimal:</span>
                                    <span class="font-bold text-green-600" id="ewOptimal">0</span>
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
                                    <span class="text-gray-600">Immediate:</span>
                                    <span class="font-bold text-red-600" id="scotImmediate">0</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-gray-600">Urgent:</span>
                                    <span class="font-bold text-orange-600" id="scotUrgent">0</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-gray-600">Optimal:</span>
                                    <span class="font-bold text-green-600" id="scotOptimal">0</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="bg-green-50 p-3 rounded">
                            <h4 class="font-semibold text-sm text-green-900 mb-2">Total UK Portfolio</h4>
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
                                    <span class="text-gray-600">Avg Age:</span>
                                    <span class="font-bold" id="avgAge">0 yr</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-gray-600">Avg FIT:</span>
                                    <span class="font-bold" id="avgFit">0 yr</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-gray-600">Efficiency:</span>
                                    <span class="font-bold text-blue-600" id="avgEfficiency">0%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Side Panel (1/4 width) -->
            <div class="space-y-6">
                <!-- Site Intelligence -->
                <div class="saber-card p-6">
                    <h3 class="text-lg mb-4">
                        <i class="fas fa-info-circle mr-2" style="color: var(--saber-green)"></i>
                        Site Intelligence
                    </h3>
                    <div id="siteDetails" class="space-y-3 text-sm">
                        <p class="text-gray-500 text-center py-8">
                            Click a site on the map for details
                        </p>
                    </div>
                </div>
                
                <!-- AI Assistant Chat -->
                <div class="saber-card p-6">
                    <h3 class="text-lg mb-4">
                        <i class="fas fa-robot mr-2" style="color: var(--saber-green)"></i>
                        AI Data Assistant
                        <button onclick="toggleChatConfig()" class="float-right text-xs text-gray-500 hover:text-gray-700">
                            <i class="fas fa-cog"></i>
                        </button>
                    </h3>
                    
                    <!-- API Configuration (hidden by default) -->
                    <div id="chatConfig" class="hidden mb-4 p-3 bg-gray-50 rounded">
                        <label class="block text-xs font-semibold mb-1">OpenRouter API Key:</label>
                        <input type="password" id="apiKey" placeholder="sk-or-..." class="w-full px-2 py-1 text-xs border rounded mb-2">
                        <label class="block text-xs font-semibold mb-1">Model:</label>
                        <select id="aiModel" class="w-full px-2 py-1 text-xs border rounded mb-2">
                            <option value="openai/gpt-3.5-turbo">GPT-3.5 Turbo (Fast & Cheap)</option>
                            <option value="anthropic/claude-3-haiku">Claude 3 Haiku (Fast & Smart)</option>
                            <option value="google/gemini-flash-1.5">Gemini 1.5 Flash (Very Fast)</option>
                            <option value="meta-llama/llama-3.1-8b-instruct">Llama 3.1 8B (Free Tier)</option>
                            <option value="anthropic/claude-3-sonnet">Claude 3 Sonnet (Balanced)</option>
                            <option value="openai/gpt-4o-mini">GPT-4o Mini (Smart & Affordable)</option>
                        </select>
                        <button onclick="saveApiConfig()" class="w-full bg-green-600 text-white px-3 py-1 rounded text-xs hover:bg-green-700">
                            Save Configuration
                        </button>
                    </div>
                    
                    <!-- Chat Messages -->
                    <div id="chatMessages" class="h-64 overflow-y-auto mb-3 p-3 bg-gray-50 rounded text-sm">
                        <div class="text-gray-500 text-center">
                            <p class="mb-2">Ask questions about the solar data!</p>
                            <p class="text-xs">Examples:</p>
                            <p class="text-xs italic">"How many sites are in Scotland?"</p>
                            <p class="text-xs italic">"What's the total capacity over 500kW?"</p>
                            <p class="text-xs italic">"Which regions have most urgent repowering?"</p>
                        </div>
                    </div>
                    
                    <!-- Chat Input -->
                    <div class="flex gap-2">
                        <input type="text" id="chatInput" placeholder="Ask about the data..." 
                               class="flex-1 px-3 py-2 border rounded text-sm" 
                               onkeypress="if(event.key==='Enter') sendChatMessage()">
                        <button onclick="sendChatMessage()" 
                                class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Priority Analysis -->
                <div class="saber-card p-6">
                    <h3 class="text-lg mb-4">
                        <i class="fas fa-chart-pie mr-2" style="color: var(--saber-green)"></i>
                        Window Distribution
                    </h3>
                    <div id="priorityChartContainer">
                        <canvas id="priorityChart"></canvas>
                    </div>
                </div>
                
                <!-- Regional Distribution -->
                <div class="saber-card p-6">
                    <h3 class="text-lg mb-4">
                        <i class="fas fa-chart-bar mr-2" style="color: var(--saber-green)"></i>
                        Top Regions (MW)
                    </h3>
                    <div class="space-y-2">
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-sm font-semibold">South West</span>
                                <span class="text-sm font-bold" style="color: var(--saber-blue)">603 MW</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="h-2 rounded-full" style="width: 100%; background: linear-gradient(90deg, var(--saber-green), var(--saber-light-green))"></div>
                            </div>
                        </div>
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-sm font-semibold">South East</span>
                                <span class="text-sm font-bold" style="color: var(--saber-blue)">301 MW</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="h-2 rounded-full" style="width: 50%; background: linear-gradient(90deg, var(--saber-green), var(--saber-light-green))"></div>
                            </div>
                        </div>
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-sm font-semibold">East England</span>
                                <span class="text-sm font-bold" style="color: var(--saber-blue)">234 MW</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="h-2 rounded-full" style="width: 39%; background: linear-gradient(90deg, var(--saber-green), var(--saber-light-green))"></div>
                            </div>
                        </div>
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-sm font-semibold">East Midlands</span>
                                <span class="text-sm font-bold" style="color: var(--saber-blue)">227 MW</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="h-2 rounded-full" style="width: 38%; background: linear-gradient(90deg, var(--saber-green), var(--saber-light-green))"></div>
                            </div>
                        </div>
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-sm font-semibold">West Midlands</span>
                                <span class="text-sm font-bold" style="color: var(--saber-blue)">193 MW</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="h-2 rounded-full" style="width: 32%; background: linear-gradient(90deg, var(--saber-green), var(--saber-light-green))"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Initialize Mapbox
        mapboxgl.accessToken = 'pk.eyJ1IjoibWFyc3RhY2siLCJhIjoiY21laTdqdjVxMDN3OTJqc2p5M3U0Z24weSJ9.IigM9MDE40B_2Ghy7i-E_w';
        
        let map;
        let currentPopup = null;
        let filteredData = {json.dumps(geojson)};
        let currentFilters = {{
            window: 'all',
            minCapacity: 0,
            maxCapacity: 50000
        }};
        
        // Initialize map
        function initMap() {{
            map = new mapboxgl.Map({{
                container: 'map',
                style: 'mapbox://styles/mapbox/light-v11',
                center: [-2, 53],
                zoom: 5.5,
                pitch: 0,
                bearing: 0
            }});
            
            map.addControl(new mapboxgl.NavigationControl(), 'top-right');
            
            map.on('load', () => {{
                loadMapData();
            }});
        }}
        
        function loadMapData() {{
            // Update regional stats on initial load
            updateRegionalStats(filteredData.features);
            
            // Add source with clustering
            map.addSource('solar-sites', {{
                type: 'geojson',
                data: filteredData,
                cluster: true,
                clusterMaxZoom: 15,
                clusterRadius: 40,
                clusterProperties: {{
                    'total_capacity': ['+', ['get', 'capacity_mw']],
                    'sum_fit': ['+', ['get', 'remaining_fit_years']]
                }}
            }});
            
            // Add cluster layer
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
                        10, '#7CC061',
                        50, '#0A5F8E',
                        100, '#044D73'
                    ],
                    'circle-radius': [
                        'step',
                        ['get', 'point_count'],
                        20, 10, 25,
                        50, 30, 100, 35
                    ],
                    'circle-stroke-width': 2,
                    'circle-stroke-color': '#fff'
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
            
            // Add unclustered points
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
                        0, 5,
                        100, 8,
                        1000, 12,
                        5000, 16
                    ],
                    'circle-stroke-width': 2,
                    'circle-stroke-color': '#fff',
                    'circle-opacity': 0.9
                }}
            }});
            
            // Click on clusters - show detailed stats
            map.on('click', 'clusters', (e) => {{
                const features = map.queryRenderedFeatures(e.point, {{ layers: ['clusters'] }});
                const clusterId = features[0].properties.cluster_id;
                
                // Get all features in cluster for detailed stats
                map.getSource('solar-sites').getClusterLeaves(clusterId, 999, 0, (err, clusterFeatures) => {{
                    if (err) return;
                    
                    const stats = calculateClusterStats(clusterFeatures);
                    const count = features[0].properties.point_count;
                    
                    if (currentPopup) currentPopup.remove();
                    
                    currentPopup = new mapboxgl.Popup({{
                        closeButton: true,
                        maxWidth: '350px'
                    }})
                        .setLngLat(features[0].geometry.coordinates)
                        .setHTML(createClusterPopupContent(stats, count))
                        .addTo(map);
                }});
            }});
            
            // Double-click clusters to zoom
            map.on('dblclick', 'clusters', (e) => {{
                const features = map.queryRenderedFeatures(e.point, {{ layers: ['clusters'] }});
                const clusterId = features[0].properties.cluster_id;
                map.getSource('solar-sites').getClusterExpansionZoom(clusterId, (err, zoom) => {{
                    if (err) return;
                    map.easeTo({{
                        center: features[0].geometry.coordinates,
                        zoom: zoom
                    }});
                }});
                e.preventDefault();
            }});
            
            // Click on individual points
            map.on('click', 'unclustered-point', (e) => {{
                const coordinates = e.features[0].geometry.coordinates.slice();
                const props = e.features[0].properties;
                
                if (currentPopup) currentPopup.remove();
                
                currentPopup = new mapboxgl.Popup()
                    .setLngLat(coordinates)
                    .setHTML(createPopupContent(props))
                    .addTo(map);
                
                showSiteInfo(props);
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
        }}
        
        // Calculate cluster statistics
        function calculateClusterStats(features) {{
            const stats = {{
                totalCapacity: 0,
                avgCapacity: 0,
                avgAge: 0,
                avgFitRemaining: 0,
                windows: {{
                    IMMEDIATE: 0,
                    URGENT: 0,
                    OPTIMAL: 0,
                    PLANNING: 0,
                    FUTURE: 0
                }},
                regions: {{}},
                topRegion: '',
                sizeCategories: {{}}
            }};
            
            features.forEach(f => {{
                const props = f.properties;
                stats.totalCapacity += props.capacity_mw;
                stats.avgAge += props.age_years;
                stats.avgFitRemaining += props.remaining_fit_years;
                
                // Count windows
                if (stats.windows[props.repowering_window] !== undefined) {{
                    stats.windows[props.repowering_window]++;
                }}
                
                // Count regions
                if (!stats.regions[props.region]) {{
                    stats.regions[props.region] = 0;
                }}
                stats.regions[props.region]++;
                
                // Count size categories
                if (!stats.sizeCategories[props.size_category]) {{
                    stats.sizeCategories[props.size_category] = 0;
                }}
                stats.sizeCategories[props.size_category]++;
            }});
            
            const count = features.length;
            stats.avgCapacity = stats.totalCapacity / count;
            stats.avgAge = stats.avgAge / count;
            stats.avgFitRemaining = stats.avgFitRemaining / count;
            
            // Find top region
            let maxRegionCount = 0;
            for (const region in stats.regions) {{
                if (stats.regions[region] > maxRegionCount) {{
                    maxRegionCount = stats.regions[region];
                    stats.topRegion = region;
                }}
            }}
            
            return stats;
        }}
        
        // Create detailed cluster popup
        function createClusterPopupContent(stats, count) {{
            const immediatePct = ((stats.windows.IMMEDIATE / count) * 100).toFixed(0);
            const urgentPct = ((stats.windows.URGENT / count) * 100).toFixed(0);
            const optimalPct = ((stats.windows.OPTIMAL / count) * 100).toFixed(0);
            
            return `
                <div class="p-3">
                    <h4 class="font-bold text-lg mb-3" style="color: var(--saber-blue)">
                        <i class="fas fa-layer-group mr-2"></i>Cluster Analysis
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
                            <span class="font-semibold">${{stats.topRegion}}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Avg Capacity:</span>
                            <span class="font-semibold">${{stats.avgCapacity < 1 ? (stats.avgCapacity * 1000).toFixed(0) + ' kW' : stats.avgCapacity.toFixed(2) + ' MW'}}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Avg Age:</span>
                            <span class="font-semibold">${{Math.round(stats.avgAge)}} years</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Avg FIT Remaining:</span>
                            <span class="font-semibold">${{Math.round(stats.avgFitRemaining)}} years</span>
                        </div>
                    </div>
                    
                    <div class="mt-3 pt-3 border-t">
                        <p class="text-xs font-semibold text-gray-600 mb-2">Repowering Windows:</p>
                        <div class="space-y-1">
                            ${{stats.windows.IMMEDIATE > 0 ? `
                            <div class="flex items-center justify-between">
                                <span class="text-xs flex items-center">
                                    <span class="w-2 h-2 rounded-full bg-red-500 mr-1"></span>
                                    Immediate (<2yr)
                                </span>
                                <span class="text-xs font-bold">${{stats.windows.IMMEDIATE}} (${{immediatePct}}%)</span>
                            </div>` : ''}}
                            ${{stats.windows.URGENT > 0 ? `
                            <div class="flex items-center justify-between">
                                <span class="text-xs flex items-center">
                                    <span class="w-2 h-2 rounded-full bg-orange-500 mr-1"></span>
                                    Urgent (2-5yr)
                                </span>
                                <span class="text-xs font-bold">${{stats.windows.URGENT}} (${{urgentPct}}%)</span>
                            </div>` : ''}}
                            ${{stats.windows.OPTIMAL > 0 ? `
                            <div class="flex items-center justify-between">
                                <span class="text-xs flex items-center">
                                    <span class="w-2 h-2 rounded-full bg-green-500 mr-1"></span>
                                    Optimal (5-10yr)
                                </span>
                                <span class="text-xs font-bold">${{stats.windows.OPTIMAL}} (${{optimalPct}}%)</span>
                            </div>` : ''}}
                        </div>
                    </div>
                    
                    <div class="mt-3 pt-3 border-t text-center">
                        <p class="text-xs text-gray-500">Double-click to zoom in</p>
                    </div>
                </div>
            `;
        }}
        
        // Create detailed site popup
        function createPopupContent(props) {{
            const windowColors = {{
                'IMMEDIATE': '#E74C3C',
                'URGENT': '#F39C12',
                'OPTIMAL': '#7CC061',
                'PLANNING': '#0A5F8E',
                'FUTURE': '#95D47E'
            }};
            
            return `
                <div class="p-2">
                    <h4 class="font-bold text-lg mb-2" style="color: var(--saber-blue)">
                        ${{props.size_category}}
                    </h4>
                    <div class="grid grid-cols-2 gap-2 mb-2 text-sm">
                        <div class="bg-gray-50 rounded p-2">
                            <p class="text-xs text-gray-600">Capacity</p>
                            <p class="font-bold">${{props.capacity_kw < 1000 ? props.capacity_kw + ' kW' : props.capacity_mw.toFixed(2) + ' MW'}}</p>
                        </div>
                        <div class="bg-gray-50 rounded p-2">
                            <p class="text-xs text-gray-600">FIT Remaining</p>
                            <p class="font-bold">${{Math.round(props.remaining_fit_years)}} years</p>
                        </div>
                    </div>
                    <div class="space-y-1 text-sm">
                        <div><strong>Postcode:</strong> ${{props.postcode}}</div>
                        <div><strong>Region:</strong> ${{props.region}}</div>
                        <div><strong>System Age:</strong> ${{Math.round(props.age_years)}} years</div>
                        <div><strong>Annual Generation:</strong> ${{props.annual_generation_mwh}} MWh</div>
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
                        <strong class="text-gray-600">Site Type:</strong>
                        <span class="font-bold" style="color: var(--saber-blue)">${{props.size_category}}</span>
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <p class="text-gray-600 text-xs uppercase">Postcode</p>
                            <p class="font-semibold">${{props.postcode}}</p>
                        </div>
                        <div>
                            <p class="text-gray-600 text-xs uppercase">Capacity</p>
                            <p class="font-semibold">${{props.capacity_kw < 1000 ? props.capacity_kw + ' kW' : props.capacity_mw.toFixed(2) + ' MW'}}</p>
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
                    <div class="pt-3 space-y-2">
                        <div>
                            <p class="text-gray-600 text-xs uppercase">Region</p>
                            <p class="font-semibold">${{props.region}}</p>
                        </div>
                        <div>
                            <p class="text-gray-600 text-xs uppercase">Annual Generation</p>
                            <p class="font-semibold">${{props.annual_generation_mwh}} MWh</p>
                        </div>
                        <div>
                            <p class="text-gray-600 text-xs uppercase">Repowering Window</p>
                            <span class="inline-block px-3 py-1 rounded-full text-xs font-bold text-white window-${{props.repowering_window.toLowerCase()}}">
                                ${{props.repowering_window}}
                            </span>
                        </div>
                    </div>
                </div>
            `;
        }}
        
        // Filter functions
        function filterByWindow(window) {{
            currentFilters.window = window;
            
            // Update button states
            document.querySelectorAll('.filter-pill').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');
            
            applyFilters();
        }}
        
        // Multi-select capacity filter
        let selectedCapacityRanges = new Set(['all']);
        
        function toggleCapacityRange(min, max, button) {{
            const rangeKey = `${{min}}-${{max || 'Infinity'}}`;
            
            if (min === 0 && max === 50000) {{
                // "All" button clicked
                selectedCapacityRanges.clear();
                selectedCapacityRanges.add('all');
                document.querySelectorAll('.capacity-filter').forEach(btn => {{
                    btn.classList.remove('active');
                }});
                button.classList.add('active');
            }} else {{
                // Specific range clicked
                if (selectedCapacityRanges.has('all')) {{
                    selectedCapacityRanges.clear();
                    document.querySelector('[data-min="0"][data-max="50000"]').classList.remove('active');
                }}
                
                if (selectedCapacityRanges.has(rangeKey)) {{
                    selectedCapacityRanges.delete(rangeKey);
                    button.classList.remove('active');
                }} else {{
                    selectedCapacityRanges.add(rangeKey);
                    button.classList.add('active');
                }}
                
                // If no ranges selected, default to "All"
                if (selectedCapacityRanges.size === 0) {{
                    selectedCapacityRanges.add('all');
                    document.querySelector('[data-min="0"][data-max="50000"]').classList.add('active');
                }}
            }}
            
            applyFilters();
        }}
        
        function applyFilters() {{
            // Filter the data
            const filtered = {{
                type: "FeatureCollection",
                features: {json.dumps(geojson)}.features.filter(f => {{
                    const props = f.properties;
                    
                    // Window filter
                    if (currentFilters.window !== 'all' && props.repowering_window !== currentFilters.window) {{
                        return false;
                    }}
                    
                    // Capacity filter (multi-select)
                    if (!isInSelectedCapacityRanges(props.capacity_kw)) {{
                        return false;
                    }}
                    
                    return true;
                }})
            }};
            
            // Update map
            map.getSource('solar-sites').setData(filtered);
            
            // Update regional statistics
            updateRegionalStats(filtered.features);
        }}
        
        function isInSelectedCapacityRanges(capacity) {{
            if (selectedCapacityRanges.has('all')) return true;
            
            for (let range of selectedCapacityRanges) {{
                const [minStr, maxStr] = range.split('-');
                const min = parseFloat(minStr);
                const max = maxStr === 'Infinity' ? Infinity : parseFloat(maxStr);
                if (capacity >= min && capacity < max) return true;
            }}
            return false;
        }}
        
        function updateRegionalStats(features) {{
            const scotlandRegions = ['Scotland', 'Highland', 'Aberdeenshire', 'Orkney', 'Shetland', 'Fife', 'Perth', 'Dundee', 'Glasgow', 'Edinburgh', 'Stirling', 'Argyll', 'Moray', 'Angus', 'Ayrshire', 'Lanarkshire', 'Lothian', 'Borders'];
            
            let ewSites = 0, ewCapacity = 0, ewImmediate = 0, ewUrgent = 0, ewOptimal = 0;
            let scotSites = 0, scotCapacity = 0, scotImmediate = 0, scotUrgent = 0, scotOptimal = 0;
            let totalAge = 0, totalFit = 0, totalEfficiency = 0;
            
            features.forEach(feature => {{
                const props = feature.properties;
                const region = props.region || '';
                const isScotland = scotlandRegions.some(term => region.toLowerCase().includes(term.toLowerCase()));
                
                if (isScotland) {{
                    scotSites++;
                    scotCapacity += props.capacity_mw;
                    if (props.repowering_window === 'IMMEDIATE') scotImmediate++;
                    if (props.repowering_window === 'URGENT') scotUrgent++;
                    if (props.repowering_window === 'OPTIMAL') scotOptimal++;
                }} else {{
                    ewSites++;
                    ewCapacity += props.capacity_mw;
                    if (props.repowering_window === 'IMMEDIATE') ewImmediate++;
                    if (props.repowering_window === 'URGENT') ewUrgent++;
                    if (props.repowering_window === 'OPTIMAL') ewOptimal++;
                }}
                
                totalAge += props.age_years;
                totalFit += props.remaining_fit_years;
                totalEfficiency += props.capacity_factor || 11;
            }});
            
            const totalSites = features.length;
            
            // Format capacity display
            function formatCapacity(mw) {{
                if (mw < 1) {{
                    return (mw * 1000).toFixed(0) + ' kW';
                }} else {{
                    return mw.toFixed(1) + ' MW';
                }}
            }}
            
            // Update display
            document.getElementById('ewSites').textContent = ewSites.toLocaleString();
            document.getElementById('ewCapacity').textContent = formatCapacity(ewCapacity);
            document.getElementById('ewImmediate').textContent = ewImmediate.toLocaleString();
            document.getElementById('ewUrgent').textContent = ewUrgent.toLocaleString();
            document.getElementById('ewOptimal').textContent = ewOptimal.toLocaleString();
            
            document.getElementById('scotSites').textContent = scotSites.toLocaleString();
            document.getElementById('scotCapacity').textContent = formatCapacity(scotCapacity);
            document.getElementById('scotImmediate').textContent = scotImmediate.toLocaleString();
            document.getElementById('scotUrgent').textContent = scotUrgent.toLocaleString();
            document.getElementById('scotOptimal').textContent = scotOptimal.toLocaleString();
            
            document.getElementById('totalSites').textContent = totalSites.toLocaleString();
            document.getElementById('totalCapacity').textContent = formatCapacity(ewCapacity + scotCapacity);
            document.getElementById('avgAge').textContent = totalSites > 0 ? (totalAge / totalSites).toFixed(1) + ' yr' : '0 yr';
            document.getElementById('avgFit').textContent = totalSites > 0 ? (totalFit / totalSites).toFixed(1) + ' yr' : '0 yr';
            document.getElementById('avgEfficiency').textContent = totalSites > 0 ? (totalEfficiency / totalSites).toFixed(1) + '%' : '0%';
        }}
        
        function resetMap() {{
            map.flyTo({{
                center: [-2, 53],
                zoom: 5.5,
                pitch: 0,
                bearing: 0
            }});
        }}
        
        // AI Chat Functions
        let chatConfig = {{
            apiKey: localStorage.getItem('openrouter_api_key') || '',
            model: localStorage.getItem('openrouter_model') || 'openai/gpt-3.5-turbo'
        }};
        
        // Load saved config on page load
        window.addEventListener('load', () => {{
            document.getElementById('apiKey').value = chatConfig.apiKey;
            document.getElementById('aiModel').value = chatConfig.model;
        }});
        
        function toggleChatConfig() {{
            const config = document.getElementById('chatConfig');
            config.classList.toggle('hidden');
        }}
        
        function saveApiConfig() {{
            const apiKey = document.getElementById('apiKey').value;
            const model = document.getElementById('aiModel').value;
            
            if (apiKey) {{
                chatConfig.apiKey = apiKey;
                chatConfig.model = model;
                localStorage.setItem('openrouter_api_key', apiKey);
                localStorage.setItem('openrouter_model', model);
                
                document.getElementById('chatConfig').classList.add('hidden');
                addChatMessage('system', 'Configuration saved! Model: ' + model);
            }} else {{
                alert('Please enter your OpenRouter API key');
            }}
        }}
        
        function getCurrentDataContext() {{
            // Get current filtered data for context
            const features = filteredData.features;
            
            // Create a simplified dataset with all key properties for AI analysis
            const sites_data = features.map(f => ({{
                postcode: f.properties.postcode,
                capacity_kw: f.properties.capacity_kw,
                capacity_mw: f.properties.capacity_mw,
                age_years: f.properties.age_years,
                remaining_fit_years: f.properties.remaining_fit_years,
                region: f.properties.region,
                repowering_window: f.properties.repowering_window,
                annual_generation_mwh: f.properties.annual_generation_mwh,
                capacity_factor: f.properties.capacity_factor || 11
            }}));
            
            // Calculate summary statistics
            const stats = {{
                total_sites: features.length,
                total_capacity_mw: features.reduce((sum, f) => sum + f.properties.capacity_mw, 0),
                avg_age: features.length > 0 ? features.reduce((sum, f) => sum + f.properties.age_years, 0) / features.length : 0,
                avg_fit_remaining: features.length > 0 ? features.reduce((sum, f) => sum + f.properties.remaining_fit_years, 0) / features.length : 0
            }};
            
            return {{
                summary: stats,
                sites: sites_data
            }};
        }}
        
        function analyzeDataForAI(sites) {{
            // Create comprehensive analytics for AI to answer any question
            const analytics = {{
                by_region: {{}},
                by_capacity_range: {{
                    '0-50kW': {{count: 0, total_capacity_mw: 0, sites: []}},
                    '50-100kW': {{count: 0, total_capacity_mw: 0, sites: []}},
                    '100-250kW': {{count: 0, total_capacity_mw: 0, sites: []}},
                    '250-500kW': {{count: 0, total_capacity_mw: 0, sites: []}},
                    '500-750kW': {{count: 0, total_capacity_mw: 0, sites: []}},
                    '750-1000kW': {{count: 0, total_capacity_mw: 0, sites: []}},
                    '1000kW+': {{count: 0, total_capacity_mw: 0, sites: []}}
                }},
                by_repowering_window: {{}},
                by_age_range: {{
                    '0-5 years': {{count: 0, total_capacity_mw: 0}},
                    '5-10 years': {{count: 0, total_capacity_mw: 0}},
                    '10-15 years': {{count: 0, total_capacity_mw: 0}},
                    '15+ years': {{count: 0, total_capacity_mw: 0}}
                }},
                by_fit_remaining: {{
                    '0-2 years': {{count: 0, total_capacity_mw: 0}},
                    '2-5 years': {{count: 0, total_capacity_mw: 0}},
                    '5-10 years': {{count: 0, total_capacity_mw: 0}},
                    '10+ years': {{count: 0, total_capacity_mw: 0}}
                }},
                scotland_specific: {{
                    total_sites: 0,
                    total_capacity_mw: 0,
                    by_capacity_range: {{}},
                    by_window: {{}}
                }},
                top_postcodes: {{}},
                generation_stats: {{
                    total_annual_mwh: 0,
                    avg_capacity_factor: 0
                }}
            }};
            
            const scotlandRegions = ['Scotland', 'Highland', 'Aberdeenshire', 'Orkney', 'Shetland', 'Fife', 'Perth', 'Dundee', 'Glasgow', 'Edinburgh', 'Stirling', 'Argyll', 'Moray', 'Angus'];
            
            sites.forEach(site => {{
                // Regional breakdown
                const region = site.region || 'Unknown';
                if (!analytics.by_region[region]) {{
                    analytics.by_region[region] = {{count: 0, total_capacity_mw: 0, avg_age: 0, sites_list: []}};
                }}
                analytics.by_region[region].count++;
                analytics.by_region[region].total_capacity_mw += site.capacity_mw;
                analytics.by_region[region].sites_list.push({{
                    postcode: site.postcode,
                    capacity_kw: site.capacity_kw
                }});
                
                // Capacity ranges
                const kw = site.capacity_kw;
                let capacityRange;
                if (kw < 50) capacityRange = '0-50kW';
                else if (kw < 100) capacityRange = '50-100kW';
                else if (kw < 250) capacityRange = '100-250kW';
                else if (kw < 500) capacityRange = '250-500kW';
                else if (kw < 750) capacityRange = '500-750kW';
                else if (kw < 1000) capacityRange = '750-1000kW';
                else capacityRange = '1000kW+';
                
                analytics.by_capacity_range[capacityRange].count++;
                analytics.by_capacity_range[capacityRange].total_capacity_mw += site.capacity_mw;
                
                // Repowering windows
                const window = site.repowering_window;
                if (!analytics.by_repowering_window[window]) {{
                    analytics.by_repowering_window[window] = {{count: 0, total_capacity_mw: 0}};
                }}
                analytics.by_repowering_window[window].count++;
                analytics.by_repowering_window[window].total_capacity_mw += site.capacity_mw;
                
                // Age ranges
                const age = site.age_years;
                let ageRange;
                if (age < 5) ageRange = '0-5 years';
                else if (age < 10) ageRange = '5-10 years';
                else if (age < 15) ageRange = '10-15 years';
                else ageRange = '15+ years';
                
                analytics.by_age_range[ageRange].count++;
                analytics.by_age_range[ageRange].total_capacity_mw += site.capacity_mw;
                
                // FIT remaining
                const fit = site.remaining_fit_years;
                let fitRange;
                if (fit < 2) fitRange = '0-2 years';
                else if (fit < 5) fitRange = '2-5 years';
                else if (fit < 10) fitRange = '5-10 years';
                else fitRange = '10+ years';
                
                analytics.by_fit_remaining[fitRange].count++;
                analytics.by_fit_remaining[fitRange].total_capacity_mw += site.capacity_mw;
                
                // Scotland specific
                const isScotland = scotlandRegions.some(term => region.includes(term));
                if (isScotland) {{
                    analytics.scotland_specific.total_sites++;
                    analytics.scotland_specific.total_capacity_mw += site.capacity_mw;
                    
                    if (!analytics.scotland_specific.by_capacity_range[capacityRange]) {{
                        analytics.scotland_specific.by_capacity_range[capacityRange] = {{count: 0, capacity_mw: 0}};
                    }}
                    analytics.scotland_specific.by_capacity_range[capacityRange].count++;
                    analytics.scotland_specific.by_capacity_range[capacityRange].capacity_mw += site.capacity_mw;
                    
                    if (!analytics.scotland_specific.by_window[window]) {{
                        analytics.scotland_specific.by_window[window] = 0;
                    }}
                    analytics.scotland_specific.by_window[window]++;
                }}
                
                // Top postcodes
                const postcodePrefix = site.postcode ? site.postcode.split(' ')[0] : 'Unknown';
                if (!analytics.top_postcodes[postcodePrefix]) {{
                    analytics.top_postcodes[postcodePrefix] = {{count: 0, capacity_mw: 0}};
                }}
                analytics.top_postcodes[postcodePrefix].count++;
                analytics.top_postcodes[postcodePrefix].capacity_mw += site.capacity_mw;
                
                // Generation stats
                analytics.generation_stats.total_annual_mwh += site.annual_generation_mwh || 0;
                analytics.generation_stats.avg_capacity_factor += site.capacity_factor || 11;
            }});
            
            // Calculate averages
            if (sites.length > 0) {{
                analytics.generation_stats.avg_capacity_factor /= sites.length;
                
                // Calculate average age per region
                Object.keys(analytics.by_region).forEach(region => {{
                    const regionSites = sites.filter(s => s.region === region);
                    const avgAge = regionSites.reduce((sum, s) => sum + s.age_years, 0) / regionSites.length;
                    analytics.by_region[region].avg_age = avgAge;
                }});
            }}
            
            // Sort top postcodes and limit to top 10
            analytics.top_postcodes = Object.entries(analytics.top_postcodes)
                .sort((a, b) => b[1].count - a[1].count)
                .slice(0, 10)
                .reduce((obj, [key, val]) => ({{...obj, [key]: val}}), {{}});
            
            return analytics;
        }}
        
        function addChatMessage(role, content) {{
            const messagesDiv = document.getElementById('chatMessages');
            
            // Clear initial placeholder if this is the first message
            if (messagesDiv.querySelector('.text-gray-500')) {{
                messagesDiv.innerHTML = '';
            }}
            
            const messageDiv = document.createElement('div');
            messageDiv.className = role === 'user' ? 'mb-2 text-right' : 'mb-2';
            
            const bubble = document.createElement('div');
            bubble.className = role === 'user' 
                ? 'inline-block bg-blue-600 text-white px-3 py-2 rounded-lg text-sm max-w-xs text-left'
                : role === 'system' 
                ? 'inline-block bg-gray-300 text-gray-700 px-3 py-2 rounded-lg text-sm max-w-xs'
                : 'inline-block bg-gray-100 text-gray-800 px-3 py-2 rounded-lg text-sm max-w-xs whitespace-pre-wrap';
            bubble.textContent = content;
            
            messageDiv.appendChild(bubble);
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }}
        
        async function sendChatMessage() {{
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            if (!chatConfig.apiKey) {{
                addChatMessage('system', 'Please configure your OpenRouter API key first (click the gear icon)');
                return;
            }}
            
            // Add user message
            addChatMessage('user', message);
            input.value = '';
            
            // Show typing indicator
            addChatMessage('system', 'Analyzing data...');
            
            try {{
                // First, query our Python API for accurate data
                let apiData = null;
                try {{
                    const apiResponse = await fetch('http://localhost:5001/api/query', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ query: message }})
                    }});
                    
                    if (apiResponse.ok) {{
                        const result = await apiResponse.json();
                        apiData = result.data;
                    }}
                }} catch (apiError) {{
                    console.log('API not available, using local data');
                }}
                
                // Get current filtered data context as fallback
                const dataContext = getCurrentDataContext();
                const analytics = apiData || analyzeDataForAI(dataContext.sites);
                
                // Prepare the system prompt
                const systemPrompt = apiData ? 
                    `You are an expert data analyst for UK commercial solar installations.
                    
                    The user asked: "${{message}}"
                    
                    Here is the ACCURATE data analysis from our database:
                    ${{JSON.stringify(apiData, null, 2)}}
                    
                    The FULL UK dataset contains 35,617 commercial solar sites with 2,244 MW total capacity.
                    
                    INSTRUCTIONS:
                    - Use the provided data to give accurate, specific answers
                    - Quote exact numbers from the analysis
                    - If a summary is provided, you can use it as the basis for your response
                    - Be concise but thorough` :
                    `You are an expert data analyst for UK commercial solar installations. 
                    
                    CURRENT FILTERED DATASET ANALYTICS:
                    Total sites visible: ${{dataContext.summary.total_sites.toLocaleString()}}
                    Total capacity: ${{dataContext.summary.total_capacity_mw.toFixed(1)}} MW
                    
                    DETAILED BREAKDOWN:
                    ${{JSON.stringify(analytics, null, 2)}}
                    
                    The FULL UK dataset contains 35,617 commercial solar sites with 2,244 MW total capacity.
                    Note: API server not available, using filtered view data only.`;
            
            try {{
                const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {{
                    method: 'POST',
                    headers: {{
                        'Authorization': `Bearer ${{chatConfig.apiKey}}`,
                        'Content-Type': 'application/json',
                        'HTTP-Referer': window.location.href,
                        'X-Title': 'Saber Solar Dashboard'
                    }},
                    body: JSON.stringify({{
                        model: chatConfig.model,
                        messages: [
                            {{ role: 'system', content: systemPrompt }},
                            {{ role: 'user', content: message }}
                        ],
                        temperature: 0.7,
                        max_tokens: 500
                    }})
                }});
                
                // Remove typing indicator
                const messages = document.getElementById('chatMessages');
                const lastMessage = messages.lastElementChild;
                if (lastMessage && lastMessage.textContent.includes('Thinking...')) {{
                    messages.removeChild(lastMessage);
                }}
                
                if (!response.ok) {{
                    const error = await response.json();
                    throw new Error(error.error?.message || `API error: ${{response.status}}`);
                }}
                
                const data = await response.json();
                const aiResponse = data.choices[0].message.content;
                addChatMessage('assistant', aiResponse);
                
            }} catch (error) {{
                // Remove typing indicator
                const messages = document.getElementById('chatMessages');
                const lastMessage = messages.lastElementChild;
                if (lastMessage && lastMessage.textContent.includes('Thinking...')) {{
                    messages.removeChild(lastMessage);
                }}
                
                console.error('Chat error:', error);
                addChatMessage('system', `Error: ${{error.message}}`);
            }}
        }}
        
        // Initialize priority chart
        function initPriorityChart() {{
            const ctx = document.getElementById('priorityChart').getContext('2d');
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: ['Immediate', 'Urgent', 'Optimal', 'Planning', 'Future'],
                    datasets: [{{
                        data: [{repowering.get('IMMEDIATE', 0)}, {repowering.get('URGENT', 0)}, {repowering.get('OPTIMAL', 0)}, {repowering.get('PLANNING', 0)}, {repowering.get('FUTURE', 0)}],
                        backgroundColor: ['#E74C3C', '#F39C12', '#7CC061', '#0A5F8E', '#95D47E'],
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
                                padding: 8,
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
            updateTable({json.dumps(geojson)}.features.slice(0, 50));
        }});
    </script>
</body>
</html>"""
    
    return html_content


def main():
    logger.info("Creating Commercial Solar Dashboard V2...")
    
    dashboard_html = create_commercial_solar_dashboard()
    
    Path('visualizations').mkdir(exist_ok=True)
    with open('visualizations/saber_solar_dashboard.html', 'w') as f:
        f.write(dashboard_html)
    
    print("\n" + "="*60)
    print("COMMERCIAL SOLAR DASHBOARD V2 CREATED")
    print("="*60)
    print("\n✅ Matching Wind Dashboard UI:")
    print("   • Cohesive filter system")
    print("   • Data table with top opportunities")
    print("   • Site intelligence panel")
    print("   • Same tooltip behavior")
    print("\n📁 Dashboard: visualizations/saber_solar_dashboard.html")
    
    import webbrowser
    import os
    full_path = os.path.abspath('visualizations/saber_solar_dashboard.html')
    webbrowser.open(f"file://{full_path}")


if __name__ == "__main__":
    main()