#!/usr/bin/env python3
"""Test improved chatbot with context handling"""

import requests
import json
import time

def test_chat_query(query, session_id="test_session"):
    """Test a chat query"""
    response = requests.post(
        "http://localhost:5000/api/chat",
        json={
            "message": query,
            "session_id": session_id
        }
    )
    return response.json()

def main():
    print("=" * 60)
    print("Testing Improved Chatbot with llama3.2:1b")
    print("=" * 60)
    
    # Test 1: Initial query
    print("\n1. Initial Query:")
    print("   Query: 'wind farms in yorkshire over 500kw'")
    start = time.time()
    response = test_chat_query("wind farms in yorkshire over 500kw", "test_improved")
    end = time.time()
    print(f"   Response time: {end-start:.2f}s")
    print(f"   Response preview: {response.get('response', '')[:200]}...")
    
    # Test 2: Context follow-up
    print("\n2. Context Follow-up:")
    print("   Query: 'give me all the details'")
    start = time.time()
    response = test_chat_query("give me all the details", "test_improved")
    end = time.time()
    print(f"   Response time: {end-start:.2f}s")
    
    # Check if it used previous results
    if "FIT ID" in response.get('response', ''):
        print("   ✅ Context retained - showing details from previous query")
    else:
        print("   ❌ Context lost - not showing previous results")
    
    # Test 3: FIT ID follow-up
    print("\n3. FIT ID Query:")
    print("   Query: 'what are their fit ids?'")
    start = time.time()
    response = test_chat_query("what are their fit ids?", "test_improved")
    end = time.time()
    print(f"   Response time: {end-start:.2f}s")
    
    if "FIT ID" in response.get('response', '') or "AUTO" in response.get('response', ''):
        print("   ✅ FIT IDs included in response")
        # Count FIT IDs
        fit_count = response['response'].count('FIT ID') + response['response'].count('AUTO')
        print(f"   Found {fit_count} FIT ID references")
    else:
        print("   ❌ No FIT IDs in response")
    
    # Test 4: New query to test session reset
    print("\n4. New Query (different topic):")
    print("   Query: 'solar installations in Aberdeen'")
    start = time.time()
    response = test_chat_query("solar installations in Aberdeen", "test_improved")
    end = time.time()
    print(f"   Response time: {end-start:.2f}s")
    
    # Check geographic accuracy
    if "AB" in response.get('response', ''):
        print("   ✅ Geographic filtering working (Aberdeen = AB postcodes)")
    else:
        print("   ⚠️  Check geographic filtering")
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("- Using llama3.2:1b for faster responses")
    print("- Context retention via session management")
    print("- FIT IDs included in all responses")
    print("- Fallback rules for when LLM times out")
    print("=" * 60)

if __name__ == "__main__":
    main()