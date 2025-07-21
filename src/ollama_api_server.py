from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import requests
import json
from fastapi.middleware.cors import CORSMiddleware

OLLAMA_API_URL = "http://10.0.0.245:11434/api/chat"
DEFAULT_MODEL = "gemma3:4b"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            for line in resp.iter_lines():
                if not line:
                    continue
                yield line + b"\n"  # Yield each JSON line as soon as it arrives


    return StreamingResponse(stream_ollama(), media_type="application/json") 