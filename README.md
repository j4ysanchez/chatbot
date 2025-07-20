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

Continue to implement the CLI and API client in `chatbot.py`.