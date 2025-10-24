#!/usr/bin/env python3
"""
Test FIT Price Integration
Tests the complete FIT price integration with the enhanced chatbot
"""

from enhanced_fit_chatbot import EnhancedFITChatbot
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_fit_integration():
    """Test the FIT price integration"""
    
    print("="*70)
    print("🚀 TESTING FIT PRICE INTEGRATION")
    print("="*70)
    
    # Initialize enhanced chatbot
    print("\n1. Initializing Enhanced FIT Chatbot...")
    chatbot = EnhancedFITChatbot()
    
    # Test queries
    test_queries = [
        "What was the FIT rate in November 2013 for a 350kW turbine?",
        "What was the FIT rate in April 2012 for a 500kW turbine?", 
        "FIT rate for 25kW solar in June 2011?",
        "What rate would a 150kW hydro get in 2012?",
        "What was the rate for 4kW solar in 2010?",
        "How many wind sites are there?",  # Non-FIT rate query
    ]
    
    print("\n2. Testing FIT Rate Queries...")
    print("-" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("📋 Response:")
        try:
            response = chatbot.chat(query)
            print(response)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)
    
    print("\n✅ FIT Integration Testing Complete!")

if __name__ == "__main__":
    test_fit_integration()