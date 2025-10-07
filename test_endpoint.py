#!/usr/bin/env python3
"""
Test script for WAN 2.2 I2V RunPod endpoint
"""

import requests
import base64
import json
import time
import sys
from pathlib import Path

def encode_image(image_path):
    """Encode image to base64"""
    try:
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"❌ Error encoding image: {e}")
        return None

def test_endpoint(endpoint_url, api_key, image_path):
    """Test the RunPod endpoint"""
    
    print("🧪 Testing WAN 2.2 I2V Endpoint")
    print("=" * 40)
    print(f"📍 Endpoint: {endpoint_url}")
    print(f"🖼️  Image: {image_path}")
    print()
    
    # Encode image
    print("📤 Encoding image...")
    image_base64 = encode_image(image_path)
    if not image_base64:
        return False
    
    print(f"✅ Image encoded ({len(image_base64)} characters)")
    
    # Prepare payload
    payload = {
        "input": {
            "prompt": "A person walking naturally with smooth motion",
            "negative_prompt": "static, frozen, blurry, low quality, artifacts",
            "image_base64": image_base64,
            "width": 640,
            "height": 640,
            "length": 81,
            "steps": 4,
            "cfg": 1.0,
            "seed": 42
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Submit job
    print("🚀 Submitting job...")
    try:
        response = requests.post(endpoint_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('id')
            print(f"✅ Job submitted successfully!")
            print(f"🆔 Job ID: {job_id}")
            
            # Poll for results
            return poll_job_status(endpoint_url.replace('/run', '/status'), headers, job_id)
            
        else:
            print(f"❌ Error submitting job: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error submitting job: {e}")
        return False

def poll_job_status(status_url, headers, job_id, max_wait=600):
    """Poll job status until completion"""
    
    print(f"⏳ Polling job status (max {max_wait}s)...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.post(
                status_url,
                headers=headers,
                json={"input": {"job_id": job_id}},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('status', 'UNKNOWN')
                
                print(f"📊 Status: {status}")
                
                if status == 'COMPLETED':
                    output = result.get('output', {})
                    if output.get('success'):
                        video_base64 = output.get('video_base64')
                        filename = output.get('filename', 'output.mp4')
                        
                        # Save video
                        if video_base64:
                            video_data = base64.b64decode(video_base64)
                            output_path = f"test_output_{filename}"
                            
                            with open(output_path, 'wb') as f:
                                f.write(video_data)
                            
                            print(f"🎉 Success! Video saved to: {output_path}")
                            print(f"📊 Video size: {len(video_data)} bytes")
                            return True
                        else:
                            print("❌ No video data in response")
                            return False
                    else:
                        error = output.get('error', 'Unknown error')
                        print(f"❌ Job failed: {error}")
                        return False
                        
                elif status == 'FAILED':
                    error = result.get('error', 'Unknown error')
                    print(f"❌ Job failed: {error}")
                    return False
                    
                elif status in ['IN_QUEUE', 'IN_PROGRESS']:
                    print("⏳ Job still processing...")
                    time.sleep(10)
                    continue
                    
            else:
                print(f"❌ Error checking status: {response.status_code}")
                time.sleep(5)
                continue
                
        except Exception as e:
            print(f"❌ Error polling status: {e}")
            time.sleep(5)
            continue
    
    print("⏰ Timeout waiting for job completion")
    return False

def main():
    """Main function"""
    
    if len(sys.argv) != 4:
        print("Usage: python test_endpoint.py <endpoint_url> <api_key> <image_path>")
        print()
        print("Example:")
        print("python test_endpoint.py \\")
        print("  https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run \\")
        print("  YOUR_API_KEY \\")
        print("  test_image.jpg")
        sys.exit(1)
    
    endpoint_url = sys.argv[1]
    api_key = sys.argv[2]
    image_path = sys.argv[3]
    
    # Validate inputs
    if not Path(image_path).exists():
        print(f"❌ Error: Image file not found: {image_path}")
        sys.exit(1)
    
    if not endpoint_url.startswith('https://'):
        print("❌ Error: Endpoint URL must start with https://")
        sys.exit(1)
    
    # Run test
    success = test_endpoint(endpoint_url, api_key, image_path)
    
    if success:
        print("\n🎉 Test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
