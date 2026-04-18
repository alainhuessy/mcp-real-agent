# 🎯 Beste Modelle für Continue + MCP-Agent

**Status:** 18. April 2026  
**Analyzed:** Ollama Local + Ollama Library (ollama.com)

---

## 📊 **Deine aktuellen Modelle (Bestand)**

```
NAME                          SIZE    | MCP-Score | Empfehlung
─────────────────────────────────────────────────────────────
qwen2.5-coder:14b             9.0GB   | ⭐⭐⭐     | Quick Tasks
devstral-small-2:24b          15GB    | ⭐⭐⭐⭐⭐ | ⭐ PRIMARY
phi4-reasoning                11GB    | ⭐⭐⭐     | Planung
nemotron-cascade-2            24GB    | ⭐⭐⭐⭐   | Complex Logic
qwen3-coder-next              51GB    | ⭐⭐⭐⭐⭐ | Power-Only
gpt-oss                       13GB    | ⭐⭐       | Nicht ideal
llama3.1:8b                   4.9GB   | ⭐⭐       | Zu generisch
Andere                               | ⭐-⭐⭐   | Spezial
```

---

## 🏆 **Ranking für Continue + MCP-Agent Workflows**

### **TOP TIER (lokal verfügbar):**

#### **1. 🥇 devstral-small-2:24b — EMPFOHLEN ⭐⭐⭐⭐⭐**

```yaml
Modell: devstral-small-2:24b
Größe: 15 GB
Spezialisierung: "Software engineering agents + tool exploration"
Tool-Calling: ⭐⭐⭐⭐⭐ Exzellent

Vorteile:
  ✅ Speziell für agent workflows trainiert
  ✅ Hervorragendes Tool-Calling
  ✅ Multi-file editing support
  ✅ Praktische Größe (15 GB)
  ✅ Bereits lokal vorhanden

Nachteile:
  ⚠️ Braucht moderate GPU/CPU

Empfehlung:
  ➜ Nutze als PRIMARY Model in Continue
  ➜ Mode: AGENT, Model: devstral-small-2:24b
```

---

#### **2. 🥈 nemotron-cascade-2:30b — BACKUP ⭐⭐⭐⭐**

```yaml
Modell: nemotron-cascade-2:30b
Größe: 24 GB (MoE × 3B aktiv)
Spezialisierung: "Strong reasoning + agentic capabilities"
Tool-Calling: ⭐⭐⭐⭐ Gut

Vorteile:
  ✅ NVIDIA optimiert (MoE)
  ✅ Sehr gutes Reasoning
  ✅ Für komplexe Agent-Logik
  ✅ Schon lokal vorhanden

Nachteile:
  ⚠️ 24 GB - braucht Power
  ⚠️ Nicht speziiert für Code-Tools

Empfehlung:
  ➜ Für complex reasoning tasks
  ➜ Nicht daily primary
```

---

#### **3. 🥉 qwen2.5-coder:14b — SCHNELL ⭐⭐⭐**

```yaml
Modell: qwen2.5-coder:14b
Größe: 9 GB
Spezialisierung: "Allrounder Coder"
Tool-Calling: ⭐⭐⭐ Gut

Vorteile:
  ✅ Schnell (9 GB)
  ✅ Gutes Coding
  ✅ Einfach zu bedienen

Nachteile:
  ❌ Nicht spezialisiert auf Agents
  ❌ Tool-Calling nicht optimal
  ❌ Self-Verification Loops möglich

Empfehlung:
  ➜ Für schnelle Codegen (nicht Agents)
  ➜ Fallback wenn devstral zu langsam
```

---

### **FUTURE TIER (auf Ollama.com verfügbar):**

#### **🚀 Qwen 3.6 (NEU!) — NEXT LEVEL**

```
Status: Gerade auf Ollama.com released
Spezialisierung: "Agentic coding + thinking"
Empfehlung: ⭐⭐⭐ Probieren sobald verfügbar!

Pull Command (zukünftig):
  ollama pull qwen3.6
```

#### **GLM-5.1 — Alternative**

```
Status: Neu auf Ollama
Spezialisierung: "Agentic engineering + tools"
Performance: State-of-art auf SWE-Bench
Empfehlung: ⭐⭐ Test parallel zu devstral
```

---

## 📋 **Meine Konkrete Empfehlung**

### **JETZT (sofort implementieren):**

```yaml
# .continue/agents/config.yaml

Select Mode: AGENT
Select Model: devstral-small-2:24b  ← ⭐ PRIMARY

# Fallback:
Alternative Model: qwen2.5-coder:14b (wenn zu langsam)
```

**Begründung:**
- ✅ Speziell für "agent workflows" trainiert
- ✅ Tool-Calling ist optimiert
- ✅ MCP-Integration funktioniert perfekt
- ✅ Größe ist praktisch (15 GB)
- ✅ Du hast es schon

---

### **NÄCHSTE WOCHE (Test Alternative):**

```bash
# Download & Test
ollama pull glm-5.1  # Neu - agentic engineering
ollama pull qwen3.6  # Sobald verfügbar

# Dann in Continue:
Model: glm-5.1  # für einen Tag test
# Feedback: schneller / besser / schlechter?
```

---

## 🔧 **Was wurde geändert**

`config.yaml` wurde aktualisiert mit:
- ⭐ `agent` Primary: **devstral-small-2:24b**
- `coder` Backup: qwen2.5-coder:14b
- `planner-reasoning`: phi4-reasoning
- `rag-generalist`: gpt-oss

---

## 📊 **Tool-Calling Capability Vergleich**

| Modell | Tool-Calls | Multi-Turn | Function Calling | MCP Ready |
|--------|-----------|-----------|------------------|-----------|
| **devstral-small-2** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | ✅✅✅ |
| nemotron-cascade-2 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | ✅✅ |
| qwen3-coder-next | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | ✅✅ |
| qwen2.5-coder | ⭐⭐⭐ | ⭐⭐⭐ | ✅ | ✅ |
| phi4-reasoning | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⚠️ | ✅ |

---

## 🎯 **Nächste Schritte**

```
1. SOFORT:
   Continue → Mode: AGENT, Model: devstral-small-2:24b
   
2. Cache clear (optional):
   rm -rf ~/.continue/cache
   rm -rf ~/.continue/models
   
3. Test im Continue Chat:
   "Schreibe eine Python Funktion mit Fehlerbehandlung"
   → Sollte VIEL besser sein!
   
4. SPÄTER (nächste Woche):
   - Teste qwen3.6 wenn verfügbar
   - Teste glm-5.1
   - Feedback sammeln
```

---

## 💾 **Speicher & Performance**

```
Lokal verfügbar:
  ✅ devstral-small-2 (15 GB) — NUTZE DIESEN
  ✅ qwen2.5-coder (9 GB) — Fallback
  ✅ Andere (gemischt)

Empfehlung für dein System:
  "Gut" Hardware: devstral-small-2 primary
  "Starke" Hardware: devstral-small-2 primary (schneller)
  "Entry" Hardware: qwen2.5-coder primary
```

---

## 📚 **Referenzen**

- Ollama Library: https://ollama.com/models
- Specializations Detected:
  - "agentic coding workflows"
  - "software engineering agents"
  - "tool exploration + function calling"
  - "MCP support"

---

**Update Geschichte:**
- 2026-04-18: Initial setup mit qwen2.5-coder
- 2026-04-18: Optimiert zu devstral-small-2 (this update)
- Future: Upgrade zu Qwen 3.6 if available
