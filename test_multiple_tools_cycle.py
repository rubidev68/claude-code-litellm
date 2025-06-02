#!/usr/bin/env python3

import requests
import json

def test_multiple_tools_in_sequence():
    print("=== Testing Multiple Tools in Sequence ===\n")
    
    # Step 1: Request that should trigger multiple tool calls
    print("Step 1: Requesting task that requires multiple tools...")
    
    initial_request = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 500,
        "messages": [
            {"role": "user", "content": "Please create a simple text file called 'hello.txt' with the content 'Hello World', then list the files to confirm it was created."}
        ],
        "tools": [
            {
                "name": "Write",
                "description": "Write content to a file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "The path to write to"},
                        "content": {"type": "string", "description": "The content to write"}
                    },
                    "required": ["file_path", "content"]
                }
            },
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
        ],
        "tool_choice": {"type": "auto"}
    }
    
    response1 = requests.post(
        "http://localhost:8082/v1/messages",
        headers={"content-type": "application/json", "x-api-key": "dummy-key"},
        json=initial_request,
        timeout=30
    )
    
    print(f"Response 1 status: {response1.status_code}")
    
    if response1.status_code != 200:
        print(f"Error: {response1.text}")
        return
    
    response1_json = response1.json()
    print(f"Response 1 stop_reason: {response1_json.get('stop_reason')}")
    
    # Find all tool_use blocks
    tool_use_blocks = []
    for content in response1_json.get('content', []):
        if content.get('type') == 'tool_use':
            tool_use_blocks.append(content)
    
    print(f"Found {len(tool_use_blocks)} tool_use blocks:")
    for i, tool in enumerate(tool_use_blocks):
        print(f"  Tool {i+1}: {tool['name']} (ID: {tool['id']})")
        print(f"    Input: {tool['input']}")
    
    if len(tool_use_blocks) == 0:
        print("❌ No tools called - this might indicate the model chose not to use tools")
        print("Response content:", json.dumps(response1_json.get('content'), indent=2))
        return
    
    # The key test: does the model call multiple tools in one response, or just one?
    if len(tool_use_blocks) == 1:
        print(f"\n🔍 Model called only 1 tool: {tool_use_blocks[0]['name']}")
        print("This suggests the model prefers to do tools one at a time")
        
        # Test continuing the conversation
        print("\nSimulating tool execution and continuing...")
        
        # Simulate executing the first tool
        first_tool = tool_use_blocks[0]
        if first_tool['name'] == 'Write':
            simulated_result = "File 'hello.txt' created successfully"
        else:
            simulated_result = "Command executed successfully"
        
        # Continue conversation
        conversation_messages = [
            {"role": "user", "content": "Please create a simple text file called 'hello.txt' with the content 'Hello World', then list the files to confirm it was created."},
            {"role": "assistant", "content": response1_json['content']},
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
        
        # Send follow-up request
        followup_request = initial_request.copy()
        followup_request["messages"] = conversation_messages
        
        response2 = requests.post(
            "http://localhost:8082/v1/messages",
            headers={"content-type": "application/json", "x-api-key": "dummy-key"},
            json=followup_request,
            timeout=30
        )
        
        print(f"\nFollow-up response status: {response2.status_code}")
        
        if response2.status_code == 200:
            response2_json = response2.json()
            print(f"Follow-up stop_reason: {response2_json.get('stop_reason')}")
            
            # Check for more tools
            more_tools = [c for c in response2_json.get('content', []) if c.get('type') == 'tool_use']
            if more_tools:
                print(f"✓ Found {len(more_tools)} more tools in follow-up:")
                for tool in more_tools:
                    print(f"  - {tool['name']}: {tool['input']}")
            else:
                print("No more tools in follow-up response")
                # Check if it mentions the task completion
                text_content = " ".join([c.get('text', '') for c in response2_json.get('content', []) if c.get('type') == 'text'])
                print(f"Text response: {text_content[:200]}...")
        
    elif len(tool_use_blocks) > 1:
        print(f"\n✓ Model called {len(tool_use_blocks)} tools in one response!")
        print("This suggests the model can handle multiple tools per turn")
        
        # Test executing all tools
        tool_results = []
        for tool in tool_use_blocks:
            if tool['name'] == 'Write':
                result = "File created successfully"
            elif tool['name'] == 'Bash':
                result = "hello.txt\nREADME.md\nserver.py\n..."
            else:
                result = "Tool executed successfully"
            
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool['id'],
                "content": result
            })
        
        print(f"Simulating execution of all {len(tool_results)} tools...")

if __name__ == "__main__":
    test_multiple_tools_in_sequence()