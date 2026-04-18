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

# ============================================================================
# 🎯 DYNAMISCH MODEL LOADING (Hot Reload Support)
# ============================================================================
# Nutzt DynamicConfigLoader für:
# - Automatische Config-Erkennung
# - Wechsel zwischen Configs ohne Restart
# - Persistente Speicherung in .continue/agents/ACTIVE_CONFIG
# ============================================================================

# Initialize DynamicConfigLoader
config_dir = Path(__file__).parent.parent / ".continue" / "agents"
CONFIG_LOADER = DynamicConfigLoader(config_dir)

# Initialisiere Models beim Modul-Import (wird aber bei jedem Zugriff neu geladen)
_INITIAL_MODELS = CONFIG_LOADER.load_config()


def get_models() -> dict:
    """Hole aktualisierte Models von der aktiven Config.
    
    Diese Funktion lädt die Config bei jedem Aufruf neu,
    um sicherzustellen, dass Wechsel erkannt werden.
    """
    return CONFIG_LOADER.load_config() or _INITIAL_MODELS or {
        "agent": "llama3-groq-tool-use:8b",
        "coder": "qwen3-coder:30b",
        "planner": "qwen3-coder:30b",
        "rag": "qwen3-coder:30b",
        "chat": "llama3-groq-tool-use:8b",
    }


# Für Backward Compatibility
MODELS = _INITIAL_MODELS


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
        """Gibt das passende Modell für einen Modus zurück (aktualisiert dynamisch)."""
        models = get_models()  # Hole aktuelle Models mit Hot Reload
        return models.get(mode, models.get("chat", "llama3-groq-tool-use:8b"))
