# Debugging Claude Code Tool Execution Through Proxy

## Summary of Testing Results ✅

All proxy functionality is working correctly:
- ✅ Tool calls are generated properly
- ✅ Tool results are processed correctly  
- ✅ Both streaming and non-streaming work
- ✅ Multiple tools in sequence work
- ✅ Complex tool result formats are handled
- ✅ Model mapping works correctly

## To Debug Your Claude Code Issue

### 1. Enable Debug Logging

In `server.py`, ensure logging is set to DEBUG:
```python
logging.basicConfig(
    level=logging.DEBUG,  # This line should be DEBUG, not INFO
    format='%(asctime)s - %(levelname)s - %(message)s',
)
```

### 2. Watch the Logs While Using Claude Code

In one terminal, run Claude Code:
```bash
ANTHROPIC_BASE_URL=http://localhost:8082 claude
```

In another terminal, watch the proxy logs:
```bash
cd "/path/to/claude-code-litellm"
# If server is already running, restart it to see logs:
uv run uvicorn server:app --host 0.0.0.0 --port 8082 --reload
```

### 3. Look for These Debug Patterns

**When Claude Code makes a request, you should see:**
```
🔍 RAW REQUEST from client:
   Model: claude-3-5-sonnet-20241022
   Messages count: 1
   Message 0 (user): <class 'str'>
   Tools: ['Write', 'Read', 'Bash', ...]
   Stream: False
   Max tokens: 8192
```

**When proxy responds with tool calls:**
```
📤 RESPONSE to client:
   Stop reason: tool_use
   Content blocks: 2
     Block 0: text - I'll create that file for you...
     Block 1: tool_use - Write (ID: toolu_123456...)
```

**When Claude Code sends tool results back:**
```
🔍 RAW REQUEST from client:
   Model: claude-3-5-sonnet-20241022
   Messages count: 3
   Message 0 (user): <class 'str'>
   Message 1 (assistant): <class 'list'>
   Message 2 (user): <class 'list'>
     Block 0: tool_result - {'type': 'tool_result', 'tool_use_id': '...', 'content': 'File created successfully...'}
```

### 4. Common Issues to Check

#### Issue 1: No Debug Logs Appearing
- **Cause**: Logging level not set to DEBUG
- **Fix**: Edit `server.py` line 23 to `level=logging.DEBUG`

#### Issue 2: Requests Not Reaching Proxy
- **Cause**: Wrong URL or proxy not running
- **Fix**: Check `http://localhost:8082` returns `{"message": "Anthropic Proxy for LiteLLM"}`

#### Issue 3: API Key Issues
- **Cause**: Proxy trying to validate API key
- **Check**: Look for authentication errors in logs
- **Fix**: Ensure proxy has valid OPENAI_API_KEY or GEMINI_API_KEY in environment

#### Issue 4: Model Mapping Issues
- **Check**: Look for "MODEL MAPPING" logs showing model transformation
- **Expected**: `claude-3-5-sonnet-20241022` → `openai/gpt-4.1` or similar

#### Issue 5: Tool Schema Issues
- **Check**: Look for warnings about tool schema cleaning or conversion
- **Fix**: Proxy automatically handles this for Gemini models

### 5. Test Scripts Available

Run these to verify proxy functionality:
```bash
python test_proxy.py                    # Basic tool call
python test_multiple_tools_cycle.py     # Multiple tools  
python test_complex_tool_result.py      # Complex results
python test_claude_code_simulation.py   # Full Claude Code simulation
python test_claude_code_headers.py      # Exact Claude Code format
```

### 6. Expected Behavior

1. **User asks for file operation**
2. **Proxy receives request** → Debug log `🔍 RAW REQUEST`
3. **Proxy returns tool_use** → Debug log `📤 RESPONSE` with `tool_use` block
4. **Claude Code executes tool** (creates file, runs command, etc.)
5. **Claude Code sends tool_result** → Debug log `🔍 RAW REQUEST` with `tool_result`
6. **Proxy processes result** → Returns acknowledgment

### 7. If Tools Still Don't Execute

The proxy is working correctly based on our tests. If Claude Code still doesn't execute tools, the issue is likely:

1. **Claude Code configuration** - Try setting different model names
2. **Environment variables** - Double-check `ANTHROPIC_BASE_URL=http://localhost:8082`
3. **Network issues** - Test with `curl` to verify proxy responds
4. **Claude Code version** - Try updating to latest version

### 8. Quick Verification Commands

```bash
# Test proxy is running
curl http://localhost:8082

# Test with exact Claude Code request
curl -X POST http://localhost:8082/v1/messages \
  -H "Content-Type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: test" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 1000,
    "messages": [{"role": "user", "content": "Create a file called test.txt"}],
    "tools": [{"name": "Write", "description": "Write file", "input_schema": {"type": "object", "properties": {"file_path": {"type": "string"}, "content": {"type": "string"}}, "required": ["file_path", "content"]}}]
  }'
```

## Conclusion

The proxy is functioning correctly. All tests pass, and tool execution works as expected. The issue is likely in the Claude Code configuration or environment setup, not the proxy itself.

Use the debug logging to identify exactly where the communication breaks down.