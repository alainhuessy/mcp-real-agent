"""Result Inspector — Speichert Task-Ergebnisse für Debugging."""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Any, Optional


class ResultInspector:
    """Speichert und inspiziert Task-Ergebnisse."""
    
    def __init__(self, results_dir: str = "task_results"):
        """Initialize Result Inspector with results directory.
        
        Args:
            results_dir: Directory to store task results (default: task_results/)
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
    
    def save_task_result(
        self,
        task_id: str,
        task_name: str,
        mode: str,
        llm_response: str,
        duration: float,
        status: str = "success",
        error: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Path:
        """
        Speichert Task-Ergebnis in JSON.
        
        Args:
            task_id: Eindeutige Task ID
            task_name: Task Beschreibung
            mode: Router Mode (coder/planner/rag/chat)
            llm_response: LLM Antwort (gekürzt)
            duration: Wie lange Task dauerte
            status: success/failed/timeout
            error: Error-Nachricht (falls fehlgeschlagen)
            metadata: Zusätzliche Infos
        
        Returns:
            Path zur gespeicherten Datei
        """
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"task-{task_id}-{timestamp}.json"
        filepath = self.results_dir / filename
        
        result_data = {
            "metadata": {
                "task_id": task_id,
                "timestamp": timestamp,
                "task_name": task_name,
            },
            "execution": {
                "mode": mode,
                "duration_seconds": round(duration, 2),
                "status": status,
            },
            "llm": {
                "response_preview": llm_response[:500],
                "response_full": llm_response,
                "response_length": len(llm_response),
            },
        }
        
        if error:
            result_data["error"] = error
        
        if metadata:
            result_data["user_metadata"] = metadata
        
        # Speichern
        with open(filepath, "w") as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        # Auch "latest" Link aktualisieren
        latest_link = self.results_dir / "latest.json"
        try:
            if latest_link.exists():
                latest_link.unlink()
            latest_link.symlink_to(filename)
        except (OSError, NotImplementedError):
            # Symlinks nicht supported (z.B. Windows)
            pass
        
        return filepath
    
    def get_latest_results(self, limit: int = 5) -> list[dict]:
        """Gibt die letzten N Ergebnisse zurück."""
        results = []
        
        # Hole alle JSON Dateien
        json_files = sorted(
            self.results_dir.glob("task-*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        for json_file in json_files[:limit]:
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    results.append(data)
            except json.JSONDecodeError:
                pass
        
        return results
    
    def print_latest(self, limit: int = 5):
        """Zeigt letzte Ergebnisse schön formatiert."""
        from rich.console import Console
        from rich.table import Table
        
        console = Console()
        results = self.get_latest_results(limit)
        
        if not results:
            console.print("[dim]Keine Ergebnisse vorhanden[/dim]")
            return
        
        # Tabelle
        table = Table(title="Latest Task Results")
        table.add_column("Task ID", style="cyan")
        table.add_column("Task", style="white")
        table.add_column("Mode", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Duration", style="blue")
        table.add_column("Response Length", style="magenta")
        
        for result in results:
            meta = result["metadata"]
            exec_info = result["execution"]
            llm_info = result["llm"]
            
            status_color = "green" if exec_info["status"] == "success" else "red"
            status_text = f"[{status_color}]{exec_info['status']}[/{status_color}]"
            
            table.add_row(
                meta["task_id"],
                meta["task_name"][:40],
                exec_info["mode"],
                status_text,
                f"{exec_info['duration_seconds']}s",
                f"{llm_info['response_length']} chars",
            )
        
        console.print(table)
    
    def open_result(self, task_id: str):
        """Öffnet ein spezifisches Ergebnis im Editor."""
        results = list(self.results_dir.glob(f"task-{task_id}-*.json"))
        
        if not results:
            print(f"❌ Task {task_id} nicht gefunden")
            return
        
        # Neueste Version
        latest = sorted(results, key=lambda p: p.stat().st_mtime, reverse=True)[0]
        
        with open(latest) as f:
            data = json.load(f)
        
        print(json.dumps(data, indent=2, ensure_ascii=False))


# ──── Global Instance ────────────────────────────────────────

_inspector: Optional[ResultInspector] = None


def get_inspector() -> ResultInspector:
    """Gibt die globale Inspector-Instanz zurück."""
    global _inspector
    if _inspector is None:
        _inspector = ResultInspector()
    return _inspector


# ──── Convenience Functions ────────────────────────────────────

def save_result(
    task_id: str,
    task_name: str,
    mode: str,
    llm_response: str,
    duration: float,
    status: str = "success",
    error: Optional[str] = None,
) -> Path:
    """Speichert ein Task-Ergebnis."""
    return get_inspector().save_task_result(
        task_id=task_id,
        task_name=task_name,
        mode=mode,
        llm_response=llm_response,
        duration=duration,
        status=status,
        error=error,
    )


def show_results(limit: int = 5):
    """Zeigt letzte Ergebnisse."""
    get_inspector().print_latest(limit)


# ──── Example Usage ────────────────────────────────────────────

if __name__ == "__main__":
    inspector = get_inspector()
    
    # Beispiel speichern
    result_path = inspector.save_task_result(
        task_id="001",
        task_name="Create a todo app",
        mode="coder",
        llm_response="def create_todo():\n    todos = []\n    return todos",
        duration=3.4,
        status="success",
    )
    
    print(f"✅ Result saved to: {result_path}")
    print("\nLatest results:")
    inspector.print_latest()
