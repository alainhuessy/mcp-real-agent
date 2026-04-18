# 🎯 Live Tracking Guide — Nachverfolgung der Agent-Ausführung

**Neue Feature**: Echtzeit-Überwachung von Agent-Tasks in `run.py` ✅

---

## 🎬 Quick Start

### 1. Agent starten
```bash
# Terminal 1: MCP Server (für Continue)
python mcp_server.py

# Terminal 2: CLI mit Tracking
python run.py
```

### 2. Task mit Tracking starten
```
Task > tracked:write a Python function that sorts a list
```

### 3. Live Verfolgung im Terminal
```
🎯 Task gestartet: write a Python function that sorts a list

[1/4] 📊 Analysiere Task...
   ✅ Analyzed
   Progress: [██░░░░░░░░] 25% (1/4 done)

[2/4] 📋 Erstelle Ausführungsplan...
   Router → Mode: coder
   ✅ Plan erstellt
   Progress: [████░░░░░░] 50% (2/4 done)

[3/4] ⚡ Führe aus...
   LLM Response: def sort_list(items):...
   ✅ Ausgeführt
   Progress: [██████░░░░] 75% (3/4 done)

[4/4] 🧪 Teste Ergebnis...
   ✅ Verifiziert
   Progress: [██████████] 100% (4/4 done)

📊 Execution Summary
                        📋 Todos                        
┏━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ #   ┃ Title          ┃ Status         ┃ Time       ┃
┡━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1   │ Analyze req... │ ✅ completed   │ 0.2s       │
│ 2   │ Create plan... │ ✅ completed   │ 0.2s       │
│ 3   │ Execute task...│ ✅ completed   │ 0.2s       │
│ 4   │ Verify test... │ ✅ completed   │ 0.2s       │
└─────┴────────────────┴────────────────┴────────────┘

        📊 Summary        
┏━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Metric      ┃ Value  ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Total Todos │ 4      │
│ ✅ Complete │ 4      │
│ Progress    │ 100%   │
│ Duration    │ 0.8s   │
└─────────────┴────────┘

✅ Task Complete
```

---

## 📝 Kommandos im Detail

### Normale Task-Ausführung (im Hintergrund)
```
Task > write a Python function
```
→ Task wird ausgeführt, aber **kein Tracking in Echtzeit**  
→ Sie sehen nur das finale Ergebnis

### ⭐ Tracked Task-Ausführung (mit Live-Überwachung)
```
Task > tracked:write a Python function
```
→ Task wird ausgeführt **MIT Echtzeit-Verfolgung**  
→ Sie sehen alle 4 Phasen live im Terminal:
1. **Analyse** — Task verstehen
2. **Planung** — Execution-Plan erstellen (Router Mode)
3. **Ausführung** — LLM antwortet, Befehle werden ausgeführt
4. **Test** — Ergebnis verifizieren

### Was Sie sehen:
- ✅ Welcher **LLM Mode** wird verwendet (coder/planner/rag/chat)
- ✅ **Progress Bar** mit % und Anzahl completed steps
- ✅ Was LLM **antwortet** (gekürzte Version)
- ✅ **Shell-Befehle**, die ausgeführt werden
- ✅ **Timing** für jeden Step
- ✅ **Finale Summary** mit Status & Dauer

---

## 🔗 Wie Continue damit arbeitet

### Scenario 1: Continue ruft MCP Tool auf
```
Continue IDE (User)
    ↓
mcp_server.py (MCP Protocol)
    ↓
MCP Tool Handler (z.B. agent_run_task)
    ↓
Worker.execute() (im Hintergrund)
    ↓
Result an Continue zurück
```

**Status**: Sie sehen nur das **finale Ergebnis** in Continue  
**Tracking**: Sie können parallel in Terminal 2 `tracked:` verwenden

### Scenario 2: Parallele Operationen
```
Terminal 1: Continue IDE mit MCP
  └─ MCP Server läuft im Hintergrund

Terminal 2: CLI mit run.py
  └─ Task > tracked:write a test
  └─ Sehen Sie LIVE tracking!
```

---

## 🎓 Praktische Beispiele

### Beispiel 1: Python-Funktion schreiben
```
Task > tracked:write a Python function to calculate fibonacci numbers
```

### Beispiel 2: Code refaktorieren
```
Task > tracked:refactor this code for better performance
[Kopiere Code wenn gefragt]
```

### Beispiel 3: Bug fixen
```
Task > tracked:debug and fix this error
[Beschreibe das Problem]
```

### Beispiel 4: Mehrere aufeinander folgende Aufgaben
```
Task > tracked:analyze the project structure
[Sehen Sie Analyse mit Tracking]

Task > tracked:create test suite for core module
[Sehen Sie Test-Erstellung mit Tracking]
```

---

## 🔍 Was Sie beobachten können

### Progress Bar (Echtzeit)
```
Progress: [████░░░░░░] 50% (2/4 done, 1 running, 0 failures)
```
- `█` = Abgeschlossene Steps
- `░` = Verbleibende Steps
- Prozent-Anzeige
- Geschichte: completed / in-progress / failed

### LLM Response Preview
```
LLM Response: def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1)...
```
- Zeigt die **erste 200 Chars** der LLM-Antwort
- Erkennt **SHELL:** Befehle
- Zeigt **Shell Output** wenn Befehle ausgeführt werden

### Router Decision
```
Router → Mode: coder
```
- Task-Router entscheidet den **LLM Mode**:
  - **coder** — Code-Aufgaben
  - **planner** — Planung & Design
  - **rag** — Information retrieval
  - **chat** — Conversation

---

## 📊 Timing & Performance

Die Summary zeigt:
- **Wie lange jeder Step dauert**
- **Gesamtdauer der Task**
- **Durchschnittliche Step-Dauer**

```
│ 1   │ Analyze req... │ ✅ completed   │ 0.2s       │
│ 2   │ Create plan... │ ✅ completed   │ 0.3s       │
│ 3   │ Execute task...│ ✅ completed   │ 1.2s       │
│ 4   │ Verify test... │ ✅ completed   │ 0.2s       │
```

→ **Bottleneck erkennen**: Schritt 3 dauerte am längsten (LLM Inference)

---

## ⚙️ Konfiguration

### Tracking ausschalten
If you don't want progress bars:
```python
# In run.py, tracked: handler
result = agent.worker.tracked_execute(task_name, show_progress=False)
```

### Tracking nur für bestimmte Task-Typen
```bash
Task > tracked:long task that takes minutes
# Sehen Sie Echtzeit-Progress!

Task > quick shell command
# Direkt ohne Tracking (deutlich schneller)
```

---

## 🧠 Continue + CLI Workflow

### Recommended Setup
```
┌─────────────────────────────────────┐
│ Continue IDE (Main Interface)        │
│ - MCP Tools für Quick Actions        │
│ - Code Completion                    │
│ - Inline Suggestions                 │
└──────────────┬──────────────────────┘
               │ (Bei komplexen Tasks)
               ↓
┌──────────────────────────────────────┐
│ Terminal 2: python run.py            │
│ Task > tracked:complex task          │
│                                      │
│ 🎯 Sehen Sie Live Tracking          │
│ - Progress Bars                      │
│ - LLM Responses                      │
│ - Tool Execution                     │
│ - Timing Info                        │
└──────────────────────────────────────┘
```

### Workflow
1. **In Continue**: "Schreibe ein Test"
   - MCP ruft agent_run_task auf
   - Result kommt in Continue zurück

2. **Im Terminal**: `tracked:similar task`
   - Sie sehen **genau wie** der Agent arbeitet
   - Sie sehen **warum** Task was tut
   - Sie sehen **wie lange** jeder Step dauert

---

## 🐛 Debugging mit Tracking

### Problem: Task dauert zu lange
```
Task > tracked:complex analysis

[3/4] ⚡ Führe aus...
   Warning: LLM Response delayed (5.2s)
```
→ **LLM Inference ist Bottleneck** (CPU-Limit oder Modell zu groß)

### Problem: Shell-Befehl schlägt fehl
```
[3/4] ⚡ Führe aus...
   🖥️  Führe Shell aus: git push
   ❌ Error: Permission denied
```
→ **Shell Command schlägt fehl** (berechtigungen, git config, etc.)

### Problem: Task hängt fest
```
Task > tracked:long task
[1/4] 📊 Analysiere Task...
[Hängt hier fest]
```
→ **Drücke Ctrl+C** zum Abbrechen

---

## 📚 Integration mit Auto Todo-Tracker

Das System nutzt intern `AutoTodoTracker`:

```python
# Was passiert im Hintergrund:
tracker = AutoTodoTracker(task)
tracker.add_todo("1. Analyze requirements")
tracker.mark_inprogress(1)
# ... work ...
tracker.mark_completed(1)  # ← Sofort aktualisiert!
tracker.print_todos()      # ← In Terminal angezeigt
```

→ **Sie sehen exakt das gleiche wie im Demo**!

---

## 🎯 Best Practices

### ✅ WAS Sie tun sollten
- **Komplexe Tasks** mit `tracked:` starten für Debugging
- **Shell-Befehle** im Tracking sehen um sicherzustellen sie richtig sind
- **Zeitmessungen** nutzen um Performance-Probleme zu finden
- **Progress Bars** nutzen um lange Tasks im Auge zu behalten

### ❌ WAS Sie nicht tun sollten
- Nicht **alle Tasks mit Tracking** starten (verlangsamt Execution)
- Nicht **direkt auf Continue warten** während Terminal läuft
- Nicht **Tracking bei sehr kurzen Tasks** (unnötig verbose)

---

## 🔗 Command Reference

```bash
# Normale (schnelle) Ausführung
Task > write a Python function
Task > refactor this code
Task > analyze the error

# Tracked (mit Echtzeit-Überwachung)
Task > tracked:write a Python function
Task > tracked:refactor this code
Task > tracked:analyze the error

# Shell-Befehle
Task > shell:ls -la main/

# Plan/Planalyse
Task > plan:create a REST API with FastAPI

# System
Task > status          # Agent Status
Task > tasks           # Task Queue
Task > loop            # Autonome Loop

# Exit
Task > quit
```

---

## 📞 Support

**Q**: Warum ist Tracking langsamer?
**A**: Weil der Agent extra Verifikations-Steps macht. Nutze es nur wenn du verstehen willst WAS passiert.

**Q**: Kann ich Tracking in Continue einbinden?
**A**: Nein, Continue nutzt MCP Protocol (binary). Nutze das Terminal für Tracking.

**Q**: Speichert sich der Tracking-Verlauf?
**A**: Ja! Automatisch in `task_logs/` als JSON

---

**🎉 Jetzt sehen Sie live, wie Ihr Agent arbeitet!**
