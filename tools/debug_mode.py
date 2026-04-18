"""Debug Mode — Detaillierte Debug-Ausgabe für Tasks."""

import time
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.llm import LLM
from core.router import Router
from core.logger import log_debug, log_info, log_error
from tasks.result_inspector import save_result
from memory.memory import Memory
from tools.registry import ToolRegistry
from agents.worker import WorkerAgent
from agents.reviewer import ReviewerAgent


class DebugMode:
    """Detaillierte Debug-Ausgabe für Task-Ausführung."""
    
    def __init__(self):
        """Initialize Debug Mode with console output and agent components."""
        self.console = Console()
        self.llm = LLM()
        self.router = Router()
        self.memory = Memory()
        self.tools = ToolRegistry()
        self.worker = WorkerAgent(self.llm, self.router, self.tools)
        self.reviewer = ReviewerAgent(self.llm)
        
        self.start_time = None
        self.task_id = None
    
    def execute_debug(self, task: str, task_id: str = None) -> str:
        """
        Führt einen Task im Debug Mode aus.
        
        Args:
            task: Task Beschreibung
            task_id: Optional: Task ID (für Tracking)
        
        Returns:
            Task Ergebnis
        """
        import hashlib
        
        self.start_time = time.time()
        self.task_id = task_id or hashlib.md5(task.encode()).hexdigest()[:8]
        
        # ──────────────────────────────────────────────────
        # PHASE 1: ANALYSIEREN
        # ──────────────────────────────────────────────────
        
        self.console.print(Panel(
            f"[bold cyan]🔍 DEBUG MODE[/bold cyan]\n"
            f"[dim]Task ID: {self.task_id}[/dim]\n"
            f"[dim]Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
            border_style="cyan"
        ))
        
        self.console.print("\n[bold]PHASE 1: ANALYSIS[/bold]")
        self.console.print(f"  Task: [cyan]{task}[/cyan]")
        
        # Logging
        log_debug("DEBUG", f"Task gestartet: {task[:50]}...")
        
        # ──────────────────────────────────────────────────
        # PHASE 2: ROUTING
        # ──────────────────────────────────────────────────
        
        self.console.print("\n[bold]PHASE 2: ROUTING[/bold]")
        
        mode = self.router.route(task)
        self.console.print(f"  Input: [cyan]{task[:50]}...[/cyan]")
        self.console.print(f"  [arrow] Router Decision: [yellow]{mode}[/yellow]")
        
        log_info("ROUTER", f"Mode selected: {mode}")
        
        # Get Model
        model = self.llm.get_model(mode)
        self.console.print(f"  [arrow] Model: [yellow]{model}[/yellow]")
        
        # ──────────────────────────────────────────────────
        # PHASE 3: MEMORY
        # ──────────────────────────────────────────────────
        
        self.console.print("\n[bold]PHASE 3: MEMORY SEARCH[/bold]")
        
        memory_results = self.memory.search(task, n_results=3)
        self.console.print(f"  Query: [cyan]{task[:50]}[/cyan]")
        self.console.print(f"  Results: [yellow]{len(memory_results)}[/yellow] similar tasks")
        
        if memory_results:
            for i, result in enumerate(memory_results, 1):
                self.console.print(f"    [{i}] {result[:60]}...")
        
        log_info("MEMORY", f"Found {len(memory_results)} similar tasks")
        
        # ──────────────────────────────────────────────────
        # PHASE 4: LLM EXECUTION
        # ──────────────────────────────────────────────────
        
        self.console.print("\n[bold]PHASE 4: LLM EXECUTION[/bold]")
        
        try:
            # Build Prompt
            ctx = "\n".join(memory_results) if memory_results else "No context."
            prompt = f"""TASK:\n{task}\n\nMEMORY CONTEXT:\n{ctx}\n\nExecute this task."""
            
            self.console.print(f"  Model: [yellow]{model}[/yellow]")
            self.console.print(f"  Prompt length: [cyan]{len(prompt)}[/cyan] chars")
            self.console.print(f"  Context: [cyan]{len(ctx)}[/cyan] chars from memory")
            
            log_info("LLM", f"Calling {model} with {len(prompt)} char prompt")
            
            # Call LLM
            self.console.print("\n  [dim]→ Waiting for LLM response...[/dim]")
            llm_start = time.time()
            
            result = self.llm.ask(model, prompt, system="Execute tasks precisely and clearly.")
            
            llm_duration = time.time() - llm_start
            self.console.print(f"  [green]✅ Response received ({llm_duration:.1f}s)[/green]")
            
            log_info("LLM", f"Response received in {llm_duration:.1f}s")
            
            # Show Response Preview
            self.console.print("\n  [bold]Response Preview:[/bold]")
            preview = result[:300] if len(result) > 300 else result
            self.console.print(f"  [dim]{preview}...[/dim]" if len(result) > 300 else f"  [dim]{preview}[/dim]")
            
            self.console.print(f"\n  Response length: [cyan]{len(result)}[/cyan] chars")
            
            # ──────────────────────────────────────────────────
            # PHASE 5: SHELL COMMANDS
            # ──────────────────────────────────────────────────
            
            if "SHELL:" in result:
                self.console.print("\n[bold]PHASE 5: SHELL EXECUTION[/bold]")
                
                for line in result.split("\n"):
                    if line.strip().startswith("SHELL:"):
                        cmd = line.replace("SHELL:", "").strip()
                        self.console.print(f"  Command: [yellow]{cmd}[/yellow]")
                        
                        log_info("SHELL", f"Executing: {cmd}")
                        
                        try:
                            shell_result = self.tools.run("shell", cmd)
                            self.console.print(f"  [green]✅ Success[/green]")
                            self.console.print(f"  Output: [dim]{shell_result[:100]}...[/dim]")
                            result += f"\n\n[Shell Output]\n{shell_result}"
                        except Exception as e:
                            self.console.print(f"  [red]❌ Failed: {e}[/red]")
                            log_error("SHELL", f"Shell command failed: {cmd}", e)
            
            # ──────────────────────────────────────────────────
            # PHASE 6: REVIEW
            # ──────────────────────────────────────────────────
            
            self.console.print("\n[bold]PHASE 6: REVIEW[/bold]")
            
            try:
                review = self.reviewer.review(task, result)
                self.console.print(f"  Review: [dim]{review['feedback'][:100]}...[/dim]")
            except Exception as e:
                self.console.print(f"  Review skipped: {str(e)[:50]}...")
                log_debug("REVIEW", f"Review skipped: {e}")
            
            log_info("REVIEW", f"Review completed")
            
            # ──────────────────────────────────────────────────
            # PHASE 5: MEMORY SYNC (speichern für zukünftige Tasks)
            # ──────────────────────────────────────────────────
            
            self.console.print("\n[bold]PHASE 5: MEMORY SYNC[/bold]")
            
            try:
                # Speichere Task + Ergebnis in Shared Memory
                memory_content = f"Task: {task}\nResult: {result[:500]}"
                self.memory.sync(memory_content, task[:30])
                self.console.print(f"  ✅ Synced to shared memory layer")
                log_info("MEMORY", f"Task synced to shared memory")
            except Exception as e:
                self.console.print(f"  ⚠️ Memory sync failed: {str(e)[:50]}...")
                log_error("MEMORY", f"Memory sync failed: {e}")
            
            # ──────────────────────────────────────────────────
            # SUMMARY
            # ──────────────────────────────────────────────────
            
            total_duration = time.time() - self.start_time
            
            # Save Result
            save_result(
                task_id=self.task_id,
                task_name=task,
                mode=mode,
                llm_response=result,
                duration=total_duration,
                status="success",
            )
            
            self.console.print("\n" + "="*60)
            self.console.print("[bold green]✅ DEBUG EXECUTION COMPLETE[/bold green]")
            self.console.print("="*60)
            
            # Summary Table
            summary_table = Table(title="Execution Summary")
            summary_table.add_column("Component", style="cyan")
            summary_table.add_column("Result", style="green")
            
            summary_table.add_row("Task ID", self.task_id)
            summary_table.add_row("Router Mode", mode)
            summary_table.add_row("Model", model)
            summary_table.add_row("Memory Results", f"{len(memory_results)}")
            summary_table.add_row("Response Length", f"{len(result)} chars")
            summary_table.add_row("LLM Duration", f"{llm_duration:.2f}s")
            summary_table.add_row("Total Duration", f"{total_duration:.2f}s")
            summary_table.add_row("Status", "[green]SUCCESS[/green]")
            summary_table.add_row("Result File", f"task_results/task-{self.task_id}-*")
            
            self.console.print(summary_table)
            
            log_info("DEBUG", f"Task completed successfully in {total_duration:.2f}s")
            
            return result
            
        except Exception as e:
            total_duration = time.time() - self.start_time
            
            self.console.print(f"\n[red]❌ ERROR: {e}[/red]")
            
            # Save Error Result
            save_result(
                task_id=self.task_id,
                task_name=task,
                mode=mode,
                llm_response="ERROR",
                duration=total_duration,
                status="failed",
                error=str(e),
            )
            
            log_error("DEBUG", f"Task failed: {str(e)}", e)
            
            raise


# ──── Global Instance ────────────────────────────────────────

_debug_mode: DebugMode = None


def get_debug_mode() -> DebugMode:
    """Gibt die Debug Mode Instanz zurück."""
    global _debug_mode
    if _debug_mode is None:
        _debug_mode = DebugMode()
    return _debug_mode


# ──── Example Usage ────────────────────────────────────────────

if __name__ == "__main__":
    debug = get_debug_mode()
    
    task = "Write a Python function to check if a number is prime"
    result = debug.execute_debug(task)
    
    print("\n" + "="*60)
    print("Final Result:")
    print("="*60)
    print(result)
