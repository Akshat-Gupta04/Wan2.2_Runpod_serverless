#!/usr/bin/env python3
"""
RunPod Handler for WAN 2.2 I2V using wan2.2i2v.json workflow
"""

import runpod
import requests
import json
import os
import sys
import base64
import uuid
from PIL import Image
import io

# Add ComfyUI to path
sys.path.append('/app/ComfyUI')

def load_workflow():
    """Load the WAN 2.2 I2V workflow"""
    try:
        with open('/app/workflow.json', 'r') as f:
            workflow = json.load(f)
        print("✅ Workflow loaded successfully")
        return workflow
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        return None

def update_workflow_parameters(workflow, prompt, negative_prompt, image_path, **kwargs):
    """Update workflow with user parameters"""
    try:
        # Update positive prompt (node 93 in your workflow)
        if "93" in workflow["nodes"]:
            for node in workflow["nodes"]:
                if node.get("id") == 93 and node.get("type") == "CLIPTextEncode":
                    node["widgets_values"] = [prompt]
                    print(f"✅ Updated positive prompt: {prompt[:50]}...")
                    break
        
        # Update negative prompt (node 89 in your workflow)  
        if "89" in workflow["nodes"]:
            for node in workflow["nodes"]:
                if node.get("id") == 89 and node.get("type") == "CLIPTextEncode":
                    node["widgets_values"] = [negative_prompt]
                    print(f"✅ Updated negative prompt: {negative_prompt[:50]}...")
                    break
        
        # Update image input (node 97 - LoadImage)
        for node in workflow["nodes"]:
            if node.get("id") == 97 and node.get("type") == "LoadImage":
                # Extract filename from path
                filename = os.path.basename(image_path)
                node["widgets_values"] = [filename, "image"]
                print(f"✅ Updated input image: {filename}")
                break
        
        # Update video parameters in WanImageToVideo node (node 98)
        for node in workflow["nodes"]:
            if node.get("id") == 98 and node.get("type") == "WanImageToVideo":
                width = kwargs.get('width', 640)
                height = kwargs.get('height', 640) 
                length = kwargs.get('length', 81)
                batch_size = kwargs.get('batch_size', 1)
                node["widgets_values"] = [width, height, length, batch_size]
                print(f"✅ Updated video params: {width}x{height}, {length} frames")
                break
        
        # Update sampler parameters (nodes 86, 85)
        seed = kwargs.get('seed', 42)
        steps = kwargs.get('steps', 4)  # Default to 4 for Lightning LoRA
        cfg = kwargs.get('cfg', 1.0)    # Default to 1.0 for Lightning LoRA
        
        # Update high noise sampler (node 86)
        for node in workflow["nodes"]:
            if node.get("id") == 86 and node.get("type") == "KSamplerAdvanced":
                widgets = node.get("widgets_values", [])
                if len(widgets) >= 10:
                    widgets[1] = seed  # noise_seed
                    widgets[3] = steps  # steps
                    widgets[4] = cfg    # cfg
                    print(f"✅ Updated high noise sampler: seed={seed}, steps={steps}, cfg={cfg}")
                break
        
        # Update low noise sampler (node 85)  
        for node in workflow["nodes"]:
            if node.get("id") == 85 and node.get("type") == "KSamplerAdvanced":
                widgets = node.get("widgets_values", [])
                if len(widgets) >= 10:
                    widgets[1] = 0      # noise_seed (fixed for second pass)
                    widgets[3] = steps  # steps
                    widgets[4] = cfg    # cfg
                    print(f"✅ Updated low noise sampler: steps={steps}, cfg={cfg}")
                break
        
        return workflow
        
    except Exception as e:
        print(f"❌ Error updating workflow parameters: {e}")
        return None

def process_image(image_data, image_path):
    """Process and save image to ComfyUI input directory"""
    try:
        # Decode base64 if needed
        if isinstance(image_data, str):
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data
        
        # Open and process image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to reasonable dimensions (your workflow uses 640x640 by default)
        max_size = 1024
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Save to ComfyUI input directory
        input_path = f"/app/ComfyUI/input/{os.path.basename(image_path)}"
        image.save(input_path, 'JPEG', quality=95)
        
        print(f"✅ Image saved to: {input_path}")
        print(f"   Size: {image.width}x{image.height}")
        
        return input_path
        
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return None

def execute_workflow(workflow):
    """Execute the workflow via ComfyUI API"""
    try:
        # Start ComfyUI server if not running
        import subprocess
        import time
        
        # Start ComfyUI in background
        print("🚀 Starting ComfyUI server...")
        process = subprocess.Popen([
            'python', '/app/ComfyUI/main.py', 
            '--listen', '0.0.0.0', 
            '--port', '8188'
        ], cwd='/app/ComfyUI')
        
        # Wait for server to start
        time.sleep(10)
        
        # Submit workflow
        api_url = "http://localhost:8188/prompt"
        payload = {
            "prompt": workflow,
            "client_id": str(uuid.uuid4())
        }
        
        print("📤 Submitting workflow to ComfyUI...")
        response = requests.post(api_url, json=payload, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            prompt_id = result.get('prompt_id')
            print(f"✅ Workflow submitted successfully. Prompt ID: {prompt_id}")
            
            # Wait for completion and get results
            return wait_for_completion(prompt_id)
        else:
            print(f"❌ Error submitting workflow: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error executing workflow: {e}")
        return None

def wait_for_completion(prompt_id, timeout=600):
    """Wait for workflow completion and return results"""
    try:
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check status
            status_url = f"http://localhost:8188/history/{prompt_id}"
            response = requests.get(status_url, timeout=10)
            
            if response.status_code == 200:
                history = response.json()
                if prompt_id in history:
                    # Workflow completed
                    result = history[prompt_id]
                    
                    # Find output video
                    outputs = result.get('outputs', {})
                    for node_id, node_output in outputs.items():
                        if 'videos' in node_output:
                            video_info = node_output['videos'][0]
                            video_path = f"/app/ComfyUI/output/{video_info['filename']}"
                            
                            if os.path.exists(video_path):
                                print(f"✅ Video generated: {video_path}")
                                
                                # Convert to base64
                                with open(video_path, 'rb') as f:
                                    video_base64 = base64.b64encode(f.read()).decode('utf-8')
                                
                                return {
                                    'success': True,
                                    'video_base64': video_base64,
                                    'video_path': video_path,
                                    'filename': video_info['filename']
                                }
            
            time.sleep(5)  # Check every 5 seconds
        
        print("❌ Timeout waiting for workflow completion")
        return None
        
    except Exception as e:
        print(f"❌ Error waiting for completion: {e}")
        return None

def handler(job):
    """Main RunPod handler function"""
    try:
        print("🚀 Starting WAN 2.2 I2V job processing...")
        
        # Get job input
        job_input = job.get('input', {})
        
        # Extract parameters
        prompt = job_input.get('prompt', 'A person walking naturally')
        negative_prompt = job_input.get('negative_prompt', '色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，杂乱的背景，三条腿，背景人很多，倒着走')
        image_path = job_input.get('image_path', '')
        image_base64 = job_input.get('image_base64', '')
        
        # Video parameters
        width = job_input.get('width', 640)
        height = job_input.get('height', 640)
        length = job_input.get('length', 81)
        seed = job_input.get('seed', 42)
        steps = job_input.get('steps', 4)
        cfg = job_input.get('cfg', 1.0)
        
        print(f"📝 Parameters:")
        print(f"   Prompt: {prompt[:50]}...")
        print(f"   Negative: {negative_prompt[:50]}...")
        print(f"   Size: {width}x{height}")
        print(f"   Length: {length} frames")
        print(f"   Seed: {seed}, Steps: {steps}, CFG: {cfg}")
        
        # Load workflow
        workflow = load_workflow()
        if not workflow:
            return {"error": "Failed to load workflow"}
        
        # Process image
        if image_base64:
            image_filename = f"input_{uuid.uuid4().hex[:8]}.jpg"
            processed_image_path = process_image(image_base64, image_filename)
        elif image_path:
            # Handle network volume path
            if image_path.startswith('/runpod-volume/'):
                source_path = image_path
            else:
                source_path = f"/runpod-volume/{image_path}"
            
            if os.path.exists(source_path):
                # Copy to ComfyUI input directory
                image_filename = os.path.basename(source_path)
                dest_path = f"/app/ComfyUI/input/{image_filename}"
                
                import shutil
                shutil.copy2(source_path, dest_path)
                processed_image_path = dest_path
                print(f"✅ Copied image from network volume: {source_path}")
            else:
                return {"error": f"Image not found: {source_path}"}
        else:
            return {"error": "No image provided"}
        
        if not processed_image_path:
            return {"error": "Failed to process image"}
        
        # Update workflow parameters
        updated_workflow = update_workflow_parameters(
            workflow, prompt, negative_prompt, processed_image_path,
            width=width, height=height, length=length,
            seed=seed, steps=steps, cfg=cfg
        )
        
        if not updated_workflow:
            return {"error": "Failed to update workflow parameters"}
        
        # Execute workflow
        result = execute_workflow(updated_workflow)
        
        if result and result.get('success'):
            print("🎉 Job completed successfully!")
            return {
                "success": True,
                "video_base64": result['video_base64'],
                "filename": result['filename'],
                "parameters": {
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "width": width,
                    "height": height,
                    "length": length,
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg
                }
            }
        else:
            return {"error": "Failed to generate video"}
            
    except Exception as e:
        print(f"❌ Handler error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    print("🚀 Starting WAN 2.2 I2V RunPod Handler...")
    runpod.serverless.start({"handler": handler})
