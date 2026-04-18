"""ChromaDB Memory Layer — Shared Memory für das Agent OS."""

import os
from datetime import datetime
import chromadb
from rich.console import Console

console = Console()


class Memory:
    """Vector Memory mit ChromaDB — speichert Facts, Tasks, Episodes mit Persistenz."""

    def __init__(self, persist_dir: str = "./chroma_data"):
        """Initialisiert ChromaDB mit Persistenz-Support.
        
        Args:
            persist_dir: Pfad für persistenten Datenspeicher (default: ./chroma_data)
        """
        # Erstelle Persistenz-Verzeichnis falls nicht vorhanden
        os.makedirs(persist_dir, exist_ok=True)
        
        # ── Wichtig: PersistentClient für Datenspeicherung ──
        # (Nicht chromadb.Client() das nur Im-Memory ist!)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.facts = self.client.get_or_create_collection("facts")
        self.tasks_mem = self.client.get_or_create_collection("tasks")
        self.episodes = self.client.get_or_create_collection("episodes")

    def add_fact(self, text: str, fact_id: str) -> None:
        """Speichert ein Fakt (Projektwissen, Entscheidung)."""
        self.facts.upsert(
            documents=[text],
            ids=[fact_id],
            metadatas=[{"timestamp": datetime.now().isoformat(), "type": "fact"}],
        )

    def add_episode(self, text: str, episode_id: str) -> None:
        """Speichert eine Episode (Verlauf / History)."""
        self.episodes.upsert(
            documents=[text],
            ids=[episode_id],
            metadatas=[{"timestamp": datetime.now().isoformat(), "type": "episode"}],
        )

    def search(self, query: str, n_results: int = 3) -> list[str]:
        """Sucht in allen Memory-Collections."""
        results = []
        for collection in [self.facts, self.tasks_mem, self.episodes]:
            try:
                res = collection.query(query_texts=[query], n_results=n_results)
                if res["documents"]:
                    results.extend(res["documents"][0])
            except Exception:
                pass
        return results

    def sync(self, text: str, sync_id: str) -> None:
        """Shared Memory Sync — speichert in Facts + Episodes."""
        self.add_fact(text, f"sync-fact-{sync_id}")
        self.add_episode(text, f"sync-ep-{sync_id}")
        console.print("[dim]🔗 Synced to shared memory layer[/dim]")
