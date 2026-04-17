"""Agent OS Core — Hauptorchestrator mit Multi-Agent Pipeline."""

from rich.console import Console
from rich.panel import Panel

from core.llm import LLM
from core.router import Router
from memory.memory import Memory
from tasks.task_queue import TaskQueue
from tools.registry import ToolRegistry
from tools.shell import shell
from tools.file import read_file, write_file, list_dir
from tools.git import git_status, git_commit, git_log
from agents.planner import PlannerAgent
from agents.worker import WorkerAgent
from agents.reviewer import ReviewerAgent

console = Console()


class AgentOS:
    """Agent Operating System v2.1 — Kernel."""

    def __init__(self):
        # Core
        self.llm = LLM()
        self.router = Router()
        self.memory = Memory()
        self.tasks = TaskQueue()

        # Tool Registry (Plugin System)
        self.tools = ToolRegistry()
        self._register_default_tools()

        # Multi-Agent System
        self.planner = PlannerAgent(self.llm)
        self.worker = WorkerAgent(self.llm, self.router, self.tools)
        self.reviewer = ReviewerAgent(self.llm)

    def _register_default_tools(self):
        """Registriert die Standard-Tools."""
        self.tools.register("shell", shell, "Execute shell commands (allowlisted)")
        self.tools.register("read_file", read_file, "Read a file")
        self.tools.register("write_file", lambda p: write_file(p), "Write a file")
        self.tools.register("list_dir", list_dir, "List directory contents")
        self.tools.register("git_status", lambda _: git_status(), "Git status")
        self.tools.register("git_commit", git_commit, "Git commit")
        self.tools.register("git_log", lambda _: git_log(), "Git log")

    def run_task(self, task: str) -> str:
        """Führt einen einzelnen Task durch die Pipeline: Route → Execute → Review → Memory."""
        # 1. Memory-Kontext holen
        mem_ctx = self.memory.search(task)

        # 2. Route bestimmen
        mode = self.router.route(task)
        console.print(f"[dim]🧭 Route: {mode}[/dim]")

        # 3. Bei Planner-Tasks: Subtasks erzeugen
        if mode == "planner":
            subtasks = self.planner.plan(task, mem_ctx)
            console.print(f"[cyan]📋 Plan: {len(subtasks)} Subtasks erstellt[/cyan]")
            for st in subtasks:
                self.tasks.add(st)
            return f"📋 {len(subtasks)} Subtasks erstellt und in Queue eingereiht."

        # 4. Worker ausführen
        result = self.worker.execute(task, mem_ctx)

        # 5. Reviewer prüfen
        review = self.reviewer.review(task, result)
        status_icon = "✅" if review["approved"] else "⚠️"
        console.print(f"[dim]{status_icon} Review: {review['status']}[/dim]")

        # 6. Memory aktualisieren
        self.memory.sync(f"Task: {task}\nResult: {result[:200]}", task[:30])

        return result

    def run_loop(self):
        """Autonomer Task Loop — arbeitet Queue ab."""
        console.print(Panel("🧠 Agent OS v2.1 — Autonomer Loop gestartet", style="bold green"))

        import time
        while True:
            task = self.tasks.get_next()
            if not task:
                time.sleep(2)
                continue

            console.print(f"\n[yellow]⚙️ Task:[/yellow] {task['task']}")
            task["status"] = "running"

            try:
                result = self.run_task(task["task"])
                self.tasks.complete(task)
                console.print(f"[green]✅ Done[/green]")
            except Exception as e:
                self.tasks.fail(task, str(e))
                console.print(f"[red]❌ Failed: {e}[/red]")

            time.sleep(1)
