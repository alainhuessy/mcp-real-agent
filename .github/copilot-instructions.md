# Agent OS v2.1 — Copilot Instructions

## Projekttyp
- Python 3.11+ Agent Operating System
- Lokale LLM-Inference via Ollama
- ChromaDB für Vector Memory
- FastAPI für API Kernel
- Rich für CLI Output

## Architektur
- Multi-Agent System (Planner / Worker / Reviewer)
- Plugin-basiertes Tool Registry
- Autonomer Task Scheduler
- Shared Memory Layer (ChromaDB)
- Model Routing (coder / rag / planner / chat)

## Regeln
- Kein Cloud-API Zugriff nötig
- Ollama läuft lokal auf http://localhost:11434
- Shell-Befehle werden über eine Allowlist geschützt
- Git-Automation nur mit expliziter Bestätigung
- Continue dient als IDE Execution Layer (nicht als Brain)
