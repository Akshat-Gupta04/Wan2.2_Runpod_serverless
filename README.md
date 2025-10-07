# WAN 2.2 Image-to-Video RunPod Serverless

🎬 **Production-ready Docker container for WAN 2.2 Image-to-Video generation on RunPod Serverless**

Generate high-quality videos from static images using the latest WAN 2.2 model with Lightning LoRA optimization.

## ✨ Features

- **⚡ Lightning LoRA Optimized**: 4-step generation (2x faster than standard)
- **🎯 Negative Prompt Support**: Better control over unwanted elements
- **📱 Mobile Optimized**: Default 640×640 resolution
- **🔧 RunPod Ready**: Pre-configured for serverless deployment
- **🌐 Network Volume Support**: S3-compatible storage integration
- **🎨 High Quality**: Optimized parameters for best results

## 🚀 Quick Deploy to RunPod

### 1. Build and Push Docker Image

```bash
# Clone this repository
git clone <your-repo-url>
cd generate_video

# Build the Docker image
./build.sh

# Tag for your registry
docker tag wan22-i2v:latest your-dockerhub-username/wan22-i2v:latest

# Push to Docker Hub
docker push your-dockerhub-username/wan22-i2v:latest
```

### 2. Deploy on RunPod

1. **Go to [RunPod Console](https://console.runpod.io/) > Serverless**
2. **Click "New Endpoint"**
3. **Configure:**
   - **Container Image**: `your-dockerhub-username/wan22-i2v:latest`
   - **Container Registry Credentials**: Your Docker Hub credentials
   - **GPU**: A100 40GB or H100 (recommended)
   - **Container Disk**: 50GB+
   - **Network Volume**: Optional (for persistent storage)

### 3. Test Your Endpoint

```python
import requests
import base64

# Your RunPod endpoint URL
endpoint_url = "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run"

# Encode your image
with open("test_image.jpg", "rb") as f:
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
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json=payload
)

print(response.json())
```

## 📋 API Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | required | Positive prompt describing desired motion |
| `negative_prompt` | string | optional | What to avoid in the video |
| `image_base64` | string | required* | Base64 encoded input image |
| `image_path` | string | required* | Path to image in network volume |
| `width` | integer | 640 | Video width (512-1024) |
| `height` | integer | 640 | Video height (512-1024) |
| `length` | integer | 81 | Video length in frames (16-81) |
| `steps` | integer | 4 | Sampling steps (4-10) |
| `cfg` | float | 1.0 | CFG scale (1.0-2.0) |
| `seed` | integer | 42 | Random seed (0-999999) |

*Either `image_base64` or `image_path` is required

## 🎯 Optimized Settings

### **Lightning LoRA (Recommended)**
```json
{
  "steps": 4,
  "cfg": 1.0,
  "width": 640,
  "height": 640
}
```
- **Generation time**: ~2 minutes
- **Quality**: High
- **VRAM usage**: ~24GB

### **Standard Quality**
```json
{
  "steps": 10,
  "cfg": 7.5,
  "width": 512,
  "height": 768
}
```
- **Generation time**: ~5 minutes
- **Quality**: Very High
- **VRAM usage**: ~32GB

## 🔧 Local Development

### Prerequisites
- Docker installed
- NVIDIA GPU with 24GB+ VRAM
- CUDA 12.1+ drivers

### Build and Test Locally

```bash
# Build the image
./build.sh

# Run locally
docker run --rm --gpus all -p 8000:8000 wan22-i2v:latest

# Test with curl
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "A person walking naturally",
      "image_base64": "YOUR_BASE64_IMAGE"
    }
  }'
```

## 📁 Project Structure

```
generate_video/
├── Dockerfile              # Docker image definition
├── handler.py              # RunPod serverless handler
├── wan2.2i2v.json         # ComfyUI workflow
├── build.sh               # Build script
├── README.md              # This file
└── .gitignore             # Git ignore rules
```

## 🔄 Workflow Details

The `wan2.2i2v.json` workflow uses:

- **WAN 2.2 Models**: Latest image-to-video diffusion models
- **Lightning LoRA**: 4-step optimization for speed
- **Dual Sampling**: High and low noise for quality
- **Smart Encoding**: Optimized text and image encoding

### Key Nodes:
- **Node 97**: Image input
- **Node 93**: Positive prompt encoding
- **Node 89**: Negative prompt encoding
- **Node 98**: Video generation parameters
- **Node 86/85**: Dual sampling stages

## 🐛 Troubleshooting

### Common Issues:

**"Out of memory" errors:**
- Reduce video length: `"length": 49`
- Use smaller resolution: `"width": 512, "height": 512`
- Ensure A100 40GB+ GPU

**"Node not found" errors:**
- Verify `wan2.2i2v.json` is valid
- Check ComfyUI model downloads

**Slow generation:**
- Use Lightning LoRA settings: `"steps": 4, "cfg": 1.0`
- Check GPU utilization in RunPod console

### Debug Mode:

Enable verbose logging:
```bash
docker run --rm --gpus all -p 8000:8000 -e DEBUG=1 wan22-i2v:latest
```

## 📊 Performance Benchmarks

| GPU | Resolution | Length | Steps | Time | VRAM |
|-----|------------|--------|-------|------|------|
| A100 40GB | 640×640 | 81 | 4 | ~2 min | 24GB |
| A100 80GB | 768×768 | 81 | 4 | ~3 min | 32GB |
| H100 | 640×640 | 81 | 4 | ~1 min | 20GB |

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Test your changes locally
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🔗 Related Projects

- [WAN 2.2 ComfyUI](https://github.com/Comfy-Org/Wan_2.2_ComfyUI_Repackaged)
- [RunPod Documentation](https://docs.runpod.io/)
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)

---

**Ready to generate amazing videos from your images!** 🎬✨
