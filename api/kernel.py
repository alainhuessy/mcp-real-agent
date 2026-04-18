"""API Kernel — FastAPI REST Interface für das Agent OS."""

from fastapi import FastAPI
from pydantic import BaseModel

from core.agent import AgentOS

app = FastAPI(title="Agent OS v2.1", description="Local AI Operating System API")
agent = AgentOS()


class TaskRequest(BaseModel):
    """Request model for task execution.
    
    Attributes:
        task: Task description
        priority: Task priority level (default: 1)
    """
    task: str
    priority: int = 1


class ShellRequest(BaseModel):
    """Request model for shell command execution.
    
    Attributes:
        command: Shell command to execute
    """
    command: str


@app.get("/")
def root():
    """Health check endpoint - returns system status.
    
    Returns:
        dict: Status information
    """
    return {"status": "running", "system": "Agent OS v2.1"}


@app.post("/task")
def add_task(req: TaskRequest):
    """Fügt einen Task zur Queue hinzu und führt ihn aus."""
    result = agent.run_task(req.task)
    return {"task": req.task, "result": result}


@app.post("/task/queue")
def queue_task(req: TaskRequest):
    """Fügt einen Task nur zur Queue hinzu (ohne sofortige Ausführung)."""
    t = agent.tasks.add(req.task, req.priority)
    return {"queued": True, "task_id": t["id"]}


@app.get("/tasks")
def list_tasks():
    """Gibt alle Tasks zurück."""
    return {"tasks": agent.tasks.get_all()}


@app.get("/status")
def status():
    """Get system status and metrics.
    
    Returns:
        dict: System status and performance metrics
    """
    return {
        "status": "running",
        "pending_tasks": agent.tasks.get_pending_count(),
        "tools": agent.tools.list_tools(),
    }


@app.post("/shell")
def run_shell(req: ShellRequest):
    """Führt einen Shell-Befehl über das Tool Registry aus."""
    result = agent.tools.run("shell", req.command)
    return {"command": req.command, "output": result}


@app.get("/memory/search")
def search_memory(q: str):
    """Sucht im Memory."""
    results = agent.memory.search(q)
    return {"query": q, "results": results}
