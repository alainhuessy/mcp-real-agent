"""Agent OS v2.1 — Main Entry Point (CLI)."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.agent import AgentOS

console = Console()


def main():
    agent = AgentOS()

    console.print(Panel.fit(
        "[bold green]🧠 Agent OS v2.1[/bold green]\n"
        "[dim]Local AI Operating System — Ollama + ChromaDB + FastAPI[/dim]\n\n"
        "Befehle:\n"
        "  [cyan]<task>[/cyan]        — Task ausführen (Standard)\n"
        "  [cyan]tracked:<task>[/cyan] — Task mit Live-Tracking ausführen ⭐\n"
        "  [cyan]debug:<task>[/cyan]   — Task mit Debug-Details ausführen 🔍\n"
        "  [cyan]results[/cyan]        — Zeige letzte Task-Ergebnisse\n"
        "  [cyan]shell:<cmd>[/cyan]   — Shell-Befehl ausführen\n"
        "  [cyan]plan:<goal>[/cyan]   — Ziel in Subtasks zerlegen\n"
        "  [cyan]status[/cyan]        — System-Status anzeigen\n"
        "  [cyan]tasks[/cyan]         — Task Queue anzeigen\n"
        "  [cyan]loop[/cyan]          — Autonomen Task Loop starten\n"
        "  [cyan]api[/cyan]           — API Server starten\n"
        "  [cyan]quit[/cyan]          — Beenden",
        title="Agent OS", border_style="green"
    ))

    while True:
        try:
            task = console.input("\n[bold cyan]Task >[/bold cyan] ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not task:
            continue

        if task == "quit":
            console.print("[dim]👋 Bye[/dim]")
            break

        if task == "status":
            console.print(f"📊 Pending Tasks: {agent.tasks.get_pending_count()}")
            console.print(f"🔧 Tools: {', '.join(agent.tools.list_tools())}")
            continue

        if task == "tasks":
            table = Table(title="Task Queue")
            table.add_column("ID", style="dim")
            table.add_column("Task")
            table.add_column("Status")
            for t in agent.tasks.get_all():
                color = {"pending": "yellow", "running": "blue", "done": "green", "failed": "red"}.get(t["status"], "white")
                table.add_row(t["id"], t["task"][:60], f"[{color}]{t['status']}[/{color}]")
            console.print(table)
            continue

        if task == "results":
            from tasks.result_inspector import show_results
            show_results(limit=10)
            continue

        if task == "loop":
            agent.run_loop()
            continue

        if task == "api":
            console.print("[cyan]🚀 API Server startet auf http://localhost:8000[/cyan]")
            import uvicorn
            uvicorn.run("api.kernel:app", host="0.0.0.0", port=8000, reload=True)
            continue

        if task.startswith("shell:"):
            cmd = task.replace("shell:", "").strip()
            result = agent.tools.run("shell", cmd)
            console.print(result)
            continue

        if task.startswith("debug:"):
            from tools.debug_mode import get_debug_mode
            task_name = task.replace("debug:", "").strip()
            debug_mode = get_debug_mode()
            result = debug_mode.execute_debug(task_name)
            console.print(f"\n[bold green]Result:[/bold green]\n{result}")
            continue

        if task.startswith("plan:"):
            goal = task.replace("plan:", "").strip()
            subtasks = agent.planner.plan(goal)
            for i, st in enumerate(subtasks, 1):
                agent.tasks.add(st)
                console.print(f"  [cyan]{i}.[/cyan] {st}")
            continue

        if task.startswith("tracked:"):
            task_name = task.replace("tracked:", "").strip()
            console.print(f"\n[bold cyan]🎯 Starte Tracked Execution: {task_name}[/bold cyan]\n")
            result = agent.worker.tracked_execute(task_name, show_progress=True)
            console.print(f"\n[bold green]✅ Task Complete[/bold green]\n")
            console.print(f"[dim]Result:[/dim]\n{result[:500]}..." if len(result) > 500 else f"[dim]Result:[/dim]\n{result}")
            continue

        # Standard: Task ausführen
        result = agent.run_task(task)
        console.print(Panel(result, title="Result", border_style="blue"))


if __name__ == "__main__":
    main()
