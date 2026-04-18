#!/usr/bin/env python3
"""
Agent OS v2.1 — MCP Server (FIXED Version).
Behebt das "Invalid request parameters" Problem durch korrekte Handler-Registrierung.

Features:
- Hot Reload: Wechsle zwischen Configs ohne Restart
- Environment Variable: ACTIVE_CONFIG controls die aktive Config
- CLI Tool: config-switch.py zum Verwalten von Configs
"""

import asyncio
import json
import sys
import logging
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
)

from core.llm import LLM, CONFIG_LOADER
from core.router import Router
from core.logger import log_info, log_debug, log_error
from memory.memory import Memory
from tasks.task_queue import TaskQueue
from tools.registry import ToolRegistry
from tools.shell import shell
from tools.file import read_file, write_file, list_dir
from tools.git import git_status, git_commit, git_log
from tools.workspace import get_project_context, get_project_summary
from agents.planner import PlannerAgent
from agents.worker import WorkerAgent
from agents.reviewer import ReviewerAgent

# Logging nur nach stderr (stdout = MCP stdio Transport)
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("agent-os-mcp")

log_info("MCP_SERVER", "Agent OS v2.1 MCP Server starting")

# ── Agent OS Instanz ──────────────────────────────────────────────
llm = LLM()
router = Router()
memory = Memory()
tasks = TaskQueue()
tools = ToolRegistry()

# ── Response Cache: Prevent infinite loops ──
_response_cache = {}

# ── Iteration Limit System (verhindert Loop-Probleme) ──
_tool_call_count = {}  # {tool_hash: count}
_MAX_ITERATIONS_PER_SESSION = 2  # Nach 2 Aufrufen: Hard Stop

# ── Config Hot-Reload (Automatischer Wechsel ohne Restart) ──
_last_active_config = CONFIG_LOADER.get_active_config_name()
log_info("MCP_SERVER", f"📌 Aktive Config beim Start: {_last_active_config}")

def _check_config_reload():
    """Prüfe ob Config gewechselt wurde und lade neu (Hot Reload)."""
    global _last_active_config
    
    current_active = CONFIG_LOADER.get_active_config_name()
    
    if _last_active_config != current_active:
        log_info("MCP_SERVER", f"🔄 Config gewechselt: {_last_active_config} → {current_active}")
        models = CONFIG_LOADER.load_config()
        _last_active_config = current_active
        return True
    
    return False

def _make_tool_key(name: str, arguments: dict) -> str:
    """Erzeuge eindeutigen Schlüssel für Tool-Aufruf."""
    import hashlib
    key_str = f"{name}:{json.dumps(arguments, sort_keys=True)}"
    return hashlib.md5(key_str.encode()).hexdigest()[:12]

planner = PlannerAgent(llm)
worker = WorkerAgent(llm, router, tools)
reviewer = ReviewerAgent(llm)
log_debug("MCP_SERVER", "Agent pipeline initialized")

# ── MCP Server ────────────────────────────────────────────────────
server = Server("agent-os-v2")


# ==================== TOOLS DEFINITION ====================

_TOOLS = [
    # ── Agent Pipeline Tools ──
    Tool(
        name="agent_run_task",
        description="Execute a task through the full Agent OS pipeline: Router → Worker (LLM) → Reviewer → Memory.",
        inputSchema={
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The task to execute (e.g. 'write a Python function for sorting')",
                }
            },
            "required": ["task"],
        },
    ),    
    Tool(
        name="agent_run_task_tracked",
        description="Execute a task WITH real-time tracking (shows progress bars, LLM decisions, etc). Use for complex tasks.",
        inputSchema={
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The task to execute with tracking",
                }
            },
            "required": ["task"],
        },
    ),    
    Tool(
        name="agent_plan",
        description="Plan goal: break into subtasks using workspace context.",
        inputSchema={
            "type": "object",
            "properties": {
                "goal": {
                    "type": "string",
                    "description": "Goal to plan",
                }
            },
            "required": ["goal"],
        },
    ),
    
    Tool(
        name="agent_review",
        description="Review code for bugs, improvements, and consistency.",
        inputSchema={
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Code to review"},
                "task": {"type": "string", "description": "Original task"},
            },
            "required": ["code"],
        },
    ),

    # ── Memory Tools ──
    Tool(
        name="memory_search",
        description="[Agent OS] Search Agent OS memory for past solutions and context.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Results limit", "default": 5},
            },
            "required": ["query"],
        },
    ),

    Tool(
        name="memory_save",
        description="[Agent OS] Save solutions and context to Agent OS memory.",
        inputSchema={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Content to save"},
                "topic": {"type": "string", "description": "Topic/tag for retrieval"},
            },
            "required": ["content", "topic"],
        },
    ),

    # ── Config Management Tools (Hot Reload) ──
    Tool(
        name="config_list",
        description="[Agent OS] List all available Continue config files (.continue/agents/config*.yaml).",
        inputSchema={"type": "object", "properties": {}},
    ),

    Tool(
        name="config_switch",
        description="[Agent OS] Switch to a different config file. Hot reload: no restart needed.",
        inputSchema={
            "type": "object",
            "properties": {
                "config_name": {
                    "type": "string",
                    "description": "Config file name (e.g., 'config-top-tier.yaml')"
                }
            },
            "required": ["config_name"],
        },
    ),

    Tool(
        name="config_current",
        description="[Agent OS] Show current config and active models.",
        inputSchema={"type": "object", "properties": {}},
    ),

    # ── Project Context Tools ──
    Tool(
        name="project_info",
        description="[Agent OS] Get Agent OS workspace overview: structure, modules, configuration.",
        inputSchema={"type": "object", "properties": {}},
    ),

    Tool(
        name="project_summary",
        description="[Agent OS] Get Agent OS project architecture analysis, tech stack, design patterns.",
        inputSchema={"type": "object", "properties": {}},
    ),

    # ── File Tools ── (PRIMARY Workspace Access)
    Tool(
        name="file_read",
        description="[Agent OS] Read workspace files. Auto-truncates large files (>100KB).",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path in workspace (e.g., 'core/agent.py')"}
            },
            "required": ["path"],
        },
    ),

    Tool(
        name="file_write",
        description="[Agent OS] Write files to workspace. Create or modify code and configs.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "content": {"type": "string", "description": "File content"},
            },
            "required": ["path", "content"],
        },
    ),

    Tool(
        name="file_list",
        description="[Agent OS] List workspace directories with 📁📄 icons and file sizes.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path (e.g., 'core')"}
            },
        },
    ),

    # ── Shell Tools ──
    Tool(
        name="shell_run",
        description="[Agent OS] Execute shell commands in workspace (python, git, npm).",
        inputSchema={
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command (safe commands only)"}
            },
            "required": ["command"],
        },
    ),

    # ── Git Tools ──
    Tool(
        name="git_status",
        description="[Agent OS] Check workspace git status, branches, changes.",
        inputSchema={"type": "object", "properties": {}},
    ),

    Tool(
        name="git_commit",
        description="[Agent OS] Create git commits in workspace.",
        inputSchema={
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Commit message"}
            },
            "required": ["message"],
        },
    ),

    Tool(
        name="git_log",
        description="[Agent OS] View workspace git history.",
        inputSchema={
            "type": "object",
            "properties": {
                "count": {"type": "integer", "description": "Number of commits", "default": 5}
            },
        },
    ),

    # ── Task Tools ──
    Tool(
        name="task_add",
        description="[Agent OS] Add task to Agent OS queue.",
        inputSchema={
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task description"},
                "priority": {"type": "integer", "description": "Priority 1-10", "default": 1},
            },
            "required": ["task"],
        },
    ),

    Tool(
        name="task_list",
        description="[Agent OS] List pending Agent OS tasks.",
        inputSchema={"type": "object", "properties": {}},
    ),

    Tool(
        name="task_next",
        description="[Agent OS] Get next pending Agent OS task.",
        inputSchema={"type": "object", "properties": {}},
    ),

    # ── Memory Tools ──
    Tool(
        name="memory_save",
        description="Save information to persistent memory. Store findings and context.",
        inputSchema={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Content to store"},
                "topic": {"type": "string", "description": "Topic/tag for retrieval"},
            },
            "required": ["content", "topic"],
        },
    ),

    # ── LLM Direct ──
    Tool(
        name="llm_ask",
        description="[Agent OS] Direct LLM query with optional model selection.",
        inputSchema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Question/prompt"},
                "model": {"type": "string", "description": "Optional: specific model"},
                "system": {"type": "string", "description": "Optional: custom system prompt"},
            },
            "required": ["prompt"],
        },
    ),

    # ── System ──
    Tool(
        name="agent_status",
        description="[Agent OS] Get system status, models, tools, workspace info.",
        inputSchema={"type": "object", "properties": {}},
    ),
]


# ==================== HANDLER FUNCTIONS ====================

def _execute_tool(name: str, arguments: dict[str, Any]) -> str:
    """Führe ein Tool aus mit Iteration Limit & Completion Signals.
    
    Features:
    - Hot Reload: Prüfet bei jedem Aufruf ob Config gewechselt wurde
    - Tracks each tool call for loop detection
    - Returns completion signals after max iterations
    - Prevents infinite Continue-Chat loops
    """
    
    # 🔄 HOT RELOAD CHECK (Automatischer Config-Wechsel erkennen)
    _check_config_reload()
    
    import hashlib
    tool_id = hashlib.md5(f"{name}{str(arguments)}".encode()).hexdigest()[:8]
    tool_key = _make_tool_key(name, arguments)
    
    log_debug("MCP_SERVER", f"[{tool_id}] Tool call: {name}")
    
    # ── ITERATION LIMIT CHECK ──
    current_count = _tool_call_count.get(tool_key, 0)
    if current_count >= _MAX_ITERATIONS_PER_SESSION:
        log_warning = print  # Simple fallback
        log_warning(f"[{tool_id}] ⚠️ MAX ITERATIONS REACHED for {name}")
        
        # Return cached result or stop message
        if tool_key in _response_cache:
            cached = _response_cache[tool_key]
            return f"{cached}\n\n⚠️ [MAX_ITERATIONS={_MAX_ITERATIONS_PER_SESSION} REACHED - Stopping to prevent loops]"
        else:
            return f"⚠️ Tool {name} reached max iterations limit. No further calls for this query."
    
    _tool_call_count[tool_key] = current_count + 1
    call_number = current_count + 1
    
    try:
        args = arguments

        # ── Agent Tools ──
        if name == "agent_run_task":
            task = args["task"]
            log_info("MCP_SERVER", f"[{tool_id}] agent_run_task: {task[:50]}...")
            router_mode = router.route(task)
            log_debug("MCP_SERVER", f"[{tool_id}] Router mode: {router_mode}")
            result = worker.execute(task, memory.search(task))
            review = reviewer.review(task, result)
            memory.sync(f"Task: {task}\nResult: {result[:200]}", task[:30])
            log_info("MCP_SERVER", f"[{tool_id}] agent_run_task completed")
            
            # ── COMPLETION SIGNAL (verhindert Further Loops) ──
            completion_msg = f"✅ Task Complete (Call #{call_number})"
            if call_number >= _MAX_ITERATIONS_PER_SESSION:
                completion_msg += " — MAX ITERATIONS REACHED"
            
            # Cache the result
            _response_cache[tool_key] = result
            
            return f"{completion_msg}\n\nExecuted:\n{result}\n\n📝 Review:\n{review}"

        if name == "agent_run_task_tracked":
            task = args["task"]
            log_info("MCP_SERVER", f"[{tool_id}] agent_run_task_tracked: {task[:50]}...")
            # Tracked execution via worker
            result = worker.tracked_execute(task, memory.search(task), show_progress=False)
            review = reviewer.review(task, result)
            memory.sync(f"Task: {task}\nResult: {result[:200]}", task[:30])
            log_info("MCP_SERVER", f"[{tool_id}] agent_run_task_tracked completed")
            
            # ── COMPLETION SIGNAL ──
            completion_msg = f"✅ Task Complete (Call #{call_number})"
            if call_number >= _MAX_ITERATIONS_PER_SESSION:
                completion_msg += " — MAX ITERATIONS REACHED"
            
            _response_cache[tool_key] = result
            return f"{completion_msg}\n\nResult:\n{result}\n\n📝 Review:\n{review}"

        if name == "agent_plan":
            goal = args["goal"]
            log_info("MCP_SERVER", f"[{tool_id}] agent_plan: {goal[:50]}...")
            
            # ── Cache Check ──
            cache_key = f"plan:{goal}"
            if cache_key in _response_cache:
                log_debug("MCP_SERVER", f"[{tool_id}] Returning cached plan")
                return _response_cache[cache_key] + "\n\n⚠️ [CACHED]"
        
            # ── Enhanced: Workspace Context ──
            workspace_context = get_project_context()
            memory_context = memory.search(goal, n_results=5)
            enhanced_context = [workspace_context] + memory_context
            
            subtasks = planner.plan(goal, enhanced_context)
            for st in subtasks:
                tasks.add(st)
            
            result = "\n".join([f"- {st}" for st in subtasks])
            _response_cache[cache_key] = result
            return result

        if name == "agent_review":
            code = args["code"]
            task = args.get("task", "Code review")
            log_info("MCP_SERVER", f"[{tool_id}] Review task: {task[:50]}...")
            return reviewer.review(task, code)

        # ── Memory ──
        if name == "memory_search":
            query = args["query"]
            limit = args.get("limit", 5)
            log_debug("MCP_SERVER", f"[{tool_id}] Memory search: {query[:30]}...")
            results = memory.search(query, n_results=limit)
            return "\n".join([f"- {r}" for r in results]) if results else "No results"

        if name == "memory_save":
            content = args["content"]
            topic = args["topic"]
            log_info("MCP_SERVER", f"[{tool_id}] Memory save: {topic}")
            memory.sync(content, topic)
            return f"✅ Saved to memory: {topic}"

        # ── Config Management (Hot Reload) ──
        if name == "config_list":
            log_debug("MCP_SERVER", f"[{tool_id}] List available configs")
            configs = CONFIG_LOADER.get_available_configs()
            active = CONFIG_LOADER.get_active_config_name()
            result = f"Active: {active}\n\nAvailable:\n"
            result += "\n".join([f"  - {c}" for c in configs])
            return result

        if name == "config_switch":
            config_name = args["config_name"]
            log_info("MCP_SERVER", f"[{tool_id}] Switch config: {config_name}")
            success = CONFIG_LOADER.switch_config(config_name)
            if success:
                models = CONFIG_LOADER.load_config()
                result = f"✅ Config switched to: {config_name}\n\nModels:\n"
                result += "\n".join([f"  {m}: {n}" for m, n in models.items()])
                return result
            else:
                return f"❌ Failed to switch config: {config_name}"

        if name == "config_current":
            log_debug("MCP_SERVER", f"[{tool_id}] Get current config")
            active = CONFIG_LOADER.get_active_config_name()
            models = CONFIG_LOADER.load_config()
            result = f"Active Config: {active}\n\nModels:\n"
            result += "\n".join([f"  {m}: {n}" for m, n in models.items()])
            return result

        # ── Project ──
        if name == "project_info":
            log_debug("MCP_SERVER", f"[{tool_id}] Get project info")
            return get_project_context()

        if name == "project_summary":
            log_debug("MCP_SERVER", f"[{tool_id}] Get project summary")
            return get_project_summary()

        # ── File ──
        if name == "file_read":
            log_debug("MCP_SERVER", f"[{tool_id}] Read file: {args['path']}")
            return read_file(args["path"])

        if name == "file_write":
            log_info("MCP_SERVER", f"[{tool_id}] Write file: {args['path']}")
            return write_file(args["path"], args["content"])

        if name == "file_list":
            log_debug("MCP_SERVER", f"[{tool_id}] List dir: {args.get('path', '.')}")
            return list_dir(args.get("path", "."))

        # ── Shell ──
        if name == "shell_run":
            cmd = args["command"]
            log_info("MCP_SERVER", f"[{tool_id}] Shell: {cmd[:50]}...")
            return shell(cmd)

        # ── Git ──
        if name == "git_status":
            log_debug("MCP_SERVER", f"[{tool_id}] Git status")
            return git_status()

        if name == "git_commit":
            msg = args["message"]
            log_info("MCP_SERVER", f"[{tool_id}] Git commit: {msg[:30]}...")
            return git_commit(msg)

        if name == "git_log":
            log_debug("MCP_SERVER", f"[{tool_id}] Git log")
            return git_log(args.get("count", 5))

        # ── Tasks ──
        if name == "task_add":
            task_desc = args["task"]
            log_info("MCP_SERVER", f"[{tool_id}] Task add: {task_desc[:50]}...")
            t = tasks.add(task_desc, args.get("priority", 1))
            return f"✅ Task added: {t['id']} — {t['task']}"

        if name == "task_list":
            log_debug("MCP_SERVER", f"[{tool_id}] Task list")
            all_tasks = tasks.get_all()
            if not all_tasks:
                return "No tasks"
            return "\n".join([f"[{t['status']}] {t['id']} — {t['task']}" for t in all_tasks])

        if name == "task_next":
            log_info("MCP_SERVER", f"[{tool_id}] Task next")
            t = tasks.get_next()
            if not t:
                return "No pending tasks"
            t["status"] = "running"
            result = worker.execute(t["task"], memory.search(t["task"]))
            tasks.complete(t)
            memory.sync(f"Task: {t['task']}\nResult: {result[:300]}", t["task"][:30])
            log_info("MCP_SERVER", f"[{tool_id}] Task completed: {t['task'][:30]}...")
            return f"✅ Task completed: {t['task']}\n\n{result}"

        # ── LLM ──
        if name == "llm_ask":
            prompt = args["prompt"]
            model_name = args.get("model")
            if not model_name:
                mode = router.route(prompt)
                model_name = llm.get_model(mode)
            system = args.get("system", "")
            log_info("MCP_SERVER", f"[{tool_id}] LLM ask: {prompt[:30]}... (model: {model_name})")
            return llm.ask(model_name, prompt, system)

        # ── System ──
        if name == "agent_status":
            log_debug("MCP_SERVER", f"[{tool_id}] Agent status")
            return json.dumps({
                "status": "running",
                "pending_tasks": tasks.get_pending_count(),
                "total_tasks": len(tasks.get_all()),
                "tools": [t.name for t in _TOOLS],
                "models": MODELS,
            }, indent=2)

        log_error("MCP_SERVER", f"[{tool_id}] Unknown tool: {name}")
        return f"❌ Unknown tool: {name}"
        
    except Exception as e:
        log_error("MCP_SERVER", f"[{tool_id}] Tool execution failed: {name}", e)
        return f"❌ Error executing tool '{name}': {str(e)}"


# ==================== MCP HANDLERS ====================

@server.list_tools()
async def list_tools_handler() -> list[Tool]:
    """MCP Handler: List all available tools."""
    logger.info(f"Handler called: list_tools (returning {len(_TOOLS)} tools)")
    return _TOOLS


@server.call_tool()
async def call_tool_handler(name: str, arguments: dict[str, Any]) -> CallToolResult:
    """MCP Handler: Call a tool."""
    logger.info(f"Handler called: call_tool({name})")
    
    try:
        result = _execute_tool(name, arguments)
        return CallToolResult(
            content=[TextContent(type="text", text=str(result))]
        )
    except Exception as e:
        logger.error(f"Tool error: {name} → {e}", exc_info=True)
        return CallToolResult(
            content=[TextContent(type="text", text=f"❌ Error: {e}")],
            isError=True,
        )


# ── Main ──────────────────────────────────────────────────────────

async def main():
    logger.info(f"🧠 Agent OS v2.1 MCP Server starting ({len(_TOOLS)} tools ready)...")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped")
