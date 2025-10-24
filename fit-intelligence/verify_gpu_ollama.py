#!/usr/bin/env python3
"""
Quick GPU verification for Ollama
"""

import subprocess
import time
import requests
import json

def check_gpu_before():
    """Check GPU memory before inference"""
    result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.used', '--format=csv,noheader'], 
                          capture_output=True, text=True)
    print("GPU Status BEFORE:")
    print(result.stdout)
    
    lines = result.stdout.strip().split('\n')
    for line in lines:
        if 'RTX 3090' in line:
            mem_str = line.split(',')[1].strip()
            mem_mb = int(mem_str.replace(' MiB', ''))
            return mem_mb
    return 0

def check_gpu_during():
    """Check GPU memory during inference"""
    result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.used', '--format=csv,noheader'], 
                          capture_output=True, text=True)
    
    lines = result.stdout.strip().split('\n')
    for line in lines:
        if 'RTX 3090' in line:
            mem_str = line.split(',')[1].strip()
            mem_mb = int(mem_str.replace(' MiB', ''))
            return mem_mb
    return 0

def test_inference(model_name):
    """Test inference and monitor GPU"""
    print(f"\n{'='*60}")
    print(f"Testing {model_name} with GPU monitoring")
    print('='*60)
    
    # Check before
    mem_before = check_gpu_before()
    
    # Start inference
    print("\nStarting inference...")
    start = time.time()
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model_name,
                'prompt': 'What is the capital of Scotland?',
                'stream': False,
                'options': {
                    'temperature': 0.1,
                    'num_predict': 50
                }
            },
            timeout=30
        )
        
        # Check during (if we can catch it)
        mem_during = check_gpu_during()
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('response', '').strip()
            
            print(f"\n✅ Response in {elapsed:.1f}s")
            print(f"Answer: {answer[:100]}")
            
            # Check memory usage
            print(f"\nGPU Memory Analysis:")
            print(f"  Before: {mem_before} MB")
            print(f"  During/After: {mem_during} MB")
            print(f"  Increase: {mem_during - mem_before} MB")
            
            if mem_during > mem_before + 100:
                print("✅ GPU IS BEING USED! Memory increased significantly")
            else:
                print("⚠️  GPU might not be used, memory didn't increase much")
                
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    # Get available models
    try:
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                print(f"Found {len(models)} model(s):")
                for model in models:
                    print(f"  - {model['name']}")
                    test_inference(model['name'])
            else:
                print("No models available yet. Still downloading...")
                print("\nChecking download progress...")
                subprocess.run(['tail', '-1', '/tmp/ollama_pull.log'], stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")

if __name__ == "__main__":
    main()