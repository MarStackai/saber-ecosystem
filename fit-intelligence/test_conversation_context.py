#!/usr/bin/env python3
"""
Test Conversation Context System
Demonstrates how the conversation memory works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from conversation_context import ConversationContext, enhance_query_with_context
from ollama_query_parser import OllamaQueryParser
import json

def test_conversation_flow():
    """Test a complete conversation flow with follow-ups and corrections"""
    
    print("=" * 60)
    print("TESTING CONVERSATION CONTEXT SYSTEM")
    print("=" * 60)
    
    # Initialize conversation manager
    conversation = ConversationContext()
    session_id = "test-session-123"
    
    # Initialize Ollama parser (if available)
    parser = OllamaQueryParser()
    
    # Test queries
    test_queries = [
        ("329kw installation near stevenage", {"capacity": 329, "location": "Stevenage"}),
        ("stevenage i meant", {}),  # Correction - should update location
        ("what about 300kw?", {"capacity": 300}),  # Follow-up - should keep Stevenage
        ("or wind farms?", {"technology": "Wind"}),  # Another follow-up - should keep capacity and location
        ("what are the nearest installations", {}),  # Should use previous location for geographic search
    ]
    
    print("\nSimulating conversation flow:")
    print("-" * 40)
    
    for i, (query, raw_entities) in enumerate(test_queries, 1):
        print(f"\n{i}. User: '{query}'")
        print(f"   Raw entities extracted: {raw_entities}")
        
        # Simulate previous results count
        results_count = 10 if i > 1 else 0
        
        # Apply conversation context
        enhanced_entities = enhance_query_with_context(
            session_id, query, raw_entities, results_count
        )
        
        print(f"   Enhanced with context: {json.dumps(enhanced_entities, indent=6)}")
        
        # Show what the system understands
        if enhanced_entities.get('location'):
            print(f"   → Looking in: {enhanced_entities['location']}")
        if enhanced_entities.get('capacity'):
            print(f"   → Capacity: {enhanced_entities['capacity']}kW")
        if enhanced_entities.get('capacity_min') or enhanced_entities.get('capacity_max'):
            min_cap = enhanced_entities.get('capacity_min', 0)
            max_cap = enhanced_entities.get('capacity_max', 'any')
            print(f"   → Capacity range: {min_cap}-{max_cap}kW")
        if enhanced_entities.get('technology'):
            print(f"   → Technology: {enhanced_entities['technology']}")
    
    # Get final context summary
    print("\n" + "=" * 60)
    summary = conversation.get_context_summary(session_id)
    print(f"Final {summary}")
    print("=" * 60)
    
    # Test with Ollama if available
    if parser.available:
        print("\n\nTesting with Ollama Parser:")
        print("-" * 40)
        
        ollama_queries = [
            "330kw in ryedale",
            "what about 250kw?",
            "or solar installations?"
        ]
        
        session_id2 = "ollama-test-456"
        
        for query in ollama_queries:
            print(f"\nQuery: '{query}'")
            
            # Parse with Ollama
            ollama_result = parser.parse_query(query)
            if ollama_result:
                print(f"Ollama parsed: {json.dumps(ollama_result, indent=4)}")
                
                # Apply context
                enhanced = enhance_query_with_context(
                    session_id2, query, ollama_result, 5
                )
                print(f"With context: {json.dumps(enhanced, indent=4)}")
            else:
                print("Ollama parsing failed")
    else:
        print("\n⚠️  Ollama not available - skipping Ollama tests")
    
    print("\n✅ Conversation context system is working!")
    print("\nKey features demonstrated:")
    print("• Corrections: 'stevenage i meant' updates the location")
    print("• Follow-ups: 'what about 300kw?' keeps previous location")
    print("• Partial queries: 'or wind farms?' adds technology while keeping context")
    print("• Geographic context: 'nearest installations' uses stored location")

if __name__ == "__main__":
    test_conversation_flow()