#!/usr/bin/env python3
"""
Test script to validate the RunPod Wan2.2 I2V setup
"""

import os
import json
import sys

def test_workflow_file():
    """Test if the workflow file exists and is valid JSON"""
    workflow_path = "/video_wan2_2_14B_i2v.json"
    
    if not os.path.exists(workflow_path):
        print(f"❌ Workflow file not found: {workflow_path}")
        return False
    
    try:
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
        print(f"✅ Workflow file loaded successfully: {len(workflow.get('nodes', []))} nodes")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in workflow file: {e}")
        return False

def test_network_volume():
    """Test if network volume is mounted and contains required models"""
    volume_path = "/runpod-volume"
    
    if not os.path.exists(volume_path):
        print(f"⚠️  Network volume not mounted at {volume_path}")
        return False
    
    print(f"✅ Network volume found at {volume_path}")
    
    # Check required model directories
    required_dirs = [
        "models/diffusion_models",
        "models/vae", 
        "models/text_encoders",
        "models/loras"
    ]
    
    all_found = True
    for dir_path in required_dirs:
        full_path = os.path.join(volume_path, dir_path)
        if os.path.exists(full_path):
            files = os.listdir(full_path)
            print(f"✅ {dir_path}: {len(files)} files")
        else:
            print(f"❌ Missing directory: {dir_path}")
            all_found = False
    
    return all_found

def test_comfyui_setup():
    """Test ComfyUI installation and configuration"""
    comfyui_path = "/ComfyUI"
    
    if not os.path.exists(comfyui_path):
        print(f"❌ ComfyUI not found at {comfyui_path}")
        return False
    
    print(f"✅ ComfyUI found at {comfyui_path}")
    
    # Check extra_model_paths.yaml
    config_path = os.path.join(comfyui_path, "extra_model_paths.yaml")
    if os.path.exists(config_path):
        print("✅ extra_model_paths.yaml configured")
    else:
        print("❌ extra_model_paths.yaml not found")
        return False
    
    # Check custom nodes
    custom_nodes_path = os.path.join(comfyui_path, "custom_nodes")
    if os.path.exists(custom_nodes_path):
        nodes = [d for d in os.listdir(custom_nodes_path) if os.path.isdir(os.path.join(custom_nodes_path, d))]
        print(f"✅ Custom nodes: {len(nodes)} installed")
        
        # Check for WanVideoWrapper specifically
        if "ComfyUI-WanVideoWrapper" in nodes:
            print("✅ ComfyUI-WanVideoWrapper found")
        else:
            print("❌ ComfyUI-WanVideoWrapper not found")
            return False
    else:
        print("❌ Custom nodes directory not found")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=== RunPod Wan2.2 I2V Setup Validation ===\n")
    
    tests = [
        ("Workflow File", test_workflow_file),
        ("Network Volume", test_network_volume),
        ("ComfyUI Setup", test_comfyui_setup)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- Testing {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    print("\n=== Test Results ===")
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Setup is ready for deployment.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()
