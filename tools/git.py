"""Git Tool — automatisierte Git-Operationen (mit Bestätigung)."""

import subprocess


def git_status() -> str:
    """Gibt den aktuellen Git-Status zurück."""
    try:
        return subprocess.getoutput("git status --short")
    except Exception as e:
        return f"❌ Git Fehler: {e}"


def git_commit(message: str, auto_add: bool = True) -> str:
    """Erstellt einen Git-Commit (mit optionalem auto-add).

    WICHTIG: Wird nur mit expliziter Bestätigung ausgeführt.
    """
    try:
        if auto_add:
            subprocess.run(["git", "add", "."], check=True)
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True, text=True
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"❌ Git Commit Fehler: {e}"


def git_log(count: int = 5) -> str:
    """Gibt die letzten N Commits zurück."""
    try:
        return subprocess.getoutput(f"git log --oneline -n {count}")
    except Exception as e:
        return f"❌ Git Fehler: {e}"
