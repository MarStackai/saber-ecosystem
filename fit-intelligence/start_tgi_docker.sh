#!/bin/bash
# Start Text Generation Inference with Docker
# Using only RTX 3090 (GPU 0)

echo "Starting Text Generation Inference (TGI) with Docker"
echo "Model: NousResearch/Llama-2-7b-chat-hf"
echo "GPU: RTX 3090 only (device 0)"
echo "Port: 8080"
echo "============================================"

# Kill any existing container
docker stop tgi-server 2>/dev/null
docker rm tgi-server 2>/dev/null

# Run TGI with only GPU 0 (RTX 3090)
# Using CUDA_VISIBLE_DEVICES to ensure only GPU 0 is seen
docker run -d \
  --name tgi-server \
  --gpus '"device=0"' \
  -e CUDA_VISIBLE_DEVICES=0 \
  -e HUGGING_FACE_HUB_TOKEN="" \
  -p 8080:80 \
  -v $HOME/.cache/huggingface:/data \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id NousResearch/Llama-2-7b-chat-hf \
  --max-input-length 2048 \
  --max-total-tokens 4096 \
  --max-batch-prefill-tokens 2048

echo "Container starting..."
echo "Logs: docker logs -f tgi-server"
echo "API will be available at http://localhost:8080"
echo ""
echo "To test when ready:"
echo "curl http://localhost:8080/generate -X POST -H 'Content-Type: application/json' -d '{\"inputs\":\"Test\",\"parameters\":{\"max_new_tokens\":20}}'"