# 🚀 Quick Deployment Guide

## 📋 Pre-Deployment Checklist

✅ **Files Ready:**
- `Dockerfile` - Docker image definition
- `handler.py` - RunPod serverless handler  
- `wan2.2i2v.json` - ComfyUI workflow
- `requirements.txt` - Python dependencies
- `build.sh` - Build script
- `deploy.sh` - Deployment script
- `test_endpoint.py` - Testing script

## 🔧 Step 1: Build Docker Image

```bash
# Make scripts executable
chmod +x build.sh deploy.sh test_endpoint.py

# Build the Docker image
./build.sh
```

Expected output:
```
🚀 Building WAN 2.2 I2V Docker Image
====================================
✅ All required files found
🔨 Building Docker image...
🎉 Build completed successfully!
```

## 📤 Step 2: Deploy to Docker Hub

```bash
# Deploy to Docker Hub (replace 'yourusername' with your Docker Hub username)
./deploy.sh yourusername
```

This will:
1. Login to Docker Hub
2. Tag the image as `yourusername/wan22-i2v:latest`
3. Push to Docker Hub
4. Provide RunPod deployment instructions

## 🌐 Step 3: Deploy on RunPod

1. **Go to [RunPod Console](https://console.runpod.io/)**
2. **Navigate to Serverless > New Endpoint**
3. **Configure:**
   - **Container Image**: `yourusername/wan22-i2v:latest`
   - **Container Registry Credentials**: Your Docker Hub credentials
   - **GPU**: A100 40GB or H100 (recommended)
   - **Container Disk**: 50GB+
   - **Network Volume**: Attach your existing volume (optional)
   - **Environment Variables**: None required

4. **Click "Deploy"**

## 🧪 Step 4: Test Your Endpoint

```bash
# Test the endpoint (replace with your actual values)
python test_endpoint.py \
  https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run \
  YOUR_API_KEY \
  path/to/test_image.jpg
```

Expected output:
```
🧪 Testing WAN 2.2 I2V Endpoint
📤 Encoding image...
✅ Image encoded
🚀 Submitting job...
✅ Job submitted successfully!
⏳ Polling job status...
📊 Status: IN_PROGRESS
🎉 Success! Video saved to: test_output_video.mp4
```

## 🎯 API Usage Example

```python
import requests
import base64

# Your endpoint details
endpoint_url = "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run"
api_key = "YOUR_API_KEY"

# Encode image
with open("image.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

# Submit job
payload = {
    "input": {
        "prompt": "A person walking naturally",
        "negative_prompt": "static, blurry, low quality",
        "image_base64": image_base64,
        "width": 640,
        "height": 640,
        "length": 81,
        "steps": 4,
        "cfg": 1.0,
        "seed": 42
    }
}

response = requests.post(
    endpoint_url,
    headers={"Authorization": f"Bearer {api_key}"},
    json=payload
)

print(response.json())
```

## ⚡ Optimized Parameters

### Lightning LoRA (Fast & High Quality)
```json
{
  "steps": 4,
  "cfg": 1.0,
  "width": 640,
  "height": 640,
  "length": 81
}
```
- **Time**: ~2 minutes
- **VRAM**: ~24GB
- **Quality**: High

### Standard Quality (Slower but Higher Quality)
```json
{
  "steps": 10,
  "cfg": 7.5,
  "width": 512,
  "height": 768,
  "length": 81
}
```
- **Time**: ~5 minutes  
- **VRAM**: ~32GB
- **Quality**: Very High

## 🐛 Troubleshooting

### Build Issues:
- **Docker not found**: Install Docker Desktop
- **Permission denied**: Run `chmod +x build.sh`
- **Out of disk space**: Free up space or use Docker cleanup

### Deployment Issues:
- **Docker Hub login failed**: Check credentials
- **Push failed**: Verify repository exists and you have push access
- **Image too large**: Check .dockerignore is working

### RunPod Issues:
- **Container failed to start**: Check logs in RunPod console
- **Out of memory**: Use A100 40GB+ GPU
- **Slow startup**: First run downloads models (~10GB)

### Generation Issues:
- **"Node not found"**: Workflow file corrupted, re-deploy
- **Out of VRAM**: Reduce length/resolution or use larger GPU
- **Poor quality**: Adjust CFG scale and steps

## 📊 Expected Performance

| GPU | Resolution | Frames | Time | VRAM |
|-----|------------|--------|------|------|
| A100 40GB | 640×640 | 81 | ~2 min | 24GB |
| A100 80GB | 768×768 | 81 | ~3 min | 32GB |
| H100 | 640×640 | 81 | ~1 min | 20GB |

## 🎉 Success Indicators

✅ **Build Success**: Image tagged and ready
✅ **Deploy Success**: Image pushed to Docker Hub  
✅ **RunPod Success**: Endpoint shows "Ready" status
✅ **Test Success**: Video generated and saved locally

Your WAN 2.2 I2V serverless is now ready for production! 🎬✨
