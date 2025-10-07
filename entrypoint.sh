#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "=== RunPod Serverless Wan2.2 I2V Setup ==="

# Check if network volume is mounted
if [ -d "/runpod-volume" ]; then
    echo "✅ Network volume detected at /runpod-volume"

    # Check for required model directories
    required_dirs=("models/diffusion_models" "models/vae" "models/text_encoders" "models/loras")
    for dir in "${required_dirs[@]}"; do
        if [ -d "/runpod-volume/$dir" ]; then
            echo "✅ Found $dir in network volume"
        else
            echo "⚠️  Warning: $dir not found in network volume"
        fi
    done
else
    echo "⚠️  Warning: Network volume not mounted at /runpod-volume"
    echo "Models will need to be available locally or the workflow may fail"
fi

# Ensure ComfyUI input directory exists for image uploads
mkdir -p /ComfyUI/input

# Start ComfyUI in the background
echo "🚀 Starting ComfyUI server..."
python /ComfyUI/main.py --listen --use-sage-attention &

# Wait for ComfyUI to be ready
echo "⏳ Waiting for ComfyUI to be ready..."
max_wait=120  # Maximum 2 minutes wait
wait_count=0
while [ $wait_count -lt $max_wait ]; do
    if curl -s http://127.0.0.1:8188/ > /dev/null 2>&1; then
        echo "✅ ComfyUI is ready!"
        break
    fi
    echo "⏳ Waiting for ComfyUI... ($wait_count/$max_wait seconds)"
    sleep 2
    wait_count=$((wait_count + 2))
done

if [ $wait_count -ge $max_wait ]; then
    echo "❌ Error: ComfyUI failed to start within $max_wait seconds"
    exit 1
fi

# Start the handler in the foreground
echo "🎬 Starting Wan2.2 I2V handler..."
exec python handler.py