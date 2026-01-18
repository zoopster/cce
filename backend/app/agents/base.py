"""
Base agent class with memory management capabilities.
"""

import json
import uuid
from pathlib import Path
from typing import Any, List, Optional

from anthropic import Anthropic

from ..models import AgentState


class BaseAgent:
    """Base class for all agents with memory operations."""

    def __init__(self, session_id: str, agent_id: str = None):
        """
        Initialize a base agent.

        Args:
            session_id: The session this agent belongs to
            agent_id: Optional unique identifier for this agent
        """
        self.session_id = session_id
        self.agent_id = agent_id or str(uuid.uuid4())
        self.client = Anthropic()
        self.memory_path = Path(f"app/memory/{session_id}")
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.tool_calls = 0
        self.status = "created"

    def save_to_memory(self, key: str, data: Any) -> None:
        """
        Save data to filesystem memory.

        Args:
            key: The memory key (can include / for nested structure)
            data: Data to save (will be JSON serialized)
        """
        file_path = self.memory_path / f"{key}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def read_from_memory(self, key: str) -> Optional[Any]:
        """
        Read data from filesystem memory.

        Args:
            key: The memory key to read

        Returns:
            The stored data or None if not found
        """
        file_path = self.memory_path / f"{key}.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return None

    def list_memory_keys(self, prefix: str = "") -> List[str]:
        """
        List all memory keys with optional prefix filter.

        Args:
            prefix: Optional prefix to filter keys

        Returns:
            List of matching memory keys
        """
        keys = []
        for file_path in self.memory_path.rglob("*.json"):
            key = str(file_path.relative_to(self.memory_path)).replace(".json", "")
            if key.startswith(prefix):
                keys.append(key)
        return keys

    def get_state(self) -> AgentState:
        """
        Get current agent state for UI display.

        Returns:
            Current state of this agent
        """
        return AgentState(
            agent_id=self.agent_id,
            agent_type=self.__class__.__name__.lower().replace("agent", ""),
            status=self.status,
            current_task=getattr(self, 'current_task', ''),
            tool_calls=self.tool_calls,
            findings_count=len(self.list_memory_keys("research/"))
        )
