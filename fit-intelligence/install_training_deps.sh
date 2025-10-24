#!/bin/bash
# Install dependencies for LoRA training

echo "Installing PyTorch with CUDA support..."
python3 -m pip install --user torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo "Installing Transformers ecosystem..."
python3 -m pip install --user transformers==4.36.0
python3 -m pip install --user peft==0.7.0
python3 -m pip install --user bitsandbytes==0.41.0
python3 -m pip install --user accelerate==0.25.0
python3 -m pip install --user datasets==2.14.0
python3 -m pip install --user trl==0.7.0

echo "Installing additional dependencies..."
python3 -m pip install --user scipy sentencepiece protobuf tensorboard

echo "✅ Installation complete!"
echo "Verify with: python3 train_gpt_oss_lora_proper.py"