# Python CLI Chatbot for Ollama LLM

## Project Setup

1. **Clone or create the project directory**
2. **Set up a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Ollama API Overview

- The chatbot will connect to an Ollama-deployed LLM via HTTP API.
- Typical endpoint: `http://localhost:11434/api/chat` or `http://localhost:11434/api/generate`
- Request format (example):
  ```json
  {
    "model": "llama2",
    "messages": [{"role": "user", "content": "Hello!"}]
  }
  ```
- Response format (example):
  ```json
  {
    "message": {"role": "assistant", "content": "Hi! How can I help you?"}
  }
  ```
- No authentication is required by default for local Ollama deployments.

---

## Running the FastAPI Ollama Proxy

The FastAPI server is now located in the `src` directory.

To run the server:

```bash
uvicorn src.ollama_api_server:app --reload
```

This will start the API at `http://localhost:8000/chat`.

---

## Docker Deployment

### Prerequisites
- Docker and Docker Compose installed
- Ollama server running at `10.0.0.245:11434` (or update the environment variable)

### Build and Run with Docker Compose

1. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

3. **Stop the services:**
   ```bash
   docker-compose down
   ```

### Individual Docker Commands

**Backend only:**
```bash
docker build -t chatbot-backend .
docker run -p 8000:8000 chatbot-backend
```

**Frontend only:**
```bash
cd frontend
docker build -t chatbot-frontend .
docker run -p 3000:80 chatbot-frontend
```

### Environment Variables

You can customize the Ollama API URL by setting the `OLLAMA_API_URL` environment variable:

```bash
export OLLAMA_API_URL=http://your-ollama-server:11434/api/chat
docker-compose up
```

---

Continue to implement the CLI and API client in `chatbot.py`.