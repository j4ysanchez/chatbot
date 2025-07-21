from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import requests
import json

OLLAMA_API_URL = "http://10.0.0.245:11434/api/chat"
DEFAULT_MODEL = "gemma3:4b"

app = FastAPI()

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    messages = body.get("messages")
    model = body.get("model", DEFAULT_MODEL)

    print(f"Received request: {messages} {model}")
    if not messages:
        return JSONResponse({"error": "'messages' field is required"}, status_code=400)

    def stream_ollama():
        payload = {"model": model, "messages": messages}
        with requests.post(OLLAMA_API_URL, json=payload, stream=True) as resp:
            resp.raise_for_status()
            reply = ""
            for line in resp.iter_lines():
                if not line:
                    continue
                data = json.loads(line.decode("utf-8"))
                content = data.get("message", {}).get("content", "")
                print(content)
                reply += content   
                if data.get("done", False):
                    break
            return reply
            return ""


    return StreamingResponse(stream_ollama(), media_type="application/json") 