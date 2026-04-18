# Brave Search Integration — Entscheidungsbericht

## Executive Summary

**Empfehlung**: Implementiere Brave Search als **separaten MCP Server** (Architektur: Option A)

**Grund**: Bessere Sicherheit, Fehlerbehandlung und Skalierbarkeit

---

## 1. Integration Analysis

### Aktuelle Situation
- MCP Agent OS hat RAG-Tools (lokal über ChromaDB)
- Keine externe Web-Suche verfügbar
- Worker Agent kann nur auf lokale Memory zugreifen

### Anforderungen
1. Web-Zugang für aktuelle Informationen
2. Externe APIs sauber integrieren
3. Sicherheit der API Keys
4. Fehlertoleranz wenn API ausfällt

---

## 2. Optionen Comparison

### Option A: Separater MCP Server ⭐ EMPFOHLEN

**Architektur**:
```
┌──────────────────┐
│   Continue IDE   │
└────────┬─────────┘
         │
    ┌────┴────────────────────────┐
    │                             │
    ▼                             ▼
┌─────────────────────┐   ┌──────────────────────┐
│  MCP: Agent OS      │   │  MCP: Brave Search   │
│  (lokal)            │   │  (REST API)          │
└─────────────────────┘   └──────────────────────┘
         │
    ┌────▼──────────────────────┐
    │   ChromaDB              │
    │   Memory                 │
    └─────────────────────────┘
```

**Implementierung**:
```bash
# 1. Neuer File: mcp_brave_search_server.py
# 2. Startet: python mcp_brave_search_server.py
# 3. Registered in Continue config als separater MCP
```

**Konfiguration in .continue/agents/config.yaml**:
```yaml
mcpServers:
  - name: agent-os
    command: ".venv/bin/python"
    args: ["mcp_server.py"]
    cwd: "/path/to/mcp-real-agent"
    
  - name: brave-search
    command: ".venv/bin/python"
    args: ["mcp_brave_search_server.py"]
    cwd: "/path/to/mcp-real-agent"
    env:
      BRAVE_SEARCH_API_KEY: "${BRAVE_API_KEY}"
```

**Vorteile** ✅:
- 🔒 **Sicherheit**: API Key in separatem Prozess
- 🛡️ **Isolation**: Fehler betreffen nicht Agent OS
- 📈 **Skalierbar**: Kann auf separate Maschine verlegt werden
- 🔄 **Wiederverwendbar**: Andere MCP Servers können es nutzen
- 🧪 **Testbar**: Separate Tests ohne Agent OS

**Nachteile** ❌:
- +1 Service zu starten
- Leichte zusätzliche Latenz (IPC)

---

### Option B: Integriert in Agent OS

**Architektur**:
```
MCP: Agent OS (mcp_server.py)
  ├── Planner Agent
  ├── Worker Agent
  ├── Reviewer Agent
  ├── Memory (ChromaDB)
  ├── Tools (Shell, File, Git)
  └── Tools (Brave Search) ← NEW
```

**Implementierung**:
```python
# In mcp_server.py:
from tools.brave_search import brave_search

_TOOLS.append(
    Tool(
        name="web_search",
        description="Search the web using Brave",
        ...
    )
)

# Handler:
if name == "web_search":
    result = brave_search(args["query"], api_key=os.getenv("BRAVE_API_KEY"))
    return result
```

**Vorteile** ✅:
- ✨ Einfach zu implementieren
- ⚡ Schneller (weniger Overhead)
- 👁️ Einfacher zu debuggen (ein process)

**Nachteile** ❌:
- 🔒 **Sicherheit**: API Key im Memory des ganzen Agents
- 💥 **Fehler**: Brave API Ausfall → ganzer Agent instabil
- 🚫 **Isolation**: Keine Fehlertoleranz
- 📦 **Bloated**: Agent OS wird größer

---

## 3. EMPFOHLENE LÖSUNG: Separater MCP Server

### Implementierungsschritte

#### Phase 1: Setup
```bash
# 1. Dieser File (tools/brave_search.py) gibt grundlegende Funktionen

# 2. Neuer File erstellen:
touch mcp_brave_search_server.py

# 3. Abhängigkeiten hinzufügen (falls nicht present):
pip install requests
```

#### Phase 2: Standalone MCP Server
```python
# mcp_brave_search_server.py

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool
from tools.brave_search import brave_search
import os

server = Server("brave-search-v1")

@server.call_tool()
async def handle_tool(name: str, arguments: dict) -> str:
    if name == "web_search":
        api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        return brave_search(arguments["query"], api_key)
    return f"Unknown tool: {name}"

# Tools Definition
TOOLS = [Tool(
    name="web_search",
    description="Search the web using Brave Search API",
    inputSchema={...}
)]

async def main():
    async with stdio_server(server):
        await server.shutdown()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

#### Phase 3: Konfiguration
```bash
# 1. Registriere in Continue:
# ~/.continue/agents/config.yaml

# 2. API Key setzen:
export BRAVE_SEARCH_API_KEY="your-api-key-here"

# 3. Test:
python mcp_brave_search_server.py
```

#### Phase 4: Integration in Agent OS

Agent OS kann über MCP Protokoll mit Brave Search sprechen:

```python
# Worker Agent kann jetzt tun:
# "search the web for Python async patterns"
# → Router erkennt → RAG-Mode
# → Worker: "Nutze web_search Tool"
# → MCP Brave Search wird aufgerufen
# → Ergebnisse kommen zurück
```

---

## 4. Sicherheit & API Key Handling

### ✅ Best Practices

```bash
# 1. Environment Variables (NIE hardcoded!)
export BRAVE_SEARCH_API_KEY="$YOUR_KEY"

# 2. .env Datei (NUR lokal, nicht in Git!)
# .env
BRAVE_SEARCH_API_KEY=your-key-here

# 3. .gitignore aktualisieren:
echo ".env" >> .gitignore
echo "*.env" >> .gitignore

# 4. Docker Secrets (für Production):
docker run --secret brave_api_key ...

# 5. Logging ist sicher:
# API Key wird NIEMALS logged
```

### Rate Limits Beachten

```python
# Brave Search API Limits:
# - Free Tier: 100 Anfragen/Monat
# - Pro: 1000-50000 Anfragen/Monat

# Implementierung mit Caching:
from functools import lru_cache

@lru_cache(maxsize=50)  # Cache 50 Suchanfragen
def brave_search_cached(query):
    return brave_search(query)
```

---

## 5. Test & Validierung

```python
# tools/test_brave_search.py

import pytest
from tools.brave_search import brave_search

def test_brave_search_no_api_key():
    """Funktioniert auch ohne API Key"""
    result = brave_search("test query", api_key=None)
    assert "nicht konfiguriert" in result.lower()

def test_brave_search_with_invalid_key():
    """Behandelt ungültige Keys"""
    result = brave_search("test", api_key="invalid-key")
    assert "❌" in result or "ungültig" in result.lower()

def test_brave_search_empty_query():
    """Lehrt leere Queries ab"""
    result = brave_search("", api_key="key")
    assert "❌ Leere" in result or "empty" in result.lower()
```

---

## 6. Migration Plan

### Wenn bereits ein Agent OS existiert:

```
1. Tag 1: Standalone testen
   └─ python mcp_brave_search_server.py in separatem Terminal

2. Tag 2: In Continue integrieren
   └─ Zur config.yaml hinzufügen

3. Tag 3: Mit Agent OS testen
   └─ Hybrid-Suche testen

4. Tag 4: Produktion
   └─ API Key sichern, Limits setzen
```

---

## 7. Fallback Strategie

**Falls Brave Search ausfällt**:

```python
# Worker kann trotzdem arbeiten mit RAG-Only:
memory_search("similar questions from past")

# Intelligent degradation:
if web_search_available:
    results = brave_search(query)
else:
    results = memory_search(query)
    results += "ℹ️ (offline-Modus: nur lokale Ergebnisse)"
```

---

## Conclusion

| Aspekt | Separate Server | Integriert |
|--------|-----------------|-----------|
| Sicherheit | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Fehlertoleranz | ⭐⭐⭐⭐⭐ | ⭐ |
| Komplexität | ⭐⭐⭐ | ⭐ |
| Skalierbarkeit | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **GESAMT** | **EMPFOHLEN** | Fallback |

**Nächste Schritte**:
1. [tools/brave_search.py](tools/brave_search.py) ist implementiert ✓
2. Erstelle `mcp_brave_search_server.py` 
3. Tests schreiben
4. In Continue config registrieren
