#!/usr/bin/env python3
"""
FIT Intelligence Training Pipeline
Fine-tune models for better natural language understanding of renewable energy queries
"""

import torch
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer, InputExample, losses
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from torch.utils.data import DataLoader
import numpy as np
import random

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrainingConfig:
    """Training configuration"""
    base_model: str = "all-MiniLM-L6-v2"
    output_dir: str = "models/fit_intelligence_v1"
    batch_size: int = 16
    epochs: int = 4
    warmup_steps: int = 100
    learning_rate: float = 2e-5
    max_seq_length: int = 256
    gpu_memory_gb: int = 24

class FITTrainingDataGenerator:
    """Generate training data from existing FIT database"""
    
    def __init__(self):
        self.renewable_technologies = ['Wind', 'Photovoltaic', 'Hydro', 'Anaerobic digestion']
        self.capacity_ranges = [
            (0, 50), (50, 100), (100, 250), (250, 500), 
            (500, 1000), (1000, 2000), (2000, 5000)
        ]
        self.uk_regions = [
            'Yorkshire', 'Scotland', 'Wales', 'Cornwall', 'Devon',
            'East Anglia', 'West Midlands', 'North West', 'South West',
            'London', 'Birmingham', 'Manchester', 'Liverpool', 'Bristol',
            'Leeds', 'Sheffield', 'Newcastle', 'Glasgow', 'Edinburgh'
        ]
        
    def generate_synthetic_queries(self, num_samples: int = 1000) -> List[Dict]:
        """Generate synthetic training queries with known intents"""
        training_data = []
        
        # Query patterns for different intents
        patterns = {
            'capacity_filter': [
                "sites over {capacity}kW",
                "installations above {capacity}kW", 
                "projects greater than {capacity}kW",
                "sites between {min_cap} and {max_cap}kW",
                "installations from {min_cap} to {max_cap}kW"
            ],
            'technology_filter': [
                "{tech} sites",
                "{tech} installations", 
                "{tech} projects",
                "{tech} farms",
                "renewable {tech}"
            ],
            'location_filter': [
                "sites in {location}",
                "installations around {location}",
                "projects near {location}",
                "{location} renewable sites",
                "sites within 25km of {location}"
            ],
            'combined_queries': [
                "{tech} sites over {capacity}kW in {location}",
                "{tech} installations above {capacity}kW near {location}",
                "large {tech} sites in {location}",
                "{tech} projects between {min_cap} and {max_cap}kW around {location}",
                "commercial {tech} sites over {capacity}kW in {location}"
            ]
        }
        
        for i in range(num_samples):
            # Choose random pattern type
            pattern_type = random.choice(list(patterns.keys()))
            pattern = random.choice(patterns[pattern_type])
            
            # Fill in variables
            tech = random.choice(self.renewable_technologies)
            location = random.choice(self.uk_regions)
            capacity = random.choice([100, 250, 500, 1000, 2000])
            min_cap = random.choice([100, 250, 500])
            max_cap = min_cap + random.choice([200, 500, 1000])
            
            query = pattern.format(
                tech=tech.lower(),
                location=location.lower(),
                capacity=capacity,
                min_cap=min_cap,
                max_cap=max_cap
            )
            
            # Create structured intent
            intent = {
                'technology': tech if 'tech' in pattern else None,
                'location': location if 'location' in pattern else None,
                'min_capacity_kw': capacity if 'capacity' in pattern else None,
                'capacity_range': (min_cap, max_cap) if 'min_cap' in pattern else None
            }
            
            training_data.append({
                'query': query,
                'intent': intent,
                'pattern_type': pattern_type
            })
            
        return training_data
    
    def create_positive_negative_pairs(self, training_data: List[Dict]) -> List[InputExample]:
        """Create positive and negative pairs for contrastive learning"""
        examples = []
        
        for i, item in enumerate(training_data):
            query = item['query']
            intent = item['intent']
            
            # Create positive examples (similar intents)
            for j, other_item in enumerate(training_data[i+1:], i+1):
                other_query = other_item['query']
                other_intent = other_item['intent']
                
                # Calculate similarity score based on intent overlap
                similarity = self._calculate_intent_similarity(intent, other_intent)
                
                if similarity > 0.7:  # High similarity
                    examples.append(InputExample(texts=[query, other_query], label=0.9))
                elif similarity < 0.3:  # Low similarity
                    examples.append(InputExample(texts=[query, other_query], label=0.1))
                elif 0.4 < similarity < 0.6:  # Medium similarity
                    examples.append(InputExample(texts=[query, other_query], label=0.5))
                    
                # Limit pairs to avoid explosion
                if len(examples) > 10000:
                    break
            
            if len(examples) > 10000:
                break
                
        return examples
    
    def _calculate_intent_similarity(self, intent1: Dict, intent2: Dict) -> float:
        """Calculate similarity between two intents"""
        similarity = 0.0
        factors = 0
        
        # Technology match
        if intent1.get('technology') and intent2.get('technology'):
            similarity += 1.0 if intent1['technology'] == intent2['technology'] else 0.0
            factors += 1
        
        # Location match
        if intent1.get('location') and intent2.get('location'):
            similarity += 1.0 if intent1['location'] == intent2['location'] else 0.0
            factors += 1
            
        # Capacity range overlap
        if intent1.get('min_capacity_kw') and intent2.get('min_capacity_kw'):
            cap_diff = abs(intent1['min_capacity_kw'] - intent2['min_capacity_kw'])
            cap_similarity = max(0, 1.0 - (cap_diff / 1000))  # Normalize by 1000kW
            similarity += cap_similarity
            factors += 1
            
        return similarity / factors if factors > 0 else 0.0

class FITModelTrainer:
    """Train and fine-tune models for FIT intelligence"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        logger.info(f"GPU Memory available: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
        
    def train_embedding_model(self, training_examples: List[InputExample]) -> SentenceTransformer:
        """Fine-tune sentence transformer for renewable energy domain"""
        
        # Load base model
        model = SentenceTransformer(self.config.base_model)
        logger.info(f"Loaded base model: {self.config.base_model}")
        
        # Split data
        random.shuffle(training_examples)
        split_idx = int(0.8 * len(training_examples))
        train_examples = training_examples[:split_idx]
        eval_examples = training_examples[split_idx:]
        
        logger.info(f"Training on {len(train_examples)} examples, evaluating on {len(eval_examples)}")
        
        # Create data loader
        train_dataloader = DataLoader(
            train_examples, 
            shuffle=True, 
            batch_size=self.config.batch_size
        )
        
        # Define loss function
        train_loss = losses.CosineSimilarityLoss(model)
        
        # Create evaluator
        evaluator = EmbeddingSimilarityEvaluator.from_input_examples(
            eval_examples, 
            name='fit_intelligence_eval'
        )
        
        # Train
        model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            epochs=self.config.epochs,
            evaluator=evaluator,
            evaluation_steps=100,
            warmup_steps=self.config.warmup_steps,
            output_path=self.config.output_dir
        )
        
        logger.info(f"Model saved to: {self.config.output_dir}")
        return model
    
    def create_evaluation_suite(self) -> List[Tuple[str, str, float]]:
        """Create evaluation test cases"""
        test_cases = [
            # High similarity cases
            ("wind sites over 250kw", "wind installations above 250kw", 0.9),
            ("solar farms in yorkshire", "photovoltaic sites in yorkshire", 0.9),
            ("sites near liverpool", "installations around liverpool", 0.8),
            
            # Medium similarity cases
            ("wind sites over 250kw", "solar sites over 250kw", 0.6),
            ("large installations in scotland", "big sites in wales", 0.5),
            
            # Low similarity cases
            ("wind sites over 250kw", "small solar installations", 0.2),
            ("sites in london", "wind farms in scotland", 0.1),
            ("hydro installations", "anaerobic digestion sites", 0.3),
        ]
        return test_cases
    
    def evaluate_model(self, model: SentenceTransformer) -> Dict:
        """Evaluate model performance"""
        test_cases = self.create_evaluation_suite()
        results = []
        
        for query1, query2, expected_sim in test_cases:
            # Get embeddings
            emb1 = model.encode([query1])
            emb2 = model.encode([query2])
            
            # Calculate similarity
            actual_sim = np.dot(emb1[0], emb2[0]) / (np.linalg.norm(emb1[0]) * np.linalg.norm(emb2[0]))
            
            results.append({
                'query1': query1,
                'query2': query2,
                'expected': expected_sim,
                'actual': actual_sim,
                'error': abs(expected_sim - actual_sim)
            })
            
        avg_error = np.mean([r['error'] for r in results])
        
        return {
            'average_error': avg_error,
            'test_cases': results
        }

def main():
    """Main training pipeline"""
    logger.info("🚀 Starting FIT Intelligence Training Pipeline")
    
    # Configuration
    config = TrainingConfig()
    
    # Generate training data
    logger.info("📊 Generating training data...")
    data_generator = FITTrainingDataGenerator()
    training_data = data_generator.generate_synthetic_queries(num_samples=2000)
    
    # Create training examples
    logger.info("🔧 Creating training examples...")
    training_examples = data_generator.create_positive_negative_pairs(training_data)
    logger.info(f"Created {len(training_examples)} training pairs")
    
    # Initialize trainer
    trainer = FITModelTrainer(config)
    
    # Train model
    logger.info("🎯 Training embedding model...")
    fine_tuned_model = trainer.train_embedding_model(training_examples)
    
    # Evaluate
    logger.info("📈 Evaluating model...")
    evaluation_results = trainer.evaluate_model(fine_tuned_model)
    logger.info(f"Average error: {evaluation_results['average_error']:.3f}")
    
    # Save training metadata
    metadata = {
        'timestamp': datetime.now().isoformat(),
        'config': config.__dict__,
        'training_samples': len(training_data),
        'training_pairs': len(training_examples),
        'evaluation_results': evaluation_results
    }
    
    with open(f"{config.output_dir}/training_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info("✅ Training pipeline completed!")
    logger.info(f"Model saved to: {config.output_dir}")
    
    return fine_tuned_model

if __name__ == "__main__":
    model = main()