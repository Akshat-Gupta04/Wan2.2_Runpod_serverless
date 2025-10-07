#!/bin/bash

# Build script for WAN 2.2 I2V Docker image

set -e

echo "🚀 Building WAN 2.2 I2V Docker Image"
echo "===================================="

# Configuration
IMAGE_NAME="wan22-i2v"
TAG="latest"
DOCKERFILE="Dockerfile"

# Check if files exist
echo "📋 Checking required files..."

if [ ! -f "$DOCKERFILE" ]; then
    echo "❌ Error: $DOCKERFILE not found"
    exit 1
fi

if [ ! -f "wan2.2i2v.json" ]; then
    echo "❌ Error: wan2.2i2v.json workflow not found"
    exit 1
fi

if [ ! -f "handler.py" ]; then
    echo "❌ Error: handler.py not found"
    exit 1
fi

echo "✅ All required files found"

# Build the Docker image
echo ""
echo "🔨 Building Docker image..."
echo "Image: $IMAGE_NAME:$TAG"
echo "Dockerfile: $DOCKERFILE"
echo ""

docker build -f "$DOCKERFILE" -t "$IMAGE_NAME:$TAG" .

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Build completed successfully!"
    echo ""
    echo "📊 Image Details:"
    docker images "$IMAGE_NAME:$TAG" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    
    echo ""
    echo "🚀 Next Steps:"
    echo "1. Test locally:"
    echo "   docker run --rm -p 8000:8000 $IMAGE_NAME:$TAG"
    echo ""
    echo "2. Push to registry:"
    echo "   docker tag $IMAGE_NAME:$TAG your-registry/$IMAGE_NAME:$TAG"
    echo "   docker push your-registry/$IMAGE_NAME:$TAG"
    echo ""
    echo "3. Deploy to RunPod:"
    echo "   - Go to RunPod Console > Serverless"
    echo "   - Create new endpoint"
    echo "   - Use image: your-registry/$IMAGE_NAME:$TAG"
    echo "   - Attach network volume"
    echo "   - Set GPU: A100 or H100 (recommended)"
    echo ""
else
    echo "❌ Build failed!"
    exit 1
fi
