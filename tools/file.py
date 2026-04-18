"""File Tool — Dateioperationen (lesen, schreiben, erstellen)."""

import os

# ── Configuration ──
_MAX_FILE_SIZE = 100 * 1024  # 100KB limit
_MAX_PREVIEW_SIZE = 500  # chars for large file preview


def read_file(path: str) -> str:
    """Liest eine Datei und gibt den Inhalt zurück (mit Größen-Limit)."""
    try:
        # ── Normalisiere Pfad ──
        path = os.path.normpath(path)
        abs_path = os.path.abspath(path)
        
        # ── Prüfe ob Datei existiert ──
        if not os.path.isfile(abs_path):
            return f"❌ Datei nicht gefunden: {path}"
        
        # ── Prüfe Dateigröße ──
        file_size = os.path.getsize(abs_path)
        
        if file_size > _MAX_FILE_SIZE:
            # Lese nur Anfang + Ende
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(_MAX_FILE_SIZE)
            return f"⚠️ Datei truncated (zu groß: {file_size} bytes, limit: {_MAX_FILE_SIZE}):\n\n{content}\n\n[...TRUNCATED...]"
        
        # Lese komplette Datei
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        # Zeige Dateigröße für Kontext
        size_mb = file_size / 1024 / 1024
        if size_mb > 1:
            return f"📄 {path} ({size_mb:.2f} MB):\n\n{content}"
        else:
            return content
            
    except FileNotFoundError:
        return f"❌ Datei nicht gefunden: {path}"
    except PermissionError:
        return f"❌ Berechtigung verweigert: {path}"
    except Exception as e:
        return f"❌ Lesefehler: {e}"


def write_file(path: str, content: str = "") -> str:
    """Schreibt Inhalt in eine Datei (erstellt Verzeichnisse automatisch)."""
    try:
        # ── Normalisiere Pfad ──
        path = os.path.normpath(path)
        
        # ── Verzeichnis erstellen ──
        dir_path = os.path.dirname(path) or "."
        os.makedirs(dir_path, exist_ok=True)
        
        # ── Schreibe Datei ──
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        
        file_size = len(content)
        return f"✅ Datei geschrieben: {path} ({file_size} bytes)"
    except Exception as e:
        return f"❌ Schreibfehler: {e}"


def list_dir(path: str = ".") -> str:
    """Listet Verzeichnisinhalt mit Kontext (Dateityp, Größe).
    
    Gibt strukturierte Info zurück damit LLM navigieren kann.
    """
    try:
        # ── Normalisiere Pfad ──
        path = os.path.normpath(path)
        abs_path = os.path.abspath(path)
        
        # ── Prüfe ob Verzeichnis existiert ──
        if not os.path.isdir(abs_path):
            return f"❌ Verzeichnis nicht gefunden: {path}"
        
        # ── Liste Einträge mit Info ──
        entries = []
        for entry in sorted(os.listdir(abs_path)):
            full_path = os.path.join(abs_path, entry)
            
            if os.path.isdir(full_path):
                entries.append(f"📁 {entry}/")
            else:
                try:
                    size = os.path.getsize(full_path)
                    if size > 1024 * 1024:  # > 1MB
                        size_str = f"{size / 1024 / 1024:.1f}MB"
                    elif size > 1024:  # > 1KB
                        size_str = f"{size / 1024:.0f}KB"
                    else:
                        size_str = f"{size}B"
                    entries.append(f"📄 {entry} ({size_str})")
                except:
                    entries.append(f"📄 {entry}")
        
        if not entries:
            return "(leer)"
        
        # Zähle Einträge
        file_count = sum(1 for e in entries if e.startswith("📄"))
        dir_count = sum(1 for e in entries if e.startswith("📁"))
        
        return f"📍 {path}\n({dir_count} dirs, {file_count} files):\n\n" + "\n".join(entries)
        
    except PermissionError:
        return f"❌ Berechtigung verweigert: {path}"
    except Exception as e:
        return f"❌ Fehler: {e}"
