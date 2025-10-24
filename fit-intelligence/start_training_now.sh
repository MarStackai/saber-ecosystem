#!/bin/bash
# Start weekend training immediately

echo "Starting FIT Intelligence Weekend Training..."
echo "This will run for up to 48 hours"
echo ""

# Auto-confirm and run in background
echo "y" | python3 weekend_training_pipeline.py > weekend_training.out 2>&1 &

TRAINING_PID=$!
echo "Training started with PID: $TRAINING_PID"
echo "Log file: weekend_training.out"
echo ""
echo "Monitor progress with:"
echo "  tail -f weekend_training.out"
echo "  OR"
echo "  echo '3' | python3 simple_training_monitor.py"