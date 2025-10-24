#!/bin/bash
# FIT Intelligence Training Pipeline Launcher
# Optimized for 24GB GPU + 128GB RAM workstation

# Use virtual environment Python if it exists
if [ -f "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
else
    PYTHON="python3"
fi

echo "🚀 FIT Intelligence Training Pipeline"
echo "======================================"

# Check GPU availability
echo "🔍 Checking GPU status..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits
else
    echo "⚠️  nvidia-smi not found - using CPU training"
fi

# Check Python dependencies
echo ""
echo "📦 Checking dependencies..."
$PYTHON -c "
import torch
import sentence_transformers
import chromadb
print(f'✅ PyTorch: {torch.__version__}')
print(f'✅ CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'✅ GPU: {torch.cuda.get_device_name(0)}')
    print(f'✅ GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB')
print(f'✅ Sentence Transformers: {sentence_transformers.__version__}')
print(f'✅ ChromaDB available')
"

echo ""
echo "🧪 Step 1: Analyze current performance..."
$PYTHON real_query_trainer.py

echo ""
echo "🎯 Step 2: Start training pipeline..."
echo "This may take 15-30 minutes on your 24GB GPU..."

# Set optimal training environment variables
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export CUDA_VISIBLE_DEVICES=0

# Run training with progress monitoring
$PYTHON training_pipeline.py 2>&1 | tee training_log.txt

# Check if training completed successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Training completed successfully!"
    echo ""
    echo "🚀 Step 3: Deploy trained model..."
    $PYTHON deploy_trained_model.py
    
    echo ""
    echo "🧪 Step 4: Quick test of trained model..."
    echo "Testing: 'wind sites over 250kw in yorkshire'"
    $PYTHON -c "
try:
    from geo_enhanced_fit_chatbot_trained import GeoEnhancedFITChatbot
    bot = GeoEnhancedFITChatbot()
    result = bot.chat('wind sites over 250kw in yorkshire')
    print('🎯 Trained model result:')
    print(result)
except Exception as e:
    print(f'❌ Test failed: {e}')
    print('💡 Try: $PYTHON geo_enhanced_fit_chatbot_trained.py')
"
    
    echo ""
    echo "🎉 TRAINING PIPELINE COMPLETED!"
    echo "==============================================="
    echo "📁 New files created:"
    echo "  - models/fit_intelligence_v1/           (trained model)"
    echo "  - trained_fit_intelligence_api.py       (enhanced API)"
    echo "  - geo_enhanced_fit_chatbot_trained.py   (improved chatbot)"
    echo "  - training_log.txt                      (training logs)"
    echo "  - model_comparison.json                  (performance comparison)"
    echo ""
    echo "🚀 To use the improved system:"
    echo "  $PYTHON -c \"from geo_enhanced_fit_chatbot_trained import GeoEnhancedFITChatbot; bot = GeoEnhancedFITChatbot(); print(bot.chat('your query here'))\""
    echo ""
    echo "📊 To start the web interface with trained model:"
    echo "  # Update geo_fit_chatbot_interface.html to use trained model"
    echo "  # Then open in browser"
    
else
    echo ""
    echo "❌ Training failed! Check training_log.txt for details"
    echo "💡 Common issues:"
    echo "  - GPU memory full (reduce batch_size in training_pipeline.py)"
    echo "  - Missing dependencies (pip install -r requirements.txt)"
    echo "  - CUDA version mismatch"
fi