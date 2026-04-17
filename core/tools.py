"""Legacy tools — safe shell execution (siehe auch tools/shell.py)."""

import subprocess


def run_shell(cmd: str) -> str:
    """Führt einen Shell-Befehl aus (nur erlaubte Kommandos)."""
    allowed = ["ls", "dir", "mkdir", "pwd", "echo", "cat", "type", "whoami"]
    base = cmd.split()[0] if cmd.strip() else ""

    if base not in allowed:
        return f"❌ Befehl blockiert: '{base}'"

    try:
        return subprocess.getoutput(cmd)
    except Exception as e:
        return f"❌ Shell Fehler: {e}"
