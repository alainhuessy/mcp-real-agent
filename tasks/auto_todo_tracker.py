"""
Automatic Todo-Tracking System für MCP-Agent v2.1
Agent erstellt AUTO eine Todo-Liste und updated sie während Ausführung
"""

from typing import Optional, Callable
from datetime import datetime
import json
from pathlib import Path
from enum import Enum

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track

console = Console()


# ════════════════════════════════════════════════════════════════════════════
# DATA MODEL
# ════════════════════════════════════════════════════════════════════════════

class TodoStatus(Enum):
    """Todo Status"""
    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TodoItem:
    """Einzelner Todo-Eintrag"""
    
    def __init__(self, id: int, title: str, description: str = ""):
        """Initialize a new Todo Item.
        
        Args:
            id: Unique todo identifier
            title: Todo title/name
            description: Detailed description (optional)
        """
        self.id = id
        self.title = title
        self.description = description
        self.status = TodoStatus.NOT_STARTED
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.sub_tasks: list["TodoItem"] = []
    
    def to_dict(self) -> dict:
        """Serialize to dict"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
        }
    
    def get_duration(self) -> Optional[float]:
        """Get duration in seconds if completed"""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


# ════════════════════════════════════════════════════════════════════════════
# AUTOMATIC TODO TRACKER
# ════════════════════════════════════════════════════════════════════════════

class AutoTodoTracker:
    """
    Automatisches Todo-Tracking System
    
    Der Agent erstellt automatisch eine Todo-Liste für jeden Task
    und updated sie während Ausführung
    """
    
    def __init__(self, task_name: str, save_dir: str = "./task_logs"):
        """
        Initialize Auto Todo Tracker
        
        Args:
            task_name: Name des Tasks (wird zu filename)
            save_dir: Verzeichnis für Task-Logs
        """
        self.task_name = task_name
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        self.todos: list[TodoItem] = []
        self.current_todo: Optional[TodoItem] = None
        self.task_start_time = datetime.now()
        self.task_completed = False
        
        # Auto-save
        self.auto_save = True
        
        console.print(Panel(
            f"[bold cyan]🎯 Auto Todo-Tracker Started: {task_name}[/bold cyan]",
            style="cyan"
        ))
    
    # ── Recording Phase: Todos erstellen ──
    
    def add_todo(self, title: str, description: str = "") -> TodoItem:
        """
        Füge einen Todo hinzu
        
        Args:
            title: Kurztitel (3-7 Worte)
            description: Optionale Beschreibung
            
        Returns:
            TodoItem Instanz
        """
        todo_id = len(self.todos) + 1
        todo = TodoItem(todo_id, title, description)
        self.todos.append(todo)
        
        console.print(f"[dim]📋 Todo hinzugefügt: [{todo_id}] {title}[/dim]")
        return todo
    
    def add_todos_from_plan(self, plan: list[str]) -> list[TodoItem]:
        """
        Füge multiple Todos aus einer Plan-Liste hinzu
        
        Args:
            plan: Liste von Todo-Titles
            
        Returns:
            Liste der erstellten TodoItems
        """
        console.print(f"[cyan]📝 Creating {len(plan)} todos from plan...[/cyan]")
        todos = []
        for title in plan:
            todo = self.add_todo(title)
            todos.append(todo)
        return todos
    
    # ── Tracking Phase: Progress updaten ──
    
    def mark_inprogress(self, todo_id: int) -> TodoItem:
        """
        Markiere einen Todo als in-progress
        
        Args:
            todo_id: ID des Todos
            
        Returns:
            Updated TodoItem
        """
        todo = self._get_todo(todo_id)
        if not todo:
            raise ValueError(f"Todo {todo_id} nicht gefunden")
        
        todo.status = TodoStatus.IN_PROGRESS
        todo.started_at = datetime.now()
        self.current_todo = todo
        
        status_bar = self._get_status_bar()
        console.print(f"[yellow]▶️  Started: [{todo.id}] {todo.title}[/yellow]")
        console.print(status_bar)
        
        if self.auto_save:
            self._save()
        
        return todo
    
    def mark_completed(self, todo_id: int, note: str = "") -> TodoItem:
        """
        Markiere einen Todo als completed
        
        Args:
            todo_id: ID des Todos
            note: Optionale Notiz
            
        Returns:
            Updated TodoItem
        """
        todo = self._get_todo(todo_id)
        if not todo:
            raise ValueError(f"Todo {todo_id} nicht gefunden")
        
        todo.status = TodoStatus.COMPLETED
        todo.completed_at = datetime.now()
        duration = todo.get_duration()
        
        duration_str = f" ({duration:.1f}s)" if duration else ""
        console.print(f"[green]✅ Completed: [{todo.id}] {todo.title}{duration_str}[/green]")
        
        if note:
            console.print(f"   📝 Note: {note}")
        
        status_bar = self._get_status_bar()
        console.print(status_bar)
        
        if self.auto_save:
            self._save()
        
        return todo
    
    def mark_failed(self, todo_id: int, error: str) -> TodoItem:
        """
        Markiere einen Todo als failed
        
        Args:
            todo_id: ID des Todos
            error: Fehlermeldung
            
        Returns:
            Updated TodoItem
        """
        todo = self._get_todo(todo_id)
        if not todo:
            raise ValueError(f"Todo {todo_id} nicht gefunden")
        
        todo.status = TodoStatus.FAILED
        todo.error_message = error
        todo.completed_at = datetime.now()
        
        console.print(f"[red]❌ Failed: [{todo.id}] {todo.title}[/red]")
        console.print(f"   [red]Error: {error}[/red]")
        
        status_bar = self._get_status_bar()
        console.print(status_bar)
        
        if self.auto_save:
            self._save()
        
        return todo
    
    def mark_blocked(self, todo_id: int, reason: str) -> TodoItem:
        """
        Markiere einen Todo als blocked
        
        Args:
            todo_id: ID des Todos
            reason: Warum ist es blockiert?
            
        Returns:
            Updated TodoItem
        """
        todo = self._get_todo(todo_id)
        if not todo:
            raise ValueError(f"Todo {todo_id} nicht gefunden")
        
        todo.status = TodoStatus.BLOCKED
        todo.error_message = reason
        
        console.print(f"[yellow]🚫 Blocked: [{todo.id}] {todo.title}[/yellow]")
        console.print(f"   [yellow]Reason: {reason}[/yellow]")
        
        if self.auto_save:
            self._save()
        
        return todo
    
    # ── Status & Reporting ──
    
    def _get_status_bar(self) -> str:
        """Erstelle eine Status-Bar"""
        total = len(self.todos)
        completed = sum(1 for t in self.todos if t.status == TodoStatus.COMPLETED)
        inprogress = sum(1 for t in self.todos if t.status == TodoStatus.IN_PROGRESS)
        failed = sum(1 for t in self.todos if t.status == TodoStatus.FAILED)
        
        pct = int((completed / total) * 100) if total > 0 else 0
        bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
        
        return (f"[cyan]Progress: [{bar}] {pct}% "
                f"({completed}/{total} done, {inprogress} running, {failed} failures)[/cyan]")
    
    def get_summary(self) -> dict:
        """Get execution summary"""
        total = len(self.todos)
        completed = sum(1 for t in self.todos if t.status == TodoStatus.COMPLETED)
        inprogress = sum(1 for t in self.todos if t.status == TodoStatus.IN_PROGRESS)
        failed = sum(1 for t in self.todos if t.status == TodoStatus.FAILED)
        blocked = sum(1 for t in self.todos if t.status == TodoStatus.BLOCKED)
        
        total_duration = (datetime.now() - self.task_start_time).total_seconds()
        
        return {
            "task_name": self.task_name,
            "total_todos": total,
            "completed": completed,
            "in_progress": inprogress,
            "failed": failed,
            "blocked": blocked,
            "completion_percentage": int((completed / total) * 100) if total > 0 else 0,
            "total_duration_seconds": total_duration,
            "status": "COMPLETE" if completed == total and failed == 0 else (
                "FAILED" if failed > 0 else "IN_PROGRESS"
            ),
        }
    
    def print_summary(self):
        """Print beautiful summary table"""
        summary = self.get_summary()
        
        table = Table(title="📊 Todo Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Task", summary["task_name"])
        table.add_row("Total Todos", str(summary["total_todos"]))
        table.add_row("✅ Completed", str(summary["completed"]))
        table.add_row("▶️  In Progress", str(summary["in_progress"]))
        table.add_row("❌ Failed", str(summary["failed"]))
        table.add_row("🚫 Blocked", str(summary["blocked"]))
        table.add_row("Progress", f"{summary['completion_percentage']}%")
        table.add_row("Duration", f"{summary['total_duration_seconds']:.1f}s")
        table.add_row("Status", summary["status"])
        
        console.print(table)
    
    def print_todos(self):
        """Print all todos with current status"""
        table = Table(title="📋 Todos")
        table.add_column("#", width=3)
        table.add_column("Title", style="cyan")
        table.add_column("Status", width=15)
        table.add_column("Time", width=10)
        
        for todo in self.todos:
            status_icon = {
                TodoStatus.NOT_STARTED: "⭕",
                TodoStatus.IN_PROGRESS: "▶️ ",
                TodoStatus.COMPLETED: "✅",
                TodoStatus.FAILED: "❌",
                TodoStatus.BLOCKED: "🚫",
            }.get(todo.status, "?")
            
            duration = ""
            if todo.get_duration():
                duration = f"{todo.get_duration():.1f}s"
            
            table.add_row(
                str(todo.id),
                todo.title,
                f"{status_icon} {todo.status.value}",
                duration,
            )
        
        console.print(table)
    
    # ── Persistence ──
    
    def _save(self):
        """Save todos to JSON file"""
        filename = self.save_dir / f"{self.task_name.replace(' ', '_')}.json"
        data = {
            "task_name": self.task_name,
            "created_at": self.task_start_time.isoformat(),
            "todos": [t.to_dict() for t in self.todos],
            "summary": self.get_summary(),
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    
    def save_and_exit(self):
        """Save todos and mark task as complete"""
        self.task_completed = True
        self._save()
        
        self.print_todos()
        self.print_summary()
        
        console.print(Panel(
            f"[bold green]✅ Task Complete: {self.task_name}[/bold green]",
            style="green"
        ))
    
    # ── Helper ──
    
    def _get_todo(self, todo_id: int) -> Optional[TodoItem]:
        """Get todo by ID"""
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        return None


# ════════════════════════════════════════════════════════════════════════════
# INTEGRATION WITH AGENT
# ════════════════════════════════════════════════════════════════════════════

class AgentWithAutoTodo:
    """Mixin for Agents to support auto todo tracking"""
    
    def __init__(self):
        """Initialize Agent with Auto Todo tracking capability."""
        self.current_tracker: Optional[AutoTodoTracker] = None
    
    def start_tracked_task(self, task_name: str, plan: list[str]) -> AutoTodoTracker:
        """
        Start a new task with automatic todo tracking
        
        Usage:
            tracker = agent.start_tracked_task("Implement Feature X", [
                "Analyze requirements",
                "Write implementation",
                "Create tests",
                "Run tests and fix failures",
            ])
        """
        self.current_tracker = AutoTodoTracker(task_name)
        self.current_tracker.add_todos_from_plan(plan)
        return self.current_tracker
    
    def mark_current_todo_done(self, note: str = ""):
        """Mark current todo as done"""
        if self.current_tracker and self.current_tracker.current_todo:
            self.current_tracker.mark_completed(
                self.current_tracker.current_todo.id,
                note
            )
    
    def mark_current_todo_failed(self, error: str):
        """Mark current todo as failed"""
        if self.current_tracker and self.current_tracker.current_todo:
            self.current_tracker.mark_failed(
                self.current_tracker.current_todo.id,
                error
            )
    
    def finish_task(self):
        """Finish tracked task"""
        if self.current_tracker:
            self.current_tracker.save_and_exit()


# ════════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Example: Track a complex task
    tracker = AutoTodoTracker("Build MCP Agent")
    
    todos = tracker.add_todos_from_plan([
        "Analyze requirements",
        "Set up project structure",
        "Implement core components",
        "Write comprehensive tests",
        "Deploy to production",
    ])
    
    # Simulate execution
    for i, todo in enumerate(todos):
        import time
        tracker.mark_inprogress(todo.id)
        time.sleep(1)  # Simulate work
        tracker.mark_completed(todo.id, f"Step {i+1} complete")
    
    # Print final report
    tracker.save_and_exit()
