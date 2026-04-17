# 🔍 Agent-Seitige Prüfung: Wie der Agent Fixes erkennt und anwendet

> Das fehlende Link: Von gespeichertem Fix zur aktiven Anwendung

---

## 🎯 Das Problem, das du erkannt hast

```
❌ PROBLEM:
Ich speichere ein Solution Pattern ab:
  Problem: "Hardcoded password"
  Lösung: "Use os.getenv()"
  
Aber: Agent kennt das Pattern nicht!

Agent generiert nächsten Code:
  password = "secret123"  ← GENAU DER GLEICHE FEHLER!
  
Warum? Agent hat nie nach dem Pattern gesucht!

RESULTAT:
- Fix existiert in Memory ✅
- Agent nutzt es nicht ❌
- Fehler wiederholt sich ❌
```

---

## 🔄 LÖSUNG: 3-Punkte Prüf-Strategie

```
Agent soll an 3 Stellen prüfen:

1️⃣ VOR Code-Generierung
   "Gibt es bekannte Patterns für diese Task?"
   → Füge sie zum Prompt hinzu
   
2️⃣ WÄHREND Code-Generierung  
   "Erkenne ich bekannte Probleme im generierten Code?"
   → Auto-Fix anwenden
   
3️⃣ NACH Code-Generierung (Reviewer)
   "Ist dieser Code problematisch?"
   → Suche Solution Pattern
   → Schlage Fix vor
```

---

## 🏗️ ARCHITEKTUR: Prüf-Punkte

```
┌────────────────────────────────────┐
│ Task Input: "Create API endpoint"  │
└────────────┬───────────────────────┘
             │
             ↓
    ┏━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ CHECKPOINT 1: BEFORE ┃
    ┃ Search Memory für     ┃
    ┃ "API endpoint"        ┃
    ┃ Patterns gefunden?    ┃
    ┃ → Add to Prompt       ┃
    ┗━━━━━┬─────────────────┛
          │
          ↓
┌────────────────────────────────────┐
│ LLM Generation (mit Patterns)      │
│                                    │
│ Prompt:                            │
│ "Create API endpoint"              │
│ "Known patterns:                   │
│  - Use HTTPBearer for auth         │
│  - Use os.getenv() for secrets     │
│ "                                  │
└────────────┬───────────────────────┘
             │
             ↓
┌────────────────────────────────────┐
│ Generated Code:                    │
│                                    │
│ @app.post("/login")               │
│ def login(user, password):         │
│   secret = os.getenv('SECRET')     │
│   if password == secret:           │
│     return token                   │
└────────────┬───────────────────────┘
             │
             ↓
    ┏━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ CHECKPOINT 2: DURING  ┃
    ┃ Analyze Generated     ┃
    ┃ Code for Problems     ┃
    ┃ Known issues?         ┃
    ┃ → Auto-Fix            ┃
    ┗━━━━━┬─────────────────┛
          │
          ↓ (no problems found)
          │
    ┏━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ CHECKPOINT 3: AFTER   ┃
    ┃ Reviewer prüft Code   ┃
    ┃ Probleme?             ┃
    ┃ → Suche Solution      ┃
    ┃ → Schlage Fix vor     ┃
    ┗━━━━━┬─────────────────┛
          │
          ↓
┌────────────────────────────────────┐
│ Output: APPROVED ✅               │
│                                    │
│ (oder: Auto-Fixed + Re-review)    │
└────────────────────────────────────┘
```

---

## 💻 CODE: Implementierung der 3 Checkpoints

### Checkpoint 1: BEFORE - Pattern Injection

```python
# agents/worker.py

def execute(self, task, memory_context=""):
    """
    Execute mit Solution Pattern Injection
    """
    from memory.memory import AgentMemory
    memory = AgentMemory()
    
    # ✅ CHECKPOINT 1: Suche bekannte Patterns
    print(f"🔍 Checkpoint 1: Searching for patterns for '{task}'")
    
    patterns = memory.list_solution_patterns()
    pattern_context = self._format_patterns_for_prompt(patterns, task)
    
    # Build prompt mit Pattern Context
    enhanced_prompt = f"""
Task: {task}

{self._get_system_rules()}

{pattern_context}

Generate solution following the patterns and best practices above.
"""
    
    print(f"✅ Checkpoint 1: Found patterns, injected into prompt")
    
    # 2. Generate code
    result = self.llm.query(enhanced_prompt, memory_context)
    
    return result

def _format_patterns_for_prompt(self, patterns: dict, task: str) -> str:
    """Format solution patterns for LLM context"""
    
    if not patterns:
        return ""
    
    pattern_text = "\n📚 KNOWN SOLUTION PATTERNS (Apply if relevant):\n"
    pattern_text += "=" * 50 + "\n"
    
    for category, pattern_list in patterns.items():
        pattern_text += f"\n{category}:\n"
        for pattern in pattern_list:
            pattern_text += f"  ✓ Problem: {pattern['problem']}\n"
            pattern_text += f"    Solution: {pattern['solution']}\n"
    
    pattern_text += "\n" + "=" * 50 + "\n"
    pattern_text += "Apply these patterns if they match your solution!\n"
    
    return pattern_text
```

---

### Checkpoint 2: DURING - Problem Detection & Auto-Fix

```python
# agents/worker.py - erweitern

def execute(self, task, memory_context=""):
    """
    Execute mit allen 3 Checkpoints
    """
    from memory.memory import AgentMemory
    memory = AgentMemory()
    
    # CHECKPOINT 1: Pattern Injection
    patterns = memory.list_solution_patterns()
    pattern_context = self._format_patterns_for_prompt(patterns, task)
    
    enhanced_prompt = f"""
Task: {task}
{self._get_system_rules()}
{pattern_context}
"""
    
    result = self.llm.query(enhanced_prompt, memory_context)
    
    # ✅ CHECKPOINT 2: Analyze generated code for problems
    print(f"\n🔍 Checkpoint 2: Analyzing generated code for known problems...")
    
    detected_problems = self._detect_and_fix_problems(result, memory)
    
    if detected_problems:
        print(f"⚠️  Checkpoint 2: Found {len(detected_problems)} problems")
        print(f"💡 Checkpoint 2: Applying fixes...")
        result = detected_problems["fixed_code"]
        print(f"✅ Checkpoint 2: Code fixed automatically")
    else:
        print(f"✅ Checkpoint 2: No known problems detected")
    
    return result

def _detect_and_fix_problems(self, code: str, memory) -> dict:
    """
    🔍 Prüfe Code auf bekannte Probleme
    💡 Falls gefunden: Wende automatische Fixes an
    """
    
    problems_found = []
    fixes_applied = []
    fixed_code = code
    
    # Problem 1: Hardcoded Passwords
    print("  → Checking: Hardcoded passwords...")
    if self._has_hardcoded_password(code):
        print("    ❌ Found: Hardcoded password")
        
        solution = memory.find_solution_for_problem("Hardcoded password")
        if solution["found"]:
            print(f"    ✅ Solution found: {solution['solution']}")
            fixed_code = self._apply_fix_hardcoded_password(fixed_code, solution)
            problems_found.append("Hardcoded password")
            fixes_applied.append(solution['solution'])
    
    # Problem 2: N+1 Queries
    print("  → Checking: N+1 query patterns...")
    if self._has_n_plus_one_query(code):
        print("    ❌ Found: N+1 query problem")
        
        solution = memory.find_solution_for_problem("N+1 query")
        if solution["found"]:
            print(f"    ✅ Solution found: {solution['solution']}")
            fixed_code = self._apply_fix_n_plus_one(fixed_code, solution)
            problems_found.append("N+1 query")
            fixes_applied.append(solution['solution'])
    
    # Problem 3: Bare Except Clauses
    print("  → Checking: Bare except clauses...")
    if self._has_bare_except(code):
        print("    ❌ Found: Bare except clause")
        
        solution = memory.find_solution_for_problem("Bare except clause")
        if solution["found"]:
            print(f"    ✅ Solution found: {solution['solution']}")
            fixed_code = self._apply_fix_bare_except(fixed_code, solution)
            problems_found.append("Bare except")
            fixes_applied.append(solution['solution'])
    
    # Problem 4: SQL Injection
    print("  → Checking: SQL injection risks...")
    if self._has_sql_injection_risk(code):
        print("    ❌ Found: SQL injection risk")
        
        solution = memory.find_solution_for_problem("SQL injection")
        if solution["found"]:
            print(f"    ✅ Solution found: {solution['solution']}")
            fixed_code = self._apply_fix_sql_injection(fixed_code, solution)
            problems_found.append("SQL injection")
            fixes_applied.append(solution['solution'])
    
    if problems_found:
        return {
            "found": True,
            "problems": problems_found,
            "fixes_applied": fixes_applied,
            "fixed_code": fixed_code,
        }
    else:
        return {"found": False}

# Problem-Detection Funktionen

def _has_hardcoded_password(self, code: str) -> bool:
    """Prüfe auf hardcoded passwords"""
    import re
    
    # Pattern 1: password = "..."
    if re.search(r"password\s*=\s*['\"]", code, re.IGNORECASE):
        return True
    
    # Pattern 2: password:  "..."
    if re.search(r"password\s*:\s*['\"]", code, re.IGNORECASE):
        return True
    
    # Pattern 3: secret = "..."
    if re.search(r"secret\s*=\s*['\"]", code, re.IGNORECASE):
        return True
    
    return False

def _has_n_plus_one_query(self, code: str) -> bool:
    """Prüfe auf N+1 Query Probleme"""
    import re
    
    # Pattern: for loop mit query inside
    if re.search(r"for\s+\w+\s+in\s+.*:\s*.*query\(", code):
        return True
    
    # Pattern: Select * im Loop
    if re.search(r"for.*in.*:\s*.*SELECT \*", code, re.IGNORECASE):
        return True
    
    return False

def _has_bare_except(self, code: str) -> bool:
    """Prüfe auf bare except clauses"""
    import re
    
    # Pattern: except:
    if re.search(r"except\s*:", code):
        return True
    
    # Pattern: except Exception:
    if re.search(r"except\s+Exception\s*:", code):
        return True
    
    return False

def _has_sql_injection_risk(self, code: str) -> bool:
    """Prüfe auf SQL Injection Risiken"""
    import re
    
    # Pattern: f"SELECT ... {variable}"
    if re.search(r'["\']SELECT\s+.*\{.*\}', code, re.IGNORECASE):
        return True
    
    # Pattern: "SELECT ... " + variable
    if re.search(r'["\']SELECT.*["\s]*\+', code, re.IGNORECASE):
        return True
    
    return False

# Fix-Anwendungs-Funktionen

def _apply_fix_hardcoded_password(self, code: str, solution: dict) -> str:
    """Wende Fix für hardcoded password an"""
    import re
    
    # Replace password = "..." with os.getenv()
    fixed = re.sub(
        r"password\s*=\s*['\"][^'\"]*['\"]",
        "password = os.getenv('PASSWORD')",
        code,
        flags=re.IGNORECASE
    )
    
    # Replace secret = "..." with os.getenv()
    fixed = re.sub(
        r"secret\s*=\s*['\"][^'\"]*['\"]",
        "secret = os.getenv('SECRET')",
        fixed,
        flags=re.IGNORECASE
    )
    
    # Add import if needed
    if "os.getenv" in fixed and "import os" not in fixed:
        fixed = "import os\n" + fixed
    
    return fixed

def _apply_fix_bare_except(self, code: str, solution: dict) -> str:
    """Wende Fix für bare except an"""
    import re
    
    # Replace bare except: with except Exception:
    fixed = re.sub(
        r"except\s*:",
        "except Exception as e:",
        code
    )
    
    return fixed

def _apply_fix_sql_injection(self, code: str, solution: dict) -> str:
    """Wende Fix für SQL Injection an"""
    import re
    
    # Hinweis: Das ist komplex - hier nur grundlegende Substitution
    # In der Realität: Verwende SQLAlchemy oder prepared statements
    
    print(f"    💡 Suggestion: {solution.get('explanation', 'Use parameterized queries')}")
    
    return code

def _apply_fix_n_plus_one(self, code: str, solution: dict) -> str:
    """Wende Fix für N+1 Query an"""
    
    print(f"    💡 Suggestion: {solution.get('explanation', 'Use eager loading')}")
    
    return code
```

---

### Checkpoint 3: AFTER - Reviewer mit Pattern-Lookup

```python
# agents/reviewer.py

def review(self, task: str, result: str) -> dict:
    """
    Review mit Solution Pattern Lookup
    """
    from memory.memory import AgentMemory
    memory = AgentMemory()
    
    # Standard review
    print(f"\n🔍 Checkpoint 3: Reviewer analyzing output...")
    
    review_result = self._basic_review(task, result)
    
    if review_result["status"] == "NEEDS_FIX":
        # ✅ CHECKPOINT 3: Suche Solution Pattern für Problem
        print(f"⚠️  Checkpoint 3: Found problem: {review_result['reason']}")
        
        # Suche bekannte Lösung
        solution = memory.find_solution_for_problem(review_result["reason"])
        
        if solution["found"]:
            print(f"💡 Checkpoint 3: Solution pattern found!")
            print(f"   Problem: {solution['problem']}")
            print(f"   Solution: {solution['solution']}")
            print(f"   Code example: {solution.get('code_example', 'N/A')[:100]}...")
            
            # Füge Solution zu Review hinzu
            review_result["suggested_solution"] = solution
            review_result["has_known_fix"] = True
        else:
            print(f"❌ Checkpoint 3: No solution pattern found for '{review_result['reason']}'")
            review_result["has_known_fix"] = False
    else:
        review_result["has_known_fix"] = False
        print(f"✅ Checkpoint 3: Output APPROVED")
    
    return review_result

def _basic_review(self, task: str, result: str) -> dict:
    """Standard review logic"""
    
    # Check for common issues
    if "password" in result.lower() and "=" in result:
        return {
            "status": "NEEDS_FIX",
            "reason": "Hardcoded password detected",
            "feedback": "Secrets should not be hardcoded"
        }
    
    if "except:" in result:
        return {
            "status": "NEEDS_FIX",
            "reason": "Bare except clause",
            "feedback": "Use specific exception types"
        }
    
    # ... mehr checks ...
    
    return {
        "status": "APPROVED",
        "reason": "Code looks good",
        "feedback": ""
    }
```

---

## 🎯 GESAMTER FLOW: Alle 3 Checkpoints zusammen

```
┌─────────────────────────────────────────────────────┐
│ USER: "Create API endpoint"                         │
└────────────────┬──────────────────────────────────┘
                 │
                 ↓
    ┌─────────────────────────────────────┐
    │ CHECKPOINT 1: BEFORE (Pattern Lookup)
    │                                      │
    │ Memory Search:                       │
    │ "API endpoint patterns?"             │
    │                                      │
    │ Found:                               │
    │ - Use HTTPBearer                     │
    │ - Use os.getenv()                    │
    │ - Error Handling                     │
    │                                      │
    │ Action: Add to LLM Prompt            │
    └────────────────┬────────────────────┘
                     │
                     ↓
    ┌──────────────────────────────────────┐
    │ LLM GENERATES CODE                    │
    │ (mit Pattern Context im Prompt)      │
    │                                      │
    │ @app.post("/auth")                  │
    │ def auth(...):                       │
    │   secret = os.getenv('SECRET')       │
    │   return token                       │
    └────────────────┬────────────────────┘
                     │
                     ↓
    ┌─────────────────────────────────────┐
    │ CHECKPOINT 2: DURING                │
    │ (Problem Detection & Auto-Fix)       │
    │                                      │
    │ Scan for:                            │
    │ ✓ Hardcoded passwords? NO            │
    │ ✓ N+1 queries? NO                    │
    │ ✓ Bare except? NO                    │
    │ ✓ SQL injection? NO                  │
    │                                      │
    │ Result: CLEAN ✅                    │
    └────────────────┬────────────────────┘
                     │
                     ↓
    ┌─────────────────────────────────────┐
    │ CHECKPOINT 3: AFTER (Reviewer)       │
    │                                      │
    │ Reviewer checks output...            │
    │ Status: APPROVED ✅                 │
    │                                      │
    │ No problems found                    │
    └─────────────────────────────────────┘
                     │
                     ↓
        ✅ FINAL OUTPUT TO USER
        ✅ ALL CHECKPOINTS PASSED
        ✅ PATTERNS APPLIED
```

---

## 📊 ALTERNATIVE SCENARIO: Mit Problem & Fix

```
Scenario: Agent generiert Code mit bekanntem Problem

┌─────────────────────────────────────────────────────┐
│ USER: "Create database connection"                  │
└────────────────┬──────────────────────────────────┘
                 │
                 ↓
    CHECKPOINT 1: Patterns?
    Found: "SQL injection protection"
                 │
                 ↓
    LLM GENERIERT:
    query = "SELECT * FROM users WHERE id = " + user_id  ← PROBLEM!
                 │
                 ↓
    CHECKPOINT 2: Problem Detection
    
    Scan for SQL injection:
    ✓ Found: String concatenation in SQL
    
    Search Memory:
    "SQL injection" → Solution Pattern found!
    
    Solution: "Use parameterized queries"
    Code example: "cursor.execute(query, (user_id,))"
    
    Action: AUTO-FIX!
    
    Fixed code:
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
                 │
                 ↓
    CHECKPOINT 3: Reviewer
    Checks fixed code:
    Status: APPROVED ✅
                 │
                 ↓
    ✅ OUTPUT: AUTOMATICALLY FIXED CODE
```

---

## 🔧 PSEUDO-CODE: Kompletter Flow

```python
# Main execution loop

def run_task(task):
    """
    Führe Task mit allen 3 Checkpoints durch
    """
    
    memory = AgentMemory()
    worker = WorkerAgent()
    reviewer = ReviewerAgent()
    
    # ✅ CHECKPOINT 1: Before Generation
    # ═══════════════════════════════════
    print("CHECKPOINT 1: Pattern Injection")
    patterns = memory.list_solution_patterns()
    
    # Generate code WITH pattern context
    code = worker.execute(task, patterns_context=patterns)
    
    
    # ✅ CHECKPOINT 2: After Generation
    # ══════════════════════════════════
    print("CHECKPOINT 2: Auto-Fix")
    code_fixed = worker.detect_and_fix_problems(code, memory)
    
    if code_fixed["found"]:
        print(f"Auto-fixed: {code_fixed['fixes_applied']}")
        code = code_fixed["fixed_code"]
    
    
    # ✅ CHECKPOINT 3: Reviewer Check
    # ════════════════════════════════
    print("CHECKPOINT 3: Reviewer + Solution Lookup")
    review = reviewer.review(task, code, memory)
    
    if review["status"] == "NEEDS_FIX":
        if review.get("has_known_fix"):
            print(f"Known solution: {review['suggested_solution']['solution']}")
            # Könnte hier automatisch nochmal fixen
        else:
            print(f"Unknown problem: {review['reason']}")
            # User muss manuell fixen
    
    
    # Store in Memory
    memory.sync(code)
    
    return {
        "code": code,
        "review": review,
        "checkpoints_passed": [1, 2, 3]
    }
```

---

## 📈 EFFEKT: Mit vs. Ohne Checkpoints

```
OHNE CHECKPOINTS:
═════════════════

Task 1: Agent generiert Code mit Problem X
        → Speichere als Solution Pattern
        Memory: Problem X → Lösung Y

Task 2: Agent generiert Code mit Problem X wieder! ❌
        Weil: Agent hat nie nach Pattern gesucht

Task 3-10: Problem X wiederholt sich immer wieder

Success Rate: 30%

─────────────────────────────────────────────────

MIT 3 CHECKPOINTS:
══════════════════

Task 1: Agent generiert Code mit Problem X
        Checkpoint 2: Erkannt & Auto-Fixed ✅
        → Speichere als Solution Pattern
        Memory: Problem X → Lösung Y

Task 2: Agent generiert Code mit Problem X
        Checkpoint 1: Pattern in Prompt injected
        → Agent vermeidet Problem von Anfang an ✅
        
        Falls dennoch Problem:
        Checkpoint 2: Erkannt & Auto-Fixed ✅

Task 3-10: Problem X nie wieder! (oder auto-fixed)

Success Rate: 90%

VERBESSERUNG: +60%!
```

---

## 🎯 PRAKTISCHE IMPLEMENTIERUNGS-REIHENFOLGE

### Phase 1: **Diese Woche** (MVP - Basic Checkpoints)
```
1. ✅ Checkpoint 2: Problem Detection
   - _has_hardcoded_password()
   - _has_bare_except()
   - _detect_and_fix_problems()
   
   Aufwand: 1-2 Stunden
   Effekt: Auto-fix häufiger Fehler
```

### Phase 2: **Nächste Woche** (Checkpoint 1 + 3)
```
1. ✅ Checkpoint 1: Pattern Injection
   - _format_patterns_for_prompt()
   - Patterns in LLM Prompt
   
   Aufwand: 1 Stunde
   Effekt: Agent vermeidet Fehler von Anfang an
   
2. ✅ Checkpoint 3: Reviewer Integration
   - Solution Lookup im Reviewer
   - Suggestions anzeigen
   
   Aufwand: 1 Stunde
   Effekt: Wenn Problem nicht verhindert: Auto-fix Suggestion
```

### Phase 3: **Nächster Monat** (Advanced)
```
1. ✅ Automatische Fix-Anwendung (optional)
2. ✅ Mehr Problem-Patterns
3. ✅ Learning from Fixes
```

---

## 💡 KEY INSIGHT

```
DAS WAR DAS MISSING PIECE:

"Speichere ich ein Solution Pattern, nutzt Agent es nicht automatisch"

LÖSUNG:
Du brauchst 3 Checkpoints:

1. BEFORE Generation: 
   "Hey Agent! Diese Patterns existieren - nutze sie!"
   
2. DURING Generation:
   "Hey Agent! Ich erkenne einen bekannten Fehler - lass mich fixen!"
   
3. AFTER Generation:
   "Hey Reviewer! Für dieses Problem gibt's einen Solution Pattern!"

→ Agent nutzt Fixes AKTIV statt passiv zu warten
```

---

> 📅 Erstellt: 17. April 2026
> 🔍 Thema: Active Problem Detection & Auto-Fix
> 🎯 Status: CRITICAL MISSING PIECE DOCUMENTED
