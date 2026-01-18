"""
Content generation endpoints with SSE streaming.

Handles initial content generation and iterative refinement.
"""

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import AsyncGenerator
import json

from ..agents.generator import ContentGeneratorAgent
from ..agents.iterator import IteratorAgent
from ..models.content import ContentSession, SessionStatus, ContentVersion
from .sessions import sessions

router = APIRouter(prefix="/api/sessions", tags=["generate"])


async def generate_event_generator(session: ContentSession) -> AsyncGenerator[dict, None]:
    """
    Generate SSE events during content generation.

    Streams outline first, then content generation in real-time.
    """
    generator = ContentGeneratorAgent(session)
    session.agents.append(generator.get_state())

    yield {
        "event": "status",
        "data": json.dumps({
            "phase": "generating",
            "message": "Starting content generation..."
        })
    }

    # Stream the generation process
    async for chunk in generator.generate_stream():
        if chunk.startswith("[OUTLINE]"):
            # Extract outline content
            outline_content = chunk.replace("[OUTLINE]\n", "")
            yield {
                "event": "outline",
                "data": json.dumps({
                    "content": outline_content,
                    "message": "Content outline created"
                })
            }
        elif chunk.startswith("[CONTENT]"):
            yield {
                "event": "content_start",
                "data": json.dumps({
                    "message": "Generating content..."
                })
            }
        else:
            # Stream content chunks
            yield {
                "event": "content",
                "data": json.dumps({"chunk": chunk})
            }

    # Update session status
    session.status = SessionStatus.READY_FOR_REVIEW

    # Add version to session (it's saved in the agent's generate_stream)
    version_num = len(session.versions)
    if version_num > 0:
        # Read the saved version back
        from ..tools.memory import read_from_memory
        version_data = read_from_memory(session.session_id, f"versions/v{version_num}")
        if version_data:
            version = ContentVersion(
                version_number=version_data["version_number"],
                content=version_data["content"],
                generated_at=version_data["generated_at"]
            )
            # Only append if not already in session
            if not any(v.version_number == version_num for v in session.versions):
                session.versions.append(version)

    yield {
        "event": "complete",
        "data": json.dumps({
            "status": "complete",
            "version": len(session.versions),
            "message": "Content generation complete"
        })
    }


@router.post("/{session_id}/generate")
async def generate_content(session_id: str):
    """
    Generate content from research (SSE streaming).

    Requires research to be completed first.

    Returns an event stream with:
    - status: Phase updates
    - outline: Content structure/outline
    - content_start: Beginning of content generation
    - content: Streaming content chunks
    - complete: Generation finished
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Validate that research is complete
    if session.status not in ["ready_for_generation", "ready_for_review", "iterating"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot generate: session must have completed research first (current status: {session.status.value})"
        )

    session.status = SessionStatus.GENERATING

    return EventSourceResponse(generate_event_generator(session))


class IterateRequest(BaseModel):
    """Request body for content iteration."""
    feedback: str


async def iterate_event_generator(session: ContentSession, feedback: str) -> AsyncGenerator[dict, None]:
    """
    Generate SSE events during content iteration.

    Streams feedback analysis, optional research, and revised content.
    """
    iterator = IteratorAgent(session)
    session.agents.append(iterator.get_state())

    yield {
        "event": "status",
        "data": json.dumps({
            "phase": "iterating",
            "message": "Processing feedback..."
        })
    }

    # Stream the iteration process
    async for chunk in iterator.iterate_stream(feedback):
        if chunk.startswith("[ANALYSIS]"):
            # Extract analysis content
            analysis_content = chunk.replace("[ANALYSIS]\n", "")
            yield {
                "event": "analysis",
                "data": json.dumps({
                    "content": analysis_content,
                    "message": "Feedback analyzed"
                })
            }
        elif chunk.startswith("[RESEARCHING"):
            yield {
                "event": "status",
                "data": json.dumps({
                    "phase": "researching",
                    "message": "Gathering additional information..."
                })
            }
        elif chunk.startswith("[RESEARCH COMPLETE]"):
            yield {
                "event": "status",
                "data": json.dumps({
                    "phase": "revising",
                    "message": "Additional research complete, revising content..."
                })
            }
        elif chunk.startswith("[REVISED"):
            yield {
                "event": "content_start",
                "data": json.dumps({
                    "message": "Generating revised content..."
                })
            }
        else:
            # Stream revised content chunks
            yield {
                "event": "content",
                "data": json.dumps({"chunk": chunk})
            }

    # Update session status
    session.status = SessionStatus.READY_FOR_REVIEW

    # Add version to session
    version_num = len(session.versions)
    if version_num > 0:
        from ..tools.memory import read_from_memory
        version_data = read_from_memory(session.session_id, f"versions/v{version_num}")
        if version_data:
            version = ContentVersion(
                version_number=version_data["version_number"],
                content=version_data["content"],
                feedback_applied=version_data.get("feedback_applied"),
                generated_at=version_data["generated_at"]
            )
            if not any(v.version_number == version_num for v in session.versions):
                session.versions.append(version)

    yield {
        "event": "complete",
        "data": json.dumps({
            "status": "complete",
            "version": len(session.versions),
            "message": "Content iteration complete"
        })
    }


@router.post("/{session_id}/iterate")
async def iterate_content(session_id: str, request: IterateRequest):
    """
    Iterate on content with user feedback (SSE streaming).

    Requires at least one content version to exist.

    Returns an event stream with:
    - status: Phase updates (iterating, researching, revising)
    - analysis: Feedback analysis results
    - content_start: Beginning of revised content
    - content: Streaming revised content chunks
    - complete: Iteration finished

    The system can automatically perform additional research if needed.
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Validate that content exists
    if not session.versions and len(session.versions) == 0:
        # Try loading from memory
        from ..tools.memory import read_from_memory
        version_data = read_from_memory(session.session_id, "versions/v1")
        if not version_data:
            raise HTTPException(
                status_code=400,
                detail="Cannot iterate: no content has been generated yet"
            )

    session.status = SessionStatus.ITERATING

    return EventSourceResponse(iterate_event_generator(session, request.feedback))


@router.get("/{session_id}/versions/{version_number}")
async def get_version(session_id: str, version_number: int):
    """
    Get a specific content version.

    Returns full content and metadata for the specified version.
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Try session versions first
    for version in session.versions:
        if version.version_number == version_number:
            return {
                "session_id": session_id,
                "version_number": version.version_number,
                "content": version.content,
                "generated_at": version.generated_at.isoformat(),
                "feedback_applied": version.feedback_applied
            }

    # Try loading from memory
    from ..tools.memory import read_from_memory
    version_data = read_from_memory(session.session_id, f"versions/v{version_number}")
    if version_data:
        return {
            "session_id": session_id,
            "version_number": version_data["version_number"],
            "content": version_data["content"],
            "generated_at": version_data["generated_at"],
            "feedback_applied": version_data.get("feedback_applied")
        }

    raise HTTPException(status_code=404, detail=f"Version {version_number} not found")
