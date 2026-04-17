"""Planner Agent — zerlegt grosse Ziele in Subtasks."""

from core.llm import LLM


PLANNER_SYSTEM = """You are a planner agent in an AI Operating System.
Your job is to break down a user goal into clear, actionable subtasks.
Return a numbered list of tasks. Each task should be specific and executable.
Do NOT explain — just return the task list."""


class PlannerAgent:
    """Strategisches Planungsmodul — erzeugt Task-Listen aus Zielen."""

    def __init__(self, llm: LLM):
        self.llm = llm

    def plan(self, goal: str, context: list[str] | None = None) -> list[str]:
        """Zerlegt ein Ziel in eine Liste von Subtasks."""
        ctx = "\n".join(context) if context else "No prior context."

        prompt = f"""GOAL:\n{goal}\n\nCONTEXT:\n{ctx}\n\nCreate a numbered task list."""

        model = self.llm.get_model("planner")
        result = self.llm.ask(model, prompt, system=PLANNER_SYSTEM)

        # Parse nummerierte Liste
        tasks = []
        for line in result.strip().split("\n"):
            line = line.strip()
            if line and line[0].isdigit():
                # Entferne Nummerierung
                cleaned = line.lstrip("0123456789.)-: ")
                if cleaned:
                    tasks.append(cleaned)

        return tasks if tasks else [goal]  # Fallback: Original-Goal
