#!/usr/bin/env python3
"""
Simulate exactly what Claude Code does to identify where tool execution breaks.
This script will step through the exact process Claude Code should follow.
"""

import requests
import json
import time

def simulate_claude_code_session():
    print("=== Simulating Claude Code Tool Execution Session ===\n")
    
    # Headers that Claude Code typically sends
    headers = {
        "content-type": "application/json",
        "anthropic-version": "2023-06-01",
        "x-api-key": "dummy-key"  # Proxy shouldn't validate this
    }
    
    # Step 1: Initial request - user asks for file creation
    print("Step 1: User requests file creation...")
    
    initial_request = {
        "model": "claude-3-5-sonnet-20241022",  # Typical Claude Code model
        "max_tokens": 1000,
        "temperature": 0.7,
        "messages": [
            {
                "role": "user", 
                "content": "Please create a simple HTML file called test.html with basic content"
            }
        ],
        "tools": [
            {
                "name": "Write",
                "description": "Writes a file to the local filesystem.",
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
        ],
        "tool_choice": {"type": "auto"}
    }
    
    print("Sending initial request...")
    response1 = requests.post(
        "http://localhost:8082/v1/messages",
        headers=headers,
        json=initial_request,
        timeout=30
    )
    
    print(f"Response 1 status: {response1.status_code}")
    if response1.status_code != 200:
        print(f"❌ Error: {response1.text}")
        return
    
    response1_json = response1.json()
    print(f"Response 1 stop_reason: {response1_json.get('stop_reason')}")
    
    # Find tool_use blocks
    tool_uses = []
    for content in response1_json.get('content', []):
        if content.get('type') == 'tool_use':
            tool_uses.append(content)
    
    if not tool_uses:
        print("❌ No tool_use blocks found!")
        print("Response content:", json.dumps(response1_json.get('content'), indent=2))
        return
    
    print(f"✓ Found {len(tool_uses)} tool_use block(s)")
    for i, tool in enumerate(tool_uses):
        print(f"  Tool {i+1}: {tool['name']} (ID: {tool['id']})")
        print(f"    Input: {tool['input']}")
    
    # Step 2: Simulate tool execution (what Claude Code should do)
    print(f"\nStep 2: Simulating tool execution...")
    
    # Simulate executing the Write tool
    first_tool = tool_uses[0]
    if first_tool['name'] == 'Write':
        file_path = first_tool['input'].get('file_path', 'test.html')
        content = first_tool['input'].get('content', '<html><body>Hello World</body></html>')
        
        # Simulate writing the file (Claude Code would actually write it)
        simulated_result = f"File written successfully to {file_path}"
        print(f"  Simulated: Write file '{file_path}' with {len(content)} characters")
        print(f"  Result: {simulated_result}")
    else:
        simulated_result = "Tool executed successfully"
    
    # Step 3: Send tool result back (what Claude Code does after executing)
    print(f"\nStep 3: Sending tool result back...")
    
    # Build the conversation with tool result
    conversation = [
        {
            "role": "user", 
            "content": "Please create a simple HTML file called test.html with basic content"
        },
        {
            "role": "assistant",
            "content": response1_json['content']  # The full assistant response with tool_use
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": first_tool['id'],
                    "content": simulated_result
                }
            ]
        }
    ]
    
    followup_request = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1000,
        "temperature": 0.7,
        "messages": conversation,
        "tools": [
            {
                "name": "Write",
                "description": "Writes a file to the local filesystem.",
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
    
    print("Sending followup with tool result...")
    response2 = requests.post(
        "http://localhost:8082/v1/messages",
        headers=headers,
        json=followup_request,
        timeout=30
    )
    
    print(f"Response 2 status: {response2.status_code}")
    if response2.status_code != 200:
        print(f"❌ Error in followup: {response2.text}")
        return
    
    response2_json = response2.json()
    print(f"Response 2 stop_reason: {response2_json.get('stop_reason')}")
    
    # Check if the model acknowledges the completion
    final_text = ""
    for content in response2_json.get('content', []):
        if content.get('type') == 'text':
            final_text += content['text']
    
    print(f"\nStep 4: Final response analysis...")
    print(f"Final response text: {final_text[:200]}...")
    
    if 'created' in final_text.lower() or 'file' in final_text.lower():
        print("✅ Model acknowledged the file creation!")
    else:
        print("⚠ Model response doesn't clearly acknowledge the tool execution")
    
    # Check for any more tool calls
    more_tools = [c for c in response2_json.get('content', []) if c.get('type') == 'tool_use']
    if more_tools:
        print(f"📋 Model wants to call {len(more_tools)} more tools:")
        for tool in more_tools:
            print(f"  - {tool['name']}: {tool['input']}")
    
    return True

def test_streaming_behavior():
    print("\n=== Testing Streaming Behavior ===\n")
    
    headers = {
        "content-type": "application/json",
        "anthropic-version": "2023-06-01",
        "x-api-key": "dummy-key"
    }
    
    request = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 300,
        "temperature": 0.7,
        "stream": True,  # Test streaming
        "messages": [
            {
                "role": "user", 
                "content": "Please write a short Python script to print hello world"
            }
        ],
        "tools": [
            {
                "name": "Write",
                "description": "Writes a file to the local filesystem.",
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
    
    print("Testing streaming request with tools...")
    
    try:
        response = requests.post(
            "http://localhost:8082/v1/messages",
            headers=headers,
            json=request,
            stream=True,
            timeout=30
        )
        
        print(f"Streaming response status: {response.status_code}")
        
        if response.status_code == 200:
            events_received = 0
            tool_use_events = 0
            
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        events_received += 1
                        try:
                            data = json.loads(line_text[6:])
                            if data.get('type') == 'content_block_start':
                                content_block = data.get('content_block', {})
                                if content_block.get('type') == 'tool_use':
                                    tool_use_events += 1
                                    print(f"  Found tool_use in stream: {content_block.get('name')}")
                        except:
                            pass
            
            print(f"Stream summary: {events_received} events, {tool_use_events} tool_use events")
            if tool_use_events > 0:
                print("✅ Streaming tool calls work!")
            else:
                print("⚠ No tool calls in streaming response")
        else:
            print(f"❌ Streaming failed: {response.text}")
    
    except Exception as e:
        print(f"❌ Streaming error: {e}")

if __name__ == "__main__":
    success = simulate_claude_code_session()
    if success:
        test_streaming_behavior()