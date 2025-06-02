#!/usr/bin/env python3

import requests
import json

# Test the complete tool execution cycle
# Step 1: Send initial request that should trigger a tool call
# Step 2: Send tool result back 
# Step 3: See if the model responds appropriately

def test_tool_cycle():
    print("=== Testing Complete Tool Execution Cycle ===\n")
    
    # Step 1: Initial request that should trigger tool use
    print("Step 1: Sending request that should trigger tool use...")
    
    initial_request = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 300,
        "messages": [
            {"role": "user", "content": "Please list the files in the current directory using ls"}
        ],
        "tools": [
            {
                "name": "Bash",
                "description": "Execute bash commands",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The bash command to execute"
                        }
                    },
                    "required": ["command"]
                }
            }
        ],
        "tool_choice": {"type": "auto"}
    }
    
    response1 = requests.post(
        "http://localhost:8082/v1/messages",
        headers={
            "content-type": "application/json",
            "x-api-key": "dummy-key"
        },
        json=initial_request,
        timeout=30
    )
    
    print(f"Response 1 status: {response1.status_code}")
    
    if response1.status_code != 200:
        print(f"Error: {response1.text}")
        return
    
    response1_json = response1.json()
    print(f"Response 1 stop_reason: {response1_json.get('stop_reason')}")
    
    # Find the tool_use block
    tool_use_block = None
    for content in response1_json.get('content', []):
        if content.get('type') == 'tool_use':
            tool_use_block = content
            break
    
    if not tool_use_block:
        print("❌ No tool_use block found in first response")
        print("Response content:", json.dumps(response1_json.get('content'), indent=2))
        return
    
    print(f"✓ Found tool_use: {tool_use_block['name']}")
    print(f"  Tool ID: {tool_use_block['id']}")
    print(f"  Tool input: {tool_use_block['input']}")
    
    # Step 2: Simulate executing the tool and sending result back
    print("\nStep 2: Sending tool result back...")
    
    # Simulate the result of running 'ls'
    simulated_ls_output = """README.md
server.py
test_proxy.py
test_multiple_tools.py
test_tool_cycle.py
pyproject.toml
uv.lock"""
    
    # Build conversation with tool result
    conversation_messages = [
        {"role": "user", "content": "Please list the files in the current directory using ls"},
        {
            "role": "assistant", 
            "content": response1_json['content']  # Include the full response with tool_use
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_block['id'],
                    "content": simulated_ls_output
                }
            ]
        }
    ]
    
    followup_request = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 300,
        "messages": conversation_messages,
        "tools": [
            {
                "name": "Bash",
                "description": "Execute bash commands",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The bash command to execute"
                        }
                    },
                    "required": ["command"]
                }
            }
        ]
    }
    
    print("Sending followup request with tool result...")
    print("Messages in conversation:", len(conversation_messages))
    print("Tool result content preview:", simulated_ls_output[:50] + "...")
    
    response2 = requests.post(
        "http://localhost:8082/v1/messages",
        headers={
            "content-type": "application/json",
            "x-api-key": "dummy-key"
        },
        json=followup_request,
        timeout=30
    )
    
    print(f"\nResponse 2 status: {response2.status_code}")
    
    if response2.status_code != 200:
        print(f"❌ Error in step 2: {response2.text}")
        return
    
    response2_json = response2.json()
    print(f"Response 2 stop_reason: {response2_json.get('stop_reason')}")
    
    # Check the final response
    print("\nStep 3: Analyzing final response...")
    for i, content in enumerate(response2_json.get('content', [])):
        print(f"Content block {i}: {content.get('type')}")
        if content.get('type') == 'text':
            print(f"  Text: {content['text'][:100]}...")
        elif content.get('type') == 'tool_use':
            print(f"  Tool: {content['name']}")
    
    # Check if the response acknowledges the file listing
    response_text = ""
    for content in response2_json.get('content', []):
        if content.get('type') == 'text':
            response_text += content['text']
    
    if 'README.md' in response_text or 'server.py' in response_text:
        print("✓ Model successfully processed the tool result!")
    else:
        print("⚠ Model response doesn't seem to acknowledge the file listing")
        print(f"Full response text: {response_text}")

if __name__ == "__main__":
    test_tool_cycle()