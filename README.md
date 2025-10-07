# RunPod Wan2.2 I2V Serverless with Network Volume

> **High-quality video generation using Wan2.2 14B model with RunPod Network Volume integration**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![RunPod](https://img.shields.io/badge/Platform-RunPod-purple.svg)](https://runpod.io)

## About the Project

**RunPod Wan2.2 I2V Serverless** is a streamlined serverless solution that transforms static images into dynamic, high-quality videos using the Wan2.2 14B model. This setup is specifically configured to work with RunPod Network Volumes, providing efficient model storage and access.

**Key Configuration:**
- **Network Volume ID**: `q596vcx1ln`
- **Endpoint URL**: `https://s3api-eu-ro-1.runpod.io`
- **Workflow**: `video_wan2_2_14B_i2v.json` (14B parameter model)
- **Model Storage**: All models accessed from network volume

## ✨ Key Features

- **🎬 Wan2.2 14B I2V**: Uses the powerful 14B parameter Wan2.2 model for high-quality image-to-video generation
- **💾 Network Volume Integration**: Efficient model storage and access via RunPod Network Volumes
- **⚡ Optimized Workflow**: Single, streamlined workflow (`video_wan2_2_14B_i2v.json`) for consistent results
- **🔧 ComfyUI Backend**: Built on ComfyUI's robust workflow management system
- **☁️ Serverless Architecture**: Optimized for RunPod's serverless environment with automatic scaling
- **📦 Pre-configured Setup**: Ready-to-use with your existing network volume containing all required models

## 🚀 Template Components

This comprehensive template includes all essential components for seamless Wan2.2 deployment:

| Component | Description |
|-----------|-------------|
| **Dockerfile** | Environment configuration and dependency management |
| **handler.py** | Core serverless request processing logic |
| **entrypoint.sh** | Worker initialization and startup procedures |
| **Workflow Files** | Multiple ComfyUI workflow configurations for different use cases |

## 📋 API Reference

### Input Parameters

The API accepts a comprehensive set of parameters for fine-tuned video generation. Images can be provided via **file path** or **Base64 encoding**.

#### 🖼️ Image Input (Choose One Method)

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image_path` | `string` | No | - | Path to the input image file (from network volume or local) |
| `image_base64` | `string` | No | - | Base64 encoded image string |

> **📝 Note**: Either `image_path` or `image_base64` must be provided. Images from network volume should use full paths.

#### 🎬 Video Generation Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | `string` | No | `"A beautiful scene with natural motion"` | Descriptive text for video generation |
| `negative_prompt` | `string` | No | `"bad quality, static, blurry"` | Negative prompt to avoid unwanted elements |
| `seed` | `integer` | No | `42` | Random seed for reproducible results |
| `cfg` | `float` | No | `7.5` | CFG scale for generation control |
| `width` | `integer` | No | `640` | Output video width (pixels) |
| `height` | `integer` | No | `640` | Output video height (pixels) |
| `length` | `integer` | No | `81` | Video length in frames |
| `steps` | `integer` | No | `20` | Number of denoising steps |

### 💡 Usage Examples

#### Basic Video Generation with Image Path
```json
{
  "input": {
    "image_path": "/runpod-volume/images/portrait.jpg",
    "prompt": "A person walking naturally through a peaceful garden",
    "negative_prompt": "static, blurry, low quality",
    "seed": 12345,
    "cfg": 7.5,
    "width": 640,
    "height": 640,
    "length": 81,
    "steps": 20
  }
}
```

#### Video Generation with Base64 Image
```json
{
  "input": {
    "image_base64": "/9j/4AAQSkZJRgABAQAAAQABAAD...",
    "prompt": "A beautiful landscape with gentle motion",
    "seed": 42,
    "cfg": 8.0,
    "width": 512,
    "height": 512
  }
}
```

#### Minimal Request (using defaults)
```json
{
  "input": {
    "image_path": "/runpod-volume/images/test.jpg"
  }
}
```

### 📤 Response Format

#### ✅ Success Response

Upon successful video generation, the API returns a JSON object containing the Base64-encoded video data.

| Parameter | Type | Description |
|-----------|------|-------------|
| `video` | `string` | Base64 encoded MP4 video file |

```json
{
  "video": "data:video/mp4;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT..."
}
```

#### ❌ Error Response

If processing fails, the API returns an error object with diagnostic information.

| Parameter | Type | Description |
|-----------|------|-------------|
| `error` | `string` | Detailed error description |

```json
{
  "error": "Failed to process video generation: Invalid image format"
}
```

## � Getting Started

### Quick Deployment

1. **Create RunPod Endpoint**: Deploy a new Serverless Endpoint using this repository as the template
2. **Wait for Build**: Allow the container to build and initialize (typically 5-10 minutes)
3. **Start Generating**: Submit HTTP POST requests to your active endpoint

### 📁 Network Volume Setup

Optimize performance and handle large files efficiently using RunPod's Network Volumes:

#### Setup Process
1. **Create Volume**: Set up a Network Volume (S3-based recommended) in your RunPod dashboard
2. **Connect to Endpoint**: Link the volume to your Serverless Endpoint configuration
3. **Upload Assets**: Transfer your images and LoRA models to the volume

#### File Organization
```
/your_volume/
├── images/
│   ├── portrait1.jpg
│   ├── landscape.png
│   └── ...
└── loras/
    ├── style_model_high.safetensors
    ├── style_model_low.safetensors
    └── ...
```

#### Path Specification
- **Images**: Use full paths (e.g., `"/my_volume/images/portrait.jpg"`)
- **LoRA Models**: Use filenames only (e.g., `"style_model_high.safetensors"`) - automatically searches `/loras/`

## 🔧 Workflow Architecture

### Single Workflow Design

This setup uses a single, optimized workflow: **`video_wan2_2_14B_i2v.json`**

**Key Features:**
- **Wan2.2 14B Model**: Uses both high-noise and low-noise 14B parameter models
- **Dual Processing Path**: Includes both standard and 4-step LoRA processing paths
- **Automatic Model Loading**: All models loaded from network volume automatically
- **Optimized Performance**: Streamlined for consistent, high-quality results

### Workflow Components

The workflow includes these essential processing nodes:

#### Core Processing Nodes
- **CLIP Text Encoding**: Advanced prompt processing with UMT5 XXL model
- **VAE Processing**: High-quality image encoding/decoding with Wan 2.1 VAE
- **WanImageToVideo**: Primary video generation engine with 14B parameters
- **Model Sampling**: SD3 sampling for optimal quality
- **Video Output**: Direct MP4 video generation

#### Model Integration
- **Diffusion Models**: High/low noise 14B models for different processing stages
- **LoRA Support**: Built-in 4-step lightning LoRA for faster generation
- **Network Volume Access**: All models accessed directly from your network volume

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 🙏 Acknowledgments

This project builds upon the excellent work of the following open-source projects:

- **[Wan2.2](https://github.com/Wan-Video/Wan2.2)**: Advanced AI model for image-to-video generation
- **[ComfyUI](https://github.com/comfyanonymous/ComfyUI)**: Powerful and modular stable diffusion GUI and backend
- **[ComfyUI-WanVideoWrapper](https://github.com/kijai/ComfyUI-WanVideoWrapper)**: ComfyUI integration for Wan video models
- **[RunPod](https://runpod.io)**: Serverless GPU infrastructure platform

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

**Developed by [Akshat Gupta](https://github.com/Akshat-Gupta04)** | **AI Enthusiast** 🎯
