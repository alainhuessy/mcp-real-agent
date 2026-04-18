# 🎯 Model Switching Guide für Continue + MCP-Agent

**Datum:** 18. April 2026  
**Hardware:** RTX 3090 (24GB VRAM) + CPU-Offload  
**Ziel:** Top-Tier Modelle testen und beste Kombination finden

---

## 🚀 **Quick Start (5 Minuten)**

### **1. Scripts ausführbar machen:**

```bash
cd /mnt/6724D393605CE580/Linux/LLM_Projekte/Github/mcp-real-agent

# Mache alle Download-Scripts ausführbar
chmod +x setup_top_tier_models.sh
chmod +x pull_power_models.sh
chmod +x pull_fast_models.sh
```

### **2. Aktiviere die neue Config:**

```bash
# Kopiere die neue Config
cd .continue/agents/
cp config.yaml config-backup-old.yaml
cp config-top-tier.yaml config.yaml

# Oder symlink (keine Duplikate):
# rm config.yaml
# ln -s config-top-tier.yaml config.yaml
```

### **3. Lade die empfohlenen Modelle:**

```bash
# Schnellste Option (recommended):
./setup_top_tier_models.sh

# Oder einzelne Profiles:
./pull_power_models.sh    # Nur große Modelle (51GB+ download)
./pull_fast_models.sh     # Nur schnelle Modelle (7-13GB download)
```

---

## 📊 **Drei Test-Profile**

### **Profile 1️⃣: BALANCED (Empfohlen — Aktuell Aktiv)**

```yaml
# Aktiviert:
  - devstral-small-2:24b (PRIMARY agent)
  - qwen2.5-coder:14b (FALLBACK)

# Performance:
  ✅ Schnell: 2-5 Sek/Response
  ✅ Gut für Agent-Workflows
  ✅ Tool-Calling optimiert
  ✅ Praktische Größen (15GB + 9GB)

# Nutze für:
  - Daily Development
  - Continue Chat
  - MCP-Agent Tasks
  - Quick Iteration

# Command in Continue:
  Mode: AGENT
  Model: agent (= devstral-small-2:24b)
```

---

### **Profile 2️⃣: POWER (Qualität > Speed)**

```yaml
# Aktiviere in config.yaml:
  # Uncomment diese Modelle:
  - glm-5.1:latest (NEW, wenn verfügbar)
  - qwen3-coder-next:latest (51GB Power)
  - nemotron-cascade-2:latest (30GB MoE)
  
  Plus: devstral-small-2:24b (fallback)

# Performance:
  ⚠️ Langsam: 20-60 Sek/Response
  ✅ Best Quality: State-of-Art
  ✅ Komplexe Agent-Reasoning
  ✅ Multi-File Understanding

# Nutze für:
  - Komplexe Debugging-Sessions
  - Intensive Code-Reviews
  - Agent-Orchestrierung
  - Wenn Zeit nicht kritisch ist

# Download:
  ./pull_power_models.sh
  # Oder einzeln:
  ollama pull qwen3-coder-next:latest
  ollama pull glm-5.1:latest
  ollama pull nemotron-cascade-2:latest

# In Continue:
  Mode: AGENT
  Model: glm-agentic (oder qwen-power oder nemotron-reasoning)
```

---

### **Profile 3️⃣: FAST (Speed > Quality)**

```yaml
# Aktiviere in config.yaml:
  # Uncomment diese Modelle:
  - mistral-nemo:7b (7.1GB, super schnell)
  - phi4-mini:latest (2.5GB, extrem schnell)
  - neural-chat:latest (4.1GB, chat-focused)

# Performance:
  ⚡⚡ Extrem schnell: 0.5-2 Sek/Response
  ✅ Noch gut genug für Drafts
  ✅ Sehr kleine Modelle
  ❌ Nicht ideal für Agents

# Nutze für:
  - Schnelle Codegen-Tests
  - Schreibe schnelle Drafts
  - UI Brainstorming
  - Wenn Speed critical ist

# Download:
  ./pull_fast_models.sh
  # Oder einzeln:
  ollama pull mistral-nemo:latest
  ollama pull phi4-mini:latest
  ollama pull neural-chat:latest

# In Continue:
  Model: coder-fast (mistral-nemo)
```

---

## 🔄 **Wie du zwischen Profilen wechselst**

### **Schritt 1: Entscheide welches Profil du testen willst**

```
A) BALANCED (jetzt aktiv - empfohlen)
B) POWER (für bessere Qualität)
C) FAST (für schnelle Tests)
```

### **Schritt 2: Lade die neuen Modelle runter**

```bash
# POWER Profile:
./pull_power_models.sh

# Oder FAST Profile:
./pull_fast_models.sh

# Oder alles auf einmal:
./setup_top_tier_models.sh
```

### **Schritt 3: Aktiviere die Modelle in config.yaml**

Öffne `.continue/agents/config.yaml`:

```yaml
# Für POWER Profile - uncomment diese Modelle:
# 
#  - name: glm-agentic
#    title: "🚀 GLM-5.1 (Agentic Engineering - NEW)"
#    model: glm-5.1:latest
#    ...
#
#  - name: qwen-power
#    title: "💪 Qwen3-Coder-Next 51B"
#    model: qwen3-coder-next:latest
#    ...

# Für FAST Profile - uncomment diese Modelle:
#
#  - name: coder-fast
#    title: "⚡⚡ Mistral Nemo 7B (Super Fast)"
#    model: mistral-nemo:latest
#    ...
```

### **Schritt 4: Reload Continue & Teste**

```bash
# Terminal:
continue dev

# Oder einfach Continue IDE neuladen:
  Ctrl+Shift+P → "Continue: Reload"
  
# Im Continue Chat dann:
Mode: AGENT
Model: [wähle dein Testmodell]

# Test:
debug: Schreibe mir eine Fibonacci Funktion mit Tests
```

---

## 💡 **Schneller Modell-Vergleich**

| Modell | Size | Speed | Agent-Quality | Best For |
|--------|------|-------|---|----------|
| **devstral-small-2:24b** ⭐ | 15GB | ⚡⚡⚡ Fast | ⭐⭐⭐⭐⭐ | Daily Agent Work |
| **qwen3-coder-next** | 51GB | 🐢 Langsam | ⭐⭐⭐⭐⭐ | Best Quality |
| **glm-5.1** | ~? | ? | ⭐⭐⭐⭐⭐ | SOTA (wenn verfügbar) |
| **nemotron-cascade-2** | 24GB | 🐢 Slow | ⭐⭐⭐⭐ | Complex Reasoning |
| **qwen2.5-coder** | 9GB | ⚡⚡⚡ | ⭐⭐⭐ | Fallback/Quick |
| **mistral-nemo** | 7.1GB | ⚡⚡⚡⚡ | ⭐⭐⭐ | Fast Tests |
| **phi4-mini** | 2.5GB | ⚡⚡⚡⚡⚡ | ⭐⭐ | Autocomplete |

---

## 🖥️ **CPU-Offload für große Modelle**

Wenn du größere Modelle testest und sie zu langsam sind, nutze CPU-Offload:

```bash
# In .bashrc oder bei Ollama-Start hinzufügen:
export OLLAMA_GPU_MEMORY=16384    # 16GB GPU
export OLLAMA_NUM_THREAD=16       # 16 CPU Threads

# Ollama neustarten:
pkill ollama
sleep 2
ollama serve

# Dann in neuem Terminal:
cd /pfad/zum/projekt
continue dev
```

**Ergebnis:**
- Größere Modelle passen auch bei 24GB VRAM
- Tradeoff: Mehr RAM-Nutzung, aber bessere Qualität
- Mit RTX 3090 + CPU-Offload kannst du 51GB Modelle testen!

---

## 📋 **Checkliste zum Testen**

```yaml
SETUP:
  ☐ Scripts mit chmod +x ausführbar gemacht
  ☐ config.yaml gesichert (backup gemacht)
  ☐ config-top-tier.yaml kopiert → config.yaml
  ☐ Modelle mit setup_top_tier_models.sh geladen

BALANCED (Aktuell):
  ☐ devstral-small-2:24b geladen (ollama list prüfen)
  ☐ qwen2.5-coder:14b geladen
  ☐ Continue gestartet: Mode AGENT, Model: agent
  ☐ Test: "Schreibe Fibonacci mit Tests"

POWER (Nächste Woche):
  ☐ pull_power_models.sh ausgeführt
  ☐ qwen3-coder-next:latest geladen (51GB)
  ☐ In config.yaml qwen-power uncommented
  ☐ Continue reloaded
  ☐ Test mit qwen3-coder-next
  ☐ Performance vs Quality dokumentieren

FAST (Optional):
  ☐ pull_fast_models.sh ausgeführt
  ☐ mistral-nemo:latest geladen
  ☐ In config.yaml coder-fast uncommented
  ☐ Continue reloaded
  ☐ Test mit mistral-nemo
```

---

## 🎯 **Meine Top-Empfehlung für 18. Apr 2026**

```
Sofort (BALANCED):
  devstral-small-2:24b (primary) + qwen2.5-coder:14b (fallback)
  → Best für Daily Work + MCP-Agent

Nächste Woche (POWER TEST):
  Nutze qwen3-coder-next wenn du Zeit hast
  → Prüfe ob Qualität die langsamere Speed rechtfertigt

Später:
  Teste glm-5.1 wenn auf ollama.com verfügbar
  → Könnte bessere SOTA Performance bringen
```

---

## 🔗 **Links & Hilfsmittel**

- Ollama Docs: https://docs.ollama.com/
- Model Library: https://ollama.com/models
- Continue Docs: https://docs.continue.dev/
- MCP Integration: https://docs.continue.dev/customization/mcp-tools

---

## ❓ **Häufige Fragen**

**F: Welches Modell sollte ich JETZT testen?**  
A: devstral-small-2:24b — es ist schon optimiert

**F: Warum ist qwen3-coder-next so groß (51GB)?**  
A: Mehr Parameter = besseres Verständnis, aber langsamer

**F: Kann ich mehrere Modelle gleichzeitig testen?**  
A: Ja! Sie können unterschiedlich in Continue definiert sein, aber nur 1 zur Zeit aktiv

**F: Was ist der beste Kompromiss Speed/Quality?**  
A: devstral-small-2:24b — 2-5 Sek Response + sehr gute Qualität

**F: Welches Modell für lange Entwicklungs-Sessions?**  
A: devstral-small-2:24b (schnell genug für viele Requests)

---

**Status:** ✅ Ready to Test!  
**Nächste Aktion:** Run `./setup_top_tier_models.sh` 🚀
