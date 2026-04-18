---
title: "🎯 Dynamic Configuration System für Agent OS v2.1"
subtitle: "Zentrale Verwaltung aller Ollama Konfigurationen"
date: 2026-04-18
---

# 🎯 Dynamic Configuration System — Agent OS v2.1

## ✨ Überblick

Das Problem war: **Mehrere YAML-Dateien zu Test-Zwecken = Synchronisationsprobleme!**

- Continue liest `config.yaml` ✅
- Aber MCP-Server hatte hardcodierte Models ❌
- Verschiedene Profile waren nicht koordiniert ❌

---

## ✅ **GELÖST: Dynamisches System**

### 1️⃣ **Core LLM — Lädt Models aus config.yaml**

**Datei:** [`core/llm.py`](../core/llm.py)

```python
# ✅ JETZT: Dynamisch laden!
MODELS = load_models_from_config()

# ✅ Folge: Immer synchronisiert mit config.yaml
# ✅ Fallback: Wenn config.yaml nicht gefunden → Defaults
# ✅ Automatisch: Beim Start ohne Neustart des Codes
```

**Wie es funktioniert:**

```
┌─────────────────────────────────────────────────────────┐
│  .continue/agents/config.yaml (aktiv)                 │
│  - agent: devstral-rtx3090:latest                      │
│  - coder: qwen2.5-coder:14b                            │
│  - qwen-power: devstral-small-2:24b                    │
│  - ...                                                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼ (beim Start)
        ┌────────────────────────────┐
        │  load_models_from_config() │
        │  (in core/llm.py)          │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  MODELS = {...}            │
        │  (dynamisch geladen)        │
        └────────────┬───────────────┘
                     │
        ┌────────────┴──────────────────────┐
        │                                   │
        ▼                                   ▼
    ┌─────────────┐               ┌──────────────────┐
    │ MCP-Server  │               │ Continue IDE     │
    │ nutzt diese │               │ nutzt diese      │
    │ Models ✅   │               │ Models ✅        │
    └─────────────┘               └──────────────────┘
         (Synchronisiert!)
```

---

### 2️⃣ **Config Manager — Zentrale Verwaltung**

**Datei:** [`config_manager.py`](../config_manager.py)

Ein Kommandozeilen-Tool zum Verwalten aller Konfigurationen:

```bash
# Liste alle Profile auf
python3 config_manager.py --list

# Zeige aktives Profil
python3 config_manager.py --active

# Wechsel zu RTX 3090 Profil
python3 config_manager.py --switch rtx3090-optimized

# Synchronisiere MCP Agent mit Continue
python3 config_manager.py --sync
```

#### Verfügbare Profile:

| Profil | Datei | Models | Best für | Status |
|--------|-------|--------|----------|--------|
| **rtx3090-optimized** | `config-rtx3090-optimized.yaml` | 5 | Daily dev, RTX 3090 | ✅ EMPFOHLEN |
| **complete** | `config-complete.yaml` | 7 | Alle Modelle testen | ✅ Verfügbar |
| **balanced** | `config-top-tier.yaml` | 2 | Schnelle, stabile Entwicklung | ✅ Verfügbar |

---

### 3️⃣ **Das Problem Gelöst: SYNCHRONISATION**

#### VORHER (Hardcoded - ❌ PROBLEMATISCH):

```python
# core/llm.py - HARDCODED
MODELS = {
    "agent": "llama3.1:8b",        # ❌ ALT!
    "coder": "llama3.1:8b",        # ❌ ALT!
}

# .continue/agents/config.yaml - NEU
models:
  - name: agent
    model: devstral-rtx3090:latest # ✅ NEU!
```

**Problem:** 
- Continue zeigt `devstral-rtx3090` ✅
- MCP-Server nutzt `llama3.1` ❌
- **MISMATCH!**

#### NACHHER (Dynamisch - ✅ SYNCHRON):

```python
# core/llm.py - DYNAMISCH
MODELS = load_models_from_config()  # ✅ Liest aus config.yaml!

# .continue/agents/config.yaml (Eine Quelle der Wahrheit!)
models:
  - name: agent
    model: devstral-rtx3090:latest
```

**Lösung:**
- Ein einziger Ort für alle Modell-Definitionen 📍
- Automatisch synchronisiert zwischen Continue + MCP 🔄
- Kein Hardcoding mehr ❌
- Einfaches Profil-Wechseln 🔌

---

## 🚀 **Quick-Start**

### Schritt 1: Wechsel zu RTX 3090 Profil

```bash
cd /mnt/6724D393605CE580/Linux/LLM_Projekte/Github/mcp-real-agent
python3 config_manager.py --switch rtx3090-optimized
```

**Output:**
```
📦 Backup erstellt: config-backup-1776515069.yaml
✅ Profil 'rtx3090-optimized' aktiv!
       📊 Models in this Profile        
┌────────┬──────────────────────────┐
│ Name   │ Model                    │
├────────┼──────────────────────────┤
│ agent  │ devstral-rtx3090:latest  │
│ coder  │ qwen2.5-coder:14b        │
└────────┴──────────────────────────┘
```

### Schritt 2: Starte MCP-Server

```bash
python3 mcp_server.py
```

Der MCP-Server lädt automatisch die Models aus `config.yaml` 💡

```
✅ Model geladen: agent → devstral-rtx3090:latest
✅ Model geladen: coder → qwen2.5-coder:14b
✅ Model geladen: qwen-power → devstral-small-2:24b
```

### Schritt 3: Starte Continue

```bash
continue dev
```

Continue nutzt dieselben Models! 🎉

---

## 📊 **Technische Details**

### Wie `load_models_from_config()` funktioniert:

```python
def load_models_from_config() -> dict:
    """Lädt Models dynmaisch aus .continue/agents/config.yaml"""
    
    # 1. Suche config.yaml (mehrere Fallbacks)
    config_path = Path.home() / ".continue" / "agents" / "config.yaml"
    
    if not config_path.exists():
        # → Try local project path
        # → Try absolute paths
        # → Use defaults if not found
    
    # 2. Parse YAML
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # 3. Extract models
    models_list = config.get('models', [])
    
    # 4. Return dict
    return {model['name']: model['model'] for model in models_list}
```

### Fallback-Mechanismus:

Wenns config.yaml nicht gefunden wird:

```python
def _get_default_models() -> dict:
    return {
        "agent": "devstral-rtx3090:latest",
        "coder": "qwen2.5-coder:14b",
        # ... etc
    }
```

---

## 🎯 **Workflow für Profil-Wechsel**

```bash
# 1. Liste alle Profile auf
python3 config_manager.py --list

# 2. Wechsel zu gewünschtem Profil
python3 config_manager.py --switch rtx3090-optimized

# 3. Verify (optional)
python3 config_manager.py --active

# 4. Sync MCP Agent (optional)
python3 config_manager.py --sync

# 5. Starte Dienste neu (optional)
python3 mcp_server.py
continue dev
```

---

## ⚙️ **Für Entwickler**

### Neue Model hinzufügen

Bearbeite einfach `config.yaml` (oder ein Profil):

```yaml
models:
  - name: my-new-model
    title: "My Awesome Model"
    model: my-awesome-model:latest
    apiBase: "http://localhost:11434"
    contextLength: 32000
```

Der MCP-Server lädt es automatisch beim nächsten Start! 🚀

### Neues Profil erstellen

1. Erstelle neue `config-my-profile.yaml`
2. Registriere in `config_manager.py`:

```python
CONFIG_PROFILES = {
    # ... existing ...
    "my-profile": {
        "file": "config-my-profile.yaml",
        "description": "My Custom Profile",
        "models": 5,
        "best_for": "My use case"
    }
}
```

3. Nutze: `python3 config_manager.py --switch my-profile`

---

## 🔍 **Troubleshooting**

### MCP-Agent lädt die Models nicht?

```bash
# 1. Check aktuelles Profil
python3 config_manager.py --active

# 2. Sync MCP Agent
python3 config_manager.py --sync

# 3. Manuell check
python3 << 'EOF'
from core.llm import MODELS
print(MODELS)
EOF
```

### Models nicht in config.yaml?

```bash
# Überprüfe die Datei
cat .continue/agents/config.yaml | grep "- name:"

# Sollte Ausgabe zeigen wie:
#   - name: agent
#   - name: coder
#   etc.
```

### Config Backup wiederherstellen?

```bash
# Backups sind in .continue/agents/
ls -la .continue/agents/config-backup-*.yaml

# Restore
cp .continue/agents/config-backup-<timestamp>.yaml .continue/agents/config.yaml
```

---

## 📈 **Status nach Implementierung**

| Komponente | Vorher | Nachher | Status |
|-----------|--------|---------|--------|
| Model-Synchronisierung | ❌ Hardcoded | ✅ Dynamisch | FIXED |
| Config-Verwaltung | ❌ Manuell | ✅ Automatisiert | FIXED |
| Profile-Wechsel | ❌ File-Copy | ✅ 1-Befehl tool | FIXED |
| Continue + MCP Sync | ❌ Manuell | ✅ Automatisch | FIXED |
| Fallback-Models | ❌ N/A | ✅ Integriert | ADDED |

---

## 🎯 **Nächste Schritte**

1. ✅ **Dynamisches Loading implementiert** → core/llm.py
2. ✅ **Config Manager erstellt** → config_manager.py
3. ✅ **RTX3090-Profil aktiviert** → config.yaml
4. 🔄 **Optional: Bei Bedarf weitere Profile testen**
5. 🚀 **MCP-Server starten und testen**

---

## 📚 **Referenzen**

- [core/llm.py](../core/llm.py) — Dynamisches Model-Loading
- [config_manager.py](../config_manager.py) — Config-Manager Tool
- [.continue/agents/config.yaml](../.continue/agents/config.yaml) — Aktive Konfiguration
- [RTX3090 Setup](./RTX3090_SETUP_COMPLETE.md) — RTX 3090 Optimierungen
