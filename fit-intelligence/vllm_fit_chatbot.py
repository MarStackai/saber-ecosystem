#!/usr/bin/env python3
"""
FIT Intelligence Chatbot using vLLM GPU inference
Replaces Ollama with GPU-accelerated vLLM
"""

import json
import requests
import logging
from typing import Dict, Any, List, Optional
from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI
from session_manager import SessionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VLLMFITChatbot:
    """
    Hybrid chatbot using vLLM for LLM inference and ChromaDB for factual data
    """
    
    def __init__(self, vllm_url: str = "http://localhost:8000"):
        """Initialize with vLLM server URL"""
        self.fit_api = EnhancedFITIntelligenceAPI()
        self.session_manager = SessionManager()
        self.vllm_url = vllm_url
        
        # Check vLLM server
        try:
            response = requests.get(f"{vllm_url}/health")
            if response.status_code == 200:
                logger.info(f"✓ vLLM server running at {vllm_url}")
            else:
                logger.warning(f"vLLM server not responding at {vllm_url}")
        except:
            logger.error(f"Cannot connect to vLLM server at {vllm_url}")
    
    def understand_query_with_llm(self, query: str, session_id: str = None) -> Dict:
        """Use vLLM to understand the user query"""
        
        # Get context from session if available
        context = ""
        if session_id:
            last_results = self.session_manager.get_last_results(session_id)
            if last_results:
                context = f"\nPrevious query context: Found {len(last_results)} results\n"
        
        prompt = f"""You are analyzing a query about UK renewable energy FIT (Feed-in Tariff) installations.
{context}
Extract the following information from this query and return ONLY valid JSON:

Query: "{query}"

Return JSON with these fields:
{{
  "is_followup": false,  // true if referencing previous results
  "intent": "search_new",  // or "get_details", "filter_results"
  "search_params": {{
    "technology": null,  // "wind", "solar", "hydro", or null
    "min_capacity_kw": null,  // number or null
    "max_capacity_kw": null,  // number or null  
    "location": null,  // location string or null
    "fit_id": null  // specific FIT ID or null
  }}
}}

JSON:"""
        
        try:
            # Call vLLM API
            response = requests.post(
                f"{self.vllm_url}/v1/completions",
                json={
                    "prompt": prompt,
                    "max_tokens": 256,
                    "temperature": 0.1,
                    "stop": ["\n\n", "```"]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                llm_output = result['choices'][0]['text'].strip()
                
                # Parse JSON from LLM response
                try:
                    # Clean up the response
                    if llm_output.startswith("```json"):
                        llm_output = llm_output[7:]
                    if llm_output.endswith("```"):
                        llm_output = llm_output[:-3]
                    
                    understanding = json.loads(llm_output)
                    logger.info(f"vLLM Understanding: {understanding}")
                    return understanding
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parse error: {e}")
                    logger.warning(f"LLM output: {llm_output}")
                    
            else:
                logger.error(f"vLLM error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"vLLM request failed: {e}")
        
        # Fallback to rule-based parsing
        return self.fallback_understanding(query)
    
    def fallback_understanding(self, query: str) -> Dict:
        """Fallback rule-based understanding"""
        query_lower = query.lower()
        
        understanding = {
            "is_followup": False,
            "intent": "search_new",
            "search_params": {}
        }
        
        # Check for follow-up patterns
        if any(phrase in query_lower for phrase in [
            "more details", "tell me more", "what are their", 
            "give me all", "show me the", "list them"
        ]):
            understanding["is_followup"] = True
            understanding["intent"] = "get_details"
        
        # Extract technology
        if "wind" in query_lower:
            understanding["search_params"]["technology"] = "wind"
        elif "solar" in query_lower:
            understanding["search_params"]["technology"] = "solar"
        elif "hydro" in query_lower:
            understanding["search_params"]["technology"] = "hydro"
        
        # Extract capacity
        import re
        capacity_match = re.search(r'(\d+)\s*(?:kw|mw)', query_lower)
        if capacity_match:
            capacity = int(capacity_match.group(1))
            if "mw" in capacity_match.group(0):
                capacity *= 1000
            
            if "over" in query_lower or "above" in query_lower or ">" in query_lower:
                understanding["search_params"]["min_capacity_kw"] = capacity
            elif "under" in query_lower or "below" in query_lower or "<" in query_lower:
                understanding["search_params"]["max_capacity_kw"] = capacity
        
        # Extract location
        locations = ["aberdeen", "edinburgh", "glasgow", "london", "manchester", "yorkshire"]
        for location in locations:
            if location in query_lower:
                understanding["search_params"]["location"] = location
                break
        
        return understanding
    
    def generate_llm_response(self, results: List[Dict], query: str) -> str:
        """Generate natural language response using vLLM"""
        
        if not results:
            return "I couldn't find any installations matching your criteria."
        
        # Prepare context for LLM
        results_summary = f"Found {len(results)} installations:\n"
        for i, r in enumerate(results[:5]):  # Show first 5
            results_summary += f"- {r.get('site_name', 'Unknown')}: "
            results_summary += f"{r.get('installed_capacity_kw', 0)}kW {r.get('technology', '')}"
            results_summary += f" (FIT ID: {r.get('fit_id', 'N/A')})\n"
        
        prompt = f"""Based on this UK renewable energy data, provide a helpful response:

Query: {query}

Data:
{results_summary}

Provide a brief, informative response that includes FIT IDs:"""
        
        try:
            response = requests.post(
                f"{self.vllm_url}/v1/completions",
                json={
                    "prompt": prompt,
                    "max_tokens": 256,
                    "temperature": 0.3,
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['text'].strip()
                
        except Exception as e:
            logger.error(f"vLLM generation failed: {e}")
        
        # Fallback response
        return self.format_results_fallback(results, query)
    
    def format_results_fallback(self, results: List[Dict], query: str) -> str:
        """Fallback formatting without LLM"""
        if not results:
            return "No installations found matching your criteria."
        
        response = f"Found {len(results)} installations:\n\n"
        
        for i, r in enumerate(results[:10], 1):
            response += f"{i}. {r.get('site_name', 'Unknown Site')}\n"
            response += f"   • Technology: {r.get('technology', 'Unknown')}\n"
            response += f"   • Capacity: {r.get('installed_capacity_kw', 0):,} kW\n"
            response += f"   • Location: {r.get('postcode', 'Unknown')}\n"
            response += f"   • FIT ID: {r.get('fit_id', 'N/A')}\n"
            response += f"   • Commissioned: {r.get('commissioned_date', 'Unknown')}\n\n"
        
        if len(results) > 10:
            response += f"... and {len(results) - 10} more installations."
        
        return response
    
    def process_query(self, query: str, session_id: str = None) -> Dict[str, Any]:
        """Main entry point for processing queries"""
        
        # Understand the query using vLLM
        understanding = self.understand_query_with_llm(query, session_id)
        
        # Handle follow-up queries
        if understanding.get("is_followup") and session_id:
            last_results = self.session_manager.get_last_results(session_id)
            if last_results:
                response = self.generate_llm_response(last_results, query)
                return {
                    "response": response,
                    "results": last_results,
                    "understanding": understanding
                }
        
        # Perform new search
        if understanding.get("search_params"):
            logger.info(f"Searching with params: {understanding['search_params']}")
            results = self.fit_api.advanced_search(**understanding["search_params"])
            
            # Store in session
            if session_id:
                self.session_manager.store_results(session_id, query, results)
            
            # Generate response
            response = self.generate_llm_response(results, query)
            
            return {
                "response": response,
                "results": results,
                "result_count": len(results),
                "understanding": understanding
            }
        
        return {
            "response": "I couldn't understand your query. Please try rephrasing.",
            "results": [],
            "understanding": understanding
        }

if __name__ == "__main__":
    # Test the vLLM chatbot
    chatbot = VLLMFITChatbot()
    
    test_queries = [
        "wind farms over 500kw in Aberdeen",
        "give me all the details",
        "solar installations in Yorkshire between 150kw and 500kw"
    ]
    
    session_id = "test_vllm_session"
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        result = chatbot.process_query(query, session_id)
        print(f"Response: {result['response']}")
        print(f"Found: {result.get('result_count', 0)} results")
        print(f"Understanding: {result.get('understanding')}")
        print("-" * 50)