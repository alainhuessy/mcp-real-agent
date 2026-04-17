# 🧠 Agent OS v2.1

> Lokales AI Operating System — kein Cloud-API nötig.

## Architektur

```
                ┌─────────────────────────────┐
                │      API Kernel (FastAPI)   │
                └────────────┬────────────────┘
                             │
                ┌────────────▼──────────────┐
                │   Scheduler / Task Loop   │
                └────────────┬──────────────┘
                             │
     ┌───────────────────────┼────────────────────────┐
     │                       │                        │
┌────▼─────┐       ┌────────▼────────┐      ┌────────▼────────┐
│ Planner  │       │ Worker Agent    │      │ Reviewer Agent  │
└──────────┘       └────────┬────────┘      └────────┬────────┘
                             │                        │
                ┌────────────▼──────────────┐         │
                │ Tool Registry (Plugins)    │─────────┘
                └────────────┬──────────────┘
                             │
        ┌────────────────────▼────────────────────┐
        │ Ollama + Continue + Memory (ChromaDB)   │
        └──────────────────────────────────────────┘
```

## Tech Stack

| Komponente | Technologie |
|-----------|-------------|
| LLM Inference | Ollama (lokal) |
| Vector Memory | ChromaDB |
| API | FastAPI |
| CLI | Rich |
| IDE Integration | Continue (VS Code) |

## Installation

```bash
pip install -r requirements.txt
```

## Voraussetzungen

- Python 3.11+
- Ollama läuft auf `http://localhost:11434`
- Modelle installiert: `ollama pull llama3.1:8b` / `ollama pull qwen2.5-coder:14b`

## Starten

### CLI Modus
```bash
python run.py
```

### API Server
```bash
python run.py
# dann: api
```

Oder direkt:
```bash
uvicorn api.kernel:app --reload
```

## CLI Befehle

| Befehl | Beschreibung |
|--------|-------------|
| `shell:<cmd>` | Shell-Befehl ausführen |
| `plan:<goal>` | Ziel in Subtasks zerlegen |
| `status` | System-Status |
| `tasks` | Task Queue anzeigen |
| `loop` | Autonomen Task Loop starten |
| `api` | API Server starten |
| `quit` | Beenden |

## API Endpoints

| Method | Endpoint | Beschreibung |
|--------|----------|-------------|
| GET | `/` | Systeminfo |
| POST | `/task` | Task ausführen |
| POST | `/task/queue` | Task einreihen |
| GET | `/tasks` | Alle Tasks |
| GET | `/status` | Systemstatus |
| POST | `/shell` | Shell-Befehl |
| GET | `/memory/search?q=...` | Memory suchen |

## Projektstruktur

```
├── core/           # Kernel (Agent, Router, LLM)
├── agents/         # Multi-Agent (Planner, Worker, Reviewer)
├── memory/         # ChromaDB Vector Memory
├── tasks/          # Task Queue + Scheduler
├── tools/          # Plugin Tool Registry
├── api/            # FastAPI REST API
├── mcp_server.py   # MCP Server (Continue Integration)
├── .continuerc.json # Continue MCP Config
├── run.py          # CLI Entry Point
└── requirements.txt
```

## MCP Server (Continue Integration)

Der Agent OS ist als **MCP Server** verfügbar — Continue (VS Code) greift damit auf alle Tools, Memory und LLM zu.

### Einrichtung

Siehe `docs/MCP_SETUP.md` für die vollständige Anleitung.

### Kurzversion

1. `pip install -r requirements.txt`
2. `.continuerc.json` liegt bereits im Projekt
3. VS Code öffnen → Continue erkennt MCP Server automatisch
4. Im Chat: Tools wie `agent_run_task`, `memory_search`, `file_write` etc. nutzen
