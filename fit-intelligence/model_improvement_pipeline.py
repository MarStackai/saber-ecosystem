#!/usr/bin/env python3
"""
Model Improvement Pipeline for FIT Intelligence Chatbot
Processes conversation data to create fine-tuning datasets and improve model performance
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import pandas as pd
import numpy as np
from conversation_logger import ConversationLogger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelImprovementPipeline:
    """
    Pipeline for analyzing conversation data and creating model improvement datasets
    """
    
    def __init__(self, conversation_logger: ConversationLogger, 
                 output_dir: str = "model_improvement_data"):
        self.logger = conversation_logger
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def analyze_conversation_patterns(self, days: int = 30) -> Dict:
        """Analyze conversation patterns to identify improvement opportunities"""
        
        analytics = self.logger.get_conversation_analytics(days)
        poor_queries = self.logger.get_poor_performing_queries(min_rating=3.0, limit=50)
        
        analysis = {
            'analysis_period': f"{days} days",
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_conversations': analytics['basic_stats']['total_conversations'],
                'avg_rating': analytics['feedback_stats']['avg_rating'],
                'improvement_candidates': len(poor_queries),
                'data_accuracy': analytics['quality_stats']['avg_accuracy'],
                'hallucination_rate': analytics['quality_stats']['hallucination_rate']
            },
            'improvement_priorities': []
        }
        
        # Identify priority areas for improvement
        if analytics['quality_stats']['hallucination_rate'] > 5.0:
            analysis['improvement_priorities'].append({
                'area': 'Hallucination Reduction',
                'severity': 'HIGH',
                'current_rate': f"{analytics['quality_stats']['hallucination_rate']}%",
                'target_rate': '< 2%',
                'recommendation': 'Implement stricter factual grounding and data validation'
            })
            
        if analytics['feedback_stats']['avg_rating'] < 4.0:
            analysis['improvement_priorities'].append({
                'area': 'Response Quality',
                'severity': 'MEDIUM',
                'current_rating': analytics['feedback_stats']['avg_rating'],
                'target_rating': '> 4.2',
                'recommendation': 'Focus on business relevance and response completeness'
            })
            
        if len(poor_queries) > 10:
            analysis['improvement_priorities'].append({
                'area': 'Query Understanding',
                'severity': 'MEDIUM',
                'poor_query_count': len(poor_queries),
                'recommendation': 'Create specialized training data for common failure patterns'
            })
        
        # Save analysis report
        report_path = self.output_dir / f"conversation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        logger.info(f"Conversation analysis saved to {report_path}")
        return analysis
    
    def generate_fine_tuning_dataset(self, min_rating: float = 4.0, 
                                   max_examples: int = 1000) -> str:
        """Generate high-quality fine-tuning dataset in OpenAI format"""
        
        training_data = self.logger.export_training_data(min_rating=min_rating)
        
        if len(training_data) == 0:
            logger.warning("No high-quality conversations found for fine-tuning")
            return None
            
        # Limit dataset size
        if len(training_data) > max_examples:
            training_data = training_data[:max_examples]
        
        # Format for OpenAI fine-tuning
        formatted_data = []
        for item in training_data:
            # Add system prompt with anti-hallucination instructions
            system_prompt = """You are the FIT Intelligence Assistant, an expert in UK renewable energy markets and Feed-in Tariff (FIT) schemes. 

CRITICAL GUIDELINES:
1. ONLY use information from the provided database results
2. If no relevant data is found, clearly state this - never guess or fabricate
3. Always cite specific data points (e.g., "Based on 15 sites in our database...")
4. Focus on business opportunities: PPA contracts, repowering, acquisition targets
5. Be precise with numbers, dates, and technical specifications

HALLUCINATION PREVENTION RULES:
- Never mention sites, companies, or specific details not in the data
- Always quantify your responses ("Found X sites", "Y MW capacity")
- If data is limited, acknowledge limitations explicitly
- Prefer saying "I don't have specific data on that" rather than guessing"""

            formatted_item = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": item['messages'][0]['content']},
                    {"role": "assistant", "content": item['messages'][1]['content']}
                ]
            }
            formatted_data.append(formatted_item)
        
        # Save dataset
        dataset_path = self.output_dir / f"fine_tuning_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(dataset_path, 'w') as f:
            for item in formatted_data:
                f.write(json.dumps(item) + '\n')
        
        logger.info(f"Fine-tuning dataset with {len(formatted_data)} examples saved to {dataset_path}")
        return str(dataset_path)
    
    def generate_evaluation_dataset(self, test_size: int = 100) -> str:
        """Generate evaluation dataset for model testing"""
        
        # Get a mix of high and medium-rated conversations for evaluation
        high_quality = self.logger.export_training_data(min_rating=4.0)
        medium_quality = self.logger.export_training_data(min_rating=3.0)
        
        # Select balanced evaluation set
        eval_data = []
        if len(high_quality) > test_size // 2:
            eval_data.extend(high_quality[:test_size // 2])
        else:
            eval_data.extend(high_quality)
            
        remaining = test_size - len(eval_data)
        if len(medium_quality) > remaining:
            eval_data.extend(medium_quality[:remaining])
        else:
            eval_data.extend(medium_quality)
        
        # Format for evaluation
        eval_formatted = []
        for item in eval_data:
            eval_item = {
                "input": item['messages'][0]['content'],
                "expected_output": item['messages'][1]['content'],
                "metadata": item['metadata']
            }
            eval_formatted.append(eval_item)
        
        # Save evaluation dataset
        eval_path = self.output_dir / f"evaluation_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(eval_path, 'w') as f:
            json.dump(eval_formatted, f, indent=2)
        
        logger.info(f"Evaluation dataset with {len(eval_formatted)} examples saved to {eval_path}")
        return str(eval_path)
    
    def create_improvement_recommendations(self) -> Dict:
        """Generate specific improvement recommendations based on data analysis"""
        
        poor_queries = self.logger.get_poor_performing_queries(min_rating=3.5, limit=20)
        analytics = self.logger.get_conversation_analytics(30)
        
        recommendations = {
            'timestamp': datetime.now().isoformat(),
            'model_improvements': [],
            'data_improvements': [],
            'system_improvements': [],
            'priority_queries': []
        }
        
        # Model improvement recommendations
        if analytics['quality_stats']['hallucination_rate'] > 3.0:
            recommendations['model_improvements'].append({
                'type': 'Anti-hallucination Training',
                'priority': 'HIGH',
                'description': 'Fine-tune with examples of saying "I don\'t have data" rather than guessing',
                'implementation': 'Create negative examples dataset with proper "no data" responses'
            })
        
        if analytics['feedback_stats']['avg_rating'] < 4.0:
            recommendations['model_improvements'].append({
                'type': 'Response Quality Enhancement',
                'priority': 'MEDIUM', 
                'description': 'Improve business relevance and completeness of responses',
                'implementation': 'Fine-tune on high-rated business-focused conversations'
            })
        
        # Data improvement recommendations
        if analytics['basic_stats']['avg_data_points'] < 10:
            recommendations['data_improvements'].append({
                'type': 'Search Result Enhancement',
                'priority': 'HIGH',
                'description': 'Improve vector search to return more relevant results',
                'implementation': 'Optimize embedding similarity thresholds and search parameters'
            })
        
        # System improvements
        recommendations['system_improvements'].append({
            'type': 'Response Validation',
            'priority': 'MEDIUM',
            'description': 'Add automated fact-checking against database',
            'implementation': 'Implement post-processing validation of numerical claims'
        })
        
        # Priority queries needing attention
        for query in poor_queries[:5]:
            recommendations['priority_queries'].append({
                'query': query['query'][:100] + '...' if len(query['query']) > 100 else query['query'],
                'avg_rating': query['avg_rating'],
                'feedback_count': query['feedback_count'],
                'suggested_fix': 'Review and create improved training example'
            })
        
        # Save recommendations
        rec_path = self.output_dir / f"improvement_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(rec_path, 'w') as f:
            json.dump(recommendations, f, indent=2)
        
        logger.info(f"Improvement recommendations saved to {rec_path}")
        return recommendations
    
    def run_full_pipeline(self) -> Dict:
        """Run the complete model improvement pipeline"""
        
        logger.info("Starting model improvement pipeline...")
        
        results = {
            'pipeline_run': datetime.now().isoformat(),
            'steps_completed': [],
            'outputs': {}
        }
        
        try:
            # Step 1: Analyze conversation patterns
            analysis = self.analyze_conversation_patterns(30)
            results['steps_completed'].append('conversation_analysis')
            results['outputs']['analysis'] = analysis
            
            # Step 2: Generate fine-tuning dataset
            if analysis['summary']['total_conversations'] > 10:
                ft_dataset = self.generate_fine_tuning_dataset(min_rating=4.0)
                if ft_dataset:
                    results['steps_completed'].append('fine_tuning_dataset')
                    results['outputs']['fine_tuning_dataset'] = ft_dataset
            
            # Step 3: Generate evaluation dataset
            eval_dataset = self.generate_evaluation_dataset()
            if eval_dataset:
                results['steps_completed'].append('evaluation_dataset')
                results['outputs']['evaluation_dataset'] = eval_dataset
            
            # Step 4: Create recommendations
            recommendations = self.create_improvement_recommendations()
            results['steps_completed'].append('recommendations')
            results['outputs']['recommendations'] = recommendations
            
            # Save pipeline summary
            summary_path = self.output_dir / f"pipeline_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Model improvement pipeline completed. Summary: {summary_path}")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            results['error'] = str(e)
        
        return results

def main():
    """Run the model improvement pipeline"""
    
    # Initialize components
    conversation_logger = ConversationLogger("fit_conversations.db")
    pipeline = ModelImprovementPipeline(conversation_logger)
    
    # Run pipeline
    results = pipeline.run_full_pipeline()
    
    print("\n" + "="*60)
    print("MODEL IMPROVEMENT PIPELINE RESULTS")
    print("="*60)
    print(f"Pipeline completed: {len(results['steps_completed'])} steps")
    print(f"Analysis period: Last 30 days")
    
    if 'analysis' in results['outputs']:
        analysis = results['outputs']['analysis']
        print(f"\nConversations analyzed: {analysis['summary']['total_conversations']}")
        print(f"Average rating: {analysis['summary']['avg_rating']:.2f}/5.0")
        print(f"Data accuracy: {analysis['summary']['data_accuracy']:.1%}")
        print(f"Hallucination rate: {analysis['summary']['hallucination_rate']:.1%}")
        
        if analysis['improvement_priorities']:
            print(f"\nImprovement priorities:")
            for priority in analysis['improvement_priorities']:
                print(f"  • {priority['area']} ({priority['severity']})")
    
    if 'fine_tuning_dataset' in results['outputs']:
        print(f"\nFine-tuning dataset: {results['outputs']['fine_tuning_dataset']}")
    
    if 'evaluation_dataset' in results['outputs']:
        print(f"Evaluation dataset: {results['outputs']['evaluation_dataset']}")
    
    print(f"\nAll outputs saved to: {pipeline.output_dir}")
    print("="*60)

if __name__ == '__main__':
    main()