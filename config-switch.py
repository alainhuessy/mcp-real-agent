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
    elif command == "enable":
        if len(sys.argv) < 3:
            console.print("[red]❌ Config-Name erforderlich[/red]")
            console.print("\n[bold]Verwendung:[/bold] config-switch.py enable config-name.yaml")
            return
        config_name = sys.argv[2]
        enable_config(config_loader, config_name)
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
        "  [cyan]enable  [/cyan] - Aktiviere eine Config (Bsp: enable config-rtx3090-optimized.yaml)"
    )
    console.print(
        "  [cyan]switch  [/cyan] - Alte Methode (veraltet, nutze 'enable')"
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
    console.print("[bold]🔧 Manuelle Editor-Methode:[/bold]")
    console.print("  Öffne: [yellow].continue/agents/ACTIVE_CONFIG[/yellow]")
    console.print("  - Kommentiere # vor der Config ein = INAKTIV")
    console.print("  - Entferne # = AKTIV")
    console.print("  - Speichere → Hot Reload funktioniert automatisch!")
    console.print()
    console.print("[bold]🔗 Umgebungsvariable (nur für Session):[/bold]")
    console.print(
        "  export ACTIVE_CONFIG=config-top-tier.yaml"
    )
    console.print("  python run.py")


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
        console.print("[bold green]✅ Config dauerhaft gespeichert![/bold green]")
        console.print()
        console.print("[bold cyan]💡 Hot Reload aktiviert:[/bold cyan]")
        console.print("  • Config-Wechsel wird beim nächsten Tool-Zugriff erkannt")
        console.print("  • Kein Server-Restart erforderlich für normale Nutzung")
        console.print("  • Optional: Das API-System neu starten für sofort Update:")
        console.print("    [yellow]python run.py[/yellow]")
        console.print()
        show_models(config_loader)


def enable_config(config_loader: DynamicConfigLoader, config_name: str):
    """Aktiviere eine Config durch Kommentar-Bearbeitung in ACTIVE_CONFIG."""
    config_path = config_loader.config_dir / config_name
    
    if not config_path.exists():
        console.print(f"[red]❌ Config nicht gefunden: {config_name}[/red]")
        return
    
    # Lese ACTIVE_CONFIG
    active_config_file = config_loader.config_dir / "ACTIVE_CONFIG"
    try:
        content = active_config_file.read_text()
        lines = content.split("\n")
        
        # Bearbeite jede Zeile
        new_lines = []
        for line in lines:
            stripped = line.strip()
            
            # Leere Zeilen bewahren
            if not stripped:
                new_lines.append(line)
                continue
            
            # Header-Kommentare bewahren
            if stripped.startswith("#") and ".yaml" not in stripped:
                new_lines.append(line)
                continue
            
            # Extract real config name (remove # if present)
            config_to_check = stripped.lstrip("#").strip()
            
            # Wenn das die gesuchte Config ist → dekommentieren
            if config_to_check == config_name:
                new_lines.append(config_name)
            # Sonst kommentieren (wenn noch nicht kommentiert)
            else:
                if stripped.startswith("#"):
                    new_lines.append(line)  # Bleibt kommentiert
                else:
                    new_lines.append(f"# {stripped}")  # Kommentiere
        
        # Schreibe zurück
        active_config_file.write_text("\n".join(new_lines))
        
        console.print(f"[green]✅ Config aktiviert:[/green] {config_name}")
        console.print()
        console.print("[bold cyan]💡 Hot Reload aktiviert:[/bold cyan]")
        console.print("  • Wechsel wird beim nächsten Tool-Zugriff erkannt")
        console.print("  • Kein Restart nötig!")
        console.print()
        
        # Lade Models neu
        config_loader.last_modified = None
        show_models(config_loader)
        
    except Exception as e:
        console.print(f"[red]❌ Fehler beim Bearbeiten von ACTIVE_CONFIG: {e}[/red]")


if __name__ == "__main__":
    main()
