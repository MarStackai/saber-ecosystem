
import chromadb
from sentence_transformers import SentenceTransformer
from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI
import logging

class TrainedFITIntelligenceAPI(EnhancedFITIntelligenceAPI):
    """Enhanced API with fine-tuned embedding model"""
    
    def __init__(self, persist_directory: str = "chroma_db"):
        # Use trained model instead of default
        self.embedding_function = SentenceTransformer("models/fit_intelligence_v1")
        
        # Initialize ChromaDB with trained embeddings
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Load existing collections with new embedding function
        self.collections = {}
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
        
        return TrainedEmbeddingFunction("models/fit_intelligence_v1")
