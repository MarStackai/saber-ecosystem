#!/usr/bin/env python3
"""
FIT Intelligence System - Deep Business Intelligence for PPA Opportunities
Combines FIT scheme data with business logic for renewable energy PPAs
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Business Context Constants
class PPAStrategy(Enum):
    """PPA acquisition strategies based on FIT expiry"""
    IMMEDIATE = "IMMEDIATE"  # <2 years - Urgent negotiation needed
    OPTIMAL = "OPTIMAL"      # 2-5 years - Prime acquisition window
    PLANNING = "PLANNING"    # 5-10 years - Relationship building phase
    FUTURE = "FUTURE"        # >10 years - Market monitoring

@dataclass
class PPAOpportunity:
    """Represents a PPA opportunity with full business context"""
    site_id: str
    technology: str
    capacity_mw: float
    location: Dict
    current_fit_rate: float
    fit_expiry: datetime
    annual_revenue: float
    grid_connection: str
    developer_info: Optional[Dict]
    risk_score: float
    opportunity_score: float
    recommended_strategy: str
    
class FITIntelligenceSystem:
    """
    Core intelligence system for FIT scheme analysis
    Provides deep insights for PPA business development
    """
    
    def __init__(self):
        self.solar_data = self._load_solar_data()
        self.wind_data = self._load_wind_data()
        self.market_data = self._load_market_context()
        
    def _load_solar_data(self) -> pd.DataFrame:
        """Load ALL commercial FIT data (solar, wind, hydro, AD, CHP)"""
        try:
            with open('data/all_commercial_fit.json', 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data['sites'])
            logger.info(f"Loaded {len(df):,} commercial FIT sites across all technologies")
            
            # Log technology breakdown
            tech_counts = df['technology'].value_counts()
            for tech, count in tech_counts.items():
                logger.info(f"  {tech}: {count:,} sites")
            
            return df
        except Exception as e:
            logger.error(f"Error loading FIT data: {e}")
            # Fallback to solar-only data if available
            try:
                with open('data/commercial_solar_fit.json', 'r') as f:
                    data = json.load(f)
                df = pd.DataFrame(data['sites'])
                logger.info(f"Fallback: Loaded {len(df):,} commercial solar sites")
                return df
            except:
                return pd.DataFrame()
    
    def _load_wind_data(self) -> pd.DataFrame:
        """Load wind farm data"""
        try:
            with open('data/uk_wind_farms_filtered.json', 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data['features'])
            # Extract properties
            if not df.empty:
                props = pd.json_normalize(df['properties'])
                df = pd.concat([df, props], axis=1)
            logger.info(f"Loaded {len(df):,} wind farms")
            return df
        except Exception as e:
            logger.error(f"Error loading wind data: {e}")
            return pd.DataFrame()
    
    def _load_market_context(self) -> Dict:
        """Load market context for PPA valuation"""
        return {
            'wholesale_price_gbp_mwh': 85,  # Current wholesale electricity price
            'ppa_discount_rate': 0.10,      # Typical PPA discount to wholesale
            'fit_rates': {
                'solar_small': 4.62,         # p/kWh for <10kW
                'solar_medium': 4.21,        # p/kWh for 10-50kW  
                'solar_large': 1.03,         # p/kWh for 50kW-5MW
                'wind_small': 8.53,          # p/kWh for <100kW
                'wind_medium': 4.89,         # p/kWh for 100-500kW
                'wind_large': 1.53,          # p/kWh for 500kW-1.5MW
            },
            'grid_upgrade_costs': {
                'minor': 50000,              # £ for capacity <1MW
                'moderate': 250000,          # £ for capacity 1-5MW
                'major': 1000000,            # £ for capacity >5MW
            },
            'repowering_multipliers': {
                'solar': 1.5,                # Modern panels 50% more efficient
                'wind': 2.5,                 # Modern turbines 150% more efficient
            }
        }
    
    def analyze_ppa_opportunity(self, site: pd.Series, technology: str = None) -> PPAOpportunity:
        """
        Comprehensive PPA opportunity analysis for a single site
        """
        # Calculate FIT expiry and remaining period
        if 'fit_end_date' in site:
            fit_expiry = pd.to_datetime(site['fit_end_date'])
        else:
            # Estimate based on commissioning + 20 years for solar, 15 for wind
            commission_date = pd.to_datetime(site.get('commission_date', '2010-01-01'))
            fit_period = 20 if technology == 'solar' else 15
            fit_expiry = commission_date + timedelta(days=fit_period*365)
        
        remaining_years = (fit_expiry - datetime.now()).days / 365
        
        # Determine strategy based on remaining FIT period
        if remaining_years < 2:
            strategy = PPAStrategy.IMMEDIATE
            urgency_multiplier = 1.5
        elif remaining_years < 5:
            strategy = PPAStrategy.OPTIMAL
            urgency_multiplier = 1.2
        elif remaining_years < 10:
            strategy = PPAStrategy.PLANNING
            urgency_multiplier = 1.0
        else:
            strategy = PPAStrategy.FUTURE
            urgency_multiplier = 0.8
        
        # Get technology from site if not provided
        if technology is None:
            technology = site.get('technology', 'Photovoltaic')
        
        # Calculate current and post-FIT revenues
        capacity_mw = site.get('capacity_mw', 0)
        
        # Capacity factors by technology
        capacity_factors = {
            'Photovoltaic': 0.11,
            'Wind': 0.27,
            'Hydro': 0.38,
            'Anaerobic digestion': 0.80,
            'Micro CHP': 0.50
        }
        capacity_factor = capacity_factors.get(technology, 0.20)
        annual_generation_mwh = capacity_mw * 8760 * capacity_factor
        
        # Current FIT revenue
        fit_rate_p_kwh = self._get_fit_rate(technology, capacity_mw)
        current_annual_revenue = annual_generation_mwh * 1000 * fit_rate_p_kwh / 100
        
        # Post-FIT PPA revenue potential
        wholesale_price = self.market_data['wholesale_price_gbp_mwh']
        ppa_price = wholesale_price * (1 - self.market_data['ppa_discount_rate'])
        ppa_annual_revenue = annual_generation_mwh * ppa_price
        
        # Risk assessment
        risk_factors = []
        risk_score = 0
        
        # Grid risk
        if capacity_mw > 5:
            risk_factors.append("Large capacity may need grid upgrades")
            risk_score += 0.3
        
        # Location risk
        if technology == 'solar' and 'scotland' in str(site.get('region', '')).lower():
            risk_factors.append("Lower solar irradiation in Scotland")
            risk_score += 0.2
        
        # Age risk
        age_years = site.get('age_years', 10)
        if age_years > 15:
            risk_factors.append("Aging equipment may need replacement")
            risk_score += 0.3
        
        # Calculate opportunity score
        revenue_gap = current_annual_revenue - ppa_annual_revenue
        revenue_gap_ratio = revenue_gap / current_annual_revenue if current_annual_revenue > 0 else 1
        
        # Opportunity scoring (0-100)
        opportunity_score = 100 * (
            (0.3 * urgency_multiplier) +  # Urgency factor
            (0.2 * min(capacity_mw / 5, 1)) +  # Size factor (bigger is better up to 5MW)
            (0.2 * (1 - revenue_gap_ratio)) +  # Revenue compatibility
            (0.2 * (1 - risk_score)) +  # Risk factor
            (0.1 * capacity_factor)  # Efficiency factor
        )
        
        # Build recommendation
        if opportunity_score > 80:
            recommendation = "HIGH PRIORITY: Immediate engagement recommended"
        elif opportunity_score > 60:
            recommendation = "MEDIUM PRIORITY: Add to active pipeline"
        elif opportunity_score > 40:
            recommendation = "LOW PRIORITY: Monitor and maintain relationship"
        else:
            recommendation = "WATCH LIST: Track for future opportunities"
        
        return PPAOpportunity(
            site_id=str(site.get('id', 'unknown')),
            technology=technology,
            capacity_mw=capacity_mw,
            location={
                'postcode': site.get('postcode', ''),
                'region': site.get('region', ''),
                'lat': site.get('latitude', 0),
                'lon': site.get('longitude', 0)
            },
            current_fit_rate=fit_rate_p_kwh,
            fit_expiry=fit_expiry,
            annual_revenue=current_annual_revenue,
            grid_connection=site.get('grid_connection', 'Unknown'),
            developer_info=None,  # Would be enriched from external sources
            risk_score=risk_score,
            opportunity_score=opportunity_score,
            recommended_strategy=f"{strategy.value}: {recommendation}"
        )
    
    def _get_fit_rate(self, technology: str, capacity_mw: float) -> float:
        """Get appropriate FIT rate based on technology and size"""
        capacity_kw = capacity_mw * 1000
        rates = self.market_data['fit_rates']
        
        if 'Photovoltaic' in technology or 'solar' in technology.lower():
            if capacity_kw < 10:
                return rates['solar_small']
            elif capacity_kw < 50:
                return rates['solar_medium']
            else:
                return rates['solar_large']
        elif 'Wind' in technology or 'wind' in technology.lower():
            if capacity_kw < 100:
                return rates['wind_small']
            elif capacity_kw < 500:
                return rates['wind_medium']
            else:
                return rates['wind_large']
        elif 'Hydro' in technology:
            # Hydro rates similar to wind
            if capacity_kw < 100:
                return rates['wind_small'] * 0.9
            elif capacity_kw < 500:
                return rates['wind_medium'] * 0.9
            else:
                return rates['wind_large'] * 0.9
        elif 'Anaerobic' in technology:
            # AD has higher rates due to baseload capability
            return rates['wind_large'] * 2.5
        elif 'CHP' in technology:
            # Micro CHP rates
            return rates['solar_medium']
        else:
            # Default rate
            return rates.get('solar_large', 1.0)
    
    def get_portfolio_insights(self) -> Dict:
        """
        Generate comprehensive portfolio-level insights
        """
        insights = {
            'total_opportunities': 0,
            'immediate_action_required': 0,
            'total_capacity_mw': 0,
            'total_annual_generation_gwh': 0,
            'regional_breakdown': {},
            'technology_mix': {},
            'risk_distribution': {},
            'top_opportunities': [],
            'market_timing': {},
            'investment_required': 0,
            'projected_returns': {}
        }
        
        # Analyze entire FIT portfolio (all technologies)
        all_opportunities = []
        for _, site in self.solar_data.iterrows():  # Note: solar_data now contains ALL technologies
            opp = self.analyze_ppa_opportunity(site)
            all_opportunities.append(opp)
        
        # Aggregate insights
        insights['total_opportunities'] = len(all_opportunities)
        insights['immediate_action_required'] = sum(
            1 for o in all_opportunities 
            if 'IMMEDIATE' in o.recommended_strategy
        )
        insights['total_capacity_mw'] = sum(o.capacity_mw for o in all_opportunities)
        
        # Regional distribution
        regional_counts = {}
        for opp in all_opportunities:
            region = opp.location.get('region', 'Unknown')
            if region not in regional_counts:
                regional_counts[region] = {'count': 0, 'capacity_mw': 0}
            regional_counts[region]['count'] += 1
            regional_counts[region]['capacity_mw'] += opp.capacity_mw
        
        insights['regional_breakdown'] = dict(
            sorted(regional_counts.items(), 
                   key=lambda x: x[1]['capacity_mw'], 
                   reverse=True)[:10]
        )
        
        # Top opportunities
        insights['top_opportunities'] = sorted(
            all_opportunities,
            key=lambda x: x.opportunity_score,
            reverse=True
        )[:20]
        
        # Market timing analysis
        expiry_years = {}
        for opp in all_opportunities:
            year = opp.fit_expiry.year
            if year not in expiry_years:
                expiry_years[year] = {'count': 0, 'capacity_mw': 0}
            expiry_years[year]['count'] += 1
            expiry_years[year]['capacity_mw'] += opp.capacity_mw
        
        insights['market_timing'] = dict(sorted(expiry_years.items()))
        
        return insights
    
    def generate_executive_summary(self) -> str:
        """
        Generate executive summary for PPA acquisition strategy
        """
        insights = self.get_portfolio_insights()
        
        summary = f"""
EXECUTIVE SUMMARY: UK FIT SCHEME PPA OPPORTUNITIES
================================================

PORTFOLIO OVERVIEW:
- Total Sites Analyzed: {insights['total_opportunities']:,}
- Total Capacity: {insights['total_capacity_mw']:.1f} MW
- Immediate Action Required: {insights['immediate_action_required']} sites

KEY OPPORTUNITIES:
The FIT scheme expiry presents a significant PPA acquisition opportunity.
Sites losing FIT support need alternative revenue streams, creating favorable
negotiation conditions for long-term PPAs.

REGIONAL FOCUS AREAS:
"""
        for region, data in list(insights['regional_breakdown'].items())[:5]:
            summary += f"- {region}: {data['count']} sites, {data['capacity_mw']:.1f} MW\n"
        
        summary += f"""
TIMING STRATEGY:
Next 24 months: {insights['immediate_action_required']} sites requiring immediate engagement
These sites present the highest urgency and potentially most favorable terms.

RECOMMENDED ACTIONS:
1. Prioritize immediate outreach to sites with <2 years FIT remaining
2. Build relationships with sites in 2-5 year window for optimal positioning
3. Focus on clusters of sites for operational efficiency
4. Consider grid infrastructure in high-concentration areas

VALUE PROPOSITION:
- Provide revenue certainty post-FIT through long-term PPAs
- Offer repowering partnerships to increase site capacity
- Bundle small sites for portfolio economies of scale
"""
        
        return summary

# Business Intelligence Query Interface
class FITQueryEngine:
    """
    Natural language query engine for FIT intelligence
    """
    
    def __init__(self, intelligence_system: FITIntelligenceSystem):
        self.system = intelligence_system
        
    def process_query(self, query: str) -> Dict:
        """
        Process natural language business queries
        """
        query_lower = query.lower()
        
        # Route to appropriate analysis
        if 'urgent' in query_lower or 'immediate' in query_lower:
            return self._get_urgent_opportunities()
        elif 'region' in query_lower or 'location' in query_lower:
            return self._analyze_regional_opportunities(query)
        elif 'risk' in query_lower:
            return self._assess_portfolio_risks()
        elif 'cluster' in query_lower:
            return self._identify_clusters()
        elif 'repower' in query_lower:
            return self._analyze_repowering_potential()
        else:
            return self._general_analysis(query)
    
    def _get_urgent_opportunities(self) -> Dict:
        """Get sites needing immediate attention"""
        df = self.system.solar_data
        urgent = df[df['remaining_fit_years'] < 2]
        
        return {
            'response': f"Found {len(urgent)} sites with FIT expiring within 2 years",
            'data': {
                'total_sites': len(urgent),
                'total_capacity_mw': urgent['capacity_mw'].sum(),
                'regions': urgent['region'].value_counts().to_dict(),
                'average_size_kw': urgent['capacity_kw'].mean()
            },
            'recommendation': "Immediate engagement recommended for these sites"
        }
    
    def _analyze_regional_opportunities(self, query: str) -> Dict:
        """Analyze opportunities by region"""
        # Extract region from query if specified
        regions = ['scotland', 'wales', 'england', 'london', 'manchester', 'birmingham']
        target_region = None
        for region in regions:
            if region in query.lower():
                target_region = region
                break
        
        df = self.system.solar_data
        if target_region:
            df = df[df['region'].str.contains(target_region, case=False, na=False)]
        
        regional_stats = df.groupby('region').agg({
            'capacity_mw': 'sum',
            'capacity_kw': 'count',
            'remaining_fit_years': 'mean'
        }).round(2)
        
        return {
            'response': f"Regional analysis for {target_region or 'all regions'}",
            'data': regional_stats.to_dict(),
            'top_regions': regional_stats.nlargest(5, 'capacity_mw').index.tolist()
        }
    
    def _assess_portfolio_risks(self) -> Dict:
        """Assess portfolio-wide risks"""
        df = self.system.solar_data
        
        risks = {
            'aging_infrastructure': len(df[df['age_years'] > 15]),
            'fit_cliff_edge_2025': len(df[df['remaining_fit_years'].between(0, 2)]),
            'fit_cliff_edge_2027': len(df[df['remaining_fit_years'].between(2, 4)]),
            'small_sites_under_50kw': len(df[df['capacity_kw'] < 50]),
            'large_sites_over_1mw': len(df[df['capacity_kw'] > 1000])
        }
        
        return {
            'response': "Portfolio risk assessment complete",
            'risks': risks,
            'high_risk_sites': risks['fit_cliff_edge_2025'],
            'recommendation': "Focus on de-risking sites with imminent FIT expiry"
        }
    
    def _identify_clusters(self) -> Dict:
        """Identify geographic clusters for efficiency"""
        df = self.system.solar_data
        
        # Group by postcode prefix (first 3-4 chars)
        df['postcode_area'] = df['postcode'].str[:4]
        clusters = df.groupby('postcode_area').agg({
            'capacity_mw': 'sum',
            'capacity_kw': 'count'
        }).rename(columns={'capacity_kw': 'site_count'})
        
        # Find significant clusters (>5 sites or >1MW)
        significant = clusters[(clusters['site_count'] > 5) | (clusters['capacity_mw'] > 1)]
        
        return {
            'response': f"Identified {len(significant)} significant clusters",
            'clusters': significant.nlargest(10, 'capacity_mw').to_dict(),
            'recommendation': "Target these clusters for operational efficiency"
        }
    
    def _analyze_repowering_potential(self) -> Dict:
        """Analyze repowering opportunities"""
        df = self.system.solar_data
        
        # Sites optimal for repowering: 10-20 years old, good location
        repower_candidates = df[
            (df['age_years'].between(10, 20)) & 
            (df['capacity_kw'] > 100)
        ]
        
        current_capacity = repower_candidates['capacity_mw'].sum()
        potential_capacity = current_capacity * self.system.market_data['repowering_multipliers']['solar']
        
        return {
            'response': f"Repowering could increase capacity by {potential_capacity - current_capacity:.1f} MW",
            'data': {
                'candidate_sites': len(repower_candidates),
                'current_capacity_mw': current_capacity,
                'potential_capacity_mw': potential_capacity,
                'capacity_increase_factor': self.system.market_data['repowering_multipliers']['solar']
            },
            'recommendation': "Partner on repowering to secure long-term PPAs"
        }
    
    def _general_analysis(self, query: str) -> Dict:
        """General analysis fallback"""
        insights = self.system.get_portfolio_insights()
        
        return {
            'response': "General portfolio analysis",
            'data': {
                'total_opportunities': insights['total_opportunities'],
                'immediate_actions': insights['immediate_action_required'],
                'total_capacity_mw': insights['total_capacity_mw'],
                'top_regions': list(insights['regional_breakdown'].keys())[:5]
            }
        }

if __name__ == "__main__":
    # Initialize the FIT Intelligence System
    print("Initializing FIT Intelligence System...")
    intelligence = FITIntelligenceSystem()
    query_engine = FITQueryEngine(intelligence)
    
    # Generate executive summary
    print("\n" + "="*60)
    print(intelligence.generate_executive_summary())
    print("="*60)
    
    # Example queries
    example_queries = [
        "What sites need urgent attention?",
        "Show me opportunities in Scotland",
        "What are the portfolio risks?",
        "Where are the best clusters?",
        "What's the repowering potential?"
    ]
    
    print("\nExample Intelligence Queries:")
    print("-"*40)
    for query in example_queries:
        result = query_engine.process_query(query)
        print(f"\nQ: {query}")
        print(f"A: {result['response']}")
        if 'recommendation' in result:
            print(f"   → {result['recommendation']}")