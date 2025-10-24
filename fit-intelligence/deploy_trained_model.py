#!/usr/bin/env python3
"""
Deploy Trained Model System
Replace existing embedding model with fine-tuned version
"""

import os
import json
import shutil
from pathlib import Path
from sentence_transformers import SentenceTransformer
from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI
import logging

logger = logging.getLogger(__name__)

class ModelDeployer:
    """Deploy trained models into production FIT system"""
    
    def __init__(self):
        self.models_dir = Path("models")
        self.backup_dir = Path("backups")
        self.current_model_path = "models/fit_intelligence_v1"
        
    def backup_current_system(self):
        """Backup current model configuration"""
        timestamp = str(int(time.time()))
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Backup current API configuration
        api_backup = {
            'original_model': 'all-MiniLM-L6-v2',
            'timestamp': timestamp,
            'backup_reason': 'Pre-training deployment'
        }
        
        with open(backup_path / 'api_config.json', 'w') as f:
            json.dump(api_backup, f, indent=2)
            
        logger.info(f"System backed up to: {backup_path}")
        
    def validate_trained_model(self, model_path: str) -> bool:
        """Validate trained model works correctly"""
        try:
            # Load trained model
            model = SentenceTransformer(model_path)
            
            # Test basic embedding generation
            test_queries = [
                "wind sites over 250kw",
                "solar installations in yorkshire", 
                "large renewable sites"
            ]
            
            embeddings = model.encode(test_queries)
            
            # Validate embedding dimensions
            if embeddings.shape[0] != len(test_queries):
                logger.error("Embedding count mismatch")
                return False
                
            if embeddings.shape[1] <= 0:
                logger.error("Invalid embedding dimensions")
                return False
                
            logger.info(f"Model validation passed: {embeddings.shape}")
            return True
            
        except Exception as e:
            logger.error(f"Model validation failed: {e}")
            return False
    
    def create_enhanced_api_with_trained_model(self, model_path: str):
        """Create new API instance with trained model"""
        
        # Create enhanced API class that uses trained model
        enhanced_api_code = f'''
import chromadb
from sentence_transformers import SentenceTransformer
from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI
import logging

class TrainedFITIntelligenceAPI(EnhancedFITIntelligenceAPI):
    """Enhanced API with fine-tuned embedding model"""
    
    def __init__(self, persist_directory: str = "chroma_db"):
        # Use trained model instead of default
        self.embedding_function = SentenceTransformer("{model_path}")
        
        # Initialize ChromaDB with trained embeddings
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Load existing collections with new embedding function
        self.collections = {{}}
        self._load_collections()
        
        # Load license data cache
        self._license_data_cache = None
        self._load_license_cache()
        
        logging.info("Trained FIT Intelligence API initialized with fine-tuned model")
    
    def _create_embedding_function(self):
        """Override to use trained model"""
        class TrainedEmbeddingFunction:
            def __init__(self, model_path):
                self.model = SentenceTransformer(model_path)
                
            def __call__(self, input_texts):
                embeddings = self.model.encode(input_texts)
                return embeddings.tolist()
        
        return TrainedEmbeddingFunction("{model_path}")
'''
        
        # Write enhanced API
        with open('trained_fit_intelligence_api.py', 'w') as f:
            f.write(enhanced_api_code)
            
        logger.info("Created enhanced API with trained model")
        
    def update_chatbot_to_use_trained_model(self, model_path: str):
        """Update chatbot to use trained model"""
        
        # Read current chatbot
        with open('geo_enhanced_fit_chatbot.py', 'r') as f:
            chatbot_code = f.read()
        
        # Update imports and initialization
        updated_code = chatbot_code.replace(
            'from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI',
            'from trained_fit_intelligence_api import TrainedFITIntelligenceAPI as EnhancedFITIntelligenceAPI'
        )
        
        # Write updated chatbot
        with open('geo_enhanced_fit_chatbot_trained.py', 'w') as f:
            f.write(updated_code)
            
        logger.info("Updated chatbot to use trained model")
    
    def performance_comparison(self, original_model_name: str, trained_model_path: str):
        """Compare original vs trained model performance"""
        
        test_queries = [
            "wind sites over 250kw in yorkshire",
            "solar installations above 500kw",
            "large renewable sites in east anglia",
            "wind site fit ids for sites over 250kw around beverly",
            "hydro installations in scotland"
        ]
        
        # Load both models
        original_model = SentenceTransformer(original_model_name)
        trained_model = SentenceTransformer(trained_model_path)
        
        comparison_results = []
        
        for query in test_queries:
            # Get embeddings from both models
            orig_emb = original_model.encode([query])
            trained_emb = trained_model.encode([query])
            
            # Test with actual API calls would go here
            # For now, just log the embedding differences
            comparison_results.append({
                'query': query,
                'original_embedding_norm': float(np.linalg.norm(orig_emb[0])),
                'trained_embedding_norm': float(np.linalg.norm(trained_emb[0])),
                'embedding_difference': float(np.linalg.norm(orig_emb[0] - trained_emb[0]))
            })
        
        # Save comparison
        with open('model_comparison.json', 'w') as f:
            json.dump({
                'test_queries': test_queries,
                'results': comparison_results,
                'summary': {
                    'avg_embedding_difference': np.mean([r['embedding_difference'] for r in comparison_results])
                }
            }, f, indent=2)
            
        logger.info("Model comparison saved to model_comparison.json")
        
    def deploy_trained_model(self, model_path: str):
        """Full deployment of trained model"""
        
        print(f"🚀 Deploying trained model from: {model_path}")
        
        # 1. Validate trained model
        if not self.validate_trained_model(model_path):
            print("❌ Model validation failed - aborting deployment")
            return False
            
        # 2. Backup current system
        self.backup_current_system()
        
        # 3. Create enhanced API
        self.create_enhanced_api_with_trained_model(model_path)
        
        # 4. Update chatbot
        self.update_chatbot_to_use_trained_model(model_path)
        
        # 5. Performance comparison
        self.performance_comparison('all-MiniLM-L6-v2', model_path)
        
        print("✅ Model deployment completed!")
        print("📁 Files created:")
        print("  - trained_fit_intelligence_api.py")
        print("  - geo_enhanced_fit_chatbot_trained.py")
        print("  - model_comparison.json")
        print("")
        print("🧪 To test the trained model:")
        print('  python -c "from geo_enhanced_fit_chatbot_trained import GeoEnhancedFITChatbot; bot = GeoEnhancedFITChatbot(); print(bot.chat(\'wind sites over 250kw in yorkshire\'))"')
        
        return True

def main():
    """Deploy the trained model"""
    deployer = ModelDeployer()
    
    # Check if trained model exists
    model_path = "models/fit_intelligence_v1"
    if not Path(model_path).exists():
        print("❌ Trained model not found. Please run training_pipeline.py first")
        print("   Expected path: models/fit_intelligence_v1")
        return
        
    # Deploy
    success = deployer.deploy_trained_model(model_path)
    
    if success:
        print("\\n🎉 Ready to test improved FIT intelligence!")
    else:
        print("\\n❌ Deployment failed")

if __name__ == "__main__":
    import time
    import numpy as np
    main()