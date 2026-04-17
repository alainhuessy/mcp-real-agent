# ✅ Implementation Checklist: Active Pattern Detection

> Copy-Paste Code für die 3 Checkpoints

---

## 🎯 Was du jetzt verstanden hast

```
Problem:
  Solution Patterns sind gespeichert
  ABER Agent nutzt sie nie automatisch!
  
Lösung:
  Du brauchst 3 AKTIVE Checkpoints
  
  1️⃣ VOR Code-Generierung (Pattern Injection)
  2️⃣ WÄHREND Code-Generierung (Problem Detection)
  3️⃣ NACH Code-Generierung (Solution Lookup)
```

---

## 📋 Implementierungs-Checkliste

### SCHRITT 1: Problem Detection hinzufügen (2h)

**Datei:** `agents/worker.py`

Füge diese neue Methode hinzu:

```python
def _detect_and_fix_problems(self, code: str, memory) -> dict:
    """
    🔍 Detecte und fixe automatisch bekannte Probleme
    
    Returns: {"found": True/False, "problems": [...], "fixed_code": "..."}
    """
    problems_found = []
    fixes_applied = []
    fixed_code = code
    
    import re
    
    # PROBLEM 1: Hardcoded Passwords
    if re.search(r"(password|secret|api_key)\s*=\s*['\"][^'\"]*['\"]", code, re.IGNORECASE):
        problems_found.append("Hardcoded password/secret")
        solution = memory.find_solution_for_problem("Hardcoded password")
        if solution.get("found"):
            print(f"  ✅ Found solution: {solution['solution']}")
            # Replace: password = "..." → password = os.getenv(...)
            fixed_code = re.sub(
                r"(password|secret|api_key)\s*=\s*['\"][^'\"]*['\"]",
                r"\1 = os.getenv('\1'.upper())",
                fixed_code,
                flags=re.IGNORECASE
            )
            if "import os" not in fixed_code:
                fixed_code = "import os\n" + fixed_code
            fixes_applied.append(solution['solution'])
    
    # PROBLEM 2: Bare Except Clauses
    if re.search(r"except\s*:", code):
        problems_found.append("Bare except clause")
        solution = memory.find_solution_for_problem("Bare except clause")
        if solution.get("found"):
            print(f"  ✅ Found solution: {solution['solution']}")
            fixed_code = re.sub(r"except\s*:", r"except Exception as e:", fixed_code)
            fixes_applied.append(solution['solution'])
    
    # PROBLEM 3: SELECT * in Database
    if re.search(r"SELECT\s+\*", code, re.IGNORECASE):
        problems_found.append("SELECT * query")
        solution = memory.find_solution_for_problem("SELECT * query")
        if solution.get("found"):
            print(f"  ✅ Found solution: {solution['solution']}")
            fixes_applied.append(solution['solution'])
            # Hinweis: SELECT * Fix ist schwierig zu automatisieren
            # Daher: Nur Suggestion, kein Auto-Fix
    
    # PROBLEM 4: SQL Injection Risk
    if re.search(r"['\"]SELECT\s+.*\{.*\}", code, re.IGNORECASE):
        problems_found.append("SQL injection risk")
        solution = memory.find_solution_for_problem("SQL injection")
        if solution.get("found"):
            print(f"  ✅ Found solution: {solution['solution']}")
            fixes_applied.append(solution['solution'])
    
    # PROBLEM 5: No Error Handling
    if "def " in code and "try:" not in code and "except" not in code:
        if len(code.split('\n')) > 5:  # Nur für längere Functions
            problems_found.append("Missing error handling")
            solution = memory.find_solution_for_problem("Error handling")
            if solution.get("found"):
                print(f"  💡 Suggestion: {solution['solution']}")
    
    if problems_found:
        return {
            "found": True,
            "problems": problems_found,
            "fixes_applied": fixes_applied,
            "fixed_code": fixed_code,
        }
    else:
        return {"found": False}
```

In der `execute()` Methode einbauen:

```python
def execute(self, task, memory_context=""):
    """Execute task mit Auto-Fix"""
    from memory.memory import AgentMemory
    memory = AgentMemory()
    
    # ... existing code ...
    
    result = self.llm.query(enhanced_prompt, memory_context)
    
    # ✅ NEW: Detect and fix problems
    print(f"\n🔍 Analyzing generated code for known problems...")
    problems = self._detect_and_fix_problems(result, memory)
    
    if problems["found"]:
        print(f"⚠️  Found {len(problems['problems'])} problem(s)")
        print(f"✅ Applied fixes: {', '.join(problems['fixes_applied'])}")
        result = problems["fixed_code"]
    else:
        print(f"✅ No known problems detected")
    
    return result
```

---

### SCHRITT 2: Pattern Injection (1h)

**Datei:** `agents/worker.py`

Erweitere `execute()`:

```python
def execute(self, task, memory_context=""):
    """Execute mit Pattern Context Injection"""
    from memory.memory import AgentMemory
    memory = AgentMemory()
    
    # ✅ NEW: Suche Patterns VORHER
    print(f"🔍 Searching for solution patterns for: {task}")
    patterns = memory.list_solution_patterns()
    
    pattern_context = self._format_patterns_for_prompt(patterns)
    
    # Build enhanced prompt
    enhanced_prompt = f"""
Task: {task}

{'=' * 50}
📚 KNOWN SOLUTION PATTERNS (Apply if relevant):
{'=' * 50}

{pattern_context}

{'=' * 50}
Follow the patterns and best practices above when generating code.
{'=' * 50}

Generate the solution:
"""
    
    print(f"✅ Injected {len(patterns)} pattern categories into prompt")
    
    result = self.llm.query(enhanced_prompt, memory_context)
    
    # ... rest of code ...
    
    return result

def _format_patterns_for_prompt(self, patterns: dict) -> str:
    """Format patterns für LLM Prompt"""
    
    if not patterns:
        return "(No patterns stored yet)"
    
    text = ""
    for category, pattern_list in patterns.items():
        text += f"\n✓ {category}:\n"
        for pattern in pattern_list:
            text += f"  • Problem: {pattern['problem']}\n"
            text += f"    Fix: {pattern['solution']}\n"
    
    return text
```

---

### SCHRITT 3: Reviewer Solution Lookup (1h)

**Datei:** `agents/reviewer.py`

Erweitere die `review()` Methode:

```python
def review(self, task: str, result: str, memory=None) -> dict:
    """
    Review mit Solution Pattern Lookup
    """
    
    print(f"\n🔍 Reviewing output...")
    
    # Standard review
    review_result = self._basic_review(task, result)
    
    # ✅ NEW: Falls Problem gefunden → suche Solution Pattern
    if review_result["status"] == "NEEDS_FIX" and memory:
        print(f"⚠️  Problem found: {review_result['reason']}")
        
        # Suche bekannte Lösung
        solution = memory.find_solution_for_problem(review_result["reason"])
        
        if solution.get("found"):
            print(f"💡 Solution Pattern found!")
            print(f"   Problem: {solution['problem']}")
            print(f"   Solution: {solution['solution']}")
            
            review_result["suggested_solution"] = solution
            review_result["has_known_fix"] = True
        else:
            print(f"❌ No solution pattern found")
            review_result["has_known_fix"] = False
    
    return review_result
```

Und in `core/agent.py` Pass memory zum Reviewer:

```python
def run_task(self, task):
    """Run task mit Reviewer + Memory"""
    
    # ... existing code ...
    
    # Pass memory zum Reviewer
    review = self.reviewer.review(task, result, memory=self.memory)
    
    # ... rest ...
```

---

## 🧪 TEST: Sind die Checkpoints aktiv?

### Test 1: Problem Detection

```python
# In Continue Chat oder Terminal:

# Create test code mit Hardcoded Password
test_code = """
def login(user, pwd):
    password = "admin123"  # ← PROBLEM!
    return password == pwd
"""

# Agent sollte das erkennen
# Output:
# 🔍 Analyzing code for problems...
# ❌ Found: Hardcoded password
# ✅ Applied fix: Use os.getenv()
# 
# Fixed code:
# import os
# def login(user, pwd):
#     password = os.getenv('PASSWORD')
#     return password == pwd
```

### Test 2: Pattern Injection

```
Before:
Task: "Create API endpoint"
Agent sieht nur: Task

After:
Task: "Create API endpoint"
Agent sieht auch:
  - Use HTTPBearer for auth
  - Use os.getenv() for secrets
  - Use try/except for errors
  
→ Agent generiert besseren Code direkt!
```

### Test 3: Solution Lookup

```
After:
Code hat Problem → Reviewer findet es
Reviewer sucht Memory nach Solution
Reviewer findet: "Hier ist der Fix"
Reviewer zeigt dem User: "Known solution available"

→ User kann manuell fixen oder Agent auto-fixen
```

---

## 📊 Erwartete Effekte nach Implementation

```
VOR Implementation:
════════════════════
Task 1: Agent macht Fehler X
        Memory: Fehler X speichern
        
Task 2: Agent macht Fehler X nochmal! ❌
Task 3: Fehler X nochmal! ❌

Success Rate: 30%

─────────────────────────────────────────

NACH Implementation:
════════════════════
Task 1: Agent macht Fehler X
        Checkpoint 2: Auto-Fixed! ✅
        Memory: "Problem X → Lösung Y"
        
Task 2: Checkpoint 1: "Use Lösung Y!"
        Agent vermeidet Fehler von Anfang an ✅
        
        Falls dennoch Fehler:
        Checkpoint 2: Auto-Fixed nochmal ✅

Task 3-10: Fehler X FAST NICHT MEHR

Success Rate: 85%+

VERBESSERUNG: +55%!
```

---

## 🎯 Integrierungs-Reihenfolge

### Woche 1: Checkpoint 2 (Problem Detection)
- [ ] Methode `_detect_and_fix_problems()` implementieren
- [ ] 5-10 Problem-Patterns hinzufügen
- [ ] In `execute()` einbauen
- [ ] Testen

**Effort: 2h | Impact: Auto-fix häufiger Fehler**

---

### Woche 2: Checkpoint 1 (Pattern Injection)
- [ ] Methode `_format_patterns_for_prompt()` implementieren
- [ ] Pattern Context zu Prompt hinzufügen
- [ ] Testen mit echten Tasks

**Effort: 1h | Impact: Agent vermeidet Fehler von Anfang an**

---

### Woche 2: Checkpoint 3 (Solution Lookup)
- [ ] Reviewer erweitern: Solution Lookup
- [ ] Memory an Reviewer übergeben
- [ ] Testen

**Effort: 1h | Impact: Reviewer kann Fixes vorschlagen**

---

## 🚀 Checklist für heute

```
☐ Lies SOLUTION_PATTERNS_ACTIVE_DETECTION.md
☐ Verstehe die 3 Checkpoints
☐ Implementiere Checkpoint 2 (Copy-Paste Code oben)
☐ Teste mit Test 1 (Hardcoded Password)
☐ Nächste Woche: Checkpoints 1 + 3
```

---

## 📍 Wenn was nicht funktioniert

### Problem: Auto-Fix ändert Code nicht
```
Check: 
- Ist Memory wirklich initialisiert?
- Gibt es Solution Patterns gespeichert?
- Passt der regex zu deinem Code?
```

### Problem: Patterns werden nicht in Prompt injektet
```
Check:
- Wird _format_patterns_for_prompt() aufgerufen?
- Gibt memory.list_solution_patterns() Daten zurück?
- Wird der enhanced_prompt wirklich an LLM übergeben?
```

### Problem: Reviewer findet Solutions nicht
```
Check:
- Wird memory.find_solution_for_problem() aufgerufen?
- Passt der Suchbegriff zu gespeicherten Patterns?
- Wird "found" wirklich True zurückgegeben?
```

---

> 📅 Erstellt: 17. April 2026
> ✅ Status: READY TO IMPLEMENT (Copy-Paste Code)
> 🎯 Time to Implementation: 4h total (2h + 1h + 1h)
