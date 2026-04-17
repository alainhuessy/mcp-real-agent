# 🧠 Agent OS v2.1 — Einrichtungsprotokoll

> Erstellt am: 17. April 2026
> Zweck: Nachvollzug der Projekteinrichtung für LLM-Kontext

---

## 1. Projektziel

Aufbau eines **lokalen AI Operating Systems** (Agent OS v2.1) — ein Python-basierter Orchestrator, der:

- Lokale LLMs via **Ollama** nutzt (kein Cloud-API)
- Ein **Multi-Agent System** (Planner → Worker → Reviewer) betreibt
- Ein **Vector Memory** (ChromaDB) als Langzeitgedächtnis hat
- Über eine **REST API** (FastAPI) steuerbar ist
- Über ein **CLI** (Rich) bedienbar ist
- In **VS Code + Continue** als IDE-Layer integriert ist

---

## 2. Erstellte Projektstruktur

```
vsc_ollama_continue_agent/
├── .github/
│   └── copilot-instructions.md    # Copilot-Kontext für das Projekt
├── .gitignore
├── README.md                       # Projektdokumentation + Architektur
├── requirements.txt                # Python Dependencies
├── run.py                          # CLI Entry Point (Hauptprogramm)
│
├── core/                           # Kernel-Schicht
│   ├── __init__.py
│   ├── agent.py                    # AgentOS Klasse — Hauptorchestrator
│   ├── llm.py                      # Ollama API Connector
│   ├── router.py                   # Intelligente Modellwahl (coder/rag/planner/chat)
│   └── tools.py                    # Legacy Shell Tool
│
├── agents/                         # Multi-Agent System
│   ├── __init__.py
│   ├── planner.py                  # Zerlegt Ziele in Subtasks
│   ├── worker.py                   # Führt Tasks mit LLM + Tools aus
│   └── reviewer.py                 # Validiert Worker-Output (Quality Gate)
│
├── memory/                         # Gedächtnis-Schicht
│   ├── __init__.py
│   └── memory.py                   # ChromaDB Vector Memory (Facts/Tasks/Episodes)
│
├── tasks/                          # Task-Verwaltung
│   ├── __init__.py
│   ├── task_queue.py               # Task Queue mit Prioritäten
│   └── scheduler.py                # Background Daemon Scheduler
│
├── tools/                          # Plugin-Tools
│   ├── __init__.py
│   ├── registry.py                 # Plugin Tool Registry System
│   ├── shell.py                    # Geschütztes Shell Tool (Allowlist)
│   ├── file.py                     # Dateioperationen (lesen/schreiben)
│   └── git.py                      # Git Automation (commit/status/log)
│
└── api/                            # REST API
    ├── __init__.py
    └── kernel.py                   # FastAPI Server (Endpoints)
```

---

## 3. Architektur-Entscheidungen

| Entscheidung | Begründung |
|---|---|
| **Ollama** statt OpenAI API | Vollständig lokal, kein API-Key nötig |
| **ChromaDB** statt SQLite für Memory | Semantische Suche über Embeddings |
| **FastAPI** als API | Async-fähig, auto-generierte Docs |
| **Rich** für CLI | Farbige, strukturierte Terminal-Ausgabe |
| **Tool Registry** statt hardcodierte Tools | Erweiterbar wie Plugins |
| **Multi-Agent** (Planner/Worker/Reviewer) | Trennung von Planung, Ausführung, Qualität |
| **Shell Allowlist** | Sicherheit — nur erlaubte Befehle |
| **Git mit Bestätigung** | Keine unkontrollierten Commits |

---

## 4. Model Routing

| Modus | Modell | Trigger-Keywords |
|---|---|---|
| `coder` | `qwen2.5-coder:14b` | code, bug, refactor, api, function |
| `rag` | `llama3.1:8b` | docs, research, pdf, knowledge |
| `planner` | `llama3.1:8b` | plan, architecture, build, project |
| `chat` | `llama3.1:8b` | alles andere |

---

## 5. Agent Pipeline (Ablauf)

```
User Input
    ↓
Router → Modus bestimmen (coder/rag/planner/chat)
    ↓
Planner Agent → Ziel in Subtasks zerlegen (falls planner)
    ↓
Worker Agent → Task ausführen (LLM + Tools)
    ↓
Reviewer Agent → Output prüfen (approved / needs_fix)
    ↓
Memory Update → Ergebnis in ChromaDB speichern
```

---

## 6. API Endpoints

| Method | Endpoint | Beschreibung |
|---|---|---|
| `GET` | `/` | Systeminfo |
| `POST` | `/task` | Task sofort ausführen |
| `POST` | `/task/queue` | Task einreihen |
| `GET` | `/tasks` | Alle Tasks anzeigen |
| `GET` | `/status` | Systemstatus |
| `POST` | `/shell` | Shell-Befehl |
| `GET` | `/memory/search?q=...` | Memory durchsuchen |

---

## 7. CLI Befehle

| Befehl | Beschreibung |
|---|---|
| `shell:<cmd>` | Shell-Befehl ausführen |
| `plan:<goal>` | Ziel in Subtasks zerlegen |
| `status` | System-Status anzeigen |
| `tasks` | Task Queue anzeigen |
| `loop` | Autonomen Task Loop starten |
| `api` | API Server starten (Port 8000) |
| `quit` | Beenden |

---

## 8. Dependencies

```
requests>=2.31.0      # HTTP Client für Ollama API
chromadb>=0.4.0       # Vector Database (Memory)
rich>=13.0.0          # Terminal UI
fastapi>=0.110.0      # REST API Framework
uvicorn>=0.29.0       # ASGI Server für FastAPI
```

---

## 9. MCP Server Integration (NEU)

Das Agent OS ist als **MCP Server** (Model Context Protocol) bereitgestellt.

### Was wurde erstellt:

| Datei | Zweck |
|---|---|
| `mcp_server.py` | MCP Protocol Handler (stdio Transport) |
| `.continuerc.json` | Continue MCP Server Konfiguration |
| `docs/MCP_SETUP.md` | Vollständige Einrichtungsanleitung |

### Exponierte MCP Tools (16 Tools):

| Kategorie | Tools |
|---|---|
| Agent Pipeline | `agent_run_task`, `agent_plan`, `agent_status` |
| Memory | `memory_search`, `memory_store` |
| Task Queue | `task_add`, `task_list`, `task_next` |
| Dateien | `file_read`, `file_write`, `file_list` |
| Shell | `shell_run` |
| Git | `git_status`, `git_commit`, `git_log` |
| LLM | `llm_ask` |

### Architektur-Entscheidung:

- **stdio Transport** (Standard für MCP, nicht HTTP)
- Continue startet/stoppt den Server automatisch
- Alle bestehenden Agent OS Komponenten werden durchgereicht

---

## 10. Offene nächste Schritte (v3 Roadmap)

- [ ] Event-driven Kernel (async)
- [ ] Parallel Agents (async execution)
- [ ] UI Dashboard (Live Task Monitor)
- [ ] MCP Tool Standard
- [ ] Self-healing Tasks (retry + repair loops)
- [ ] Open WebUI RAG Sync
- [ ] Project Memory Isolation
