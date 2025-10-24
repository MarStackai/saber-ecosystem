#!/usr/bin/env python3
"""
PyTorch-based GPU inference server for FIT Intelligence
Uses transformers library with CUDA acceleration
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from flask import Flask, request, jsonify
import logging
import time
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class GPUInferenceServer:
    def __init__(self, model_name="microsoft/phi-2"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        if self.device == "cuda":
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"CUDA version: {torch.version.cuda}")
            logger.info(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        
        logger.info(f"Loading model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None,
            trust_remote_code=True
        )
        
        if self.device == "cuda":
            self.model = self.model.cuda()
        
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if self.device == "cuda" else -1
        )
        
        logger.info("Model loaded successfully")
    
    def generate(self, prompt, max_length=512, temperature=0.1):
        start_time = time.time()
        
        with torch.cuda.amp.autocast() if self.device == "cuda" else torch.no_grad():
            outputs = self.pipe(
                prompt,
                max_new_tokens=max_length,
                temperature=temperature,
                do_sample=True if temperature > 0 else False,
                top_p=0.9,
                return_full_text=False
            )
        
        response = outputs[0]['generated_text']
        inference_time = time.time() - start_time
        
        logger.info(f"Inference time: {inference_time:.2f}s")
        
        if self.device == "cuda":
            logger.info(f"GPU memory used: {torch.cuda.memory_allocated() / 1024**3:.1f} GB")
        
        return response

inference_server = None

@app.route('/v1/completions', methods=['POST'])
def completions():
    global inference_server
    
    if inference_server is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    data = request.json
    prompt = data.get('prompt', '')
    max_tokens = data.get('max_tokens', 512)
    temperature = data.get('temperature', 0.1)
    
    try:
        response = inference_server.generate(prompt, max_tokens, temperature)
        
        return jsonify({
            "choices": [{
                "text": response,
                "index": 0,
                "finish_reason": "stop"
            }],
            "model": "phi-2",
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response.split())
            }
        })
    
    except Exception as e:
        logger.error(f"Error during inference: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/v1/models', methods=['GET'])
def models():
    return jsonify({
        "data": [{
            "id": "phi-2",
            "object": "model",
            "owned_by": "microsoft"
        }]
    })

@app.route('/health', methods=['GET'])
def health():
    if inference_server is None:
        return jsonify({"status": "loading"}), 503
    
    return jsonify({
        "status": "healthy",
        "device": inference_server.device,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "cuda_version": torch.version.cuda if torch.cuda.is_available() else None
    })

if __name__ == "__main__":
    logger.info("Starting PyTorch GPU Inference Server...")
    
    inference_server = GPUInferenceServer()
    
    logger.info("Server ready at http://localhost:8000")
    logger.info("Endpoints:")
    logger.info("  POST /v1/completions - Generate text")
    logger.info("  GET /v1/models - List models")
    logger.info("  GET /health - Health check")
    
    app.run(host="0.0.0.0", port=8000, debug=False)