"""Tool Registry — Plugin-System für erweiterbare Tools."""

from typing import Callable
from rich.console import Console

console = Console()


class ToolRegistry:
    """Registriert und verwaltet Tools als Plugins."""

    def __init__(self):
        self.tools: dict[str, Callable] = {}

    def register(self, name: str, func: Callable, description: str = "") -> None:
        """Registriert ein neues Tool."""
        self.tools[name] = {"func": func, "description": description}
        console.print(f"[dim]🔧 Tool registriert: {name}[/dim]")

    def run(self, name: str, input_data: str) -> str:
        """Führt ein registriertes Tool aus."""
        if name not in self.tools:
            return f"❌ Tool nicht gefunden: '{name}'"
        try:
            return self.tools[name]["func"](input_data)
        except Exception as e:
            return f"❌ Tool Fehler ({name}): {e}"

    def list_tools(self) -> list[str]:
        """Gibt alle registrierten Tool-Namen zurück."""
        return list(self.tools.keys())
