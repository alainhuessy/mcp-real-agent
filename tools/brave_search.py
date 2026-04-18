"""
Brave Search Integration Module für MCP-Agent v2.1
Unterstützt externe Web-Suche über Brave Search API
"""

import requests
from typing import Optional
from rich.console import Console

console = Console()


# ════════════════════════════════════════════════════════════════════════════
# BRAVE SEARCH CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════

class BraveSearchConfig:
    """Konfiguration für Brave Search Integration"""
    
    API_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Brave Search
        
        Args:
            api_key: Brave Search API Key (von https://api.search.brave.com/)
                    Falls None: Überspringt externe Suche (verwendet nur lokale Memory)
        """
        self.api_key = api_key
        self.enabled = api_key is not None
        
        if self.enabled:
            console.print("[green]✅ Brave Search aktiviert[/green]")
        else:
            console.print("[yellow]⚠️  Brave Search deaktiviert (kein API Key)[/yellow]")


# ════════════════════════════════════════════════════════════════════════════
# BRAVE SEARCH TOOL
# ════════════════════════════════════════════════════════════════════════════

def brave_search(query: str, api_key: Optional[str] = None, limit: int = 5) -> str:
    """
    Führt eine Brave-Search durch
    
    Args:
        query: Suchbegriffe
        api_key: Brave Search API Key
        limit: Maximale Anzahl Ergebnisse (default: 5)
        
    Returns:
        Formatierte Suchergebnisse als String
    """
    
    if not api_key:
        return """
ℹ️  Brave Search nicht konfiguriert.

Zum Aktivieren:
1. API Key von https://api.search.brave.com/ registrieren
2. In environment variable BRAVE_SEARCH_API_KEY setzen
3. Oder in MCP Server config übergeben

Im Moment: Nutze lokale Memory + RAG für Suche
        """
    
    if not query.strip():
        return "❌ Leere Suchquery"
    
    try:
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": api_key,
        }
        
        params = {
            "q": query,
            "count": limit,
        }
        
        response = requests.get(
            BraveSearchConfig.API_ENDPOINT,
            headers=headers,
            params=params,
            timeout=10
        )
        
        if response.status_code == 401:
            return "❌ Brave Search API Key ungültig"
        
        if response.status_code != 200:
            return f"❌ Brave Search Fehler: {response.status_code}"
        
        data = response.json()
        
        # Format results
        results = []
        results.append(f"🔍 Suchergebnisse für: '{query}'\n")
        
        if "web" not in data or not data["web"]["results"]:
            results.append("Keine Ergebnisse gefunden")
            return "\n".join(results)
        
        for i, result in enumerate(data["web"]["results"][:limit], 1):
            title = result.get("title", "No Title")
            url = result.get("url", "No URL")
            description = result.get("description", "No Description")
            
            results.append(f"\n{i}. {title}")
            results.append(f"   URL: {url}")
            results.append(f"   → {description[:150]}...")
        
        return "\n".join(results)
        
    except requests.Timeout:
        return "❌ Brave Search Timeout (10s)"
    except requests.ConnectionError:
        return "❌ Brave Search nicht erreichbar (Netzwerkfehler)"
    except Exception as e:
        return f"❌ Brave Search Fehler: {e}"


# ════════════════════════════════════════════════════════════════════════════
# HYBRID SEARCH (Local Memory + Brave Search)
# ════════════════════════════════════════════════════════════════════════════

def hybrid_search(query: str, memory_func, api_key: Optional[str] = None) -> str:
    """
    Hybrid-Suche: Verbindet lokale Memory + Brave Search
    
    1. Zuerst lokale Memory durchsuchen
    2. Falls zu wenig Ergebnisse: externe Brave-Suche
    
    Args:
        query: Suchbegriffe
        memory_func: Memory search function (z.B. memory.search())
        api_key: Brave Search API Key (optional)
        
    Returns:
        Kombinierte Suchergebnisse
    """
    
    results = []
    results.append(f"🔎 Hybrid Search: '{query}'\n")
    results.append("=" * 60)
    
    # ── Phase 1: Local Memory ──
    results.append("\n📚 Lokale Memory:")
    try:
        local_results = memory_func(query, n_results=3)
        if local_results:
            for i, result in enumerate(local_results, 1):
                preview = result[:100] + "..." if len(result) > 100 else result
                results.append(f"  {i}. {preview}")
        else:
            results.append("  (keine lokalen Ergebnisse)")
    except Exception as e:
        results.append(f"  ❌ Memory Fehler: {e}")
    
    # ── Phase 2: External Brave Search ──
    if api_key:
        results.append("\n🌐 Brave Search:")
        brave_result = brave_search(query, api_key, limit=3)
        results.append(brave_result)
    else:
        results.append("\n🌐 Brave Search:")
        results.append("  (nicht konfiguriert)")
    
    results.append("=" * 60)
    return "\n".join(results)


# ════════════════════════════════════════════════════════════════════════════
# MCP TOOL REGISTRATION
# ════════════════════════════════════════════════════════════════════════════

def get_brave_search_tool_definition() -> dict:
    """
    Gibt die MCP Tool-Definition für Brave Search zurück
    (kann in mcp_server.py's _TOOLS liste eingebunden werden)
    """
    return {
        "name": "web_search",
        "description": "Search the web using Brave Search API (external)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query/keywords",
                }
            },
            "required": ["query"],
        },
    }


# ════════════════════════════════════════════════════════════════════════════
# INTEGRATION GUIDE
# ════════════════════════════════════════════════════════════════════════════

"""
INTEGRATION OPTIONEN:

Option A: SEPARATE MCP SERVER (EMPFOHLEN)
─────────────────────────────────────────
✅ Vorteile:
  - Unabhängig vom Agent OS
  - Bessere Fehlerbehandlung
  - Kann parallel laufen
  - Cleaner separation of concerns
  
❌ Nachteile:
  - Zusätzlicher Service

Implementierung:
  1. Erstelle: mcp_brave_search_server.py
  2. Registriere in Continue config als separater MCP Server
  3. Agent kann es via tool call erreichen


Option B: INTEGRIERT IN AGENT OS (SCHNELL)
───────────────────────────────────────────
✅ Vorteile:
  - Direkter Integration
  - Weniger Services
  - Einfacher zu debuggen
  
❌ Nachteile:
  - Abhängigkeit von Brave API
  - Fehler betreffen ganzen Agent

Implementierung:
  1. In mcp_server.py: _TOOLS liste erweitern
  2. Handler für "web_search" tool hinzufügen
  3. API Key via Umgebungsvariable oder config laden


EMPFEHLUNG:
───────────
→ OPTION A (Separater MCP Server)

Gründe:
  1. Brave API Key = Sicherheitsrisiko wenn gehackt
  2. Rate Limits besser isoliert
  3. Kann unabhängig gescailt werden
  4. Andere Agents können es auch nutzen

Architektur:
  Continue IDE
    ↓
  MCP Server (Agent OS)  ←  (lokal)
    ↓
  MCP Server (Brave Search)  ←  (REST zu api.search.brave.com)
"""
