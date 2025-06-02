#!/usr/bin/env python3
"""
Debug script to help troubleshoot Claude Code tool execution issues.

Usage:
1. Enable debug logging in server.py by changing level to logging.DEBUG
2. Run Claude Code with the proxy
3. Look for the "🔍 RAW REQUEST from client:" logs to see what Claude Code is sending
4. Compare with expected format

This script shows what a typical tool execution flow should look like.
"""

import requests
import json

def show_expected_tool_flow():
    print("=== Expected Tool Execution Flow ===\n")
    
    print("1. Initial request (user asks for file operation):")
    initial_request = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 300,
        "messages": [
            {"role": "user", "content": "Please create a file called test.txt with content 'Hello World'"}
        ],
        "tools": [
            {
                "name": "Write",
                "description": "Write content to a file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["file_path", "content"]
                }
            }
        ]
    }
    print(json.dumps(initial_request, indent=2))
    
    print("\n2. Expected response (model returns tool_use):")
    expected_response = {
        "content": [
            {"type": "text", "text": "I'll create the file for you."},
            {
                "type": "tool_use",
                "id": "toolu_123456",
                "name": "Write", 
                "input": {"file_path": "test.txt", "content": "Hello World"}
            }
        ],
        "stop_reason": "tool_use"
    }
    print(json.dumps(expected_response, indent=2))
    
    print("\n3. Tool result (Claude Code executes tool and sends result):")
    tool_result_request = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 300,
        "messages": [
            {"role": "user", "content": "Please create a file called test.txt with content 'Hello World'"},
            {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "I'll create the file for you."},
                    {
                        "type": "tool_use",
                        "id": "toolu_123456",
                        "name": "Write",
                        "input": {"file_path": "test.txt", "content": "Hello World"}
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "toolu_123456",
                        "content": "File created successfully at: /path/to/test.txt"
                    }
                ]
            }
        ]
    }
    print(json.dumps(tool_result_request, indent=2))
    
    print("\n4. Final response (model acknowledges completion):")
    final_response = {
        "content": [
            {"type": "text", "text": "Perfect! I've successfully created the file test.txt with the content 'Hello World'."}
        ],
        "stop_reason": "end_turn"
    }
    print(json.dumps(final_response, indent=2))

def debug_tips():
    print("\n=== Debugging Tips ===\n")
    
    print("If Claude Code tools aren't working through the proxy:")
    print("1. Enable debug logging in server.py (change level to logging.DEBUG)")
    print("2. Look for '🔍 RAW REQUEST from client:' logs")
    print("3. Check that:")
    print("   - Tool definitions have proper input_schema")
    print("   - tool_use responses have 'id', 'name', and 'input' fields")
    print("   - tool_result messages have 'tool_use_id' and 'content' fields")
    print("   - Content can be string OR list of content blocks")
    
    print("\n4. Common issues:")
    print("   - Model mapped incorrectly (check model validation logs)")
    print("   - Tool schema incompatible with target LLM")
    print("   - tool_result content format not recognized")
    print("   - Missing required fields in tool definitions")
    
    print("\n5. Test the proxy independently:")
    print("   python test_proxy.py                    # Basic tool call")
    print("   python test_multiple_tools_cycle.py     # Multiple tools")
    print("   python test_complex_tool_result.py      # Complex tool results")

def test_proxy_health():
    print("\n=== Proxy Health Check ===\n")
    
    try:
        response = requests.get("http://localhost:8082/", timeout=5)
        if response.status_code == 200:
            print("✓ Proxy is running")
            print(f"  Response: {response.json()}")
        else:
            print(f"⚠ Proxy returned {response.status_code}")
    except Exception as e:
        print(f"❌ Proxy is not responding: {e}")
        print("Make sure the server is running with:")
        print("  uvicorn server:app --host 0.0.0.0 --port 8082 --reload")

if __name__ == "__main__":
    test_proxy_health()
    show_expected_tool_flow()
    debug_tips()