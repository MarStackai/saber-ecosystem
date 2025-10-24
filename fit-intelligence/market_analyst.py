#!/usr/bin/env python3
"""
Market analysis capabilities for FIT Intelligence Platform
Handles comparative, aggregative, and analytical queries
"""

import logging
from typing import Dict, List, Any
from collections import defaultdict
from financial_calculator import render_result_summary

logger = logging.getLogger(__name__)

class MarketAnalyst:
    """Provides market analysis and comparative insights"""
    
    def __init__(self, warm_index):
        self.warm_index = warm_index
    
    def analyze_comparative(self, query: str, params: Dict) -> Dict:
        """Handle comparative analysis queries (e.g., wind vs solar)"""
        
        # Detect comparative intent
        if 'compar' in query.lower() or ' vs ' in query.lower() or ' versus ' in query.lower():
            return self._compare_technologies(params)
        elif 'total' in query.lower() or 'sum' in query.lower() or 'aggregate' in query.lower():
            return self._aggregate_analysis(params)
        elif 'average' in query.lower() or 'mean' in query.lower():
            return self._average_analysis(params)
        else:
            return None
    
    def _compare_technologies(self, params: Dict) -> Dict:
        """Compare different technologies in a region"""
        
        # Get location from params
        areas = params.get('postcode_areas', [])
        
        # Fetch ALL sites for each technology (not just 10)
        technologies = ['wind', 'photovoltaic', 'hydro', 'anaerobic digestion']
        comparison = {}
        
        for tech in technologies:
            # Search for this technology
            results = self.warm_index.search(
                f"{tech} installations",
                areas=areas,
                technology=tech,
                top_k=5000  # Get all sites, not just 10
            )
            
            if results:
                # Calculate aggregates
                total_capacity = 0
                total_sites = len(results)
                total_annual_income = 0
                
                for score, id, metadata in results:
                    rendered = render_result_summary(metadata)
                    capacity = metadata.get('capacity_kw', 0)
                    if capacity:
                        total_capacity += float(capacity)
                    income = rendered.get('annual_income_gbp', 0)
                    if income:
                        total_annual_income += income
                
                comparison[tech] = {
                    'total_sites': total_sites,
                    'total_capacity_mw': round(total_capacity / 1000, 2),
                    'average_capacity_kw': round(total_capacity / total_sites, 1) if total_sites > 0 else 0,
                    'total_annual_income_gbp': round(total_annual_income, 2),
                    'average_income_per_site': round(total_annual_income / total_sites, 2) if total_sites > 0 else 0
                }
        
        return {
            'type': 'technology_comparison',
            'location': areas if areas else 'All UK',
            'data': comparison
        }
    
    def _aggregate_analysis(self, params: Dict) -> Dict:
        """Provide aggregate statistics for a search"""
        
        # Get all matching sites
        technology = params.get('technology')
        areas = params.get('postcode_areas', [])
        min_kw = params.get('min_capacity_kw')
        max_kw = params.get('max_capacity_kw')
        
        results = self.warm_index.search(
            f"{technology or 'renewable'} installations",
            areas=areas,
            technology=technology,
            min_kw=min_kw,
            max_kw=max_kw,
            top_k=5000  # Get all matching sites
        )
        
        # Calculate comprehensive statistics
        stats = {
            'total_sites': len(results),
            'total_capacity_mw': 0,
            'total_annual_income_gbp': 0,
            'total_remaining_value_gbp': 0,
            'capacity_ranges': defaultdict(int),
            'commissioning_years': defaultdict(int),
            'repowering_windows': defaultdict(int),
            'tariff_ranges': defaultdict(list)
        }
        
        for score, id, metadata in results:
            rendered = render_result_summary(metadata)
            
            # Capacity
            capacity = metadata.get('capacity_kw', 0)
            if capacity:
                capacity = float(capacity)
                stats['total_capacity_mw'] += capacity / 1000
                
                # Categorize by size
                if capacity < 50:
                    stats['capacity_ranges']['<50kW'] += 1
                elif capacity < 250:
                    stats['capacity_ranges']['50-250kW'] += 1
                elif capacity < 1000:
                    stats['capacity_ranges']['250kW-1MW'] += 1
                else:
                    stats['capacity_ranges']['>1MW'] += 1
            
            # Financial
            income = rendered.get('annual_income_gbp', 0)
            if income:
                stats['total_annual_income_gbp'] += income
            
            remaining = rendered.get('total_remaining_value', 0)
            if remaining:
                stats['total_remaining_value_gbp'] += remaining
            
            # Commissioning year
            comm_date = metadata.get('commission_date', '')
            if comm_date:
                year = comm_date[:4]
                stats['commissioning_years'][year] += 1
            
            # Repowering window
            window = rendered.get('repowering_window', 'UNKNOWN')
            stats['repowering_windows'][window] += 1
            
            # Tariff rates
            tariff = rendered.get('tariff_p_kwh')
            if tariff:
                stats['tariff_ranges']['all'].append(tariff)
        
        # Calculate tariff statistics
        if stats['tariff_ranges']['all']:
            tariffs = stats['tariff_ranges']['all']
            stats['tariff_stats'] = {
                'min_p_kwh': min(tariffs),
                'max_p_kwh': max(tariffs),
                'avg_p_kwh': round(sum(tariffs) / len(tariffs), 2)
            }
            del stats['tariff_ranges']['all']  # Remove raw list
        
        # Round financial totals
        stats['total_capacity_mw'] = round(stats['total_capacity_mw'], 2)
        stats['total_annual_income_gbp'] = round(stats['total_annual_income_gbp'], 2)
        stats['total_remaining_value_gbp'] = round(stats['total_remaining_value_gbp'], 2)
        
        return {
            'type': 'aggregate_analysis',
            'query_params': params,
            'statistics': stats
        }
    
    def _average_analysis(self, params: Dict) -> Dict:
        """Calculate averages for the search results"""
        
        # Get aggregate data first
        agg = self._aggregate_analysis(params)
        stats = agg['statistics']
        
        if stats['total_sites'] == 0:
            return {
                'type': 'average_analysis',
                'message': 'No sites found matching criteria'
            }
        
        total = stats['total_sites']
        
        averages = {
            'average_capacity_kw': round(stats['total_capacity_mw'] * 1000 / total, 1),
            'average_annual_income_gbp': round(stats['total_annual_income_gbp'] / total, 2),
            'average_remaining_value_gbp': round(stats['total_remaining_value_gbp'] / total, 2) if stats['total_remaining_value_gbp'] > 0 else None,
            'average_tariff_p_kwh': stats.get('tariff_stats', {}).get('avg_p_kwh'),
            'total_sites_analyzed': total
        }
        
        return {
            'type': 'average_analysis',
            'query_params': params,
            'averages': averages,
            'capacity_distribution': dict(stats['capacity_ranges']),
            'repowering_distribution': dict(stats['repowering_windows'])
        }
    
    def format_analysis_response(self, analysis: Dict) -> str:
        """Format analysis results for display"""
        
        if not analysis:
            return None
        
        analysis_type = analysis.get('type')
        
        if analysis_type == 'technology_comparison':
            response = "Technology Comparison Analysis\n"
            response += "=" * 50 + "\n\n"
            
            location = analysis.get('location')
            if location and location != 'All UK':
                response += f"Location: Postcode areas {', '.join(location[:5])}\n\n"
            
            data = analysis.get('data', {})
            
            # Sort by total capacity
            sorted_techs = sorted(data.items(), key=lambda x: x[1]['total_capacity_mw'], reverse=True)
            
            for tech, stats in sorted_techs:
                if stats['total_sites'] > 0:
                    response += f"{tech.title()}:\n"
                    response += f"  • Total sites: {stats['total_sites']:,}\n"
                    response += f"  • Total capacity: {stats['total_capacity_mw']:,.1f} MW\n"
                    response += f"  • Average site size: {stats['average_capacity_kw']:,.1f} kW\n"
                    response += f"  • Total annual income: £{stats['total_annual_income_gbp']:,.0f}\n"
                    response += f"  • Average income per site: £{stats['average_income_per_site']:,.0f}\n\n"
            
            # Summary comparison
            if len([t for t in data.values() if t['total_sites'] > 0]) > 1:
                response += "Summary:\n"
                total_capacity = sum(t['total_capacity_mw'] for t in data.values())
                total_sites = sum(t['total_sites'] for t in data.values())
                total_income = sum(t['total_annual_income_gbp'] for t in data.values())
                
                response += f"  • Combined capacity: {total_capacity:,.1f} MW across {total_sites:,} sites\n"
                response += f"  • Combined annual income: £{total_income:,.0f}\n"
            
            return response
        
        elif analysis_type == 'aggregate_analysis':
            stats = analysis.get('statistics', {})
            response = "Aggregate Analysis\n"
            response += "=" * 50 + "\n\n"
            
            response += f"Total sites: {stats['total_sites']:,}\n"
            response += f"Total capacity: {stats['total_capacity_mw']:,.2f} MW\n"
            response += f"Total annual income: £{stats['total_annual_income_gbp']:,.0f}\n"
            
            if stats['total_remaining_value_gbp'] > 0:
                response += f"Total remaining FIT value: £{stats['total_remaining_value_gbp']:,.0f}\n"
            
            # Capacity distribution
            if stats['capacity_ranges']:
                response += "\nCapacity Distribution:\n"
                for range_name, count in sorted(stats['capacity_ranges'].items()):
                    response += f"  • {range_name}: {count} sites\n"
            
            # Repowering windows
            if stats['repowering_windows']:
                response += "\nRepowering Windows:\n"
                for window, count in sorted(stats['repowering_windows'].items()):
                    response += f"  • {window}: {count} sites\n"
            
            return response
        
        elif analysis_type == 'average_analysis':
            avgs = analysis.get('averages', {})
            response = "Average Analysis\n"
            response += "=" * 50 + "\n\n"
            
            response += f"Sites analyzed: {avgs['total_sites_analyzed']:,}\n"
            response += f"Average capacity: {avgs['average_capacity_kw']:,.1f} kW\n"
            response += f"Average annual income: £{avgs['average_annual_income_gbp']:,.0f}\n"
            
            if avgs.get('average_remaining_value_gbp'):
                response += f"Average remaining value: £{avgs['average_remaining_value_gbp']:,.0f}\n"
            
            if avgs.get('average_tariff_p_kwh'):
                response += f"Average tariff: {avgs['average_tariff_p_kwh']:.2f}p/kWh\n"
            
            return response
        
        return None