"""Memory Manager: persistent JSON storage and session state for Feynman sessions."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from typing import Any

DEFAULT_MEMORY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory.json"
)
DEFAULT_WEAK_THRESHOLD = 7


def is_weak_topic(score: int, threshold: int = DEFAULT_WEAK_THRESHOLD) -> bool:
    """Check if a score falls below the weak topic threshold."""
    return score < threshold


class MemoryManager:
    """Manager for loading, saving, and querying Feynman session records."""

    def __init__(self, file_path: str = DEFAULT_MEMORY_PATH, weak_threshold: int = DEFAULT_WEAK_THRESHOLD):
        self.file_path = file_path
        self.weak_threshold = weak_threshold

    def load_memory(self) -> list[dict[str, Any]]:
        """Load session records from JSON file. Returns an empty list if file is missing or invalid."""
        if not os.path.exists(self.file_path):
            return []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Handle possible dict wrapped memory e.g. {"sessions": [...]}
                return data.get("sessions", [])
            return []
        except Exception:
            return []

    def save_memory(self, sessions: list[dict[str, Any]]) -> None:
        """Persist a list of session records to the JSON file."""
        os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False)

    def save_session(self, session_data: dict[str, Any]) -> dict[str, Any]:
        """Save a new learning session or update an existing one."""
        sessions = self.load_memory()

        record = dict(session_data)
        if "id" not in record or not record["id"]:
            record["id"] = f"session_{uuid.uuid4().hex[:8]}"

        if "timestamp" not in record or not record["timestamp"]:
            record["timestamp"] = datetime.now().isoformat()

        score = record.get("score", 5)
        record["is_weak"] = is_weak_topic(score, self.weak_threshold)

        # Update if ID exists, otherwise append
        existing_index = next((i for i, s in enumerate(sessions) if s.get("id") == record["id"]), None)
        if existing_index is not None:
            sessions[existing_index] = record
        else:
            sessions.append(record)

        self.save_memory(sessions)
        return record

    def get_weak_topics(self) -> list[dict[str, Any]]:
        """Retrieve all sessions marked as weak topics."""
        sessions = self.load_memory()
        return [s for s in sessions if s.get("is_weak") or is_weak_topic(s.get("score", 10), self.weak_threshold)]

    def get_session_by_id(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve a specific session record by ID."""
        for s in self.load_memory():
            if s.get("id") == session_id:
                return s
        return None

    def delete_session(self, session_id: str) -> bool:
        """Delete a session record by ID."""
        sessions = self.load_memory()
        filtered = [s for s in sessions if s.get("id") != session_id]
        if len(filtered) < len(sessions):
            self.save_memory(filtered)
            return True
        return False

    def clear_memory(self) -> None:
        """Clear all stored session records."""
        self.save_memory([])


# Module-level convenience functions
def load_memory(file_path: str = DEFAULT_MEMORY_PATH) -> list[dict[str, Any]]:
    return MemoryManager(file_path).load_memory()


def save_session(session_data: dict[str, Any], file_path: str = DEFAULT_MEMORY_PATH, weak_threshold: int = DEFAULT_WEAK_THRESHOLD) -> dict[str, Any]:
    return MemoryManager(file_path, weak_threshold).save_session(session_data)


def get_weak_topics(file_path: str = DEFAULT_MEMORY_PATH, weak_threshold: int = DEFAULT_WEAK_THRESHOLD) -> list[dict[str, Any]]:
    return MemoryManager(file_path, weak_threshold).get_weak_topics()


def get_session_by_id(session_id: str, file_path: str = DEFAULT_MEMORY_PATH) -> dict[str, Any] | None:
    return MemoryManager(file_path).get_session_by_id(session_id)
