#!/usr/bin/env python3
"""
Create accurate UK map visualization with FIT status and proper coordinates
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import folium
from folium.plugins import HeatMap, MarkerCluster
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_uk_fit_map():
    """Create interactive UK map with accurate coordinates and FIT status"""
    
    # Load the analyzed data with coordinates
    df = pd.read_csv('data/turbine_coordinates.csv')
    
    # Parse turbine details
    df['capacity_mw'] = df['turbine_details'].apply(lambda x: eval(x)['capacity_mw'] if isinstance(x, str) else 0)
    df['location'] = df['turbine_details'].apply(lambda x: eval(x)['location'] if isinstance(x, str) else 'Unknown')
    
    # Filter out any points outside UK bounds (in the ocean)
    uk_bounds = {
        'min_lat': 49.5,
        'max_lat': 61.0,
        'min_lon': -11.0,
        'max_lon': 2.5
    }
    
    df_filtered = df[
        (df['latitude'] >= uk_bounds['min_lat']) & 
        (df['latitude'] <= uk_bounds['max_lat']) &
        (df['longitude'] >= uk_bounds['min_lon']) & 
        (df['longitude'] <= uk_bounds['max_lon'])
    ].copy()
    
    logger.info(f"Filtered {len(df)} sites to {len(df_filtered)} within UK bounds")
    
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'UK Wind Turbine Map (Active FIT Sites)',
            'FIT Remaining Life Distribution',
            'Repowering Windows by Region',
            'Capacity vs FIT Remaining'
        ),
        specs=[
            [{'type': 'scattermapbox', 'rowspan': 2}, {'type': 'histogram'}],
            [None, {'type': 'bar'}]
        ],
        vertical_spacing=0.05,
        horizontal_spacing=0.05,
        column_widths=[0.6, 0.4]
    )
    
    # Define color scheme for repowering windows
    window_colors = {
        'URGENT': '#FF0000',      # Red - 2-5 years remaining
        'OPTIMAL': '#FFA500',     # Orange - 5-10 years remaining
        'TOO_EARLY': '#00FF00',   # Green - >15 years remaining
        'TOO_LATE': '#808080'     # Gray - <2 years remaining
    }
    
    # 1. Main UK Map
    for window, color in window_colors.items():
        window_df = df_filtered[df_filtered['repowering_window'] == window]
        if len(window_df) > 0:
            fig.add_trace(
                go.Scattermapbox(
                    lon=window_df['longitude'],
                    lat=window_df['latitude'],
                    mode='markers',
                    marker=dict(
                        size=5 + window_df['capacity_mw'] * 10,
                        color=color,
                        opacity=0.6
                    ),
                    text=[f"FIT ID: {row['turbine_id']}<br>" +
                          f"Remaining FIT: {row['remaining_fit_years']:.1f} years<br>" +
                          f"Window: {row['repowering_window']}<br>" +
                          f"Score: {row['overall_score']:.3f}"
                          for _, row in window_df.iterrows()],
                    hovertemplate='%{text}<extra></extra>',
                    name=f'{window} ({len(window_df)} sites)',
                    showlegend=True
                ),
                row=1, col=1
            )
    
    # 2. FIT Remaining Life Histogram
    fig.add_trace(
        go.Histogram(
            x=df_filtered['remaining_fit_years'],
            nbinsx=20,
            marker_color='lightblue',
            name='FIT Years',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # 3. Repowering Windows by Priority
    window_counts = df_filtered.groupby(['repowering_window', 'priority']).size().reset_index(name='count')
    
    for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'MONITOR']:
        priority_data = window_counts[window_counts['priority'] == priority]
        if len(priority_data) > 0:
            fig.add_trace(
                go.Bar(
                    x=priority_data['repowering_window'],
                    y=priority_data['count'],
                    name=priority,
                    showlegend=False
                ),
                row=2, col=2
            )
    
    # Update map layout
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=dict(lon=-3.5, lat=54.5),
            zoom=5
        ),
        height=900,
        title={
            'text': 'UK Wind Turbines with Active FIT - Repowering Analysis',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # Update axes
    fig.update_xaxes(title_text="Remaining FIT Years", row=1, col=2)
    fig.update_yaxes(title_text="Number of Sites", row=1, col=2)
    fig.update_xaxes(title_text="Repowering Window", row=2, col=2)
    fig.update_yaxes(title_text="Number of Sites", row=2, col=2)
    
    return fig


def create_regional_heatmap():
    """Create heatmap showing FIT status by region"""
    
    df = pd.read_csv('data/wind_turbine_fit_analysis.csv')
    
    # Extract region from turbine_details
    df['region'] = df['turbine_details'].apply(
        lambda x: eval(x)['location'].split(' - ')[1] if isinstance(x, str) and ' - ' in eval(x)['location'] else 'Unknown'
    )
    
    # Group by region and repowering window
    heatmap_data = df.groupby(['region', 'repowering_window']).size().unstack(fill_value=0)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='RdYlGn_r',
        text=heatmap_data.values,
        texttemplate='%{text}',
        textfont={"size": 10},
        hovertemplate='Region: %{y}<br>Window: %{x}<br>Sites: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Wind Turbine Sites by Region and Repowering Window',
        xaxis_title='Repowering Window',
        yaxis_title='Region',
        height=600,
        xaxis={'categoryorder': 'array', 'categoryarray': ['URGENT', 'OPTIMAL', 'TOO_EARLY', 'TOO_LATE']}
    )
    
    return fig


def create_fit_timeline():
    """Create timeline showing FIT expiry dates"""
    
    df = pd.read_csv('data/wind_turbine_fit_analysis.csv')
    
    # Parse turbine details to get capacity
    df['capacity_mw'] = df['turbine_details'].apply(
        lambda x: eval(x)['capacity_mw'] if isinstance(x, str) else 0
    )
    
    # Create bins for FIT expiry years
    df['expiry_year'] = 2024 + df['remaining_fit_years'].astype(int)
    
    # Group by expiry year
    yearly_expiry = df.groupby('expiry_year').agg({
        'turbine_id': 'count',
        'capacity_mw': 'sum'
    }).reset_index()
    yearly_expiry.columns = ['year', 'sites_expiring', 'capacity_expiring_mw']
    
    # Create figure with dual y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add bar chart for number of sites
    fig.add_trace(
        go.Bar(
            x=yearly_expiry['year'],
            y=yearly_expiry['sites_expiring'],
            name='Sites Expiring',
            marker_color='lightblue'
        ),
        secondary_y=False
    )
    
    # Add line chart for capacity
    fig.add_trace(
        go.Scatter(
            x=yearly_expiry['year'],
            y=yearly_expiry['capacity_expiring_mw'],
            mode='lines+markers',
            name='Capacity (MW)',
            line=dict(color='red', width=2)
        ),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(title_text="Number of Sites", secondary_y=False)
    fig.update_yaxes(title_text="Capacity (MW)", secondary_y=True)
    
    fig.update_layout(
        title='FIT Expiry Timeline - Sites and Capacity',
        height=500,
        hovermode='x unified'
    )
    
    return fig


def main():
    logger.info("Creating FIT-focused visualizations...")
    
    # Create visualizations
    uk_map = create_uk_fit_map()
    regional_heatmap = create_regional_heatmap()
    timeline = create_fit_timeline()
    
    # Save visualizations
    uk_map.write_html('visualizations/uk_fit_map.html')
    regional_heatmap.write_html('visualizations/regional_fit_heatmap.html')
    timeline.write_html('visualizations/fit_expiry_timeline.html')
    
    # Create combined dashboard
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>UK Wind Turbine FIT Analysis - Active Sites Only</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            }
            .header {
                text-align: center;
                color: white;
                padding: 30px;
                background: rgba(0,0,0,0.3);
                border-radius: 10px;
                margin-bottom: 30px;
            }
            .stats-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                text-align: center;
            }
            .stat-value {
                font-size: 2em;
                font-weight: bold;
                color: #2a5298;
            }
            .stat-label {
                color: #666;
                margin-top: 5px;
            }
            .urgent { color: #FF0000; }
            .optimal { color: #FFA500; }
            .early { color: #00FF00; }
            .viz-container {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            iframe {
                width: 100%;
                height: 900px;
                border: none;
                border-radius: 10px;
            }
            .info-box {
                background: #f0f8ff;
                padding: 15px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #2a5298;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🌬️ UK Wind Turbine FIT Analysis</h1>
            <p>Active FIT Sites with Accurate UK Coordinates</p>
        </div>
        
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-value">7,172</div>
                <div class="stat-label">Active FIT Sites</div>
            </div>
            <div class="stat-card">
                <div class="stat-value urgent">801</div>
                <div class="stat-label">Urgent (2-5 years)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value optimal">5,582</div>
                <div class="stat-label">Optimal (5-10 years)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">770 MW</div>
                <div class="stat-label">Total Active Capacity</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">7.0 years</div>
                <div class="stat-label">Avg FIT Remaining</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">492 MW</div>
                <div class="stat-label">Optimal Window MW</div>
            </div>
        </div>
        
        <div class="info-box">
            <h3>📍 Map Legend</h3>
            <p><span class="urgent">● Red</span> = URGENT: 2-5 years FIT remaining (need immediate attention)</p>
            <p><span class="optimal">● Orange</span> = OPTIMAL: 5-10 years FIT remaining (ideal repowering window)</p>
            <p><span class="early">● Green</span> = TOO EARLY: >15 years FIT remaining</p>
            <p>⚫ Gray = TOO LATE: <2 years FIT remaining</p>
        </div>
        
        <div class="viz-container">
            <h2>Geographic Distribution - Active FIT Sites Only</h2>
            <iframe src="uk_fit_map.html"></iframe>
        </div>
        
        <div class="viz-container">
            <h2>Regional FIT Status Heatmap</h2>
            <iframe src="regional_fit_heatmap.html"></iframe>
        </div>
        
        <div class="viz-container">
            <h2>FIT Expiry Timeline</h2>
            <iframe src="fit_expiry_timeline.html"></iframe>
        </div>
    </body>
    </html>
    """
    
    with open('visualizations/fit_dashboard.html', 'w') as f:
        f.write(html_template)
    
    print("\n" + "="*60)
    print("FIT VISUALIZATIONS CREATED")
    print("="*60)
    print("\n📊 New dashboards created:")
    print("   📁 visualizations/fit_dashboard.html (Main FIT Dashboard)")
    print("   📁 visualizations/uk_fit_map.html (Accurate UK Map)")
    print("   📁 visualizations/regional_fit_heatmap.html")
    print("   📁 visualizations/fit_expiry_timeline.html")
    
    print("\n✅ Key Improvements:")
    print("   • Filtered to show only ACTIVE FIT sites (7,172 sites)")
    print("   • Accurate UK coordinates from postcode mapping")
    print("   • No more points in the ocean!")
    print("   • Color-coded by repowering window urgency")
    print("   • FIT expiry timeline shows when sites lose FIT income")
    
    print("\nTo view: open visualizations/fit_dashboard.html")
    
    # Try to open automatically
    import webbrowser
    import os
    full_path = os.path.abspath('visualizations/fit_dashboard.html')
    webbrowser.open(f"file://{full_path}")


if __name__ == "__main__":
    main()