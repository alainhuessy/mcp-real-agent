# Docstring Korrekturen - Umsetzungsplan

## Ziel
Vollständige, konsistente und korrekte Docstrings für alle Module im `core`-Verzeichnis gemäß PEP 257/NumPy/Google Style Conventions.

---

## Phase 1: Kritische Korrekturen (router.py)

- [ ] **`core/router.py`** - Router.route()
  - [ ] Args-Abschnitt ergänzen (`task: str`)
  - [ ] Returns-Abschnitt ergänzen (Typ: `str`, Werte: 'coder', 'rag', 'planner', 'chat')
  - [ ] Modus-Beschreibungen in Args hinzufügen

---

## Phase 2: Inkonsistenzen beheben (llm.py)

- [ ] **`core/llm.py`** - LLM.ask()
  - [ ] Args-Abschnitt vollständig: `model`, `prompt`, `system` dokumentieren
  - [ ] Returns-Abschnitt hinzufügen (str: Antwort oder Fehlermeldung)
  - [ ] Raises-Abschnitt hinzufügen (ConnectionError, requests.exceptions)
  - [ ] Sprachkonvention prüfen (Deutsch vs. Englisch konsistent halten)

- [ ] **`core/llm.py`** - LLM.get_model()
  - [ ] Args-Abschnitt ergänzen (`mode: str`)
  - [ ] Returns-Abschnitt ergänzen (str: Modellname oder Fallback)
  - [ ] Erklärung des Fallback-Verhaltens hinzufügen

- [ ] **`core/llm.py`** - load_models_from_config()
  - [ ] Tippfehler korrigieren: "dynmaisch" → "dynamisch"

---

## Phase 3: Tippfehler & Feinschliff (agent.py)

- [ ] **`core/agent.py`** - AgentOS.__init__()
  - [ ] Tippfehler korrigieren: "Intialisierungsschritte" → "Initialisierungsschritte"

- [ ] **`core/agent.py`** - AgentOS.run_loop()
  - [ ] Returns-Abschnitt ergänzen (None / keine Rückgabe, da endlosschleife)
  - [ ] Raises-Abschnitt ergänzen (KeyboardInterrupt bei Ctrl+C)

---

## Phase 4: Überprüfung aller Module

- [ ] **`core/__init__.py`** - Moduldokumentation prüfen ✅ (bereits OK)
- [ ] **`core/tools.py`** - Docstrings prüfen ✅ (bereits OK)
- [ ] **`core/logger.py`** - Docstrings prüfen ✅ (bereits OK)

---

## Quality Checklist

- [ ] Alle Docstrings verwenden konsistente Sprache (Deutsch oder Englisch)
- [ ] Alle Args sind dokumentiert mit Typ und Beschreibung
- [ ] Alle Returns sind dokumentiert mit Typ und Beschreibung
- [ ] Optional: Raises für Exceptions dokumentiert
- [ ] Optional: Beispiele in Docstrings vorhanden
- [ ] Kein Tippfehler in Docstrings
- [ ] Formatierung aller Docstrings einheitlich

---

## Geplante Umsetzung

1. **Step 1:** `router.py` anpassen (kritisch)
2. **Step 2:** `llm.py` anpassen (inkonsistent)
3. **Step 3:** `agent.py` Tippfehler korrigieren
4. **Step 4:** Finale Prüfung aller Dateien