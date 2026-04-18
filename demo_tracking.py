#!/usr/bin/env python3
"""
Demo: Live Tracking mit agent_run_task_tracked
"""

import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

from core.llm import LLM
from core.router import Router
from memory.memory import Memory
from tools.registry import ToolRegistry
from agents.worker import WorkerAgent

def main():
    print("\n" + "="*80)
    print("🎯 AGENT TRACKING DEMO")
    print("="*80)
    
    # Initialize
    llm = LLM()
    router = Router()
    memory = Memory()
    tools = ToolRegistry()
    worker = WorkerAgent(llm, router, tools)
    
    # Demo task
    task = "Create a Python function that checks if a number is prime"
    
    print(f"\nTask: {task}\n")
    print("-" * 80)
    
    # Execute with tracking
    result = worker.tracked_execute(
        task,
        memory.search(task),
        show_progress=True
    )
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE")
    print("="*80)
    print(f"\nFinal Result:\n{result}\n")

if __name__ == "__main__":
    main()
