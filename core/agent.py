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
    """Agent Operating System v2.1 — Multi-Agent Kernel.
    
    Das AgentOS ist der zentrale Orchestrator für eine intelligente Multi-Agent Pipeline:
    
    Pipeline-Flow:
        1. Router: Bestimmt den Ausführungsmodus (planner/worker/reviewer)
        2. Planner: Zerlegt komplexe Tasks in Subtasks
        3. Worker: Führt Tasks aus mit Zugriff auf Tools und LLM
        4. Reviewer: Überprüft Qualität der Ergebnisse
        5. Memory: Speichert Erkenntnisse für zukünftige Tasks
    
    Komponenten:
        - LLM: Lokale Language Model über Ollama
        - Router: Intelligentes Task-Routing
        - Memory: ChromaDB Vector Memory für semantische Suche
        - TaskQueue: Verwaltete Warteschlange für autonome Ausführung
        - ToolRegistry: Plugin-System für Shell, File, Git, etc.
        - Multi-Agent System: Planner → Worker → Reviewer Pipeline
    """

    def __init__(self):
        """Initialisiert die Agent OS Komponenten und ihr Zusammenspiel.
        
        Führt folgende Intialisierungsschritte durch:
        1. LLM Module: Language Model über Ollama laden
        2. Core Komponenten: Router, Memory, TaskQueue
        3. Tool Registry: Plugin-System aufbauen (Shell, File, Git)
        4. Multi-Agent System: Planner, Worker, Reviewer initialisieren
        
        Die Komponenten werden anschließend über 'run_task()' oder 'run_loop()' 
        orchestriert.
        """
        # Core Infrastructure
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
        """Registriert die Standard-Tools im Plugin-Registry.
        
        Diese Tools stehen allen Agenten zur Verfügung:
        - shell: Shell-Befehle ausführen (mit Sicherheits-Allowlist)
        - read_file: Dateien lesen
        - write_file: Dateien schreiben
        - list_dir: Verzeichnisinhalt auflisten
        - git_*: Git-Operationen (status, commit, log)
        
        Neue Tools können später mit self.tools.register() hinzugefügt werden.
        """
        self.tools.register("shell", shell, "Execute shell commands (allowlisted)")
        self.tools.register("read_file", read_file, "Read a file")
        self.tools.register("write_file", lambda p: write_file(p), "Write a file")
        self.tools.register("list_dir", list_dir, "List directory contents")
        self.tools.register("git_status", lambda _: git_status(), "Git status")
        self.tools.register("git_commit", git_commit, "Git commit")
        self.tools.register("git_log", lambda _: git_log(), "Git log")

    def run_task(self, task: str) -> str:
        """Führt einen einzelnen Task durch die vollständige Pipeline.
        
        Prozessablauf:
        1. Memory-Kontext: Sucht ähnliche Tasks in der Vector-Datenbank
        2. Routing: Router bestimmt den optimalen Ausführungsmodus
        3. Planung (optional): Bei "planner" Mode werden Subtasks erzeugt
        4. Ausführung: Worker führt den Task mit LLM und Tools aus
        5. Review: Reviewer bewertet Qualität und Vollständigkeit
        6. Memory-Update: Ergebnis wird für zukünftige Anfragen gespeichert
        
        Args:
            task: Textuelle Beschreibung des auszuführenden Tasks
        
        Returns:
            str: Vollständiges Ergebnis oder Status-Nachricht (z.B. bei Planung)
        
        Hinweis:
            - Bei "planner" Mode werden Subtasks in die Queue eingereiht
            - Der Reviewer kann "approved=False" zurückgeben wenn Qualität gering ist
            - Ergebnisse werden automatisch in Memory gespeichert
        """
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
        """Startet den autonomen Task-Loop für kontinuierliche Verarbeitung.
        
        Diese Methode blockiert und läuft solange bis manuell unterbrochen (Ctrl+C):
        
        Ablauf in jeder Iteration:
        1. TaskQueue: Nächsten Task aus der Warteschlange holen
        2. Bei Task vorhanden: Setze Status auf "running"
        3. Ausführung: run_task() aufrufen für die vollständige Pipeline
        4. Status-Update: Task als "completed" oder "failed" markieren
        5. Pause: 1-2 Sekunden Wartezeit vor der nächsten Task
        
        Fehlerbehandlung:
        - Exceptions werden gefangen und in der TaskQueue protokolliert
        - Agent läuft weiter auch wenn einzelne Tasks fehlschlagen
        
        Polling:
        - Wenn Queue leer: 2 Sekunden warten, dann erneut prüfen
        - Dies ermöglicht asynchrone Task-Hinzufügung während der Ausführung
        
        Hinweis:
            Drücke Ctrl+C um den Loop zu stoppen. Die Logs zeigen alle ausgeführten Tasks.
        """
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
