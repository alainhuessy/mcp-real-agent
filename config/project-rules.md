# Agent OS v2.1 — Project-Specific Rules & Prompts

## 🎯 Deine Projekt-Regeln hier definieren

> Diese Datei ist ein Template. Kopiere sie nach `config/project-rules.md`
> und passe sie an deine Anforderungen an.

---

## 📋 System-Wide Rules

### Code Generation
- [ ] Verwende Python 3.11+ Features
- [ ] Type Hints sind erforderlich
- [ ] Docstrings für alle Funktionen
- [ ] Max Line Length: 100 Characters
- [ ] PEP 8 Style Guide

### Documentation
- [ ] README für neue Module
- [ ] Inline Comments für komplexe Logik
- [ ] Type Hints in Docstrings (reST Format)

### Git Workflow
- [ ] Commits müssen mit `feat:`, `fix:`, `docs:` beginnen
- [ ] Keine direkten Commits auf `main`
- [ ] Code Review vor Merge
- [ ] Tests müssen passen

### Security
- [ ] Keine Secrets in Code (nutze .env)
- [ ] Shell Commands immer mit Allowlist prüfen
- [ ] Input Validation für alle User-Inputs

---

## 🤖 Agent OS Specific Rules

### Worker Agent (Code Generation)
```
Bei Code-Generierung:
1. Nutze immer die neueste Best Practice
2. Erwäge Edge Cases
3. Schreibe Tests
4. Dokumentiere Entscheidungen
```

### Reviewer Agent (Code Review)
```
Bei Code-Review:
1. Syntax-Check: Funktioniert es?
2. Logic-Check: Ist es richtig?
3. Quality-Check: Ist es wartbar?
4. Security-Check: Ist es sicher?
```

### Planner Agent (Task Planning)
```
Bei Projekt-Planung:
1. Zerlege in max. 7 Subtasks
2. Jeder Task sollte < 30 min dauern
3. Dependencies auflisten
4. Priorities setzen (1-10)
```

---

## 🧠 Memory Context Rules

### Was speichern?
- [ ] Architektur-Entscheidungen
- [ ] API-Design Patterns
- [ ] Database Schemas
- [ ] Security Policies
- [ ] Known Bugs & Workarounds

### Speicher-Format:
```
Memory Entry:
- **Title**: Kurz und prägnant
- **Date**: YYYY-MM-DD
- **Category**: architecture | api | database | security | ...
- **Details**: Die eigentliche Information
- **Related Tags**: Für Suche
```

---

## 📝 Custom System Prompts

### Für Worker Agent (Code Tasks)

```
Du bist ein Code-Writing Agent für ein Python Agent OS Project.

Deine Aufgaben:
- Schreibe Production-Ready Python Code
- Nutze Type Hints
- Folge PEP 8
- Dokumentiere mit Docstrings (Google Style)

Konventionen:
- Private Methods mit _ Präfix
- Constants mit CAPS_LOCK
- Classes mit CamelCase
- Functions mit snake_case

Frameworks & Libraries:
- FastAPI für APIs
- ChromaDB für Memory
- MCP für Tool-Protokoll
- Ollama für LLM-Zugriff

WICHTIG: Schreibe immer testbar Code!
```

### Für Reviewer Agent (Validation Tasks)

```
Du bist ein Code-Quality Reviewer.

Check-Liste:
1. SYNTAX: Ist der Code syntaktisch korrekt?
2. LOGIC: Erfüllt er die Anforderungen?
3. STYLE: Folgt er den Konventionen?
4. PERFORMANCE: Ist er effizient?
5. SECURITY: Gibt es Sicherheitslücken?
6. TESTABILITY: Kann man es testen?

Bewertung:
- GREEN (APPROVED): Alles ok
- YELLOW (REVIEW): Kleine Issues
- RED (NEEDS_FIX): Größere Issues

Format: "APPROVED" oder "NEEDS_FIX: [reason]"
```

### Für Planner Agent (Planning Tasks)

```
Du bist ein Project-Planning Agent.

Bei Projekt-Zerlegung:
1. Identifiziere Dependencies
2. Nutze Topological Sorting
3. Setze realistische Estimates
4. Markiere Critical Path
5. Definiere Checkpoints

Output-Format:
1. [priority] Task Title (estimate: Xh)
   Dependencies: task_id1, task_id2
   
2. [priority] Task Title (estimate: Yh)
   Dependencies: task_id1

Priorities: 1 (low) - 10 (critical)
```

---

## 🔗 Continue Integration Rules

### Wann Agent Tools nutzen?

| Anfrage | Tool | Grund |
|---|---|---|
| "Write a function" | `agent_run_task` | Code-Generator in Pipeline |
| "Check my code" | `agent_run_task` | Code-Quality überprüfung |
| "Create a file" | `file_write` | Direkt speichern |
| "Plan this" | `agent_plan` | Zerlege in Subtasks |
| "Save this idea" | `memory_store` | Speicher als Fakt |
| "Find related code" | `memory_search` | Kontext suchen |
| "Run tests" | `shell_run` | Pytest ausführen |
| "Commit changes" | `git_commit` | Version speichern |

### Continue Chat Patterns

```
Pattern 1: Code Generation
User: "Schreibe eine Funktion für X"
Continue: agent_run_task → Worker Agent → file_write → git_commit

Pattern 2: Analysis
User: "Analysiere diesen Code"
Continue: memory_search (Context) + agent_run_task (Analysis)

Pattern 3: Planning
User: "Plan ein Projekt für X"
Continue: agent_plan → Subtasks → task_add

Pattern 4: Problem Solving
User: "Warum funktioniert Y nicht?"
Continue: file_read (Code) + agent_run_task (Analysis) + memory_search (Known Issues)
```

---

## 🔒 Constraints & Limits

### Tool Limits
```
shell_run:
- Timeout: 30 seconds
- Max Output: 10KB
- Allowed Commands: [siehe tools/shell.py]

file_write:
- Max File Size: 1MB
- Create Dirs Automatically: Yes
- Overwrite Allowed: Yes

memory_search:
- Max Results: 5
- Search Index: facts + tasks + episodes
- Max Context: 2000 tokens

task_queue:
- Max Queue Size: 1000 tasks
- Max Task Duration: None (but monitor)
```

### LLM Limits
```
Ollama:
- Model qwen2.5-coder: 14B (8-10GB RAM)
- Model llama3.1: 8B (4-6GB RAM)
- Context Window: 4096 tokens
- Timeout: 120 seconds
```

---

## 📊 Performance Expectations

```
Tool Call Times (approximate):
- agent_run_task: 5-30 seconds (depends on complexity)
- memory_search: < 500ms
- file_write: < 100ms
- shell_run: < 2 seconds (typical)
- git_commit: 1-3 seconds

Memory Usage:
- MCP Server Startup: ~200MB
- Per Tool Call: +10-50MB
- ChromaDB Index: ~100MB+ (grows with data)
```

---

## 🧪 Testing Rules

### Test Coverage
- [ ] Unit Tests für alle Funktionen
- [ ] Integration Tests für Workflows
- [ ] E2E Tests für Critical Paths

### Test Format
```python
# pytest style
def test_agent_run_task_creates_file():
    """Agent sollte Datei erstellen können."""
    result = agent.run_task("Create a test file")
    assert "✅" in result
    assert Path("test_file.py").exists()
```

---

## 🚀 Deployment Checklist

- [ ] Alle Tests passen
- [ ] Alle Tools erreichbar
- [ ] Ollama läuft
- [ ] Memory initialisiert
- [ ] MCP Server startet
- [ ] Continue erkennt MCP Server
- [ ] 3 Sample Calls getestet

---

> 📅 Zuletzt aktualisiert: 17. April 2026
> 🔧 Nutze diese Datei um dein Agent OS zu konfigurieren
