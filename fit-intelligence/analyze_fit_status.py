#!/usr/bin/env python3
"""
Analyze FIT status and create visualizations with accurate UK coordinates
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from pathlib import Path

from src.fit_data_processor import RealFITDataProcessor
from src.fit_analyzer import FITAnalyzer
from src.repowering_scorer import RepoweringScorer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    # Initialize components
    processor = RealFITDataProcessor()
    analyzer = FITAnalyzer()
    scorer = RepoweringScorer()
    
    # Define the FIT data files
    fit_files = [
        'data/Feed-in Tariff Installation Report Part 1.xlsx',
        'data/Feed-in Tariff Installation Report Part 2.xlsx',
        'data/Feed-in Tariff Installation Report Part 3.xlsx'
    ]
    
    logger.info("="*60)
    logger.info("ANALYZING FIT STATUS AND REMAINING LIFE")
    logger.info("="*60)
    
    # Load and combine all data
    all_data = []
    for file_path in fit_files:
        logger.info(f"Loading {file_path}...")
        df = processor.load_fit_excel(file_path)
        wind_df = processor.filter_wind_turbines(df)
        all_data.append(wind_df)
    
    # Combine all dataframes
    combined_df = pd.concat(all_data, ignore_index=True)
    logger.info(f"Total wind turbines loaded: {len(combined_df)}")
    
    # Clean the data
    combined_df = processor.clean_wind_data(combined_df)
    
    # Analyze FIT status and get proper coordinates
    logger.info("Analyzing FIT expiry dates and mapping coordinates...")
    analyzed_df = analyzer.analyze_fit_portfolio(combined_df)
    
    # Get summary statistics
    stats = analyzer.get_fit_summary_stats(analyzed_df)
    
    # Filter for sites with remaining FIT life
    active_fit_df = analyzed_df[analyzed_df['fit_status'].isin(['ACTIVE', 'EXPIRING_SOON'])].copy()
    
    # Calculate repowering scores for active sites
    logger.info("Calculating repowering scores for active FIT sites...")
    scored_data = []
    for idx, row in active_fit_df.iterrows():
        turbine_data = {
            'id': str(row.get('fit_id', idx)),
            'metadata': processor.create_turbine_metadata(row)
        }
        score_result = scorer.calculate_repowering_score(turbine_data)
        
        # Add FIT-specific data
        score_result['remaining_fit_years'] = row['remaining_fit_years']
        score_result['fit_expiry_date'] = row['fit_expiry_date']
        score_result['repowering_window'] = row['repowering_window']
        score_result['latitude'] = row['latitude']
        score_result['longitude'] = row['longitude']
        score_result['postcode'] = row.get('postcode', '')
        
        scored_data.append(score_result)
    
    # Create results dataframe
    results_df = pd.DataFrame(scored_data)
    
    # Sort by repowering window and score
    window_priority = {'URGENT': 0, 'OPTIMAL': 1, 'TOO_EARLY': 2, 'TOO_LATE': 3}
    results_df['window_priority'] = results_df['repowering_window'].map(window_priority)
    results_df = results_df.sort_values(['window_priority', 'overall_score'], ascending=[True, False])
    
    # Display results
    print("\n" + "="*60)
    print("FIT PORTFOLIO ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\nTOTAL SITES: {stats['total_sites']}")
    print(f"├─ Active FIT: {stats['active_fit_sites']} sites")
    print(f"├─ Expiring Soon (≤2 years): {stats['expiring_soon_sites']} sites")
    print(f"└─ Already Expired: {stats['expired_sites']} sites")
    
    print(f"\nREPOWERING WINDOWS (Active FIT sites only):")
    window_counts = results_df['repowering_window'].value_counts()
    for window in ['URGENT', 'OPTIMAL', 'TOO_EARLY', 'TOO_LATE']:
        if window in window_counts.index:
            count = window_counts[window]
            print(f"├─ {window}: {count} sites")
    
    print(f"\nCAPACITY ANALYSIS:")
    print(f"├─ Total capacity with active FIT: {stats['total_capacity_with_fit_mw']:.2f} MW")
    print(f"└─ Capacity in optimal window (5-10 years): {stats['capacity_optimal_window_mw']:.2f} MW")
    
    print(f"\nAVERAGE REMAINING FIT LIFE: {stats['average_remaining_years']:.1f} years")
    
    # Show top repowering candidates with FIT life
    print("\n" + "="*60)
    print("TOP 20 REPOWERING CANDIDATES (WITH ACTIVE FIT)")
    print("="*60)
    
    for i, row in results_df.head(20).iterrows():
        if i < 20:  # Safety check
            details = row['turbine_details']
            print(f"\n{i+1}. FIT ID: {row['turbine_id']}")
            print(f"   Location: {details['location']}")
            print(f"   Postcode: {row.get('postcode', 'Unknown')}")
            print(f"   Capacity: {details['capacity_mw']:.2f} MW")
            print(f"   Age: {details['age_years']:.1f} years")
            print(f"   Remaining FIT: {row['remaining_fit_years']:.1f} years")
            print(f"   FIT Expires: {row['fit_expiry_date'].strftime('%Y-%m-%d') if pd.notna(row['fit_expiry_date']) else 'Unknown'}")
            print(f"   Repowering Window: {row['repowering_window']}")
            print(f"   Priority Score: {row['overall_score']:.3f} ({row['priority']})")
            if row.get('recommendations'):
                print(f"   Action: {row['recommendations'][0]}")
    
    # Regional analysis
    print("\n" + "="*60)
    print("REGIONAL DISTRIBUTION (ACTIVE FIT SITES)")
    print("="*60)
    
    regional_counts = active_fit_df['region'].value_counts().head(10)
    for region, count in regional_counts.items():
        capacity = active_fit_df[active_fit_df['region'] == region]['capacity_mw'].sum()
        avg_remaining = active_fit_df[active_fit_df['region'] == region]['remaining_fit_years'].mean()
        print(f"{region}: {count} sites | {capacity:.2f} MW | {avg_remaining:.1f} years remaining")
    
    # Save enhanced results
    output_file = 'data/wind_turbine_fit_analysis.csv'
    results_df.to_csv(output_file, index=False)
    print(f"\nDetailed results saved to: {output_file}")
    
    # Save geographic data for mapping
    geo_df = results_df[['turbine_id', 'latitude', 'longitude', 'overall_score', 
                         'priority', 'remaining_fit_years', 'repowering_window',
                         'postcode']].copy()
    geo_df['turbine_details'] = results_df['turbine_details'].apply(str)
    geo_file = 'data/turbine_coordinates.csv'
    geo_df.to_csv(geo_file, index=False)
    print(f"Geographic data saved to: {geo_file}")
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("\nKey Findings:")
    print(f"✓ {stats['active_fit_sites']} sites still have active FIT income")
    print(f"✓ {stats['optimal_repowering_sites']} sites in optimal repowering window (5-10 years FIT remaining)")
    print(f"✓ {stats['urgent_repowering_sites']} sites need urgent attention (2-5 years FIT remaining)")
    print(f"✓ Coordinates mapped for accurate UK visualization")


if __name__ == "__main__":
    main()