# 🏗️ Agent Tracking Architecture

## System Overview

```
┌────────────────────────────────────────────────────────────────┐
│                    YOUR DEVELOPMENT SETUP                       │
└────────────────────────────────────────────────────────────────┘

┌─────────────────────────────┐      ┌──────────────────────────┐
│   TERMINAL 1: Continue IDE  │      │  TERMINAL 2: CLI (run.py)│
│                             │      │                          │
│  • Code writing             │      │  • Task input            │
│  • Quick fixes              │      │  • Tracking display      │
│  • MCP Tools (fast)         │      │  • Progress bars         │
│                             │      │  • Debug insights        │
└────────┬────────────────────┘      └───────────┬──────────────┘
         │                                       │
         │ MCP Protocol (binary)                │ stdin/stdout
         │                                       │
         ▼                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              MCP SERVER (mcp_server.py)                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Tools:                                                    │   │
│  │  • agent_run_task          [Quick, no tracking]         │   │
│  │  • agent_run_task_tracked  [Tracked version]            │   │
│  │  • agent_plan              [Planning]                    │   │
│  │  • memory_search/save      [Memory ops]                 │   │
│  │  • shell_run               [Execute commands]            │   │
│  │  • ... 15+ more tools                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────┬──────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
            ▼                         ▼
     ┌──────────────┐         ┌───────────────┐
     │ Normal Path  │         │ Tracked Path  │
     │              │         │               │
     │ agent.execute│         │ agent.tracked_│
     │              │         │ execute()     │
     │ [FAST]       │         │ [VERBOSE]     │
     └──────────────┘         └───────────────┘
            │                         │
            │                         ▼
            │                  ┌─────────────────────┐
            │                  │ 4-Phase Execution   │
            │                  │                     │
            │                  │ 1. ANALYZE          │
            │                  │    [Progress: 25%]  │
            │                  │                     │
            │                  │ 2. PLAN             │
            │                  │    [Router Decision]│
            │                  │    [Progress: 50%]  │
            │                  │                     │
            │                  │ 3. EXECUTE          │
            │                  │    [LLM Response]   │
            │                  │    [Progress: 75%]  │
            │                  │                     │
            │                  │ 4. VERIFY           │
            │                  │    [Progress: 100%] │
            │                  │                     │
            │                  └─────────────────────┘
            │                         │
            │                         ▼
            │                  ┌─────────────────────┐
            │                  │ AutoTodoTracker     │
            │                  │                     │
            │                  │ • mark_inprogress() │
            │                  │ • mark_completed()  │
            │                  │ • print_todos()     │
            │                  │ • print_summary()   │
            │                  │                     │
            │                  └─────────────────────┘
            │                         │
            ▼                         ▼
     ┌──────────────────────────────────────┐
     │   SHARED COMPONENTS                   │
     │                                       │
     │  • LLM (Ollama)                       │
     │  • Router (Task → Mode)               │
     │  • Memory (ChromaDB)                  │
     │  • Tools (Registry)                   │
     │  • Planner, Reviewer                  │
     │                                       │
     └──────────────────────────────────────┘
```

---

## Data Flow (Detailed)

### **Path 1: Continue IDE → MCP → Normal Execution**

```
Continue User Action
  ↓
MCP Transport (stdio)
  ↓
mcp_server.py list_tools()
  ↓ [User selects: agent_run_task]
  ↓
mcp_server.py call_tool("agent_run_task")
  ↓
_execute_tool() handler
  ↓
worker.execute(task, memory_context)
  ├─ router.route(task)
  ├─ llm.ask(model, prompt)
  └─ tools.run("shell", cmd) [if needed]
  ↓
Result returned to Continue
[~1-5 seconds total]
```

**Result in Continue**: Final answer only

---

### **Path 2: Terminal CLI → Tracked Execution**

```
Terminal Input: tracked:write a function
  ↓
run.py detects "tracked:" prefix
  ↓
agent.worker.tracked_execute(task, show_progress=True)
  ↓
├─ Phase 1: ANALYZE
│  ├─ Create tracker
│  ├─ Add todos
│  ├─ mark_inprogress(1)
│  ├─ [Simulate analysis]
│  ├─ mark_completed(1)
│  └─ print progress bar
│
├─ Phase 2: PLAN
│  ├─ mark_inprogress(2)
│  ├─ router.route(task)
│  ├─ Display: Router → Mode: coder
│  ├─ mark_completed(2)
│  └─ print progress bar
│
├─ Phase 3: EXECUTE
│  ├─ mark_inprogress(3)
│  ├─ model = llm.get_model(mode)
│  ├─ result = llm.ask(model, prompt)
│  ├─ Display: LLM Response: [first 200 chars]
│  ├─ [if "SHELL:" → execute shell commands]
│  ├─ mark_completed(3)
│  └─ print progress bar
│
└─ Phase 4: VERIFY
   ├─ mark_inprogress(4)
   ├─ [Simulate verification]
   ├─ mark_completed(4)
   ├─ print final todos table
   ├─ print summary
   └─ save to task_logs/
```

**Result in Terminal**: 
- Progress bars (0% → 100%)
- Todo table with timings
- Summary report
- Full visibility into what agent did

---

## Component Integration

### **AutoTodoTracker**
```python
class AutoTodoTracker:
    todos: list[TodoItem]      # 4 items for each phase
    
    def mark_inprogress(id):   # When starting a phase
        # Updates UI → Progress bar
        
    def mark_completed(id):    # When phase done
        # Updates UI → ✅ symbol + timing
        
    def print_todos():         # Display table
        # Beautiful Rich table
        
    def print_summary():       # Display metrics
        # Summary stats
```

### **WorkerAgent Enhancement**
```python
class WorkerAgent:
    def execute(task):
        # OLD: Basic execution, no tracking
        # Used by Continue for speed
        
    def tracked_execute(task, show_progress=True):
        # NEW: 4-phase execution with tracking
        # Used by CLI for visibility
        
    def start_tracked_task(task, plan):
        # Manual control: You manage phases
        # For custom workflows
```

### **MCP Tools**
```
agent_run_task()          ← Used by Continue (fast)
agent_run_task_tracked()  ← Alternative (tracked)
agent_plan()              ← Planning
agent_review()            ← Code review
memory_search()           ← Memory access
shell_run()               ← Command execution
... 15+ more tools
```

---

## Command Execution Modes

```
TERMINAL INPUT          →  EXECUTION PATH              →  OUTPUT
──────────────────────────────────────────────────────────────────

write a function        →  worker.execute()            →  Result only
                            [No tracking]

tracked:write function  →  worker.tracked_execute()    →  Progress bars
                            [4 phases with UI]         +  Todo table
                                                       +  Summary

shell:ls -la            →  tools.run("shell", cmd)     →  Shell output

plan:build an API       →  agent.planner.plan()        →  Subtasks list

status                  →  agent.show_status()         →  System stats

loop                    →  agent.run_loop()            →  Continuous task
                            [Processes queue]          execution
```

---

## Architecture Decisions

### Why Separate Paths?

| Aspect | Normal | Tracked | Why? |
|--------|--------|---------|------|
| **Speed** | ⚡ Fast | 🐢 Slower | Tracking adds verification |
| **UI** | Minimal | Rich | Different use cases |
| **Hidden** | Yes | No | You see everything |
| **Best For** | Continue IDE | Debugging |  |

### Why Not Always Tracked?

- 🐢 Slower (extra steps)
- 📺 Too much output
- ⚡ Continue expects speed
- 💾 Not needed for production

### Why Keep Both?

- ✅ Fast path for normal work
- ✅ Detailed path for debugging
- ✅ User chooses when they need visibility

---

## Integration Points

### 1. Continue ↔ MCP Server
- **Transport**: stdio protocol
- **Direction**: One-way calls from Continue
- **Speed**: Sub-second responses expected
- **Tracking**: Hidden (not visible)

### 2. Terminal ↔ run.py
- **Transport**: stdin/stdout
- **Direction**: Interactive input
- **Speed**: No constraint (user watching)
- **Tracking**: Fully visible

### 3. MCP Server ↔ Worker
- **Method**: Direct function calls
- **Speed**: Depends on `show_progress` flag
- **Output**: stdio vs file

### 4. AutoTodoTracker ↔ UI
- **Rich Console**: Terminal output
- **Formats**: Tables, bars, summaries
- **Persistence**: JSON logs

---

## Example: Complete Flow

```
User in Continue IDE:
  "Write a function to validate emails"
  
  ↓ (MCP Tool: agent_run_task)
  
mcp_server processes:
  → router.route("validate emails") = "coder"
  → llm.ask("coder", prompt) 
  → returns: "def validate_email(email): ..."
  
Continue shows:
  ✅ [Full code solution in editor]
  
Meanwhile, user opens Terminal tab:
  
  Task > tracked:Write a function to validate emails
  
Terminal shows:
  [1/4] 📊 Analysiere Task...
        ✅ Analyzed
        Progress: [██░░░░░░░░] 25%
        
  [2/4] 📋 Erstelle Plan...
        Router → Mode: coder
        ✅ Plan erstellt
        Progress: [████░░░░░░] 50%
        
  [3/4] ⚡ Führe aus...
        LLM Response: def validate_email(email):...
        ✅ Ausgeführt
        Progress: [██████░░░░] 75%
        
  [4/4] 🧪 Teste...
        ✅ Verifiziert
        Progress: [██████████] 100%
        
  📊 Summary: 4 todos, 0.8s total

User understands:
  ✅ What the task was
  ✅ How it was analyzed
  ✅ Which AI mode was used ("coder")
  ✅ What the solution is
  ✅ How long it took
```

---

## File Structure

```
mcp-real-agent/
│
├── agents/
│   ├── worker.py          ← Enhanced with tracked_execute()
│   ├── planner.py
│   └── reviewer.py
│
├── tasks/
│   ├── auto_todo_tracker.py   ← Core tracking system
│   ├── task_queue.py
│   └── scheduler.py
│
├── core/
│   ├── agent.py
│   ├── llm.py
│   ├── router.py
│   └── tools.py
│
├── docs/
│   ├── LIVE_TRACKING_GUIDE.md   ← User guide
│   └── ...
│
├── run.py                 ← Enhanced with tracked: command
├── mcp_server.py          ← Enhanced with tracked tool
├── demo_tracking.py       ← Standalone demo
│
└── TRACKING_ANSWER.md     ← Your question answered
```

---

## Next Steps

1. **Try it:**
   ```bash
   python run.py
   Task > tracked:your task here
   ```

2. **Open docs:**
   - [LIVE_TRACKING_GUIDE.md](docs/LIVE_TRACKING_GUIDE.md) — Detailed guide
   - [TRACKING_ANSWER.md](TRACKING_ANSWER.md) — Your question

3. **Run demo:**
   ```bash
   python demo_tracking.py
   ```

---

**🎯 Now you understand the complete architecture!**
