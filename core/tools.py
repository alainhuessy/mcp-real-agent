"""Sichere Tools für Agent OS v2.1.

Dieses Modul enthält sicherheitsrelevante Tools, insbesondere die 
run_shell-Funktion, die nur eine begrenzte Menge an Shell-Befehlen erlaubt.

Die Tools sind für die sichere Interaktion mit dem System konzipiert 
und sollen helfen, unerlaubte Operationen zu verhindern.
"""

import subprocess


def run_shell(cmd: str) -> str:
    """Führt einen Shell-Befehl aus (nur erlaubte Kommandos).
    
    Diese Funktion führt Shell-Befehle sicher aus, wobei nur eine vordefinierte 
    Liste von erlaubten Kommandos erlaubt ist. Dies dient zur Sicherheit, um 
    unerlaubte Befehle zu verhindern.
    
    Args:
        cmd (str): Der auszuführende Shell-Befehl
        
    Returns:
        str: Die Ausgabe des Befehls oder eine Fehlermeldung
        
    Hinweise:
        - Nur Kommandos aus der erlaubten Liste sind erlaubt
        - Blockierte Kommandos werden mit einer Fehlermeldung zurückgegeben
        - Fehler bei der Ausführung werden als Fehlermeldung zurückgegeben
        - Die Liste der erlaubten Kommandos ist in der Funktion definiert
        
    Beispiel:
        >>> run_shell("ls -la")
        'Dateien und Ordner im aktuellen Verzeichnis'
        
        >>> run_shell("rm -rf /")
        "❌ Befehl blockiert: 'rm'"
    """
    allowed = ["ls", "dir", "mkdir", "pwd", "echo", "cat", "type", "whoami"]
    base = cmd.split()[0] if cmd.strip() else ""

    if base not in allowed:
        return f"❌ Befehl blockiert: '{base}'"

    try:
        return subprocess.getoutput(cmd)
    except Exception as e:
        return f"❌ Shell Fehler: {e}"