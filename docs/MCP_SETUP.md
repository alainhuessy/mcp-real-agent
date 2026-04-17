# 🧠 Agent OS v2.1 — MCP Server Einrichtung

> Schritt-für-Schritt-Anleitung: Agent OS als MCP Server in VS Code mit Continue + Ollama.
> Kein tiefes Informatikwissen nötig.

---

## 📋 Was du am Ende hast

Wenn du fertig bist, kannst du im **Continue Chat in VS Code** direkt auf dein gesamtes Agent OS zugreifen:

```
Continue Chat > "Erstelle eine Python Funktion für Fibonacci"
                    ↓
               MCP Server (Agent OS)
                    ↓
            Router → Worker → Reviewer → Memory
                    ↓
               Antwort im Chat
```

**Verfügbare Fähigkeiten im Chat:**

| Tool | Was es kann |
|---|---|
| `agent_run_task` | Task durch volle Pipeline (Router → LLM → Review → Memory) |
| `agent_plan` | Ziel in Subtasks zerlegen |
| `memory_search` | Wissen durchsuchen (semantisch) |
| `memory_store` | Fakten/Entscheidungen speichern |
| `task_add` / `task_list` / `task_next` | Task Queue verwalten |
| `file_read` / `file_write` / `file_list` | Dateien lesen/schreiben |
| `shell_run` | Shell-Befehle (mit Sicherheits-Allowlist) |
| `git_status` / `git_commit` / `git_log` | Git-Operationen |
| `llm_ask` | Direkt ein Ollama-Modell befragen |
| `agent_status` | Systemstatus abfragen |

---

## 🖥️ Voraussetzungen

Bevor du startest, müssen folgende Dinge laufen:

- [ ] **Python 3.11+** installiert
- [ ] **Ollama** installiert und läuft (`ollama serve`)
- [ ] **Mindestens 1 Modell** heruntergeladen (`ollama pull llama3.1:8b`)
- [ ] **VS Code** installiert
- [ ] **Continue Extension** in VS Code installiert
- [ ] **Agent OS Projekt** vorhanden (dieser Workspace)

> Falls etwas fehlt → siehe `docs/SETUP_ANLEITUNG_LINUX.md`

---

# Schritt 1 — Dependencies installieren

Öffne ein Terminal im Projektordner und stelle sicher, dass dein venv aktiv ist:

### Linux / macOS

```bash
cd ~/Projekte/agent-os-v2
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
cd C:\Pfad\zum\Projekt
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> **Wichtig:** Das Paket `mcp` muss installiert sein. Prüfe mit:
> ```bash
> pip show mcp
> ```

---

# Schritt 2 — Prüfen ob Ollama läuft

```bash
curl http://localhost:11434/api/tags
```

Falls nicht:

```bash
ollama serve
```

> Lass Ollama in einem separaten Terminal laufen.

---

# Schritt 3 — MCP Server testen

Teste ob der Server startet:

### Linux / macOS

```bash
python mcp_server.py
```

### Windows

```powershell
python mcp_server.py
```

> Der Server startet und wartet auf stdin-Eingaben (du siehst keine Ausgabe — das ist normal!).
> Stoppe mit `Ctrl + C`.

Falls Fehler auftreten:

| Fehler | Lösung |
|---|---|
| `ModuleNotFoundError: mcp` | `pip install mcp` |
| `ModuleNotFoundError: chromadb` | `pip install -r requirements.txt` |
| `Ollama nicht erreichbar` | `ollama serve` in separatem Terminal |

---

# Schritt 4 — Continue für MCP konfigurieren

Es gibt zwei Möglichkeiten den MCP Server zu konfigurieren:

---

## Option A: Projekt-lokal (empfohlen) ⭐

Die Datei `.continuerc.json` im Projektordner ist bereits erstellt. Prüfe den Inhalt:

```json
{
  "mcpServers": [
    {
      "name": "agent-os",
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "."
    }
  ]
}
```

> **Was passiert?** Wenn du dieses Projekt in VS Code öffnest, erkennt Continue automatisch den MCP Server.

---

## Option B: Global (für alle Projekte)

Falls du den Agent OS MCP Server in **allen** Projekten nutzen willst, editiere die globale Continue Config:

### Linux / macOS

```bash
code ~/.continue/config.json
```

### Windows

```powershell
code "$env:USERPROFILE\.continue\config.json"
```

Füge den `mcpServers` Block hinzu:

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
  },
  "mcpServers": [
    {
      "name": "agent-os",
      "command": "python",
      "args": ["/ABSOLUTER/PFAD/ZU/mcp_server.py"],
      "cwd": "/ABSOLUTER/PFAD/ZUM/PROJEKT"
    }
  ]
}
```

> ⚠️ **Ersetze** `/ABSOLUTER/PFAD/...` mit deinem echten Pfad!
>
> Beispiel Linux: `/home/alain/Projekte/agent-os-v2/mcp_server.py`
> Beispiel Windows: `C:\\Users\\alain\\LLM\\vsc_ollama_continue_agent\\mcp_server.py`

---

# Schritt 5 — VS Code neu starten

1. Schliesse VS Code komplett
2. Öffne VS Code wieder
3. Öffne das Projekt

```bash
code /pfad/zum/projekt
```

---

# Schritt 6 — Prüfen ob MCP Server erkannt wird

1. Öffne das **Continue Panel** (Seitenleiste links oder `Ctrl + L`)
2. Öffne die Continue-Einstellungen (Zahnrad-Symbol)
3. Unter **"MCP Servers"** sollte `agent-os` erscheinen mit Status **"Connected"**

Falls der Server **nicht** erscheint:

- Prüfe ob `.continuerc.json` im Projektordner liegt
- Prüfe ob `python` im PATH ist (teste: `python --version`)
- Prüfe Continue-Logs: `Ctrl + Shift + P` → "Continue: View Logs"

---

# Schritt 7 — Im Chat nutzen

Jetzt kannst du den Agent OS im Continue Chat verwenden!

## Beispiele:

### Task durch die volle Pipeline schicken

```
Nutze das agent_run_task Tool um eine Python Funktion zu schreiben
die eine Liste von Zahlen sortiert und Duplikate entfernt.
```

### Ziel in Subtasks zerlegen

```
Nutze agent_plan um folgendes Ziel aufzuteilen:
Baue eine komplette REST API mit User-Authentifizierung.
```

### Memory durchsuchen

```
Nutze memory_search um nach "authentication" zu suchen.
Was wissen wir bereits über Authentifizierung?
```

### Wissen speichern

```
Nutze memory_store um folgenden Fakt zu speichern:
"Wir verwenden JWT Tokens für die Authentifizierung."
ID: "auth-decision-jwt"
```

### Datei erstellen

```
Nutze file_write um eine Datei src/utils/helpers.py zu erstellen
mit einer Funktion calculate_average(numbers: list) -> float.
```

### Git Status prüfen

```
Nutze git_status um zu sehen welche Dateien geändert wurden.
```

### Shell-Befehl ausführen

```
Nutze shell_run um "ls -la" auszuführen.
```

### Direkt ein Modell befragen

```
Nutze llm_ask mit dem Prompt "Erkläre Python Decorators in 3 Sätzen"
und dem Modell "llama3.1:8b".
```

---

# Schritt 8 — Täglicher Gebrauch

## Jeden Tag wenn du arbeitest:

### 1. Ollama starten (falls nicht als Service)

```bash
ollama serve
```

### 2. Projekt in VS Code öffnen

```bash
code /pfad/zum/projekt
```

### 3. Continue öffnen (`Ctrl + L`)

Der MCP Server startet automatisch! Du kannst sofort loslegen.

> **Tipp:** Der MCP Server wird von Continue automatisch gestartet und gestoppt.
> Du musst ihn **NICHT** manuell starten.

---

# Fehlerbehebung

## ❌ "MCP Server not connected"

1. Prüfe ob Python im PATH ist:
   ```bash
   python --version
   ```
2. Prüfe ob alle Dependencies installiert sind:
   ```bash
   pip install -r requirements.txt
   ```
3. Teste den Server manuell:
   ```bash
   python mcp_server.py
   ```
4. Starte VS Code neu

## ❌ "Tool call failed: Ollama not reachable"

```bash
# Prüfe ob Ollama läuft
curl http://localhost:11434/api/tags

# Falls nicht
ollama serve
```

## ❌ "ModuleNotFoundError: mcp"

```bash
pip install mcp
```

## ❌ Continue zeigt keine MCP Tools

1. Prüfe `.continuerc.json` im Projektordner
2. Oder die globale Config `~/.continue/config.json`
3. Starte VS Code komplett neu (nicht nur Fenster schliessen)
4. Prüfe Continue-Logs: `Ctrl + Shift + P` → "Continue: View Logs"

## ❌ "python" wird nicht gefunden (Windows)

Verwende den vollen Pfad in `.continuerc.json`:

```json
{
  "mcpServers": [
    {
      "name": "agent-os",
      "command": "C:\\Users\\DEIN_USER\\LLM\\vsc_ollama_continue_agent\\.venv\\Scripts\\python.exe",
      "args": ["mcp_server.py"],
      "cwd": "C:\\Users\\DEIN_USER\\LLM\\vsc_ollama_continue_agent"
    }
  ]
}
```

---

# Architektur-Übersicht

```
VS Code
  └── Continue Extension
        └── MCP Client
              │
              │ stdio (stdin/stdout)
              │
              ▼
        ┌─────────────────────────────┐
        │     mcp_server.py           │
        │     (MCP Protocol Layer)    │
        └──────────┬──────────────────┘
                   │
        ┌──────────▼──────────────────┐
        │     Agent OS Kernel         │
        │  ┌─────────────────────┐    │
        │  │ Router (auto model) │    │
        │  └──────────┬──────────┘    │
        │             │               │
        │  ┌──────────▼──────────┐    │
        │  │ Planner / Worker /  │    │
        │  │ Reviewer Agents     │    │
        │  └──────────┬──────────┘    │
        │             │               │
        │  ┌──────────▼──────────┐    │
        │  │ Tool Registry       │    │
        │  │ (Shell/File/Git)    │    │
        │  └──────────┬──────────┘    │
        │             │               │
        │  ┌──────────▼──────────┐    │
        │  │ Memory (ChromaDB)   │    │
        │  └─────────────────────┘    │
        └──────────────┬──────────────┘
                       │
              ┌────────▼────────┐
              │ Ollama (lokal)  │
              │ llama3.1 / qwen │
              └─────────────────┘
```

---

# Verfügbare MCP Tools (Referenz)

| Tool | Beschreibung | Pflicht-Parameter |
|---|---|---|
| `agent_run_task` | Volle Pipeline (Route → LLM → Review → Memory) | `task` |
| `agent_plan` | Ziel in Subtasks zerlegen | `goal` |
| `agent_status` | Systemstatus | — |
| `memory_search` | Semantische Suche im Memory | `query` |
| `memory_store` | Fakt/Entscheidung speichern | `text`, `id` |
| `task_add` | Task zur Queue hinzufügen | `task` |
| `task_list` | Alle Tasks anzeigen | — |
| `task_next` | Nächsten Task ausführen | — |
| `file_read` | Datei lesen | `path` |
| `file_write` | Datei schreiben | `path`, `content` |
| `file_list` | Verzeichnis auflisten | `path` (optional) |
| `shell_run` | Shell-Befehl (Allowlist) | `command` |
| `git_status` | Git Status | — |
| `git_commit` | Git Commit | `message` |
| `git_log` | Git History | `count` (optional) |
| `llm_ask` | Direkt LLM befragen | `prompt` |

---

> 📅 Erstellt: 17. April 2026
> 🧠 System: Agent OS v2.1 MCP Server
