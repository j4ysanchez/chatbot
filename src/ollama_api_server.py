from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse
import requests
import json
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pytz
import re

OLLAMA_API_URL = "http://10.0.0.245:11434/api/chat"
DEFAULT_MODEL = "mistral-nemo:12b"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple tool functions
def get_current_time(city: str, timezone: str) -> str:
    """Returns the current time in a specified city and timezone

    Args:
        city (str): The name of the city for which to retrieve the current time.
        timezone (str): The timezone for the city.

    Returns:
        dict: status and result or error msg.
    """
    try:
        # Common timezone mappings
    
        city_lower = city.lower().strip()
        timezone_name = timezone
        
        # Try to get the timezone
        try:
            tz = pytz.timezone(timezone_name)
        except pytz.exceptions.UnknownTimeZoneError:
            # If the city isn't in our map, try to use it directly
            tz = pytz.timezone(city)
        
        current_time = datetime.now(tz)
        return f"Current time in {city}: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    
    except Exception as e:
        return f"Error getting time for {city}: {str(e)}"

def get_weather(city: str) -> str:
    """Get weather information for a given city (mock implementation)"""
    weather_data = {
        "new york": "Partly cloudy, 72°F",
        "london": "Rainy, 55°F", 
        "tokyo": "Sunny, 78°F",
        "paris": "Cloudy, 65°F",
        "sydney": "Clear, 82°F"
    }
    
    city_lower = city.lower().strip()
    return weather_data.get(city_lower, f"Weather data not available for {city}")

def detect_tool_calls(content: str):
    """Detect tool calls in the AI response"""
    tool_calls = []
    
    # Pattern to match tool calls like: [TOOL_CALL: tool_name(param1=value1, param2=value2)]
    pattern = r'\[TOOL_CALL:\s*(\w+)\s*\((.*?)\)\]'
    matches = re.findall(pattern, content, re.IGNORECASE)
    
    for match in matches:
        tool_name, params_str = match
        try:
            # Parse parameters
            params = {}
            if params_str.strip():
                param_pairs = params_str.split(',')
                for pair in param_pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        params[key] = value
            
            tool_calls.append({
                "tool": tool_name,
                "parameters": params
            })
        except Exception as e:
            print(f"Error parsing tool call: {e}")
    
    return tool_calls

def execute_tool_calls(tool_calls):
    """Execute tool calls and return results"""
    results = []
    
    for tool_call in tool_calls:
        try:
            tool_name = tool_call["tool"]
            parameters = tool_call["parameters"]
            
            if tool_name == "get_current_time":
                result = get_current_time(**parameters)
            elif tool_name == "get_weather":
                result = get_weather(**parameters)
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

@app.get("/tools")
async def get_tools():
    """Get available tools"""
    return {
        "tools": [
            {
                "name": "get_current_time",
                "description": "Get the current time for a specific city and timezone. Requires city name and timezone (e.g., 'America/New_York', 'Europe/London')"
            },
            {
                "name": "get_weather", 
                "description": "Get weather information for a specific city. Requires city name"
            }
        ]
    }

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    messages = body.get("messages")
    model = body.get("model", DEFAULT_MODEL)
    enable_tools = body.get("enable_tools", True)
    
    if not messages:
        return JSONResponse({"error": "'messages' field is required"}, status_code=400)

    def stream_ollama():
        # Add tool information to the system message if tools are enabled
        if enable_tools:
            tool_instructions = """
You have access to the following tools. When you need to use a tool, format your response like this:
[TOOL_CALL: tool_name(param1=value1, param2=value2)]

Available tools:
- get_current_time(city, timezone): Get the current time for a specific city and timezone. Requires city name and timezone (e.g., "America/New_York", "Europe/London")
- get_weather(city): Get weather information for a specific city. Requires city name
"""
            
            # Add tool instructions to the first message if it's from the user
            if messages and messages[0]["role"] == "user":
                messages[0]["content"] = tool_instructions + "\n\nUser request: " + messages[0]["content"]
        
        payload = {"model": model, "messages": messages}
        full_response = ""
        
        with requests.post(OLLAMA_API_URL, json=payload, stream=True) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                data = json.loads(line.decode("utf-8"))
                content = data.get("message", {}).get("content", "")
                full_response += content
                
                # Check for tool calls in the accumulated response
                if enable_tools:
                    tool_calls = detect_tool_calls(full_response)
                    if tool_calls:
                        # Execute tools and add results to the response
                        tool_results = execute_tool_calls(tool_calls)
                        tool_response = "\n\nTool Results:\n"
                        for result in tool_results:
                            tool_response += f"- {result['tool']}: {result['result']}\n"
                        
                        # Send the original response plus tool results
                        yield json.dumps({
                            "content": full_response + tool_response,
                            "tool_calls": tool_calls,
                            "tool_results": tool_results
                        }).encode() + b"\n"
                        return
                
                yield line + b"\n"
                
                if data.get("done", False):
                    break

    return StreamingResponse(stream_ollama(), media_type="application/json")

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        body = json.loads(data)
        messages = body.get("messages")
        model = body.get("model", DEFAULT_MODEL)
        enable_tools = body.get("enable_tools", True)
        
        if not messages:
            await websocket.send_json({"error": "'messages' field is required"})
            await websocket.close()
            return
        
        # Add tool information to the system message if tools are enabled
        if enable_tools:
            tool_instructions = """
You have access to the following tools. When you need to use a tool, format your response like this:
[TOOL_CALL: tool_name(param1=value1, param2=value2)]

Available tools:
- get_current_time(city, timezone): Get the current time for a specific city and timezone. Requires city name and timezone (e.g., "America/New_York", "Europe/London")
- get_weather(city): Get weather information for a specific city. Requires city name
"""
            
            # Add tool instructions to the first message if it's from the user
            if messages and messages[0]["role"] == "user":
                messages[0]["content"] = tool_instructions + "\n\nUser request: " + messages[0]["content"]
        
        payload = {"model": model, "messages": messages}
        full_response = ""
        
        with requests.post(OLLAMA_API_URL, json=payload, stream=True) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line.decode("utf-8"))
                    content = chunk.get("message", {}).get("content", "")
                    full_response += content
                    
                    # Check for tool calls in the accumulated response
                    if enable_tools:
                        tool_calls = detect_tool_calls(full_response)
                        if tool_calls:
                            # Execute tools and add results to the response
                            tool_results = execute_tool_calls(tool_calls)
                            tool_response = "\n\nTool Results:\n"
                            for result in tool_results:
                                tool_response += f"- {result['tool']}: {result['result']}\n"
                            
                            # Send the complete response with tool results
                            await websocket.send_json({
                                "content": full_response + tool_response,
                                "tool_calls": tool_calls,
                                "tool_results": tool_results,
                                "done": True
                            })
                            return
                    
                    await websocket.send_json({"content": content})
                    if chunk.get("done", False):
                        await websocket.send_json({"done": True})
                        break
                except Exception as e:
                    await websocket.send_json({"error": str(e)})
                    break
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close() 