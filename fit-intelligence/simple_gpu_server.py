#!/usr/bin/env python3
"""
Simple GPU inference server that works with existing CUDA 11.8
Optimized for FIT Intelligence domain
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from flask import Flask, request, jsonify
import logging
import time
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class SimpleGPUServer:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        if self.device == "cuda":
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"CUDA version: {torch.version.cuda}")
            logger.info(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
            torch.cuda.empty_cache()
        
        # Use Phi-2 - a small but capable model that fits well in GPU memory
        model_name = "microsoft/phi-2"
        
        logger.info(f"Loading model: {model_name}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        
        if self.device == "cuda":
            # Move model to GPU
            self.model = self.model.cuda()
            
        logger.info(f"Model loaded on {self.device}")
        
        # Create pipeline for easy generation
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if self.device == "cuda" else -1
        )
        
    def understand_query(self, query):
        """Extract structured information from FIT queries"""
        prompt = f"""You are analyzing a query about UK renewable energy FIT (Feed-in Tariff) installations.
Extract the following information and return as JSON:

Query: "{query}"

Return JSON with:
- is_followup: boolean (true if asking for more details, FIT IDs, or referencing previous results)
- intent: string (search_new, get_details, filter_results, or clarify)  
- search_params: object with any of:
  - technology: string (wind, solar, hydro, anaerobic_digestion, or null)
  - min_capacity_kw: number or null
  - max_capacity_kw: number or null
  - location: string or null (extract city/region names)
  - fit_id: string or null

JSON:"""
        
        response = self.generate(prompt, temperature=0.1, max_tokens=256)
        return response
    
    def generate(self, prompt, temperature=0.1, max_tokens=512):
        start_time = time.time()
        
        with torch.cuda.amp.autocast() if self.device == "cuda" else torch.no_grad():
            outputs = self.pipe(
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                top_p=0.9,
                return_full_text=False,
                pad_token_id=self.tokenizer.pad_token_id
            )
        
        response = outputs[0]['generated_text']
        inference_time = time.time() - start_time
        
        logger.info(f"Inference time: {inference_time:.2f}s")
        
        if self.device == "cuda":
            memory_gb = torch.cuda.memory_allocated() / 1024**3
            logger.info(f"GPU memory used: {memory_gb:.1f} GB")
        
        return response

# Initialize server
logger.info("Initializing Simple GPU Server...")
server = SimpleGPUServer()

@app.route('/api/generate', methods=['POST'])
def generate():
    """Ollama-compatible endpoint"""
    data = request.json
    prompt = data.get('prompt', '')
    options = data.get('options', {})
    temperature = options.get('temperature', 0.1)
    max_tokens = options.get('num_predict', 512)
    
    try:
        response = server.generate(prompt, temperature, max_tokens)
        
        return jsonify({
            "model": "phi-2",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "response": response,
            "done": True,
            "context": [],
            "total_duration": int(time.time() * 1e9),
            "prompt_eval_duration": 0,
            "eval_count": len(response.split()),
            "eval_duration": int(time.time() * 1e9)
        })
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/understand', methods=['POST'])
def understand():
    """Special endpoint for FIT query understanding"""
    data = request.json
    query = data.get('query', '')
    
    try:
        result = server.understand_query(query)
        
        # Try to parse as JSON
        try:
            parsed = json.loads(result)
            return jsonify(parsed)
        except:
            # Return raw if not valid JSON
            return jsonify({"response": result})
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "model": "phi-2",
        "device": server.device,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
        "memory_gb": f"{torch.cuda.memory_allocated() / 1024**3:.1f}" if torch.cuda.is_available() else None
    })

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Simple GPU Server Ready (Ollama-compatible)")
    logger.info("=" * 60)
    logger.info("Server: http://localhost:11434")
    logger.info("Endpoints:")
    logger.info("  POST /api/generate - Ollama-compatible generation")
    logger.info("  POST /api/understand - FIT query understanding")
    logger.info("  GET /health - Server health check")
    logger.info("=" * 60)
    
    # Run on Ollama's port as a drop-in replacement
    app.run(host="0.0.0.0", port=11434, debug=False)