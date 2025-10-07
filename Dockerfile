# Use the official RunPod PyTorch image with CUDA support
FROM runpod/pytorch:2.2.0-py3.11-cuda12.1.1-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    unzip \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    runpod \
    requests \
    pillow \
    opencv-python \
    numpy \
    torch \
    torchvision \
    torchaudio \
    transformers \
    diffusers \
    accelerate \
    xformers \
    safetensors

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /app/ComfyUI

# Install ComfyUI dependencies
RUN cd /app/ComfyUI && pip install -r requirements.txt

# Create model directories
RUN mkdir -p /app/ComfyUI/models/diffusion_models \
    /app/ComfyUI/models/vae \
    /app/ComfyUI/models/text_encoders \
    /app/ComfyUI/models/loras \
    /app/ComfyUI/input \
    /app/ComfyUI/output

# Download WAN 2.2 models
# Diffusion models
RUN wget -O /app/ComfyUI/models/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors \
    "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors"

RUN wget -O /app/ComfyUI/models/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors \
    "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors"

# VAE model
RUN wget -O /app/ComfyUI/models/vae/wan_2.1_vae.safetensors \
    "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors"

# Text encoder
RUN wget -O /app/ComfyUI/models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors \
    "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"

# LoRA models
RUN wget -O /app/ComfyUI/models/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors \
    "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors"

RUN wget -O /app/ComfyUI/models/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors \
    "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors"

# Copy workflow and handler
COPY wan2.2i2v.json /app/workflow.json
COPY handler.py /app/handler.py

# Set environment variables
ENV PYTHONPATH="/app/ComfyUI:${PYTHONPATH}"
ENV COMFYUI_PATH="/app/ComfyUI"

# Expose port
EXPOSE 8000

# Start the handler
CMD ["python", "-u", "handler.py"]
