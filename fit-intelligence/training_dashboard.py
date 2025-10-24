#!/usr/bin/env python3
"""
Real-time Training Dashboard for Weekend Training
Shows progress, metrics, and model performance
"""

from flask import Flask, render_template, jsonify
import json
import os
from pathlib import Path
from datetime import datetime
import subprocess

app = Flask(__name__)

@app.route('/')
def dashboard():
    """Main dashboard view"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>FIT Intelligence Training Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        h1 {
            margin: 0;
            color: #333;
            font-size: 2.5em;
        }
        .subtitle {
            color: #666;
            margin-top: 10px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .card h2 {
            margin-top: 0;
            color: #667eea;
            font-size: 1.3em;
        }
        .metric {
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
            margin: 10px 0;
        }
        .label {
            color: #999;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #f0f0f0;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        .model-list {
            max-height: 400px;
            overflow-y: auto;
        }
        .model-item {
            padding: 15px;
            background: #f8f9fa;
            margin: 10px 0;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .model-name {
            font-weight: bold;
            color: #333;
        }
        .model-score {
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
        }
        .best-model {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.8em;
            letter-spacing: 1px;
        }
        .status.running {
            background: #4caf50;
            color: white;
        }
        .status.stopped {
            background: #f44336;
            color: white;
        }
        .status.idle {
            background: #ff9800;
            color: white;
        }
        .chart {
            margin-top: 20px;
            height: 300px;
        }
        .log-viewer {
            background: #2d2d2d;
            color: #f0f0f0;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            max-height: 300px;
            overflow-y: auto;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.3s;
        }
        .refresh-btn:hover {
            background: #5a67d8;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 FIT Intelligence Training Dashboard</h1>
            <div class="subtitle">Weekend Training Pipeline - Real-time Monitoring</div>
            <button class="refresh-btn" onclick="refreshData()">Refresh</button>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>Training Status</h2>
                <div id="status" class="status running">RUNNING</div>
                <div class="label">Current Iteration</div>
                <div id="iteration" class="metric">-</div>
                <div class="label">Elapsed Time</div>
                <div id="elapsed" class="metric">-</div>
            </div>
            
            <div class="card">
                <h2>Best Model</h2>
                <div class="label">Model Name</div>
                <div id="best-model" class="metric" style="font-size: 1.5em">-</div>
                <div class="label">Accuracy</div>
                <div id="best-score" class="metric">-</div>
            </div>
            
            <div class="card">
                <h2>Training Progress</h2>
                <div class="progress-bar">
                    <div id="progress" class="progress-fill" style="width: 0%">0%</div>
                </div>
                <div class="label">Examples Processed</div>
                <div id="examples" class="metric">0</div>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>Model Performance Over Time</h2>
                <canvas id="performanceChart"></canvas>
            </div>
            
            <div class="card">
                <h2>Trained Models</h2>
                <div id="model-list" class="model-list">
                    <!-- Models will be added here -->
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>Training Log</h2>
            <div id="log" class="log-viewer">
                Loading logs...
            </div>
        </div>
    </div>
    
    <script>
        let performanceChart;
        
        function initChart() {
            const ctx = document.getElementById('performanceChart').getContext('2d');
            performanceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Accuracy (%)',
                        data: [],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }
        
        async function refreshData() {
            try {
                const response = await fetch('/api/training-status');
                const data = await response.json();
                
                // Update status
                document.getElementById('status').textContent = data.status;
                document.getElementById('status').className = 'status ' + data.status.toLowerCase();
                
                // Update metrics
                document.getElementById('iteration').textContent = data.current_iteration || '-';
                document.getElementById('elapsed').textContent = data.elapsed || '-';
                document.getElementById('best-model').textContent = data.best_model || '-';
                document.getElementById('best-score').textContent = data.best_score ? data.best_score.toFixed(1) + '%' : '-';
                document.getElementById('examples').textContent = data.examples_processed || '0';
                
                // Update progress
                const progress = data.progress || 0;
                document.getElementById('progress').style.width = progress + '%';
                document.getElementById('progress').textContent = progress + '%';
                
                // Update model list
                const modelList = document.getElementById('model-list');
                modelList.innerHTML = '';
                if (data.models) {
                    data.models.forEach(model => {
                        const item = document.createElement('div');
                        item.className = 'model-item';
                        if (model.is_best) item.classList.add('best-model');
                        item.innerHTML = `
                            <span class="model-name">${model.name}</span>
                            <span class="model-score">${model.score.toFixed(1)}%</span>
                        `;
                        modelList.appendChild(item);
                    });
                }
                
                // Update chart
                if (data.performance_history && performanceChart) {
                    performanceChart.data.labels = data.performance_history.map(p => p.iteration);
                    performanceChart.data.datasets[0].data = data.performance_history.map(p => p.score);
                    performanceChart.update();
                }
                
                // Update log
                if (data.recent_logs) {
                    document.getElementById('log').innerHTML = data.recent_logs.join('<br>');
                    document.getElementById('log').scrollTop = document.getElementById('log').scrollHeight;
                }
                
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }
        
        // Initialize
        initChart();
        refreshData();
        
        // Auto-refresh every 5 seconds
        setInterval(refreshData, 5000);
    </script>
</body>
</html>
'''

@app.route('/api/training-status')
def training_status():
    """Get current training status"""
    
    status_data = {
        "status": "IDLE",
        "current_iteration": 0,
        "elapsed": "0:00:00",
        "best_model": None,
        "best_score": 0,
        "progress": 0,
        "examples_processed": 0,
        "models": [],
        "performance_history": [],
        "recent_logs": []
    }
    
    # Check if training is running
    result = subprocess.run(
        ["pgrep", "-f", "weekend_training_pipeline.py"],
        capture_output=True
    )
    
    if result.returncode == 0:
        status_data["status"] = "RUNNING"
    
    # Read latest checkpoint
    checkpoint_dir = Path("./weekend_checkpoints")
    if checkpoint_dir.exists():
        checkpoints = sorted(checkpoint_dir.glob("checkpoint_*.json"))
        if checkpoints:
            # Get latest checkpoint
            with open(checkpoints[-1], 'r') as f:
                latest = json.load(f)
                status_data["current_iteration"] = latest.get("iteration", 0)
                status_data["elapsed"] = latest.get("elapsed", "0:00:00")
                
            # Get all checkpoints for history
            for cp_file in checkpoints:
                with open(cp_file, 'r') as f:
                    cp = json.load(f)
                    status_data["performance_history"].append({
                        "iteration": cp.get("iteration", 0),
                        "score": cp.get("score", 0)
                    })
                    
                    # Track models
                    model_info = {
                        "name": cp.get("model_name", ""),
                        "score": cp.get("score", 0),
                        "is_best": False
                    }
                    status_data["models"].append(model_info)
            
            # Find best model
            if status_data["models"]:
                best = max(status_data["models"], key=lambda x: x["score"])
                best["is_best"] = True
                status_data["best_model"] = best["name"]
                status_data["best_score"] = best["score"]
    
    # Calculate progress
    max_iterations = 20
    status_data["progress"] = min(100, (status_data["current_iteration"] / max_iterations) * 100)
    status_data["examples_processed"] = status_data["current_iteration"] * 4007  # train examples per iteration
    
    # Read recent logs
    log_files = sorted(Path(".").glob("weekend_training_*.log"))
    if log_files:
        with open(log_files[-1], 'r') as f:
            lines = f.readlines()
            status_data["recent_logs"] = [line.strip() for line in lines[-20:]]  # Last 20 lines
    
    return jsonify(status_data)

if __name__ == '__main__':
    print("Starting Training Dashboard on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)