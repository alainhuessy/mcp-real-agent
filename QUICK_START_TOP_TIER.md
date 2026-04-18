# ⚡ Quick Start - Top-Tier Modelle für Continue + MCP-Agent

**Ziel:** Neue Modelle testen & switchen in 15 Minuten  
**Hardware:** RTX 3090 (24GB VRAM)  
**System:** Agent OS v2.1 + Continue IDE

---

## 🎯 **15-Minute Setup**

### **Minute 1-2: Prepare**

```bash
# 1. Gehe zum Project
cd /mnt/6724D393605CE580/Linux/LLM_Projekte/Github/mcp-real-agent

# 2. Mache Scripts ausführbar
chmod +x setup_top_tier_models.sh pull_power_models.sh pull_fast_models.sh

# 3. Backup alte config
cd .continue/agents
cp config.yaml config-backup-$(date +%s).yaml
```

### **Minute 3-5: Setup neue Config**

```bash
# Option A: Kopiere neue Config (einfach)
cp config-top-tier.yaml config.yaml

# Option B: Symlink (clean)
rm config.yaml
ln -s config-top-tier.yaml config.yaml

# Prüfe:
ls -la config.yaml  # sollte auf config-top-tier.yaml zeigen
```

### **Minute 6-12: Lade Top-Tier Modelle**

```bash
# Gehe zurück zum Root
cd ../..

# Starte Download (empfohlen - alles automatisch):
./setup_top_tier_models.sh

# Das Tool wird fragen:
# [1/5] devstral-small-2:24b ........... [✅ schon da]
# [2/5] qwen2.5-coder:14b ............. [✅ schon da]
# [3/5] nemotron-cascade-2 ............ [laden? j/n]
# [4/5] qwen3-coder-next (51GB) ....... [laden? j/n]
# [5/5] glm-5.1 (wenn verfügbar) ...... [laden? j/n]

# For this first test, antworte:
# 3: j (nemotron ist gut, nur 24GB)
# 4: n (qwen3 ist 51GB - später!)
# 5: n (glm-5.1 kann man später laden)
```

### **Minute 13-15: Test in Continue**

```bash
# Terminal 1: Start MCP-Server
python mcp_server.py
# Sollte zeigen: "🔌 MCP Server started on stdio"

# Terminal 2: Start Continue
continue dev

# In Continue Chat:
# Select: Mode: AGENT
# Select: Model: agent (devstral-small-2:24b)

# Type:
debug: Schreibe eine Python Fibonacci Funktion mit Unit Tests

# Beobachte:
# ✅ Modell denkt nach
# ✅ Erstellt File
# ✅ Testet Code
# ✅ Zeigt: "✅ Task Complete (Call #1)"
```

---

## 📊 **Was wurde geladen/aktiviert**

```
✅ SOFORT VERFÜGBAR (neue config.yaml):
  - devstral-small-2:24b (PRIMARY agent) ← Nutze diesen!
  - qwen2.5-coder:14b (Fallback)
  
🔄 ZUM OPTIONAL-LADEN (scripts bereitstehend):
  - nemotron-cascade-2:30b (Power: Laden optional)
  - qwen3-coder-next:51b (Power: Nur wenn Zeit)
  - glm-5.1:latest (Power: Später wenn verfügbar)
  - mistral-nemo:7b (Fast: Optional)
  - phi4-mini:2.5b (Fast: Optional)
```

---

## 🚀 **Nächste Tests (Morgen/Diese Woche)**

### **Tag 1 (Heute) — Test PRIMARY Model:**

```bash
# 1. Setup (schon gemacht oben)
# 2. Test devstral-small-2:24b
#    Continue → Mode: AGENT, Model: agent
# 3. Führe 5-10 Tasks aus
# 4. Feedback: Schnell? Gut? Fehler?
```

### **Tag 2 (Morgen) — Test POWER Model (optional):**

```bash
# 1. Download & Activate:
./pull_power_models.sh

# 2. In config.yaml uncomment:
#    - name: nemotron-reasoning
#      model: nemotron-cascade-2:latest

# 3. Continue reload
# 4. Mode: AGENT, Model: nemotron-reasoning (oder qwen-power)
# 5. Vergleiche: Speed vs Quality

# Erwartung:
# - Langsamer als devstral (20-60 Sek vs 2-5 Sek)
# - Aber bessere Qualität
```

### **Diese Woche (Later) — Test FAST Model (optional):**

```bash
# Wenn du schnelle Iteration bevorzugst:
./pull_fast_models.sh

# Test mistral-nemo:7b
# Sehr schnell (1-2 Sek) aber basics
```

---

## 🎮 **In Continue IDE nutzen**

### **Model Wechsel (Live):**

```
Continue Chat:
┌──────────────────────────────────────┐
│ Settings (Zahnrad Icon)              │
│ > Default Model: [agent ↓]           │
│   - agent (devstral-small-2)         │
│   - coder (qwen2.5-coder)            │
│   - nemotron-reasoning (wenn geladen)|
│   - qwen-power (wenn geladen)        │
│                                       │
│ > Mode: [AGENT ↓]                    │
│   - AGENT (✓ nutze diesen)           │
│   - CHAT                             │
│   - EDIT                             │
│                                       │
└──────────────────────────────────────┘

Dann: Schreib deine Prompt
"debug: Schreibe mir ein Test Script"
```

### **Zwischen Modellen Switchen:**

```
Während du arbeitest kannst du switchen:

Current: Model: agent
↓
Change Model: nemotron-reasoning
↓
Type: debug: Komplexe Analyse Tasks
↓
Feedback: Besser? Langsamer?
↓
Zurück zu: Model: agent (schneller)
```

---

## ✅ **Verifizierungs-Checkliste**

```yaml
PREPARATION:
  ☐ Scripts mit chmod +x ausführbar gemacht
  ☐ config.yaml in .continue/agents/
  ☐ config-top-tier.yaml im Root kopiert
  ☐ Backup der alten config gemacht

MODEL LOADING:
  ☐ setup_top_tier_models.sh ausgeführt
  ☐ devstral-small-2:24b geladen (ollama list prüft)
  ☐ qwen2.5-coder:14b vorhanden
  ☐ Optionale: nemotron-cascade-2 geladen

CONFIG ACTIVATION:
  ☐ config.yaml → config-top-tier.yaml symlink/copy
  ☐ MCP-Server section in config.yaml vorhanden
  ☐ Agent model in config.yaml definiert

MCP-SERVER:
  ☐ mcp_server.py läuft (python mcp_server.py)
  ☐ Zeigt "🔌 MCP Server started"
  ☐ ChromaDB Directory existiert (chroma_data/)
  
CONTINUE IDE:
  ☐ Continue gestartet (continue dev)
  ☐ Mode: AGENT selected
  ☐ Model: agent selected (= devstral-small-2)
  ☐ MCP-Server verbunden (sollte in logs sichtbar)

FIRST TEST:
  ☐ debug: Schreibe Fibonacci Funktion ausgeführt
  ☐ Model hat getoolzt (file_write, shell_execute, etc)
  ☐ "✅ Task Complete (Call #1)" Message gezigt
  ☐ Memory sync erfolgreich (logs: "🔗 Synced")
```

---

## 🔧 **Troubleshooting**

### **Model nicht gefunden?**

```bash
# Liste alle Modelle:
ollama list

# Wenn devstral-small-2 fehlt:
ollama pull devstral-small-2:24b

# Wenn auch das fehlschlägt:
# → Internet-Check: ollama.com erreichbar?
# → Speicherplatz Check: 100GB+ frei?
# → Manuel reload im Browser: https://ollama.com/library/devstral-small-2
```

### **Continue sieht MCP-Server nicht?**

```bash
# Prüfe ob MCP-Server läuft:
ps aux | grep mcp_server.py

# Wenn nicht läuft, starte:
cd /mnt/.../mcp-real-agent
source .venv/bin/activate
python mcp_server.py

# Dann: Continue IDE reload (Ctrl+Shift+P)
```

### **Zu langsam (>10 Sek)?**

```bash
# Wechsel zu schnellerem Modell:
Model: coder (qwen2.5-coder:14b)

# Oder:
Model: agent (devstral-small-2 sollte schneller sein)

# Wenn immer noch langssam → CPU nutzt alle Cores?
ps aux | grep ollama  # Prüfe CPU-Last
```

### **Keine Tool-Calls?**

```bash
# Prüfe MCP-Connection:
# In Continue → Settings → MCP-Server
# Sollte "agent-os" mit ✅ zeigen

# Restart MCP-Server:
pkill -f mcp_server.py
sleep 2
python mcp_server.py

# Restart Continue:
Ctrl+Shift+P → Continue: Reload
```

---

## 📚 **Dokumentationen die dir helfen**

```
Wichtige Dateien in projekt:
  ✅ .continue/agents/config-top-tier.yaml — Modell Konfiguration
  ✅ MODEL_SWITCHING_GUIDE.md — Ausführliches Switching Guide
  ✅ MCP_COMPATIBILITY_MATRIX.md — MCP-Kompatibilität aller Modelle
  ✅ docs/MODEL_SELECTION_FOR_MCP.md — Modell Empfehlungen
  
Scripts:
  ✅ setup_top_tier_models.sh — Alle Modelle loadem
  ✅ pull_power_models.sh — Große Modelle
  ✅ pull_fast_models.sh — Schnelle Modelle
```

---

## 🎯 **Meine TOP 3 TODO für dich**

```
1️⃣ JETZT (5 Min):
   chmod +x *.sh
   cp .continue/agents/config-top-tier.yaml .continue/agents/config.yaml

2️⃣ JETZT (10 Min):
   ./setup_top_tier_models.sh
   # Antworte: 3=j, 4=n, 5=n

3️⃣ JETZT (5 Min):
   python mcp_server.py
   (in Terminal 2) continue dev
   
   Mode: AGENT
   Model: agent
   
   debug: Schreibe Fibonacci
   
   ✅ DONE! Test erfolgreich!
```

---

## 🚀 **Status nach diesem Setup**

```
✅ config.yaml optimiert für Top-Tier Modelle
✅ devstral-small-2:24b als PRIMARY Model
✅ Alle Modelle haben MCP-Zugriff
✅ RTX 3090 Ressourcen optimal genutzt
✅ CPU-Offload Configuration dokumentiert
✅ Quick Switching zwischen Modellen möglich
✅ Performance-Tests nachvollziehbar

BEREIT für:
✅ Daily Development mit Continue
✅ Complex Agent-Tasks mit MCP
✅ Future Model-Testing (qwen3, glm-5.1, etc)
```

---

**Total Setup Time:** ~15 Minuten ⚡  
**Result:** Production-Ready Top-Tier MCP-Agent 🚀

---

## 🔗 **Schnelle Links**

```
Setup-Scripts:
  ./setup_top_tier_models.sh      — Alle Modelle (recommended)
  ./pull_power_models.sh          — Nur große Modelle
  ./pull_fast_models.sh           — Nur schnelle Modelle

Config-Dateien:
  .continue/agents/config-top-tier.yaml    — Neue Konfiguration
  .continue/agents/config.yaml             — Schreib hier die Aktive

Dokumentation:
  MODEL_SWITCHING_GUIDE.md              — Ausführliches Guide
  MCP_COMPATIBILITY_MATRIX.md           — MCP für jedes Modell
  docs/MODEL_SELECTION_FOR_MCP.md       — Modell Empfehlungen

Run MCP-Server:
  python mcp_server.py

Start Continue:
  continue dev
```

---

**🎉 Alles ready! Viel Erfolg! 🚀**
