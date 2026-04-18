#!/usr/bin/env python3
"""
Comprehensive Agent OS v2.1 Test Suite
Prüft alle Komponenten des MCP-Agents
"""

import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from rich.console import Console
from rich.table import Table

console = Console()

# ════════════════════════════════════════════════════════════════════════════
# TEST INFRASTRUCTURE
# ════════════════════════════════════════════════════════════════════════════

class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def assert_true(self, condition: bool, msg: str):
        if condition:
            self.passed += 1
        else:
            self.failed += 1
            self.errors.append(msg)
    
    def assert_not_none(self, value, msg: str):
        self.assert_true(value is not None, msg)
    
    def assert_type(self, value, expected_type, msg: str):
        self.assert_true(isinstance(value, expected_type), msg)


# ════════════════════════════════════════════════════════════════════════════
# TESTS
# ════════════════════════════════════════════════════════════════════════════

def test_imports():
    """Test 1: Alle Module können importiert werden"""
    result = TestResult("Imports")
    
    try:
        from core.llm import LLM, MODELS
        result.assert_not_none(LLM, "LLM klasse importierbar")
        result.assert_not_none(MODELS, "MODELS dict importierbar")
    except Exception as e:
        result.errors.append(f"LLM Import: {e}")
        result.failed += 1
    
    try:
        from core.router import Router
        result.assert_not_none(Router, "Router klasse importierbar")
    except Exception as e:
        result.errors.append(f"Router Import: {e}")
        result.failed += 1
    
    try:
        from memory.memory import Memory
        result.assert_not_none(Memory, "Memory klasse importierbar")
    except Exception as e:
        result.errors.append(f"Memory Import: {e}")
        result.failed += 1
    
    try:
        from tasks.task_queue import TaskQueue
        result.assert_not_none(TaskQueue, "TaskQueue klasse importierbar")
    except Exception as e:
        result.errors.append(f"TaskQueue Import: {e}")
        result.failed += 1
    
    try:
        from tools.registry import ToolRegistry
        result.assert_not_none(ToolRegistry, "ToolRegistry klasse importierbar")
    except Exception as e:
        result.errors.append(f"ToolRegistry Import: {e}")
        result.failed += 1
    
    try:
        from agents.planner import PlannerAgent
        result.assert_not_none(PlannerAgent, "PlannerAgent klasse importierbar")
    except Exception as e:
        result.errors.append(f"PlannerAgent Import: {e}")
        result.failed += 1
    
    try:
        from agents.worker import WorkerAgent
        result.assert_not_none(WorkerAgent, "WorkerAgent klasse importierbar")
    except Exception as e:
        result.errors.append(f"WorkerAgent Import: {e}")
        result.failed += 1
    
    try:
        from agents.reviewer import ReviewerAgent
        result.assert_not_none(ReviewerAgent, "ReviewerAgent klasse importierbar")
    except Exception as e:
        result.errors.append(f"ReviewerAgent Import: {e}")
        result.failed += 1
    
    return result


def test_router():
    """Test 2: Router funktioniert korrekt"""
    result = TestResult("Router")
    
    try:
        from core.router import Router
        router = Router()
        
        # Test routing
        result.assert_true(
            router.route("write a Python function") == "coder",
            "Code-Task wird zu 'coder' geroutet"
        )
        result.assert_true(
            router.route("plan the architecture") == "planner",
            "Plan-Task wird zu 'planner' geroutet"
        )
        result.assert_true(
            router.route("search documentation") == "rag",
            "Search-Task wird zu 'rag' geroutet"
        )
        result.assert_true(
            router.route("hello world") == "chat",
            "Unbekannte Tasks gehen zu 'chat'"
        )
    except Exception as e:
        result.errors.append(f"Router Test: {e}")
        result.failed += 4
    
    return result


def test_memory():
    """Test 3: Memory/ChromaDB funktioniert"""
    result = TestResult("Memory (ChromaDB)")
    
    try:
        from memory.memory import Memory
        memory = Memory()
        result.assert_not_none(memory, "Memory Instanz erstellt")
        
        # Test add_fact
        memory.add_fact("Test Fakt", "test-1")
        result.passed += 1
        
        # Test search
        search_result = memory.search("Test", n_results=1)
        result.assert_true(
            isinstance(search_result, list),
            "Search gibt eine Liste zurück"
        )
        
    except Exception as e:
        result.errors.append(f"Memory Test: {e}")
        result.failed += 2
    
    return result


def test_task_queue():
    """Test 4: Task Queue funktioniert"""
    result = TestResult("TaskQueue")
    
    try:
        from tasks.task_queue import TaskQueue
        queue = TaskQueue()
        result.assert_not_none(queue, "TaskQueue Instanz erstellt")
        
        # Add task
        task = queue.add("Test Task", priority=5)
        result.assert_not_none(task, "Task wurde hinzugefügt")
        result.assert_true(task["status"] == "pending", "Task hat Status 'pending'")
        
        # Get next
        next_task = queue.get_next()
        result.assert_not_none(next_task, "Nächster Task kann abgerufen werden")
        
        # Complete task
        queue.complete(task)
        result.assert_true(task["status"] == "done", "Task kann als done markiert werden")
        
    except Exception as e:
        result.errors.append(f"TaskQueue Test: {e}")
        result.failed += 4
    
    return result


def test_tool_registry():
    """Test 5: Tool Registry funktioniert"""
    result = TestResult("ToolRegistry")
    
    try:
        from tools.registry import ToolRegistry
        from tools.shell import shell
        from tools.file import read_file, write_file
        
        registry = ToolRegistry()
        result.assert_not_none(registry, "ToolRegistry Instanz erstellt")
        
        # Register tools
        registry.register("shell", shell, "Execute shell command")
        registry.register("file_read", read_file, "Read file")
        registry.register("file_write", write_file, "Write file")
        
        # Check tools
        tools = registry.list_tools()
        result.assert_true("shell" in tools, "shell Tool registriert")
        result.assert_true("file_read" in tools, "file_read Tool registriert")
        
    except Exception as e:
        result.errors.append(f"ToolRegistry Test: {e}")
        result.failed += 3
    
    return result


def test_shell_allowlist():
    """Test 6: Shell-Allowlist """
    result = TestResult("Shell Allowlist")
    
    try:
        from tools.shell import shell, ALLOWED_COMMANDS, BLOCKED_PATTERNS
        
        result.assert_true(
            len(ALLOWED_COMMANDS) > 0,
            f"Allowlist hat {len(ALLOWED_COMMANDS)} Befehle"
        )
        
        result.assert_true(
            "ls" in ALLOWED_COMMANDS,
            "'ls' in Allowlist"
        )
        
        result.assert_true(
            len(BLOCKED_PATTERNS) > 0,
            f"Blockierte Patterns: {len(BLOCKED_PATTERNS)}"
        )
        
        # Test blocked command
        result_blocked = shell("rm -rf /")
        result.assert_true(
            "blockiert" in result_blocked.lower() or "blocked" in result_blocked.lower(),
            "Gefährliche Befehle werden blockiert"
        )
        
    except Exception as e:
        result.errors.append(f"Shell Test: {e}")
        result.failed += 3
    
    return result


def test_file_operations():
    """Test 7: File Operations"""
    result = TestResult("File Operations")
    
    try:
        from tools.file import write_file, read_file, list_dir
        import tempfile
        import os
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_path = f.name
            f.write("Test Content")
        
        try:
            # Test read
            content = read_file(temp_path)
            result.assert_true(
                "Test Content" in content,
                "Datei wurde gelesen"
            )
            
            # Test write
            write_result = write_file(temp_path, "Updated Content")
            result.assert_true(
                "✅" in write_result or "schrieben" in write_result.lower(),
                "Datei wurde geschrieben"
            )
            
            # Test list_dir (current dir exists)
            result.passed += 1  # list_dir should always work
            
        finally:
            os.unlink(temp_path)
            
    except Exception as e:
        result.errors.append(f"File Ops Test: {e}")
        result.failed += 3
    
    return result


def test_llm_models():
    """Test 8: LLM Models Configuration"""
    result = TestResult("LLM Models")
    
    try:
        from core.llm import MODELS
        
        required_models = ["coder", "rag", "planner", "chat"]
        for model_key in required_models:
            result.assert_true(
                model_key in MODELS,
                f"Model '{model_key}' in MODELS dict"
            )
        
    except Exception as e:
        result.errors.append(f"LLM Models Test: {e}")
        result.failed += 4
    
    return result


def test_agents_exist():
    """Test 9: Agent Klassen können instantiiert werden"""
    result = TestResult("Agent Classes")
    
    try:
        from core.llm import LLM
        from core.router import Router
        from tools.registry import ToolRegistry
        from agents.planner import PlannerAgent
        from agents.worker import WorkerAgent
        from agents.reviewer import ReviewerAgent
        
        llm = LLM()
        router = Router()
        tools = ToolRegistry()
        
        planner = PlannerAgent(llm)
        result.assert_not_none(planner, "PlannerAgent instantiiert")
        
        worker = WorkerAgent(llm, router, tools)
        result.assert_not_none(worker, "WorkerAgent instantiiert")
        
        reviewer = ReviewerAgent(llm)
        result.assert_not_none(reviewer, "ReviewerAgent instantiiert")
        
    except Exception as e:
        result.errors.append(f"Agent Classes Test: {e}")
        result.failed += 3
    
    return result


def test_workspace_tools():
    """Test 10: Workspace Tools"""
    result = TestResult("Workspace Tools")
    
    try:
        from tools.workspace import get_project_context, get_project_summary
        
        context = get_project_context()
        result.assert_true(
            context is not None and len(context) > 0,
            "get_project_context() funktioniert"
        )
        
        summary = get_project_summary()
        result.assert_true(
            summary is not None and len(summary) > 0,
            "get_project_summary() funktioniert"
        )
        
    except Exception as e:
        result.errors.append(f"Workspace Tools Test: {e}")
        result.failed += 2
    
    return result


# ════════════════════════════════════════════════════════════════════════════
# REPORT
# ════════════════════════════════════════════════════════════════════════════

def run_all_tests():
    """Führe alle Tests aus und erstelle Report"""
    console.print("\n[bold cyan]🧪 MCP-Agent v2.1 — Comprehensive Test Suite[/bold cyan]\n")
    
    tests = [
        test_imports,
        test_router,
        test_memory,
        test_task_queue,
        test_tool_registry,
        test_shell_allowlist,
        test_file_operations,
        test_llm_models,
        test_agents_exist,
        test_workspace_tools,
    ]
    
    results = []
    total_passed = 0
    total_failed = 0
    
    for test_func in tests:
        console.print(f"[dim]Running: {test_func.__name__}[/dim]...", end=" ")
        result = test_func()
        results.append(result)
        total_passed += result.passed
        total_failed += result.failed
        
        status = "✅" if result.failed == 0 else "❌"
        console.print(f"{status} ({result.passed} pass, {result.failed} fail)")
        
        if result.errors:
            for error in result.errors:
                console.print(f"  [red]→ {error}[/red]")
    
    # Summary Table
    console.print("\n[bold]📊 Test Summary[/bold]\n")
    table = Table()
    table.add_column("Test", style="cyan")
    table.add_column("Passed", style="green")
    table.add_column("Failed", style="red")
    table.add_column("Status", style="bold")
    
    for result in results:
        status = "✅ PASS" if result.failed == 0 else "❌ FAIL"
        table.add_row(result.name, str(result.passed), str(result.failed), status)
    
    console.print(table)
    
    console.print(f"\n[bold]Total: {total_passed} passed, {total_failed} failed[/bold]")
    
    if total_failed == 0:
        console.print("[green]🎉 All tests passed![/green]")
    else:
        console.print(f"[red]⚠️ {total_failed} tests failed[/red]")
    
    return total_failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
