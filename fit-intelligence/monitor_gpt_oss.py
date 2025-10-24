#!/usr/bin/env python3
"""
Monitor GPT-OSS download progress and launch training when ready
"""

import time
import subprocess
import requests
import sys
from datetime import datetime

def check_ollama_models():
    """Check what models are available in Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return [m['name'] for m in models]
    except:
        pass
    return []

def check_download_progress():
    """Check if GPT-OSS is downloading"""
    try:
        # Check for ollama pull process
        result = subprocess.run(
            "ps aux | grep 'ollama pull gpt-oss' | grep -v grep",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            # Try to get progress
            progress_check = subprocess.run(
                "timeout 2 ollama pull gpt-oss 2>&1 | grep -E 'pulling.*%' | tail -1",
                shell=True,
                capture_output=True,
                text=True
            )
            
            if progress_check.stdout:
                return True, progress_check.stdout.strip()
            else:
                return True, "Downloading... (progress unavailable)"
        
        return False, None
        
    except:
        return False, None

def main():
    print("=" * 60)
    print("🔍 GPT-OSS Download Monitor")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print("")
    
    last_progress = ""
    check_count = 0
    
    while True:
        check_count += 1
        
        # Check available models
        models = check_ollama_models()
        
        if any('gpt-oss' in m or 'gpt:oss' in m for m in models):
            print(f"\n✅ GPT-OSS is ready! Found in models: {models}")
            print("=" * 60)
            
            # Launch training pipeline
            print("\n🚀 Launching advanced training pipeline...")
            time.sleep(2)
            
            try:
                subprocess.run(["bash", "start_advanced_training.sh"])
            except KeyboardInterrupt:
                print("\n\n👋 Training interrupted by user")
            except Exception as e:
                print(f"\n❌ Error launching training: {e}")
            
            break
        
        # Check if downloading
        is_downloading, progress = check_download_progress()
        
        if is_downloading:
            if progress and progress != last_progress:
                # Clear line and print new progress
                sys.stdout.write('\r' + ' ' * 80 + '\r')
                sys.stdout.write(f"📥 {progress}")
                sys.stdout.flush()
                last_progress = progress
            elif check_count % 10 == 0:
                sys.stdout.write('.')
                sys.stdout.flush()
        else:
            print(f"\n⚠️  GPT-OSS not downloading and not available")
            print("Available models:", models[:5] if models else "None")
            
            # Ask user what to do
            print("\nOptions:")
            print("1. Start download: ollama pull gpt-oss")
            print("2. Use alternative model (llama3.2, mixtral, etc)")
            print("3. Keep waiting")
            print("4. Exit")
            
            choice = input("\nChoice (1-4): ").strip()
            
            if choice == "1":
                print("\n📥 Starting GPT-OSS download...")
                subprocess.Popen(["ollama", "pull", "gpt-oss"])
                time.sleep(5)  # Give it time to start
            elif choice == "2":
                print("\n🔄 Switching to alternative model...")
                # Could modify scripts to use different model
                break
            elif choice == "4":
                print("\n👋 Exiting...")
                sys.exit(0)
        
        # Wait before next check
        time.sleep(5)
    
    print("\n✅ Monitoring complete!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped by user")