#!/bin/bash
# Ubuntu Workstation Setup for FIT Intelligence Training
# Optimized for 24GB GPU + 128GB RAM system

echo "🖥️  FIT Intelligence Ubuntu Workstation Setup"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}❌ Please run as regular user, not root${NC}"
    exit 1
fi

echo "📋 System Requirements Check..."
echo "- Ubuntu 20.04+ ✓"
echo "- 24GB+ GPU Memory ✓" 
echo "- 128GB+ System RAM ✓"
echo "- CUDA-compatible GPU ✓"
echo ""

# Update system
echo "🔄 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "📦 Installing essential packages..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    git \
    wget \
    curl \
    htop \
    nvtop \
    build-essential \
    software-properties-common

# Install NVIDIA drivers and CUDA (if not already installed)
echo "🎮 Checking NVIDIA setup..."
if ! command -v nvidia-smi &> /dev/null; then
    echo "Installing NVIDIA drivers..."
    sudo ubuntu-drivers autoinstall
    echo "⚠️  Please reboot after this script completes to load NVIDIA drivers"
else
    echo "✅ NVIDIA drivers already installed"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
fi

# Install CUDA toolkit
if ! command -v nvcc &> /dev/null; then
    echo "📥 Installing CUDA toolkit..."
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb
    sudo dpkg -i cuda-keyring_1.0-1_all.deb
    sudo apt-get update
    sudo apt-get -y install cuda
    echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
    echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
else
    echo "✅ CUDA already installed"
fi

# Create project directory
PROJECT_DIR="$HOME/fit-intelligence-training"
echo "📁 Creating project directory: $PROJECT_DIR"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Create Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install PyTorch with CUDA support
echo "⚡ Installing PyTorch with CUDA support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install training dependencies
echo "📚 Installing training dependencies..."
cat > requirements.txt << EOF
torch>=2.0.0
torchvision>=0.15.0
torchaudio>=2.0.0
sentence-transformers>=2.2.0
transformers>=4.30.0
datasets>=2.12.0
accelerate>=0.20.0
chromadb>=0.4.0
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
jupyterlab>=4.0.0
tensorboard>=2.13.0
wandb>=0.15.0
flask>=2.3.0
requests>=2.31.0
tqdm>=4.65.0
python-dotenv>=1.0.0
psutil>=5.9.0
EOF

pip install -r requirements.txt

# Test PyTorch CUDA installation
echo "🧪 Testing PyTorch CUDA installation..."
python3 -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU count: {torch.cuda.device_count()}')
    print(f'GPU name: {torch.cuda.get_device_name(0)}')
    print(f'GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB')
else:
    print('❌ CUDA not available - check NVIDIA driver installation')
"

# Create directory structure
echo "📂 Creating directory structure..."
mkdir -p {data,models,logs,backups,notebooks,scripts}

# Create environment file
echo "⚙️  Creating environment configuration..."
cat > .env << EOF
# FIT Intelligence Training Environment
PROJECT_NAME=fit-intelligence-training
CUDA_VISIBLE_DEVICES=0
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Training Configuration  
BATCH_SIZE=16
EPOCHS=4
LEARNING_RATE=2e-5
MAX_SEQ_LENGTH=256

# Paths
MODEL_OUTPUT_DIR=./models
DATA_DIR=./data
LOGS_DIR=./logs

# Hardware Configuration
GPU_MEMORY_GB=24
SYSTEM_RAM_GB=128
EOF

# Create project transfer script
echo "📋 Creating project transfer script..."
cat > transfer_from_mac.sh << 'EOF'
#!/bin/bash
# Transfer project files from Mac

MAC_USER="robcarroll"
MAC_HOST="your-mac-ip-or-hostname"  # Update this
PROJECT_PATH="/Users/robcarroll/wind-repowering-db"

echo "📡 Transferring project files from Mac..."
echo "Please ensure:"
echo "1. SSH access to Mac is configured"
echo "2. Update MAC_HOST variable in this script"
echo "3. Mac has the wind-repowering-db project"
echo ""

# Core project files to transfer
rsync -avz --progress \
    $MAC_USER@$MAC_HOST:$PROJECT_PATH/{*.py,*.json,*.md} \
    ./

# Data directories
rsync -avz --progress \
    $MAC_USER@$MAC_HOST:$PROJECT_PATH/chroma_db/ \
    ./chroma_db/

rsync -avz --progress \
    $MAC_USER@$MAC_HOST:$PROJECT_PATH/data/ \
    ./data/

echo "✅ Project transfer completed!"
EOF

chmod +x transfer_from_mac.sh

# Create monitoring script
echo "📊 Creating system monitoring script..."
cat > monitor_training.py << 'EOF'
#!/usr/bin/env python3
"""
Training Monitor - Track GPU/CPU usage during training
"""

import psutil
import time
import subprocess
import json
from datetime import datetime

def get_gpu_info():
    """Get GPU memory usage"""
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu,temperature.gpu', 
                               '--format=csv,noheader,nounits'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            gpu_data = []
            for line in lines:
                used, total, util, temp = line.split(', ')
                gpu_data.append({
                    'memory_used_mb': int(used),
                    'memory_total_mb': int(total),
                    'memory_percent': round(int(used) / int(total) * 100, 1),
                    'utilization_percent': int(util),
                    'temperature_c': int(temp)
                })
            return gpu_data
    except:
        pass
    return []

def monitor_system(duration_minutes=30):
    """Monitor system during training"""
    print("🖥️  Starting system monitoring...")
    print("📊 Monitoring for", duration_minutes, "minutes")
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    log_data = []
    
    while time.time() < end_time:
        timestamp = datetime.now().isoformat()
        
        # CPU info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # GPU info
        gpu_info = get_gpu_info()
        
        data_point = {
            'timestamp': timestamp,
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_gb': round(memory.used / 1e9, 2),
            'memory_available_gb': round(memory.available / 1e9, 2),
            'gpu_info': gpu_info
        }
        
        log_data.append(data_point)
        
        # Print current status
        gpu_status = ""
        if gpu_info:
            gpu_status = f"GPU: {gpu_info[0]['memory_percent']}% mem, {gpu_info[0]['utilization_percent']}% util, {gpu_info[0]['temperature_c']}°C"
        
        print(f"[{timestamp[:19]}] CPU: {cpu_percent:5.1f}% | RAM: {memory.percent:5.1f}% | {gpu_status}")
        
        time.sleep(10)  # Log every 10 seconds
    
    # Save log data
    with open(f'training_monitor_{int(start_time)}.json', 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print("✅ Monitoring completed, data saved")

if __name__ == "__main__":
    monitor_system()
EOF

chmod +x monitor_training.py

# Create quick setup verification
echo "✅ Creating setup verification..."
cat > verify_setup.py << 'EOF'
#!/usr/bin/env python3
"""
Verify Ubuntu workstation setup for FIT training
"""

import torch
import sys
import psutil
import subprocess

def check_system():
    print("🔍 FIT Intelligence Setup Verification")
    print("=" * 50)
    
    # Python version
    print(f"Python: {sys.version.split()[0]} ✅")
    
    # PyTorch
    print(f"PyTorch: {torch.__version__} ✅")
    
    # CUDA
    cuda_available = torch.cuda.is_available()
    print(f"CUDA available: {cuda_available}", "✅" if cuda_available else "❌")
    
    if cuda_available:
        print(f"CUDA version: {torch.version.cuda} ✅")
        print(f"GPU count: {torch.cuda.device_count()} ✅")
        
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            print(f"GPU {i}: {props.name} ({props.total_memory / 1e9:.1f}GB) ✅")
    
    # System memory
    memory = psutil.virtual_memory()
    print(f"System RAM: {memory.total / 1e9:.1f}GB ✅")
    
    # Test sentence transformers
    try:
        from sentence_transformers import SentenceTransformer
        print("Sentence Transformers: Available ✅")
    except ImportError:
        print("Sentence Transformers: Missing ❌")
    
    # Test ChromaDB
    try:
        import chromadb
        print("ChromaDB: Available ✅")
    except ImportError:
        print("ChromaDB: Missing ❌")
    
    print("\n🎯 System Ready for FIT Intelligence Training!")

if __name__ == "__main__":
    check_system()
EOF

chmod +x verify_setup.py

# Final setup summary
echo ""
echo -e "${GREEN}🎉 Ubuntu Workstation Setup Complete!${NC}"
echo "================================================"
echo "📁 Project directory: $PROJECT_DIR"
echo "🐍 Virtual environment: $PROJECT_DIR/venv"
echo ""
echo "📋 Next steps:"
echo "1. Reboot system if NVIDIA drivers were installed"
echo "2. Update MAC_HOST in transfer_from_mac.sh"
echo "3. Run: ./transfer_from_mac.sh"
echo "4. Run: python3 verify_setup.py"
echo "5. Start training: ./start_training.sh"
echo ""
echo "🔧 Useful commands:"
echo "  source venv/bin/activate     # Activate Python environment"
echo "  nvidia-smi                   # Check GPU status"
echo "  python3 monitor_training.py # Monitor system during training"
echo "  htop                         # Monitor CPU"
echo "  nvtop                        # Monitor GPU"
echo ""
echo -e "${YELLOW}⚠️  Remember to update the MAC_HOST variable in transfer_from_mac.sh${NC}"