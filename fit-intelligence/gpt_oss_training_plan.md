# GPT-OSS FIT Intelligence Training Plan

## Current Problems
1. Geographic filtering is broken (Aberdeen query returns BD/ML postcodes instead of AB)
2. FIT IDs not included in responses
3. Context not maintained between queries
4. Poor instruction following
5. Inconsistent response formats

## Training Strategy

### Phase 1: Data Preparation (Week 1)

#### 1.1 Core Dataset Enhancement
- Add FIT IDs to ALL responses
- Ensure geographic accuracy in training data
- Create explicit instruction-response pairs

```python
# Example training format
{
  "instruction": "what are the site ids of wind over 250kw near aberdeen",
  "context": "Aberdeen postcodes: AB10-AB56",
  "response": "Found 3 wind sites over 250kW near Aberdeen:\n\n1. FIT ID: 12345\n   • Technology: Wind\n   • Capacity: 500kW\n   • Location: AB21 (Aberdeen)\n   • FIT Rate: 15.2p/kWh\n\n2. FIT ID: 12346\n   • Technology: Wind\n   • Capacity: 335kW\n   • Location: AB51 (Aberdeenshire)\n   • FIT Rate: 14.9p/kWh"
}
```

#### 1.2 Geographic Training Data
Create explicit mappings:
- Aberdeen: AB postcodes only
- Edinburgh: EH postcodes only
- Glasgow: G postcodes only
- Yorkshire: YO, HU, LS, BD, HX, HD, WF, S, DN
- Scotland: AB, DD, DG, EH, FK, G, HS, IV, KA, KW, KY, ML, PA, PH, TD, ZE

#### 1.3 Conversation Context Training
```python
# Multi-turn conversation examples
{
  "conversation": [
    {"user": "wind farms over 1MW in Scotland", 
     "assistant": "Found 5 wind farms over 1MW in Scotland:\n1. FIT ID: 7891..."},
    {"user": "what are their FIT rates?",
     "assistant": "The FIT rates for these sites are:\n• FIT ID 7891: 12.3p/kWh\n• FIT ID 7892: 14.5p/kWh..."}
  ]
}
```

### Phase 2: Training Implementation (Week 2)

#### 2.1 LoRA Fine-tuning Configuration
```yaml
model: gpt-oss:20b
training:
  lora_r: 32
  lora_alpha: 64
  learning_rate: 1e-5
  batch_size: 4
  gradient_accumulation: 8
  epochs: 3
  temperature: 0.1  # For generation during training
```

#### 2.2 Training Dataset Categories
1. **FIT ID Queries** (5,000 examples)
   - Direct lookups
   - Rate queries
   - Multi-site comparisons

2. **Geographic Searches** (5,000 examples)
   - City/region specific
   - Postcode validation
   - Distance-based queries

3. **Technical Queries** (5,000 examples)
   - Capacity filters
   - Technology combinations
   - Repowering analysis

4. **Conversation Context** (5,000 examples)
   - Follow-up questions
   - Clarifications
   - Related queries

### Phase 3: Evaluation & Testing (Week 3)

#### 3.1 Benchmark Tests
```python
test_queries = [
    {
        "query": "wind over 250kw near Aberdeen",
        "must_have": ["AB postcode", "FIT ID", ">250kW"],
        "must_not_have": ["BD", "ML", "YO"]
    },
    {
        "query": "what are their FIT IDs",
        "requires_context": True,
        "must_have": ["FIT ID", "previous results"]
    }
]
```

#### 3.2 Accuracy Metrics
- Geographic accuracy: 100% (only correct postcodes)
- FIT ID inclusion: 100% (always show when available)
- Capacity filtering: ±5% tolerance
- Context retention: 95%+ accuracy

### Phase 4: Production Deployment

#### 4.1 Inference Pipeline
```python
class GPTOSSFITIntelligence:
    def __init__(self):
        self.model = "gpt-oss-fit:20b"
        self.temperature = 0.1
        self.context_window = []
        
    def query(self, user_input, include_fit_ids=True):
        # Always include FIT IDs
        # Validate geographic accuracy
        # Maintain conversation context
        pass
```

#### 4.2 Response Validation
- Postcode validator
- FIT ID verifier
- Capacity checker
- Rate validator

## Implementation Timeline

### Immediate Actions (Today)
1. Fix geographic filtering in current system
2. Add FIT IDs to all responses
3. Generate proper training data

### Week 1
- Generate 20,000 high-quality training examples
- Validate all geographic data
- Create conversation chains

### Week 2
- Fine-tune GPT-OSS:20b
- Test on validation set
- Iterate on problem areas

### Week 3
- Production testing
- Team feedback integration
- Performance optimization

### Success Criteria
1. **100% geographic accuracy** - Aberdeen queries return ONLY AB postcodes
2. **100% FIT ID inclusion** - Every site shows its FIT ID
3. **95% instruction following** - Understands "what are their IDs" in context
4. **<2s response time** - Fast enough for production
5. **Zero hallucination** - Only returns real database entries

## Training Data Generator

```python
def generate_fit_training_data():
    templates = {
        "fit_id_query": "What is the FIT ID for the {technology} site in {location}?",
        "geographic_search": "Show me {technology} sites over {capacity}kW near {city}",
        "follow_up": "What are their FIT IDs?",
        "rate_query": "What are the FIT rates for sites {fit_ids}?"
    }
    
    # Ensure geographic accuracy
    city_postcodes = {
        "Aberdeen": ["AB10", "AB11", "AB12", "AB21", "AB22", "AB23"],
        "Edinburgh": ["EH1", "EH2", "EH3", "EH4", "EH5", "EH6"],
        "Glasgow": ["G1", "G2", "G3", "G4", "G11", "G12"],
        # ... etc
    }
    
    # Generate with proper responses
    for city, postcodes in city_postcodes.items():
        # Only include sites with matching postcodes
        # Always include FIT IDs
        # Maintain conversation context
```

This plan will create a powerful, accurate GPT-OSS model specifically for FIT intelligence that:
- Never makes geographic errors
- Always includes FIT IDs
- Understands context
- Responds with facts only
- Maintains conversation state