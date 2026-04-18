"""Ollama LLM Connector — lokale Inference via Ollama REST API."""

import requests
from pathlib import Path
from rich.console import Console

from core.config_loader import DynamicConfigLoader

console = Console()

OLLAMA_URL = "http://localhost:11434/api/chat"

# ============================================================================
# 🎯 DYNAMISCH MODEL LOADING (Hot Reload Support)
# ============================================================================
# Nutzt DynamicConfigLoader für:
# - Automatische Config-Erkennung
# - Wechsel zwischen Configs ohne Restart
# - Environment Variable: ACTIVE_CONFIG
# ============================================================================

# Initialize DynamicConfigLoader
config_dir = Path(__file__).parent.parent / ".continue" / "agents"
CONFIG_LOADER = DynamicConfigLoader(config_dir)

# Load Models beim Start
MODELS = CONFIG_LOADER.load_config()

if not MODELS:
    console.print("[yellow]⚠️  Nutze Fallback-Models[/yellow]")
    MODELS = {
        "agent": "llama3-groq-tool-use:8b",
        "coder": "qwen3-coder:30b",
        "planner": "qwen3-coder:30b",
        "rag": "qwen3-coder:30b",
        "chat": "llama3-groq-tool-use:8b",
    }


class LLM:
    """Wrapper für Ollama Chat-API."""

    def __init__(self, base_url: str = OLLAMA_URL):
        """Initialize LLM client with Ollama server URL.
        
        Args:
            base_url: Ollama server endpoint (default: http://localhost:11434)
        """
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
