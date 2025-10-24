#!/usr/bin/env python3
"""
GPU-accelerated inference server using HuggingFace Accelerate
Works with existing CUDA 11.8 installation
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from accelerate import init_empty_weights, load_checkpoint_and_dispatch, infer_auto_device_map
from flask import Flask, request, jsonify
import logging
import time
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class AccelerateGPUServer:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        if self.device == "cuda":
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"CUDA version: {torch.version.cuda}")
            logger.info(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
            torch.cuda.empty_cache()
        
        # Load a model optimized for our GPU
        model_name = "TheBloke/Llama-2-7B-GPTQ"  # Quantized for efficiency
        
        logger.info(f"Loading model: {model_name}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model with device mapping for optimal GPU usage
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        
        logger.info("Model loaded on GPU")
        
    def generate(self, prompt, temperature=0.1, max_tokens=512):
        start_time = time.time()
        
        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Generate with GPU acceleration
        with torch.cuda.amp.autocast():
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=temperature > 0,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.pad_token_id
                )
        
        # Decode response
        response = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        
        inference_time = time.time() - start_time
        logger.info(f"Inference time: {inference_time:.2f}s")
        
        if self.device == "cuda":
            memory_used = torch.cuda.memory_allocated() / 1024**3
            memory_reserved = torch.cuda.memory_reserved() / 1024**3
            logger.info(f"GPU memory: {memory_used:.1f}GB used, {memory_reserved:.1f}GB reserved")
        
        return response

# Initialize server
logger.info("Initializing Accelerate GPU Server...")
server = AccelerateGPUServer()

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    data = request.json
    messages = data.get('messages', [])
    temperature = data.get('temperature', 0.1)
    max_tokens = data.get('max_tokens', 512)
    
    # Convert messages to prompt
    prompt = ""
    for msg in messages:
        role = msg.get('role', 'user')
        content = msg.get('content', '')
        if role == 'system':
            prompt += f"System: {content}\n"
        elif role == 'user':
            prompt += f"User: {content}\n"
        elif role == 'assistant':
            prompt += f"Assistant: {content}\n"
    prompt += "Assistant: "
    
    try:
        response = server.generate(prompt, temperature, max_tokens)
        
        return jsonify({
            "id": f"chat-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "llama-2-7b",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response.split()),
                "total_tokens": len(prompt.split()) + len(response.split())
            }
        })
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/v1/completions', methods=['POST'])
def completions():
    data = request.json
    prompt = data.get('prompt', '')
    temperature = data.get('temperature', 0.1)
    max_tokens = data.get('max_tokens', 512)
    
    try:
        response = server.generate(prompt, temperature, max_tokens)
        
        return jsonify({
            "id": f"cmpl-{int(time.time())}",
            "object": "text_completion",
            "created": int(time.time()),
            "model": "llama-2-7b",
            "choices": [{
                "text": response,
                "index": 0,
                "logprobs": None,
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response.split()),
                "total_tokens": len(prompt.split()) + len(response.split())
            }
        })
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "model": "llama-2-7b",
        "device": server.device,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
        "memory_allocated": f"{torch.cuda.memory_allocated() / 1024**3:.1f}GB" if torch.cuda.is_available() else None
    })

@app.route('/v1/models', methods=['GET'])
def models():
    return jsonify({
        "object": "list",
        "data": [{
            "id": "llama-2-7b",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "thebloke"
        }]
    })

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Accelerate GPU Server Ready")
    logger.info("=" * 60)
    logger.info("Server: http://localhost:8000")
    logger.info("Endpoints:")
    logger.info("  POST /v1/chat/completions")
    logger.info("  POST /v1/completions")
    logger.info("  GET /v1/models")
    logger.info("  GET /health")
    logger.info("=" * 60)
    
    app.run(host="0.0.0.0", port=8000, debug=False)