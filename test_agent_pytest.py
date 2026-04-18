"""
Pytest Test Suite für MCP-Agent v2.1
Comprehensive testing mit fixtures und parametrized tests
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from core.llm import LLM, MODELS
from core.router import Router
from memory.memory import Memory
from tasks.task_queue import TaskQueue
from tools.registry import ToolRegistry
from tools.shell import shell, ALLOWED_COMMANDS, BLOCKED_PATTERNS
from tools.file import read_file, write_file, list_dir
from agents.planner import PlannerAgent
from agents.worker import WorkerAgent
from agents.reviewer import ReviewerAgent


# ════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def temp_file():
    """Erstellt eine temporäre Datei für Tests"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Test Content")
        temp_path = f.name
    yield temp_path
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_dir():
    """Erstellt ein temporäres Verzeichnis"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup
    import shutil
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)


@pytest.fixture
def router():
    """Router Instanz"""
    return Router()


@pytest.fixture
def llm():
    """LLM Instanz"""
    return LLM()


@pytest.fixture
def memory():
    """Memory Instanz"""
    return Memory()


@pytest.fixture
def task_queue():
    """TaskQueue Instanz"""
    return TaskQueue()


@pytest.fixture
def tool_registry():
    """ToolRegistry Instanz"""
    return ToolRegistry()


@pytest.fixture
def planner(llm):
    """PlannerAgent Instanz"""
    return PlannerAgent(llm)


@pytest.fixture
def worker(llm, router, tool_registry):
    """WorkerAgent Instanz"""
    return WorkerAgent(llm, router, tool_registry)


@pytest.fixture
def reviewer(llm):
    """ReviewerAgent Instanz"""
    return ReviewerAgent(llm)


# ════════════════════════════════════════════════════════════════════════════
# ROUTER TESTS
# ════════════════════════════════════════════════════════════════════════════

class TestRouter:
    """Router Tests"""
    
    def test_route_coder_tasks(self, router):
        """Code-Tasks sollten zu 'coder' geroutet werden"""
        tasks = [
            "write a function",
            "fix this bug",
            "refactor the API",
            "implement a class",
        ]
        for task in tasks:
            assert router.route(task) == "coder", f"Failed for: {task}"
    
    def test_route_planner_tasks(self, router):
        """Plan-Tasks sollten zu 'planner' geroutet werden"""
        tasks = ["plan the architecture", "design the system", "build project structure"]
        for task in tasks:
            assert router.route(task) == "planner"
    
    def test_route_rag_tasks(self, router):
        """Search-Tasks sollten zu 'rag' geroutet werden"""
        tasks = ["search docs", "research knowledge base", "find PDF"]
        for task in tasks:
            assert router.route(task) == "rag"
    
    def test_route_default_chat(self, router):
        """Unbekannte Tasks sollten zu 'chat' gehen"""
        assert router.route("hello world") == "chat"
        assert router.route("what is 2+2") == "chat"


# ════════════════════════════════════════════════════════════════════════════
# MEMORY TESTS
# ════════════════════════════════════════════════════════════════════════════

class TestMemory:
    """Memory/ChromaDB Tests"""
    
    def test_memory_creation(self, memory):
        """Memory Instanz kann erstellt werden"""
        assert memory is not None
        assert memory.facts is not None
        assert memory.tasks_mem is not None
        assert memory.episodes is not None
    
    def test_add_fact(self, memory):
        """Facts können gespeichert werden"""
        memory.add_fact("Test Fakt", "fact-1")
        # Should not raise
    
    def test_add_episode(self, memory):
        """Episodes können gespeichert werden"""
        memory.add_episode("Test Episode", "ep-1")
        # Should not raise
    
    def test_search_returns_list(self, memory):
        """Search gibt eine Liste zurück"""
        memory.add_fact("Test Fakt", "fact-1")
        result = memory.search("Test", n_results=5)
        assert isinstance(result, list)
    
    def test_sync_saves_fact_and_episode(self, memory):
        """Sync speichert in Facts und Episodes"""
        memory.sync("Sync Test", "sync-1")
        # Should not raise


# ════════════════════════════════════════════════════════════════════════════
# TASK QUEUE TESTS
# ════════════════════════════════════════════════════════════════════════════

class TestTaskQueue:
    """TaskQueue Tests"""
    
    def test_add_task(self, task_queue):
        """Task kann hinzugefügt werden"""
        task = task_queue.add("Test Task", priority=5)
        assert task is not None
        assert task["status"] == "pending"
        assert task["task"] == "Test Task"
        assert task["priority"] == 5
    
    def test_get_next_returns_highest_priority(self, task_queue):
        """get_next gibt Task mit höchster Priorität zurück"""
        task_queue.add("Low", priority=1)
        task_queue.add("High", priority=10)
        next_task = task_queue.get_next()
        assert next_task["task"] == "High"
    
    def test_complete_task(self, task_queue):
        """Task kann als erledigt markiert werden"""
        task = task_queue.add("Test", priority=1)
        task_queue.complete(task)
        assert task["status"] == "done"
        assert "completed" in task
    
    def test_fail_task(self, task_queue):
        """Task kann als fehlgeschlagen markiert werden"""
        task = task_queue.add("Test", priority=1)
        task_queue.fail(task, "Error occurred")
        assert task["status"] == "failed"
        assert task["error"] == "Error occurred"
    
    def test_get_pending_count(self, task_queue):
        """Pending Count ist korrekt"""
        task_queue.add("Task1", priority=1)
        task_queue.add("Task2", priority=1)
        assert task_queue.get_pending_count() == 2
        
        task = task_queue.get_next()
        task_queue.complete(task)
        assert task_queue.get_pending_count() == 1


# ════════════════════════════════════════════════════════════════════════════
# TOOL REGISTRY TESTS
# ════════════════════════════════════════════════════════════════════════════

class TestToolRegistry:
    """Tool Registry Tests"""
    
    def test_register_tool(self, tool_registry):
        """Tool kann registriert werden"""
        dummy_func = lambda x: f"Result: {x}"
        tool_registry.register("dummy", dummy_func, "A dummy tool")
        assert "dummy" in tool_registry.tools
    
    def test_list_tools(self, tool_registry):
        """Alle registrierten Tools können aufgelistet werden"""
        tool_registry.register("tool1", lambda x: x)
        tool_registry.register("tool2", lambda x: x)
        tools = tool_registry.list_tools()
        assert "tool1" in tools
        assert "tool2" in tools
    
    def test_run_tool_success(self, tool_registry):
        """Ein registriertes Tool kann ausgeführt werden"""
        tool_registry.register("echo", lambda x: f"Echo: {x}")
        result = tool_registry.run("echo", "test")
        assert "Echo: test" in result
    
    def test_run_nonexistent_tool(self, tool_registry):
        """Nicht vorhandenes Tool gibt Fehler zurück"""
        result = tool_registry.run("nonexistent", "data")
        assert "nicht gefunden" in result.lower() or "not found" in result.lower()


# ════════════════════════════════════════════════════════════════════════════
# SHELL TESTS
# ════════════════════════════════════════════════════════════════════════════

class TestShell:
    """Shell Tool Tests"""
    
    def test_allowed_commands_exist(self):
        """Allowed commands liste ist nicht leer"""
        assert len(ALLOWED_COMMANDS) > 0
        assert "ls" in ALLOWED_COMMANDS
    
    def test_blocked_patterns_exist(self):
        """Blocked patterns liste ist nicht leer"""
        assert len(BLOCKED_PATTERNS) > 0
        assert any("rm" in p.lower() for p in BLOCKED_PATTERNS)
    
    def test_empty_command_fails(self):
        """Leerer Befehl wird abgelehnt"""
        result = shell("")
        assert "❌" in result or "leer" in result.lower()
    
    def test_dangerous_command_blocked(self):
        """Gefährliche Befehle werden blockiert"""
        result = shell("rm -rf /")
        assert "blockiert" in result.lower() or "blocked" in result.lower()
    
    def test_allowed_command_executes(self):
        """Erlaubte Befehle können ausgeführt werden"""
        result = shell("echo test")
        # Should not contain error message
        assert "❌" not in result
    
    @pytest.mark.parametrize("cmd", [
        "rm -rf /",
        "mkfs /dev/sda",
        "shutdown -h now",
        "reboot",
        "del /s /q C:\\*",
    ])
    def test_dangerous_commands_blocked(self, cmd):
        """Alle gefährlichen Commands werden blockiert"""
        result = shell(cmd)
        assert "blockiert" in result.lower() or "blocked" in result.lower()


# ════════════════════════════════════════════════════════════════════════════
# FILE OPERATIONS TESTS
# ════════════════════════════════════════════════════════════════════════════

class TestFileOperations:
    """File Tool Tests"""
    
    def test_read_existing_file(self, temp_file):
        """Existierende Datei kann gelesen werden"""
        content = read_file(temp_file)
        assert "Test Content" in content
    
    def test_read_nonexistent_file(self):
        """Nicht vorhandene Datei gibt Fehler zurück"""
        result = read_file("/nonexistent/path/file.txt")
        assert "❌" in result or "nicht gefunden" in result.lower()
    
    def test_write_file(self, temp_dir):
        """Datei kann geschrieben werden"""
        file_path = os.path.join(temp_dir, "test.txt")
        result = write_file(file_path, "Test Content")
        assert "✅" in result or "schrieben" in result.lower()
        assert os.path.exists(file_path)
    
    def test_write_creates_directories(self, temp_dir):
        """Write erstellt fehlende Verzeichnisse"""
        nested_path = os.path.join(temp_dir, "nested", "deep", "file.txt")
        result = write_file(nested_path, "Test")
        assert os.path.exists(nested_path)
    
    def test_list_dir(self, temp_dir):
        """Verzeichnis kann aufgelistet werden"""
        write_file(os.path.join(temp_dir, "file1.txt"), "content")
        write_file(os.path.join(temp_dir, "file2.txt"), "content")
        result = list_dir(temp_dir)
        assert "file1.txt" in result or "file2.txt" in result


# ════════════════════════════════════════════════════════════════════════════
# LLM TESTS
# ════════════════════════════════════════════════════════════════════════════

class TestLLM:
    """LLM Model Tests"""
    
    def test_models_dict_exists(self):
        """MODELS dict existiert"""
        assert MODELS is not None
        assert isinstance(MODELS, dict)
    
    def test_required_models_present(self):
        """Alle erforderlichen Modelle sind present"""
        required = ["coder", "rag", "planner", "chat"]
        for model in required:
            assert model in MODELS
    
    def test_get_model_returns_string(self, llm):
        """get_model gibt einen String zurück"""
        model = llm.get_model("coder")
        assert isinstance(model, str)
        assert len(model) > 0
    
    def test_get_model_fallback(self, llm):
        """get_model fällt zu 'chat' zurück bei unbekanntem Mode"""
        model = llm.get_model("unknown")
        assert model == MODELS["chat"]


# ════════════════════════════════════════════════════════════════════════════
# AGENT TESTS
# ════════════════════════════════════════════════════════════════════════════

class TestAgents:
    """Agent Classes Tests"""
    
    def test_planner_agent_creation(self, planner):
        """PlannerAgent kann erstellt werden"""
        assert planner is not None
        assert planner.llm is not None
    
    def test_worker_agent_creation(self, worker):
        """WorkerAgent kann erstellt werden"""
        assert worker is not None
        assert worker.llm is not None
        assert worker.router is not None
        assert worker.tools is not None
    
    def test_reviewer_agent_creation(self, reviewer):
        """ReviewerAgent kann erstellt werden"""
        assert reviewer is not None
        assert reviewer.llm is not None
    
    @patch('core.llm.requests.post')
    def test_planner_returns_list(self, mock_post, planner):
        """PlannerAgent.plan gibt eine Liste zurück"""
        mock_post.return_value.json.return_value = {
            "message": {"content": "1. First task\n2. Second task\n3. Third task"}
        }
        
        result = planner.plan("Build a project")
        assert isinstance(result, list)
    
    @patch('core.llm.requests.post')
    def test_reviewer_returns_dict(self, mock_post, reviewer):
        """ReviewerAgent.review gibt ein Dict zurück"""
        mock_post.return_value.json.return_value = {
            "message": {"content": "APPROVED"}
        }
        
        result = reviewer.review("test task", "test output")
        assert isinstance(result, dict)
        assert "approved" in result
        assert "feedback" in result
        assert "status" in result


# ════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ════════════════════════════════════════════════════════════════════════════

class TestIntegration:
    """Integration Tests (Agent Pipeline)"""
    
    def test_full_agent_pipeline_components(self, llm, router, memory, task_queue, planner, worker, reviewer):
        """Alle Pipeline-Komponenten sind verfügbar"""
        assert llm is not None
        assert router is not None
        assert memory is not None
        assert task_queue is not None
        assert planner is not None
        assert worker is not None
        assert reviewer is not None
    
    def test_task_flow(self, task_queue):
        """Task-Flow funktioniert"""
        # Add
        task = task_queue.add("Implement feature X", priority=8)
        assert task["status"] == "pending"
        
        # Get
        next_task = task_queue.get_next()
        assert next_task["id"] == task["id"]
        
        # Complete
        task_queue.complete(task)
        assert task["status"] == "done"
    
    def test_memory_context_storage(self, memory):
        """Memory kann Kontext speichern"""
        memory.add_fact("Project uses Python", "arch-1")
        memory.add_fact("Uses ChromaDB for memory", "arch-2")
        results = memory.search("Project Python")
        assert isinstance(results, list)
    
    def test_tool_registry_full_suite(self, tool_registry):
        """Tool Registry kann mehrere Tools verwalten"""
        def echo_func(x):
            return f"Echo: {x}"
        
        def reverse_func(x):
            return x[::-1]
        
        tool_registry.register("echo", echo_func)
        tool_registry.register("reverse", reverse_func)
        
        assert len(tool_registry.list_tools()) >= 2
        
        result1 = tool_registry.run("echo", "hello")
        result2 = tool_registry.run("reverse", "hello")
        
        assert "hello" in result1
        assert "olleh" in result2


# ════════════════════════════════════════════════════════════════════════════
# PARAMETRIZED TESTS
# ════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("task,expected_route", [
    ("write a sorting function", "coder"),
    ("plan the system architecture", "planner"),
    ("find documentation", "rag"),
    ("general question", "chat"),
])
def test_router_parametrized(task, expected_route):
    """Parametrized routing test"""
    router = Router()
    result = router.route(task)
    assert result == expected_route


@pytest.mark.parametrize("priority", [1, 5, 10])
def test_task_priority_levels(priority):
    """Parametrized priority test"""
    queue = TaskQueue()
    task = queue.add("Test", priority=priority)
    assert task["priority"] == priority


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
