# Simplified Chat API with Tools

This document explains how to use the simplified tool system in your chat API, which allows the AI to execute specific functions like getting the current time and weather information.

## Overview

The simplified tool system consists of:
- **Tool Functions**: Direct implementations of the tools
- **Tool Detection**: Parses AI responses to detect tool calls
- **Tool Execution**: Runs the detected tools and returns results

## Available Tools

### 1. get_current_time
Gets the current time for a specific city.

**Usage**: `[TOOL_CALL: get_current_time(city="Tokyo")]`

**Supported cities**: New York, London, Paris, Tokyo, Sydney, Los Angeles, Chicago, Miami, San Francisco, Toronto, Vancouver, Berlin, Madrid, Rome, Moscow, Beijing, Shanghai, Seoul, Singapore, Dubai, Mumbai, Delhi, UTC, GMT, and many more.

### 2. get_weather
Gets weather information for a specific city (mock implementation).

**Usage**: `[TOOL_CALL: get_weather(city="London")]`

**Supported cities**: New York, London, Tokyo, Paris, Sydney

## API Endpoints

### GET /tools
Returns the list of available tools.

**Response**:
```json
{
  "tools": [
    {
      "name": "get_current_time",
      "description": "Get the current time for a specific city"
    },
    {
      "name": "get_weather",
      "description": "Get weather information for a specific city"
    }
  ]
}
```

### POST /chat
Chat endpoint with optional tool support.

**Request**:
```json
{
  "messages": [
    {"role": "user", "content": "What's the current time in Tokyo?"}
  ],
  "enable_tools": true,
  "model": "gemma3:4b"
}
```

**Response** (with tools):
```json
{
  "content": "I'll check the current time in Tokyo for you.\n\n[TOOL_CALL: get_current_time(city=\"Tokyo\")]\n\nTool Results:\n- get_current_time: Current time in Tokyo: 2024-01-15 14:30:25 JST",
  "tool_calls": [
    {
      "tool": "get_current_time",
      "parameters": {"city": "Tokyo"}
    }
  ],
  "tool_results": [
    {
      "tool": "get_current_time",
      "result": "Current time in Tokyo: 2024-01-15 14:30:25 JST",
      "success": true
    }
  ]
}
```

### WebSocket /ws/chat
WebSocket endpoint with the same functionality as the POST endpoint.

## How It Works

1. **Tool Instructions**: When `enable_tools` is true, the API automatically adds tool instructions to the user's message, informing the AI about available tools and how to use them.

2. **Tool Call Detection**: The API monitors the AI's response for tool calls in the format `[TOOL_CALL: tool_name(param1=value1, param2=value2)]`.

3. **Tool Execution**: When tool calls are detected, the API executes the corresponding functions and includes the results in the response.

4. **Response Enhancement**: The final response includes both the AI's original response and the tool execution results.

## Adding New Tools

To add a new tool, follow these steps:

### 1. Define the Tool Function
```python
def my_new_tool(param1: str) -> str:
    """Description of what this tool does"""
    # Your tool implementation here
    result = f"Processed {param1}"
    return result
```

### 2. Add Tool Execution Logic
In the `execute_tool_calls` function, add a new condition:

```python
def execute_tool_calls(tool_calls):
    results = []
    
    for tool_call in tool_calls:
        try:
            tool_name = tool_call["tool"]
            parameters = tool_call["parameters"]
            
            if tool_name == "get_current_time":
                result = get_current_time(**parameters)
            elif tool_name == "get_weather":
                result = get_weather(**parameters)
            elif tool_name == "my_new_tool":  # Add your new tool here
                result = my_new_tool(**parameters)
            else:
                result = f"Unknown tool: {tool_name}"
            
            results.append({
                "tool": tool_name,
                "result": result,
                "success": True
            })
        except Exception as e:
            results.append({
                "tool": tool_name,
                "result": f"Error: {str(e)}",
                "success": False
            })
    
    return results
```

### 3. Update Tool Instructions
Add your tool to the tool instructions in both the `/chat` and `/ws/chat` endpoints:

```python
tool_instructions = """
You have access to the following tools. When you need to use a tool, format your response like this:
[TOOL_CALL: tool_name(param1=value1, param2=value2)]

Available tools:
- get_current_time: Get the current time for a specific city
- get_weather: Get weather information for a specific city
- my_new_tool: Description of your new tool
"""
```

### 4. Update GET /tools Endpoint
Add your tool to the tools list:

```python
@app.get("/tools")
async def get_tools():
    return {
        "tools": [
            {
                "name": "get_current_time",
                "description": "Get the current time for a specific city"
            },
            {
                "name": "get_weather", 
                "description": "Get weather information for a specific city"
            },
            {
                "name": "my_new_tool",
                "description": "Description of your new tool"
            }
        ]
    }
```

## Testing

Run the test script to see the tool system in action:

```bash
python test_tools.py
```

Make sure your API server is running first:

```bash
uvicorn src.ollama_api_server:app --reload
```

## Configuration

### Enabling/Disabling Tools
- Set `enable_tools: true` in your request to enable tool functionality
- Set `enable_tools: false` to disable tools and get normal AI responses

### Model Selection
- Tools work with any model that supports the Ollama API
- The default model is `gemma3:4b`
- You can specify a different model in the request

## Security Considerations

1. **Input Validation**: All tool parameters are validated before execution
2. **Error Handling**: Tool execution errors are caught and returned gracefully
3. **Rate Limiting**: Consider implementing rate limiting for tool calls in production

## Dependencies

Make sure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

The tool system requires:
- `pytz` for timezone handling
- `requests` for API calls
- `fastapi` for the web framework
- `uvicorn` for the ASGI server

## Troubleshooting

### Common Issues

1. **Tool not found**: Make sure the tool is properly added to the `execute_tool_calls` function
2. **Parameter parsing errors**: Check that tool call format matches `[TOOL_CALL: tool_name(param=value)]`
3. **Timezone errors**: Ensure the city name is supported or use a valid timezone name
4. **Connection errors**: Verify that the Ollama API is running and accessible

### Debug Mode

To enable debug logging, add this to your server startup:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed information about tool detection and execution. 