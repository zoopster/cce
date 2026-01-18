"""
Research endpoints with SSE streaming.

Handles the multi-agent research process with real-time updates.
"""

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse
from typing import AsyncGenerator
import json

from ..agents.lead import LeadAgent
from ..models.content import ContentSession
from ..tools.memory import aggregate_research
from .sessions import sessions

router = APIRouter(prefix="/api/sessions", tags=["research"])


async def research_event_generator(session: ContentSession) -> AsyncGenerator[dict, None]:
    """
    Generate SSE events during research process.

    Streams real-time updates as the lead agent coordinates research subagents.
    """
    lead_agent = LeadAgent(session)
    session.agents.append(lead_agent.get_state())

    # Phase 1: Analyze complexity
    yield {
        "event": "status",
        "data": json.dumps({
            "phase": "analyzing",
            "message": "Analyzing query complexity..."
        })
    }

    session.complexity = await lead_agent.analyze_complexity()

    yield {
        "event": "complexity",
        "data": json.dumps({
            "complexity": session.complexity.value,
            "message": f"Classified as {session.complexity.value} complexity"
        })
    }

    # Phase 2: Create research plan
    yield {
        "event": "status",
        "data": json.dumps({
            "phase": "planning",
            "message": "Creating research plan..."
        })
    }

    plan = await lead_agent.create_research_plan()

    yield {
        "event": "plan",
        "data": json.dumps({
            "tasks": len(plan["tasks"]),
            "plan": plan,
            "message": f"Created plan with {len(plan['tasks'])} research tasks"
        })
    }

    # Phase 3: Execute research
    yield {
        "event": "status",
        "data": json.dumps({
            "phase": "researching",
            "message": f"Spawning {len(plan['tasks'])} parallel research agents..."
        })
    }

    research_result = await lead_agent.execute_research(plan)

    yield {
        "event": "research_progress",
        "data": json.dumps({
            "agents_completed": research_result["successful"],
            "total_agents": research_result["num_agents"],
            "message": f"Completed {research_result['successful']} of {research_result['num_agents']} research tasks"
        })
    }

    # Phase 4: Synthesize findings
    yield {
        "event": "status",
        "data": json.dumps({
            "phase": "synthesizing",
            "message": "Synthesizing findings from all agents..."
        })
    }

    synthesis = await lead_agent.synthesize_findings()

    # Update session
    session.status = "ready_for_generation"

    # Get aggregated results
    aggregated = aggregate_research(session.session_id)

    yield {
        "event": "complete",
        "data": json.dumps({
            "status": "complete",
            "synthesis_preview": synthesis[:1000],
            "total_sources": aggregated["total_sources"],
            "message": "Research complete and ready for content generation"
        })
    }


@router.post("/{session_id}/research")
async def start_research(session_id: str):
    """
    Start the multi-agent research process (SSE streaming).

    Returns an event stream with real-time progress updates.

    Event types:
    - status: Phase updates (analyzing, planning, researching, synthesizing)
    - complexity: Complexity classification result
    - plan: Research plan with task decomposition
    - research_progress: Progress of parallel research agents
    - complete: Final synthesis and results
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != "created":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start research: session is in {session.status.value} state"
        )

    session.status = "researching"

    return EventSourceResponse(research_event_generator(session))


@router.get("/{session_id}/research")
async def get_research_results(session_id: str):
    """
    Get aggregated research results for a session.

    Returns all sources, findings, and research data collected by subagents.
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    aggregated = aggregate_research(session_id)

    return {
        "session_id": session_id,
        "total_sources": aggregated["total_sources"],
        "sources": aggregated["sources"][:20],  # Limit to 20 for response size
        "findings_count": len(aggregated["findings"]),
        "has_synthesis": read_from_memory(session_id, "synthesis") is not None
    }


from ..tools.memory import read_from_memory


@router.get("/{session_id}/research/synthesis")
async def get_research_synthesis(session_id: str):
    """
    Get the synthesized research summary.

    Returns the lead agent's synthesis of all research findings.
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    synthesis = read_from_memory(session_id, "synthesis")
    if not synthesis:
        raise HTTPException(
            status_code=404,
            detail="No research synthesis available. Run research first."
        )

    return {
        "session_id": session_id,
        "synthesis": synthesis.get("content", ""),
        "source_count": synthesis.get("source_count", 0),
        "created_at": synthesis.get("created_at", "")
    }
