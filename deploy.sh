#!/bin/bash

# Deployment script for WAN 2.2 I2V to Docker Hub

set -e

echo "🚀 WAN 2.2 I2V Deployment Script"
echo "================================"

# Configuration
IMAGE_NAME="wan22-i2v"
TAG="latest"

# Check if Docker Hub username is provided
if [ -z "$1" ]; then
    echo "❌ Error: Docker Hub username required"
    echo "Usage: ./deploy.sh <dockerhub-username>"
    echo "Example: ./deploy.sh myusername"
    exit 1
fi

DOCKERHUB_USERNAME="$1"
FULL_IMAGE_NAME="$DOCKERHUB_USERNAME/$IMAGE_NAME:$TAG"

echo "📋 Configuration:"
echo "   Local image: $IMAGE_NAME:$TAG"
echo "   Remote image: $FULL_IMAGE_NAME"
echo ""

# Check if local image exists
if ! docker images "$IMAGE_NAME:$TAG" --format "{{.Repository}}:{{.Tag}}" | grep -q "$IMAGE_NAME:$TAG"; then
    echo "❌ Error: Local image $IMAGE_NAME:$TAG not found"
    echo "Please build the image first:"
    echo "   ./build.sh"
    exit 1
fi

echo "✅ Local image found"

# Login to Docker Hub
echo ""
echo "🔐 Logging in to Docker Hub..."
echo "Please enter your Docker Hub credentials:"
docker login

if [ $? -ne 0 ]; then
    echo "❌ Docker Hub login failed"
    exit 1
fi

echo "✅ Docker Hub login successful"

# Tag the image
echo ""
echo "🏷️  Tagging image..."
docker tag "$IMAGE_NAME:$TAG" "$FULL_IMAGE_NAME"

if [ $? -eq 0 ]; then
    echo "✅ Image tagged successfully"
else
    echo "❌ Failed to tag image"
    exit 1
fi

# Push to Docker Hub
echo ""
echo "📤 Pushing to Docker Hub..."
echo "This may take several minutes..."
docker push "$FULL_IMAGE_NAME"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Deployment successful!"
    echo ""
    echo "📊 Image Details:"
    docker images "$FULL_IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    echo ""
    echo "🚀 Next Steps:"
    echo "1. Go to RunPod Console: https://console.runpod.io/"
    echo "2. Navigate to Serverless > New Endpoint"
    echo "3. Use container image: $FULL_IMAGE_NAME"
    echo "4. Configure GPU: A100 40GB or H100"
    echo "5. Set container disk: 50GB+"
    echo "6. Attach network volume (optional)"
    echo ""
    echo "🔗 Your image is now available at:"
    echo "   https://hub.docker.com/r/$DOCKERHUB_USERNAME/$IMAGE_NAME"
    echo ""
else
    echo "❌ Failed to push image to Docker Hub"
    exit 1
fi
