#!/usr/bin/env python3
"""
Test the proxy with Gemini environment variables
"""

import requests
import json
import os

def test_model_mapping():
    print("=== Testing Model Mapping with Gemini Environment ===")
    
    # Simulate the environment variables you should set
    print("For your setup, you should set these environment variables:")
    print("export PREFERRED_PROVIDER=google")
    print("export GEMINI_API_KEY=your_gemini_api_key_here")
    print("export BIG_MODEL=gemini-2.5-pro-preview-05-06")
    print("export SMALL_MODEL=gemini-2.5-flash-preview-05-20")
    print()
    
    # Test model mappings
    test_cases = [
        ("claude-3-5-sonnet-20241022", "Should map to BIG_MODEL"),
        ("claude-3-5-haiku-20241022", "Should map to SMALL_MODEL"),
        ("gemini-2.5-pro-preview-05-06", "Should get gemini/ prefix"),
        ("gemini-2.5-flash-preview-05-20", "Should get gemini/ prefix")
    ]
    
    headers = {
        "content-type": "application/json",
        "anthropic-version": "2023-06-01",
        "x-api-key": "test-key"
    }
    
    for model, description in test_cases:
        print(f"Testing: {model} ({description})")
        
        request = {
            "model": model,
            "max_tokens": 50,
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        try:
            response = requests.post(
                "http://localhost:8082/v1/messages",
                headers=headers,
                json=request,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                mapped_model = data.get('model', 'unknown')
                print(f"  ✓ Success: {model} → {mapped_model}")
            else:
                print(f"  ❌ Error: {response.status_code}")
                error_text = response.text[:200]
                if "No module named 'google'" in error_text:
                    print("    → Google dependencies installed successfully")
                elif "GEMINI_API_KEY" in error_text:
                    print("    → Need to set GEMINI_API_KEY environment variable")
                else:
                    print(f"    → {error_text}...")
        except Exception as e:
            print(f"  ❌ Exception: {e}")
        
        print()

def create_env_file_template():
    print("=== Creating .env.example for Gemini ===")
    
    env_content = """# Anthropic API Key (optional, only needed if using anthropic/ models)
ANTHROPIC_API_KEY=your_anthropic_key_here

# OpenAI API Key (for fallback or if using openai/ models)
OPENAI_API_KEY=your_openai_key_here

# Gemini API Key (required for Gemini models)
GEMINI_API_KEY=your_gemini_key_here

# Provider preference (openai or google)
PREFERRED_PROVIDER=google

# Model mappings
BIG_MODEL=gemini-2.5-pro-preview-05-06
SMALL_MODEL=gemini-2.5-flash-preview-05-20

# Optional: Custom OpenAI API base URL
# OPENAI_API_BASE=http://localhost:4000/v1
"""
    
    try:
        with open('/home/anatole/Documents/ENSI/Stage 2A/claude-code-litellm/.env.example', 'w') as f:
            f.write(env_content)
        print("✓ Created .env.example file")
        print("Copy it to .env and fill in your API keys:")
        print("  cp .env.example .env")
        print("  # Edit .env with your actual API keys")
    except Exception as e:
        print(f"❌ Error creating .env.example: {e}")

if __name__ == "__main__":
    create_env_file_template()
    print()
    test_model_mapping()