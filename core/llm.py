"""Ollama LLM Connector — lokale Inference via Ollama REST API."""

import requests
import yaml
from pathlib import Path
from rich.console import Console

console = Console()

OLLAMA_URL = "http://localhost:11434/api/chat"

# ============================================================================
# 🎯 DYNAMISCH MODEL LOADING (aus config.yaml)
# ============================================================================
# Liest automatisch die Models aus Continue config.yaml
# Kein Hardcoding mehr - immer synchronisiert!
# ============================================================================


def load_models_from_config() -> dict:
    """Lädt Models dynmaisch aus .continue/agents/config.yaml.
    
    Returns:
        dict: MODELS mapping {mode: model_name}
    
    Fallback: Wenn config.yaml nicht gefunden, nutzt Defaults
    """
    # 1. Versuche relative Path (Project-lokal)
    config_path = Path(__file__).parent.parent / ".continue" / "agents" / "config.yaml"
    
    if config_path.exists():
        console.print(f"[green]✅[/green] Config found (relative): {config_path}")
    else:
        # 2. Versuche Home directory
        config_path = Path.home() / ".continue" / "agents" / "config.yaml"
        if config_path.exists():
            console.print(f"[green]✅[/green] Config found (home): {config_path}")
        else:
            # 3. Versuche absolute Pfade (Linux)
            alt_paths = [
                Path("/mnt/6724D393605CE580/Linux/LLM_Projekte/Github/mcp-real-agent/.continue/agents/config.yaml"),
                Path("/mnt/6724D393605CE580/Linux/LJMProjekte/Github/mcp-real-agent/.continue/agents/config.yaml"),
            ]
            
            found = False
            for alt_path in alt_paths:
                if alt_path.exists():
                    config_path = alt_path
                    console.print(f"[green]✅[/green] Config found (absolute): {config_path}")
                    found = True
                    break
            
            if not found:
                console.print("[yellow]⚠️  config.yaml nicht gefunden[/yellow]")
                console.print("[yellow]Nutze Fallback-Models...[/yellow]")
                return _get_default_models()
    
    # Wenn IMMER NOCH nicht gefunden, nutze Defaults
    if not config_path.exists():
        console.print(f"[yellow]⚠️  config.yaml nicht gefunden ({config_path})[/yellow]")
        console.print("[yellow]Nutze Fallback-Models...[/yellow]")
        return _get_default_models()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Extrahiere Models aus YAML
        models_list = config.get('models', [])
        models_dict = {}
        
        for model_entry in models_list:
            if isinstance(model_entry, dict) and 'name' in model_entry and 'model' in model_entry:
                name = model_entry['name']
                model_name = model_entry['model']
                models_dict[name] = model_name
                console.print(f"[green]✅[/green] Model geladen: {name} → {model_name}")
        
        if not models_dict:
            console.print("[yellow]⚠️  Keine Models in config.yaml gefunden[/yellow]")
            return _get_default_models()
        
        return models_dict
    
    except Exception as e:
        console.print(f"[red]❌ Fehler beim Lesen von config.yaml: {e}[/red]")
        return _get_default_models()


def _get_default_models() -> dict:
    """Fallback Models wenn keine config.yaml vorhanden."""
    return {
        "agent": "devstral-rtx3090:latest",           # PRIMARY
        "coder": "qwen2.5-coder:14b",                 # FALLBACK
        "planner": "devstral-small-2:24b",            # PLANNING
        "rag": "devstral-small-2:24b",                # RAG/REASONING
        "chat": "devstral-rtx3090:latest",            # CHAT
    }


# Load Models beim Start
MODELS = load_models_from_config()


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
