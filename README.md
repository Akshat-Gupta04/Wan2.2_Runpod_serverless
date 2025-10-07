# RunPod Image 2 Video using RunPod Serverless

> **Empowering high-quality video generation through cutting-edge AI and serverless deployment**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![RunPod](https://img.shields.io/badge/Platform-RunPod-purple.svg)](https://runpod.io)

[한국어 README 보기](README_kr.md)

## About the Project

**RunPod Image 2 Video** is a comprehensive serverless solution that transforms static images into dynamic, high-quality videos using advanced AI technology. Built specifically for the RunPod Serverless environment, this project leverages the power of [Wan2.2](https://github.com/Comfy-Org/Wan_2.2_ComfyUI_Repackaged) to generate videos with natural motion and realistic animations.

This template provides a complete, production-ready deployment solution that handles everything from image processing to video generation, all while maintaining optimal performance in a serverless architecture.

## ✨ Key Features

- **🎬 Image-to-Video Generation**: Transform static images into dynamic videos with natural motion and realistic animations
- **🎯 High-Quality Output**: Generate high-resolution videos with professional-grade visual quality
- **⚙️ Customizable Parameters**: Fine-tune video generation with comprehensive control over seed, dimensions, prompts, and more
- **🔧 ComfyUI Integration**: Built on ComfyUI's robust workflow management system for maximum flexibility
- **☁️ Serverless Architecture**: Optimized for RunPod's serverless environment with automatic scaling
- **🎨 LoRA Support**: Advanced LoRA model integration for enhanced customization capabilities

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
| `image_path` | `string` | No | `/example_image.png` | Local path to the input image file |
| `image_base64` | `string` | No | - | Base64 encoded image string |

#### 🎨 LoRA Configuration

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `lora_pairs` | `array` | No | `[]` | Array of LoRA model pairs for enhanced customization |

> **📝 Note**: LoRA models must be uploaded to the `/loras/` directory in your RunPod Network Volume. Model names in `lora_pairs` should match the filenames exactly.

#### LoRA Pair Structure

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `high` | `string` | Yes | - | High-quality LoRA model filename |
| `low` | `string` | Yes | - | Low-quality LoRA model filename |
| `high_weight` | `float` | No | `1.0` | Weight for high-quality LoRA |
| `low_weight` | `float` | No | `1.0` | Weight for low-quality LoRA |

#### 🎬 Video Generation Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | `string` | Yes | - | Descriptive text for video generation |
| `seed` | `integer` | Yes | - | Random seed for reproducible results |
| `cfg` | `float` | Yes | - | CFG scale for generation control |
| `width` | `integer` | Yes | - | Output video width (pixels) |
| `height` | `integer` | Yes | - | Output video height (pixels) |
| `length` | `integer` | No | `81` | Video length in frames |
| `steps` | `integer` | No | `10` | Number of denoising steps |

### 💡 Usage Examples

#### Basic Video Generation
```json
{
  "input": {
    "prompt": "A person walking naturally through a peaceful garden",
    "image_path": "/my_volume/portrait.jpg",
    "seed": 12345,
    "cfg": 7.5,
    "width": 512,
    "height": 512,
    "length": 81,
    "steps": 10
  }
}
```

#### Enhanced Generation with LoRA
```json
{
  "input": {
    "prompt": "A person walking naturally through a peaceful garden",
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...",
    "seed": 12345,
    "cfg": 7.5,
    "width": 512,
    "height": 512,
    "lora_pairs": [
      {
        "high": "style_enhancement_high.safetensors",
        "low": "style_enhancement_low.safetensors",
        "high_weight": 1.0,
        "low_weight": 0.8
      }
    ]
  }
}
```

#### Advanced Multi-LoRA Configuration
```json
{
  "input": {
    "prompt": "A person walking naturally through a peaceful garden",
    "image_path": "/my_volume/portrait.jpg",
    "seed": 12345,
    "cfg": 7.5,
    "width": 512,
    "height": 512,
    "lora_pairs": [
      {
        "high": "motion_style_high.safetensors",
        "low": "motion_style_low.safetensors",
        "high_weight": 1.0,
        "low_weight": 0.8
      },
      {
        "high": "lighting_enhance_high.safetensors",
        "low": "lighting_enhance_low.safetensors",
        "high_weight": 0.9,
        "low_weight": 0.7
      }
    ]
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

### Intelligent Workflow Selection

The template features **dynamic workflow selection** that automatically chooses the optimal configuration based on your LoRA requirements:

| LoRA Pairs | Workflow File | Description |
|------------|---------------|-------------|
| **0** | `wan22_nolora.json` | Standard image-to-video generation |
| **1** | `wan22_1lora.json` | Single LoRA pair enhancement |
| **2** | `wan22_2lora.json` | Dual LoRA pair processing |
| **3** | `wan22_3lora.json` | Triple LoRA pair optimization |

### Workflow Components

Each workflow is built on **ComfyUI's robust architecture** and includes:

#### Core Processing Nodes
- **CLIP Text Encoding**: Advanced prompt processing and understanding
- **VAE Processing**: High-quality image encoding and decoding
- **WanImageToVideo**: Primary video generation engine
- **Image Processing**: Concatenation and transformation utilities

#### LoRA Integration (When Applicable)
- **Dynamic LoRA Loading**: Automatic model loading based on configuration
- **Weight Application**: Precise control over LoRA influence
- **Multi-LoRA Blending**: Seamless integration of multiple enhancement models

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
