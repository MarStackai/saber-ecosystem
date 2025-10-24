#!/usr/bin/env python3
"""
Ollama-powered FIT Intelligence Chatbot
Uses local open-weight LLMs for complete privacy and no API costs
"""

import os
import json
import requests
from typing import Dict, List, Any
from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI
from fit_id_lookup import FITIDLookup
import re

class OllamaFITChatbot:
    def __init__(self, model: str = "llama3.2"):
        """
        Initialize chatbot with Ollama and local FIT system
        
        Recommended models (all work on RTX 3090 24GB):
        - llama3.2 (3B): Fast, good for basic queries
        - llama3.1:8b: Balanced performance
        - mixtral:8x7b: Most capable but slower
        - mistral:7b: Good balance
        - qwen2.5:14b: Excellent for structured data
        - deepseek-coder-v2: Great for JSON parsing
        """
        self.fit_api = EnhancedFITIntelligenceAPI()
        self.model = model
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Check if Ollama is running
        self.check_ollama()
        
        self.system_prompt = """You are an expert assistant for the UK Feed-in Tariff (FIT) intelligence system.
        You help users find renewable energy sites and analyze FIT data.
        
        Database contains 40,194 commercial renewable energy sites:
        - Technologies: Solar, Wind, Hydro, Anaerobic Digestion
        - Data: Capacity (kW/MW), location, FIT rates, commissioning dates, repowering potential
        
        For user queries, extract and return JSON with these fields:
        {
            "technology": "solar/wind/hydro/anaerobic_digestion/all",
            "min_capacity_kw": number or null,
            "max_capacity_kw": number or null,
            "location": "location string or null",
            "additional_filters": {}
        }
        
        Be precise with location names and capacity values."""

    def check_ollama(self):
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                print(f"✅ Ollama running with models: {models}")
                if self.model not in [m.split(':')[0] for m in models]:
                    print(f"⚠️  Model {self.model} not found. Pulling...")
                    self.pull_model()
            else:
                print("❌ Ollama not responding. Make sure it's running: ollama serve")
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Ollama. Install and run it:")
            print("   curl -fsSL https://ollama.com/install.sh | sh")
            print("   ollama serve")
            exit(1)

    def pull_model(self):
        """Pull model if not available"""
        print(f"📥 Pulling {self.model}... This may take a few minutes...")
        response = requests.post(
            "http://localhost:11434/api/pull",
            json={"name": self.model}
        )
        print(f"✅ Model {self.model} ready!")

    def query_ollama(self, prompt: str, system: str = None) -> str:
        """Query Ollama model"""
        payload = {
            "model": self.model,
            "prompt": f"{system}\n\n{prompt}" if system else prompt,
            "stream": False,
            "format": "json" if "json" in prompt.lower() else None,
            "options": {
                "temperature": 0.3,  # Lower for more consistent parsing
                "top_p": 0.9,
                "max_tokens": 500
            }
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()['response']
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error querying Ollama: {str(e)}"

    def parse_query_with_ollama(self, query: str) -> Dict[str, Any]:
        """Use Ollama to parse natural language query"""
        
        prompt = f"""Parse this renewable energy query into JSON format:

User Query: "{query}"

Extract technology type, capacity requirements, and location.
Return valid JSON only, no explanation.

Example output:
{{"technology": "wind", "min_capacity_kw": 250, "location": "Yorkshire"}}

Your JSON response:"""

        response = self.query_ollama(prompt, self.system_prompt)
        
        try:
            # Extract JSON from response
            if '{' in response and '}' in response:
                json_str = response[response.find('{'):response.rfind('}')+1]
                return json.loads(json_str)
            else:
                # Fallback to basic parsing
                return self.fallback_parse(query)
        except json.JSONDecodeError:
            print(f"⚠️  JSON parse error, using fallback")
            return self.fallback_parse(query)

    def fallback_parse(self, query: str) -> Dict[str, Any]:
        """Simple fallback parser if LLM fails"""
        query_lower = query.lower()
        
        # Detect technology
        tech = "all"
        for t in ["solar", "wind", "hydro", "anaerobic"]:
            if t in query_lower:
                tech = t if t != "anaerobic" else "anaerobic_digestion"
                break
        
        # Detect capacity
        min_capacity = None
        if "over" in query_lower or "above" in query_lower:
            import re
            numbers = re.findall(r'(\d+)\s*(?:kw|mw)', query_lower)
            if numbers:
                min_capacity = int(numbers[0])
                if 'mw' in query_lower:
                    min_capacity *= 1000
        
        # Detect location (basic)
        location = None
        uk_regions = ["scotland", "wales", "yorkshire", "london", "manchester", 
                      "birmingham", "cornwall", "devon", "kent", "essex"]
        for region in uk_regions:
            if region in query_lower:
                location = region.title()
                break
        
        return {
            "technology": tech,
            "min_capacity_kw": min_capacity,
            "max_capacity_kw": None,
            "location": location
        }

    def search_local_database(self, params: Dict[str, Any]) -> List[Dict]:
        """Search local FIT database with parsed parameters"""
        
        # Build search query
        search_parts = []
        
        if params.get('technology') and params['technology'] != 'all':
            search_parts.append(params['technology'])
        
        if params.get('min_capacity_kw'):
            search_parts.append(f"over {params['min_capacity_kw']}kw")
        
        if params.get('location'):
            search_parts.append(f"in {params['location']}")
        
        query = " ".join(search_parts) if search_parts else "renewable energy sites"
        
        # Search using local vector DB
        results = self.fit_api.natural_language_query(
            query=query,
            max_results=10
        )
        
        # Extract commercial results
        return results.get('commercial_results', [])

    def format_response_with_ollama(self, query: str, results: List[Dict]) -> str:
        """Use Ollama to format results nicely"""
        
        if not results:
            return "No sites found matching your criteria. Try broadening your search."
        
        # Prepare concise results summary
        summary = f"Found {len(results)} sites for '{query}':\n\n"
        
        for i, r in enumerate(results[:5], 1):
            metadata = r.get('metadata', {})
            summary += f"{i}. {metadata.get('technology', 'Unknown')} - "
            summary += f"{metadata.get('capacity_kw', 0):,.0f}kW "
            summary += f"in {metadata.get('postcode', 'Unknown')}"
            if metadata.get('repowering_window'):
                summary += f" [{metadata['repowering_window']} repowering]"
            summary += "\n"
        
        # Use Ollama for insights
        prompt = f"""Based on these renewable energy sites, provide 2-3 key insights:

{summary}

Keep insights brief and practical (under 100 words total)."""

        insights = self.query_ollama(prompt)
        
        return summary + "\n📊 Insights:\n" + insights

    def chat(self, query: str) -> str:
        """Process query through Ollama pipeline"""
        
        try:
            # Check if this is a FIT ID/site number query
            fit_id_match = re.search(r'\b(?:fit\s*(?:id)?|site|installation)\s+(\d+)\b', query.lower())
            if fit_id_match:
                fit_id = fit_id_match.group(1)
                lookup = FITIDLookup()
                result = lookup.lookup_fit_id(fit_id)
                
                if result['found']:
                    data = result['data']
                    # Check if asking specifically about rate
                    if 'rate' in query.lower() or 'tariff' in query.lower():
                        response = f"The FIT rate for site {fit_id} is {data['fit_rate']}p/kWh.\n\n"
                    else:
                        response = f"Site {fit_id} details:\n"
                        response += f"FIT Rate: {data['fit_rate']}p/kWh\n"
                    
                    response += f"Technology: {data['technology']}\n"
                    response += f"Capacity: {data['capacity_kw']}kW\n"
                    response += f"Location: {data['location']}\n"
                    response += f"Commission Date: {data['commission_date']}\n"
                    response += f"Status: {data['status']}"
                    return response
                else:
                    return result['message']
            
            # Otherwise use Ollama for regular queries
            # 1. Parse with Ollama
            print(f"🤔 Parsing with {self.model}...")
            parsed = self.parse_query_with_ollama(query)
            print(f"📋 Extracted: {parsed}")
            
            # 2. Search local database
            print("🔍 Searching FIT database...")
            results = self.search_local_database(parsed)
            
            # 3. Format response
            print("✍️  Formatting response...")
            response = self.format_response_with_ollama(query, results)
            
            return response
            
        except Exception as e:
            return f"Error: {str(e)}"

def main():
    """Interactive chatbot interface"""
    
    print("🦙 Ollama-Powered FIT Intelligence Chatbot")
    print("=" * 50)
    print("Using local LLMs - No API keys needed!")
    print("\nAvailable models (install with: ollama pull <model>):")
    print("  - llama3.2 (3B) - Fastest")
    print("  - llama3.1:8b - Balanced") 
    print("  - mixtral:8x7b - Most capable")
    print("  - qwen2.5:14b - Great for data")
    print("\nExample queries:")
    print("  - Large wind farms in Scotland")
    print("  - Solar sites over 500kW in Yorkshire")
    print("  - Sites ready for repowering")
    print("\nType 'exit' to quit\n")
    
    # Let user choose model
    model = input("Model to use (default: llama3.2): ").strip() or "llama3.2"
    
    chatbot = OllamaFITChatbot(model=model)
    
    while True:
        query = input("\n🔍 Your query: ").strip()
        
        if query.lower() in ['exit', 'quit']:
            print("Goodbye! 👋")
            break
        
        if not query:
            continue
        
        print("-" * 50)
        response = chatbot.chat(query)
        print("\n" + response)
        print("-" * 50)

if __name__ == "__main__":
    main()