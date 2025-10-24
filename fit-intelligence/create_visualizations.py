#!/usr/bin/env python3
"""
Create interactive geographic heat map and visualizations for UK wind turbine data
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    # Check if analysis file exists
    analysis_file = 'data/wind_turbine_repowering_analysis.csv'
    if not Path(analysis_file).exists():
        logger.error(f"Analysis file not found: {analysis_file}")
        logger.info("Please run 'python3 process_real_data.py' first to generate the analysis")
        sys.exit(1)
    
    # Import visualizer
    from src.geo_visualizer import WindTurbineGeoVisualizer
    
    logger.info("="*60)
    logger.info("CREATING INTERACTIVE VISUALIZATIONS")
    logger.info("="*60)
    
    # Initialize visualizer
    visualizer = WindTurbineGeoVisualizer(analysis_file)
    
    # Create and save all visualizations
    logger.info("Generating visualizations...")
    output_files = visualizer.save_all_visualizations()
    
    print("\n" + "="*60)
    print("VISUALIZATIONS CREATED SUCCESSFULLY")
    print("="*60)
    print("\n📊 Interactive dashboards have been created:")
    print("\n1. COMBINED DASHBOARD (Main Entry Point):")
    print(f"   📁 {output_files['combined']}")
    print("   Features: All visualizations in one interface with navigation tabs")
    
    print("\n2. Individual Visualizations:")
    print(f"   📊 Main Dashboard: {output_files['dashboard']}")
    print(f"   🗺️  Geographic Map: {output_files['map']}")
    print(f"   🔥 Regional Heatmap: {output_files['heatmap']}")
    print(f"   📈 Fleet Evolution: {output_files['animation']}")
    
    print("\n" + "="*60)
    print("HOW TO VIEW")
    print("="*60)
    print("\n1. Open the combined dashboard in your browser:")
    print(f"   open {output_files['combined']}")
    print("\n2. Or open individual visualizations:")
    print(f"   open {output_files['dashboard']}")
    
    print("\n" + "="*60)
    print("FEATURES")
    print("="*60)
    print("\n✨ Interactive Features:")
    print("   • Hover over data points for detailed information")
    print("   • Click and drag to zoom in on specific areas")
    print("   • Use sliders to filter by age ranges")
    print("   • Animation shows fleet evolution over time")
    print("   • Regional heatmap shows performance metrics")
    print("   • Priority distribution with color coding")
    
    print("\n🎯 Key Insights Visualized:")
    print("   • Geographic concentration of turbines")
    print("   • Age vs capacity relationships")
    print("   • Regional repowering priorities")
    print("   • Capacity distribution by location")
    print("   • Historical installation patterns")
    
    print("\n" + "="*60)
    print("VISUALIZATION COMPLETE")
    print("="*60)
    
    # Try to open the combined dashboard automatically
    import webbrowser
    import os
    
    full_path = os.path.abspath(output_files['combined'])
    url = f"file://{full_path}"
    
    print(f"\n🚀 Opening dashboard in your default browser...")
    webbrowser.open(url)


if __name__ == "__main__":
    main()