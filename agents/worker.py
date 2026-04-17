"""Worker Agent — führt Tasks aus mit LLM + Tools."""

from core.llm import LLM
from core.router import Router
from tools.registry import ToolRegistry


WORKER_SYSTEM = """You are a worker agent in an AI Operating System.
Execute the given task precisely. If the task requires code, write clean code.
If the task requires a shell command, prefix it with SHELL: followed by the command.
Be concise and actionable."""


class WorkerAgent:
    """Execution Agent — nutzt LLM und Tools zur Task-Ausführung."""

    def __init__(self, llm: LLM, router: Router, tools: ToolRegistry):
        self.llm = llm
        self.router = router
        self.tools = tools

    def execute(self, task: str, memory_context: list[str] | None = None) -> str:
        """Führt einen einzelnen Task aus."""
        mode = self.router.route(task)
        model = self.llm.get_model(mode)

        ctx = "\n".join(memory_context) if memory_context else "No context."

        prompt = f"""TASK:\n{task}\n\nMEMORY CONTEXT:\n{ctx}\n\nExecute this task."""

        result = self.llm.ask(model, prompt, system=WORKER_SYSTEM)

        # Shell-Befehle erkennen und ausführen
        if "SHELL:" in result:
            for line in result.split("\n"):
                if line.strip().startswith("SHELL:"):
                    cmd = line.replace("SHELL:", "").strip()
                    shell_result = self.tools.run("shell", cmd)
                    result += f"\n\n[Shell Output]\n{shell_result}"

        return result
