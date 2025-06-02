#!/usr/bin/env python3

import requests
import json

def test_complex_tool_result():
    print("=== Testing Complex Tool Result Handling ===\n")
    
    # Simulate what Claude Code might send as a tool result
    # This mimics the complex structure Claude Code uses
    
    messages = [
        {"role": "user", "content": "Please list files in the current directory"},
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "I'll list the files for you."},
                {
                    "type": "tool_use",
                    "id": "toolu_123456789",
                    "name": "Bash",
                    "input": {"command": "ls -la"}
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "toolu_123456789",
                    "content": [
                        {
                            "type": "text",
                            "text": "total 48\ndrwxr-xr-x  8 user user  4096 May 28 13:15 .\ndrwxr-xr-x  3 user user  4096 May 28 12:30 ..\n-rw-r--r--  1 user user  1234 May 28 13:10 README.md\n-rw-r--r--  1 user user  8765 May 28 13:12 server.py\n-rw-r--r--  1 user user   567 May 28 13:15 test.py"
                        }
                    ]
                }
            ]
        }
    ]
    
    request_data = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 300,
        "messages": messages,
        "tools": [
            {
                "name": "Bash",
                "description": "Execute bash commands",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "The bash command to execute"}
                    },
                    "required": ["command"]
                }
            }
        ]
    }
    
    print("Testing complex tool_result structure...")
    print(f"Messages in conversation: {len(messages)}")
    print(f"Last message content type: {type(messages[-1]['content'])}")
    print(f"Tool result content structure: {json.dumps(messages[-1]['content'][0]['content'], indent=2)}")
    
    response = requests.post(
        "http://localhost:8082/v1/messages",
        headers={"content-type": "application/json", "x-api-key": "dummy-key"},
        json=request_data,
        timeout=30
    )
    
    print(f"\nResponse status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Error: {response.text}")
        return
    
    response_json = response.json()
    print(f"Response stop_reason: {response_json.get('stop_reason')}")
    
    # Check if the model properly processed the tool result
    text_content = ""
    for content in response_json.get('content', []):
        if content.get('type') == 'text':
            text_content += content['text']
    
    print(f"\nResponse text preview: {text_content[:200]}...")
    
    # Check if it mentions the files from the ls output
    expected_files = ['README.md', 'server.py', 'test.py']
    mentioned_files = [f for f in expected_files if f in text_content]
    
    print(f"Files mentioned in response: {mentioned_files}")
    
    if len(mentioned_files) >= 2:
        print("✓ Model successfully processed complex tool result!")
    else:
        print("⚠ Model may not have properly processed the tool result")

def test_simple_tool_result():
    print("\n=== Testing Simple Tool Result (String Content) ===\n")
    
    # Test with simple string content (what our previous tests used)
    messages = [
        {"role": "user", "content": "Please list files in the current directory"},
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "I'll list the files for you."},
                {
                    "type": "tool_use",
                    "id": "toolu_123456789",
                    "name": "Bash",
                    "input": {"command": "ls -la"}
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "toolu_123456789",
                    "content": "total 48\ndrwxr-xr-x  8 user user  4096 May 28 13:15 .\ndrwxr-xr-x  3 user user  4096 May 28 12:30 ..\n-rw-r--r--  1 user user  1234 May 28 13:10 README.md\n-rw-r--r--  1 user user  8765 May 28 13:12 server.py\n-rw-r--r--  1 user user   567 May 28 13:15 test.py"
                }
            ]
        }
    ]
    
    request_data = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 300,
        "messages": messages,
        "tools": [
            {
                "name": "Bash",
                "description": "Execute bash commands",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "The bash command to execute"}
                    },
                    "required": ["command"]
                }
            }
        ]
    }
    
    print("Testing simple string tool_result...")
    
    response = requests.post(
        "http://localhost:8082/v1/messages",
        headers={"content-type": "application/json", "x-api-key": "dummy-key"},
        json=request_data,
        timeout=30
    )
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        response_json = response.json()
        text_content = " ".join([c.get('text', '') for c in response_json.get('content', []) if c.get('type') == 'text'])
        expected_files = ['README.md', 'server.py', 'test.py']
        mentioned_files = [f for f in expected_files if f in text_content]
        print(f"Files mentioned: {mentioned_files}")
        
        if len(mentioned_files) >= 2:
            print("✓ Simple tool result works!")
        else:
            print("⚠ Issue with simple tool result")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    test_complex_tool_result()
    test_simple_tool_result()