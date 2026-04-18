#!/usr/bin/env python3
"""
Brave Search MCP Server — Standalone Web Search
Betrieb: python mcp_brave_search_server.py
"""

import asyncio
import json
import os
import sys
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolResult

from tools.brave_search import brave_search, hybrid_search

# Logging nur nach stderr (stdout = MCP stdio Transport)
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("brave-search-mcp")

# ── Configuration ──────────────────────────────────────────
API_KEY = os.getenv("BRAVE_SEARCH_API_KEY", "")

# ── MCP Server ────────────────────────────────────────────
server = Server("brave-search-v1")

# ── Tools Definition ───────────────────────────────────────

_TOOLS = [
    Tool(
        name="web_search",
        description="Search the web using Brave Search API for current information, research, and external knowledge",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query or keywords (e.g. 'Python async patterns 2024')",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of results (1-20, default 5)",
                    "default": 5,
                }
            },
            "required": ["query"],
        },
    ),
]


# ── Handler ─────────────────────────────────────────────────

def _handle_tool(name: str, arguments: dict[str, Any]) -> str:
    """Execute a tool"""
    
    if name == "web_search":
        query = arguments.get("query", "")
        limit = min(arguments.get("limit", 5), 20)  # Max 20
        
        if not query.strip():
            return "❌ Leere Suchquery"
        
        logger.info(f"Web search: {query}")
        result = brave_search(query, api_key=API_KEY, limit=limit)
        return result
    
    return f"❌ Unbekanntes Tool: {name}"


# ── MCP Tool Request Handler ───────────────────────────────

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls"""
    result = _handle_tool(name, arguments)
    return [TextContent(type="text", text=result)]


# ── Tool Listing ────────────────────────────────────────────

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return _TOOLS


# ── Status Information ──────────────────────────────────────

@server.list_resources()
async def handle_list_resources():
    """Provide information about the server"""
    return [
        {
            "uri": "brave://status",
            "name": "Brave Search Status",
            "description": "Information about Brave Search server configuration",
        }
    ]


# ── Health Check ─────────────────────────────────────────────

async def health_check() -> bool:
    """Simple health check"""
    try:
        if not API_KEY:
            logger.warning("⚠️  BRAVE_SEARCH_API_KEY not set (server will return demo mode)")
            return True  # Still functional, just without real API
        logger.info("✅ Brave Search MCP Server ready")
        return True
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return False


# ── Main ────────────────────────────────────────────────────

async def main():
    """Main server loop"""
    logger.info("🚀 Brave Search MCP Server v1.0 starting...")
    
    # Health check
    if not await health_check():
        sys.exit(1)
    
    logger.info(f"📡 Tools available: {len(_TOOLS)}")
    
    # Start server on stdio
    async with stdio_server(server) as streams:
        logger.info("✅ Server running on stdio transport")
        await streams.wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️  Server stopped")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
