"""Workspace Intelligence — Analysiert das Projekt und sammelt Context."""

import os
import json
from pathlib import Path
from typing import Any


class WorkspaceIntelligence:
    """Analysiert Projekt-Struktur, Git, Code-Quality, Dependencies."""
    
    def __init__(self, project_root: str = "."):
        self.root = Path(project_root)
    
    def analyze_project(self) -> dict:
        """Führt vollständige Projekt-Analyse durch."""
        return {
            "summary": self._get_summary(),
            "structure": self._analyze_structure(),
            "git": self._get_git_status(),
            "dependencies": self._read_requirements(),
            "code_stats": self._count_code(),
            "modules": self._analyze_modules(),
            "entry_points": self._find_entry_points(),
            "status": self._determine_status(),
        }
    
    def _get_summary(self) -> dict:
        """Kurze Zusammenfassung."""
        return {
            "project_name": "Agent OS v2.1",
            "project_type": "Python Agent System",
            "version": "2.1.0",
            "main_framework": "FastAPI + MCP + Ollama",
        }
    
    def _analyze_structure(self) -> dict:
        """Analysiert Verzeichnis-Struktur."""
        structure = {}
        main_dirs = ["core", "agents", "tools", "api", "memory", "tasks", "docs"]
        
        for dir_name in main_dirs:
            dir_path = self.root / dir_name
            if dir_path.exists():
                py_files = list(dir_path.glob("*.py"))
                structure[dir_name] = {
                    "files": len(py_files),
                    "file_names": [f.name for f in py_files]
                }
        
        return structure
    
    def _analyze_modules(self) -> list[str]:
        """Identifiziert Hauptmodule."""
        modules = []
        for module in ["core", "agents", "tools", "api", "memory", "tasks"]:
            if (self.root / module).exists():
                modules.append(module)
        return modules
    
    def _count_code(self) -> dict:
        """Zählt Lines of Code pro Modul."""
        stats = {}
        total_lines = 0
        total_files = 0
        
        for module in ["core", "agents", "tools", "api", "memory", "tasks"]:
            module_path = self.root / module
            if module_path.exists():
                py_files = list(module_path.glob("*.py"))
                lines = 0
                
                for py_file in py_files:
                    try:
                        with open(py_file) as f:
                            lines += len(f.readlines())
                    except:
                        pass
                
                if lines > 0:
                    stats[module] = {
                        "files": len(py_files),
                        "lines": lines,
                    }
                    total_lines += lines
                    total_files += len(py_files)
        
        stats["total"] = {"files": total_files, "lines": total_lines}
        return stats
    
    def _get_git_status(self) -> dict:
        """Prüft Git-Status."""
        git_info = {}
        
        try:
            # Letzter Commit
            result = os.popen("cd {} && git log --oneline -1 2>/dev/null".format(self.root)).read().strip()
            if result:
                git_info["latest_commit"] = result
            
            # Branch
            result = os.popen("cd {} && git branch --show-current 2>/dev/null".format(self.root)).read().strip()
            if result:
                git_info["current_branch"] = result
            
            # Status
            result = os.popen("cd {} && git status --short 2>/dev/null".format(self.root)).read().strip()
            git_info["changes"] = len(result.split("\n")) if result else 0
            
        except Exception as e:
            git_info["error"] = str(e)
        
        return git_info
    
    def _read_requirements(self) -> list[str]:
        """Liest requirements.txt."""
        req_file = self.root / "requirements.txt"
        if req_file.exists():
            with open(req_file) as f:
                return [line.strip() for line in f if line.strip() and not line.startswith("#")]
        return []
    
    def _find_entry_points(self) -> list[str]:
        """Findet Einstiegspunkte."""
        entry_points = []
        
        # CLI
        if (self.root / "run.py").exists():
            entry_points.append("CLI: python3 run.py")
        
        # MCP Server
        if (self.root / "mcp_server.py").exists():
            entry_points.append("MCP: python3 mcp_server.py")
        
        # API
        if (self.root / "api" / "kernel.py").exists():
            entry_points.append("API: uvicorn api.kernel:app --reload")
        
        return entry_points
    
    def _determine_status(self) -> dict:
        """Bestimmt Projekt-Status."""
        # Lese AUDIT_SUMMARY falls vorhanden
        audit_file = self.root / "AUDIT_SUMMARY.md"
        if audit_file.exists():
            with open(audit_file) as f:
                content = f.read()
                if "70%" in content:
                    return {"completion": "70%", "status": "In Development", "grade": "B+"}
        
        return {"completion": "60%", "status": "Active Development"}
    
    def format_for_llm(self) -> str:
        """Formatiert Analyse als LLM-Prompt."""
        analysis = self.analyze_project()
        
        prompt = f"""
# PROJECT CONTEXT

## Summary
- Name: {analysis['summary']['project_name']}
- Type: {analysis['summary']['project_type']}
- Version: {analysis['summary']['version']}

## Status
- Completion: {analysis['status'].get('completion', 'Unknown')}
- Grade: {analysis['status'].get('grade', 'Unknown')}

## Structure
- Modules: {', '.join(analysis['modules'])}
- Total Files: {analysis['code_stats'].get('total', {}).get('files', 0)}
- Total Lines: {analysis['code_stats'].get('total', {}).get('lines', 0)}

## Entry Points
{chr(10).join('- ' + ep for ep in analysis['entry_points'])}

## Key Dependencies
{chr(10).join('- ' + dep for dep in analysis['dependencies'][:5])}

## Recent Activity
- Latest Commit: {analysis['git'].get('latest_commit', 'Unknown')}
- Branch: {analysis['git'].get('current_branch', 'Unknown')}
- Pending Changes: {analysis['git'].get('changes', 0)}

## Code Statistics
"""
        for module, stats in analysis['code_stats'].items():
            if module != 'total':
                prompt += f"- {module}: {stats.get('lines', 0)} lines in {stats.get('files', 0)} files\n"
        
        return prompt


# ──── Global Instance ────────────────────────────────────────

workspace = WorkspaceIntelligence()


def get_project_context() -> str:
    """Gibt formatierte Projekt-Context für LLM."""
    return workspace.format_for_llm()


def get_project_summary() -> dict:
    """Gibt Projekt-Zusammenfassung."""
    analysis = workspace.analyze_project()
    return {
        "name": "Agent OS v2.1",
        "status": analysis['status'].get('completion', 'Unknown'),
        "modules": analysis['modules'],
        "code_stats": analysis['code_stats'],
        "entry_points": analysis['entry_points'],
        "dependencies": analysis['dependencies'],
    }
