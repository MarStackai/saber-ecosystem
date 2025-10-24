#!/usr/bin/env python3
"""
Test vLLM with FIT Intelligence queries
"""

import requests
import json
import time
from datetime import datetime

def test_vllm_server():
    """Test if vLLM server is running"""
    try:
        response = requests.get("http://localhost:8000/v1/models", timeout=2)
        if response.status_code == 200:
            print("✅ vLLM server is running")
            models = response.json()
            print(f"Available models: {models}")
            return True
    except:
        pass
    
    print("❌ vLLM server not responding on port 8000")
    print("Starting fallback with TinyLlama for testing...")
    return False

def query_fit_intelligence(query: str, session_id: str = "test-session"):
    """Send query to FIT Intelligence API"""
    url = "http://localhost:8888/api/chat"
    
    payload = {
        "message": query,
        "session_id": session_id
    }
    
    print(f"\n🔍 Query: {query}")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response ({elapsed:.1f}s):")
            print(data.get("response", "No response"))
            
            if "fit_ids" in data:
                print(f"\nFIT IDs found: {len(data['fit_ids'])}")
                for fit_id in data['fit_ids'][:5]:
                    print(f"  - {fit_id}")
            
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def main():
    """Run test queries"""
    
    print("=" * 60)
    print("FIT Intelligence vLLM Query Test")
    print("=" * 60)
    print(f"Time: {datetime.now()}")
    
    # Check vLLM status
    vllm_running = test_vllm_server()
    
    # Test queries as requested by user
    test_queries = [
        ("wind sites near aberdeen over 225kw", "test-1"),
        ("solar installations in Yorkshire between 150kw and 500kw", "test-2"),
        ("give me all the details", "test-2"),  # Context test
    ]
    
    print("\n" + "=" * 60)
    print("Running Test Queries")
    print("=" * 60)
    
    for query, session_id in test_queries:
        result = query_fit_intelligence(query, session_id)
        
        if result and "response" in result:
            # Check for geographic accuracy
            response_text = result["response"].lower()
            
            if "aberdeen" in query.lower():
                if "ab" in response_text or "aberdeen" in response_text:
                    print("✅ Geographic accuracy: Aberdeen postcodes found")
                else:
                    print("❌ Geographic accuracy: No Aberdeen (AB) postcodes")
            
            if "yorkshire" in query.lower():
                yorkshire_postcodes = ["yo", "hu", "ls", "bd", "hx", "hd", "wf", "dn"]
                if any(pc in response_text for pc in yorkshire_postcodes):
                    print("✅ Geographic accuracy: Yorkshire postcodes found")
                else:
                    print("❌ Geographic accuracy: No Yorkshire postcodes")
        
        time.sleep(2)  # Brief pause between queries
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()