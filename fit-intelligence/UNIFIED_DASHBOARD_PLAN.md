# Unified FIT Intelligence Dashboard - Architecture Plan

## 🎯 Vision Statement

Create a seamless, NLP-driven geographic intelligence platform where users can explore UK renewable energy assets through natural language queries that instantly translate into interactive map visualizations with intelligent clustering and rich data insights.

## 🏗️ Core Architecture

### 1. NLP Chat-to-Map Pipeline

```
User Query → NLP Processing → Query Enhancement → Data Retrieval → 
Geographic Clustering → Map Rendering → Interactive Tooltips
```

#### 1.1 Query Flow Architecture
```python
# Proposed pipeline structure
class UnifiedQueryPipeline:
    """
    Integrates NLP chat with real-time map visualization
    """
    
    components = {
        'query_parser': 'Enhanced NLP with LoRA fine-tuning',
        'query_optimizer': 'Existing fit_query_optimizer.py',
        'data_retrieval': 'Warm index + ChromaDB',
        'geo_processor': 'New clustering engine',
        'map_renderer': 'Leaflet.js with custom plugins',
        'websocket_bridge': 'Real-time bidirectional updates'
    }
    
    flow = """
    1. User types query in chat window
    2. NLP parses intent + extracts filters
    3. Query optimizer enhances with synonyms/variations
    4. Warm index pre-filters by geography
    5. ChromaDB retrieves detailed results
    6. Clustering engine groups by location/characteristics
    7. Map updates with animated transitions
    8. Tooltips populate with enriched data
    """
```

### 2. Component Integration Strategy

#### 2.1 Frontend Architecture
- **Single Page Application (SPA)**
  - React/Vue.js framework for component management
  - Split-pane layout: Chat (left) | Map (right)
  - Synchronized state management (Redux/Vuex)
  - WebSocket for real-time updates

#### 2.2 Backend Services
- **API Gateway** (fit_api_server.py enhancement)
  - REST endpoints for initial load
  - WebSocket for live updates
  - Session management for context preservation
  
- **Processing Pipeline**
  - Async queue for heavy computations
  - Redis cache for frequently accessed clusters
  - Background workers for financial calculations

## 📍 Geographic Clustering Strategy

### 1. Multi-Level Clustering

```python
# Proposed clustering hierarchy
CLUSTERING_LEVELS = {
    'zoom_0-5': {  # Country level
        'method': 'region_aggregation',
        'display': 'bubble_markers',
        'data': ['total_capacity', 'site_count', 'avg_remaining_years']
    },
    'zoom_6-8': {  # County level
        'method': 'county_boundaries',
        'display': 'heat_map_overlay',
        'data': ['capacity_density', 'technology_mix', 'repowering_urgency']
    },
    'zoom_9-12': {  # City/Town level
        'method': 'k_means_clustering',
        'display': 'cluster_circles',
        'data': ['detailed_stats', 'top_opportunities', 'financial_summary']
    },
    'zoom_13+': {  # Individual sites
        'method': 'individual_markers',
        'display': 'custom_icons_by_tech',
        'data': ['full_site_details', 'financial_projections', 'contact_info']
    }
}
```

### 2. Smart Clustering Algorithm

```python
# Intelligent grouping based on multiple factors
class SmartClusterer:
    """
    Groups sites by proximity AND business logic
    """
    
    clustering_factors = {
        'geographic_proximity': 0.4,  # Weight: 40%
        'technology_type': 0.2,       # Weight: 20%
        'capacity_range': 0.15,       # Weight: 15%
        'repowering_window': 0.15,    # Weight: 15%
        'ownership_pattern': 0.1      # Weight: 10%
    }
    
    special_clusters = {
        'portfolio_view': 'Group by owner/operator',
        'urgent_opportunities': 'Sites needing immediate action',
        'high_value_targets': 'Top 10% by remaining FIT value',
        'technology_parks': 'Multi-tech renewable hubs'
    }
```

### 3. Dynamic Cluster Updates

- **Real-time reclustering** based on zoom level
- **Smooth transitions** between cluster levels
- **Cluster splitting/merging** animations
- **Progressive data loading** for performance

## 💬 NLP Chat Enhancement

### 1. Query Understanding Improvements

```python
# Enhanced query patterns to support
QUERY_PATTERNS = {
    'geographic_filters': [
        "show me {tech} in {location}",
        "map all {capacity_range} sites near {city}",
        "cluster {tech} farms within {distance} of {location}"
    ],
    'complex_filters': [
        "urgent repowering opportunities in {region} over {capacity}",
        "sites expiring between {date1} and {date2} with {tech}",
        "profitable buyout targets with {years} remaining"
    ],
    'aggregations': [
        "total capacity by county in {region}",
        "average remaining value for {tech} in {location}",
        "technology distribution across {area}"
    ],
    'comparisons': [
        "compare wind vs solar in {location}",
        "contrast {region1} with {region2} for {tech}",
        "benchmark {site} against regional average"
    ]
}
```

### 2. LoRA Training Dataset Structure

```python
# Training data format for improved NLP
TRAINING_SCHEMA = {
    'input_variations': {
        'capacity_ranges': [
            "over 50kw", "50kw to 350kw", "between 50 and 350 kilowatts",
            "minimum 50kw maximum 350kw", ">50kW <350kW"
        ],
        'location_formats': [
            "in Surrey", "Surrey area", "Surrey county", "near Guildford",
            "KT postcodes", "Surrey and surrounding areas"
        ],
        'technology_aliases': [
            "solar/Solar PV/photovoltaic/PV panels",
            "wind/wind turbines/wind farms/onshore wind",
            "hydro/hydroelectric/water power"
        ]
    },
    'output_structure': {
        'intent': 'search/filter/aggregate/compare',
        'entities': {
            'technology': 'normalized_name',
            'location': 'postcode_areas[]',
            'capacity_min': 'kilowatts',
            'capacity_max': 'kilowatts',
            'repowering_category': 'immediate/urgent/optimal',
            'time_range': 'years_remaining'
        }
    }
}
```

## 🎨 Enhanced Tooltip/Panel Design

### 1. Progressive Information Disclosure

```javascript
// Tooltip information hierarchy
const TOOLTIP_LEVELS = {
    hover: {  // Quick hover - 100ms delay
        fields: ['name', 'technology', 'capacity', 'years_remaining'],
        format: 'compact_card',
        size: 'small'
    },
    click: {  // Click on marker/cluster
        fields: [
            'fit_id', 'full_address', 'postcode',
            'commission_date', 'expiry_date',
            'fit_rate', 'annual_generation',
            'standard_income', 'regional_income',
            'total_remaining_value', 'degradation_adjusted_value'
        ],
        format: 'detailed_panel',
        size: 'medium'
    },
    details: {  // "More details" button
        fields: [
            '...all_above',
            'monthly_projections', 'buyout_valuation',
            'repowering_recommendations', 'contact_details',
            'historical_performance', 'grid_connection_info'
        ],
        format: 'full_sidebar',
        size: 'large'
    }
};
```

### 2. Visual Data Presentation

```css
/* Enhanced tooltip styling */
.tooltip-enhanced {
    /* Status indicators */
    .repowering-status {
        immediate: red_pulse_animation;
        urgent: orange_highlight;
        optimal: green_checkmark;
    }
    
    /* Financial metrics */
    .financial-data {
        display: dual_column;
        left: standard_rates;
        right: regional_adjusted;
        highlight: total_remaining_value;
    }
    
    /* Technology icons */
    .tech-icon {
        solar: sun_icon_with_degradation_indicator;
        wind: turbine_with_capacity_factor;
        hydro: water_drop_with_flow_rate;
    }
}
```

## 🔄 Filter Synchronization

### 1. Bidirectional Filter Updates

```javascript
// Chat query ↔ Map filters synchronization
class FilterSync {
    constructor() {
        this.chatFilters = {};
        this.mapFilters = {};
        this.activeFilters = {};
    }
    
    onChatQuery(query) {
        // Parse query into filters
        this.chatFilters = NLPParser.extract(query);
        // Update map
        this.syncToMap();
        // Update filter UI
        this.updateFilterPanel();
    }
    
    onMapInteraction(event) {
        // User draws region or clicks filters
        this.mapFilters = MapHandler.getFilters(event);
        // Generate natural language summary
        this.syncToChat();
        // Update results
        this.refreshData();
    }
    
    syncToMap() {
        // Animate map to show filtered region
        // Update marker visibility
        // Refresh clusters
    }
    
    syncToChat() {
        // Generate: "Showing 47 solar sites in Surrey over 100kW"
        // Update chat context for follow-up queries
    }
}
```

### 2. Filter UI Components

```
┌─────────────────────────────────────────┐
│  Active Filters (click to remove)       │
├─────────────────────────────────────────┤
│ [✕ Technology: Solar] [✕ County: Surrey]│
│ [✕ Capacity: >250kW] [✕ Status: Optimal]│
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Quick Filters                          │
├─────────────────────────────────────────┤
│ Technology: [All][Solar][Wind][Hydro]   │
│ Repowering: [All][Immediate][Urgent]    │
│ Capacity:   [<50][50-250][250-500][>500]│
│ Region:     [Dropdown with counties]     │
└─────────────────────────────────────────┘
```

## 📊 Performance Optimizations

### 1. Caching Strategy

```python
CACHE_LAYERS = {
    'browser': {
        'cluster_data': '5_minutes',
        'map_tiles': '1_hour',
        'tooltip_data': '10_minutes'
    },
    'redis': {
        'search_results': '15_minutes',
        'financial_calculations': '1_hour',
        'aggregations': '30_minutes'
    },
    'warm_index': {
        'full_reload': 'daily',
        'incremental_updates': 'hourly'
    }
}
```

### 2. Progressive Loading

- Initial load: Top 100 results + clusters
- Zoom in: Load additional detail for visible area
- Background: Preload adjacent regions
- Lazy load: Financial calculations on-demand

## 🚀 Implementation Phases

### Phase 1: Foundation (Week 1-2)
- WebSocket infrastructure
- Basic chat-to-map connection
- Simple clustering (by postcode area)
- Enhanced tooltip with existing data

### Phase 2: Intelligence (Week 3-4)
- LoRA training for NLP improvement
- Smart clustering algorithm
- Regional financial calculations in tooltips
- Filter synchronization

### Phase 3: Polish (Week 5-6)
- Animations and transitions
- Advanced clustering strategies
- Performance optimizations
- Comprehensive testing

### Phase 4: Advanced Features (Week 7-8)
- Portfolio grouping
- Comparison tools
- Export functionality
- Admin dashboard

## 🧪 Testing Strategy

### 1. User Journey Tests
```
1. "Show me urgent wind sites in Scotland"
   → Map zooms to Scotland
   → Orange markers for urgent sites
   → Cluster shows "23 sites, 2-5 years remaining"

2. "Filter to over 500kW only"
   → Map updates, smaller sites fade out
   → Clusters recalculate
   → Chat shows "Filtered to 8 sites over 500kW"

3. Click on cluster
   → Cluster expands to show individual sites
   → Tooltip shows aggregated stats
   → Financial summary panel slides in

4. "Compare with Wales"
   → Split screen comparison view
   → Side-by-side statistics
   → Highlighting differences
```

### 2. Performance Benchmarks
- Initial load: < 2 seconds
- Query to map update: < 500ms
- Cluster recalculation: < 200ms
- Tooltip display: < 100ms

## 📋 Technical Requirements

### Frontend
- Leaflet.js 1.9+ with plugins:
  - Leaflet.markercluster
  - Leaflet.heat
  - Leaflet.draw
- React 18+ or Vue 3+
- WebSocket client (Socket.io)
- D3.js for custom visualizations

### Backend
- Enhanced Flask with WebSocket support
- Redis for caching and pub/sub
- PostgreSQL for user sessions
- Celery for background tasks

### DevOps
- Docker containerization
- Nginx reverse proxy
- PM2 process management
- Monitoring with Grafana

## 🎯 Success Metrics

1. **User Engagement**
   - 80% queries result in map interaction
   - Average session duration > 10 minutes
   - 50% users apply multiple filters

2. **Performance**
   - 95% queries complete < 2 seconds
   - Zero perceived lag on map interactions
   - Smooth 60fps animations

3. **Data Quality**
   - 100% accurate geographic mapping
   - Zero hallucinated results
   - Correct financial calculations

## 🔄 Future Enhancements

1. **Mobile App** with offline capabilities
2. **AR View** for field visits
3. **Predictive Analytics** for market trends
4. **Integration APIs** for third-party platforms
5. **Machine Learning** for opportunity scoring
6. **Blockchain** for transaction tracking

---

**Document Status**: Planning Phase
**Next Steps**: Review with stakeholders, refine requirements, begin Phase 1 implementation
**Estimated Timeline**: 8 weeks for full implementation
**Estimated Resources**: 2 frontend developers, 1 backend developer, 1 ML engineer, 1 designer