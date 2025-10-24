#!/usr/bin/env python3
"""
Simple Training Monitor - No dependencies required
Monitors weekend training progress
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime
import subprocess

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def get_training_status():
    """Get current training status"""
    status = {
        "running": False,
        "current_iteration": 0,
        "best_model": None,
        "best_score": 0,
        "models": [],
        "start_time": None,
        "elapsed": "Not started"
    }
    
    # Check if training is running
    result = subprocess.run(
        ["pgrep", "-f", "weekend_training_pipeline.py"],
        capture_output=True
    )
    
    status["running"] = result.returncode == 0
    
    # Read checkpoints
    checkpoint_dir = Path("./weekend_checkpoints")
    if checkpoint_dir.exists():
        checkpoints = sorted(checkpoint_dir.glob("checkpoint_*.json"))
        if checkpoints:
            # Get latest checkpoint
            with open(checkpoints[-1], 'r') as f:
                latest = json.load(f)
                status["current_iteration"] = latest.get("iteration", 0)
                status["elapsed"] = latest.get("elapsed", "0:00:00")
            
            # Get all models
            for cp_file in checkpoints:
                with open(cp_file, 'r') as f:
                    cp = json.load(f)
                    model_info = {
                        "name": cp.get("model_name", ""),
                        "score": cp.get("score", 0),
                        "iteration": cp.get("iteration", 0)
                    }
                    status["models"].append(model_info)
            
            # Find best model
            if status["models"]:
                best = max(status["models"], key=lambda x: x["score"])
                status["best_model"] = best["name"]
                status["best_score"] = best["score"]
    
    # Read latest log
    log_files = sorted(Path(".").glob("weekend_training_*.log"))
    if log_files:
        status["log_file"] = str(log_files[-1])
        with open(log_files[-1], 'r') as f:
            lines = f.readlines()
            status["recent_logs"] = lines[-10:]  # Last 10 lines
    else:
        status["recent_logs"] = ["No logs yet..."]
    
    return status

def display_dashboard():
    """Display training dashboard in terminal"""
    while True:
        clear_screen()
        status = get_training_status()
        
        # Header
        print("=" * 80)
        print(" " * 20 + "🚀 FIT INTELLIGENCE TRAINING MONITOR 🚀")
        print("=" * 80)
        print()
        
        # Status
        if status["running"]:
            print(f"📊 Status: ✅ TRAINING RUNNING")
        else:
            print(f"📊 Status: ⏸️  IDLE")
        
        print(f"⏱️  Elapsed: {status['elapsed']}")
        print(f"🔄 Current Iteration: {status['current_iteration']}/20")
        print()
        
        # Progress bar
        progress = (status["current_iteration"] / 20) * 100
        bar_length = 50
        filled = int(bar_length * progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"Progress: [{bar}] {progress:.1f}%")
        print()
        
        # Best Model
        print("=" * 80)
        print("🏆 BEST MODEL")
        print("-" * 80)
        if status["best_model"]:
            print(f"Model: {status['best_model']}")
            print(f"Accuracy: {status['best_score']:.1f}%")
        else:
            print("No models trained yet")
        print()
        
        # Model History
        print("=" * 80)
        print("📈 MODEL PERFORMANCE")
        print("-" * 80)
        if status["models"]:
            # Show last 5 models
            for model in status["models"][-5:]:
                score_bar = "▓" * int(model["score"] / 5)
                print(f"Iter {model['iteration']:2d}: {model['name']:25s} {model['score']:5.1f}% {score_bar}")
        else:
            print("No models yet...")
        print()
        
        # Recent Logs
        print("=" * 80)
        print("📝 RECENT ACTIVITY")
        print("-" * 80)
        for log_line in status["recent_logs"][-5:]:
            # Clean up the log line
            if isinstance(log_line, str):
                cleaned = log_line.strip()
                if cleaned:
                    # Extract just the message part
                    if ']' in cleaned:
                        message = cleaned.split(']', 1)[-1].strip()
                    else:
                        message = cleaned
                    print(f"  {message[:75]}")
        print()
        
        # Footer
        print("=" * 80)
        print("Press Ctrl+C to exit monitor (training will continue)")
        print("Refreshing every 5 seconds...")
        
        time.sleep(5)

def start_training():
    """Start the weekend training if not running"""
    status = get_training_status()
    
    if status["running"]:
        print("✅ Training is already running!")
        return True
    
    print("Starting weekend training...")
    
    # Create auto-start script
    with open("auto_start_training.sh", 'w') as f:
        f.write("#!/bin/bash\necho 'y' | python3 weekend_training_pipeline.py > weekend_training.out 2>&1 &")
    
    os.chmod("auto_start_training.sh", 0o755)
    
    # Start training
    subprocess.Popen(["./auto_start_training.sh"])
    
    time.sleep(3)
    
    # Check if started
    result = subprocess.run(
        ["pgrep", "-f", "weekend_training_pipeline.py"],
        capture_output=True
    )
    
    if result.returncode == 0:
        print("✅ Training started successfully!")
        return True
    else:
        print("❌ Failed to start training")
        return False

def main():
    print("\n🚀 FIT Intelligence Training Monitor\n")
    print("1. Start training and monitor")
    print("2. Just monitor existing training")
    print("3. Check status once and exit")
    
    choice = input("\nChoice (1/2/3): ").strip()
    
    if choice == "1":
        if start_training():
            time.sleep(5)
            display_dashboard()
    elif choice == "2":
        display_dashboard()
    elif choice == "3":
        status = get_training_status()
        print(f"\nStatus: {'RUNNING' if status['running'] else 'IDLE'}")
        print(f"Iteration: {status['current_iteration']}/20")
        print(f"Best Model: {status['best_model']} ({status['best_score']:.1f}%)" if status['best_model'] else "No models yet")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Monitor stopped. Training continues in background.")
        print("Run this script again to check progress.")