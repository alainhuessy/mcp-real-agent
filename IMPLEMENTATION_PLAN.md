# 📋 IMPLEMENTATION PLAN: Workspace Intelligence Tool
**Status:** In Entwicklung  
**Ziel:** Agent nutzt echte Project Data → Intelligente Pläne  
**Estimated Time:** 1-2 Stunden  
**Priority:** 🔴 HIGH

---

## 🎯 Plan Breakdown

### Phase 1: Workspace Intelligence Tool schreiben (30 Min)
- [x] Datei `tools/workspace.py` erstellen
- [ ] Funktionen:
  - `analyze_structure()` - Modul-Übersicht
  - `get_git_status()` - Repository Info
  - `read_requirements()` - Dependencies
  - `check_health()` - Code Quality
  - `analyze_project()` - Alles kombinieren

### Phase 2: MCP Server Integration (20 Min)
- [ ] Import `WorkspaceIntelligence` in `mcp_server.py`
- [ ] Handler `handle_agent_plan` anpassen
- [ ] Workspace-Context vor Planner übergeben
- [ ] Test: `agent_plan` mit Context

### Phase 3: Planner verbessern (20 Min)
- [ ] `agents/planner.py` System Prompt ergänzen
- [ ] Project Context in Prompt injizieren
- [ ] Bessere Task-Listen generieren

### Phase 4: Test & Validation (20 Min)
- [ ] Manuell testen in Continue
- [ ] Vergleich: Vorher vs. Nachher
- [ ] GitHub Commit

---

## 📊 Implementation Details

### Datei 1: tools/workspace.py (Neu)
**Größe:** ~80 Zeilen  
**Abhängigkeiten:** os, json, pathlib, subprocess  
**Funktionen:**
```
class WorkspaceIntelligence:
    - analyze_project() → dict (Hauptfunktion)
    - _analyze_structure() → dict (Module, Files)
    - _get_git_status() → dict (Git Info)
    - _read_requirements() → list (Dependencies)
    - _count_lines_of_code() → int (LOC)
    - _check_health() → dict (Errors, Warnings)
```

### Datei 2: mcp_server.py (Änderung)
**Größe der Änderung:** ~15 Zeilen  
**Punkte:**
- Import WorkspaceIntelligence
- Modifiziere `handle_agent_plan` Funktion
- Sammle Workspace-Daten
- Übergebe an Planner

### Datei 3: agents/planner.py (Verbesserung)
**Größe der Änderung:** ~10 Zeilen  
**Punkte:**
- Besserer System Prompt mit Kontext
- Workspace-Daten in Prompt injizieren
- Beispiele für spezifische Tasks

---

## 🚀 Kickoff

**Nächster Schritt:** Datei `tools/workspace.py` schreiben und integrieren

