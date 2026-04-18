"""Planner Agent — zerlegt grosse Ziele in Subtasks."""

from core.llm import LLM


PLANNER_SYSTEM = """You are a planner agent in an AI Operating System for Python development.
Your job is to break down a user goal into clear, actionable subtasks.
Return a numbered list of tasks. Each task should be specific, measurable, and executable.

IMPORTANT: After you read the goal and context, provide your answer ONCE and STOP.
Do not repeat your answer. Do not ask clarifying questions.

When you have PROJECT CONTEXT provided:
- Use it to create PROJECT-SPECIFIC tasks, not generic ones
- Reference actual files, modules, and tools mentioned in the context
- Suggest realistic next steps based on current project status

Do NOT create generic templates - use the provided context!
Return ONLY the numbered list, no explanations. PROVIDE THE ANSWER ONCE AND STOP."""


class PlannerAgent:
    """Strategisches Planungsmodul — erzeugt Task-Listen aus Zielen."""

    def __init__(self, llm: LLM):
        """Initialize Planner Agent with LLM instance.
        
        Args:
            llm: LLM instance for planning tasks
        """
        self.llm = llm

    def plan(self, goal: str, context: list[str] | None = None) -> list[str]:
        """Zerlegt ein Ziel in eine Liste von Subtasks."""
        ctx = "\n\n".join(context) if context else "No project context available."

        # ── Enhanced Prompt with Project Knowledge ──
        prompt = f"""PROJECT CONTEXT:
{ctx}

---

GOAL TO BREAK DOWN:
{goal}

---

Create a numbered task list that is SPECIFIC to this project.
If project context is available, use it to guide your planning.
Return only the numbered list."""

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
