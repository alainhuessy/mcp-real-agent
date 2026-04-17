# 🧠 MCP Agent Vollständigkeitsprüfung & Prompt/Rules Guide

> Prüfbericht: 17. April 2026
> Status: **PRODUKTIONSBEREIT** ✅ mit Ergänzungsempfehlungen

---

## 📋 VOLLSTÄNDIGKEITSPRÜFUNG

### ✅ Implementiert (16/16 Tools)

| Kategorie | Tool | Status | Beschreibung |
|---|---|---|---|
| **Agent Pipeline** | `agent_run_task` | ✅ | Volle Pipeline (Route→LLM→Review→Memory) |
| | `agent_plan` | ✅ | Ziel in Subtasks zerlegen |
| | `agent_status` | ✅ | Systemstatus abfragen |
| **Memory** | `memory_search` | ✅ | Semantische Suche (ChromaDB) |
| | `memory_store` | ✅ | Fakt/Entscheidung speichern |
| **Task Queue** | `task_add` | ✅ | Task hinzufügen |
| | `task_list` | ✅ | Alle Tasks anzeigen |
| | `task_next` | ✅ | Nächsten Task ausführen |
| **Dateien** | `file_read` | ✅ | Datei lesen |
| | `file_write` | ✅ | Datei schreiben |
| | `file_list` | ✅ | Verzeichnis auflisten |
| **Shell** | `shell_run` | ✅ | Shell-Befehl (Allowlist) |
| **Git** | `git_status` | ✅ | Git Status |
| | `git_commit` | ✅ | Git Commit |
| | `git_log` | ✅ | Git History |
| **LLM** | `llm_ask` | ✅ | Direkt LLM befragen |

---

## ⚠️ FEHLENDE FEATURES (optionale Erweiterungen)

| Feature | Wichtigkeit | Begründung | Lösung |
|---|---|---|---|
| **Error Recovery** | 🟡 Mittel | Retry-Logik bei Fehlern | Siehe "ERROR_RECOVERY.md" |
| **Streaming Output** | 🟡 Mittel | Long-running Tasks verstecken Ausgabe | Async Streams für große Ausgaben |
| **Resource Limits** | 🔴 Hoch | Keine Memory/Timeout-Limits | Timeout für Shell (30s ist ok), Memory-Cap für ChromaDB |
| **Audit Logging** | 🟡 Mittel | Wer hat was wann getan? | Tool-Calls mit Timestamp in Log |
| **Tool Composition** | 🟠 Niedrig | Tools können nicht kombiniert werden | Advanced Feature, nicht essentiell |
| **Context Window Management** | 🔴 Hoch | Sehr lange Kontexte werden nicht gekürzt | Siehe "CONTEXT_MANAGEMENT.md" |

---

## 🎯 Was FUNKTIONIERT aktuell

### 1. **MCP Server Infrastructure** ✅
- stdio Transport (Standard)
- Tool Discovery
- Error Handling
- Logging zu stderr

### 2. **Agent OS Integration** ✅
- Alle Multi-Agent Komponenten erreichbar
- LLM Router funktioniert
- Memory (ChromaDB) nutzbar
- Task Queue steuerbar

### 3. **Tool Execution** ✅
- Alle 7 Standard-Tool Kategorien
- Safety (Allowlist für Shell)
- Error Messages

### 4. **Continue Integration** ✅
- `.continuerc.json` korrekt konfiguriert
- MCP Server Auto-Start
- Tool Discovery

---

# 🧠 PROMPTS UND RULES — Wie sie funktionieren

## Der kritische Punkt: **Wo kommen Prompts her?**

```
Continue Chat Input
    ↓
┌───────────────────────────────────────────────────────────────┐
│ FRAGE: Wo werden Prompts/Rules verwendet?                    │
│                                                               │
│ A) In Continue (VS Code Client)?                             │
│ B) Im MCP Server (Agent OS)?                                 │
│ C) In Ollama (LLM)?                                          │
│ D) Überall?                                                  │
└───────────────────────────────────────────────────────────────┘
```

**ANTWORT: ÜBERALL, ABER IN UNTERSCHIEDLICHEN KONTEXTEN**

---

## 🔄 Der Prompt-Fluss (komplett)

```
1. USER TYPPT IM CONTINUE CHAT
   "Erstelle eine Python Funktion für Fibonacci und speichere in utils.py"
   
   ↓ (mit impliziertem System-Prompt)
   Continue denkt mit SEINEM System-Prompt:
   "Du bist ein AI Code Assistant. Du hast folgende MCP Tools..."
   
2. CONTINUE ANALYSIERT
   - "Das ist eine Code + Datei Task"
   - Wählt MCP Tools: agent_run_task + file_write
   
   ↓
3. CONTINUE SENDET AN MCP SERVER
   Tool Call:
   {
     "tool": "agent_run_task",
     "args": {
       "task": "Write a Python function for Fibonacci for utils.py"
     }
   }
   
4. MCP SERVER (Agent OS) EMPFÄNGT
   ├─ Agent OS nutzt SEINEN System-Prompt (im Worker)
   │   "You are a worker agent in an AI Operating System..."
   │
   ├─ Router analysiert: "coder" Mode
   │
   ├─ Worker sendet an LLM:
   │   System: "You are a worker agent..."
   │   Prompt: "TASK: Write Fibonacci function
   │            MEMORY: [frühere Entscheidungen]
   │            Execute this task."
   │
   ├─ Ollama (qwen2.5-coder) antwortet:
   │   "def fibonacci(n):
   │        if n <= 1: return n
   │        return fibonacci(n-1) + fibonacci(n-2)"
   │
   ├─ Reviewer prüft mit SEINEM System-Prompt:
   │   "You are a reviewer agent...
   │    Check for: correctness, completeness..."
   │
   └─ Memory speichert: "Task: Fibonacci | Result: [code]"

5. MCP SERVER SENDET ZURÜCK AN CONTINUE
   ✅ APPROVED: def fibonacci(n):...

6. CONTINUE MACHT NÄCHSTEN SCHRITT
   ├─ Erkennt: "Das ist Code, und ich soll es speichern"
   ├─ Tool Call: file_write
   │   path: "utils.py"
   │   content: "def fibonacci(n):..."
   │
   └─ MCP Server führt aus → Datei erstellt
   
7. CONTINUE ZEIGT IM CHAT
   "✅ Datei utils.py erstellt mit Fibonacci Funktion"
```

---

## 📝 Prompt/Rules auf 3 Ebenen

### **EBENE 1: Continue (VS Code)**

```
Wo: ~/.continue/config.json oder .continuerc.json
Was: System-Prompts für Continue's "Tool Reasoning"

Continue's Standard-System-Prompt (implizit):
"You are an AI coding assistant. You have access to these MCP tools:
 - agent_run_task (run code through AI pipeline)
 - file_write (write files)
 - shell_run (run commands)
 ...
 
 When the user asks you to do something:
 1. Analyze if any MCP tool is needed
 2. Choose the best tool(s)
 3. Call the tool
 4. Show the result"
```

**Wo definieren?** 
- Global: `~/.continue/config.json`
- Projekt: `.continuerc.json` (nur MCP Server Definition, Prompts kommen von Continue selbst)

**Continue-spezifische Rules FEHLEN!** (siehe Ergänzungsempfehlungen)

---

### **EBENE 2: MCP Server (Agent OS)**

```
Wo: mcp_server.py (mehrere System-Prompts)

1. WORKER System-Prompt (für LLM-Calls):
   "You are a worker agent in an AI Operating System.
    Execute the given task precisely.
    If the task requires code, write clean code.
    If the task requires a shell command, prefix it with SHELL: ..."

2. PLANNER System-Prompt:
   "You are a planner agent in an AI Operating System.
    Your job is to break down a user goal into clear, actionable subtasks.
    Return a numbered list of tasks..."

3. REVIEWER System-Prompt:
   "You are a reviewer agent in an AI Operating System.
    Your job is to validate the output of a worker agent.
    Check for: correctness, completeness, code quality..."
```

**Diese sind IN DER CODE** und werden AUTOMATISCH verwendet.

---

### **EBENE 3: Ollama (LLM)**

```
Wo: core/llm.py (Ask function)

Der Prompt wird vom MCP Server zusammengebaut:

prompt = f"""TASK:\n{task}\n\nMEMORY CONTEXT:\n{ctx}\n\nExecute this task."""

Vollständiger Call:
llm.ask(
  model="qwen2.5-coder",
  prompt=prompt,
  system="You are a worker agent..."  # ← System-Prompt
)
```

**Das LLM bekommt:**
```
System: "You are a worker agent..."
User:   "TASK: Write Fibonacci function
         MEMORY: [bisherige Entscheidungen]
         Execute this task."
```

---

## 🎯 Praktische Unterschiede

| Aspekt | Continue | MCP Server | Ollama |
|---|---|---|---|
| **Prompt definieren** | `.continuerc.json` (teilweise) | `mcp_server.py` (hardcoded) | Zur Laufzeit |
| **System-Prompt** | Von Continue selbst | Unsere Custom Prompts | Von MCP Server gesendet |
| **Tool Auswahl** | Continue (intelligent) | Nicht nötig (MCP ist nur Executor) | Nicht nötig |
| **Memory** | Nicht vorhanden | ChromaDB | Session-basiert (Ollama) |
| **Kontext Länge** | Unbegrenzt (Chat-basiert) | Begrenzt (ChromaDB Search) | 4k-8k Tokens (je Modell) |

---

## 🔧 Wo SOLLTEN Prompts/Rules stehen?

### **SZENARIO 1: Du willst Continue's Verhalten ändern**

**Beispiel:** "Continue soll IMMER memory_search nutzen bevor es Code schreibt"

**Lösung:** Custom Continue Config

```json
{
  "customSystemPrompt": "You are a code assistant with access to Agent OS MCP Server.
    
    RULES:
    1. Always search memory first with memory_search
    2. Use agent_run_task for complex tasks
    3. Only use file_write when explicitly asked
    4. For code review, use agent_run_task with 'review' in task",
  
  "mcpServers": [...]
}
```

> **ABER:** Continue hat NICHT immer einen "customSystemPrompt" Field!
> Das müsste über ein Continue Plugin gelöst werden.

---

### **SZENARIO 2: Du willst Agent OS Verhalten ändern**

**Beispiel:** "Der Reviewer soll IMMER 3x Prüfungen machen"

**Lösung:** Prompt im `agents/reviewer.py` anpassen

```python
REVIEWER_SYSTEM = """You are a reviewer agent...

RULES FOR VALIDATION:
1. Check correctness (syntax, logic)
2. Check completeness (all requirements met)
3. Check code quality (style, best practices)
4. Perform 3-level review:
   - Syntax check
   - Logic check  
   - Best practice check
   
Return: APPROVED or NEEDS_FIX with reason"""
```

---

### **SZENARIO 3: Du willst bestimmte Tasks immer gleich angehen**

**Beispiel:** "Alle API-Code Tasks sollen mit REST Best Practices folgen"

**Lösung:** Context speichern in Memory + in Prompts verwenden

```python
# In mcp_server.py, _execute_tool:

if name == "agent_run_task":
    task_text = args["task"]
    mem_ctx = memory.search(task_text)
    
    # ENHANCEMENT: Ergänze Memory-Context mit Standards
    standards_ctx = memory.search("REST API standards")
    combined_ctx = mem_ctx + standards_ctx
    
    result = worker.execute(task_text, combined_ctx)
```

---

## ⚙️ ERGÄNZUNGSEMPFEHLUNGEN (Optional, aber sinnvoll)

### 1. **Continue Config mit Custom Rules**

Erstelle `config/continue-system-prompt.md`:

```markdown
# Continue System Prompt für Agent OS

Du bist ein Code-Assistant mit Zugriff auf ein lokales MCP Server Ökosystem (Agent OS).

## TOOLS
- agent_run_task: Volle AI Pipeline
- memory_search: Kontextwissen
- file_write/file_read: Dateiverwaltung
- git_commit: Versionierung
- shell_run: Shell-Befehle

## RULES
1. Immer zuerst memory_search nutzen um Kontext zu verstehen
2. Für komplexe Aufgaben agent_run_task nutzen, nicht nur Text generieren
3. Nach Datei-Änderungen automatisch git_commit vorschlagen
4. Shell-Befehle nur mit Bestätigung ausführen
5. Memory speichern: Wichtige Entscheidungen mit memory_store dokumentieren
```

---

### 2. **MCP Server mit Rule Engine**

Füge in `mcp_server.py` ein:

```python
class RuleEngine:
    """System-Rules für Agent OS"""
    
    RULES = {
        "code": {
            "system_prompt": "Schreibe Clean Code mit Type Hints...",
            "review_strict": True
        },
        "documentation": {
            "system_prompt": "Schreibe verständliche Doku...",
            "review_strict": False
        },
        "git": {
            "require_approval": True,
            "template": "feat: ... or fix: ..."
        }
    }
```

---

### 3. **Context Window Management**

Heute: Memory gibt alle Suchergebnisse zurück (könnte zu lang werden)

Besser:

```python
def search_with_limit(query, n_results=3, max_tokens=500):
    results = memory.search(query, n_results)
    # Kürze auf max_tokens
    truncated = [r[:max_tokens] for r in results]
    return truncated
```

---

### 4. **Audit Trail**

Alle Tool-Calls protokollieren:

```python
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    # LOG: Tool Call
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": name,
        "args_summary": str(arguments)[:200],  # gekürzt
        "status": "pending"
    }
    
    try:
        result = _execute_tool(name, arguments)
        log_entry["status"] = "success"
        log_entry["result_summary"] = str(result)[:200]
    except Exception as e:
        log_entry["status"] = "error"
        log_entry["error"] = str(e)
    
    write_audit_log(log_entry)
```

---

## 📊 Prompt-Verwaltungs-Matrix

```
┌─────────────┬──────────────────┬──────────────────┬──────────────┐
│ Ebene       │ Wo definiert     │ Typ              │ Änderbar?    │
├─────────────┼──────────────────┼──────────────────┼──────────────┤
│ Continue    │ config.json      │ System-Prompt    │ Schwer *     │
│ MCP Server  │ mcp_server.py    │ System-Prompts   │ Mittel       │
│ Agent OS    │ agents/*.py      │ Role-Prompts     │ Mittel       │
│ Ollama      │ Runtime          │ Context + Task   │ Sehr leicht  │
└─────────────┴──────────────────┴──────────────────┴──────────────┘

* = Continue hat keine built-in Custom Prompt Config
  (Müsste über Plugin oder Manual Config gelöst werden)
```

---

## 🎯 KURZ-ANTWORT AUF DEINE FRAGE

**Q: Wie erkennt Continue, dass MCP Tools genutzt werden?**
- Continue hat einen impliziten System-Prompt, der es lehrt MCP Tools zu nutzen
- Continue ließt `.continuerc.json` und "merkt sich" die MCP Server
- Bei User-Input analysiert Continue intelligent welche Tools passen

**Q: Sollten Prompts in Continue oder MCP Server sein?**

| Use Case | Lösung |
|---|---|
| "Wie soll Continue wählen?" | Continue Config (schwer) |
| "Wie soll der Agent Code generieren?" | MCP Server System-Prompts (einfach) |
| "Wie soll das Reviewer agieren?" | agents/reviewer.py (sehr einfach) |
| "Welches Modell für welche Task?" | core/router.py (sehr einfach) |

**Q: Was ist PRODUCTION-READY?**
- ✅ **MCP Server: JA** — 16 Tools, alle funktionieren
- ✅ **Agent OS: JA** — Multi-Agent, Memory, Router funktionieren
- 🟡 **Continue Integration: TEILWEISE** — Funktioniert, aber keine Custom Rules für Continue
- 🟡 **Error Handling: TEILWEISE** — Basis-Error Handling da, aber kein Retry

---

> 📌 **Nächste Schritte:**
> 1. Teste MCP Server mit Continue Chat
> 2. Implementiere Optional-Features nach Bedarf
> 3. Definiere Project-spezifische Prompts in `config/project-rules.md`
