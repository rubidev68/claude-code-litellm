#!/usr/bin/env python3

import requests
import json

# Test the proxy with multiple tool calls
test_request = {
    "model": "claude-3-haiku-20240307",  # Test with haiku model too
    "max_tokens": 500,
    "messages": [
        {"role": "user", "content": "Please list the files in the current directory using ls, then create a new file called test.txt with the content 'Hello World'"}
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
        },
        {
            "name": "Write", 
            "description": "Write content to a file",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path of the file to write"
                    },
                    "content": {
                        "type": "string", 
                        "description": "The content to write to the file"
                    }
                },
                "required": ["file_path", "content"]
            }
        }
    ],
    "tool_choice": {"type": "auto"}
}

print("Testing proxy with multiple tools...")

response = requests.post(
    "http://localhost:8082/v1/messages",
    headers={
        "content-type": "application/json",
        "x-api-key": "dummy-key"
    },
    json=test_request,
    timeout=30
)

print(f"\nResponse status: {response.status_code}")

if response.status_code == 200:
    try:
        response_json = response.json()
        print("\nResponse content blocks:")
        
        tool_uses = []
        for i, content_block in enumerate(response_json.get('content', [])):
            print(f"\nBlock {i}: {content_block.get('type')}")
            if content_block.get('type') == 'tool_use':
                tool_uses.append(content_block)
                print(f"  Tool: {content_block['name']}")
                print(f"  Input: {json.dumps(content_block['input'], indent=4)}")
            elif content_block.get('type') == 'text':
                print(f"  Text: {content_block['text'][:100]}...")
        
        print(f"\n✓ Found {len(tool_uses)} tool_use blocks")
        
        # Test that we get the expected tools
        expected_tools = {'Bash', 'Write'}
        actual_tools = {tool['name'] for tool in tool_uses}
        
        if expected_tools.intersection(actual_tools):
            print(f"✓ Expected tools present: {actual_tools}")
        else:
            print(f"⚠ Unexpected tools: {actual_tools}")
            
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Raw response: {response.text}")
else:
    print(f"Error response: {response.text}")