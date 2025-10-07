#!/usr/bin/env python3
"""
Parse the video_wan2_2_14B_i2v.json workflow to understand its structure
"""

import json

def parse_workflow():
    with open('/video_wan2_2_14B_i2v.json', 'r') as f:
        workflow = json.load(f)
    
    print("=== Workflow Analysis ===")
    print(f"Total nodes: {len(workflow['nodes'])}")
    
    # Find key node types
    node_types = {}
    for node in workflow['nodes']:
        node_type = node['type']
        node_id = str(node['id'])
        
        if node_type not in node_types:
            node_types[node_type] = []
        node_types[node_type].append({
            'id': node_id,
            'mode': node.get('mode', 0),
            'widgets_values': node.get('widgets_values', [])
        })
    
    # Print important node types
    important_types = ['LoadImage', 'CLIPTextEncode', 'WanImageToVideo', 'KSamplerAdvanced', 'SaveVideo', 'CreateVideo']
    
    for node_type in important_types:
        if node_type in node_types:
            print(f"\n{node_type} nodes:")
            for node_info in node_types[node_type]:
                mode_str = f" (mode={node_info['mode']})" if node_info['mode'] != 0 else ""
                print(f"  ID: {node_info['id']}{mode_str}")
                if node_info['widgets_values']:
                    print(f"    widgets_values: {node_info['widgets_values']}")
    
    # Convert to ComfyUI API format
    api_workflow = {}
    for node in workflow['nodes']:
        node_id = str(node['id'])
        api_workflow[node_id] = {
            'class_type': node['type'],
            'inputs': {}
        }
        
        # Add inputs from links
        if 'inputs' in node:
            for input_def in node['inputs']:
                if input_def.get('link') is not None:
                    # This input is connected to another node
                    continue
                elif 'widget' in input_def:
                    # This is a widget input
                    widget_name = input_def['widget']['name']
                    api_workflow[node_id]['inputs'][widget_name] = None
        
        # Add widget values
        if 'widgets_values' in node and node['widgets_values']:
            # Map widget values to input names based on node type
            if node['type'] == 'LoadImage':
                if len(node['widgets_values']) > 0:
                    api_workflow[node_id]['inputs']['image'] = node['widgets_values'][0]
            elif node['type'] == 'CLIPTextEncode':
                if len(node['widgets_values']) > 0:
                    api_workflow[node_id]['inputs']['text'] = node['widgets_values'][0]
            elif node['type'] == 'WanImageToVideo':
                if len(node['widgets_values']) >= 4:
                    api_workflow[node_id]['inputs']['width'] = node['widgets_values'][0]
                    api_workflow[node_id]['inputs']['height'] = node['widgets_values'][1]
                    api_workflow[node_id]['inputs']['length'] = node['widgets_values'][2]
                    api_workflow[node_id]['inputs']['batch_size'] = node['widgets_values'][3]
            elif node['type'] == 'KSamplerAdvanced':
                if len(node['widgets_values']) >= 10:
                    api_workflow[node_id]['inputs']['add_noise'] = node['widgets_values'][0]
                    api_workflow[node_id]['inputs']['noise_seed'] = node['widgets_values'][1]
                    api_workflow[node_id]['inputs']['steps'] = node['widgets_values'][3]
                    api_workflow[node_id]['inputs']['cfg'] = node['widgets_values'][4]
                    api_workflow[node_id]['inputs']['sampler_name'] = node['widgets_values'][5]
                    api_workflow[node_id]['inputs']['scheduler'] = node['widgets_values'][6]
    
    # Add links
    for link in workflow['links']:
        link_id, from_node, from_socket, to_node, to_socket, data_type = link
        to_node_id = str(to_node)
        from_node_id = str(from_node)
        
        if to_node_id in api_workflow:
            # Find the input name for this socket
            for node in workflow['nodes']:
                if node['id'] == to_node:
                    if 'inputs' in node and to_socket < len(node['inputs']):
                        input_name = node['inputs'][to_socket]['name']
                        api_workflow[to_node_id]['inputs'][input_name] = [from_node_id, from_socket]
                    break
    
    return api_workflow

if __name__ == "__main__":
    workflow = parse_workflow()
    
    # Save the parsed workflow
    with open('/parsed_workflow.json', 'w') as f:
        json.dump(workflow, f, indent=2)
    
    print(f"\nParsed workflow saved to /parsed_workflow.json")
