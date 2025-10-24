#!/usr/bin/env python3
"""
Create a Saber analytics dashboard with time-based charts
"""

import pandas as pd
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


def create_analytics_dashboard():
    """Create analytics dashboard with time-based visualizations"""
    
    logo_svg = get_logo_base64()
    
    # Generate sample time-based data
    current_year = 2024
    years = list(range(current_year, current_year + 16))
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Saber Analytics | Wind Repowering Time Analysis</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
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
        
        .chart-container {{
            position: relative;
            height: 300px;
        }}
        
        .timeline-container {{
            position: relative;
            height: 400px;
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
                        <h1 class="text-2xl">Analytics Dashboard</h1>
                        <p class="text-sm opacity-90 font-light">Time-Based Repowering Intelligence</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <a href="saber_mapbox_dashboard.html" class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg hover:bg-white/30 transition">
                        <i class="fas fa-map mr-2"></i>Map View
                    </a>
                    <button onclick="exportData()" class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg hover:bg-white/30 transition">
                        <i class="fas fa-download mr-2"></i>Export
                    </button>
                </div>
            </div>
        </div>
    </header>
    
    <!-- Main Content -->
    <div class="w-full px-6 py-8">
        <!-- FIT Expiry Timeline -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div class="saber-card p-6">
                <h3 class="text-xl font-bold mb-4">
                    <i class="fas fa-calendar-alt mr-2" style="color: var(--saber-green)"></i>
                    FIT Expiry Timeline
                </h3>
                <div class="timeline-container">
                    <canvas id="fitTimelineChart"></canvas>
                </div>
                <div class="mt-4 text-sm text-gray-600">
                    <p><i class="fas fa-info-circle mr-1"></i>Shows number of sites losing FIT support each year</p>
                </div>
            </div>
            
            <div class="saber-card p-6">
                <h3 class="text-xl font-bold mb-4">
                    <i class="fas fa-chart-area mr-2" style="color: var(--saber-green)"></i>
                    Cumulative Capacity Available
                </h3>
                <div class="timeline-container">
                    <canvas id="capacityTimelineChart"></canvas>
                </div>
                <div class="mt-4 text-sm text-gray-600">
                    <p><i class="fas fa-info-circle mr-1"></i>Total MW capacity becoming available for repowering</p>
                </div>
            </div>
        </div>
        
        <!-- Regional Time Analysis -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div class="lg:col-span-2 saber-card p-6">
                <h3 class="text-xl font-bold mb-4">
                    <i class="fas fa-chart-line mr-2" style="color: var(--saber-green)"></i>
                    Regional Opportunity Timeline
                </h3>
                <div class="chart-container">
                    <canvas id="regionalTimelineChart"></canvas>
                </div>
            </div>
            
            <div class="saber-card p-6">
                <h3 class="text-xl font-bold mb-4">
                    <i class="fas fa-chart-bar mr-2" style="color: var(--saber-green)"></i>
                    Window Distribution
                </h3>
                <div class="chart-container">
                    <canvas id="windowDistributionChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Capacity Evolution -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div class="saber-card p-6">
                <h3 class="text-xl font-bold mb-4">
                    <i class="fas fa-battery-half mr-2" style="color: var(--saber-green)"></i>
                    Capacity by Age Group
                </h3>
                <div class="chart-container">
                    <canvas id="ageCapacityChart"></canvas>
                </div>
            </div>
            
            <div class="saber-card p-6">
                <h3 class="text-xl font-bold mb-4">
                    <i class="fas fa-tachometer-alt mr-2" style="color: var(--saber-green)"></i>
                    Efficiency Score Trends
                </h3>
                <div class="chart-container">
                    <canvas id="efficiencyTrendChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Detailed Statistics -->
        <div class="saber-card p-6">
            <h3 class="text-xl font-bold mb-4">
                <i class="fas fa-table mr-2" style="color: var(--saber-green)"></i>
                Year-by-Year Breakdown
            </h3>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="border-b-2 border-gray-200">
                            <th class="text-left py-2">Year</th>
                            <th class="text-right py-2">Sites Expiring</th>
                            <th class="text-right py-2">MW Available</th>
                            <th class="text-right py-2">Avg Capacity</th>
                            <th class="text-right py-2">Priority Sites</th>
                            <th class="text-right py-2">Investment Potential</th>
                        </tr>
                    </thead>
                    <tbody id="yearlyBreakdown">
                        <!-- Populated by JavaScript -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <!-- Footer -->
    <footer class="mt-12 py-8 text-white text-center" style="background: var(--dark-blue)">
        <p class="text-sm opacity-80">© 2024 Saber Renewable Energy Ltd. All rights reserved.</p>
        <p class="text-xs opacity-60 mt-2">Analytics Dashboard | Data-Driven Renewable Energy Intelligence</p>
    </footer>
    
    <script>
        // Sample data generation
        const years = [];
        const currentYear = new Date().getFullYear();
        for (let i = 0; i < 16; i++) {{
            years.push(currentYear + i);
        }}
        
        // FIT Timeline Chart
        const fitTimelineCtx = document.getElementById('fitTimelineChart').getContext('2d');
        new Chart(fitTimelineCtx, {{
            type: 'bar',
            data: {{
                labels: years,
                datasets: [{{
                    label: 'Sites Losing FIT',
                    data: [0, 0, 276, 342, 459, 801, 892, 1043, 987, 876, 765, 543, 321, 198, 87, 32],
                    backgroundColor: function(context) {{
                        const value = context.dataset.data[context.dataIndex];
                        if (value > 800) return '#FF4444';
                        if (value > 500) return '#F39C12';
                        if (value > 200) return '#7CC061';
                        return '#95D47E';
                    }},
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
                                return context.parsed.y + ' sites';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        grid: {{ color: 'rgba(0,0,0,0.05)' }}
                    }},
                    x: {{
                        grid: {{ display: false }}
                    }}
                }}
            }}
        }});
        
        // Capacity Timeline Chart
        const capacityTimelineCtx = document.getElementById('capacityTimelineChart').getContext('2d');
        new Chart(capacityTimelineCtx, {{
            type: 'line',
            data: {{
                labels: years,
                datasets: [{{
                    label: 'Cumulative MW',
                    data: [0, 0, 28, 62, 108, 189, 297, 425, 567, 698, 812, 897, 945, 978, 995, 1002],
                    borderColor: '#7CC061',
                    backgroundColor: 'rgba(124, 192, 97, 0.1)',
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
                                return context.parsed.y + ' MW cumulative';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        grid: {{ color: 'rgba(0,0,0,0.05)' }}
                    }},
                    x: {{
                        grid: {{ display: false }}
                    }}
                }}
            }}
        }});
        
        // Regional Timeline Chart
        const regionalTimelineCtx = document.getElementById('regionalTimelineChart').getContext('2d');
        new Chart(regionalTimelineCtx, {{
            type: 'line',
            data: {{
                labels: years.slice(0, 10),
                datasets: [
                    {{
                        label: 'Orkney',
                        data: [0, 0, 45, 89, 134, 198, 267, 312, 298, 245],
                        borderColor: '#044D73',
                        borderWidth: 2,
                        tension: 0.3
                    }},
                    {{
                        label: 'Aberdeenshire',
                        data: [0, 0, 32, 67, 98, 145, 189, 234, 256, 198],
                        borderColor: '#7CC061',
                        borderWidth: 2,
                        tension: 0.3
                    }},
                    {{
                        label: 'Cornwall',
                        data: [0, 0, 28, 54, 87, 123, 167, 198, 187, 156],
                        borderColor: '#95D47E',
                        borderWidth: 2,
                        tension: 0.3
                    }},
                    {{
                        label: 'Highland',
                        data: [0, 0, 19, 38, 62, 89, 112, 134, 145, 132],
                        borderColor: '#0A5F8E',
                        borderWidth: 2,
                        tension: 0.3
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{ padding: 15 }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Sites Available'
                        }},
                        grid: {{ color: 'rgba(0,0,0,0.05)' }}
                    }},
                    x: {{
                        grid: {{ display: false }}
                    }}
                }}
            }}
        }});
        
        // Window Distribution Chart
        const windowDistributionCtx = document.getElementById('windowDistributionChart').getContext('2d');
        new Chart(windowDistributionCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Urgent (2-5yr)', 'Optimal (5-10yr)', 'Planning (10-15yr)', 'Future (>15yr)'],
                datasets: [{{
                    data: [801, 5582, 513, 276],
                    backgroundColor: ['#FF4444', '#7CC061', '#0A5F8E', '#95D47E'],
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
        
        // Age Capacity Chart
        const ageCapacityCtx = document.getElementById('ageCapacityChart').getContext('2d');
        new Chart(ageCapacityCtx, {{
            type: 'bar',
            data: {{
                labels: ['0-5 years', '5-10 years', '10-15 years', '15-20 years', '20+ years'],
                datasets: [{{
                    label: 'Total MW',
                    data: [45, 234, 389, 102, 0],
                    backgroundColor: ['#95D47E', '#7CC061', '#0A5F8E', '#044D73', '#091922'],
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
                        }},
                        grid: {{ color: 'rgba(0,0,0,0.05)' }}
                    }},
                    x: {{
                        grid: {{ display: false }}
                    }}
                }}
            }}
        }});
        
        // Efficiency Trend Chart
        const efficiencyTrendCtx = document.getElementById('efficiencyTrendChart').getContext('2d');
        new Chart(efficiencyTrendCtx, {{
            type: 'line',
            data: {{
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{{
                    label: 'Average Score',
                    data: [0.72, 0.73, 0.71, 0.74, 0.75, 0.76, 0.78, 0.77, 0.79, 0.81, 0.80, 0.82],
                    borderColor: '#7CC061',
                    backgroundColor: 'rgba(124, 192, 97, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 3
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
                        min: 0.6,
                        max: 1.0,
                        title: {{
                            display: true,
                            text: 'Efficiency Score'
                        }},
                        grid: {{ color: 'rgba(0,0,0,0.05)' }}
                    }},
                    x: {{
                        grid: {{ display: false }}
                    }}
                }}
            }}
        }});
        
        // Populate yearly breakdown table
        const yearlyBreakdown = document.getElementById('yearlyBreakdown');
        const yearlyData = [
            {{year: 2026, sites: 276, mw: 28, avg: 0.10, priority: 276, investment: '£14M'}},
            {{year: 2027, sites: 342, mw: 34, avg: 0.10, priority: 342, investment: '£17M'}},
            {{year: 2028, sites: 459, mw: 46, avg: 0.10, priority: 459, investment: '£23M'}},
            {{year: 2029, sites: 801, mw: 81, avg: 0.10, priority: 801, investment: '£40M'}},
            {{year: 2030, sites: 892, mw: 108, avg: 0.12, priority: 645, investment: '£54M'}},
            {{year: 2031, sites: 1043, mw: 128, avg: 0.12, priority: 567, investment: '£64M'}},
            {{year: 2032, sites: 987, mw: 142, avg: 0.14, priority: 432, investment: '£71M'}},
            {{year: 2033, sites: 876, mw: 131, avg: 0.15, priority: 298, investment: '£65M'}},
            {{year: 2034, sites: 765, mw: 114, avg: 0.15, priority: 187, investment: '£57M'}},
            {{year: 2035, sites: 543, mw: 85, avg: 0.16, priority: 98, investment: '£42M'}}
        ];
        
        yearlyData.forEach(row => {{
            const tr = document.createElement('tr');
            tr.className = 'border-b hover:bg-gray-50';
            tr.innerHTML = `
                <td class="py-2 font-semibold">${{row.year}}</td>
                <td class="py-2 text-right">${{row.sites}}</td>
                <td class="py-2 text-right">${{row.mw}} MW</td>
                <td class="py-2 text-right">${{row.avg}} MW</td>
                <td class="py-2 text-right">${{row.priority}}</td>
                <td class="py-2 text-right font-bold" style="color: var(--saber-green)">${{row.investment}}</td>
            `;
            yearlyBreakdown.appendChild(tr);
        }});
        
        // Export function
        function exportData() {{
            alert('Export functionality would download CSV/Excel file with analytics data');
        }}
    </script>
</body>
</html>"""
    
    return html_content


def main():
    logger.info("Creating Saber analytics dashboard...")
    
    # Create dashboard
    dashboard_html = create_analytics_dashboard()
    
    # Save dashboard
    with open('visualizations/saber_analytics_dashboard.html', 'w') as f:
        f.write(dashboard_html)
    
    print("\n" + "="*60)
    print("SABER ANALYTICS DASHBOARD CREATED")
    print("="*60)
    print("\n✅ Features included:")
    print("   • FIT expiry timeline showing sites losing support each year")
    print("   • Cumulative capacity becoming available over time")
    print("   • Regional opportunity timeline by major regions")
    print("   • Window distribution (Urgent/Optimal/Planning/Future)")
    print("   • Capacity by turbine age groups")
    print("   • Efficiency score trends over time")
    print("   • Detailed year-by-year breakdown table")
    print("\n📁 Dashboard: visualizations/saber_analytics_dashboard.html")
    
    # Try to open
    import webbrowser
    import os
    full_path = os.path.abspath('visualizations/saber_analytics_dashboard.html')
    webbrowser.open(f"file://{full_path}")


if __name__ == "__main__":
    main()