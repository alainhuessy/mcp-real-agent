# 🛠️ FEATURE IMPLEMENTATION GUIDE — Top 5 Verbesserungen

**Goal:** Mache deinen Agent noch intelligenter wie GitHub Copilot  
**Timeline:** 4-5 Stunden für Top 2 Features (Quick Wins)  
**Difficulty:** Easy-Medium

---

## 🎯 FEATURE 1: WORKSPACE INTELLIGENCE (2-3 Hours) ⭐ START HERE

### Was ist das?
Dein Agent wird "aware" von deinem Projekt:
- Versteht Dependencies
- Kennt Projektstruktur
- Weiß über Entry Points
- Analysiert Python-Module

### Schritt 1.1: Neues Tool erstellen

**File:** `tools/workspace.py` (NEW)

```python
"""Workspace Intelligence — Agent versteht dein Projekt."""

import os
import json
from pathlib import Path
from rich.console import Console

console = Console()


def analyze_project_structure(root_path: str = ".") -> dict:
    """Analysiert die Projektstruktur komplett."""
    
    structure = {
        "project_type": None,
        "dependencies": {},
        "python_files": [],
        "entry_points": [],
        "config_files": [],
        "total_lines_of_code": 0,
        "main_modules": [],
    }
    
    # 1. Erkenne Project Type
    if os.path.exists(os.path.join(root_path, "pyproject.toml")):
        structure["project_type"] = "poetry"
    elif os.path.exists(os.path.join(root_path, "setup.py")):
        structure["project_type"] = "setuptools"
    elif os.path.exists(os.path.join(root_path, "requirements.txt")):
        structure["project_type"] = "pip"
    elif os.path.exists(os.path.join(root_path, "Pipfile")):
        structure["project_type"] = "pipenv"
    else:
        structure["project_type"] = "unknown"
    
    # 2. Parse Dependencies
    if os.path.exists(os.path.join(root_path, "requirements.txt")):
        with open(os.path.join(root_path, "requirements.txt")) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "==" in line:
                    package, version = line.split("==")
                    structure["dependencies"][package] = version
    
    # 3. Finde alle Python Files
    for root, dirs, files in os.walk(root_path):
        # Skip: .git, __pycache__, venv, .venv
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', '.venv', '.pytest_cache']]
        
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                relative_path = os.path.relpath(filepath, root_path)
                structure["python_files"].append(relative_path)
                
                # Count lines of code
                try:
                    with open(filepath) as f:
                        structure["total_lines_of_code"] += len(f.readlines())
                except:
                    pass
    
    # 4. Identifiziere Entry Points
    potential_entry_points = ["main.py", "app.py", "run.py", "__main__.py", "cli.py"]
    for entry in potential_entry_points:
        if os.path.exists(os.path.join(root_path, entry)):
            structure["entry_points"].append(entry)
    
    # 5. Finde Config Files
    config_patterns = [
        "setup.py", "setup.cfg", "pyproject.toml", "requirements.txt",
        ".env", ".env.example", "config.yml", "config.yaml",
        "Makefile", ".github/workflows"
    ]
    for config in config_patterns:
        if os.path.exists(os.path.join(root_path, config)):
            structure["config_files"].append(config)
    
    # 6. Finde Main Modules (top-level directories with __init__.py)
    for item in os.listdir(root_path):
        item_path = os.path.join(root_path, item)
        if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "__init__.py")):
            if not item.startswith(('.', '_')):
                structure["main_modules"].append(item)
    
    return structure


def get_project_summary(root_path: str = ".") -> str:
    """Gibt eine Human-Readable Zusammenfassung."""
    structure = analyze_project_structure(root_path)
    
    summary = f"""
📦 PROJECT STRUCTURE ANALYSIS
═════════════════════════════

📝 Project Type: {structure['project_type']}
📊 Total Lines of Code: {structure['total_lines_of_code']:,}
🐍 Python Files: {len(structure['python_files'])}
📚 Main Modules: {', '.join(structure['main_modules']) or 'None'}

🔧 Dependencies ({len(structure['dependencies'])})
{json.dumps(structure['dependencies'], indent=2)}

🚀 Entry Points
{chr(10).join(f"  • {ep}" for ep in structure['entry_points']) or "  None found"}

📋 Config Files
{chr(10).join(f"  • {cf}" for cf in structure['config_files']) or "  None found"}
"""
    return summary


def get_module_structure(root_path: str = ".") -> str:
    """Gibt Struktur aller Module aus."""
    structure = analyze_project_structure(root_path)
    
    modules_info = "📦 MODULE STRUCTURE\n" + "═" * 40 + "\n\n"
    
    for module in structure["main_modules"]:
        module_path = os.path.join(root_path, module)
        py_files = [f for f in os.listdir(module_path) if f.endswith(".py")]
        modules_info += f"📁 {module}/\n"
        for py_file in py_files:
            modules_info += f"   ├─ {py_file}\n"
        modules_info += "\n"
    
    return modules_info
```

**Status:** ☐ TODO

---

### Schritt 1.2: Tool in Registry registrieren

**File:** `core/agent.py`

**Zu modifizieren:** `_register_default_tools()` Method

```python
    def _register_default_tools(self):
        """Registriert Standard-Tools."""
        from tools.shell import shell
        from tools.file import read_file, write_file, list_dir
        from tools.git import git_status, git_commit, git_log
        from tools.workspace import analyze_project_structure, get_project_summary  # ADD THIS

        self.tools.register("shell", shell, "Execute shell commands")
        self.tools.register("read_file", read_file, "Read a file")
        self.tools.register("write_file", write_file, "Write to a file")
        self.tools.register("list_dir", list_dir, "List directory contents")
        self.tools.register("git_status", git_status, "Check git status")
        self.tools.register("git_commit", git_commit, "Commit changes")
        self.tools.register("git_log", git_log, "Show git log")
        
        # ADD THESE:
        self.tools.register("analyze_workspace", 
                           analyze_project_structure, 
                           "Analyze project structure")
        self.tools.register("workspace_summary", 
                           get_project_summary, 
                           "Get project summary")
```

**Status:** ☐ TODO

---

### Schritt 1.3: MCP Tools hinzufügen

**File:** `mcp_server.py`

**Location:** In `@server.list_tools()`, nach "# ── System ──"

```python
        # ── Workspace Intelligence ──
        Tool(
            name="analyze_workspace",
            description=(
                "Analyze the project structure and understand dependencies, "
                "modules, entry points, and configuration."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "root_path": {
                        "type": "string",
                        "description": "Project root path (default: current dir)",
                        "default": ".",
                    }
                },
            },
        ),
        Tool(
            name="workspace_summary",
            description=(
                "Get a human-readable summary of the project structure. "
                "Useful for understanding what the project does."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "root_path": {
                        "type": "string",
                        "description": "Project root path (default: current dir)",
                        "default": ".",
                    }
                },
            },
        ),
```

**Status:** ☐ TODO

---

### Schritt 1.4: Tool Handler in MCP

**File:** `mcp_server.py`

**Location:** In `_execute_tool()`, vor "return ❌ Unbekanntes Tool"

```python
    # ── Workspace ──
    if name == "analyze_workspace":
        from tools.workspace import analyze_project_structure
        result = analyze_project_structure(args.get("root_path", "."))
        return json.dumps(result, indent=2)
    
    if name == "workspace_summary":
        from tools.workspace import get_project_summary
        result = get_project_summary(args.get("root_path", "."))
        return result
```

**Status:** ☐ TODO

---

### Schritt 1.5: Test!

```bash
# MCP Server starten
python mcp_server.py

# In Continue IDE:
/analyze_workspace

# Expected Output:
# {
#   "project_type": "pip",
#   "total_lines_of_code": 5432,
#   "dependencies": {...},
#   ...
# }

/workspace_summary

# Expected Output:
# 📦 PROJECT STRUCTURE ANALYSIS
# ═════════════════════════════
# 📝 Project Type: pip
# 📊 Total Lines: 5,432
# ...
```

**Status:** ☐ TODO

---

## 🎯 FEATURE 2: ERROR DETECTION (1.5-2 Hours) ⭐ QUICK WIN

### Was ist das?
Agent findet Bugs & Security Issues VOR Ausführung

### Schritt 2.1: Dependencies installieren

```bash
pip install flake8 bandit mypy pylint
```

**Status:** ☐ TODO

---

### Schritt 2.2: Linter Tool erstellen

**File:** `tools/linter.py` (NEW)

```python
"""Code Quality Analysis — Findet Bugs, Security Issues, Style Problems."""

import subprocess
import tempfile
import os
from rich.console import Console

console = Console()


def analyze_code_quality(code: str, language: str = "python") -> dict:
    """Analysiert Code auf Fehler, Security Issues, und Style Problems."""
    
    if language != "python":
        return {"error": "Currently only Python is supported"}
    
    analysis = {
        "errors": [],
        "warnings": [],
        "security_issues": [],
        "style_issues": [],
        "type_issues": [],
        "summary": None,
    }
    
    # Schreibe Code in tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        # 1. FLAKE8 (Style + Basic Errors)
        try:
            result = subprocess.run(
                ["flake8", temp_path, "--max-line-length=100"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            for line in result.stdout.split("\n"):
                if not line.strip():
                    continue
                if "E" in line and line[line.index(":")+1] == "":  # Error
                    analysis["errors"].append(line)
                elif "W" in line:  # Warning
                    analysis["warnings"].append(line)
                elif "C" in line:  # Complexity
                    analysis["style_issues"].append(line)
        except subprocess.TimeoutExpired:
            analysis["warnings"].append("Flake8 timeout")
        except FileNotFoundError:
            analysis["warnings"].append("Flake8 not installed")
        except Exception as e:
            pass
        
        # 2. BANDIT (Security Analysis)
        try:
            result = subprocess.run(
                ["bandit", temp_path, "-f", "json"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            import json
            try:
                bandit_output = json.loads(result.stdout)
                for issue in bandit_output.get("results", []):
                    analysis["security_issues"].append(
                        f"[{issue['severity']}] {issue['issue_text']}"
                    )
            except:
                pass
        except FileNotFoundError:
            pass
        except Exception as e:
            pass
        
        # 3. PYLINT (Deep Analysis)
        try:
            result = subprocess.run(
                ["pylint", temp_path, "--disable=all", "--enable=E,F"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            for line in result.stdout.split("\n"):
                if "error" in line.lower():
                    analysis["errors"].append(line)
        except FileNotFoundError:
            pass
        except Exception as e:
            pass
        
        # 4. MYPY (Type Checking)
        try:
            result = subprocess.run(
                ["mypy", temp_path, "--ignore-missing-imports"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            for line in result.stdout.split("\n"):
                if "error" in line.lower():
                    analysis["type_issues"].append(line)
        except FileNotFoundError:
            pass
        except Exception as e:
            pass
        
        # Generate Summary
        total_issues = (
            len(analysis["errors"]) +
            len(analysis["security_issues"]) +
            len(analysis["warnings"]) +
            len(analysis["style_issues"])
        )
        
        analysis["summary"] = f"Found {total_issues} issues"
        if analysis["security_issues"]:
            analysis["summary"] += f" ({len(analysis['security_issues'])} CRITICAL security issues!)"
    
    finally:
        os.unlink(temp_path)
    
    return analysis


def get_quality_report(code: str) -> str:
    """Gibt einen Human-Readable Quality Report."""
    analysis = analyze_code_quality(code)
    
    report = "🔍 CODE QUALITY ANALYSIS\n" + "═" * 50 + "\n\n"
    
    if analysis.get("security_issues"):
        report += "🚨 SECURITY ISSUES:\n"
        for issue in analysis["security_issues"]:
            report += f"  ❌ {issue}\n"
        report += "\n"
    
    if analysis.get("errors"):
        report += "❌ ERRORS:\n"
        for error in analysis["errors"][:5]:
            report += f"  ❌ {error}\n"
        report += "\n"
    
    if analysis.get("warnings"):
        report += "⚠️  WARNINGS:\n"
        for warning in analysis["warnings"][:5]:
            report += f"  ⚠️  {warning}\n"
        report += "\n"
    
    if analysis.get("style_issues"):
        report += "🎨 STYLE ISSUES:\n"
        for style in analysis["style_issues"][:5]:
            report += f"  • {style}\n"
        report += "\n"
    
    if not any([analysis.get("security_issues"), analysis.get("errors"), 
                analysis.get("warnings"), analysis.get("style_issues")]):
        report += "✅ CODE LOOKS GOOD!\n"
    
    return report
```

**Status:** ☐ TODO

---

### Schritt 2.3: MCP Tool hinzufügen

**File:** `mcp_server.py`

```python
        # ── Code Quality ──
        Tool(
            name="analyze_code_quality",
            description=(
                "Analyze Python code for errors, security issues, style problems. "
                "Helps catch bugs before execution."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to analyze",
                    }
                },
                "required": ["code"],
            },
        ),
```

**Status:** ☐ TODO

---

### Schritt 2.4: Tool Handler

**File:** `mcp_server.py`, in `_execute_tool()`

```python
    if name == "analyze_code_quality":
        from tools.linter import get_quality_report
        code = args["code"]
        report = get_quality_report(code)
        return report
```

**Status:** ☐ TODO

---

### Schritt 2.5: Test!

```bash
# In Continue:

/analyze_code_quality "except:"

# Expected:
# 🔍 CODE QUALITY ANALYSIS
# ═══════════════════════
# ❌ ERRORS:
#   ❌ bare except clause
# ⚠️ WARNINGS:
#   ⚠️ Invalid syntax
```

**Status:** ☐ TODO

---

## 🎯 FEATURE 3: DOCUMENTATION GENERATION (1-2 Hours)

### Schritt 3.1: Doc Generator Tool

**File:** `tools/docgen.py` (NEW)

```python
"""Documentation Generation — Generiert Docstrings, Tests, Comments."""

import re


def generate_docstring(function_code: str, style: str = "google") -> str:
    """Generiert einen Docstring für eine Funktion."""
    
    # Simple Parser für Function Signature
    match = re.search(r'def\s+(\w+)\s*\((.*?)\)\s*->\s*(\w+)?:', function_code)
    if not match:
        return "# Could not parse function"
    
    func_name = match.group(1)
    params = match.group(2).split(",")
    return_type = match.group(3) or "Any"
    
    params_clean = [p.strip().split(":")[0].strip() for p in params if p.strip()]
    
    if style == "google":
        docstring = f'''"""
    {func_name} - [Add description here]
    
    Args:
{chr(10).join(f"        {p} (type): Description" for p in params_clean if p)}
    
    Returns:
        {return_type}: Description
    """'''
    
    elif style == "numpy":
        docstring = f'''"""
    {func_name}
    
    [Add description here]
    
    Parameters
    ----------
{chr(10).join(f"    {p} : type" for p in params_clean if p)}
    
    Returns
    -------
    {return_type}
        Description
    """'''
    
    else:  # rst
        docstring = f'''"""
    :param {', '.join(params_clean)}: Description
    :return: Description
    :rtype: {return_type}
    """'''
    
    return docstring


def generate_test_template(function_code: str) -> str:
    """Generiert einen Unit Test Template."""
    
    match = re.search(r'def\s+(\w+)\s*\((.*?)\):', function_code)
    if not match:
        return "# Could not parse function"
    
    func_name = match.group(1)
    
    template = f'''import pytest
from module_name import {func_name}


class Test{func_name.capitalize()}:
    """Tests for {func_name} function."""
    
    def test_{func_name}_basic(self):
        """Test basic functionality."""
        # Arrange
        # Act
        # Assert
        pass
    
    def test_{func_name}_edge_cases(self):
        """Test edge cases."""
        pass
    
    def test_{func_name}_error_handling(self):
        """Test error handling."""
        pass
'''
    
    return template
```

**Status:** ☐ TODO

---

### Schritt 3.2: MCP Tools

```python
        Tool(
            name="generate_docstring",
            description="Generate a docstring for a Python function.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Function code"},
                    "style": {
                        "type": "string",
                        "description": "Style: google, numpy, rst",
                        "default": "google",
                    }
                },
                "required": ["code"],
            },
        ),
        Tool(
            name="generate_tests",
            description="Generate unit test template for a function.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Function code"}
                },
                "required": ["code"],
            },
        ),
```

**Status:** ☐ TODO

---

## ✅ COMPLETION CHECKLIST

### Feature 1: Workspace Intelligence
- [ ] Create `tools/workspace.py`
- [ ] Add methods to `core/agent.py`
- [ ] Add MCP tools to `mcp_server.py`
- [ ] Add handlers to `_execute_tool()`
- [ ] Test: `/analyze_workspace`
- [ ] Test: `/workspace_summary`

### Feature 2: Error Detection
- [ ] Install: `pip install flake8 bandit mypy`
- [ ] Create `tools/linter.py`
- [ ] Add MCP tool to `mcp_server.py`
- [ ] Add handler to `_execute_tool()`
- [ ] Test: `/analyze_code_quality "bad code"`

### Feature 3: Documentation
- [ ] Create `tools/docgen.py`
- [ ] Add MCP tools to `mcp_server.py`
- [ ] Add handlers to `_execute_tool()`
- [ ] Test: `/generate_docstring "def my_func..."`
- [ ] Test: `/generate_tests "def my_func..."`

---

## 🚀 QUICK START

**Estimated Time for ALL 3 Features: 3-4 Hours**

1. Start mit Feature 1 (Workspace) — 2h
2. Then Feature 2 (Linter) — 1h
3. Then Feature 3 (Docgen) — 1h
4. Test everything
5. Commit changes

**Expected Result:**
- Agent versteht dein Projekt ✅
- Agent findet Bugs ✅
- Agent generiert Docs ✅

---

**Nächste Schritte:**
1. Öffne `tools/workspace.py` (neie Datei)
2. Kopiere den Code von Schritt 1.1
3. Folge der Checkliste
4. Test nach jedem Step
5. 🎉 Du hast 3x besseren Agent!

