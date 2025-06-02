#!/usr/bin/env python3
"""
Test Gemini models specifically to identify the issue
"""

import requests
import json
import os

def test_gemini_model(model_name):
    print(f"\n=== Testing {model_name} ===")
    
    headers = {
        "content-type": "application/json",
        "anthropic-version": "2023-06-01",
        "x-api-key": "test-key"
    }
    
    # Test 1: Simple text request (no tools)
    print("Test 1: Simple text request...")
    simple_request = {
        "model": model_name,
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ]
    }
    
    try:
        response = requests.post(
            "http://localhost:8082/v1/messages",
            headers=headers,
            json=simple_request,
            timeout=30
        )
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Success: {data.get('content', [{}])[0].get('text', '')[:50]}...")
        else:
            print(f"  Error: {response.text[:200]}...")
    except Exception as e:
        print(f"  Exception: {e}")
    
    # Test 2: Request with tools
    print("Test 2: Request with tools...")
    tools_request = {
        "model": model_name,
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
    
    try:
        response = requests.post(
            "http://localhost:8082/v1/messages",
            headers=headers,
            json=tools_request,
            timeout=30
        )
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            tool_uses = [c for c in data.get('content', []) if c.get('type') == 'tool_use']
            if tool_uses:
                print(f"  Success: Found {len(tool_uses)} tool calls")
                for tool in tool_uses:
                    print(f"    - {tool['name']}: {tool['input']}")
            else:
                print(f"  No tools called, response: {data.get('content', [])}")
        else:
            print(f"  Error: {response.text[:500]}...")
    except Exception as e:
        print(f"  Exception: {e}")

def check_gemini_config():
    print("=== Checking Gemini Configuration ===")
    
    # Check environment variables
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        print(f"✓ GEMINI_API_KEY is set (length: {len(gemini_key)})")
    else:
        print("❌ GEMINI_API_KEY is not set")
    
    preferred_provider = os.environ.get("PREFERRED_PROVIDER", "openai")
    print(f"PREFERRED_PROVIDER: {preferred_provider}")
    
    big_model = os.environ.get("BIG_MODEL", "default")
    small_model = os.environ.get("SMALL_MODEL", "default")
    print(f"BIG_MODEL: {big_model}")
    print(f"SMALL_MODEL: {small_model}")

def test_model_mapping():
    print("\n=== Testing Model Mapping ===")
    
    # Test with models that should map to Gemini
    test_models = [
        "claude-3-5-sonnet-20241022",  # Should map to big model
        "claude-3-5-haiku-20241022",   # Should map to small model
        "gemini-2.5-flash-preview-05-20",  # Direct Gemini model
        "gemini-2.5-pro-preview-05-06"     # Direct Gemini model
    ]
    
    for model in test_models:
        print(f"\nTesting model mapping for: {model}")
        
        headers = {
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
            "x-api-key": "test-key"
        }
        
        request = {
            "model": model,
            "max_tokens": 50,
            "messages": [
                {"role": "user", "content": "Say hello"}
            ]
        }
        
        try:
            response = requests.post(
                "http://localhost:8082/v1/messages",
                headers=headers,
                json=request,
                timeout=30
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                returned_model = data.get('model', 'unknown')
                print(f"  Mapped to: {returned_model}")
            else:
                print(f"  Error: {response.text[:200]}...")
        except Exception as e:
            print(f"  Exception: {e}")

if __name__ == "__main__":
    check_gemini_config()
    
    # Test specific Gemini models mentioned in the error
    test_gemini_model("gemini-2.5-flash-preview-05-20")
    test_gemini_model("gemini-2.5-pro-preview-05-06")
    
    test_model_mapping()