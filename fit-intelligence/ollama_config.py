#!/usr/bin/env python3
"""
Ollama Configuration for FIT Intelligence
Low temperature for factual accuracy
"""

OLLAMA_CONFIG = {
    "temperature": 0.05,  # Even lower for maximum factual accuracy
    "top_p": 0.9,       # Moderate diversity
    "top_k": 40,        # Limited token selection
    "repeat_penalty": 1.1,  # Avoid repetition
    "seed": 42,         # Reproducible responses
    "num_predict": 250, # Limit response length
    "stop": ["User:", "Human:", "Assistant:", "\n\n\n"]  # Stop sequences
}

SYSTEM_PROMPT = """You are a database query assistant for UK renewable energy FIT sites.
CRITICAL RULES:
1. Only return facts from the database - no opinions or predictions
2. If data is not available, say "Data not available"
3. Do not perform calculations unless explicitly requested
4. Be precise with numbers and locations
5. Format responses as bullet points for clarity
6. Maximum 5 sites per response unless more requested"""

def get_ollama_params(prompt: str, system: str = SYSTEM_PROMPT):
    """Get Ollama API parameters with strict settings"""
    return {
        "prompt": f"{system}\n\nUser: {prompt}\n\nAssistant:",
        "stream": False,
        "options": OLLAMA_CONFIG
    }