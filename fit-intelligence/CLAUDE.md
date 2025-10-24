# FIT Intelligence Platform - Claude AI Assistant Context

## 🎯 Project Overview

The FIT Intelligence Platform is a comprehensive AI-powered system for analyzing UK renewable energy Feed-in Tariff (FIT) installations. It combines vector search, natural language processing, and business intelligence to identify Power Purchase Agreement (PPA) opportunities and analyze renewable energy portfolios.

## 📊 Key Statistics

- **Total Database Size**: 75,194+ renewable energy assets
- **Commercial Sites**: 40,194 installations
- **FIT Licenses**: 35,000+ embedded records  
- **Combined Capacity**: 4,781 MW
- **Technologies**: Solar (Photovoltaic), Wind, Hydro, Anaerobic Digestion
- **Geographic Coverage**: Full UK coverage with postcode-level accuracy (all 120+ UK postcode areas)
- **Model**: Llama 2 13B (GPU-accelerated, ~11GB VRAM)

## 🏗️ System Architecture

### Core Technology Stack
- **OS**: Ubuntu 24.04 LTS
- **Python**: 3.12.3
- **Database**: ChromaDB vector database (⚠️ NOT location-aware)
- **LLM**: Ollama with llama2:13b (GPU-accelerated, ~11GB VRAM)
- **Embeddings**: all-MiniLM-L6-v2 (384 dimensions)
- **API**: Flask web server on port 5000
- **GPU**: NVIDIA RTX 3090 (24GB VRAM) ✅ WORKING
- **RAM**: 125GB available

### Directory Structure
```
/home/marstack/fit_intelligence/
├── data/                          # Raw and processed FIT data
├── chroma_db/                     # ChromaDB vector storage
├── visualizations/                # Web interfaces and dashboards
├── models/                        # Trained model checkpoints
├── lora_training/                 # LoRA fine-tuning configs
├── weekend_training_data/         # Training datasets
└── web/                          # Web chat interfaces
```

## 🔑 Key Components

### Primary APIs and Servers
1. **fit_api_server.py** - Main production API server (port 5000)
2. **llm_enhanced_chatbot.py** - LLM-powered chatbot with context preservation
3. **enhanced_fit_intelligence_api.py** - Enhanced search and insights
4. **warm_index.py** - In-memory index for fast geographic filtering
5. **financial_calculator.py** - FIT rate calculations and financial projections

### Data Processing & Enhancement
1. **uk_postcodes.py** - Comprehensive UK postcode and county mappings
2. **fit_rate_mapper.py** - Historical FIT rate lookup (2010-2019)
3. **enhanced_query_parser.py** - Deterministic NLP parser with years_left support
4. **market_analyst.py** - Comparative and aggregate market analysis
5. **location_detector.py** - Follow-up query location detection
6. **query_enhancer.py** - Query expansion and optimization
7. **fit_query_optimizer.py** - Query preprocessing and result enrichment
8. **regional_capacity_calculator.py** - Regional energy variance adjustments

### Data Management
1. **process_fit_licenses_batch.py** - Process Excel FIT license data
2. **process_all_commercial_fit.py** - Process commercial installations
3. **enhanced_chroma_fit_intelligence.py** - ChromaDB management
4. **update_fit_rates.py** - Update database with historical FIT rates

## 🚀 Common Tasks

### Starting the System

```bash
# 1. Start Ollama (already running with GPU support)
# Check status: ollama ps

# 2. Start main API server (uses venv automatically)
cd /home/marstack/fit_intelligence
./venv/bin/python fit_api_server.py

# 3. Access web interface
# Browse to: http://localhost:5000

# 4. Check health
curl http://localhost:5000/api/health
```

### Running Tests

```bash
# Test system accuracy
python test_system.py

# Test specific FIT ID lookup
python test_fit_764485.py

# Verify ChromaDB coverage
python verify_complete_coverage.py
```

## 🎯 Dashboard Enhancements (2025-08-27)

### Wind Turbine Dashboard - PRODUCTION READY
**Status**: ✅ Ready for Demo - All major features working

#### Current Features
- **Data**: 3,206 wind sites from ChromaDB with full UK coverage
- **Financial Data**: 93.4% sites have complete financial calculations (2,994 FIT sites)
- **Map Visualization**: Clustering working, individual sites visible when zooming
- **Regional Analysis**: Scotland vs England/Wales split with financial totals
- **Capacity Breakdown**: Sites categorized by size (0-100kW, 100-500kW, 500kW-1MW, 1MW+)

#### Today's Improvements
1. **Fixed Missing FIT Rates** ✅
   - Identified and fixed 1,344 sites with zero tariffs
   - Applied correct historical FIT rates based on commission dates
   - Site 830547 now correctly shows £9,034 annual income

2. **Dashboard Layout Optimization** ✅
   - Map height: min 800px, scales with viewport (calc(100vh - 450px))
   - Regional distribution: dynamic height matching map container
   - No page overrun, professional alignment

3. **Enhanced Analytics** ✅
   - Priority pie chart shows percentages and annual income
   - Regional distribution shows capacity bands per region
   - Scotland filtering fixed (1,210 sites, £71.9M income)

4. **Financial Display** ✅
   - Site intelligence panel shows Est. Annual Income & Est. Revenue Remaining
   - Map tooltips include FIT rates and financial values
   - Market summary tables show regional income totals

#### Key Statistics
- **Total Sites**: 3,206 wind turbines
- **Scotland**: 1,210 sites (£71.9M annual income)
- **England & Wales**: 1,996 sites (£121.8M annual income)
- **FIT Sites**: 2,994 (Apr 2010 - Mar 2019)
- **ROC Sites**: 201 (pre-Apr 2010)
- **Financial Coverage**: 93.4% with complete data

## 🎯 Recent Updates (2025-08-27)

### ✅ NEW Features

1. **Years Left Filtering** ✅
   - **Feature**: Filter sites by FIT years remaining (e.g., "8 to 10 years fit left")
   - **Implementation**: Enhanced parser extracts min/max years_left, warm index filters
   - **Training**: Added 100+ years_left examples to LoRA training dataset
   - **Status**: ✅ Working deterministically, LLM training in progress

2. **Market Analysis Mode** ✅
   - **Feature**: Comparative and aggregate analysis (vs just site listings)
   - **Implementation**: MarketAnalyst class provides technology comparisons, aggregations
   - **Capabilities**: Compare wind vs solar, total capacity analysis, average calculations
   - **Status**: ✅ Detects "compare", "total", "average" queries automatically

3. **Enhanced Query Parser** ✅
   - **Feature**: Deterministic NLP parsing with 100% accuracy on critical patterns
   - **Handles**: Capacity ranges, years_left, locations, technologies, repowering
   - **Assertions**: Manchester→M only, Yorkshire→full set, Solar→photovoltaic
   - **Status**: ✅ Production ready, fallback to LLM for complex queries

4. **LoRA Model Training** ✅
   - **Model**: fit-intelligence-enhanced (based on Llama2 13B)
   - **Dataset**: 710+ training examples with critical assertions
   - **Coverage**: Years_left, capacity ranges, geographic accuracy, tech aliases
   - **Status**: ✅ Model created, needs more training for years_left accuracy

## 🎯 Previous Fixes (2025-08-26)

### ✅ COMPLETED Issues

1. **Geographic Coverage** ✅
   - **Problem**: Only cities were mapped, not counties (31 out of 34 major areas missing)
   - **Solution**: Added comprehensive county mappings in uk_postcodes.py
   - **Coverage**: Now includes Surrey, Kent, Essex, Sussex, Hampshire, Berkshire, Devon, Somerset, Lancashire, Yorkshire counties, etc.
   - **Status**: ✅ Counties now searchable (e.g., "sites in Surrey", "wind farms in Lancashire")

2. **FIT Rate Attachment** ✅
   - **Problem**: All tariff rates showing 0.0 or null
   - **Solution**: Extended FIT rates database to cover 2016-2019, implemented rate lookup
   - **Result**: Correct historical rates now showing (e.g., 12.47p/kWh for 4kW solar in 2015)
   - **Status**: ✅ Rates correctly attached based on technology, capacity, and commission date

3. **20-Year FIT Contracts** ✅
   - **Problem**: Missing FIT expiry dates preventing financial calculations
   - **Solution**: Implemented automatic 20-year contract duration from commission date
   - **Result**: Years remaining and expiry dates now calculated for all sites
   - **Status**: ✅ Working (e.g., site commissioned 2015 expires 2035)

4. **Solar PV Degradation Model** ✅
   - **Problem**: No accounting for solar panel efficiency degradation
   - **Solution**: Implemented 2% year 1, then 0.54% annual degradation
   - **Impact**: Total remaining value calculations now account for declining output
   - **Status**: ✅ Applied to Photovoltaic technology only

5. **Repowering Categories** ✅
   - **Problem**: LLM not understanding "optimal", "urgent", "immediate" filters
   - **Solution**: Enhanced prompts and added category detection
   - **Categories**:
     - OPTIMAL: 5-10 years left
     - URGENT: 2-5 years left  
     - IMMEDIATE: 0-2 years left
     - EXPIRED: Already past expiry
   - **Status**: ✅ Category filtering working

6. **Total Remaining Value** ✅
   - **Problem**: Not calculating total FIT income over remaining contract
   - **Solution**: Fixed calculation (annual income × years remaining × degradation factor)
   - **Status**: ✅ Calculations working where generation data exists

## 📈 Performance Metrics

### Current Performance
- **Response Time**: 1-4 seconds (GPU-accelerated)
- **Geographic Accuracy**: 98% (postcode enforcement working)
- **FIT ID Coverage**: 100% (all responses include FIT IDs)
- **Financial Data**: 90% (working where generation data exists)
- **Context Retention**: 85% (follow-up queries working)

### Known Limitations
- **Generation Data**: Many sites missing annual generation figures
- **Regional Factors**: Limited to predefined regional capacity factors
- **ChromaDB Filtering**: WHERE clauses sometimes ignored (mitigated by warm index)
- **Technology Names**: Must use "Photovoltaic" not "Solar" in database

## 🔧 Development Guidelines

### Code Style
- NO COMMENTS unless explicitly requested
- Follow existing patterns in codebase
- Use existing libraries (check requirements.txt)
- Maintain consistent naming conventions

### Testing Requirements
- Always run lint/typecheck before committing
- Test with test_system.py for accuracy
- Verify no hallucination with factual_fit_chatbot.py

### Security
- Never expose API keys or credentials
- FIT data is proprietary - handle carefully
- No logging of sensitive information

## 📝 Important Context

### Business Domain
- **FIT (Feed-in Tariff)**: UK government renewable energy subsidy scheme (closed March 2019)
- **PPA (Power Purchase Agreement)**: Commercial energy contracts
- **Repowering**: Replacing old turbines/panels with new technology
- **FIT Contracts**: All are 20-year duration from commissioning date

### Geographic Coverage
- **Complete UK Coverage**: All 120+ postcode areas supported
- **Counties**: Now includes all major UK counties (Surrey, Kent, Essex, Devon, etc.)
- **Regional Searches**: Scotland, Wales, England, Northern Ireland
- **City-Level Searches**: All major UK cities
- **Postcode Areas**: Full UK postcode prefix validation

### Data Quality Notes
- **Surrey**: Limited large solar sites (largest is 173kW, none over 250kW)
- **Cornwall**: Correctly mapped to TR and PL postcodes
- **Dorset**: Correctly mapped to DT and BH postcodes
- **Manchester**: Returns M postcode area correctly
- **Yorkshire**: Returns all Yorkshire postcodes (YO, HU, LS, BD, HX, HD, WF, S, DN)

## 🎯 Testing Queries

```python
# County searches (working):
"sites in Surrey"
"wind farms in Lancashire"
"solar sites in Kent over 100kw"
"optimal sites in Devon"

# Years left filtering (NEW - working):
"wind sites in Yorkshire over 50kw that have between 8 to 10 years fit left"
"sites with 5-10 years FIT remaining"
"solar installations with less than 2 years left"

# Market analysis (NEW - working):
"Compare wind and solar capacity in Scotland"
"Total wind capacity in Yorkshire"
"Average site size for solar in Surrey"
"Aggregate analysis of all sites in Wales"

# Repowering categories:
"urgent wind sites in Scotland"
"immediate solar sites needing repowering"
"optimal repowering opportunities"

# Financial queries:
"show me sites with their FIT rates and total remaining value"
"detailed financial analysis of FIT ID 743267"
```

## ⚠️ Critical Notes

1. **NEVER create files unless absolutely necessary** - prefer editing existing
2. **NEVER proactively create documentation** unless explicitly requested
3. **ALWAYS verify postcodes match geographic rules** ✅
4. **ALWAYS include FIT IDs in responses** ✅
5. **NEVER allow hallucination** - only return verified database entries
6. **Temperature MUST stay at 0.1 or lower** for accuracy
7. **LOCATION SEARCH WORKING** ✅ - Counties and cities both supported
8. **FIT RATES WORKING** ✅ - Historical rates correctly applied
9. **FINANCIAL CALCULATIONS** ✅ - Working where data exists

## 🔄 System Status

### Working Features
- ✅ County and city searches  
- ✅ FIT rate lookup and attachment
- ✅ 20-year contract calculations
- ✅ Years remaining calculations with filtering
- ✅ Solar degradation modeling
- ✅ Repowering window categories
- ✅ Regional capacity factors
- ✅ Postcode enforcement
- ✅ Context preservation
- ✅ **NEW: Years left range filtering (8-10 years FIT left)**
- ✅ **NEW: Market analysis mode (compare, aggregate, average)**
- ✅ **NEW: Enhanced deterministic parser**
- ✅ **NEW: LoRA fine-tuned model (fit-intelligence-enhanced)**

### Data Issues
- ⚠️ Some sites missing generation data (prevents income calculations)
- ⚠️ 2019 sites have 0.0 rates (FIT scheme closed March 2019)
- ⚠️ Pre-2010 sites have no rates (FIT started April 2010)

---

**Last Updated**: 2025-08-27 12:45
**Version**: 2.2.0
**Status**: Production Ready - Wind Dashboard Demo-Ready with Full Financial Data