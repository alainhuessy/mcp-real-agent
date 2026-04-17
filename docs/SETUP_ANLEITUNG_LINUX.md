# 🧠 Agent OS v2.1 — Komplette Einrichtungsanleitung (Linux)

> Schritt-für-Schritt-Anleitung für Einsteiger.
> Kein tiefes Informatikwissen nötig — einfach der Reihe nach durcharbeiten.

---

## 📋 Was du am Ende hast

- **Ollama** → lokale KI-Modelle auf deinem Rechner
- **VS Code** → Code-Editor
- **Continue** → KI-Assistent in VS Code
- **Agent OS** → dein eigenes KI-Betriebssystem (Python)

---

## 🖥️ Voraussetzungen

- Ein Linux-Rechner (Ubuntu 22.04+ empfohlen)
- Mindestens 16 GB RAM (besser 32 GB für grössere Modelle)
- Mindestens 20 GB freier Speicherplatz
- Internetverbindung (für Installation)

---

# TEIL 1: Grundsystem installieren

---

## Schritt 1 — Terminal öffnen

Drücke `Ctrl + Alt + T` um ein Terminal zu öffnen.
Alle folgenden Befehle werden dort eingegeben.

---

## Schritt 2 — System aktualisieren

```bash
sudo apt update && sudo apt upgrade -y
```

> **Was passiert?** Dein System wird auf den neuesten Stand gebracht.

---

## Schritt 3 — Python installieren

```bash
sudo apt install python3 python3-pip python3-venv git curl -y
```

Prüfe ob es geklappt hat:

```bash
python3 --version
```

> Sollte `Python 3.11` oder höher anzeigen.

---

## Schritt 4 — Git konfigurieren

```bash
git config --global user.name "Dein Name"
git config --global user.email "deine@email.ch"
```

> Ersetze Name und E-Mail mit deinen eigenen Daten.

---

# TEIL 2: Ollama installieren

---

## Schritt 5 — Ollama installieren

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

> **Was passiert?** Ollama wird heruntergeladen und installiert.
> Ollama ist das Programm, das KI-Modelle lokal auf deinem Rechner ausführt.

---

## Schritt 6 — Prüfen ob Ollama läuft

```bash
ollama --version
```

Starte den Ollama-Server (falls er nicht automatisch läuft):

```bash
ollama serve
```

> **Tipp:** Lass dieses Terminal offen. Öffne ein neues Terminal für die nächsten Schritte (`Ctrl + Alt + T`).

---

## Schritt 7 — KI-Modelle herunterladen

```bash
ollama pull llama3.1:8b
ollama pull qwen2.5-coder:14b
```

> **Was passiert?** Zwei KI-Modelle werden heruntergeladen:
> - `llama3.1:8b` → Allgemeines Modell (Chat, Planung)
> - `qwen2.5-coder:14b` → Spezialisiert auf Programmierung
>
> ⏱ Das dauert je nach Internetverbindung 5–30 Minuten.

---

## Schritt 8 — Ollama testen

```bash
ollama run llama3.1:8b "Hallo, funktionierst du?"
```

> Wenn du eine Antwort bekommst → ✅ Ollama funktioniert!

Teste auch die API:

```bash
curl http://localhost:11434/api/tags
```

> Sollte eine Liste deiner installierten Modelle zeigen.

---

# TEIL 3: VS Code installieren

---

## Schritt 9 — VS Code installieren

### Option A: Über Snap (einfachste Methode)

```bash
sudo snap install code --classic
```

### Option B: Über das .deb-Paket

```bash
curl -L "https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64" -o vscode.deb
sudo dpkg -i vscode.deb
sudo apt install -f -y
rm vscode.deb
```

---

## Schritt 10 — VS Code starten

```bash
code
```

> VS Code öffnet sich. Beim ersten Start:
> - Sprache auf Deutsch stellen (wird vorgeschlagen)
> - Theme auswählen (egal welches)

---

## Schritt 11 — Python Extension installieren

1. In VS Code: Klicke links auf das **Extensions-Symbol** (vier Quadrate)
2. Suche nach **"Python"**
3. Installiere die Extension von **Microsoft**
4. Starte VS Code neu falls nötig

---

# TEIL 4: Continue installieren (KI-Assistent für VS Code)

---

## Schritt 12 — Continue Extension installieren

1. In VS Code: **Extensions** öffnen (Ctrl + Shift + X)
2. Suche nach **"Continue"**
3. Installiere **"Continue - Codestral, Claude, and more"**
4. Starte VS Code neu

---

## Schritt 13 — Continue konfigurieren

Nach dem Neustart erscheint Continue in der Seitenleiste.

1. Klicke auf das **Continue-Symbol** (links in der Seitenleiste)
2. Wähle **"Local Models"** oder **"Ollama"** als Provider
3. Konfiguriere die Modelle:

Continue erstellt eine Datei `~/.continue/config.json`. Öffne sie:

```bash
code ~/.continue/config.json
```

Ersetze den Inhalt mit:

```json
{
  "models": [
    {
      "title": "Llama 3.1 (Chat)",
      "provider": "ollama",
      "model": "llama3.1:8b",
      "apiBase": "http://localhost:11434"
    },
    {
      "title": "Qwen Coder (Code)",
      "provider": "ollama",
      "model": "qwen2.5-coder:14b",
      "apiBase": "http://localhost:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Qwen Coder",
    "provider": "ollama",
    "model": "qwen2.5-coder:14b",
    "apiBase": "http://localhost:11434"
  }
}
```

Speichere mit `Ctrl + S`.

---

## Schritt 14 — Continue testen

1. Öffne das Continue-Panel in VS Code (Seitenleiste)
2. Tippe eine Frage: **"Hallo, funktionierst du?"**
3. Wenn du eine Antwort bekommst → ✅ Continue funktioniert!

> **Tipp:** Mit `Ctrl + L` kannst du Continue jederzeit öffnen.
> Mit `Ctrl + I` kannst du inline im Code Fragen stellen.

---

# TEIL 5: Agent OS Projekt einrichten

---

## Schritt 15 — Projektordner erstellen

```bash
mkdir -p ~/Projekte/agent-os-v2
cd ~/Projekte/agent-os-v2
```

---

## Schritt 16 — Git Repository initialisieren

```bash
git init
```

---

## Schritt 17 — Projekt von GitHub klonen (Alternative)

Falls das Projekt bereits auf GitHub liegt:

```bash
git clone https://github.com/DEIN-USERNAME/agent-os-v2.git
cd agent-os-v2
```

> Ersetze `DEIN-USERNAME` mit deinem GitHub-Benutzernamen.

---

## Schritt 18 — Python Virtual Environment erstellen

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> **Was passiert?** Eine isolierte Python-Umgebung wird erstellt.
> Der Prompt im Terminal zeigt jetzt `(.venv)` am Anfang.
>
> ⚠️ **Wichtig:** Diesen Befehl musst du jedes Mal ausführen, wenn du ein neues Terminal öffnest:
> ```bash
> source .venv/bin/activate
> ```

---

## Schritt 19 — Dependencies installieren

```bash
pip install -r requirements.txt
```

> Installiert alle benötigten Python-Pakete:
> - `requests` — HTTP-Verbindung zu Ollama
> - `chromadb` — Vector-Datenbank (Gedächtnis)
> - `rich` — Hübsche Terminal-Ausgabe
> - `fastapi` — REST API
> - `uvicorn` — Webserver

---

## Schritt 20 — Projekt in VS Code öffnen

```bash
code .
```

> VS Code öffnet sich mit dem Projektordner.

---

## Schritt 21 — Python Interpreter auswählen

1. In VS Code: Drücke `Ctrl + Shift + P`
2. Tippe: **"Python: Select Interpreter"**
3. Wähle den Interpreter aus `.venv` (z.B. `./venv/bin/python3`)

---

# TEIL 6: Agent OS bedienen

---

## Schritt 22 — Prüfen ob Ollama läuft

Bevor du startest, stelle sicher dass Ollama läuft:

```bash
curl http://localhost:11434/api/tags
```

Falls nicht → in einem separaten Terminal:

```bash
ollama serve
```

---

## Schritt 23 — Agent OS starten (CLI Modus)

```bash
python3 run.py
```

> Du siehst ein grünes Panel mit den verfügbaren Befehlen.

---

## Schritt 24 — Befehle ausprobieren

### Einfache Frage stellen

```
Task > Erkläre mir was ein Python Dictionary ist
```

### Shell-Befehl ausführen

```
Task > shell:ls -la
```

### Ein Ziel in Subtasks zerlegen lassen

```
Task > plan:Erstelle eine REST API für eine Todo-App
```

> Der Planner Agent zerlegt das Ziel automatisch in Einzelschritte.

### Task Queue anzeigen

```
Task > tasks
```

### Autonomen Modus starten

```
Task > loop
```

> Der Agent arbeitet jetzt alle offenen Tasks selbständig ab.
> Stoppe mit `Ctrl + C`.

### Beenden

```
Task > quit
```

---

## Schritt 25 — API Server starten

### Option A: Über das CLI

```
Task > api
```

### Option B: Direkt aus dem Terminal

```bash
uvicorn api.kernel:app --reload --host 0.0.0.0 --port 8000
```

Dann im Browser öffnen:

- **API Docs:** http://localhost:8000/docs
- **Status:** http://localhost:8000/status

### API testen (neues Terminal)

```bash
# Task ausführen
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task": "Schreibe eine Python Funktion die Fibonacci berechnet"}'

# Status abfragen
curl http://localhost:8000/status

# Memory durchsuchen
curl "http://localhost:8000/memory/search?q=fibonacci"
```

---

# TEIL 7: Täglicher Gebrauch (Kurzanleitung)

---

## Jeden Tag wenn du arbeitest:

### 1. Terminal öffnen und Ollama starten

```bash
ollama serve
```

### 2. Neues Terminal → Projekt öffnen

```bash
cd ~/Projekte/agent-os-v2
source .venv/bin/activate
code .
```

### 3. Agent starten

```bash
python3 run.py
```

### Fertig! 🎉

---

# TEIL 8: Fehlerbehebung

---

## ❌ "Ollama nicht erreichbar"

```bash
# Prüfe ob Ollama läuft
systemctl status ollama

# Oder starte manuell
ollama serve
```

---

## ❌ "Modell nicht gefunden"

```bash
# Zeige installierte Modelle
ollama list

# Modell nochmal herunterladen
ollama pull llama3.1:8b
```

---

## ❌ "ModuleNotFoundError" in Python

```bash
# Stelle sicher dass venv aktiv ist
source .venv/bin/activate

# Dependencies neu installieren
pip install -r requirements.txt
```

---

## ❌ "Continue verbindet nicht"

1. Prüfe ob Ollama läuft: `curl http://localhost:11434/api/tags`
2. Prüfe die Continue Config: `~/.continue/config.json`
3. Starte VS Code neu

---

## ❌ Port 8000 bereits belegt

```bash
# Finde den Prozess
lsof -i :8000

# Anderen Port verwenden
uvicorn api.kernel:app --port 8001
```

---

# TEIL 9: Nützliche Befehle (Spickzettel)

| Was | Befehl |
|---|---|
| Ollama starten | `ollama serve` |
| Modell testen | `ollama run llama3.1:8b "Hallo"` |
| Modelle auflisten | `ollama list` |
| venv aktivieren | `source .venv/bin/activate` |
| Agent starten | `python3 run.py` |
| API starten | `uvicorn api.kernel:app --reload` |
| API Docs | http://localhost:8000/docs |
| Git Status | `git status` |
| Git Commit | `git add . && git commit -m "Nachricht"` |

---

> 📅 Erstellt: 17. April 2026
> 🧠 System: Agent OS v2.1
