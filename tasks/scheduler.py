"""Scheduler — Background Daemon für autonome Task-Ausführung."""

import time
from typing import Generator
from tasks.task_queue import TaskQueue
from rich.console import Console

console = Console()


class Scheduler:
    """OS-Level Loop — arbeitet Tasks automatisch ab."""

    def __init__(self, task_queue: TaskQueue, interval: float = 2.0):
        """Initialize Task Scheduler.
        
        Args:
            task_queue: TaskQueue instance for managing tasks
            interval: Polling interval in seconds (default: 2.0)
        """
        self.queue = task_queue
        self.interval = interval
        self.running = False

    def run(self) -> Generator[dict, None, None]:
        """Generator-basierter Task Loop."""
        self.running = True
        console.print("[bold green]🧠 Scheduler gestartet[/bold green]")

        while self.running:
            task = self.queue.get_next()
            if not task:
                time.sleep(self.interval)
                continue

            console.print(f"[yellow]⚙️ Executing:[/yellow] {task['task']}")
            task["status"] = "running"
            yield task
            time.sleep(0.5)

    def stop(self):
        """Stop the task scheduler."""
        self.running = False
        console.print("[red]⏹ Scheduler gestoppt[/red]")
