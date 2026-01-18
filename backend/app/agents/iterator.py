"""
Iterator Agent - Refines content based on user feedback.

Key responsibilities:
1. Analyze user feedback to understand requested changes
2. Identify specific sections to modify
3. Optionally spawn additional research if needed
4. Regenerate improved content version
5. Track version history
"""

import asyncio
from typing import AsyncGenerator, Dict, Any, Optional, List
from datetime import datetime

from anthropic import Anthropic

from .base import BaseAgent
from .research import ResearchTask, run_parallel_research
from ..tools.memory import read_from_memory, save_to_memory, aggregate_research
from ..models.content import ContentSession, ContentVersion, AgentState
from ..config import settings


class IteratorAgent(BaseAgent):
    """
    Refines content based on user feedback.

    Can perform targeted modifications or full regeneration
    depending on the nature of the feedback.
    """

    def __init__(self, session: ContentSession):
        super().__init__(session.session_id, agent_id="iterator")
        self.session = session
        self.current_task = "initializing"

    async def analyze_feedback(self, feedback: str) -> Dict[str, Any]:
        """
        Analyze user feedback to determine action needed.

        Returns:
        - action: "modify_section", "rewrite", "add_content", "research_more"
        - details: specific instructions
        """
        self.status = "analyzing"
        self.current_task = "analyzing feedback"

        current_content = self._get_current_content()

        prompt = f"""Analyze this user feedback for content revision:

FEEDBACK: {feedback}

CURRENT CONTENT (first 2000 chars):
{current_content[:2000]}

Determine:
1. What type of change is needed?
   - MODIFY_SECTION: Change specific parts
   - REWRITE: Significant rewrite needed
   - ADD_CONTENT: Add new sections/information
   - RESEARCH_MORE: Need additional research first

2. What specific changes should be made?

Respond in JSON format:
{{
  "action": "MODIFY_SECTION|REWRITE|ADD_CONTENT|RESEARCH_MORE",
  "sections_affected": ["section names if applicable"],
  "specific_changes": "detailed description of changes",
  "needs_research": true/false,
  "research_queries": ["queries if research needed"]
}}"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        try:
            result_text = response.content[0].text.strip()
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            return json.loads(result_text)
        except:
            return {
                "action": "MODIFY_SECTION",
                "sections_affected": [],
                "specific_changes": feedback,
                "needs_research": False,
                "research_queries": []
            }

    async def iterate_content(self, feedback: str) -> str:
        """
        Apply feedback to generate improved content version.
        """
        self.status = "iterating"
        self.current_task = "applying feedback"

        analysis = await self.analyze_feedback(feedback)

        # If research needed, do it first
        if analysis.get("needs_research") and analysis.get("research_queries"):
            await self._do_additional_research(analysis["research_queries"])

        current_content = self._get_current_content()
        research = self._get_research_context()

        prompt = f"""Revise this content based on the feedback and analysis.

ORIGINAL CONTENT:
{current_content}

USER FEEDBACK: {feedback}

ANALYSIS:
- Action: {analysis.get('action')}
- Changes needed: {analysis.get('specific_changes')}
- Sections affected: {analysis.get('sections_affected', [])}

ADDITIONAL CONTEXT:
{research[:2000] if research else 'None'}

CONTENT PARAMETERS:
- Tone: {self.session.parameters.tone.value}
- Audience: {self.session.parameters.audience_level.value}
- Target length: {self.session.parameters.word_count} words

Rewrite the content incorporating the feedback. Maintain the overall structure unless the feedback specifically requests structural changes. Output only the revised content in markdown format."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        new_content = response.content[0].text

        # Save new version
        version_num = len(self.session.versions) + 1
        version = ContentVersion(
            version_number=version_num,
            content=new_content,
            generated_at=datetime.utcnow(),
            feedback_applied=feedback
        )
        self.session.versions.append(version)

        save_to_memory(self.session_id, f"versions/v{version_num}", {
            "version_number": version_num,
            "content": new_content,
            "feedback_applied": feedback,
            "analysis": analysis,
            "generated_at": datetime.utcnow().isoformat()
        })

        self.status = "complete"
        self.current_task = "iteration complete"

        return new_content

    async def iterate_stream(self, feedback: str) -> AsyncGenerator[str, None]:
        """Stream the iteration process for real-time display."""
        self.status = "iterating"
        self.current_task = "streaming iteration"

        analysis = await self.analyze_feedback(feedback)
        yield f"[ANALYSIS]\n{analysis.get('specific_changes', feedback)}\n\n[REVISED CONTENT]\n"

        if analysis.get("needs_research") and analysis.get("research_queries"):
            yield "[RESEARCHING...]\n"
            await self._do_additional_research(analysis["research_queries"])
            yield "[RESEARCH COMPLETE]\n\n"

        current_content = self._get_current_content()
        research = self._get_research_context()

        prompt = f"""Revise this content based on the feedback.

ORIGINAL CONTENT:
{current_content}

USER FEEDBACK: {feedback}
CHANGES NEEDED: {analysis.get('specific_changes')}

Rewrite incorporating the feedback. Output only the revised markdown content."""

        content_parts = []

        with self.client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for text in stream.text_stream:
                content_parts.append(text)
                yield text

        # Save version
        full_content = "".join(content_parts)
        version_num = len(self.session.versions) + 1

        save_to_memory(self.session_id, f"versions/v{version_num}", {
            "version_number": version_num,
            "content": full_content,
            "feedback_applied": feedback,
            "generated_at": datetime.utcnow().isoformat()
        })

        self.status = "complete"

    async def _do_additional_research(self, queries: List[str]) -> None:
        """Spawn research subagents for additional information."""
        tasks = [
            ResearchTask(
                objective=f"Find additional information: {q}",
                search_queries=[q, f"{q} examples", f"{q} details"],
                output_format="summary",
                max_sources=3
            )
            for q in queries[:2]  # Limit to 2 additional research tasks
        ]

        await run_parallel_research(self.session_id, tasks)

    def _get_current_content(self) -> str:
        """Get the most recent content version."""
        if self.session.versions:
            return self.session.versions[-1].content

        # Try reading from memory
        for i in range(10, 0, -1):
            version_data = read_from_memory(self.session_id, f"versions/v{i}")
            if version_data:
                return version_data.get("content", "")

        return ""

    def _get_research_context(self) -> str:
        """Get research synthesis for context."""
        synthesis = read_from_memory(self.session_id, "synthesis")
        if synthesis:
            return synthesis.get("content", "")
        return ""

    def get_state(self) -> AgentState:
        return AgentState(
            agent_id=self.agent_id,
            agent_type="iterator",
            status=self.status,
            current_task=self.current_task,
            tool_calls=self.tool_calls,
            findings_count=len(self.session.versions)
        )
