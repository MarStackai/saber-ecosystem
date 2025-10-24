#!/usr/bin/env python3
"""
Create a professionally branded Saber Solar Dashboard
Extends the wind dashboard with solar-specific metrics and visualizations
"""

import pandas as pd
import numpy as np
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

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


def generate_solar_data():
    """Generate realistic UK solar data for demonstration"""
    np.random.seed(42)
    
    # UK regions with solar potential
    regions = {
        'South East England': {'lat': 51.2787, 'lon': 0.5217, 'irradiance': 1150},
        'South West England': {'lat': 50.7772, 'lon': -3.9997, 'irradiance': 1200},
        'East Anglia': {'lat': 52.6309, 'lon': 1.2974, 'irradiance': 1100},
        'Midlands': {'lat': 52.4862, 'lon': -1.8904, 'irradiance': 1050},
        'Yorkshire': {'lat': 53.9591, 'lon': -1.0815, 'irradiance': 1000},
        'North West': {'lat': 53.7632, 'lon': -2.7044, 'irradiance': 950},
        'Scotland': {'lat': 56.4907, 'lon': -4.2026, 'irradiance': 900},
        'Wales': {'lat': 52.1307, 'lon': -3.7837, 'irradiance': 1000},
        'Northern Ireland': {'lat': 54.7877, 'lon': -6.4923, 'irradiance': 920}
    }
    
    solar_sites = []
    site_id = 1
    
    for region, data in regions.items():
        # Generate sites per region (more in southern regions)
        num_sites = np.random.randint(50, 200) if 'South' in region else np.random.randint(20, 80)
        
        for _ in range(num_sites):
            # Capacity ranges from 10kW to 50MW
            capacity_kw = np.random.choice([
                np.random.uniform(10, 50),      # Residential
                np.random.uniform(50, 250),     # Commercial rooftop
                np.random.uniform(250, 1000),   # Large commercial
                np.random.uniform(1000, 5000),  # Small solar farm
                np.random.uniform(5000, 50000)  # Large solar farm
            ], p=[0.4, 0.3, 0.15, 0.1, 0.05])
            
            # Age distribution
            age_years = np.random.uniform(0, 15)
            
            # Performance ratio affected by age
            base_pr = 0.85
            degradation = min(age_years * 0.005, 0.1)  # 0.5% per year
            performance_ratio = base_pr - degradation
            
            # Annual generation based on irradiance
            annual_generation = capacity_kw * data['irradiance'] * performance_ratio
            
            # FIT rates based on installation year
            if age_years > 10:
                fit_rate = np.random.uniform(40, 50)  # Old high FIT rates
            elif age_years > 5:
                fit_rate = np.random.uniform(10, 20)
            else:
                fit_rate = np.random.uniform(3, 5)  # Current low rates
            
            solar_sites.append({
                'site_id': f'SOL{site_id:04d}',
                'region': region,
                'latitude': data['lat'] + np.random.normal(0, 0.5),
                'longitude': data['lon'] + np.random.normal(0, 0.5),
                'capacity_kw': capacity_kw,
                'capacity_mw': capacity_kw / 1000,
                'age_years': age_years,
                'installation_date': datetime.now() - timedelta(days=age_years*365),
                'panel_type': np.random.choice(['Monocrystalline', 'Polycrystalline', 'Thin Film']),
                'inverter_brand': np.random.choice(['SMA', 'Fronius', 'Huawei', 'SolarEdge', 'ABB']),
                'performance_ratio': performance_ratio,
                'annual_generation_kwh': annual_generation,
                'capacity_factor': (annual_generation / (capacity_kw * 8760)) * 100,  # CF calculation
                'fit_rate': fit_rate,
                'fit_remaining_years': max(0, 20 - age_years),
                'irradiance': data['irradiance'],
                'degradation_rate': 0.5,  # %/year
                'temperature_coefficient': -0.4  # %/°C
            })
            
            site_id += 1
    
    return pd.DataFrame(solar_sites)


def generate_hourly_generation_pattern():
    """Generate typical solar generation pattern for 24 hours"""
    hours = list(range(24))
    
    # Summer pattern (peak at noon)
    summer_pattern = []
    for hour in hours:
        if hour < 5 or hour > 20:
            generation = 0
        elif hour < 12:
            generation = np.sin((hour - 5) * np.pi / 14) * 100
        else:
            generation = np.sin((20 - hour) * np.pi / 14) * 100
        summer_pattern.append(max(0, generation + np.random.normal(0, 5)))
    
    # Winter pattern (shorter day, lower peak)
    winter_pattern = []
    for hour in hours:
        if hour < 8 or hour > 16:
            generation = 0
        elif hour < 12:
            generation = np.sin((hour - 8) * np.pi / 8) * 40
        else:
            generation = np.sin((16 - hour) * np.pi / 8) * 40
        winter_pattern.append(max(0, generation + np.random.normal(0, 3)))
    
    return hours, summer_pattern, winter_pattern


def create_solar_dashboard():
    """Create the main solar dashboard HTML"""
    
    logo_svg = get_logo_base64()
    
    # Generate solar data
    solar_df = generate_solar_data()
    hours, summer_pattern, winter_pattern = generate_hourly_generation_pattern()
    
    # Calculate statistics
    total_sites = len(solar_df)
    total_capacity_mw = solar_df['capacity_mw'].sum()
    avg_capacity_factor = solar_df['capacity_factor'].mean()
    total_annual_generation_gwh = solar_df['annual_generation_kwh'].sum() / 1_000_000
    
    # Regional statistics
    regional_stats = solar_df.groupby('region').agg({
        'capacity_mw': 'sum',
        'site_id': 'count',
        'capacity_factor': 'mean',
        'performance_ratio': 'mean'
    }).sort_values('capacity_mw', ascending=False)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Saber Solar Intelligence | PV Performance Analytics Platform</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- Mapbox GL JS -->
    <link href='https://api.mapbox.com/mapbox-gl-js/v3.1.0/mapbox-gl.css' rel='stylesheet' />
    <script src='https://api.mapbox.com/mapbox-gl-js/v3.1.0/mapbox-gl.js'></script>
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    
    <!-- Google Fonts -->
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
        
        .generation-meter {{
            position: relative;
            width: 200px;
            height: 200px;
            margin: 0 auto;
        }}
        
        .meter-ring {{
            stroke-dasharray: 440;
            stroke-dashoffset: 440;
            animation: fillMeter 2s ease-out forwards;
            filter: drop-shadow(0 0 10px rgba(124, 192, 97, 0.5));
        }}
        
        @keyframes fillMeter {{
            to {{
                stroke-dashoffset: 88;
            }}
        }}
        
        /* Fixed height containers for charts */
        .chart-container {{
            position: relative;
            height: 250px;
        }}
        
        .chart-container-small {{
            position: relative;
            height: 200px;
        }}
        
        .chart-container-large {{
            position: relative;
            height: 300px;
        }}
    </style>
</head>
<body>
    <!-- Header -->
    <header class="solar-gradient text-white shadow-2xl relative">
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
                        <p class="text-sm opacity-90 font-light">Real-time PV Performance Analytics</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <a href="saber_mapbox_dashboard.html" class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg hover:bg-white/30 transition">
                        <i class="fas fa-wind mr-2"></i>Wind
                    </a>
                    <div class="text-right px-4">
                        <p class="text-2xl font-bold">{total_sites:,}</p>
                        <p class="text-xs opacity-90 uppercase">Solar Sites</p>
                    </div>
                    <button onclick="location.reload()" class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg hover:bg-white/30 transition">
                        <i class="fas fa-sync-alt mr-2"></i>Refresh
                    </button>
                </div>
            </div>
        </div>
    </header>
    
    <!-- Key Metrics -->
    <div class="container mx-auto px-6 mt-6 relative z-20">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div class="stat-card p-5">
                <div class="relative z-10">
                    <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Total Capacity</p>
                    <p class="text-3xl font-bold text-white">{total_capacity_mw:.1f} MW</p>
                    <p class="text-xs text-white/60 mt-1">Installed solar</p>
                </div>
                <div class="absolute top-4 right-4 text-4xl text-white/20">
                    <i class="fas fa-solar-panel"></i>
                </div>
            </div>
            
            <div class="stat-card p-5">
                <div class="relative z-10">
                    <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Capacity Factor</p>
                    <p class="text-3xl font-bold text-white">{avg_capacity_factor:.1f}%</p>
                    <p class="text-xs text-white/60 mt-1">UK average</p>
                </div>
                <div class="absolute top-4 right-4 text-4xl text-white/20">
                    <i class="fas fa-percentage"></i>
                </div>
            </div>
            
            <div class="stat-card p-5">
                <div class="relative z-10">
                    <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Annual Generation</p>
                    <p class="text-3xl font-bold text-white">{total_annual_generation_gwh:.1f} GWh</p>
                    <p class="text-xs text-white/60 mt-1">Total output</p>
                </div>
                <div class="absolute top-4 right-4 text-4xl text-white/20">
                    <i class="fas fa-bolt"></i>
                </div>
            </div>
            
            <div class="stat-card p-5">
                <div class="relative z-10">
                    <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Avg Degradation</p>
                    <p class="text-3xl font-bold text-white">0.5%</p>
                    <p class="text-xs text-white/60 mt-1">Per year</p>
                </div>
                <div class="absolute top-4 right-4 text-4xl text-white/20">
                    <i class="fas fa-chart-line"></i>
                </div>
            </div>
            
            <div class="stat-card p-5">
                <div class="relative z-10">
                    <p class="text-white/80 text-xs uppercase tracking-wider font-semibold">Peak Hours</p>
                    <p class="text-3xl font-bold text-white">1,100</p>
                    <p class="text-xs text-white/60 mt-1">Annual avg</p>
                </div>
                <div class="absolute top-4 right-4 text-4xl text-white/20">
                    <i class="fas fa-sun"></i>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Main Dashboard Content -->
    <div class="container mx-auto px-6 py-8">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            <!-- Daily Generation Pattern -->
            <div class="lg:col-span-2 saber-card p-6">
                <h3 class="text-xl font-bold mb-4">
                    <i class="fas fa-chart-area mr-2" style="color: var(--solar-orange)"></i>
                    Daily Generation Pattern
                </h3>
                <div class="mb-4">
                    <button onclick="toggleSeason('summer')" class="season-btn px-4 py-2 rounded-lg mr-2 bg-orange-500 text-white">Summer</button>
                    <button onclick="toggleSeason('winter')" class="season-btn px-4 py-2 rounded-lg bg-gray-200 text-gray-700">Winter</button>
                </div>
                <div style="height: 300px; position: relative;">
                    <canvas id="dailyGenerationChart"></canvas>
                </div>
            </div>
            
            <!-- Live Generation Meter -->
            <div class="saber-card p-6">
                <h3 class="text-xl font-bold mb-4">
                    <i class="fas fa-tachometer-alt mr-2" style="color: var(--solar-orange)"></i>
                    Current Output
                </h3>
                <div class="generation-meter">
                    <svg viewBox="0 0 200 200">
                        <circle cx="100" cy="100" r="70" stroke="#e0e0e0" stroke-width="15" fill="none"/>
                        <circle cx="100" cy="100" r="70" stroke="url(#solarGradient)" stroke-width="15" fill="none"
                                class="meter-ring" transform="rotate(-90 100 100)"/>
                        <defs>
                            <linearGradient id="solarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" style="stop-color:#FFA500;stop-opacity:1" />
                                <stop offset="100%" style="stop-color:#FFD700;stop-opacity:1" />
                            </linearGradient>
                        </defs>
                    </svg>
                    <div class="absolute inset-0 flex items-center justify-center flex-col">
                        <p class="text-4xl font-bold">{(total_capacity_mw * 0.75):.0f}</p>
                        <p class="text-sm text-gray-600">MW</p>
                        <p class="text-xs text-green-600 mt-2">75% of capacity</p>
                    </div>
                </div>
                <div class="mt-4 space-y-2 text-sm">
                    <div class="flex justify-between">
                        <span class="text-gray-600">Irradiance:</span>
                        <span class="font-bold">850 W/m²</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Panel Temp:</span>
                        <span class="font-bold">42°C</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Performance Ratio:</span>
                        <span class="font-bold text-green-600">82%</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Regional Analysis and Seasonal Variation -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            
            <!-- Regional Performance -->
            <div class="saber-card p-6">
                <h3 class="text-xl font-bold mb-4">
                    <i class="fas fa-map-marked-alt mr-2" style="color: var(--solar-orange)"></i>
                    Regional Performance
                </h3>
                <div style="height: 250px; position: relative;">
                    <canvas id="regionalChart"></canvas>
                </div>
            </div>
            
            <!-- Seasonal Variation Heatmap -->
            <div class="saber-card p-6">
                <h3 class="text-xl font-bold mb-4">
                    <i class="fas fa-calendar-alt mr-2" style="color: var(--solar-orange)"></i>
                    Monthly Generation Heatmap
                </h3>
                <div style="height: 250px; position: relative;">
                    <canvas id="heatmapChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Panel Types and Degradation Analysis -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
            
            <!-- Panel Type Distribution -->
            <div class="saber-card p-6">
                <h3 class="text-lg font-bold mb-4">
                    <i class="fas fa-layer-group mr-2" style="color: var(--solar-orange)"></i>
                    Panel Technology
                </h3>
                <div style="height: 200px; position: relative;">
                    <canvas id="panelTypeChart"></canvas>
                </div>
            </div>
            
            <!-- Degradation Curve -->
            <div class="saber-card p-6">
                <h3 class="text-lg font-bold mb-4">
                    <i class="fas fa-chart-line mr-2" style="color: var(--solar-orange)"></i>
                    Degradation Trend
                </h3>
                <div style="height: 200px; position: relative;">
                    <canvas id="degradationChart"></canvas>
                </div>
            </div>
            
            <!-- Temperature Impact -->
            <div class="saber-card p-6">
                <h3 class="text-lg font-bold mb-4">
                    <i class="fas fa-thermometer-half mr-2" style="color: var(--solar-orange)"></i>
                    Temperature Impact
                </h3>
                <div style="height: 200px; position: relative;">
                    <canvas id="temperatureChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Sites Table -->
        <div class="saber-card p-6 mt-6">
            <h3 class="text-xl font-bold mb-4">
                <i class="fas fa-table mr-2" style="color: var(--saber-green)"></i>
                Top Performing Sites
            </h3>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="border-b-2 border-gray-200">
                            <th class="text-left py-2">Site ID</th>
                            <th class="text-left py-2">Region</th>
                            <th class="text-right py-2">Capacity (MW)</th>
                            <th class="text-right py-2">CF (%)</th>
                            <th class="text-right py-2">PR (%)</th>
                            <th class="text-right py-2">Age (years)</th>
                            <th class="text-right py-2">Annual Gen (MWh)</th>
                        </tr>
                    </thead>
                    <tbody id="sitesTable">
                        <!-- Populated by JavaScript -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <!-- Footer -->
    <footer class="mt-12 py-8 text-white text-center solar-gradient">
        <div class="relative z-10">
            <p class="text-sm opacity-90">© 2024 Saber Renewable Energy Ltd. All rights reserved.</p>
            <p class="text-xs opacity-75 mt-2">Solar Intelligence Platform | Precision PV Analytics</p>
        </div>
    </footer>
    
    <script>
        // Data for charts
        const hours = {json.dumps(hours)};
        const summerPattern = {json.dumps(summer_pattern)};
        const winterPattern = {json.dumps(winter_pattern)};
        
        // Daily Generation Chart
        const dailyCtx = document.getElementById('dailyGenerationChart').getContext('2d');
        const dailyChart = new Chart(dailyCtx, {{
            type: 'line',
            data: {{
                labels: hours.map(h => `${{h}}:00`),
                datasets: [{{
                    label: 'Generation (%)',
                    data: summerPattern,
                    borderColor: '#FFA500',
                    backgroundColor: 'rgba(255, 165, 0, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 3
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.parsed.y.toFixed(1) + '% of capacity';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        title: {{
                            display: true,
                            text: 'Output (% of capacity)'
                        }}
                    }},
                    x: {{
                        grid: {{ display: false }}
                    }}
                }}
            }}
        }});
        
        // Regional Performance Chart
        const regionalCtx = document.getElementById('regionalChart').getContext('2d');
        new Chart(regionalCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(regional_stats.head(5).index.tolist())},
                datasets: [{{
                    label: 'Capacity (MW)',
                    data: {json.dumps(regional_stats.head(5)['capacity_mw'].tolist())},
                    backgroundColor: 'rgba(255, 165, 0, 0.8)',
                    borderRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Capacity (MW)'
                        }}
                    }}
                }}
            }}
        }});
        
        // Monthly Heatmap (simplified bar chart)
        const heatmapCtx = document.getElementById('heatmapChart').getContext('2d');
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const monthlyGen = [40, 50, 70, 85, 95, 100, 100, 95, 80, 60, 45, 35];
        
        new Chart(heatmapCtx, {{
            type: 'bar',
            data: {{
                labels: months,
                datasets: [{{
                    label: 'Generation Index',
                    data: monthlyGen,
                    backgroundColor: monthlyGen.map(v => {{
                        if (v > 80) return '#FF6B6B';
                        if (v > 60) return '#FFA500';
                        if (v > 40) return '#FFD700';
                        return '#90EE90';
                    }}),
                    borderRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return 'Index: ' + context.parsed.y;
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }}
        }});
        
        // Panel Type Distribution
        const panelCtx = document.getElementById('panelTypeChart').getContext('2d');
        new Chart(panelCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Monocrystalline', 'Polycrystalline', 'Thin Film'],
                datasets: [{{
                    data: [60, 30, 10],
                    backgroundColor: ['#FF6B6B', '#FFA500', '#FFD700'],
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
                        labels: {{ font: {{ size: 11 }} }}
                    }}
                }}
            }}
        }});
        
        // Degradation Chart
        const degradationCtx = document.getElementById('degradationChart').getContext('2d');
        const years = Array.from({{length: 25}}, (_, i) => i);
        const degradation = years.map(y => 100 - (y * 0.5));
        
        new Chart(degradationCtx, {{
            type: 'line',
            data: {{
                labels: years,
                datasets: [{{
                    label: 'Performance (%)',
                    data: degradation,
                    borderColor: '#FF6B6B',
                    backgroundColor: 'rgba(255, 107, 107, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: false,
                        min: 85,
                        max: 100,
                        title: {{
                            display: true,
                            text: 'Performance (%)'
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Years'
                        }}
                    }}
                }}
            }}
        }});
        
        // Temperature Impact Chart
        const tempCtx = document.getElementById('temperatureChart').getContext('2d');
        const temps = Array.from({{length: 16}}, (_, i) => i * 5);
        const efficiency = temps.map(t => {{
            if (t <= 25) return 100;
            return 100 - ((t - 25) * 0.4);
        }});
        
        new Chart(tempCtx, {{
            type: 'line',
            data: {{
                labels: temps.map(t => t + '°C'),
                datasets: [{{
                    label: 'Efficiency (%)',
                    data: efficiency,
                    borderColor: '#FFA500',
                    backgroundColor: 'rgba(255, 165, 0, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: false,
                        min: 85,
                        max: 105,
                        title: {{
                            display: true,
                            text: 'Efficiency (%)'
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Panel Temperature'
                        }}
                    }}
                }}
            }}
        }});
        
        // Toggle season
        function toggleSeason(season) {{
            const data = season === 'summer' ? summerPattern : winterPattern;
            dailyChart.data.datasets[0].data = data;
            dailyChart.data.datasets[0].label = season === 'summer' ? 'Summer Generation (%)' : 'Winter Generation (%)';
            dailyChart.update();
            
            // Update button styles
            document.querySelectorAll('.season-btn').forEach(btn => {{
                btn.style.backgroundColor = '#e5e7eb';
                btn.style.color = '#374151';
            }});
            event.target.style.backgroundColor = 'var(--saber-green)';
            event.target.style.color = 'white';
        }}
        
        // Populate sites table
        const topSites = {json.dumps(solar_df.nlargest(10, 'capacity_factor')[['site_id', 'region', 'capacity_mw', 'capacity_factor', 'performance_ratio', 'age_years', 'annual_generation_kwh']].to_dict('records'))};
        
        const tbody = document.getElementById('sitesTable');
        topSites.forEach(site => {{
            const row = tbody.insertRow();
            row.innerHTML = `
                <td class="py-2 font-mono text-xs">${{site.site_id}}</td>
                <td class="py-2">${{site.region}}</td>
                <td class="py-2 text-right">${{site.capacity_mw.toFixed(2)}}</td>
                <td class="py-2 text-right">${{site.capacity_factor.toFixed(1)}}</td>
                <td class="py-2 text-right">${{(site.performance_ratio * 100).toFixed(1)}}</td>
                <td class="py-2 text-right">${{site.age_years.toFixed(1)}}</td>
                <td class="py-2 text-right">${{(site.annual_generation_kwh / 1000).toFixed(0)}}</td>
            `;
        }});
        
        // Animate meter on load
        setTimeout(() => {{
            document.querySelector('.meter-ring').style.strokeDashoffset = '132'; // 80% fill
        }}, 500);
    </script>
</body>
</html>"""
    
    return html_content


def main():
    logger.info("Creating Saber Solar Dashboard...")
    
    # Create dashboard
    dashboard_html = create_solar_dashboard()
    
    # Save dashboard
    Path('visualizations').mkdir(exist_ok=True)
    with open('visualizations/saber_solar_dashboard.html', 'w') as f:
        f.write(dashboard_html)
    
    print("\n" + "="*60)
    print("SABER SOLAR DASHBOARD CREATED")
    print("="*60)
    print("\n✅ Features included:")
    print("   • Real-time generation meter with solar gradients")
    print("   • Daily generation bell curves (summer/winter)")
    print("   • Monthly generation heatmap")
    print("   • Regional performance analysis")
    print("   • Panel degradation tracking (0.5%/year)")
    print("   • Temperature impact visualization")
    print("   • Panel technology distribution")
    print("   • Top performing sites table")
    print("\n📊 Solar-specific metrics:")
    print("   • Capacity Factor: 10-12% (UK average)")
    print("   • Performance Ratio tracking")
    print("   • Irradiance correlation")
    print("   • Seasonal variation (3-4x summer:winter)")
    print("\n📁 Dashboard: visualizations/saber_solar_dashboard.html")
    
    # Try to open
    import webbrowser
    import os
    full_path = os.path.abspath('visualizations/saber_solar_dashboard.html')
    webbrowser.open(f"file://{full_path}")


if __name__ == "__main__":
    main()