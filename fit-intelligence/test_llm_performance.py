#!/usr/bin/env python3
"""Test LLM performance and configuration"""

import time
import requests
import json

def test_model_speed(model_name):
    """Test response time for a model"""
    print(f"\nTesting {model_name}...")
    
    prompt = """Extract technology from: "wind farms in yorkshire"
    Return only: wind, solar, hydro, or all"""
    
    start = time.time()
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_gpu": -1  # Use all available GPU layers
                }
            },
            timeout=10
        )
        
        end = time.time()
        
        if response.status_code == 200:
            result = response.json()['response']
            print(f"✅ Success in {end-start:.2f}s")
            print(f"Response: {result[:100]}...")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout after 10 seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_gpu_usage():
    """Check if models are using GPU"""
    try:
        response = requests.get("http://localhost:11434/api/ps")
        if response.status_code == 200:
            models = response.json().get('models', [])
            print("\nActive models:")
            for model in models:
                print(f"  - {model['name']}: Size {model['size'] / 1e9:.1f}GB")
                print(f"    Details: {model.get('details', {})}")
        else:
            print("Could not get model status")
    except Exception as e:
        print(f"Error checking models: {e}")

def main():
    print("=" * 60)
    print("LLM Performance Test")
    print("=" * 60)
    
    # Check current GPU usage
    check_gpu_usage()
    
    # Test available models
    models_to_test = [
        "llama3.2:1b",
        "gpt-oss:20b"
    ]
    
    results = {}
    for model in models_to_test:
        # Check if model exists
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                available = [m['name'] for m in response.json().get('models', [])]
                if model in available:
                    results[model] = test_model_speed(model)
                else:
                    print(f"\n⚠️  {model} not found")
        except:
            pass
    
    print("\n" + "=" * 60)
    print("Recommendation:")
    if results.get("llama3.2:1b"):
        print("✅ Use llama3.2:1b for fast responses with good accuracy")
    elif results.get("gpt-oss:20b"):
        print("⚠️  gpt-oss:20b works but is slow - consider using fallback")
    else:
        print("❌ No working models - relying on rule-based fallback")
    print("=" * 60)

if __name__ == "__main__":
    main()