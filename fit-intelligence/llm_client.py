#!/usr/bin/env python3
"""
Ollama LLM Client - GPU-accelerated inference
Replaces vLLM with direct Ollama HTTP API
"""
import os
import requests
import logging

logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
FIT_MODEL = os.getenv("FIT_MODEL", "llama2:13b")

def chat(system_prompt, user_prompt, model=None, temperature=0.1, max_tokens=512, timeout=30):
    """
    Chat with Ollama using the GPU-accelerated model
    """
    m = model or FIT_MODEL
    payload = {
        "model": m,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {
            "temperature": temperature, 
            "num_ctx": 4096, 
            "num_predict": max_tokens
        }
    }
    
    try:
        logger.info(f"Calling Ollama with model {m}")
        r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()["message"]["content"]
    except requests.exceptions.Timeout:
        logger.error(f"Ollama timeout after {timeout}s")
        raise
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        raise

def get_active_model():
    """Get the currently active model name"""
    return FIT_MODEL

def test_connection():
    """Test if Ollama is accessible and has models"""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        r.raise_for_status()
        models = r.json().get("models", [])
        return len(models) > 0, [m["name"] for m in models]
    except:
        return False, []