#!/usr/bin/env python3
"""
GPT-OSS Powered FIT Intelligence Chatbot
Uses OpenAI's open-weight models via Ollama for powerful local inference
"""

import os
import json
import requests
from typing import Dict, List, Any
from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI

class GPTOSSFITChatbot:
    def __init__(self, model: str = "gpt:oss:20b"):
        """
        Initialize chatbot with GPT-OSS models
        
        Available GPT-OSS models (if released):
        - gpt:oss:20b - Fits well on RTX 3090 (24GB)
        - gpt:oss:120b - Requires quantization or multiple GPUs
        """
        self.fit_api = EnhancedFITIntelligenceAPI()
        self.model = model
        self.ollama_url = "http://localhost:11434/api/generate"
        
        print(f"🚀 Initializing with {model}")
        print("Note: GPT-OSS models would be groundbreaking if available!")
        
        # Check model availability
        self.check_model_availability()
        
        self.system_prompt = """You are an expert assistant for the UK Feed-in Tariff (FIT) intelligence system.
        You have access to a database with 40,194 commercial renewable energy sites.
        
        Parse queries to extract:
        - Technology: solar/wind/hydro/anaerobic_digestion
        - Capacity: min/max in kW
        - Location: UK regions, counties, cities, postcodes
        - Special requirements: repowering potential, FIT rates, age
        
        Always return structured JSON for database queries."""

    def check_model_availability(self):
        """Check if GPT-OSS models are available"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                
                if any('gpt' in m.lower() for m in models):
                    print(f"✅ Found GPT models: {[m for m in models if 'gpt' in m.lower()]}")
                else:
                    print("ℹ️  No GPT models found. Available models:", models[:5] if models else "None")
                    print("\nTo use GPT-OSS models (if available):")
                    print("  ollama pull gpt:oss:20b")
                    print("  ollama pull gpt:oss:120b")
                    print("\nAlternatively, try these excellent open models:")
                    print("  ollama pull llama3.2")
                    print("  ollama pull mixtral:8x7b")
                    
                    # Fallback to available model
                    if models:
                        fallback = models[0]
                        print(f"\n🔄 Falling back to: {fallback}")
                        self.model = fallback
                    
        except requests.exceptions.ConnectionError:
            print("❌ Ollama not running. Install and start it:")
            print("   curl -fsSL https://ollama.com/install.sh | sh")
            print("   ollama serve")
            
            # Continue anyway for demonstration
            print("\n📝 Continuing in demo mode...")

    def query_model(self, prompt: str, system: str = None, json_mode: bool = False) -> str:
        """Query GPT-OSS or fallback model"""
        
        payload = {
            "model": self.model,
            "prompt": f"{system}\n\nUser: {prompt}\n\nAssistant:" if system else prompt,
            "stream": False,
            "format": "json" if json_mode else None,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": 1000,
                # GPT-OSS specific parameters (if supported)
                "num_gpu": -1,  # Use all available GPUs
                "num_thread": 8,
            }
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            if response.status_code == 200:
                return response.json()['response']
            else:
                return self.fallback_response(prompt)
        except:
            return self.fallback_response(prompt)

    def fallback_response(self, prompt: str) -> str:
        """Fallback if model not available"""
        # Use simple pattern matching as fallback
        prompt_lower = prompt.lower()
        
        result = {
            "technology": "all",
            "min_capacity_kw": None,
            "location": None
        }
        
        # Detect technology
        for tech in ["solar", "wind", "hydro", "anaerobic"]:
            if tech in prompt_lower:
                result["technology"] = tech
                break
        
        # Detect capacity
        import re
        capacity_match = re.search(r'(\d+)\s*(kw|mw)', prompt_lower)
        if capacity_match:
            capacity = int(capacity_match.group(1))
            if 'mw' in capacity_match.group(2):
                capacity *= 1000
            result["min_capacity_kw"] = capacity
        
        return json.dumps(result)

    def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse query using GPT-OSS model"""
        
        prompt = f"""Parse this renewable energy query into structured JSON:

Query: "{query}"

Return JSON with these fields:
{{
    "technology": "solar/wind/hydro/anaerobic_digestion/all",
    "min_capacity_kw": number or null,
    "max_capacity_kw": number or null,
    "location": "location string or null",
    "repowering_needed": boolean,
    "fit_rate_important": boolean
}}

Return only valid JSON, no explanation."""

        response = self.query_model(prompt, self.system_prompt, json_mode=True)
        
        try:
            if isinstance(response, str):
                # Extract JSON from response
                if '{' in response:
                    json_str = response[response.find('{'):response.rfind('}')+1]
                    return json.loads(json_str)
            return json.loads(response)
        except:
            # Fallback parsing
            return json.loads(self.fallback_response(query))

    def search_database(self, params: Dict[str, Any]) -> List[Dict]:
        """Search FIT database with parsed parameters"""
        
        # Build search query
        search_parts = []
        
        if params.get('technology') and params['technology'] != 'all':
            search_parts.append(params['technology'])
        
        if params.get('min_capacity_kw'):
            search_parts.append(f"over {params['min_capacity_kw']}kw")
        elif params.get('max_capacity_kw'):
            search_parts.append(f"under {params['max_capacity_kw']}kw")
        
        if params.get('location'):
            search_parts.append(f"in {params['location']}")
        
        if params.get('repowering_needed'):
            search_parts.append("repowering potential")
        
        query = " ".join(search_parts) if search_parts else "renewable energy sites"
        
        results = self.fit_api.search(
            query=query,
            collection_name="commercial_fit_sites",
            limit=15
        )
        
        return results.get('results', [])

    def generate_insights(self, query: str, results: List[Dict]) -> str:
        """Generate insights using GPT-OSS"""
        
        if not results:
            return "No sites found. Try adjusting your search criteria."
        
        # Prepare summary
        summary_data = {
            "total_sites": len(results),
            "total_capacity_mw": sum(r.get('capacity_kw', 0) for r in results) / 1000,
            "technologies": {},
            "locations": {},
            "repowering_opportunities": 0
        }
        
        for r in results:
            tech = r.get('technology', 'Unknown')
            summary_data['technologies'][tech] = summary_data['technologies'].get(tech, 0) + 1
            
            location = r.get('postcode', 'Unknown')[:3]  # Postcode area
            summary_data['locations'][location] = summary_data['locations'].get(location, 0) + 1
            
            if r.get('repowering_potential') in ['High', 'Medium']:
                summary_data['repowering_opportunities'] += 1
        
        prompt = f"""Based on this renewable energy search for "{query}":

Summary:
- Found {summary_data['total_sites']} sites
- Total capacity: {summary_data['total_capacity_mw']:.1f} MW
- Technologies: {summary_data['technologies']}
- Locations: {list(summary_data['locations'].keys())[:5]}
- Repowering opportunities: {summary_data['repowering_opportunities']}

Provide 3 key insights and recommendations. Be specific and actionable.
Keep response under 150 words."""

        insights = self.query_model(prompt, self.system_prompt)
        
        # Format results
        output = f"🔍 Found {len(results)} sites matching '{query}'\n\n"
        
        # Top 5 results
        output += "📊 Top Results:\n"
        for i, r in enumerate(results[:5], 1):
            output += f"{i}. {r.get('technology', 'Unknown')} - "
            output += f"{r.get('capacity_kw', 0):,.0f}kW "
            output += f"({r.get('postcode', 'Unknown')})"
            if r.get('repowering_potential'):
                output += f" [{r['repowering_potential']}]"
            output += "\n"
        
        output += f"\n💡 Insights:\n{insights}"
        
        return output

    def chat(self, query: str) -> str:
        """Process query through GPT-OSS pipeline"""
        
        print(f"\n🔍 Processing: {query}")
        
        try:
            # Parse query
            print(f"🤖 Parsing with {self.model}...")
            parsed = self.parse_query(query)
            print(f"📋 Extracted: {json.dumps(parsed, indent=2)}")
            
            # Search database
            print("💾 Searching FIT database...")
            results = self.search_database(parsed)
            print(f"✅ Found {len(results)} sites")
            
            # Generate response
            print("✍️  Generating insights...")
            response = self.generate_insights(query, results)
            
            return response
            
        except Exception as e:
            return f"Error processing query: {str(e)}"

def main():
    """Interactive GPT-OSS chatbot"""
    
    print("=" * 60)
    print("🤖 GPT-OSS Powered FIT Intelligence System")
    print("=" * 60)
    print("\nIf GPT-OSS models are available through Ollama, this would be")
    print("revolutionary for local AI applications!")
    print("\nChecking for models...")
    
    chatbot = GPTOSSFITChatbot()
    
    print("\n" + "=" * 60)
    print("Example queries:")
    print("  • Wind farms in Scotland needing repowering")
    print("  • Large solar installations with good FIT rates")
    print("  • Sites over 1MW in Yorkshire")
    print("  • Best renewable opportunities in Wales")
    print("\nType 'exit' to quit")
    print("=" * 60)
    
    while True:
        query = input("\n🔍 Query: ").strip()
        
        if query.lower() in ['exit', 'quit', 'bye']:
            print("\nGoodbye! 👋")
            break
        
        if not query:
            continue
        
        response = chatbot.chat(query)
        print("\n" + response)
        print("-" * 60)

if __name__ == "__main__":
    main()