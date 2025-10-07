import runpod
from runpod.serverless.utils import rp_upload
import os
import websocket
import base64
import json
import uuid
import logging
import urllib.request
import urllib.parse
import binascii
import time

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server_address = os.getenv('SERVER_ADDRESS', '127.0.0.1')
client_id = str(uuid.uuid4())

def save_data_if_base64(data_input, temp_dir, output_filename):
    """
    Check if input data is Base64 string and save as file, otherwise return as path.
    """
    if not isinstance(data_input, str):
        return data_input

    try:
        decoded_data = base64.b64decode(data_input)
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.abspath(os.path.join(temp_dir, output_filename))
        with open(file_path, 'wb') as f:
            f.write(decoded_data)
        logger.info(f"✅ Base64 input saved to '{file_path}'")
        return file_path
    except (binascii.Error, ValueError):
        logger.info(f"➡️ '{data_input}' treated as file path")
        return data_input
    
def queue_prompt(prompt):
    url = f"http://{server_address}:8188/prompt"
    logger.info(f"Queueing prompt to: {url}")
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(url, data=data)
    req.add_header('Content-Type', 'application/json')

    try:
        response = urllib.request.urlopen(req)
        response_data = response.read()
        return json.loads(response_data)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        logger.error(f"HTTP Error {e.code}: {error_body}")
        raise Exception(f"ComfyUI API Error {e.code}: {error_body}")
    except Exception as e:
        logger.error(f"Failed to queue prompt: {e}")
        raise

def get_image(filename, subfolder, folder_type):
    url = f"http://{server_address}:8188/view"
    logger.info(f"Getting image from: {url}")
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"{url}?{url_values}") as response:
        return response.read()

def get_history(prompt_id):
    url = f"http://{server_address}:8188/history/{prompt_id}"
    logger.info(f"Getting history from: {url}")
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())

def get_videos(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_videos = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break
        else:
            continue

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        videos_output = []

        # Check for different video output formats
        if 'gifs' in node_output:
            for video in node_output['gifs']:
                with open(video['fullpath'], 'rb') as f:
                    video_data = base64.b64encode(f.read()).decode('utf-8')
                videos_output.append(video_data)
        elif 'videos' in node_output:
            for video in node_output['videos']:
                with open(video['fullpath'], 'rb') as f:
                    video_data = base64.b64encode(f.read()).decode('utf-8')
                videos_output.append(video_data)
        elif 'mp4' in node_output:
            for video in node_output['mp4']:
                with open(video['fullpath'], 'rb') as f:
                    video_data = base64.b64encode(f.read()).decode('utf-8')
                videos_output.append(video_data)

        if videos_output:
            output_videos[node_id] = videos_output

    return output_videos

def load_workflow(workflow_path):
    """Load and convert ComfyUI workflow to API format"""
    with open(workflow_path, 'r') as file:
        workflow_data = json.load(file)

    # Convert ComfyUI export format to API format
    if 'nodes' in workflow_data:
        # This is a ComfyUI export format, convert to API format
        api_workflow = {}
        for node in workflow_data['nodes']:
            node_id = str(node['id'])
            api_workflow[node_id] = {
                'class_type': node['type'],
                'inputs': {}
            }

            # Convert inputs
            if 'inputs' in node:
                for input_item in node['inputs']:
                    input_name = input_item['name']
                    if input_item.get('link') is not None:
                        # This input is connected to another node
                        # Find the source node and output
                        link_id = input_item['link']
                        for link in workflow_data.get('links', []):
                            if link[0] == link_id:
                                source_node_id = str(link[1])
                                source_output_index = link[2]
                                api_workflow[node_id]['inputs'][input_name] = [source_node_id, source_output_index]
                                break

            # Add widget values as inputs
            if 'widgets_values' in node:
                # Map widget values to input names based on node type
                if node['type'] == 'CLIPTextEncode' and len(node['widgets_values']) > 0:
                    api_workflow[node_id]['inputs']['text'] = node['widgets_values'][0]
                elif node['type'] == 'LoadImage' and len(node['widgets_values']) > 0:
                    api_workflow[node_id]['inputs']['image'] = node['widgets_values'][0]
                elif node['type'] == 'WanImageToVideo' and len(node['widgets_values']) >= 4:
                    api_workflow[node_id]['inputs']['width'] = node['widgets_values'][0]
                    api_workflow[node_id]['inputs']['height'] = node['widgets_values'][1]
                    api_workflow[node_id]['inputs']['length'] = node['widgets_values'][2]
                    api_workflow[node_id]['inputs']['batch_size'] = node['widgets_values'][3]
                elif node['type'] == 'KSamplerAdvanced' and len(node['widgets_values']) >= 10:
                    api_workflow[node_id]['inputs']['add_noise'] = node['widgets_values'][0]
                    api_workflow[node_id]['inputs']['noise_seed'] = node['widgets_values'][1]
                    api_workflow[node_id]['inputs']['steps'] = node['widgets_values'][3]
                    api_workflow[node_id]['inputs']['cfg'] = node['widgets_values'][4]
                    api_workflow[node_id]['inputs']['sampler_name'] = node['widgets_values'][5]
                    api_workflow[node_id]['inputs']['scheduler'] = node['widgets_values'][6]
                    api_workflow[node_id]['inputs']['start_at_step'] = node['widgets_values'][7]
                    api_workflow[node_id]['inputs']['end_at_step'] = node['widgets_values'][8]
                    api_workflow[node_id]['inputs']['return_with_leftover_noise'] = node['widgets_values'][9]
                elif node['type'] in ['UNETLoader', 'VAELoader', 'CLIPLoader'] and len(node['widgets_values']) > 0:
                    # Model loaders - use first widget value as model name
                    if node['type'] == 'UNETLoader':
                        api_workflow[node_id]['inputs']['unet_name'] = node['widgets_values'][0]
                        if len(node['widgets_values']) > 1:
                            api_workflow[node_id]['inputs']['weight_dtype'] = node['widgets_values'][1]
                    elif node['type'] == 'VAELoader':
                        api_workflow[node_id]['inputs']['vae_name'] = node['widgets_values'][0]
                    elif node['type'] == 'CLIPLoader':
                        api_workflow[node_id]['inputs']['clip_name'] = node['widgets_values'][0]
                        if len(node['widgets_values']) > 1:
                            api_workflow[node_id]['inputs']['type'] = node['widgets_values'][1]
                        if len(node['widgets_values']) > 2:
                            api_workflow[node_id]['inputs']['device'] = node['widgets_values'][2]
                elif node['type'] == 'LoraLoaderModelOnly' and len(node['widgets_values']) >= 2:
                    api_workflow[node_id]['inputs']['lora_name'] = node['widgets_values'][0]
                    api_workflow[node_id]['inputs']['strength_model'] = node['widgets_values'][1]
                elif node['type'] == 'ModelSamplingSD3' and len(node['widgets_values']) > 0:
                    api_workflow[node_id]['inputs']['shift'] = node['widgets_values'][0]
                elif node['type'] == 'CreateVideo' and len(node['widgets_values']) > 0:
                    api_workflow[node_id]['inputs']['fps'] = node['widgets_values'][0]
                elif node['type'] == 'SaveVideo' and len(node['widgets_values']) >= 3:
                    api_workflow[node_id]['inputs']['filename_prefix'] = node['widgets_values'][0]
                    api_workflow[node_id]['inputs']['format'] = node['widgets_values'][1]
                    api_workflow[node_id]['inputs']['codec'] = node['widgets_values'][2]

        return api_workflow
    else:
        # Already in API format
        return workflow_data

def handler(job):
    job_input = job.get("input", {})
    logger.info(f"Received job input: {job_input}")
    task_id = f"task_{uuid.uuid4()}"

    # Handle image input (Base64 or path)
    image_path_input = job_input.get("image_path")
    image_base64_input = job_input.get("image_base64")

    if image_path_input:
        image_path = image_path_input
    elif image_base64_input:
        try:
            os.makedirs(task_id, exist_ok=True)
            image_path = os.path.join(task_id, "input_image.jpg")
            decoded_data = base64.b64decode(image_base64_input)
            with open(image_path, 'wb') as f:
                f.write(decoded_data)
            logger.info(f"Base64 image saved to '{image_path}'")
        except Exception as e:
            return {"error": f"Base64 image decoding failed: {e}"}
    else:
        return {"error": "Either image_path or image_base64 must be provided"}

    # Load the specific Wan2.2 I2V workflow
    workflow_file = "/video_wan2_2_14B_i2v.json"
    fallback_workflow = "/test_simple_workflow.json"

    try:
        logger.info(f"Attempting to load workflow: {workflow_file}")
        prompt = load_workflow(workflow_file)
        logger.info(f"Loaded workflow with {len(prompt)} nodes")

    except Exception as e:
        logger.error(f"Failed to load main workflow: {e}")
        logger.info(f"Trying fallback workflow: {fallback_workflow}")
        try:
            prompt = load_workflow(fallback_workflow)
            logger.info(f"Loaded fallback workflow with {len(prompt)} nodes")
        except Exception as e2:
            logger.error(f"Failed to load fallback workflow: {e2}")
            return {"error": f"Failed to load any workflow. Main: {e}, Fallback: {e2}"}

    # Save converted workflow for debugging
    debug_workflow_path = f"/tmp/converted_workflow_{task_id}.json"
    try:
        with open(debug_workflow_path, 'w') as f:
            json.dump(prompt, f, indent=2)
        logger.info(f"Saved converted workflow to {debug_workflow_path}")
    except Exception as e:
        logger.warning(f"Could not save debug workflow: {e}")

    # Get parameters from input
    positive_prompt = job_input.get("prompt", "A beautiful scene with natural motion")
    negative_prompt = job_input.get("negative_prompt", "bad quality, static, blurry")
    seed = job_input.get("seed", 42)
    cfg = job_input.get("cfg", 7.5)
    width = job_input.get("width", 640)
    height = job_input.get("height", 640)
    length = job_input.get("length", 81)
    steps = job_input.get("steps", 20)

    # Configure workflow parameters based on video_wan2_2_14B_i2v.json structure
    # Copy image to ComfyUI input directory so it can be found
    import shutil
    comfyui_input_dir = "/ComfyUI/input"
    os.makedirs(comfyui_input_dir, exist_ok=True)
    image_filename = os.path.basename(image_path)
    comfyui_image_path = os.path.join(comfyui_input_dir, image_filename)
    shutil.copy2(image_path, comfyui_image_path)
    logger.info(f"Copied image to ComfyUI input directory: {comfyui_image_path}")

    # Image input nodes (LoadImage nodes: 62 and 97)
    if "62" in prompt:
        prompt["62"]["inputs"]["image"] = image_filename
    if "97" in prompt:
        prompt["97"]["inputs"]["image"] = image_filename

    # Text encoding nodes (CLIPTextEncode nodes: 6, 7, 93, 89)
    if "6" in prompt:  # Positive prompt for fp8_scaled workflow
        prompt["6"]["inputs"]["text"] = positive_prompt
    if "7" in prompt:  # Negative prompt for fp8_scaled workflow
        prompt["7"]["inputs"]["text"] = negative_prompt
    if "93" in prompt:  # Positive prompt for 4steps LoRA workflow
        prompt["93"]["inputs"]["text"] = positive_prompt
    if "89" in prompt:  # Negative prompt for 4steps LoRA workflow
        prompt["89"]["inputs"]["text"] = negative_prompt

    # WanImageToVideo nodes (63 and 98) - video parameters
    if "63" in prompt:  # fp8_scaled workflow
        prompt["63"]["inputs"]["width"] = width
        prompt["63"]["inputs"]["height"] = height
        prompt["63"]["inputs"]["length"] = length
        prompt["63"]["inputs"]["batch_size"] = 1
    if "98" in prompt:  # 4steps LoRA workflow
        prompt["98"]["inputs"]["width"] = width
        prompt["98"]["inputs"]["height"] = height
        prompt["98"]["inputs"]["length"] = length
        prompt["98"]["inputs"]["batch_size"] = 1

    # KSamplerAdvanced nodes for sampling parameters
    sampler_nodes = ["57", "58", "85", "86"]  # KSamplerAdvanced node IDs
    for node_id in sampler_nodes:
        if node_id in prompt:
            # Update seed, steps, and cfg
            if "noise_seed" in prompt[node_id]["inputs"]:
                prompt[node_id]["inputs"]["noise_seed"] = seed
            if "steps" in prompt[node_id]["inputs"]:
                prompt[node_id]["inputs"]["steps"] = steps
            if "cfg" in prompt[node_id]["inputs"]:
                prompt[node_id]["inputs"]["cfg"] = cfg

    logger.info(f"Configured workflow with: prompt='{positive_prompt[:50]}...', seed={seed}, cfg={cfg}, size={width}x{height}, length={length}, steps={steps}")

    # Connect to ComfyUI WebSocket
    ws_url = f"ws://{server_address}:8188/ws?clientId={client_id}"
    logger.info(f"Connecting to WebSocket: {ws_url}")

    # Check HTTP connection first
    http_url = f"http://{server_address}:8188/"
    logger.info(f"Checking HTTP connection to: {http_url}")

    max_http_attempts = 180
    for http_attempt in range(max_http_attempts):
        try:
            with urllib.request.urlopen(http_url, timeout=5) as response:
                logger.info(f"HTTP connection successful (attempt {http_attempt+1})")
                break
        except Exception as e:
            logger.warning(f"HTTP connection failed (attempt {http_attempt+1}/{max_http_attempts}): {e}")
            if http_attempt == max_http_attempts - 1:
                return {"error": "Cannot connect to ComfyUI server. Please check if server is running."}
            time.sleep(1)

    # Connect to WebSocket
    ws = websocket.WebSocket()
    max_attempts = int(180/5)  # 3 minutes
    for attempt in range(max_attempts):
        try:
            ws.connect(ws_url)
            logger.info(f"WebSocket connection successful (attempt {attempt+1})")
            break
        except Exception as e:
            logger.warning(f"WebSocket connection failed (attempt {attempt+1}/{max_attempts}): {e}")
            if attempt == max_attempts - 1:
                return {"error": "WebSocket connection timeout (3 minutes)"}
            time.sleep(5)

    # Generate video
    try:
        videos = get_videos(ws, prompt)
        ws.close()

        # Return first video found
        for node_id in videos:
            if videos[node_id]:
                logger.info(f"Found video output from node {node_id}")
                return {"video": videos[node_id][0]}

        return {"error": "No video output found in any node"}

    except Exception as e:
        ws.close()
        logger.error(f"Error during video generation: {e}")
        return {"error": f"Video generation failed: {e}"}

runpod.serverless.start({"handler": handler})