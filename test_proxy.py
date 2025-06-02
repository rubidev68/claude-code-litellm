#!/usr/bin/env python3

import requests
import json

# Test the proxy with a simple tool call
test_request = {
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 300,
    "messages": [
        {"role": "user", "content": "Please use the bash tool to run 'echo hello world'"}
    ],
    "tools": [
        {
            "name": "bash",
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

print("Testing proxy with tool call request...")
print("Request:", json.dumps(test_request, indent=2))

response = requests.post(
    "http://localhost:8082/v1/messages",
    headers={
        "content-type": "application/json",
        "x-api-key": "dummy-key"  # The proxy likely won't validate this
    },
    json=test_request,
    timeout=30
)

print("\nResponse status:", response.status_code)
print("Response headers:", dict(response.headers))
print("Response body:", response.text)

if response.status_code == 200:
    try:
        response_json = response.json()
        print("\nParsed response:")
        print(json.dumps(response_json, indent=2))
        
        # Check if there's a tool_use in the response
        if 'content' in response_json:
            for content_block in response_json['content']:
                if content_block.get('type') == 'tool_use':
                    print(f"\n✓ Found tool_use: {content_block['name']}")
                    print(f"Tool input: {content_block['input']}")
                else:
                    print(f"\nContent block: {content_block}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")