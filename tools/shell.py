"""Shell Tool — geschützte Shell-Ausführung mit Allowlist."""

import subprocess

ALLOWED_COMMANDS = [
    "ls", "dir", "mkdir", "pwd", "echo", "cat", "type",
    "whoami", "date", "python", "pip", "git",
]

BLOCKED_PATTERNS = ["rm -rf", "mkfs", "shutdown", "reboot", "format", "del /s"]


def shell(cmd: str) -> str:
    """Führt einen Shell-Befehl aus (nur erlaubte Kommandos)."""
    if not cmd.strip():
        return "❌ Leerer Befehl"

    # Blockierte Patterns prüfen
    for pattern in BLOCKED_PATTERNS:
        if pattern in cmd.lower():
            return f"❌ Befehl blockiert (Pattern: '{pattern}')"

    base = cmd.split()[0]
    if base not in ALLOWED_COMMANDS:
        return f"❌ Befehl nicht erlaubt: '{base}'"

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        return result.stdout or result.stderr or "(kein Output)"
    except subprocess.TimeoutExpired:
        return "❌ Timeout (30s)"
    except Exception as e:
        return f"❌ Shell Fehler: {e}"
