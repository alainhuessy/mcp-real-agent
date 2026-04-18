"""Worker Agent — führt Tasks aus mit LLM + Tools."""

import time
from rich.console import Console
from core.llm import LLM
from core.router import Router
from core.logger import log_debug, log_info, log_error
from tools.registry import ToolRegistry
from tasks.auto_todo_tracker import AutoTodoTracker
from tasks.result_inspector import save_result


WORKER_SYSTEM = """You are a worker agent in an AI Operating System.
Execute the given task precisely. If the task requires code, write clean code.
If the task requires a shell command, prefix it with SHELL: followed by the command.
Be concise and actionable."""

console = Console()


class WorkerAgent:
    """Execution Agent — nutzt LLM und Tools zur Task-Ausführung."""

    def __init__(self, llm: LLM, router: Router, tools: ToolRegistry):
        """Initialize Worker Agent with LLM, Router, and Tool Registry.
        
        Args:
            llm: LLM instance for execution
            router: Router for model selection
            tools: Tool Registry for available tools
        """
        self.llm = llm
        self.router = router
        self.tools = tools
        self.tracker = None  # Wird bei tracked_execute() gesetzt

    def execute(self, task: str, memory_context: list[str] | None = None) -> str:
        """Führt einen einzelnen Task aus (ohne Tracking)."""
        import hashlib
        task_id = hashlib.md5(task.encode()).hexdigest()[:8]
        
        log_info("WORKER", f"[{task_id}] Execute task: {task[:50]}...")
        
        try:
            mode = self.router.route(task)
            log_debug("WORKER", f"[{task_id}] Router mode: {mode}")
            
            model = self.llm.get_model(mode)
            log_debug("WORKER", f"[{task_id}] Model: {model}")

            ctx = "\n".join(memory_context) if memory_context else "No context."

            prompt = f"""TASK:\n{task}\n\nMEMORY CONTEXT:\n{ctx}\n\nExecute this task."""

            result = self.llm.ask(model, prompt, system=WORKER_SYSTEM)
            log_debug("WORKER", f"[{task_id}] LLM response: {len(result)} chars")

            # Shell-Befehle erkennen und ausführen
            if "SHELL:" in result:
                log_debug("WORKER", f"[{task_id}] Shell commands found")
                for line in result.split("\n"):
                    if line.strip().startswith("SHELL:"):
                        cmd = line.replace("SHELL:", "").strip()
                        log_info("WORKER", f"[{task_id}] Execute shell: {cmd}")
                        shell_result = self.tools.run("shell", cmd)
                        result += f"\n\n[Shell Output]\n{shell_result}"
            
            log_info("WORKER", f"[{task_id}] Task completed successfully")
            return result
            
        except Exception as e:
            log_error("WORKER", f"[{task_id}] Task failed", e)
            raise

    def tracked_execute(self, task: str, memory_context: list[str] | None = None, 
                       show_progress: bool = True) -> str:
        """
        Führt einen Task aus MIT automatischem Todo-Tracking.
        
        Args:
            task: Task-Beschreibung
            memory_context: Kontext aus Memory
            show_progress: Ob Progress bars in Terminal angezeigt werden
        
        Returns:
            Task-Ergebnis
        """
        import hashlib
        task_id = hashlib.md5(task.encode()).hexdigest()[:8]
        
        log_info("WORKER", f"[{task_id}] Tracked execution started: {task[:50]}...")
        
        # ── Tracker starten ──
        self.tracker = AutoTodoTracker(task)
        
        if show_progress:
            console.print(f"\n🎯 Task gestartet: [bold cyan]{task}[/bold cyan]")
        
        try:
            # ── Step 1: Analysieren ──
            if show_progress:
                console.print("\n[1/4] 📊 Analysiere Task...")
            self.tracker.add_todo("1. Analyze requirements")
            self.tracker.mark_inprogress(1)
            log_debug("WORKER", f"[{task_id}] Phase 1: Analyzing")
            time.sleep(0.2)  # Simulate work
            self.tracker.mark_completed(1)
            
            if show_progress:
                console.print(f"✅ Analyzed\n{self.tracker._get_status_bar()}\n")

            # ── Step 2: Planen ──
            if show_progress:
                console.print("[2/4] 📋 Erstelle Ausführungsplan...")
            self.tracker.add_todo("2. Create execution plan")
            self.tracker.mark_inprogress(2)
            
            mode = self.router.route(task)
            if show_progress:
                console.print(f"   Router → Mode: [cyan]{mode}[/cyan]")
            log_info("WORKER", f"[{task_id}] Phase 2: Planning - Mode: {mode}")
            time.sleep(0.2)
            self.tracker.mark_completed(2)
            
            if show_progress:
                console.print(f"✅ Plan erstellt\n{self.tracker._get_status_bar()}\n")

            # ── Step 3: Ausführen ──
            if show_progress:
                console.print("[3/4] ⚡ Führe aus...")
            self.tracker.add_todo("3. Execute task with LLM")
            self.tracker.mark_inprogress(3)
            
            model = self.llm.get_model(mode)
            ctx = "\n".join(memory_context) if memory_context else "No context."
            prompt = f"""TASK:\n{task}\n\nMEMORY CONTEXT:\n{ctx}\n\nExecute this task."""
            
            log_debug("WORKER", f"[{task_id}] Phase 3: Calling LLM - Model: {model}")
            result = self.llm.ask(model, prompt, system=WORKER_SYSTEM)
            
            if show_progress:
                console.print(f"   LLM Response:{result[:200]}...")
            log_debug("WORKER", f"[{task_id}] LLM response: {len(result)} chars")
            
            # Shell-Befehle verarbeiten
            if "SHELL:" in result:
                for line in result.split("\n"):
                    if line.strip().startswith("SHELL:"):
                        cmd = line.replace("SHELL:", "").strip()
                        if show_progress:
                            console.print(f"   🖥️  Führe Shell aus: [dim]{cmd[:50]}[/dim]")
                        log_info("WORKER", f"[{task_id}] Shell: {cmd}")
                        shell_result = self.tools.run("shell", cmd)
                        result += f"\n\n[Shell Output]\n{shell_result}"
            
            time.sleep(0.2)
            self.tracker.mark_completed(3)
            
            if show_progress:
                console.print(f"✅ Ausgeführt\n{self.tracker._get_status_bar()}\n")

            # ── Step 4: Testen ──
            if show_progress:
                console.print("[4/4] 🧪 Teste Ergebnis...")
            self.tracker.add_todo("4. Verify & test result")
            self.tracker.mark_inprogress(4)
            log_debug("WORKER", f"[{task_id}] Phase 4: Verifying")
            time.sleep(0.2)
            self.tracker.mark_completed(4)
            
            if show_progress:
                console.print(f"✅ Verifiziert\n{self.tracker._get_status_bar()}\n")

        except Exception as e:
            self.tracker.mark_failed(len(self.tracker.todos), str(e))
            if show_progress:
                console.print(f"[red]❌ Error: {e}[/red]")
            log_error("WORKER", f"[{task_id}] Tracked execution failed", e)
        
        # ── Final Summary ──
        if show_progress:
            console.print("\n[bold green]📊 Execution Summary[/bold green]")
            self.tracker.print_todos()
            self.tracker.print_summary()
        
        log_info("WORKER", f"[{task_id}] Tracked execution completed")
        return result

    def start_tracked_task(self, task: str, task_plan: list[str] | None = None) -> AutoTodoTracker:
        """
        Starten einer Task mit automatischem Todo-Tracking.
        Nutze dies für bessere Kontrolle über einzelne Steps.
        
        Args:
            task: Task-Name
            task_plan: Liste von Subtasks
        
        Returns:
            AutoTodoTracker instance für weitere Kontrolle
        """
        self.tracker = AutoTodoTracker(task)
        
        if task_plan:
            self.tracker.add_todos_from_plan(task_plan)
            console.print(f"\n🎯 Task: [bold cyan]{task}[/bold cyan]")
            self.tracker.print_todos()
        
        return self.tracker
