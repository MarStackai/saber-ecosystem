#!/usr/bin/env python3
"""
Ollama-based Query Parser for FIT Intelligence
Replaces regex-based parsing with LLM parsing
"""

import json
import re
import subprocess
import logging

logger = logging.getLogger(__name__)

class OllamaQueryParser:
    """Parse natural language queries using Ollama LLM"""
    
    def __init__(self, model_name="fit-intelligence-v2-1"):
        self.model_name = model_name
        self.available = self._check_ollama()
        
    def _check_ollama(self):
        """Check if Ollama and model are available"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and self.model_name in result.stdout:
                logger.info(f"✅ Ollama model {self.model_name} is available")
                return True
        except:
            pass
        
        logger.warning(f"❌ Ollama model {self.model_name} not available")
        return False
    
    def parse_query(self, query):
        """Parse a natural language query into structured filters"""
        
        if not self.available:
            return None
        
        try:
            # Call Ollama
            result = subprocess.run(
                ["ollama", "run", self.model_name, query],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.error(f"Ollama error: {result.stderr}")
                return None
            
            # Extract JSON from response
            response = result.stdout.strip()
            
            # Clean up ANSI/terminal control characters first
            response = re.sub(r'\x1b\[[0-9;]*[mGKH]', '', response)
            response = re.sub(r'\[\?[0-9]+[hl]', '', response)
            response = re.sub(r'\[[0-9]+[GK]', '', response)
            
            # GPT-OSS includes thinking - extract JSON after "...done thinking."
            if "done thinking" in response:
                response = response.split("done thinking.")[-1].strip()
            
            # Try to find JSON in the response
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response)
            if json_match:
                parsed = json.loads(json_match.group())
                
                # Normalize the structure
                filters = {}
                
                # Handle technology
                if "technology" in parsed:
                    filters["technology"] = parsed["technology"]
                
                # Handle capacity
                if "capacity_min_kw" in parsed:
                    filters["capacity_min"] = parsed["capacity_min_kw"]
                if "capacity_max_kw" in parsed:
                    filters["capacity_max"] = parsed["capacity_max_kw"]
                
                # Handle location/postcodes
                if "postcode_patterns" in parsed:
                    filters["postcode_patterns"] = parsed["postcode_patterns"]
                elif "location" in parsed and "postcode_patterns" in parsed:
                    filters["postcode_patterns"] = parsed["postcode_patterns"]
                
                # Handle FIT ID queries
                if "fit_id" in parsed:
                    filters["fit_id"] = parsed["fit_id"]
                
                # Handle query type
                if "query_type" in parsed:
                    filters["query_type"] = parsed["query_type"]
                
                logger.info(f"Parsed query: {query} -> {filters}")
                return filters
                
        except Exception as e:
            logger.error(f"Error parsing query with Ollama: {e}")
        
        return None


def test_parser():
    """Test the Ollama parser"""
    
    parser = OllamaQueryParser()
    
    test_queries = [
        "wind sites over 100kw in berkshire",
        "solar farms in Yorkshire",
        "what is the fit rate for fit id 1585",
        "hydro installations in Scotland",
        "sites between 50 and 200 kw"
    ]
    
    print("Testing Ollama Query Parser")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = parser.parse_query(query)
        if result:
            print(f"✅ Parsed: {json.dumps(result, indent=2)}")
        else:
            print("❌ Failed to parse")


if __name__ == "__main__":
    test_parser()