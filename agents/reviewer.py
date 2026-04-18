"""Reviewer Agent — prüft und validiert Worker-Output."""

from core.llm import LLM


REVIEWER_SYSTEM = """You are a reviewer agent in an AI Operating System.
Your job is to validate the output of a worker agent.
Check for: correctness, completeness, code quality, potential issues.
Return one of:
- APPROVED: if the output is good
- NEEDS_FIX: <reason> if something needs improvement
Be concise."""


class ReviewerAgent:
    """Quality Gate — validiert Ergebnisse vor Memory-Speicherung."""

    def __init__(self, llm: LLM):
        """Initialize Reviewer Agent with LLM instance.
        
        Args:
            llm: LLM instance for reviewing outputs
        """
        self.llm = llm

    def review(self, task: str, output: str) -> dict:
        """Prüft den Output eines Workers."""
        prompt = f"""ORIGINAL TASK:\n{task}\n\nWORKER OUTPUT:\n{output}\n\nReview this output."""

        model = self.llm.get_model("chat")
        result = self.llm.ask(model, prompt, system=REVIEWER_SYSTEM)

        approved = result.strip().upper().startswith("APPROVED")

        return {
            "approved": approved,
            "feedback": result,
            "status": "approved" if approved else "needs_fix",
        }
