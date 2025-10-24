#!/usr/bin/env python3
"""
Process real FIT data files and populate the vector database
"""

import os
import sys
import logging
from pathlib import Path

from src.fit_data_processor import RealFITDataProcessor
from src.vector_database import WindTurbineVectorDB
from src.repowering_scorer import RepoweringScorer
from src.config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    # Initialize components
    processor = RealFITDataProcessor()
    scorer = RepoweringScorer()
    
    # Define the FIT data files
    fit_files = [
        'data/Feed-in Tariff Installation Report Part 1.xlsx',
        'data/Feed-in Tariff Installation Report Part 2.xlsx',
        'data/Feed-in Tariff Installation Report Part 3.xlsx'
    ]
    
    # Check if files exist
    for file_path in fit_files:
        if not Path(file_path).exists():
            logger.error(f"File not found: {file_path}")
            sys.exit(1)
    
    logger.info("="*60)
    logger.info("PROCESSING REAL FIT DATA")
    logger.info("="*60)
    
    # Process all files
    all_turbine_data = processor.process_multiple_files(fit_files)
    
    if not all_turbine_data:
        logger.error("No wind turbine data found in the files")
        sys.exit(1)
    
    # Score all turbines
    logger.info("\nScoring turbines for repowering priority...")
    scored_turbines = scorer.score_multiple_turbines(all_turbine_data)
    
    # Get summary
    summary = scorer.get_priority_summary(scored_turbines)
    
    # Display results
    print("\n" + "="*60)
    print("WIND TURBINE PORTFOLIO ANALYSIS")
    print("="*60)
    print(f"\nTotal wind turbines found: {len(all_turbine_data)}")
    print(f"Average repowering score: {summary['average_score']:.3f}")
    print(f"Immediate action required: {summary['immediate_action_required']} turbines")
    print(f"Total repowering potential: {summary['total_repowering_potential_mw']:.2f} MW")
    
    print("\nPRIORITY BREAKDOWN:")
    for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'MONITOR']:
        count = summary['priority_counts'][priority]
        capacity = summary['total_capacity_mw_by_priority'][priority]
        percentage = (count / len(all_turbine_data) * 100) if all_turbine_data else 0
        print(f"  {priority}: {count} turbines ({percentage:.1f}%) - {capacity:.2f} MW")
    
    # Show top candidates
    print("\nTOP 20 REPOWERING CANDIDATES:")
    print("-" * 60)
    
    for i, turbine in enumerate(scored_turbines[:20], 1):
        details = turbine['turbine_details']
        print(f"\n{i}. FIT ID: {turbine['turbine_id']}")
        print(f"   Score: {turbine['overall_score']:.3f} ({turbine['priority']})")
        print(f"   Capacity: {details['capacity_mw']:.2f} MW")
        print(f"   Age: {details['age_years']:.1f} years")
        print(f"   Location: {details['location']}")
        if turbine['recommendations']:
            print(f"   Action: {turbine['recommendations'][0]}")
    
    # Initialize vector database if configured
    config = Config()
    if config.PINECONE_API_KEY:
        try:
            logger.info("\n" + "="*60)
            logger.info("POPULATING VECTOR DATABASE")
            logger.info("="*60)
            
            vector_db = WindTurbineVectorDB()
            
            # Clear existing data and upload new data
            logger.info("Uploading turbine data to Pinecone...")
            vector_db.upsert_turbine_data(all_turbine_data, batch_size=100)
            
            # Get stats
            stats = vector_db.get_index_stats()
            print(f"\nVector database updated:")
            print(f"  Total vectors: {stats['total_vectors']}")
            print(f"  Dimension: {stats['dimension']}")
            
        except Exception as e:
            logger.error(f"Failed to update vector database: {e}")
    else:
        logger.info("\nVector database not configured (set PINECONE_API_KEY to enable)")
    
    # Save results to CSV for further analysis
    import pandas as pd
    
    results_df = pd.DataFrame([
        {
            'fit_id': t['turbine_id'],
            'score': t['overall_score'],
            'priority': t['priority'],
            'capacity_mw': t['turbine_details']['capacity_mw'],
            'age_years': t['turbine_details']['age_years'],
            'location': t['turbine_details']['location'],
            'age_score': t['component_scores']['age_score'],
            'capacity_score': t['component_scores']['capacity_score'],
            'efficiency_score': t['component_scores']['efficiency_score'],
            'location_score': t['component_scores']['location_score'],
            'recommendations': '; '.join(t['recommendations'])
        }
        for t in scored_turbines
    ])
    
    output_file = 'data/wind_turbine_repowering_analysis.csv'
    results_df.to_csv(output_file, index=False)
    print(f"\nResults saved to: {output_file}")
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()