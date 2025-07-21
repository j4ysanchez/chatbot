from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
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

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        body = json.loads(data)
        messages = body.get("messages")
        model = body.get("model", DEFAULT_MODEL)
        if not messages:
            await websocket.send_json({"error": "'messages' field is required"})
            await websocket.close()
            return
        payload = {"model": model, "messages": messages}
        with requests.post(OLLAMA_API_URL, json=payload, stream=True) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line.decode("utf-8"))
                    content = chunk.get("message", {}).get("content", "")
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