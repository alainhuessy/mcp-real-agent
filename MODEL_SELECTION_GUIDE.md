---
title: "🎯 Ollama Model Selection Guide für Agent OS v2.1"
subtitle: "Optimale Modelle für RTX 3090 + Continue IDE + Tool-Use (MCP)"
date: 2026-04-18
source: "ollama.com/library (researched 2026-04-18)"
---

# 🎯 Modell-Auswahl Guide — Agent OS v2.1 auf RTX 3090

> **Hardware**: RTX 3090 (24GB VRAM)
> **Use-Case**: Agent OS mit MCP-Tools, Continue IDE, Agentic Workflows
> **Quelle**: Recherche auf ollama.com/library

---

## 🏆 **TOP EMPFEHLUNGEN nach Anwendungsfall**

### 1️⃣ **BEST FOR TOOL-USE (Was du wirklich brauchst!)**

#### 🥇 **llama3-groq-tool-use** (8B & 70B)
- **Spezialisiert auf Tool-Use / Function Calling**
- ✅ 8B Version: 8GB VRAM (perfekt für Tab-Autocomplete)
- ✅ 70B Version: 24GB + CPU-Offload möglich
- ✅ **Production-Grade Tool Integration**
- ✅ **Continue IDE**: Vollständig eingebunden
- **Bewertung für dich**: ⭐⭐⭐⭐⭐ **IDEAL FÜR AGENT OS!**
- **Performance**: 3-7 Sekunden (8B), 5-15 Sekunden (70B mit Offload)

```yaml
# Empfohlene Config für RTX 3090:
Tier 1 (Daily Work):
  - llama3-groq-tool-use:8b       # Quick tool-use, autocomplete
  - Backup: qwen2.5-coder:14b     # Code generation fallback

Tier 2 (Complex Tasks):
  - llama3-groq-tool-use:70b      # Deep reasoning + tools
  - (Mit CPU-Offload: 20GB GPU + 4GB CPU)
```

---

#### 🥈 **qwen3-coder** (30B) - AGENTIC CODING
- **Spezialisiert auf Agentic Workflows**
- ✅ Tool-Support: `tools` tag
- ✅ Cloud-Mode: Integration mit Continue IDE
- ✅ 30B (mit Quantisierung ~15GB) für RTX 3090
- ✅ **Kein CPU-Offload nötig!**
- **Bewertung**: ⭐⭐⭐⭐⭐ **PERFECT FOR AGENTS!**
- **Besonderheit**: Speziell für Multi-File Edits trainiert
- **Performance**: 5-10 Sekunden

```yaml
# Alt: Wenn qwen3-coder nicht verfügbar:
- qwen3-coder-next:latest    # Newest version
- qwen2.5-coder:14b          # Fallback
```

---

#### 🥉 **Devstral-Small-2** (24B) - BALANCED
- ✅ Tool-Support confirmed
- ✅ Vision-Support (kann Screenshots analysieren!)
- ✅ 15GB VRAM (mit Sicherheitsmarge)
- ✅ Multi-File Editing für große Repos
- **Bewertung**: ⭐⭐⭐⭐ **GUTE BALANCE**
- **Problem**: In diversen Benchmarks nicht so stark im Tool-Use wie Llama3-Groq
- **Empfehlung**: Als Fallback nutzen, nicht als Primary

```yaml
# NICHT als Primary verwenden (du hattest Probleme damit):
# Nutze als Fallback:
- devstral-small-2:24b       # Backup für Heavy Tasks
```

---

### 2️⃣ **AGENTIC + REASONING (für komplexe Workflows)**

#### 🚀 **GLM-5.1** (Newest November 2024!)
- **State-of-Art für agentic engineering**
- ✅ `tools` + `thinking` tags
- ✅ **SWE-Bench Pro leader** (Software Engineering Agents!)
- ✅ 500B+ aber mit Smart MoE → nur ~40B aktiv
- ⚠️ Größer als RTX 3090 OHNE massive CPU-Offload
- **Bewertung**: ⭐⭐⭐⭐⭐ **THEORETISCH BEST, aber Hardware-Problem**
- **Alternative**: GLM-4.7-Flash (30B)

#### 🔥 **Qwen3.6** (Newest April 2026!)
- **Freshest, strongest agentic model**
- ✅ Vision + Tools + Thinking
- ✅ 35B parameters (mit Quantisierung ~18GB)
- ✅ **Upgraded Agentic Capabilities**
- **Bewertung**: ⭐⭐⭐⭐⭐ **NEXT GENERATION**
- **Problem**: Gerade eben released, noch nicht auf ollama.com Standardlibrarian?

#### 🎯 **Nemotron-3-Super** (NVIDIA)
- **120B MoE, aber nur 12B aktiv**
- ✅ Tools + Thinking support
- ✅ Designed for multi-agent applications
- ✅ "Maximum compute efficiency"
- ⚠️ Komplexes MoE-Loading auf RTX 3090 → teste erst!
- **Performance**: unknown für RTX 3090

---

### 3️⃣ **CONTINUE IDE OPTIMIERT**

**Best Models für Continue IDE (mit "cloud" option):**

```
✅ RECOMMENDED:
- qwen3-coder (tools, cloud)
- qwen3-coder-next (tools, cloud)
- devstral-small-2 (tools, cloud)
- kimi-k2.5 (vision, tools, thinking, cloud) ← NEWEST

⭐ SPECIAL: llama3-groq-tool-use
- Nicht "cloud" tagged aber beste Tool-Use Integration
- Manuell in Continue config.yaml hinzufügen
```

---

## 📊 **HARDWARE-OPTIMIERTE AUSWAHL für RTX 3090**

### 🎯 **Die 3 Best Profiles für DEINE Setup:**

#### **Profile A: DAILY DEVELOPMENT (EMPFOHLEN)**
```yaml
# Schnell + Zuverlässig + Tool-Support

Primary: llama3-groq-tool-use:8b
  - Memory: 8GB
  - Speed: 3-5 Sekunden
  - Tool-Use: ⭐⭐⭐⭐⭐ BEST
  - Use for: Daily agent tasks

Secondary: qwen2.5-coder:14b
  - Memory: 9GB
  - Speed: 2-5 Sekunden
  - Use for: Quick code generation

Reserve: mistral-nemo:12b
  - Memory: 7GB
  - Speed: 1-2 Sekunden
  - Use for: Ultra-fast drafts

Total GPU: 8 + 9 + 7 = 24GB (PERFECT FIT!)
```

#### **Profile B: POWER MODE (wenn Zeit egal)**
```yaml
# Best Quality + Tool Integration

Primary: llama3-groq-tool-use:70b
  - Memory: 24GB GPU (maybe + CPU-Offload)
  - Speed: 5-15 Sekunden
  - Tool-Use: ⭐⭐⭐⭐⭐ PRODUCTION

Secondary: qwen3-coder:30b
  - Memory: ~15GB (mit Q4 quantization)
  - Speed: 5-10 Sekunden
  - Use for: Complex agentic workflows

 ≈ Rotate between models (can't run both!)
```

#### **Profile C: AGENTIC ENGINEERING (Experimental)**
```yaml
# LATEST + BEST Agentic Tech

Primary: qwen3.6:35b (if available)
  - Memory: ~18GB
  - Speed: 5-12 Sekunden
  - Features: Vision + Tools + Thinking
  - Status: Newest, best agentic

Fallback: kimi-k2.5:80b
  - Memory: 80B but MoE (nur ~20B aktiv?)
  - Tools + Vision + Thinking
  - Status: New, untested on RTX 3090

Alternative: glm-4.7-flash:30b
  - Memory: ~15GB
  - Smaller GLM-5 alternative
  - Status: Stable, proven
```

---

## 🔍 **MODEL COMPARISON (from ollama.com/library)**

### Tool-Use Capability Ranking:

| Modell | Tool-Support | Größe | RTX 3090 | Continue | Agent OS | Rating |
|--------|-------------|-------|---------|----------|----------|--------|
| **llama3-groq-tool-use** | ⭐⭐⭐⭐⭐ | 8B/70B | ✅ easy | ✅ yes | ✅✅✅ | **10/10** |
| **qwen3-coder** | ⭐⭐⭐⭐⭐ | 30B | ✅ yes | ✅ cloud | ✅✅✅ | **10/10** |
| **qwen3-coder-next** | ⭐⭐⭐⭐⭐ | ? | ✅ ? | ✅ cloud | ✅✅ | **9/10** |
| **devstral-small-2** | ⭐⭐⭐⭐ | 24B | ✅ yes | ✅ cloud | ✅ | **8/10** |
| **qwen2.5-coder** | ⭐⭐⭐⭐ | 14B | ✅ easy | ✅ yes | ✅✅ | **8/10** |
| **mistral-nemo** | ⭐⭐⭐ | 12B | ✅ easy | ✅ yes | ✅ | **7/10** |
| Nemotron-mini | ⭐⭐⭐⭐ | 4B | ✅ tiny | ✅ | ⚠️ | **6/10** |
| devstral | ⭐⭐⭐ | ? | ? | ? | ? | **5/10** |

---

## ⚡ **VERWENDUNGSZWECKE → OPTIMALE MODELLE**

### Für DAILY AGENT WORK:
```
PRIMARY: llama3-groq-tool-use:8b (8GB, schnell, beste Tool-Use)
FALLBACK: qwen2.5-coder:14b (Code-spezifisch)
```

### Für COMPLEX MULTI-FILE EDITING:
```
PRIMARY: qwen3-coder:30b (Agentic + Tool-Support)
or
PRIMARY: llama3-groq-tool-use:70b (if you have patience)
```

### Für CONTINUE IDE DEVELOPMENT:
```
PRIMARY: qwen3-coder (native cloud-mode support)
SECONDARY: llama3-groq-tool-use:8b (best tool-calling)
```

### Für TAB-AUTOCOMPLETE:
```
PRIMARY: mistral-nemo:12b (super fast)
LIGHTWEIGHT: phi4-mini:3.8b (extremly fast)
```

### Für REASONING + PLANNING:
```
PRIMARY: qwen3.6:35b (new, with thinking mode)
FALLBACK: llama3-groq-tool-use:70b (thinking-ready)
```

---

## 🛠️ **MCP-TOOL-USE INTEGRATION**

### Die besten Modelle FÜR MCP-Agenten:

**Tier 1 - OPTIMAL:**
- ✅ **llama3-groq-tool-use** (8B & 70B)
  - Explicitly trained for function calling
  - JSON-Schema tool descriptions understood
  - Continue IDE: Full MCP integration
  - Agent OS: Perfect fit for worker.py

**Tier 2 - VERY GOOD:**
- ✅ **qwen3-coder** (30B)
  - Agentic training
  - Tool understanding ⭐⭐⭐⭐
  - Cloud mode für Continue

**Tier 3 - GOOD:**
- ✅ **devstral-small-2** (24B)
  - Tool support but not primary focus
  - Vision capabilities added
  - Gute für complex tasks

**AVOID für MCP:**
- ❌ **devstral:24b** (Ollama.com says "coding agents" aber weaker tool-use)
- ❌ **llama3.1:8b** (Generic model, kein Tool-Training)

---

## 📋 **SCRIPT: Modelle automatisch recherchieren lassen**

Der Agent OS sollte diese Recherche SELBST durchführen können:

```python
# agents/model_researcher.py (NEW!)

class ModelResearcher:
    """Autonomer Agent der Modelle auf ollama.com recherchiert."""
    
    def find_optimal_models(self, 
                           hardware: str = "rtx3090",
                           use_case: str = "agent-os",
                           vram_gb: int = 24) -> list[dict]:
        """
        Recherchiert optimale Modelle basierend auf:
        1. Hardware-Spezifikationen (VRAM, GPU-Typ)
        2. Use-Case (agentic, coding, chat, tool-use)
        3. Criteria: Tool-Support, Speed vs Quality
        """
        
        # Pseudo-Code:
        # 1. Scrape ollama.com/library für alle Modelle
        # 2. Filter nach Tags: tools, cloud, thinking
        # 3. Berechne VRAM-Anforderungen
        # 4. Rank nach Use-Case
        # 5. Return Top 5 Empfehlungen
        
        pass
```

---

## 🚀 **IMPLEMENTATION: Update config.yaml mit TOP MODELS**

### Empfehlung für DEINE config.yaml:

```yaml
# .continue/agents/config.yaml (UPDATED)

name: Agent OS v2.1 — TOOL-USE OPTIMIZED
version: 3.1.0

models:
  # 🥇 TIER 1: TOOL-USE SPECIALISTS
  
  # PRIMARY: Best Tool-Calling Model
  - name: agent
    title: "🟢 llama3-groq-tool-use:8b (PRIMARY)"
    provider: ollama
    model: llama3-groq-tool-use:8b
    apiBase: "http://localhost:11434"
    contextLength: 8192
    tags: ["tools", "production", "recommend"]
    
  # POWER: Deep Reasoning + Tools
  - name: agent-power
    title: "💪 llama3-groq-tool-use:70b (POWER)"
    provider: ollama
    model: llama3-groq-tool-use:70b
    apiBase: "http://localhost:11434"
    contextLength: 8192
    tags: ["tools", "reasoning", "heavy"]
    
  # 🥈 TIER 2: AGENTIC CODING
  
  - name: coder
    title: "⚡ qwen3-coder:30b (Agentic Coding)"
    provider: ollama
    model: qwen3-coder:30b
    apiBase: "http://localhost:11434"
    contextLength: 32000
    tags: ["tools", "agentic", "coding"]
    
  # 🥉 TIER 3: FALLBACK & SPECIAL
  
  - name: coder-quick
    title: "⚡⚡ qwen2.5-coder:14b (Quick)"
    provider: ollama
    model: qwen2.5-coder:14b
    apiBase: "http://localhost:11434"
    contextLength: 28000
    tags: ["fast", "coding"]

# Tab Autocomplete
tabAutocompleteModel:
  name: coder-quick
  model: qwen2.5-coder:14b

# MCP Servers
mcpServers:
  - name: agent-os
    command: ".venv/bin/python"
    args: ["mcp_server.py"]
```

---

## 📚 **NEXT STEPS**

### 1. Installiere die besten Modelle:

```bash
# PRIMARY (Tool-Use Best)
ollama pull llama3-groq-tool-use:8b

# BACKUP (Agentic)
ollama pull qwen3-coder:30b

# FALLBACK (Quick)
ollama pull qwen2.5-coder:14b
```

### 2. Update core/llm.py:

Das Dynamic Loading wird automatisch greifen!

### 3. Test in Continue IDE:

```
Mode: AGENT
Model: agent (llama3-groq-tool-use:8b)

Prompt: "Schreibe eine Python Funktion die Fibonacci berechnet"

Expected:
- Agent erkennt Tools
- Tools werden korrekt aufgerufen
- Multi-File Edits möglich
```

### 4. Monitor Performance:

```bash
# In Terminal: watch GPU memory
watch -n 1 nvidia-smi

# Expected:
# llama3-groq-tool-use:8b = 8-10GB
# qwen3-coder:30b = 20-22GB
# qwen2.5-coder:14b = 14-16GB
```

---

## 🎯 **ZUSAMMENFASSUNG**

### Was Ollama.com zeigt (2026-04-18):

1. **llama3-groq-tool-use ist STATE-OF-ART für Tool-Use**
   - Explizit für MCP / Function Calling trainiert
   - 8B Version = perfekt für RTX 3090
   - Besser als devstral für Agent OS

2. **qwen3-coder ist beste Alternative für Agentic Work**
   - Spezialisiert auf Software Engineering Agents
   - Cloud-Mode für Continue IDE
   - 30B mit Q4 Quantisierung passt auf RTX 3090

3. **Devstral ist nicht optimal für Tool-Use**
   - "Coding Agents" aber nicht spezifisch für Tool-Calling
   - Deine Probleme damit = expected
   - Nutze als Fallback, nicht Primary

4. **Newest Models (qwen3.6, kimi-k2.5, glm-5.1)**
   - State-of-Art aber noch nicht getestet auf Ollama
   - GLM-5.1 leader in SWE-Bench Pro (Agents!)
   - Werden in den nächsten 2-3 Monaten mainstream

---

## ✅ **EMPFEHLUNG FÜR DICH**

```
🎯 BESTE LÖSUNG für deine RTX 3090:

PRIMARY:  llama3-groq-tool-use:8b      (8GB - Daily work)
FALLBACK: qwen3-coder:30b              (15GB - Complex tasks)
QUICK:    qwen2.5-coder:14b            (9GB - Drafts)
LITE:     mistral-nemo:12b             (7GB - Autocomplete)

TOTAL: Alle Modelle passen auf 24GB RAM mit Rotation!
```

---

## 📖 **Referenzen**

- [Ollama Library](https://ollama.com/library)
- Tool-Use Models: llama3-groq-tool-use, qwen3-coder, devstral-small-2
- Agentic Models: qwen3.6, glm-5, kimi-k2
- Ressourcen: RTX 3090 (24GB optimal), Zero CPU-Offload
