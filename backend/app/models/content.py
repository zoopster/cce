"""
Content session and research models.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from .parameters import GenerationParameters


class SessionStatus(str, Enum):
    """Status of a content generation session."""

    CREATED = "created"
    RESEARCHING = "researching"
    GENERATING = "generating"
    READY_FOR_REVIEW = "ready_for_review"
    ITERATING = "iterating"
    PUBLISHED = "published"


class Complexity(str, Enum):
    """Complexity level determining agent count and tool usage."""

    SIMPLE = "simple"      # 1 subagent, 3-10 tool calls
    MODERATE = "moderate"  # 2-4 subagents, 10-15 tool calls each
    COMPLEX = "complex"    # 5-10 subagents, 15-20 tool calls each


class ResearchResult(BaseModel):
    """A single research finding from an agent."""

    source_url: str
    title: str
    snippet: str
    agent_id: str
    relevance_score: float = 0.0


class ContentVersion(BaseModel):
    """A version of generated content."""

    version_number: int
    content: str  # Markdown
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    feedback_applied: Optional[str] = None


class AgentState(BaseModel):
    """Current state of an agent for UI display."""

    agent_id: str
    agent_type: str  # lead, research, generator, iterator, publisher
    status: str      # planning, executing, waiting, complete, error
    current_task: str
    tool_calls: int = 0
    findings_count: int = 0


class ContentSession(BaseModel):
    """A complete content generation session."""

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str
    parameters: GenerationParameters
    status: SessionStatus = SessionStatus.CREATED
    complexity: Complexity = Complexity.MODERATE
    research_plan: Optional[str] = None
    research_results: List[ResearchResult] = Field(default_factory=list)
    versions: List[ContentVersion] = Field(default_factory=list)
    agents: List[AgentState] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
