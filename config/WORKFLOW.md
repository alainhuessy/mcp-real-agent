# Agent OS v2.1 — Systematic Workflow & Execution Protocol

## Überblick

Dieser Workflow definiert das **strukturierte Vorgehen** des Agents bei jedem Task.
Verhindert chaotisches Vorgehen und stellt sicher, dass der Agent systematisch arbeitet.

---

## WORKFLOW OVERVIEW

```
┌────────────────────────────────────────────────────────────┐
│ TASK EINGEGEBEN                                            │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ PHASE 1: ANALYSE     │
            │ (5-10 min)           │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ PHASE 2: PLANUNG     │
            │ (5-15 min)           │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ PHASE 3: EXECUTION   │
            │ (10-∞ min)           │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ PHASE 4: VERIFICATION│
            │ (5-15 min)           │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ PHASE 5: REPORTING   │
            │ (2-5 min)            │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ ✅ TASK COMPLETE     │
            └──────────────────────┘
```

---

## PHASE 1: TASK ANALYSIS

### Ziel
Vollständiges Verständnis der Anforderung BEVOR Action genommen wird

### Checklist

```
1. Task Description analysieren
   ├─ Primären Goal identifizieren
   ├─ Success Criteria definieren
   └─ Constraints/Limits verstehen

2. Context laden
   ├─ Ähnliche Tasks aus Memory suchen
   ├─ Relevante Dokumente/Code lesen
   └─ Abhängigkeiten identifizieren

3. Prerequisites checken
   ├─ Tools verfügbar?
   ├─ Dependencies installiert?
   ├─ Permissions OK?
   └─ API Keys vorhanden?

4. Risk Assessment
   ├─ Potenzielle Probleme?
   ├─ Fallback Plans?
   ├─ Reversibility (kann es rückgängig gemacht werden)?
   └─ Safety Concerns?

5. Clarification (falls nötig)
   ├─ Wenn unklar → Fragen stellen
   ├─ Annahmen explizit nennen
   └─ NICHT: Zurates raten
```

### Output
**Analysis Document** (intern):
```
TASK: [Original Goal]

SUCCESS CRITERIA:
- [ ] Kriterium 1
- [ ] Kriterium 2

CONTEXT:
- Ähnliche Tasks: [Link zu Memory]
- Dependencies: [Was ist nötig]

RISKS:
- Risk 1: Mitigation Strategy
- Risk 2: Mitigation Strategy

ASSUMPTIONS:
- Annahme 1
- Annahme 2

CONSTRAINTS:
- Constraint 1
- Constraint 2
```

---

## PHASE 2: PLANNING

### Ziel
Zerlege komplexe Tasks in umsetzbare Sub-Steps

### Für Small Tasks (<30 min)
```
✅ Analyse genügt
❌ Ausführliche Planung nicht nötig

Vorgehen:
  1. Analysis direkt nutzen
  2. Direkt zu Phase 3
```

### Für Medium Tasks (30 min - 3h)
```
PFLICHT-Planung:

1. Main Steps definieren
   └─ Meist 3-5 Schritte

2. Subtasks identifier
   └─ Jeder Main Step in kleine Teile

3. Dependencies katalogisieren
   └─ Was hängt von was ab?

4. Zeit-Schätzung
   └─ Grobe Schätzung pro Step
```

### Für Large Tasks (>3h)
```
AUSFÜHRLICHE Planung:

1. Architecture Decision Document (ADD)
   ├─ Design Choices
   ├─ Alternativen + warum nicht
   └─ Trade-offs

2. Detaillierter Execution Plan
   ├─ Alle Steps numeriert
   ├─ Abhängigkeiten mapped
   ├─ Zeitschätzung pro Step
   └─ Rollback Procedures

3. Success Metrics
   ├─ How to measure success
   ├─ Performance Targets
   └─ Quality Gates

4. Risk Mitigation
   ├─ Identifizierte Risks
   ├─ Mitigation Strategy pro Risk
   └─ Escalation Path
```

### Output Format
```markdown
# Execution Plan: [Task Title]

## Top-Level Steps
1. [ ] Step 1: Description
2. [ ] Step 2: Description
3. [ ] Step 3: Description

## Details

### Step 1: Description
- Sub-step 1.1
- Sub-step 1.2
  - Details
- Dependencies: None

**Timeline**: ~X minutes

### Step 2: ...
...

## Risks & Mitigations
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Rollback Plan
If failure at step X: [rollback procedure]
```

---

## PHASE 3: EXECUTION

### Principle: Structured Execution

```
WÄHREND Ausführung:
  
  FOR EACH Step:
    1. Schritt verstehen
    2. Prerequisites prüfen
    3. Aktion durchführen
    4. Output überprüfen
    5. ✓ oder ✗ → nächster Schritt oder error handling
    6. Todo-List aktualisieren
```

### Detailliertes Vorgehen

#### Step 3.1: Setup
```python
# Vor jedem Sub-Task:
1. Todo-List aktualisieren (as in-progress)
2. Workspace context laden
3. Prerequisites validate
4. Backup machen (falls sinnvoll)
```

#### Step 3.2: Execution
```python
# Während Sub-Task:
1. Code schreiben/Aktion durchführen
2. Nach jedem Änderung testen
3. Wenn error: 
   - Debug durchführen
   - Dokumentieren
   - Alternative versuchen
4. Fortschritt trackten
```

#### Step 3.3: Validation
```python
# Nach jedem Sub-Task:
1. Erwartetes Ergebnis überprüfen
2. Keine unerwarteten Side-Effects?
3. Tests bestanden?
4. Performance OK?
```

#### Step 3.4: Progress Tracking
```python
# Nach jedem Step:
- Todo-List updaten
- Status: ✅ completed
- Notes: Was hat funktioniert?
- Issues: Probleme dokumentieren
```

### Error Handling

```
WENN Error passiert:

1. PAUSE execution
2. Analyze (was ist schief gelaufen?)
3. Vorbereitung (kann ich das fixen?)
4. TRY:
   a. Problem diagn agnosieren
   b. Root cause finden
   c. Fix implementieren
   d. Test again
5. IF erfolgreich:
   - Continue
6. ELSE IF recoverable:
   - Alternative versuchen
7. ELSE:
   - Explicitly report + HALT
```

### Output
Live-Status auf Todo-List + Konsolen-Output

---

## PHASE 4: VERIFICATION

### Comprehensive Testing

```
BEI jedem Feature/Change:

1. FUNCTIONAL Testing
   ├─ Happy Path: funktioniert?
   ├─ Error Cases: exceptions handled?
   └─ Edge Cases: boundary tests?

2. INTEGRATION Testing
   ├─ Mit anderen komponenten OK?
   ├─ Keine regressions?
   └─ Data consistency?

3. PERFORMANCE Check
   ├─ Schnell genug?
   ├─ Memory usage OK?
   └─ Keine n+1 queries?

4. CODE Quality
   ├─ Pylint/Flake8 pass?
   ├─ Type hints OK?
   ├─ Documentation present?
   └─ No hardcoded values?

5. SECURITY Audit
   ├─ Keine secrets exposed?
   ├─ Input validation OK?
   ├─ Permissions correct?
   └─ No SQL injection etc?
```

### Test Coverage Minimum
```
✅ MINIMUM standar:
   - 80% code coverage
   - Alle public functions haben tests
   - Error cases sind geteststet

⭐ GOLD standard:
   - 95%+ coverage
   - Integration tests
   - Performance benchmarks documented
```

### Verification Checklist
```
[ ] Alle Success Criteria erfüllt?
[ ] Tests bestanden (>80% coverage)?
[ ] Keine regressions?
[ ] Performance OK?
[ ] Code Review ready?
[ ] Documentation complete?
[ ] Keine security issues?
```

---

## PHASE 5: REPORTING

### Format

```markdown
# Task Completion Report

## Task
[Original Request]

## Status
✅ COMPLETED / 🟡 PARTIAL / ❌ FAILED

## What Was Done
- Schritt 1: Beschreibung + Result
- Schritt 2: Beschreibung + Result
- ...

## Outcome
[Kurze zusammenfassung]

## Tests
- Pytest: 53/53 passed ✅
- Coverage: 95% ✅
- No regressions: ✅

## Files Changed
- file1.py: +50 lines, -10 lines
- file2.py: new file
- tests/: +200 lines tests

## Key Decisions
1. Decision 1: Warum diese Choice?
2. Decision 2: Trade-offs?

## Known Issues / Limitations
- Issue 1: Wird später gefixt
- Limitation 1: Bei >10K items langsam

## Documentation
- Changed: docs/API.md
- Added: docs/WORKFLOW.md

## Next Steps
1. [ ] Integration in CI/CD
2. [ ] Performance monitoring
3. [ ] User documentation

## Learning
- Insight 1: Für zukünftige Tasks relevant
- Insight 2: Pattern erkannt

---
Generated: [timestamp]
```

### Summary Template
```
🎯 TASK: [Zusammenfassung in 1 Satz]

✅ STATUS: [DONE / IN PROGRESS / FAILED]

📊 METRICS:
   - Tests: X/Y passed
   - Coverage: Z%
   - Time: ~H min

🔑 KEY RESULT:
   [Was wurde genau erreicht]

📝 NOTES:
   - Important point 1
   - Important point 2
```

---

## WORKFLOW INTEGRATION WITH TODO-LIST

### Todo-List Management

```python
# INITIALIZATION (Anfang des Tasks)
1. CreateTodoList("Task Name", [
    "Phase 1: Analyze requirements",
    "Phase 2: Create plan",
    "Phase 3: Execute steps",
    "Phase 4: Test everything",
    "Phase 5: Document & report"
])

# DURING EXECUTION (während Task läuft)
for step in execution_plan:
    mark_todo_inprogress(step)
    execute(step)
    mark_todo_completed(step)  # ← WICHTIG: sofort nach completion!

# COMPLETION (am Ende)
report(todos)  # Zeige alle completed todos
```

### Status Update Frequency
```
- Nach Phase 1: "Analyzed, ready to plan"
- Nach Phase 2: "Plan ready, starting execution"
- Nach Phase 3: "Execution complete, verifying"
- Nach Phase 4: "Verified, preparing report"
- Nach Phase 5: "✅ DONE"
```

---

## SPECIAL CASES

### Multi-Agent Coordination
```
WENN mehrere Agents zusammenarbeiten:

1. DEFINE Interfaces klar
   └─ Input/Output contracts

2. SEQUENCE die Arbeit
   └─ Agent A → Agent B → Agent C

3. HANDOFF Dokumentieren
   └─ Jede Handoff wird logged

4. ERROR HANDLING
   └─ Was passiert wenn An Agent A fehlschlägt?
```

### Long-Running Tasks (>1h)
```
VORGEHEN:
  1. Teile auf mehrere Phasen
  2. Speicher zustand nach jedem Phase
  3. Kann unterbrochen + resumed werden
  4. Checkpoints every 15 min
  
RECOVERY:
  - State ist persistent
  - Von Checkpoint weitermachen
  - Kein Neustart von Anfang
```

### Decision Points
```
WENN Entscheidung nötig ist:

1. Analyze alternatives
2. List trade-offs
3. State "I recommend X because..."
4. Wait für user input (wenn nicht klar)
5. Execute chosen path
```

---

## METRICS & CONTINUOUS IMPROVEMENT

### Track These
```
PER TASK:
  - Time taken
  - Errors encountered
  - Re-tries needed
  - Coverage achieved
  - Pattern matched?

WEEKLY:
  - Avg execution time
  - Error rate
  - Test coverage trend
  - User satisfaction
```

### Learning Loop
```
EACH TASK:
  1. What went well?
  2. What could be better?
  3. New patterns learned?
  4. Update memories/rules
  5. Share insights
```

---

## Summary: The 7-Step Loop

```
1. UNDERSTAND task clearly
2. LOAD context from memory
3. PLAN approach (if complex)
4. EXECUTE systematically
5. VERIFY thoroughly
6. TEST extensively
7. REPORT & LEARN
```

**Duration**: 10 min (simple) to 8h+ (complex)
**Principle**: Quality > Speed, always

---

## Checklist: Ready to Execute?

```
BEFORE Starting:
  ☐ Task is understood
  ☐ Context loaded
  ☐ Prerequisites ready
  ☐ Risks identified
  ☐ Plan in place (if needed)

DURING Execution:
  ☐ Following plan or have good reason to deviate
  ☐ Documenting progress
  ☐ Testing as I go
  ☐ Handling errors gracefully

BEFORE Completing:
  ☐ All success criteria met
  ☐ Tests passing
  ☐ Documentation updated
  ☐ Report ready
  ☐ Learning captured
```

**You're ready to start when ALL boxes are ☐** ✓
