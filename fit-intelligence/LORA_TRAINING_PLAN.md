# LoRA Fine-Tuning Plan for FIT Intelligence

## Problem Statement
The current regex-based NLP processor cannot properly understand queries like:
- "wind sites over 100kw in berkshire" 
- "solar farms in Yorkshire expiring soon"
- "show me all large wind installations in East Anglia"

## Solution: LoRA Fine-Tuning

### 1. Base Model Selection
- **Llama 3.1 8B** or **Mistral 7B** (run locally)
- Small enough for local inference
- Good at structured output generation

### 2. Training Data Format
Create training pairs from actual FIT data:

```json
{
  "instruction": "Parse this FIT query into structured filters",
  "input": "wind sites over 100kw in berkshire",
  "output": {
    "technology": "Wind",
    "capacity_min_kw": 100,
    "location": "Berkshire",
    "postcode_patterns": ["RG", "SL"],
    "action": "search"
  }
}

{
  "instruction": "Parse this FIT query into structured filters",  
  "input": "all solar farms in Yorkshire expiring within 2 years",
  "output": {
    "technology": "Photovoltaic",
    "location": "Yorkshire",
    "postcode_patterns": ["YO", "HU", "DN", "HD", "WF", "LS", "BD"],
    "fit_remaining_max_years": 2,
    "action": "search"
  }
}
```

### 3. Training Dataset Generation
Generate from our 40,194 records:
- Location variations (counties, regions, postcodes)
- Capacity ranges (kW, MW, descriptive terms)
- Technology types (wind, solar, hydro)
- Time windows (expiring, urgent, soon)
- Aggregations (total, average, count by)

### 4. LoRA Configuration
```python
lora_config = LoRAConfig(
    r=16,  # Rank
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    task_type="CAUSAL_LM"
)
```

### 5. Integration Architecture
```
User Query → LoRA Model → Structured JSON → ChromaDB Filter → Results
```

### 6. Benefits Over Current System
- **Understands context**: "large" = >500kW, "small" = <50kW
- **Regional knowledge**: "East Anglia" = Norfolk, Suffolk, Cambridgeshire
- **Flexible language**: "expiring", "ending soon", "FIT running out"
- **Multi-filter queries**: Combines location + capacity + technology correctly

### 7. Implementation Steps
1. Generate training dataset from ChromaDB (1000+ examples)
2. Fine-tune Llama 3.1 8B with LoRA
3. Deploy model locally with Ollama
4. Replace regex parser with LoRA inference
5. Test with complex queries

### 8. Expected Improvements
- Query: "wind sites over 100kw in berkshire"
  - Current: Returns all 3,206 wind sites
  - With LoRA: Returns only Berkshire wind sites >100kW

- Query: "large solar farms in the north"
  - Current: Fails to understand
  - With LoRA: Returns PV sites >1MW in Northern England

### 9. Training Tools
- **Unsloth**: Fast LoRA training
- **Ollama**: Local deployment
- **vLLM**: Fast inference
- **Weights & Biases**: Track experiments

### 10. Success Metrics
- Precision: % of returned results matching query intent
- Recall: % of relevant results found
- Query understanding: Human evaluation of 100 test queries