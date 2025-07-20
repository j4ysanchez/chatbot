import requests
import sys
from rich.console import Console
from rich.prompt import Prompt
import json

OLLAMA_API_URL = "http://10.0.0.245:11434/api/chat"
MODEL_NAME = "gemma3:4b"  # Change as needed

console = Console()

def stream_chat(messages):
    payload = {
        "model": MODEL_NAME,
        "messages": messages
    }
    try:
        with requests.post(OLLAMA_API_URL, json=payload, stream=True) as resp:
            resp.raise_for_status()
            reply = ""
            for line in resp.iter_lines():
                if not line:
                    continue
                data = json.loads(line.decode("utf-8"))
                content = data.get("message", {}).get("content", "")
                console.print(content, end="", style="bold green")
                reply += content
                if data.get("done", False):
                    break
            console.print()  # Newline after response
            return reply
            return ""
    except Exception as e:
        console.print(f"[red]Error communicating with Ollama API: {e}")
        return ""

def main():
    console.print("[bold blue]Ollama CLI Chatbot[/bold blue]")
    messages = []
    while True:
        try:
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[bold yellow]Goodbye![/bold yellow]")
            break
        if user_input.strip().lower() in {"exit", "quit"}:
            console.print("[bold yellow]Goodbye![/bold yellow]")
            break
        messages.append({"role": "user", "content": user_input})
        reply = stream_chat(messages)
        messages.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main() 