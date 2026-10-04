"""Memory Manager: saves/loads completed sessions and marks weak topics,
using plain JSON file storage (no database), per PRD FR-10 and FR-11."""
from __future__ import annotations

import json
import os
from datetime import datetime

# memory.json lives at the project root (see PRD section 6.3), one level
# up from this services/ folder.
MEMORY_PATH = os.path.join(os.path.dirname(__file__), "..", "memory.json")

WEAK_SCORE_THRESHOLD = 6  # scores below this are marked weak (FR-11)


def _read_raw() -> dict:
    """Reads memory.json safely. Returns {"sessions": []} if missing or corrupt."""
    if not os.path.exists(MEMORY_PATH):
        return {"sessions": []}
    try:
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"sessions": []}

    if not isinstance(data, dict) or "sessions" not in data or not isinstance(data["sessions"], list):
        return {"sessions": []}
    return data


def _write_raw(data: dict) -> None:
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_sessions() -> list[dict]:
    """Returns all saved sessions, most recent last."""
    return _read_raw()["sessions"]


def save_session(record: dict) -> dict:
    """
    Saves a completed session record and marks it weak if its score is
    below the threshold (FR-10, FR-11).

    `record` should include at least: topic, level, clarity_score (or score).
    Adds/overwrites "date" and "weak" if not already present, then persists
    to memory.json. Returns the final saved record.
    """
    score = record.get("clarity_score", record.get("score", 0))

    saved_record = {
        "topic": record.get("topic", "Untitled topic"),
        "level": record.get("level", ""),
        "score": score,
        "date": record.get("date") or datetime.now().strftime("%Y-%m-%d %H:%M"),
        "weak": record.get("weak", score < WEAK_SCORE_THRESHOLD),
    }

    data = _read_raw()
    data["sessions"].append(saved_record)
    _write_raw(data)
    return saved_record


def get_weak_topics() -> list[dict]:
    """Returns all sessions currently marked weak (FR-11)."""
    return [s for s in load_sessions() if s.get("weak")]

