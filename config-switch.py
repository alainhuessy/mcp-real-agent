#!/usr/bin/env python3
"""CLI Tool zum dynamischen Wechsel zwischen Config-Dateien."""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config_loader import DynamicConfigLoader
from rich.console import Console
from rich.table import Table

console = Console()


def main():
    """Hauptfunktion für Config-Verwaltung."""
    config_loader = DynamicConfigLoader()

    # Argumente analysieren
    if len(sys.argv) < 2:
        show_help_and_list(config_loader)
        return

    command = sys.argv[1]

    if command == "list":
        show_available(config_loader)
    elif command == "switch" or command == "use":
        if len(sys.argv) < 3:
            console.print("[red]❌ Config-Name erforderlich[/red]")
            console.print("\n[bold]Verwendung:[/bold] config-switch.py switch config-name.yaml")
            return
        config_name = sys.argv[2]
        switch_config(config_loader, config_name)
    elif command == "active":
        show_active(config_loader)
    elif command == "models":
        show_models(config_loader)
    elif command == "help":
        show_help(config_loader)
    else:
        console.print(f"[red]❌ Unbekannter Befehl: {command}[/red]")
        show_help(config_loader)


def show_help_and_list(config_loader: DynamicConfigLoader):
    """Zeige Hilfe und verfügbare Configs."""
    console.print(
        "[bold cyan]⚙️  Config Switcher[/bold cyan] — Dynamischer Wechsel zwischen Configs"
    )
    console.print()
    show_available(config_loader)
    console.print()
    show_help(config_loader)


def show_help(config_loader: DynamicConfigLoader):
    """Zeige Hilfe-Text."""
    console.print("[bold]📖 Befehle:[/bold]")
    console.print(
        "  [cyan]list    [/cyan] - Zeige alle verfügbaren Configs"
    )
    console.print(
        "  [cyan]switch  [/cyan] - Wechsle zu einer Config (Bsp: switch config-top-tier.yaml)"
    )
    console.print(
        "  [cyan]active  [/cyan] - Zeige die aktuelle Config"
    )
    console.print(
        "  [cyan]models  [/cyan] - Zeige alle Models der aktiven Config"
    )
    console.print(
        "  [cyan]help    [/cyan] - Diese Hilfe"
    )
    console.print()
    console.print("[bold]🔧 Verwendung über Environment Variable:[/bold]")
    console.print(
        "  export ACTIVE_CONFIG=config-top-tier.yaml"
    )
    console.print("  python mcp_server.py")


def show_available(config_loader: DynamicConfigLoader):
    """Zeige alle verfügbaren Configs."""
    console.print("[bold]📋 Verfügbare Configs:[/bold]")
    
    configs = config_loader.get_available_configs()
    active = config_loader.get_active_config_name()
    
    if not configs:
        console.print("[yellow]⚠️  Keine Config-Dateien gefunden[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Status")
    table.add_column("Config-Name")
    table.add_column("Größe (KB)")

    for config_name in configs:
        config_path = config_loader.config_dir / config_name
        size_kb = config_path.stat().st_size / 1024
        
        is_active = "✅ AKTIV" if config_name == active else ""
        table.add_row(is_active, config_name, f"{size_kb:.1f}")

    console.print(table)


def show_active(config_loader: DynamicConfigLoader):
    """Zeige die aktuelle Config."""
    active = config_loader.get_active_config_name()
    console.print(f"[bold]📌 Aktive Config:[/bold] {active}")


def show_models(config_loader: DynamicConfigLoader):
    """Zeige alle Models der aktiven Config."""
    models = config_loader.load_config()
    
    if not models:
        console.print("[yellow]⚠️  Keine Models gefunden[/yellow]")
        return

    console.print("[bold]🤖 Models (aktive Config):[/bold]")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Mode")
    table.add_column("Model")

    for mode, model_name in models.items():
        table.add_row(mode, model_name)

    console.print(table)


def switch_config(config_loader: DynamicConfigLoader, config_name: str):
    """Wechsle zu einer anderen Config."""
    success = config_loader.switch_config(config_name)
    
    if success:
        console.print()
        console.print(
            "[bold cyan]💡 Tipp:[/bold cyan] Starten Sie den MCP-Server neu für die Änderungen:"
        )
        console.print("  [yellow]python mcp_server.py[/yellow]")
        console.print()
        show_models(config_loader)


if __name__ == "__main__":
    main()
