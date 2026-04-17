"""File Tool — Dateioperationen (lesen, schreiben, erstellen)."""

import os


def read_file(path: str) -> str:
    """Liest eine Datei und gibt den Inhalt zurück."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"❌ Datei nicht gefunden: {path}"
    except Exception as e:
        return f"❌ Lesefehler: {e}"


def write_file(path: str, content: str = "") -> str:
    """Schreibt Inhalt in eine Datei (erstellt Verzeichnisse automatisch)."""
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ Datei geschrieben: {path}"
    except Exception as e:
        return f"❌ Schreibfehler: {e}"


def list_dir(path: str = ".") -> str:
    """Listet den Inhalt eines Verzeichnisses auf."""
    try:
        entries = os.listdir(path)
        return "\n".join(entries) if entries else "(leer)"
    except Exception as e:
        return f"❌ Fehler: {e}"
