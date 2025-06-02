#!/usr/bin/env python3
"""
Test anthropic/ models to ensure they get proper tool_use blocks
"""

import requests
import json

def test_anthropic_model_detection():
    print("=== Testing Anthropic Model Detection ===\n")
    
    # Test cases for different anthropic/ models
    test_cases = [
        {
            "model": "anthropic/claude-sonnet-4-20250514",
            "description": "Direct anthropic/ model"
        },
        {
            "model": "anthropic/claude-3-5-haiku-latest", 
            "description": "Direct anthropic/ model"
        },
        {
            "model": "claude-3-5-sonnet-20241022",
            "description": "Claude model that might map to anthropic/"
        },
        {
            "model": "claude-3-5-haiku-20241022",
            "description": "Claude model that might map to anthropic/"
        }
    ]
    
    headers = {
        "content-type": "application/json",
        "anthropic-version": "2023-06-01",
        "x-api-key": "test-key"
    }
    
    for test_case in test_cases:
        model = test_case["model"]
        description = test_case["description"]
        
        print(f"Testing: {model}")
        print(f"Description: {description}")
        
        request = {
            "model": model,
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
                json=request,
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Mapped to: {data.get('model')}")
                print(f"Stop reason: {data.get('stop_reason')}")
                
                # Check for tool_use blocks
                tool_uses = [c for c in data.get('content', []) if c.get('type') == 'tool_use']
                text_blocks = [c for c in data.get('content', []) if c.get('type') == 'text']
                
                if tool_uses:
                    print(f"✅ Found {len(tool_uses)} tool_use blocks (correct for Claude models)")
                    for i, tool in enumerate(tool_uses):
                        print(f"   Tool {i+1}: {tool['name']} (ID: {tool['id'][:12]}...)")
                        print(f"   Input: {tool['input']}")
                else:
                    print("❌ No tool_use blocks found")
                    
                # Check if it was converted to text (wrong behavior)
                if text_blocks:
                    for text_block in text_blocks:
                        if 'Tool usage:' in text_block.get('text', ''):
                            print("❌ Tools were converted to text (incorrect for Claude models)")
                            print(f"   Text: {text_block['text'][:100]}...")
                            break
                
            else:
                error_text = response.text
                print(f"Error: {error_text[:200]}...")
                
                # Check for specific error types
                if "anthropic" in error_text.lower() and "api" in error_text.lower():
                    print("   → This indicates the model is correctly routed to Anthropic API")
                elif "not found" in error_text.lower():
                    print("   → Model mapping might need adjustment")
                
        except Exception as e:
            print(f"Exception: {e}")
        
        print("-" * 50)

def test_environment_setup():
    print("=== Environment Setup for Anthropic Models ===\n")
    
    print("To use anthropic/ models, set these environment variables:")
    print("export BIG_MODEL=anthropic/claude-sonnet-4-20250514")
    print("export SMALL_MODEL=anthropic/claude-3-5-haiku-latest")
    print("export ANTHROPIC_API_KEY=your_anthropic_api_key")
    print()
    
    print("Or for mapping Claude requests to anthropic/ models:")
    print("export PREFERRED_PROVIDER=anthropic  # Would need to be implemented")
    print()
    
    print("Test with direct anthropic/ model names:")
    print("Model: anthropic/claude-sonnet-4-20250514")
    print("Expected: Should get tool_use blocks, not text conversion")

if __name__ == "__main__":
    test_environment_setup()
    print()
    test_anthropic_model_detection()