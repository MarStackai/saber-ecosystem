#!/usr/bin/env python3
"""
Bridge to run Ollama models on GPU using PyTorch
Converts Ollama models to use GPU acceleration
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from flask import Flask, request, jsonify
import logging
import time
import os
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class OllamaGPUBridge:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        if self.device == "cuda":
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"CUDA version: {torch.version.cuda}")
            logger.info(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        
        self.model = None
        self.tokenizer = None
        self.current_model = None
    
    def load_model(self, model_name):
        if self.current_model == model_name:
            return True
        
        try:
            logger.info(f"Loading model: {model_name}")
            
            model_map = {
                "llama3.2:1b": "meta-llama/Llama-3.2-1B",
                "phi-2": "microsoft/phi-2",
                "tinyllama": "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
            }
            
            hf_model = model_map.get(model_name, "microsoft/phi-2")
            
            self.tokenizer = AutoTokenizer.from_pretrained(hf_model, trust_remote_code=True)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.model = AutoModelForCausalLM.from_pretrained(
                hf_model,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            if self.device == "cuda":
                self.model = self.model.cuda()
                torch.cuda.empty_cache()
            
            self.current_model = model_name
            logger.info(f"Model {model_name} loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            return False
    
    def generate(self, prompt, model="phi-2", temperature=0.1, max_tokens=512):
        if not self.load_model(model):
            return None
        
        start_time = time.time()
        
        inputs = self.tokenizer(prompt, return_tensors="pt")
        if self.device == "cuda":
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        with torch.cuda.amp.autocast() if self.device == "cuda" else torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                top_p=0.9,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        inference_time = time.time() - start_time
        
        logger.info(f"Inference time: {inference_time:.2f}s")
        
        if self.device == "cuda":
            memory_used = torch.cuda.memory_allocated() / 1024**3
            logger.info(f"GPU memory used: {memory_used:.1f} GB")
        
        return response

bridge = OllamaGPUBridge()

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    model = data.get('model', 'phi-2')
    temperature = data.get('options', {}).get('temperature', 0.1)
    max_tokens = data.get('options', {}).get('num_predict', 512)
    
    response = bridge.generate(prompt, model, temperature, max_tokens)
    
    if response is None:
        return jsonify({"error": "Model generation failed"}), 500
    
    return jsonify({
        "model": model,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "response": response,
        "done": True
    })

@app.route('/api/tags', methods=['GET'])
def list_models():
    return jsonify({
        "models": [
            {"name": "llama3.2:1b", "size": 1300000000},
            {"name": "phi-2", "size": 2700000000},
            {"name": "tinyllama", "size": 1100000000}
        ]
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "device": bridge.device,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
        "current_model": bridge.current_model
    })

if __name__ == "__main__":
    logger.info("Starting Ollama GPU Bridge Server...")
    logger.info("Server ready at http://localhost:11435")
    logger.info("This server acts as a drop-in replacement for Ollama but uses GPU")
    
    app.run(host="0.0.0.0", port=11435, debug=False)