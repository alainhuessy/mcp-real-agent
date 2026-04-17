# 🔧 ANALYSE: Warum agent_plan immer generische Pläne erstellt

## ❌ DAS PROBLEM

Wenn du `plan: Überprüfe Agent OS Projekt-Status` eingibst:

```
Continue Chat
    ↓
MCP Server ruft agent_plan auf
    ↓
PlannerAgent.plan(goal="Überprüfe Agent OS Projekt-Status")
    ↓
LLM bekommt NUR:
    - Das Goal
    - Optional: Memory Context (generische Facts)
    ↓
LLM hat KEINE Infos über:
    ✗ Projekt-Struktur
    ✗ Welche Dateien existieren
    ✗ Source Code
    ✗ Git Status
    ✗ Aktuelle Fehler
    ✗ Task Queue
    ✗ Konfiguration
    ↓
LLM macht generischen Plan basierend auf Template
```

---

## 📊 AKTUELLER FLOW (simplistic)

```python
# mcp_server.py - agent_plan Tool Handler

async def handle_agent_plan(goal: str):
    # 1. Memory-Context einige Worte
    mem_ctx = memory.search(goal, n_results=3)  # ← Nur 3 alte Memories!
    
    # 2. Plan erstellen
    subtasks = planner.plan(goal, mem_ctx)      # ← Goal + vage Memory
    
    # 3. Zurück
    return subtasks
```

**Das ist das ganze System!** Keine Workspace-Analyse, kein Code-Lesen.

---

## ✅ WAS SEIN SOLLTE (Ideal)

Wenn du `plan: Überprüfe Agent OS Projekt-Status` eingibst:

```
Continue Chat
    ↓
MCP Server ruft agent_plan auf
    ↓
🔍 WORKSPACE INTELLIGENCE (NEU!)
   ├─ Liest requirements.txt
   ├─ Zählt Python Files
   ├─ Analysiert Module
   ├─ Findet Entry Points
   ├─ Checkt Git Status
   └─ Liest .venv/pyvenv.cfg
    ↓
📊 PROBLEM DETECTION (NEU!)
   ├─ Führt Flake8 aus
   ├─ Checkt Security (Bandit)
   ├─ Type Checking (Mypy)
   └─ Identifiziert Probleme
    ↓
📚 KNOWLEDGE RETRIEVAL
   ├─ Memory durchsuchen
   ├─ Docs lesen (Markdown)
   ├─ Code-Snippet zusammenfassen
    ↓
🧠 LLM bekommt:
   ✅ Projekt-Struktur
   ✅ 640 LOC core
   ✅ 21 Python Files
   ✅ 6 Module: core, agents, tools, api, memory, tasks
   ✅ Modelle: phi4, qwen, gpt-oss
   ✅ Status: "70% Complete, Learning System TODO"
   ✅ Git: Latest commit, Branch, Changes
   ✅ Errors: None (Code is clean)
    ↓
LLM erstellt INTELLIGENTEN Plan:
   ✅ 1. Review AUDIT_SUMMARY.md für Status
   ✅ 2. Prüfe MCP-Server funktioniert
   ✅ 3. Validiere alle 3 Ollama Modelle
   ✅ 4. Teste Memory (ChromaDB)
   ✅ 5. Prüfe Task Queue
   ✅ 6. Identifiziere fehlende 30% (Learning System)
   ✅ 7. Erstelle Prioritäts-Roadmap
```

---

## 🎯 KONKRETE IMPLEMENTIERUNG

### Das fehlende Tool: `tools/workspace.py`

```python
class WorkspaceIntelligence:
    def analyze_project(self) -> dict:
        """Sammelt ALLE Project-Informationen."""
        return {
            "structure": self._analyze_structure(),
            "files": self._count_files(),
            "modules": self._analyze_modules(),
            "git": self._get_git_status(),
            "dependencies": self._read_requirements(),
            "health": self._check_health(),
            "entry_points": self._find_entry_points(),
        }
    
    def _analyze_structure(self) -> dict:
        # Find all .py files
        # Count lines per module
        # Identify main components
        
    def _get_git_status(self) -> dict:
        # git status, git log, branches
        
    def _check_health(self) -> dict:
        # Flake8, Bandit, Mypy
        # Return issues
```

### Integration in MCP Server

```python
# mcp_server.py - IMPROVED agent_plan

async def handle_agent_plan_improved(goal: str):
    # 1. Workspace-Kontext sammeln
    workspace = WorkspaceIntelligence()
    project_context = workspace.analyze_project()  # ← NEU!
    
    # 2. Memory-Context
    mem_ctx = memory.search(goal, n_results=5)
    
    # 3. System-Prompt mit Project Knowledge
    system_prompt = f"""
    You are a planner for this specific project:
    - Structure: {project_context['structure']}
    - Health: {project_context['health']}
    - Status: {project_context.get('status', 'Unknown')}
    - Entry Points: {project_context['entry_points']}
    
    Create a SPECIFIC plan for this project, not generic.
    """
    
    # 4. Plan mit context
    subtasks = planner.plan(goal, [system_prompt] + mem_ctx)
    
    return subtasks
```

---

## 📋 BEISPIELE: Vorher vs. Nachher

### VORHER (Generisch - Was du jetzt bekommst)

Input: `plan: Überprüfe das Projekt`

Output:
```
1. Start by accessing your current project file on your computer.
2. Review the project's Gantt chart or timeline to get an overview of its progress.
3. Check if all required tasks and milestones are documented in the project management tool.
4. Identify any critical dependencies that might be holding up progress.
5. Download and install MCP-Agent software according to the user manual instructions.
6. Launch MCP-Agent and connect it with your project file.
7. Run a report or analysis using MCP-Agent to evaluate project status and provide recommendations for improvement.
```

**Problem:** Spricht von "Gantt chart", "project management tool", "download software" — hat keine Ahnung!

---

### NACHHER (Spezifisch - Mit Workspace Intelligence)

Input: `plan: Überprüfe das Projekt`

Output:
```
1. Verify MCP Server is running: python3 mcp_server.py (http://localhost:11434)
2. Check all 3 Ollama models are loaded (phi4, qwen2.5-coder, gpt-oss)
3. Review AUDIT_SUMMARY.md for 70% complete status
4. Validate ChromaDB Memory connectivity
5. Run full test: test_agent_pipeline() in tests/
6. Check Task Queue in memory/ - should be empty after completion
7. Identify missing 30%: Learning System (Checkpoints, Feedback, Patterns)
8. Create Sprint Plan for next features (2-3 hour estimate)
```

**Besser:** Kennt die echte Struktur, Modelle, Konfiguration, Fehlende Features!

---

## 🔄 WAS DER AGENT AKTUELL TUT

### Schritt 1: MCP Server läuft
```bash
.venv/bin/python mcp_server.py
# Registriert alle Tools
# Wartet auf Continue-Anfragen
```

### Schritt 2: Continue ruft Tool auf
```
Continue User Chat:
"plan: Erstelle einen System-Health-Check"
    ↓
Continue sendet an MCP Server:
{
  "method": "tools/call",
  "params": {
    "name": "agent_plan",
    "arguments": {"goal": "erstelle einen system-health-check"}
  }
}
```

### Schritt 3: MCP Server verarbeitet
```python
# mcp_server.py
if tool_name == "agent_plan":
    goal = args["goal"]
    
    # Memory suchen
    mem_ctx = memory.search(goal)
    
    # Plan erstellen
    plan = planner.plan(goal, mem_ctx)
    
    # Zurückgeben
    return {"status": "ok", "plan": plan}
```

### Schritt 4: LLM macht generischen Plan
```python
# agents/planner.py
def plan(self, goal, context):
    prompt = f"GOAL:\n{goal}\n\nCONTEXT:\n{context}\nCreate numbered task list."
    
    result = self.llm.ask("gpt-oss", prompt)  # ← LLM hat keine Project Knowledge!
    
    # Rückgabe: Generic template
    return parse_tasks(result)
```

### Schritt 5: Continue zeigt Plan
```
Result:
1. Start by accessing your current project...
2. Review the project's Gantt chart...
```

---

## 💌 ZUSAMMENFASSUNG: Warum generisch?

| Punkt | Jetzt | Sollte sein |
|-------|-------|------------|
| **Input zu LLM** | Nur das Goal + generische Memory | Goal + Project Analysis |
| **Context** | 3 alte Memories | Project structure, git, files, errors |
| **LLM weiß** | "Es gibt ein Projekt" | Exact: 640 LOC, 21 files, 70% done |
| **LLM erstellt** | Generic template | Specific action plan |
| **Beispiel** | "download software" | "verify phi4-reasoning model loaded" |

---

## 🚀 QUICK FIX (30 Minuten)

Füge zu `agent_plan` Handler 3 Zeilen hinzu:

```python
async def handle_agent_plan(goal: str):
    # BESTEHEND
    mem_ctx = memory.search(goal, n_results=3)
    
    # NEU - PRE-CONTEXT
    workspace_info = await get_project_summary()  # ← Neue Funktion
    system_context = format_system_prompt(workspace_info)  # ← Neue Funktion
    
    # MODIFIZIERT
    subtasks = planner.plan(goal, [system_context] + mem_ctx)
    
    return subtasks
```

`get_project_summary()` (nur 20 Zeilen):
```python
async def get_project_summary():
    return {
        "status": "70% complete - Agent OS v2.1",
        "modules": ["core", "agents", "tools", "api", "memory", "tasks"],
        "lines_of_code": 640,
        "modelle": ["phi4-reasoning", "qwen2.5-coder", "gpt-oss"],
        "missing": "Learning System: Checkpoints, Feedback, Patterns",
        "entry_points": ["run.py", "mcp_server.py", "uvicorn api.kernel:app"],
    }
```

---

## 📝 ANTWORT AUF DEINE FRAGE

**"Wie nutzt der Agent die Workspace & Skripte?"**

**Antwort:** **Er tut es NICHT!** Das ist das Design-Problem.

Der Agent-Flow ist gut:
- Router wählt Modell ✅
- Worker führt mit Tools aus ✅
- Memory speichert ✅
- Reviewer prüft ✅

**ABER:** Der `agent_plan` Tool bekommt nicht genug Context über das Projekt.

**Lösung:** Workspace Intelligence Tool schreiben, das:
1. Projekt-Struktur liest
2. Git-Status prüft
3. Dateien analysiert
4. Fehler erkennt
5. Diesen Context dem LLM gibt

Dann erstellt das LLM intelligente, projekt-spezifische Pläne! 🎯

---

*Geschrieben: 17.04.2026*
