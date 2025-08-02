#!/usr/bin/env python3
"""
Test script for the simplified chat API with tools functionality
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_get_tools():
    """Test getting available tools"""
    print("=== Testing GET /tools ===")
    response = requests.get(f"{API_BASE_URL}/tools")
    print(f"Status: {response.status_code}")
    print("Available tools:")
    for tool in response.json()["tools"]:
        print(f"  - {tool['name']}: {tool['description']}")
    print()

def test_chat_with_tools():
    """Test chat endpoint with tools enabled"""
    print("=== Testing POST /chat with tools ===")
    
    # Test cases
    test_cases = [
        {
            "name": "Get current time",
            "message": "What's the current time in Tokyo with timezone Asia/Tokyo?"
        },
        {
            "name": "Get weather",
            "message": "What's the weather like in London?"
        },
        {
            "name": "Multiple tools",
            "message": "What's the time in New York with timezone America/New_York and what's the weather like there?"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        print(f"User: {test_case['message']}")
        
        payload = {
            "messages": [
                {"role": "user", "content": test_case['message']}
            ],
            "enable_tools": True
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/chat",
                json=payload,
                stream=True
            )
            
            print("Assistant: ", end="")
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode('utf-8'))
                    if "content" in data:
                        print(data["content"], end="")
                    if "tool_calls" in data:
                        print(f"\n[Tool calls detected: {data['tool_calls']}]")
                    if "tool_results" in data:
                        print(f"\n[Tool results: {data['tool_results']}]")
                    if data.get("done", False):
                        break
            print("\n")
            
        except Exception as e:
            print(f"Error: {e}")

def test_chat_without_tools():
    """Test chat endpoint with tools disabled"""
    print("=== Testing POST /chat without tools ===")
    
    payload = {
        "messages": [
            {"role": "user", "content": "What's the current time in Tokyo with timezone Asia/Tokyo?"}
        ],
        "enable_tools": False
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            stream=True
        )
        
        print("User: What's the current time in Tokyo with timezone Asia/Tokyo?")
        print("Assistant: ", end="")
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8'))
                if "content" in data:
                    print(data["content"], end="")
                if data.get("done", False):
                    break
        print("\n")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing Simplified Chat API with Tools")
    print("=" * 45)
    
    try:
        test_get_tools()
        test_chat_with_tools()
        test_chat_without_tools()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
        print("Run: uvicorn src.ollama_api_server:app --reload") 