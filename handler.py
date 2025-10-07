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
    return json.loads(urllib.request.urlopen(req).read())

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
        if 'gifs' in node_output:
            for video in node_output['gifs']:
                # fullpath를 이용하여 직접 파일을 읽고 base64로 인코딩
                with open(video['fullpath'], 'rb') as f:
                    video_data = base64.b64encode(f.read()).decode('utf-8')
                videos_output.append(video_data)
        output_videos[node_id] = videos_output

    return output_videos

def load_workflow(workflow_path):
    with open(workflow_path, 'r') as file:
        return json.load(file)

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
    logger.info("Using video_wan2_2_14B_i2v.json workflow")

    try:
        prompt = load_workflow(workflow_file)
    except Exception as e:
        return {"error": f"Failed to load workflow: {e}"}

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
    # Image input nodes (LoadImage nodes: 62 and 97)
    if "62" in prompt:
        prompt["62"]["inputs"]["image"] = os.path.basename(image_path)
    if "97" in prompt:
        prompt["97"]["inputs"]["image"] = os.path.basename(image_path)

    # Text encoding nodes (CLIPTextEncode nodes: 6, 7, 93, 89)
    if "6" in prompt:  # Positive prompt for fp8_scaled workflow
        prompt["6"]["widgets_values"][0] = positive_prompt
    if "7" in prompt:  # Negative prompt for fp8_scaled workflow
        prompt["7"]["widgets_values"][0] = negative_prompt
    if "93" in prompt:  # Positive prompt for 4steps LoRA workflow
        prompt["93"]["widgets_values"][0] = positive_prompt
    if "89" in prompt:  # Negative prompt for 4steps LoRA workflow
        prompt["89"]["widgets_values"][0] = negative_prompt

    # WanImageToVideo nodes (63 and 98) - video parameters
    if "63" in prompt:  # fp8_scaled workflow
        prompt["63"]["widgets_values"] = [width, height, length, 1]  # [width, height, length, batch_size]
    if "98" in prompt:  # 4steps LoRA workflow
        prompt["98"]["widgets_values"] = [width, height, length, 1]

    # KSamplerAdvanced nodes for sampling parameters
    sampler_nodes = ["57", "58", "85", "86"]  # KSamplerAdvanced node IDs
    for node_id in sampler_nodes:
        if node_id in prompt:
            # Update seed and steps
            if "noise_seed" in prompt[node_id]["widgets_values"]:
                seed_index = 1  # Usually index 1 for noise_seed
                if len(prompt[node_id]["widgets_values"]) > seed_index:
                    prompt[node_id]["widgets_values"][seed_index] = seed
            if "steps" in prompt[node_id]["widgets_values"]:
                steps_index = 3  # Usually index 3 for steps
                if len(prompt[node_id]["widgets_values"]) > steps_index:
                    prompt[node_id]["widgets_values"][steps_index] = steps
            if "cfg" in prompt[node_id]["widgets_values"]:
                cfg_index = 4  # Usually index 4 for cfg
                if len(prompt[node_id]["widgets_values"]) > cfg_index:
                    prompt[node_id]["widgets_values"][cfg_index] = cfg

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
            response = urllib.request.urlopen(http_url, timeout=5)
            logger.info(f"HTTP connection successful (attempt {http_attempt+1})")
            break
        except Exception as e:
            logger.warning(f"HTTP connection failed (attempt {http_attempt+1}/{max_http_attempts}): {e}")
            if http_attempt == max_http_attempts - 1:
                raise Exception("Cannot connect to ComfyUI server. Please check if server is running.")
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
                raise Exception("WebSocket connection timeout (3 minutes)")
            time.sleep(5)

    # Generate video
    videos = get_videos(ws, prompt)
    ws.close()

    # Return first video found
    for node_id in videos:
        if videos[node_id]:
            return {"video": videos[node_id][0]}

    return {"error": "No video output found"}

runpod.serverless.start({"handler": handler})