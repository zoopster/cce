"""
Session management endpoints.

Handles CRUD operations for content creation sessions.
"""

from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from ..models.content import ContentSession, SessionStatus, Complexity, AgentState
from ..models.parameters import GenerationParameters
from ..tools.memory import save_to_memory, read_from_memory, clear_session_memory

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

# In-memory session store (for simplicity)
# In production, use a proper database
sessions: Dict[str, ContentSession] = {}


class CreateSessionRequest(BaseModel):
    """Request body for creating a new session."""
    topic: str
    source_url: Optional[str] = None
    parameters: Optional[GenerationParameters] = None


class CreateSessionResponse(BaseModel):
    """Response for successful session creation."""
    session_id: str
    topic: str
    status: str
    complexity: str
    created_at: datetime


@router.post("", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """
    Create a new content creation session.

    Returns session metadata including unique session_id.
    """
    session = ContentSession(
        session_id=str(uuid.uuid4()),
        topic=request.topic,
        source_url=request.source_url,
        parameters=request.parameters or GenerationParameters()
    )
    sessions[session.session_id] = session

    # Save to memory
    save_to_memory(session.session_id, "session", session.model_dump())

    return CreateSessionResponse(
        session_id=session.session_id,
        topic=session.topic,
        status=session.status.value,
        complexity=session.complexity.value,
        created_at=session.created_at
    )


@router.get("/{session_id}")
async def get_session(session_id: str):
    """
    Get comprehensive session details.

    Returns session metadata, agent states, research count, and version count.
    """
    session = sessions.get(session_id)
    if not session:
        # Try to load from memory
        session_data = read_from_memory(session_id, "session")
        if session_data:
            session = ContentSession(**session_data)
            sessions[session_id] = session
        else:
            raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session.session_id,
        "topic": session.topic,
        "status": session.status.value if isinstance(session.status, Enum) else session.status,
        "complexity": session.complexity.value if isinstance(session.complexity, Enum) else session.complexity,
        "parameters": session.parameters.model_dump(),
        "research_results_count": len(session.research_results),
        "versions_count": len(session.versions),
        "agents": [a.model_dump() for a in session.agents],
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat()
    }


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session and all its associated memory.

    This operation is irreversible.
    """
    if session_id in sessions:
        del sessions[session_id]
    clear_session_memory(session_id)
    return {"status": "deleted", "session_id": session_id}


@router.get("/{session_id}/agents")
async def get_agent_states(session_id: str) -> List[Dict[str, Any]]:
    """
    Get real-time agent states for UI display.

    Shows status, current task, and progress for all active agents.
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return [a.model_dump() for a in session.agents]


@router.get("/{session_id}/versions")
async def get_versions(session_id: str):
    """
    Get all content versions for a session.

    Returns metadata for each version with content preview.
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "versions": [
            {
                "version_number": v.version_number,
                "generated_at": v.generated_at.isoformat(),
                "feedback_applied": v.feedback_applied,
                "content_preview": v.content[:500] + "..." if len(v.content) > 500 else v.content
            }
            for v in session.versions
        ]
    }


@router.get("/{session_id}/content")
async def get_current_content(session_id: str):
    """
    Get the current (latest) content version.

    Returns full content of the most recent version.
    """
    session = sessions.get(session_id)
    if not session:
        # Try loading from memory
        session_data = read_from_memory(session_id, "session")
        if session_data:
            session = ContentSession(**session_data)
            sessions[session_id] = session
        else:
            raise HTTPException(status_code=404, detail="Session not found")

    # Check in-memory versions first
    if session.versions:
        latest = session.versions[-1]
        return {
            "session_id": session_id,
            "version_number": latest.version_number,
            "content": latest.content,
            "generated_at": latest.generated_at.isoformat(),
            "feedback_applied": latest.feedback_applied
        }

    # Fall back to filesystem
    for i in range(10, 0, -1):
        version_data = read_from_memory(session_id, f"versions/v{i}")
        if version_data:
            return {
                "session_id": session_id,
                "version_number": version_data["version_number"],
                "content": version_data["content"],
                "generated_at": version_data["generated_at"],
                "feedback_applied": version_data.get("feedback_applied")
            }

    raise HTTPException(status_code=404, detail="No content generated yet")
