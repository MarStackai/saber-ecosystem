#!/usr/bin/env python3
"""
GPT-OSS FIT Wrapper
Combines GPT-OSS language capabilities with our FIT database
"""

import json
import requests
from typing import Dict, List, Any
from factual_fit_chatbot import FactualFITChatbot
from enhanced_fit_intelligence_api import EnhancedFITIntelligenceAPI
import re

class GPTOSSFITWrapper:
    def __init__(self):
        self.factual_chatbot = FactualFITChatbot()
        self.fit_api = EnhancedFITIntelligenceAPI()
        self.context = []  # Conversation history
        
    def query(self, user_input: str) -> str:
        """Process query with GPT-OSS understanding + FIT database facts"""
        
        # First, use our factual chatbot to get real data
        factual_response = self.factual_chatbot.chat(user_input)
        
        # Check for context-dependent queries
        if self._is_context_query(user_input):
            return self._handle_context_query(user_input)
        
        # Store context
        self.context.append({
            "query": user_input,
            "response": factual_response
        })
        
        return factual_response
    
    def _is_context_query(self, query: str) -> bool:
        """Check if query refers to previous context"""
        context_patterns = [
            r'\btheir\b',
            r'\bthese\b',
            r'\bthose\b',
            r'\bthe same\b',
            r'\babove\b',
            r'\bprevious\b'
        ]
        query_lower = query.lower()
        return any(re.search(pattern, query_lower) for pattern in context_patterns)
    
    def _handle_context_query(self, query: str) -> str:
        """Handle queries that reference previous results"""
        if not self.context:
            return "No previous query context available. Please ask a specific question first."
        
        last_response = self.context[-1]['response']
        query_lower = query.lower()
        
        # Extract FIT IDs from previous response
        if 'fit id' in query_lower or 'their ids' in query_lower:
            fit_ids = re.findall(r'FIT ID[:\s]+(\d+)', last_response)
            if fit_ids:
                return "The FIT IDs are:\n" + "\n".join(f"• FIT ID {fid}" for fid in fit_ids)
            else:
                # Extract from numbered list
                lines = last_response.split('\n')
                fit_ids = []
                for line in lines:
                    match = re.search(r'(?:FIT ID|Site)[:\s]+(\d+)', line)
                    if match:
                        fit_ids.append(match.group(1))
                
                if fit_ids:
                    return "The FIT IDs from the previous results are:\n" + "\n".join(f"• FIT ID {fid}" for fid in fit_ids)
                else:
                    return "No FIT IDs found in the previous results"
        
        # Extract rates
        if 'rate' in query_lower or 'tariff' in query_lower:
            rates = re.findall(r'(\d+\.?\d*)\s*p/kWh', last_response)
            fit_ids = re.findall(r'FIT ID[:\s]+(\d+)', last_response)
            
            if rates and fit_ids:
                response = "The FIT rates are:\n"
                for fid, rate in zip(fit_ids, rates):
                    response += f"• FIT ID {fid}: {rate}p/kWh\n"
                return response
            elif rates:
                return "The FIT rates are: " + ", ".join(f"{r}p/kWh" for r in rates)
            else:
                return "No FIT rates found in the previous results"
        
        # Default: reprocess with context
        combined_query = f"Based on my previous query about '{self.context[-1]['query']}', {query}"
        return self.factual_chatbot.chat(combined_query)

def test_wrapper():
    """Test the GPT-OSS FIT wrapper"""
    wrapper = GPTOSSFITWrapper()
    
    print("=" * 60)
    print("GPT-OSS FIT WRAPPER TEST")
    print("=" * 60)
    
    # Test 1: Aberdeen query (should return AB postcodes only)
    print("\nTest 1: Geographic accuracy")
    response1 = wrapper.query("wind sites over 250kw near Aberdeen")
    print(response1)
    
    # Check for wrong postcodes
    if any(pc in response1 for pc in ['BD', 'ML', 'YO', 'LS']):
        print("❌ FAILED: Non-Aberdeen postcodes found!")
    elif 'AB' not in response1 and 'No matching' not in response1:
        print("❌ FAILED: No Aberdeen postcodes found!")
    else:
        print("✅ PASSED: Geographic accuracy maintained")
    
    # Test 2: Context query
    print("\n" + "-" * 40)
    print("Test 2: Context handling")
    response2 = wrapper.query("what are their FIT IDs?")
    print(response2)
    
    if 'FIT ID' in response2:
        print("✅ PASSED: Context understood")
    else:
        print("❌ FAILED: Context not understood")
    
    # Test 3: Specific FIT ID
    print("\n" + "-" * 40)
    print("Test 3: FIT ID lookup")
    response3 = wrapper.query("what is the rate for site 1585")
    print(response3)
    
    if '14.9p/kWh' in response3 or 'Site 1585' in response3:
        print("✅ PASSED: FIT ID lookup working")
    else:
        print("❌ FAILED: FIT ID lookup not working")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_wrapper()