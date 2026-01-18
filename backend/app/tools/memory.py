"""
Filesystem memory operations for agent coordination.

Provides persistent storage for agents to share data and coordinate
their work via the filesystem. Each session gets its own isolated
memory space.
"""

import json
import shutil
from pathlib import Path
from typing import Any, Optional, List, Dict
from datetime import datetime

from ..config import settings

MEMORY_BASE_PATH = settings.memory_base_path


def get_session_path(session_id: str) -> Path:
    """
    Get memory path for a session.

    Args:
        session_id: Unique identifier for the session

    Returns:
        Path object for the session's memory directory
    """
    path = MEMORY_BASE_PATH / session_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_to_memory(session_id: str, key: str, data: Any) -> str:
    """
    Save data to filesystem memory.

    Args:
        session_id: Session identifier
        key: Memory key (can be hierarchical: "research/agent_123")
        data: Data to save (must be JSON-serializable)

    Returns:
        File path where the data was saved

    Notes:
        - Hierarchical keys create nested directory structures
        - Automatically adds metadata (timestamp, key)
        - Uses JSON serialization with datetime support
    """
    session_path = get_session_path(session_id)
    file_path = session_path / f"{key}.json"
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Add metadata
    payload = {
        "data": data,
        "saved_at": datetime.utcnow().isoformat(),
        "key": key
    }

    with open(file_path, 'w') as f:
        json.dump(payload, f, indent=2, default=str)

    return str(file_path)


def read_from_memory(session_id: str, key: str) -> Optional[Any]:
    """
    Read data from filesystem memory.

    Args:
        session_id: Session identifier
        key: Memory key to retrieve

    Returns:
        The stored data, or None if key doesn't exist
    """
    session_path = get_session_path(session_id)
    file_path = session_path / f"{key}.json"

    if not file_path.exists():
        return None

    with open(file_path, 'r') as f:
        payload = json.load(f)

    return payload.get("data")


def list_memory_keys(session_id: str, prefix: str = "") -> List[str]:
    """
    List all memory keys for a session.

    Args:
        session_id: Session identifier
        prefix: Optional prefix filter (e.g., "research/" to get all research findings)

    Returns:
        Sorted list of memory keys
    """
    session_path = get_session_path(session_id)
    if not session_path.exists():
        return []

    keys = []
    for file_path in session_path.rglob("*.json"):
        key = str(file_path.relative_to(session_path)).replace(".json", "")
        if prefix == "" or key.startswith(prefix):
            keys.append(key)

    return sorted(keys)


def aggregate_research(session_id: str) -> Dict[str, Any]:
    """
    Aggregate all research findings from subagents.

    Reads all files under research/ prefix and combines them into
    a unified structure.

    Args:
        session_id: Session identifier

    Returns:
        Dictionary containing:
            - sources: list - All sources from all research agents
            - findings: list - All findings and summaries
            - total_sources: int - Total number of unique sources
    """
    research_keys = list_memory_keys(session_id, prefix="research/")

    aggregated = {
        "sources": [],
        "findings": [],
        "total_sources": 0
    }

    for key in research_keys:
        data = read_from_memory(session_id, key)
        if data:
            if "sources" in data:
                aggregated["sources"].extend(data["sources"])
            if "findings" in data:
                aggregated["findings"].append(data["findings"])
            if "summary" in data:
                aggregated["findings"].append(data["summary"])

    aggregated["total_sources"] = len(aggregated["sources"])
    return aggregated


def clear_session_memory(session_id: str) -> bool:
    """
    Delete all memory for a session.

    Args:
        session_id: Session identifier

    Returns:
        True if memory was deleted, False if session didn't exist
    """
    session_path = get_session_path(session_id)
    if session_path.exists():
        shutil.rmtree(session_path)
        return True
    return False
