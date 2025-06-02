#!/usr/bin/env python3
"""
Test with the exact headers and format that Claude Code uses
"""

import requests
import json

# Test with Claude Code's typical headers and model
def test_claude_code_format():
    print("Testing with Claude Code format...")
    
    # Headers that Claude Code actually sends
    headers = {
        "content-type": "application/json",
        "anthropic-version": "2023-06-01",
        "x-api-key": "test-key"  # Claude Code uses the actual API key
    }
    
    # Request format that matches Claude Code exactly
    request = {
        "model": "claude-3-5-sonnet-20241022",  # Exact model Claude Code uses
        "max_tokens": 8192,  # Claude Code's typical max tokens
        "messages": [
            {
                "role": "user",
                "content": "Please create a simple test file called hello.txt with the content 'Hello World'"
            }
        ],
        "tools": [
            {
                "name": "Write",
                "description": "Writes a file to the local filesystem.\n\nUsage:\n- The file_path parameter must be an absolute path, not a relative path\n- By default, it reads up to 2000 lines starting from the beginning of the file\n- You can optionally specify a line offset and limit (especially handy for long files), but it's recommended to read the whole file by not providing these parameters\n- Any lines longer than 2000 characters will be truncated\n- Results are returned using cat -n format, with line numbers starting at 1\n- This tool allows Claude Code to read images (eg PNG, JPG, etc). When reading an image file the contents are presented visually as Claude Code is a multimodal LLM.\n- For Jupyter notebooks (.ipynb files), use the NotebookRead instead\n- You have the capability to call multiple tools in a single response. It is always better to speculatively read multiple files as a batch that are potentially useful. \n- You will regularly be asked to read screenshots. If the user provides a path to a screenshot ALWAYS use this tool to view the file at the path. This tool will work with all temporary file paths like /var/folders/123/abc/T/TemporaryItems/NSIRD_screencaptureui_ZfB1tD/Screenshot.png\n- If you read a file that exists but has empty contents you will receive a system reminder warning in place of file contents.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "description": "The absolute path to the file to write (must be absolute, not relative)",
                            "type": "string"
                        },
                        "content": {
                            "description": "The content to write to the file",
                            "type": "string"
                        }
                    },
                    "required": ["file_path", "content"],
                    "additionalProperties": False
                }
            }
        ]
    }
    
    print("Sending request with Claude Code format...")
    print(f"Model: {request['model']}")
    print(f"Max tokens: {request['max_tokens']}")
    print(f"Tool: {request['tools'][0]['name']}")
    
    response = requests.post(
        "http://localhost:8082/v1/messages",
        headers=headers,
        json=request,
        timeout=30
    )
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Stop reason: {data.get('stop_reason')}")
        
        tool_uses = [c for c in data.get('content', []) if c.get('type') == 'tool_use']
        if tool_uses:
            print(f"✅ Tool use found: {tool_uses[0]['name']}")
            print(f"   Input: {tool_uses[0]['input']}")
            print(f"   ID: {tool_uses[0]['id']}")
        else:
            print("❌ No tool use found")
            print("Content:", json.dumps(data.get('content'), indent=2))
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    test_claude_code_format()