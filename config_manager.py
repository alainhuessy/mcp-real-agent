#!/usr/bin/env python3
"""
🎯 Continue Config Manager — Zentrale Verwaltung aller Konfigurationen
=========================================================================

Dieses Tool verwaltet die verschiedenen config.yaml Dateien
und ermöglicht einfaches Wechseln zwischen Profilen.

PROFILE:
  - rtx3090-optimized    (RTX 3090 optimal, 5 Models, Zero CPU-Offload)
  - complete             (Alle Modelle, 7 Models, maximal)
  - balanced             (Top-Tier, 2 Models, schnell)

USAGE:
  python config_manager.py --list              # Zeige alle Profile
  python config_manager.py --active            # Zeige aktives Profil
  python config_manager.py --switch rtx3090    # Wechsel zu Profil
  python config_manager.py --sync              # Sync MCP + Continue
"""

import argparse
import shutil
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# ============================================================================
# CONFIG MANAGER SETTINGS
# ============================================================================

CONFIG_DIR = Path(".continue/agents")
CONFIG_PROFILES = {
    "tool-use-optimized": {
        "file": "config-tool-use-optimized.yaml",
        "description": "🎯 BEST FOR MCP - llama3-groq-tool-use (Tool-Use Specialist)",
        "models": 5,
        "best_for": "Agent OS MCP + Continue IDE (RECOMMENDED)",
        "default": True
    },
    "rtx3090-optimized": {
        "file": "config-rtx3090-optimized.yaml",
        "description": "🎯 RTX 3090 Optimized - Zero CPU-Offload",
        "models": 5,
        "best_for": "Daily development with RTX 3090",
    },
    "complete": {
        "file": "config-complete.yaml",
        "description": "📊 Complete - All Available Models",
        "models": 7,
        "best_for": "Testing all models and configurations",
    },
    "balanced": {
        "file": "config-top-tier.yaml",
        "description": "⚖️  Balanced - Top-Tier Setup",
        "models": 2,
        "best_for": "Fast, stable development",
    }
}


class ConfigManager:
    """Zentrale Verwaltung von Continue Konfigurationen."""
    
    def __init__(self, config_dir: Path = CONFIG_DIR):
        self.config_dir = Path(config_dir)
        self.active_config = self.config_dir / "config.yaml"
        self.mcp_llm_file = Path("core/llm.py")
    
    def list_profiles(self):
        """Zeige alle verfügbaren Profile."""
        table = Table(title="📋 Available Configuration Profiles")
        table.add_column("Profile", style="cyan")
        table.add_column("File", style="green")
        table.add_column("Models", style="yellow")
        table.add_column("Description", style="white")
        
        for name, profile in CONFIG_PROFILES.items():
            is_active = " ✅" if name == self.get_active_profile() else ""
            table.add_row(
                name + is_active,
                profile["file"],
                str(profile["models"]),
                profile["description"]
            )
        
        console.print(table)
    
    def get_active_profile(self) -> str:
        """Bestimme das aktuell aktive Profil."""
        if not self.active_config.exists():
            return "NONE"
        
        try:
            # Vergleiche Content
            active_content = self.active_config.read_text()
            
            for profile_name, profile_info in CONFIG_PROFILES.items():
                profile_file = self.config_dir / profile_info["file"]
                if profile_file.exists():
                    if profile_file.read_text() == active_content:
                        return profile_name
            
            return "CUSTOM"  # Wenn nicht übereinstimmend
        except:
            return "UNKNOWN"
    
    def show_active(self):
        """Zeige das aktuell aktive Profil."""
        active = self.get_active_profile()
        
        if active in CONFIG_PROFILES:
            profile = CONFIG_PROFILES[active]
            panel = Panel(
                f"[green]✅ {profile['description']}[/green]\n"
                f"[cyan]File:[/cyan] {profile['file']}\n"
                f"[yellow]Models:[/yellow] {profile['models']}\n"
                f"[white]Best for:[/white] {profile.get('best_for', 'N/A')}",
                title="[bold]Active Configuration Profile[/bold]"
            )
            console.print(panel)
        else:
            console.print(f"[yellow]⚠️  Active profile: {active}[/yellow]")
    
    def switch_profile(self, profile_name: str) -> bool:
        """Wechsel zu einem anderen Profil."""
        if profile_name not in CONFIG_PROFILES:
            console.print(f"[red]❌ Profil '{profile_name}' nicht gefunden![/red]")
            self.list_profiles()
            return False
        
        source_file = self.config_dir / CONFIG_PROFILES[profile_name]["file"]
        
        if not source_file.exists():
            console.print(f"[red]❌ Datei '{source_file}' existiert nicht![/red]")
            return False
        
        try:
            # Backup des alten  config
            if self.active_config.exists():
                backup_file = self.config_dir / f"config-backup-{datetime.now().timestamp()}.yaml"
                shutil.copy(self.active_config, backup_file)
                console.print(f"[yellow]📦 Backup erstellt: {backup_file.name}[/yellow]")
            
            # Kopiere neue Config
            shutil.copy(source_file, self.active_config)
            console.print(f"[green]✅ Profil '{profile_name}' aktiv![/green]")
            
            # Zeige Änderungen
            self._show_models_from_config(self.active_config)
            
            return True
        except Exception as e:
            console.print(f"[red]❌ Fehler beim Wechsel: {e}[/red]")
            return False
    
    def sync_mcp_agent(self) -> bool:
        """Synchronisiere MCP Agent mit aktiver Config."""
        if not self.active_config.exists():
            console.print(f"[red]❌ config.yaml nicht gefunden![/red]")
            return False
        
        try:
            # Lese Models aus config.yaml
            with open(self.active_config, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            models = {}
            for model_entry in config.get('models', []):
                if isinstance(model_entry, dict) and 'name' in model_entry:
                    name = model_entry['name']
                    model = model_entry['model']
                    models[name] = model
            
            # Infomation display
            console.print("[green]✅ MCP Agent Synchronisierung[/green]")
            table = Table(title="Loaded Models (MCP Agent)")
            table.add_column("Mode", style="cyan")
            table.add_column("Model", style="green")
            
            for mode, model_name in models.items():
                table.add_row(mode, model_name)
            
            console.print(table)
            console.print("[yellow]💡 MCP Agent lädt diese Models automatisch![/yellow]")
            
            return True
        except Exception as e:
            console.print(f"[red]❌ Sync-Fehler: {e}[/red]")
            return False
    
    def _show_models_from_config(self, config_file: Path):
        """Zeige Models von einer Config-Datei."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            table = Table(title="📊 Models in this Profile")
            table.add_column("Name", style="cyan")
            table.add_column("Model", style="green")
            
            for model_entry in config.get('models', []):
                if isinstance(model_entry, dict):
                    table.add_row(model_entry.get('name', 'N/A'), model_entry.get('model', 'N/A'))
            
            console.print(table)
        except:
            pass


def main():
    parser = argparse.ArgumentParser(
        description="🎯 Continue Configuration Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python config_manager.py --list               # Liste alle Profile
  python config_manager.py --active             # Zeige aktives Profil
  python config_manager.py --switch rtx3090     # Wechsel zu RTX 3090 Profil
  python config_manager.py --sync               # Sync MCP + Continue
        """
    )
    
    parser.add_argument('--list', action='store_true', help='Liste alle Profile')
    parser.add_argument('--active', action='store_true', help='Zeige aktives Profil')
    parser.add_argument('--switch', type=str, help='Wechsel zu Profil')
    parser.add_argument('--sync', action='store_true', help='Synchronisiere MCP Agent')
    
    args = parser.parse_args()
    
    manager = ConfigManager()
    
    if args.list:
        manager.list_profiles()
    elif args.active:
        manager.show_active()
    elif args.switch:
        manager.switch_profile(args.switch)
    elif args.sync:
        manager.sync_mcp_agent()
    else:
        # Default: show active
        manager.show_active()


if __name__ == "__main__":
    main()
