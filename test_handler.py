#!/usr/bin/env python3
"""
Test script for the handler.py
"""

import json
import base64
import os

# Mock job input for testing
def create_test_job():
    # Create a simple test image (1x1 pixel PNG)
    test_image_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
    )
    
    # Save test image
    with open("test_image.png", "wb") as f:
        f.write(test_image_data)
    
    return {
        "input": {
            "image_path": "test_image.png",
            "prompt": "A beautiful scene with natural motion",
            "negative_prompt": "bad quality, static, blurry",
            "seed": 42,
            "cfg": 7.5,
            "width": 640,
            "height": 640,
            "length": 81,
            "steps": 20
        }
    }

def test_workflow_conversion():
    """Test the workflow conversion function"""
    from handler import load_workflow
    
    print("Testing workflow conversion...")
    
    # Test with the main workflow
    try:
        workflow = load_workflow("/video_wan2_2_14B_i2v.json")
        print(f"✅ Main workflow loaded: {len(workflow)} nodes")
        
        # Check for key nodes
        key_nodes = ["62", "97", "6", "7", "63", "98", "57", "58"]
        for node_id in key_nodes:
            if node_id in workflow:
                print(f"✅ Found node {node_id}: {workflow[node_id]['class_type']}")
            else:
                print(f"❌ Missing node {node_id}")
                
    except Exception as e:
        print(f"❌ Failed to load main workflow: {e}")
    
    # Test with fallback workflow
    try:
        workflow = load_workflow("/test_simple_workflow.json")
        print(f"✅ Fallback workflow loaded: {len(workflow)} nodes")
    except Exception as e:
        print(f"❌ Failed to load fallback workflow: {e}")

def test_handler():
    """Test the handler function"""
    from handler import handler
    
    print("\nTesting handler function...")
    
    job = create_test_job()
    print(f"Test job: {json.dumps(job, indent=2)}")
    
    try:
        result = handler(job)
        print(f"Handler result: {result}")
        
        if "error" in result:
            print(f"❌ Handler returned error: {result['error']}")
        elif "video" in result:
            print(f"✅ Handler returned video (length: {len(result['video'])} chars)")
        else:
            print(f"⚠️ Unexpected result format: {result}")
            
    except Exception as e:
        print(f"❌ Handler failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== Handler Test Script ===")
    
    # Check if files exist
    files_to_check = [
        "/video_wan2_2_14B_i2v.json",
        "/test_simple_workflow.json"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ Found {file_path}")
        else:
            print(f"❌ Missing {file_path}")
    
    test_workflow_conversion()
    
    # Only test handler if ComfyUI is running
    import urllib.request
    try:
        with urllib.request.urlopen("http://127.0.0.1:8188/", timeout=5):
            print("✅ ComfyUI server is running")
            test_handler()
    except:
        print("⚠️ ComfyUI server not running, skipping handler test")
    
    print("\n=== Test Complete ===")
