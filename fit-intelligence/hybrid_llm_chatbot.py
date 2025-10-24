#!/usr/bin/env python3
"""
Hybrid FIT Intelligence Chatbot
Combines local vector search with hosted LLM for enhanced capabilities
"""

import os
import json
from typing import Dict, List, Any
from openai import OpenAI
from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI
from dotenv import load_dotenv

load_dotenv()

class HybridFITChatbot:
    def __init__(self):
        """Initialize hybrid chatbot with local FIT system and OpenAI"""
        self.fit_api = EnhancedFITIntelligenceAPI()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        self.system_prompt = """You are an expert assistant for the UK Feed-in Tariff (FIT) intelligence system.
        You help users find renewable energy sites and analyze FIT data.
        
        You have access to a database with 40,194 commercial renewable energy sites including:
        - Solar, Wind, Hydro, Anaerobic Digestion installations
        - Capacity, location, FIT rates, commissioning dates
        - Repowering potential analysis
        
        Parse user queries to extract:
        1. Technology type (solar/wind/hydro/anaerobic digestion)
        2. Capacity requirements (in kW or MW)
        3. Location (UK regions, counties, cities, postcodes)
        4. Other filters (age, FIT rates, etc.)
        
        Return structured JSON for database queries."""

    def parse_query_with_llm(self, query: str) -> Dict[str, Any]:
        """Use LLM to parse natural language query into structured format"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # or gpt-3.5-turbo for lower cost
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"""Parse this query into a structured search:
                Query: {query}
                
                Return JSON with:
                - technology: solar/wind/hydro/anaerobic_digestion/all
                - min_capacity_kw: number or null
                - max_capacity_kw: number or null  
                - location: string or null
                - additional_context: any other relevant details
                
                Example: {{"technology": "wind", "min_capacity_kw": 250, "location": "Yorkshire"}}"""}
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)

    def search_local_database(self, params: Dict[str, Any]) -> List[Dict]:
        """Search local FIT database with parsed parameters"""
        
        # Build search query for local system
        search_parts = []
        
        if params.get('technology') and params['technology'] != 'all':
            search_parts.append(params['technology'])
        
        if params.get('min_capacity_kw'):
            search_parts.append(f"over {params['min_capacity_kw']}kw")
        elif params.get('max_capacity_kw'):
            search_parts.append(f"under {params['max_capacity_kw']}kw")
        
        if params.get('location'):
            search_parts.append(f"in {params['location']}")
        
        query = " ".join(search_parts) if search_parts else "renewable energy sites"
        
        # Search using local vector DB
        results = self.fit_api.search(
            query=query,
            collection_name="commercial_fit_sites",
            limit=10
        )
        
        return results.get('results', [])

    def format_response_with_llm(self, query: str, results: List[Dict]) -> str:
        """Use LLM to format results into natural language response"""
        
        if not results:
            return "No sites found matching your criteria. Try broadening your search."
        
        # Prepare results summary for LLM
        results_summary = []
        for r in results[:5]:  # Limit to top 5 for context window
            site = {
                'technology': r.get('technology'),
                'capacity_kw': r.get('capacity_kw'),
                'location': r.get('postcode', 'Unknown'),
                'commission_date': r.get('commission_date'),
                'fit_rate': r.get('tariff_p_kwh'),
                'repowering_potential': r.get('repowering_potential')
            }
            results_summary.append(site)
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Format renewable energy site data into a helpful response."},
                {"role": "user", "content": f"""
                User asked: {query}
                
                Found {len(results)} matching sites. Top results:
                {json.dumps(results_summary, indent=2)}
                
                Provide a concise, informative summary highlighting:
                - Number of sites found
                - Key characteristics (capacity ranges, locations)
                - Notable opportunities (repowering potential)
                - Brief insights if relevant
                
                Keep response under 200 words."""}
            ]
        )
        
        return response.choices[0].message.content

    def chat(self, query: str) -> str:
        """Process query through hybrid pipeline"""
        
        try:
            # 1. Parse query with LLM
            print("🤔 Understanding your query...")
            parsed = self.parse_query_with_llm(query)
            print(f"📋 Parsed: {parsed}")
            
            # 2. Search local database
            print("🔍 Searching local FIT database...")
            results = self.search_local_database(parsed)
            print(f"📊 Found {len(results)} sites")
            
            # 3. Format response with LLM
            print("✍️ Generating response...")
            response = self.format_response_with_llm(query, results)
            
            return response
            
        except Exception as e:
            return f"Error processing query: {str(e)}\nMake sure OPENAI_API_KEY is set in .env"

def main():
    """Interactive chatbot interface"""
    
    print("🌟 Hybrid FIT Intelligence Chatbot")
    print("=" * 50)
    print("Combines local FIT database with GPT for natural language understanding")
    print("\nMake sure to set OPENAI_API_KEY in .env file")
    print("\nExample queries:")
    print("- What wind farms in Scotland might need repowering soon?")
    print("- Show me large solar installations in the Southeast")
    print("- Find anaerobic digestion sites with good FIT rates")
    print("\nType 'exit' to quit\n")
    
    chatbot = HybridFITChatbot()
    
    while True:
        query = input("Your query: ").strip()
        
        if query.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye! 👋")
            break
        
        if not query:
            continue
        
        print("\n" + "-" * 50)
        response = chatbot.chat(query)
        print("\n" + response)
        print("-" * 50 + "\n")

if __name__ == "__main__":
    main()