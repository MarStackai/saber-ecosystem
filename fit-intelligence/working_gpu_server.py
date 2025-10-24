#!/usr/bin/env python3
"""
Working GPU server - guaranteed to work on RTX 3090
Using a proven model and simple Flask API
"""

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Force RTX 3090

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from flask import Flask, request, jsonify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Model that definitely works and fits
MODEL_NAME = "microsoft/phi-2"

logger.info("=" * 60)
logger.info("Starting Working GPU Server")
logger.info("=" * 60)
logger.info(f"Model: {MODEL_NAME}")
logger.info(f"Device: cuda:0 (RTX 3090)")
logger.info("=" * 60)

# Load model
logger.info("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

logger.info("Loading model to GPU...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    trust_remote_code=True
).to("cuda:0")

logger.info(f"Model loaded! Device: {next(model.parameters()).device}")
logger.info(f"GPU Memory: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")

@app.route('/v1/completions', methods=['POST'])
def completions():
    """OpenAI-compatible completions endpoint"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 100)
        temperature = data.get('temperature', 0.1)
        
        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda:0")
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                pad_token_id=tokenizer.pad_token_id
            )
        
        # Decode
        generated = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        
        return jsonify({
            "choices": [{
                "text": generated,
                "index": 0,
                "finish_reason": "stop"
            }],
            "model": MODEL_NAME
        })
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "ready",
        "model": MODEL_NAME,
        "device": "cuda:0",
        "gpu": torch.cuda.get_device_name(0),
        "memory_used_gb": f"{torch.cuda.memory_allocated(0) / 1024**3:.2f}"
    })

if __name__ == '__main__':
    logger.info("-" * 60)
    logger.info("Server starting on http://localhost:8002")
    logger.info("Endpoints:")
    logger.info("  POST /v1/completions - Generate text")
    logger.info("  GET /health - Check status")
    logger.info("-" * 60)
    app.run(host='0.0.0.0', port=8002, debug=False)