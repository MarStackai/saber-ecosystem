# FIT Intelligence Ubuntu Installation

## Quick Setup
1. Run the setup script:
   ```bash
   chmod +x ubuntu_setup.sh
   ./ubuntu_setup.sh
   ```

2. Verify installation:
   ```bash
   source venv/bin/activate
   python3 verify_setup.py
   ```

3. Start training:
   ```bash
   chmod +x start_training.sh
   ./start_training.sh
   ```

## Manual Installation
If the setup script fails:

1. Install NVIDIA drivers:
   ```bash
   sudo ubuntu-drivers autoinstall
   sudo reboot
   ```

2. Install CUDA:
   ```bash
   wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb
   sudo dpkg -i cuda-keyring_1.0-1_all.deb
   sudo apt-get update
   sudo apt-get -y install cuda
   ```

3. Create Python environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## System Requirements
- Ubuntu 20.04+
- 24GB+ GPU Memory
- 128GB+ System RAM
- CUDA-compatible GPU

## Training Pipeline
The training consists of:
1. `real_query_trainer.py` - Analyze current performance
2. `training_pipeline.py` - Train the model
3. `deploy_trained_model.py` - Deploy improved model

## Monitoring
- Use `python3 monitor_training.py` to monitor system resources
- Use `nvidia-smi` to check GPU status
- Use `htop` for CPU monitoring
