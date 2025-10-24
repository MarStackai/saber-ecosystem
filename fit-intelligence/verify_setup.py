#!/usr/bin/env python3
"""
Verify FIT Intelligence System Setup
"""

import sys
import os
from pathlib import Path

def check_package(name, import_name=None):
    """Check if a package is installed and importable"""
    import_name = import_name or name
    try:
        __import__(import_name)
        return True, f"✓ {name} installed"
    except ImportError as e:
        return False, f"✗ {name} missing: {e}"

def check_data_files():
    """Check if required data files exist"""
    data_dir = Path("data")
    chroma_dir = Path("chroma_db")
    
    files_to_check = [
        ("ChromaDB database", chroma_dir / "chroma.sqlite3"),
        ("Commercial FIT data", data_dir / "all_commercial_fit.json"),
        ("Enhanced sites data", data_dir / "commercial_sites_enhanced_with_fit.json"),
        ("Commercial solar CSV", data_dir / "commercial_solar_fit.csv"),
    ]
    
    results = []
    for name, path in files_to_check:
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            results.append((True, f"✓ {name}: {size_mb:.1f} MB"))
        else:
            results.append((False, f"✗ {name}: Not found"))
    
    return results

def check_gpu():
    """Check if GPU is available"""
    try:
        import torch
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            return True, f"✓ GPU available: {device_name} ({memory_gb:.1f} GB)"
        else:
            return False, "✗ No CUDA GPU available (CPU mode)"
    except ImportError:
        return False, "⚠ PyTorch not installed (required for GPU check)"

def main():
    print("=" * 60)
    print("FIT INTELLIGENCE SYSTEM VERIFICATION")
    print("=" * 60)
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"\n✓ Python {python_version}")
    
    # Check core packages
    print("\n📦 CORE PACKAGES:")
    print("-" * 40)
    packages = [
        ("NumPy", "numpy"),
        ("Pandas", "pandas"),
        ("ChromaDB", "chromadb"),
        ("Flask", "flask"),
        ("Python-dotenv", "dotenv"),
        ("OpenPyXL", "openpyxl"),
    ]
    
    all_good = True
    for name, import_name in packages:
        success, msg = check_package(name, import_name)
        print(msg)
        if not success:
            all_good = False
    
    # Check optional ML packages
    print("\n🤖 ML PACKAGES (Optional):")
    print("-" * 40)
    ml_packages = [
        ("PyTorch", "torch"),
        ("Transformers", "transformers"),
        ("Sentence-Transformers", "sentence_transformers"),
    ]
    
    for name, import_name in ml_packages:
        success, msg = check_package(name, import_name)
        print(msg)
    
    # Check GPU
    print("\n🎮 GPU STATUS:")
    print("-" * 40)
    success, msg = check_gpu()
    print(msg)
    
    # Check data files
    print("\n📂 DATA FILES:")
    print("-" * 40)
    file_results = check_data_files()
    for success, msg in file_results:
        print(msg)
        if not success:
            all_good = False
    
    # Check environment
    print("\n🔧 ENVIRONMENT:")
    print("-" * 40)
    print(f"✓ Working directory: {os.getcwd()}")
    if os.path.exists("venv"):
        print("✓ Virtual environment: venv/")
    else:
        print("✗ Virtual environment not found")
        all_good = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_good:
        print("✅ SETUP VERIFIED - System ready to use!")
        print("\nNext steps:")
        print("1. Explore data: python3 explore_fit_data.py")
        print("2. Start chatbot: python3 fit_chatbot.py")
        print("3. Start API: python3 fit_intelligence_api.py")
    else:
        print("⚠️  PARTIAL SETUP - Some components missing")
        print("\nCore functionality should work, but some features may be limited.")
    print("=" * 60)

if __name__ == "__main__":
    main()