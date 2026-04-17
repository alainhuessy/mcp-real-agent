"""Router — intelligente Modellwahl basierend auf Task-Inhalt."""


class Router:
    """Analysiert einen Task-Text und wählt den passenden Modus."""

    ROUTES = {
        "coder": ["code", "bug", "refactor", "api", "function", "class", "test", "implement"],
        "rag": ["docs", "research", "pdf", "document", "knowledge", "search"],
        "planner": ["plan", "architecture", "design", "build", "create system", "project", "structure"],
    }

    def route(self, task: str) -> str:
        """Gibt den Modus zurück: coder / rag / planner / chat."""
        t = task.lower()
        for mode, keywords in self.ROUTES.items():
            if any(kw in t for kw in keywords):
                return mode
        return "chat"
