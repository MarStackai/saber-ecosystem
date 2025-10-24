# FIT Intelligence - Next Training Phases

## Current Status ✅
- [x] Base system setup with 40,194 renewable energy sites
- [x] PyTorch 2.7.1 + Transformers installed 
- [x] Initial embedding model trained (87.5% accuracy)
- [x] ChromaDB vector database populated
- [ ] GPT-OSS model downloading (ETA: ~20 minutes)

## Phase 1: Domain-Specific Fine-Tuning (After GPT-OSS)
**Goal**: Adapt GPT-OSS to understand renewable energy terminology

### 1.1 Create Training Dataset
```python
# Generate domain-specific Q&A pairs from your data
python3 create_fit_training_data.py
```
- Extract patterns from 40K sites
- Generate technical Q&A pairs
- Include FIT rates, capacity factors, grid codes

### 1.2 Fine-tune with LoRA
```python
# Efficient fine-tuning for RTX 3090
python3 lora_finetune_gpt_oss.py \
  --model gpt-oss \
  --data fit_training_data.json \
  --epochs 3 \
  --batch_size 4
```

## Phase 2: RAG Enhancement Training
**Goal**: Optimize retrieval-augmented generation

### 2.1 Query Understanding Model
```python
# Train query parser for better intent detection
python3 train_query_parser.py
```
- Classify query types (location, capacity, technology, etc.)
- Extract structured parameters
- Handle complex multi-part queries

### 2.2 Reranking Model
```python
# Train to rerank ChromaDB results
python3 train_reranker.py
```
- Score relevance of retrieved documents
- Consider user intent
- Optimize for FIT-specific metrics

## Phase 3: Specialized Models

### 3.1 Repowering Prediction Model
```python
# Predict repowering opportunities
python3 train_repowering_model.py
```
Input features:
- Age, capacity, technology
- Historical performance
- Grid connection data
- Regional factors

Output: Repowering score & timeline

### 3.2 FIT Rate Optimizer
```python
# Optimize FIT rate recommendations
python3 train_fit_optimizer.py
```
- Predict optimal technology mix
- Calculate ROI projections
- Consider policy changes

### 3.3 Location Intelligence
```python
# Enhanced geographic understanding
python3 train_location_model.py
```
- UK-specific place name resolution
- Grid capacity analysis
- Planning constraint awareness

## Phase 4: Multi-Model Ensemble

### 4.1 Model Orchestra
```python
# Coordinate multiple models
python3 create_model_ensemble.py
```
Architecture:
```
User Query → GPT-OSS (parse)
    ↓
Query Parser → Parameter Extraction
    ↓
ChromaDB → Retrieval (40K sites)
    ↓
Reranker → Top Results
    ↓
Specialized Models → Insights
    ↓
GPT-OSS → Natural Response
```

### 4.2 Performance Optimization
```python
# Optimize for RTX 3090
python3 optimize_inference.py \
  --quantize int8 \
  --compile \
  --batch_size 8
```

## Phase 5: Continuous Learning Pipeline

### 5.1 Feedback Loop
```python
# Learn from user interactions
python3 setup_feedback_loop.py
```
- Track successful queries
- Identify failure patterns
- Auto-generate training data

### 5.2 A/B Testing Framework
```python
# Compare model versions
python3 ab_testing_framework.py
```
- Route % of queries to new models
- Measure success metrics
- Auto-promote better models

## Training Schedule

### Week 1 (Starting Today)
- [ ] Complete GPT-OSS setup
- [ ] Generate domain training data
- [ ] Start LoRA fine-tuning

### Week 2
- [ ] Train query parser
- [ ] Implement reranking
- [ ] Test ensemble system

### Week 3
- [ ] Train specialized models
- [ ] Optimize inference
- [ ] Deploy production system

### Week 4
- [ ] Setup monitoring
- [ ] Implement feedback loop
- [ ] Performance benchmarking

## Resource Requirements

### GPU Time Estimates (RTX 3090)
- GPT-OSS fine-tuning: 4-6 hours
- Query parser: 1 hour
- Reranker: 2 hours
- Specialized models: 3-4 hours each
- Total: ~15-20 hours GPU time

### Storage
- Models: ~50GB
- Training data: ~5GB
- Checkpoints: ~20GB
- Total: ~75GB needed

## Quick Start Commands

```bash
# After GPT-OSS downloads
cd ~/fit_intelligence

# Test GPT-OSS
ollama run gpt-oss

# Start Phase 1 training
source venv/bin/activate
python3 create_fit_training_data.py
python3 lora_finetune_gpt_oss.py

# Monitor GPU
watch -n 1 nvidia-smi
```

## Success Metrics

1. **Query Understanding**: 95%+ intent accuracy
2. **Retrieval Precision**: 90%+ relevant results
3. **Response Quality**: Human-like explanations
4. **Inference Speed**: <2s per query
5. **User Satisfaction**: 85%+ positive feedback

## Next Immediate Steps

1. ✅ Wait for GPT-OSS download (~20 min)
2. ⏳ Create training data generation script
3. ⏳ Setup LoRA fine-tuning pipeline
4. ⏳ Test baseline performance
5. ⏳ Begin Phase 1 training

---

Ready to start as soon as GPT-OSS is ready!