"""Ollama LLM Connector — lokale Inference via Ollama REST API."""

import requests
from rich.console import Console

console = Console()

OLLAMA_URL = "http://localhost:11434/api/chat"

# Model Mapping
MODELS = {
    "coder": "qwen2.5-coder:14b",
    "rag": "llama3.1:8b",
    "planner": "llama3.1:8b",
    "chat": "llama3.1:8b",
}


class LLM:
    """Wrapper für Ollama Chat-API."""

    def __init__(self, base_url: str = OLLAMA_URL):
        self.base_url = base_url

    def ask(self, model: str, prompt: str, system: str = "") -> str:
        """Sendet einen Prompt an Ollama und gibt die Antwort zurück."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            res = requests.post(
                self.base_url,
                json={"model": model, "messages": messages, "stream": False},
                timeout=120,
            )
            res.raise_for_status()
            return res.json()["message"]["content"]
        except requests.ConnectionError:
            console.print("[red]❌ Ollama nicht erreichbar — läuft der Server?[/red]")
            return "ERROR: Ollama not reachable"
        except Exception as e:
            console.print(f"[red]❌ LLM Fehler: {e}[/red]")
            return f"ERROR: {e}"

    def get_model(self, mode: str) -> str:
        """Gibt das passende Modell für einen Modus zurück."""
        return MODELS.get(mode, MODELS["chat"])
