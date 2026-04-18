"""DynamicConfigLoader — Dynamisches Wechseln zwischen Config-Dateien ohne Restart."""

import os
from pathlib import Path
from typing import Dict, Optional

import yaml
from rich.console import Console

console = Console()


class DynamicConfigLoader:
    """Verwaltet dynamisches Laden und Wechseln von Config-Dateien.
    
    Features:
    - Überwacht alle .yaml Dateien im .continue/agents/ Verzeichnis
    - Wechselt dinamisch zwischen Configs (kein Restart nötig)
    - Hot Reload wenn sich die aktive Config ändert
    - Environment Variable für Konfiguration: ACTIVE_CONFIG (z.B. config-top-tier.yaml)
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize DynamicConfigLoader.
        
        Args:
            config_dir: Pfad zu .continue/agents/. Wenn None, wird Standard genutzt.
        """
        if config_dir is None:
            # Standard: Projekt-lokal
            config_dir = (
                Path(__file__).parent.parent / ".continue" / "agents"
            )

        self.config_dir = config_dir
        self.current_config_file: Optional[Path] = None
        self.current_models: Dict[str, str] = {}
        self.last_modified = None

    def get_available_configs(self) -> list[str]:
        """Liste alle verfügbaren Config-Dateien auf."""
        if not self.config_dir.exists():
            console.print(
                f"[yellow]⚠️  Config-Verzeichnis nicht gefunden: {self.config_dir}[/yellow]"
            )
            return []

        configs = sorted(
            f.name for f in self.config_dir.glob("config*.yaml")
            if f.is_file()
        )
        return configs

    def get_active_config_name(self) -> str:
        """Bestimme welche Config aktiv sein soll.
        
        Priority:
        1. Environment Variable ACTIVE_CONFIG
        2. Symlink "active-config.yaml" (wenn vorhanden)
        3. Default: "config.yaml"
        """
        # 1. Environment Variable
        if env_config := os.environ.get("ACTIVE_CONFIG"):
            return env_config

        # 2. Symlink
        symlink_path = self.config_dir / "active-config.yaml"
        if symlink_path.is_symlink():
            return symlink_path.resolve().name

        # 3. Default
        return "config.yaml"

    def load_config(self) -> Dict[str, str]:
        """Lade die aktive Config neu (Hot Reload).
        
        Returns:
            dict: {mode: model_name} mapping
        """
        active_name = self.get_active_config_name()
        config_path = self.config_dir / active_name

        if not config_path.exists():
            console.print(
                f"[red]❌ Config nicht gefunden: {config_path}[/red]"
            )
            return {}

        # Prüfe auf Änderungen (Hot Reload)
        try:
            stat = config_path.stat()
            if (
                self.current_config_file == config_path
                and self.last_modified == stat.st_mtime
            ):
                # Config hat sich nicht geändert
                return self.current_models

            # Config hat sich geändert oder ist neue Datei
            console.print(
                f"[blue]🔄 Lade Config:[/blue] {active_name}"
            )
            self.last_modified = stat.st_mtime

        except OSError as e:
            console.print(f"[red]❌ Fehler beim Lesen von {config_path}: {e}[/red]")
            return {}

        # Parse YAML
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Extrahiere Models
            models_dict = {}
            for model_entry in config.get("models", []):
                if isinstance(model_entry, dict) and "name" in model_entry:
                    name = model_entry["name"]
                    model_name = model_entry.get("model", "")
                    models_dict[name] = model_name
                    console.print(
                        f"[green]✅ Model:[/green] {name} → {model_name}"
                    )

            self.current_config_file = config_path
            self.current_models = models_dict

            return models_dict

        except (yaml.YAMLError, KeyError) as e:
            console.print(f"[red]❌ Fehler beim Parsen von {config_path}: {e}[/red]")
            return {}

    def switch_config(self, config_name: str) -> bool:
        """Wechsle zu einer anderen Config.
        
        Args:
            config_name: Name der Config (z.B. "config-top-tier.yaml")
            
        Returns:
            bool: True wenn erfolgreich, False sonst
        """
        config_path = self.config_dir / config_name

        if not config_path.exists():
            console.print(
                f"[red]❌ Config nicht gefunden: {config_name}[/red]"
            )
            return False

        # Setze Environment Variable
        os.environ["ACTIVE_CONFIG"] = config_name
        console.print(
            f"[green]✅ ACTIVE_CONFIG gesetzt auf:[/green] {config_name}"
        )

        # Lade neue Config
        self.last_modified = None  # Force reload
        self.load_config()
        return True

    def get_model(self, mode: str) -> str:
        """Gib das Modell für einen Mode zurück.
        
        Args:
            mode: Mode (z.B. "agent", "coder", "qwen3.6-premium")
            
        Returns:
            str: Model name, oder leerer String wenn nicht gefunden
        """
        # Hot Reload prüfen
        self.load_config()
        return self.current_models.get(mode, "")

    def show_available(self):
        """Zeige alle verfügbaren Configs mit Details."""
        console.print("\n[bold]📋 Verfügbare Configs:[/bold]")
        
        configs = self.get_available_configs()
        active = self.get_active_config_name()

        for config_name in configs:
            is_active = "⭐" if config_name == active else "  "
            console.print(f"{is_active} {config_name}")

        console.print(f"\n[bold]Aktive Config:[/bold] {active}")
        console.print(
            "\n[bold]Zum Wechseln:[/bold] export ACTIVE_CONFIG=config-name.yaml"
        )
