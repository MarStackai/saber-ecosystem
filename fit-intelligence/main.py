import os
import sys
import argparse
import logging
from pathlib import Path
import pandas as pd
from typing import Optional

from src.data_processor import FITDataProcessor
from src.vector_database import WindTurbineVectorDB
from src.repowering_scorer import RepoweringScorer
from src.data_generator import generate_sample_excel_data
from src.config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WindRepoweringSystem:
    def __init__(self):
        self.config = Config()
        self.processor = FITDataProcessor()
        self.vector_db = None
        self.scorer = RepoweringScorer()
        
        if self.config.PINECONE_API_KEY:
            try:
                self.vector_db = WindTurbineVectorDB()
            except Exception as e:
                logger.warning(f"Could not initialize Pinecone: {e}")
                logger.info("Running in offline mode without vector database")
    
    def process_and_store_data(self, file_path: str, sheet_name: Optional[str] = None):
        logger.info(f"Processing FIT data from {file_path}")
        
        processed_data = self.processor.process_fit_data(file_path, sheet_name)
        
        if self.vector_db:
            logger.info("Storing data in vector database...")
            self.vector_db.upsert_turbine_data(processed_data)
            
            stats = self.vector_db.get_index_stats()
            logger.info(f"Vector database stats: {stats}")
        else:
            logger.info("Vector database not available, skipping storage")
        
        scored_turbines = self.scorer.score_multiple_turbines(processed_data)
        
        summary = self.scorer.get_priority_summary(scored_turbines)
        
        return {
            'processed_count': len(processed_data),
            'scored_turbines': scored_turbines[:10],
            'summary': summary
        }
    
    def search_turbines_for_repowering(
        self,
        query: Optional[str] = None,
        min_age_years: Optional[float] = None,
        max_capacity_mw: Optional[float] = None,
        location: Optional[str] = None,
        top_k: int = 20
    ):
        if not self.vector_db:
            logger.error("Vector database not initialized")
            return []
        
        if query:
            results = self.vector_db.search_similar_turbines(query, top_k)
        else:
            results = self.vector_db.search_by_criteria(
                min_age_years=min_age_years,
                max_capacity_mw=max_capacity_mw,
                location=location,
                top_k=top_k
            )
        
        scored_results = self.scorer.score_multiple_turbines(results)
        
        return scored_results
    
    def analyze_portfolio(self, file_path: str, sheet_name: Optional[str] = None):
        logger.info(f"Analyzing portfolio from {file_path}")
        
        processed_data = self.processor.process_fit_data(file_path, sheet_name)
        
        scored_turbines = self.scorer.score_multiple_turbines(processed_data)
        
        summary = self.scorer.get_priority_summary(scored_turbines)
        
        critical_turbines = [t for t in scored_turbines if t['priority'] == 'CRITICAL']
        high_priority = [t for t in scored_turbines if t['priority'] == 'HIGH']
        
        return {
            'summary': summary,
            'critical_turbines': critical_turbines,
            'high_priority_turbines': high_priority[:10],
            'total_analyzed': len(scored_turbines)
        }


def main():
    parser = argparse.ArgumentParser(description='Wind Turbine Repowering Analysis System')
    parser.add_argument('command', choices=['generate', 'process', 'search', 'analyze'],
                       help='Command to execute')
    parser.add_argument('--file', '-f', help='Path to Excel/CSV file')
    parser.add_argument('--sheet', '-s', help='Sheet name for Excel files')
    parser.add_argument('--query', '-q', help='Search query for similar turbines')
    parser.add_argument('--min-age', type=float, help='Minimum turbine age in years')
    parser.add_argument('--max-capacity', type=float, help='Maximum capacity in MW')
    parser.add_argument('--location', help='Location filter')
    parser.add_argument('--top-k', type=int, default=20, help='Number of results to return')
    
    args = parser.parse_args()
    
    system = WindRepoweringSystem()
    
    if args.command == 'generate':
        output_path = args.file or 'data/sample_fit_data.xlsx'
        generate_sample_excel_data(output_path, num_records=50)
        logger.info(f"Sample data generated at {output_path}")
    
    elif args.command == 'process':
        if not args.file:
            logger.error("Please provide a file path with --file")
            sys.exit(1)
        
        result = system.process_and_store_data(args.file, args.sheet)
        
        print("\n" + "="*60)
        print("PROCESSING RESULTS")
        print("="*60)
        print(f"Processed {result['processed_count']} turbine records")
        print(f"\nPORTFOLIO SUMMARY:")
        summary = result['summary']
        print(f"  Total turbines: {summary['total_turbines']}")
        print(f"  Average repowering score: {summary['average_score']}")
        print(f"  Immediate action required: {summary['immediate_action_required']} turbines")
        print(f"  Total repowering potential: {summary['total_repowering_potential_mw']} MW")
        
        print(f"\nPRIORITY BREAKDOWN:")
        for priority, count in summary['priority_counts'].items():
            capacity = summary['total_capacity_mw_by_priority'][priority]
            print(f"  {priority}: {count} turbines ({capacity} MW)")
        
        print(f"\nTOP 10 REPOWERING CANDIDATES:")
        for i, turbine in enumerate(result['scored_turbines'], 1):
            details = turbine['turbine_details']
            print(f"\n  {i}. Turbine ID: {turbine['turbine_id']}")
            print(f"     Score: {turbine['overall_score']} ({turbine['priority']})")
            print(f"     Details: {details['manufacturer']} {details['model']}")
            print(f"     Age: {details['age_years']:.1f} years, Capacity: {details['capacity_mw']:.2f} MW")
            print(f"     Location: {details['location']}")
            if turbine['recommendations']:
                print(f"     Recommendations: {turbine['recommendations'][0]}")
    
    elif args.command == 'search':
        if not system.vector_db:
            logger.error("Vector database not configured. Please set PINECONE_API_KEY in .env")
            sys.exit(1)
        
        results = system.search_turbines_for_repowering(
            query=args.query,
            min_age_years=args.min_age,
            max_capacity_mw=args.max_capacity,
            location=args.location,
            top_k=args.top_k
        )
        
        print("\n" + "="*60)
        print("SEARCH RESULTS")
        print("="*60)
        print(f"Found {len(results)} matching turbines\n")
        
        for i, turbine in enumerate(results[:10], 1):
            details = turbine['turbine_details']
            print(f"{i}. Turbine ID: {turbine['turbine_id']}")
            print(f"   Score: {turbine['overall_score']} ({turbine['priority']})")
            print(f"   {details['manufacturer']} {details['model']}")
            print(f"   Age: {details['age_years']:.1f} years, Capacity: {details['capacity_mw']:.2f} MW")
            print(f"   Location: {details['location']}")
            print()
    
    elif args.command == 'analyze':
        if not args.file:
            logger.error("Please provide a file path with --file")
            sys.exit(1)
        
        result = system.analyze_portfolio(args.file, args.sheet)
        
        print("\n" + "="*60)
        print("PORTFOLIO ANALYSIS REPORT")
        print("="*60)
        
        summary = result['summary']
        print(f"\nPORTFOLIO OVERVIEW:")
        print(f"  Total turbines analyzed: {result['total_analyzed']}")
        print(f"  Average repowering score: {summary['average_score']}")
        print(f"  Immediate action required: {summary['immediate_action_required']} turbines")
        print(f"  Total repowering potential: {summary['total_repowering_potential_mw']} MW")
        
        print(f"\nPRIORITY CLASSIFICATION:")
        for priority, count in summary['priority_counts'].items():
            capacity = summary['total_capacity_mw_by_priority'][priority]
            percentage = (count / result['total_analyzed'] * 100) if result['total_analyzed'] > 0 else 0
            print(f"  {priority}: {count} turbines ({percentage:.1f}%) - {capacity:.2f} MW")
        
        if result['critical_turbines']:
            print(f"\nCRITICAL TURBINES REQUIRING IMMEDIATE ATTENTION:")
            for turbine in result['critical_turbines'][:5]:
                details = turbine['turbine_details']
                print(f"  • ID: {turbine['turbine_id']} - {details['manufacturer']} {details['model']}")
                print(f"    Age: {details['age_years']:.1f} years, Capacity: {details['capacity_mw']:.2f} MW")
                print(f"    Location: {details['location']}")
                print(f"    Score: {turbine['overall_score']}")
                if turbine['recommendations']:
                    print(f"    Action: {turbine['recommendations'][0]}")
                print()


if __name__ == "__main__":
    main()