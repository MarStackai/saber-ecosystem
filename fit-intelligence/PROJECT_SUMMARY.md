# FIT Intelligence Project Summary

## Current System
- **ChromaDB Vector Database**: 75,194+ renewable energy installations
- **Embedding Model**: all-MiniLM-L6-v2 (sentence transformers)
- **Query Types**: Natural language queries for capacity, technology, location
- **Geographic Intelligence**: UK postcode/location mapping
- **Web Interface**: Flask API + HTML interface

## Training Objective
Improve natural language query understanding for renewable energy terminology:

### Current Issues
- "wind sites over 250kW" sometimes returns <250kW results
- Location parsing inconsistent ("near beverly" vs "around liverpool") 
- Combined queries not properly filtered

### Training Approach
1. **Fine-tune embedding model** on renewable energy terminology
2. **Create synthetic training data** with known query-intent pairs
3. **Contrastive learning** for better semantic understanding
4. **Domain-specific vocabulary** (kW, MW, wind, solar, Yorkshire, etc.)

## Expected Improvements
- Better capacity range filtering
- Improved location understanding
- More consistent query parsing
- Reduced "No results found" for valid queries

## Hardware Requirements Met
- ✅ 24GB GPU (optimal batch sizes)
- ✅ 128GB RAM (large dataset loading)
- ✅ Fast storage (model checkpointing)

## File Structure
```
fit_intelligence_package/
├── training_pipeline.py          # Main training script
├── real_query_trainer.py         # Performance analysis
├── deploy_trained_model.py       # Model deployment
├── enhanced_fit_intelligence_api.py  # Current API
├── geo_enhanced_fit_chatbot.py   # Current chatbot
├── chroma_db/                    # Vector database
├── data/                         # Training data
└── ubuntu_setup.sh              # System setup
```
