#!/usr/bin/env python3
"""
Test Ollama with GPU and FIT Intelligence queries
"""

import requests
import json
import time
import subprocess

def check_ollama():
    """Check if Ollama is running and model is loaded"""
    try:
        # Check models
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        print("Available models:")
        print(result.stdout)
        
        # Check if using GPU
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if 'ollama' in result.stdout.lower():
            print("✅ Ollama is using GPU")
        else:
            print("⚠️  Ollama not detected on GPU yet")
            
    except Exception as e:
        print(f"Error checking Ollama: {e}")

def test_ollama_generation(prompt, model="llama2:13b"):
    """Test direct Ollama generation"""
    print(f"\n{'='*60}")
    print(f"Testing: {prompt[:50]}...")
    print(f"Model: {model}")
    print('-'*60)
    
    start = time.time()
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.1,
                    'num_predict': 100
                }
            },
            timeout=30
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received in {elapsed:.1f}s")
            print(f"Response: {data.get('response', '')[:200]}...")
            
            # Check if GPU was used
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            if 'ollama' in result.stdout.lower():
                print("✅ GPU was used for inference")
            
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def test_fit_queries():
    """Test FIT Intelligence specific queries"""
    
    test_queries = [
        {
            "query": "Extract search parameters from: 'wind sites near aberdeen over 225kw'. Return JSON.",
            "check": "Should identify Aberdeen, wind, and 225kw"
        },
        {
            "query": "Extract location and capacity from: 'solar installations in Yorkshire between 150kw and 500kw'. Return as JSON.",
            "check": "Should identify Yorkshire, solar, 150-500kw range"
        },
        {
            "query": "Is Aberdeen in Scotland? What are the postcode prefixes for Aberdeen?",
            "check": "Should identify AB postcodes"
        }
    ]
    
    print("\n" + "="*60)
    print("Testing FIT Intelligence Queries")
    print("="*60)
    
    for test in test_queries:
        result = test_ollama_generation(test["query"])
        if result:
            print(f"Expected: {test['check']}")
            print()

def main():
    print("="*60)
    print("Ollama GPU Test Suite")
    print("="*60)
    
    # Check Ollama status
    check_ollama()
    
    # Wait for model if needed
    print("\nWaiting for llama2:13b model to be ready...")
    for i in range(10):
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if 'llama2:13b' in result.stdout:
            print("✅ Model ready!")
            break
        print(f"Waiting... {i+1}/10")
        time.sleep(10)
    
    # Run tests
    test_fit_queries()
    
    print("\n" + "="*60)
    print("Test complete!")
    print("="*60)

if __name__ == "__main__":
    main()