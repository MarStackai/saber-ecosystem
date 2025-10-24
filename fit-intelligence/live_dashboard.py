#!/usr/bin/env python3
"""
Live Terminal Dashboard for Weekend Training
Real-time monitoring with auto-refresh
"""

import json
import os
import time
import subprocess
from pathlib import Path
from datetime import datetime

def get_terminal_size():
    """Get terminal dimensions"""
    try:
        rows, cols = os.popen('stty size', 'r').read().split()
        return int(rows), int(cols)
    except:
        return 24, 80

def create_progress_bar(percent, width=50):
    """Create a visual progress bar"""
    filled = int(width * percent / 100)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {percent:.1f}%"

def format_time(seconds):
    """Format seconds into readable time"""
    if isinstance(seconds, str):
        return seconds
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def get_live_status():
    """Get current training status"""
    status = {
        "running": False,
        "iteration": 0,
        "total_iterations": 20,
        "best_model": None,
        "best_score": 0,
        "current_model": None,
        "current_score": 0,
        "models": [],
        "elapsed": "00:00:00",
        "eta": "Unknown",
        "recent_activity": []
    }
    
    # Check if training is running
    result = subprocess.run(["pgrep", "-f", "weekend_training_pipeline.py"], capture_output=True)
    status["running"] = result.returncode == 0
    
    # Read checkpoints
    checkpoint_dir = Path("./weekend_checkpoints")
    if checkpoint_dir.exists():
        checkpoints = sorted(checkpoint_dir.glob("checkpoint_*.json"))
        if checkpoints:
            # Get latest checkpoint
            with open(checkpoints[-1], 'r') as f:
                latest = json.load(f)
                status["iteration"] = latest.get("iteration", 0)
                status["elapsed"] = latest.get("elapsed", "00:00:00")
                status["current_model"] = latest.get("model_name", "")
                status["current_score"] = latest.get("score", 0)
            
            # Get all models for history
            for cp_file in checkpoints:
                with open(cp_file, 'r') as f:
                    cp = json.load(f)
                    status["models"].append({
                        "name": cp.get("model_name", ""),
                        "score": cp.get("score", 0),
                        "iteration": cp.get("iteration", 0)
                    })
            
            # Find best model
            if status["models"]:
                best = max(status["models"], key=lambda x: x["score"])
                status["best_model"] = best["name"]
                status["best_score"] = best["score"]
    
    # Calculate ETA
    if status["iteration"] > 0:
        # Parse elapsed time
        try:
            if ":" in str(status["elapsed"]):
                parts = str(status["elapsed"]).split(":")
                if len(parts) >= 3:
                    elapsed_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
                else:
                    elapsed_seconds = 0
            else:
                elapsed_seconds = 0
            
            if elapsed_seconds > 0 and status["iteration"] > 0:
                seconds_per_iteration = elapsed_seconds / status["iteration"]
                remaining_iterations = status["total_iterations"] - status["iteration"]
                eta_seconds = seconds_per_iteration * remaining_iterations
                status["eta"] = format_time(eta_seconds)
        except:
            status["eta"] = "Calculating..."
    
    # Read latest log
    log_files = sorted(Path(".").glob("weekend_training_*.log"))
    if log_files:
        with open(log_files[-1], 'r') as f:
            lines = f.readlines()
            # Get last 10 meaningful lines
            for line in lines[-20:]:
                if line.strip() and not line.startswith("[2025"):
                    # Extract message part
                    if "]" in line:
                        msg = line.split("]", 1)[-1].strip()
                    else:
                        msg = line.strip()
                    if msg and len(msg) > 5:
                        status["recent_activity"].append(msg[:80])
            
            # Keep only last 5 activities
            status["recent_activity"] = status["recent_activity"][-5:]
    
    return status

def draw_dashboard():
    """Draw the live dashboard"""
    rows, cols = get_terminal_size()
    
    while True:
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')
        
        status = get_live_status()
        
        # Header
        print("╔" + "═" * (cols - 2) + "╗")
        title = "🚀 FIT INTELLIGENCE WEEKEND TRAINING DASHBOARD 🚀"
        padding = (cols - len(title) - 2) // 2
        print("║" + " " * padding + title + " " * (cols - len(title) - padding - 2) + "║")
        print("╠" + "═" * (cols - 2) + "╣")
        
        # Status line
        if status["running"]:
            status_text = f"║ 🟢 TRAINING ACTIVE | Iteration {status['iteration']}/{status['total_iterations']} | Elapsed: {status['elapsed']} | ETA: {status['eta']}"
        else:
            status_text = f"║ 🔴 TRAINING STOPPED | Last Iteration: {status['iteration']}/{status['total_iterations']}"
        print(status_text + " " * (cols - len(status_text) - 1) + "║")
        
        print("╠" + "═" * (cols - 2) + "╣")
        
        # Progress bar
        progress = (status["iteration"] / status["total_iterations"]) * 100
        bar = create_progress_bar(progress, width=cols - 15)
        print(f"║ Progress: {bar}" + " " * (cols - len(bar) - 12) + "║")
        
        print("╠" + "═" * (cols - 2) + "╣")
        
        # Current and Best Model
        print(f"║ {'CURRENT MODEL':30} │ {'BEST MODEL':30}" + " " * (cols - 64) + "║")
        print(f"║ {'-' * 30} │ {'-' * 30}" + " " * (cols - 64) + "║")
        
        current_name = status.get("current_model", "None")[:28] if status.get("current_model") else "None"
        best_name = status.get("best_model", "None")[:28] if status.get("best_model") else "None"
        print(f"║ {current_name:30} │ {best_name:30}" + " " * (cols - 64) + "║")
        
        current_score = f"{status.get('current_score', 0):.1f}%" if status.get('current_score') else "0.0%"
        best_score = f"{status.get('best_score', 0):.1f}%" if status.get('best_score') else "0.0%"
        print(f"║ Accuracy: {current_score:19} │ Accuracy: {best_score:19}" + " " * (cols - 64) + "║")
        
        print("╠" + "═" * (cols - 2) + "╣")
        
        # Model Performance History (last 5)
        print(f"║ {'MODEL PERFORMANCE HISTORY':^{cols-4}}║")
        print(f"║ {'-' * (cols - 4):^{cols-4}}║")
        
        if status["models"]:
            # Show last 5 models
            for model in status["models"][-5:]:
                score_bar = "▓" * int(model["score"] / 2)  # Each block = 2%
                line = f"║ Iter {model['iteration']:2d}: {model['name'][:20]:20} {model['score']:5.1f}% {score_bar}"
                print(line + " " * (cols - len(line) - 1) + "║")
        else:
            print(f"║ {'No models trained yet':^{cols-4}}║")
        
        # Fill remaining space
        models_shown = min(5, len(status["models"]))
        for _ in range(5 - models_shown):
            print("║" + " " * (cols - 2) + "║")
        
        print("╠" + "═" * (cols - 2) + "╣")
        
        # Recent Activity
        print(f"║ {'RECENT ACTIVITY':^{cols-4}}║")
        print(f"║ {'-' * (cols - 4):^{cols-4}}║")
        
        if status["recent_activity"]:
            for activity in status["recent_activity"]:
                line = f"║ • {activity[:cols-7]}"
                print(line + " " * (cols - len(line) - 1) + "║")
        else:
            print(f"║ {'Waiting for activity...':^{cols-4}}║")
        
        # Fill remaining space
        for _ in range(5 - len(status["recent_activity"])):
            print("║" + " " * (cols - 2) + "║")
        
        # Footer
        print("╠" + "═" * (cols - 2) + "╣")
        footer = "Press Ctrl+C to exit dashboard (training continues) | Auto-refresh: 5s"
        print(f"║ {footer:^{cols-4}}║")
        print("╚" + "═" * (cols - 2) + "╝")
        
        # Sleep before refresh
        time.sleep(5)

def main():
    """Run the live dashboard"""
    print("\n🎯 Starting Live Training Dashboard...\n")
    print("This dashboard will auto-refresh every 5 seconds")
    print("Press Ctrl+C to exit (training will continue in background)")
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    try:
        draw_dashboard()
    except KeyboardInterrupt:
        print("\n\n✅ Dashboard closed. Training continues in background.")
        print("\nTo check status again, run:")
        print("  python3 live_dashboard.py")
        print("\nTo view logs:")
        print("  tail -f weekend_training_*.log")

if __name__ == "__main__":
    main()