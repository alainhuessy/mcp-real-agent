"""Task Queue — Aufgabenverwaltung mit Prioritäten."""

from datetime import datetime
from typing import Optional
import uuid


class TaskQueue:
    """In-Memory Task Queue mit Status-Management."""

    def __init__(self):
        """Initialize empty task queue for task management."""
        self.tasks: list[dict] = []

    def add(self, task: str, priority: int = 1, context: list[str] | None = None) -> dict:
        """Fügt einen neuen Task hinzu."""
        t = {
            "id": str(uuid.uuid4())[:8],
            "task": task,
            "status": "pending",
            "priority": priority,
            "context": context or [],
            "created": datetime.now().isoformat(),
        }
        self.tasks.append(t)
        return t

    def get_next(self) -> Optional[dict]:
        """Gibt den nächsten pending Task zurück (höchste Priorität)."""
        pending = [t for t in self.tasks if t["status"] == "pending"]
        if not pending:
            return None
        pending.sort(key=lambda x: x["priority"], reverse=True)
        return pending[0]

    def complete(self, task: dict) -> None:
        """Markiert einen Task als erledigt."""
        task["status"] = "done"
        task["completed"] = datetime.now().isoformat()

    def fail(self, task: dict, reason: str = "") -> None:
        """Markiert einen Task als fehlgeschlagen."""
        task["status"] = "failed"
        task["error"] = reason

    def get_all(self) -> list[dict]:
        """Gibt alle Tasks zurück."""
        return self.tasks

    def get_pending_count(self) -> int:
        """Get count of pending tasks in queue.
        
        Returns:
            int: Number of pending tasks
        """
        return len([t for t in self.tasks if t["status"] == "pending"])
