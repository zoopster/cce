"""
Content Generator Agent - Creates content from research findings.

Key responsibilities:
1. Read aggregated research from filesystem
2. Plan content structure using extended thinking
3. Generate content based on parameters
4. Stream output for real-time display
5. Save versions to memory
"""

import asyncio
from typing import AsyncGenerator, Dict, Any, Optional
from datetime import datetime

from anthropic import Anthropic

from .base import BaseAgent
from ..tools.memory import read_from_memory, save_to_memory, aggregate_research
from ..models.content import ContentSession, ContentVersion, AgentState
from ..models.parameters import GenerationParameters
from ..config import settings


class ContentGeneratorAgent(BaseAgent):
    """
    Generates content from research findings.

    Uses extended thinking to plan structure before writing.
    Supports streaming for real-time content display.
    """

    def __init__(self, session: ContentSession):
        super().__init__(session.session_id, agent_id="generator")
        self.session = session
        self.current_task = "initializing"

    async def read_research(self) -> str:
        """Read synthesized research from filesystem."""
        synthesis = read_from_memory(self.session_id, "synthesis")
        if synthesis:
            return synthesis.get("content", "")

        # Fallback to aggregating raw research
        aggregated = aggregate_research(self.session_id)
        return "\n\n".join(aggregated.get("findings", []))

    async def plan_structure(self, research: str) -> str:
        """
        Use extended thinking to plan content structure.
        """
        self.status = "planning"
        self.current_task = "planning content structure"

        params = self.session.parameters

        prompt = f"""Plan the structure for this content:

TOPIC: {self.session.topic}
TYPE: {params.content_type.value}
TONE: {params.tone.value}
AUDIENCE: {params.audience_level.value}
LENGTH: {params.word_count} words
KEYWORDS: {', '.join(params.keywords) or 'None'}
CUSTOM INSTRUCTIONS: {params.custom_instructions or 'None'}

RESEARCH SUMMARY:
{research[:3000]}

Create a detailed outline including:
1. Title (compelling, SEO-friendly)
2. Introduction approach
3. Main sections with key points
4. Conclusion approach
5. Estimated word count per section

Format as markdown outline."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        outline = response.content[0].text

        # Save outline to memory
        save_to_memory(self.session_id, "outline", {
            "content": outline,
            "created_at": datetime.utcnow().isoformat()
        })

        return outline

    async def generate_content(self, research: str, outline: str) -> str:
        """
        Generate full content based on research and outline.
        """
        self.status = "generating"
        self.current_task = "generating content"

        params = self.session.parameters

        prompt = f"""Write a {params.content_type.value} based on this outline and research.

OUTLINE:
{outline}

RESEARCH:
{research[:4000]}

REQUIREMENTS:
- Tone: {params.tone.value}
- Audience: {params.audience_level.value}
- Target length: {params.word_count} words
- Keywords to include: {', '.join(params.keywords) or 'None'}
- {params.custom_instructions or ''}

Write in markdown format with:
- Compelling title (H1)
- Clear section headings (H2, H3)
- Engaging introduction
- Well-structured body with examples
- Strong conclusion
- Appropriate for {params.audience_level.value} readers

Write the complete content now:"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text

        # Save version
        version_num = len(self.session.versions) + 1
        version = ContentVersion(
            version_number=version_num,
            content=content,
            generated_at=datetime.utcnow()
        )
        self.session.versions.append(version)

        save_to_memory(self.session_id, f"versions/v{version_num}", {
            "version_number": version_num,
            "content": content,
            "generated_at": datetime.utcnow().isoformat()
        })

        self.status = "complete"
        self.current_task = "generation complete"

        return content

    async def generate_stream(self) -> AsyncGenerator[str, None]:
        """
        Stream content generation for real-time display.
        """
        self.status = "generating"
        self.current_task = "streaming content generation"

        # Read research
        research = await self.read_research()

        # Plan structure
        outline = await self.plan_structure(research)
        yield f"[OUTLINE]\n{outline}\n\n[CONTENT]\n"

        params = self.session.parameters

        prompt = f"""Write a {params.content_type.value} based on this outline and research.

OUTLINE:
{outline}

RESEARCH:
{research[:4000]}

REQUIREMENTS:
- Tone: {params.tone.value}
- Audience: {params.audience_level.value}
- Target length: {params.word_count} words
- Keywords: {', '.join(params.keywords) or 'None'}
- {params.custom_instructions or ''}

Write in markdown format. Write the complete content:"""

        content_parts = []

        with self.client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for text in stream.text_stream:
                content_parts.append(text)
                yield text

        # Save complete version
        full_content = "".join(content_parts)
        version_num = len(self.session.versions) + 1

        save_to_memory(self.session_id, f"versions/v{version_num}", {
            "version_number": version_num,
            "content": full_content,
            "generated_at": datetime.utcnow().isoformat()
        })

        self.status = "complete"

    async def run_generation(self) -> str:
        """
        Complete generation workflow (non-streaming):
        1. Read research
        2. Plan structure
        3. Generate content
        """
        research = await self.read_research()
        outline = await self.plan_structure(research)
        content = await self.generate_content(research, outline)
        return content

    def get_state(self) -> AgentState:
        return AgentState(
            agent_id=self.agent_id,
            agent_type="generator",
            status=self.status,
            current_task=self.current_task,
            tool_calls=self.tool_calls,
            findings_count=len(self.session.versions)
        )
