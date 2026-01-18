"""
Research Subagent - Parallel worker that searches for specific information.

Key principles (from Anthropic):
1. Start wide, then narrow - broad queries first, then drill into specifics
2. Write findings to filesystem - avoid telephone game information loss
3. Use interleaved thinking - evaluate sources between tool calls
4. Independent execution - each subagent explores autonomously
"""

import asyncio
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from anthropic import Anthropic

from .base import BaseAgent
from ..tools.search import search_web
from ..tools.scrape import scrape_url
from ..tools.memory import save_to_memory
from ..models.content import AgentState
from ..config import settings


class ResearchTask:
    """Task assigned by Lead Agent to Research Subagent"""

    def __init__(
        self,
        objective: str,
        search_queries: List[str],
        output_format: str = "summary",
        max_sources: int = 5,
        tool_guidance: str = ""
    ):
        """
        Initialize a research task.

        Args:
            objective: What this subagent needs to find out
            search_queries: List of queries to execute (first 2 are broad, rest are narrow)
            output_format: How to format findings (summary, detailed, bullet_points)
            max_sources: Maximum number of sources to scrape deeply
            tool_guidance: Additional guidance for source evaluation
        """
        self.objective = objective
        self.search_queries = search_queries
        self.output_format = output_format
        self.max_sources = max_sources
        self.tool_guidance = tool_guidance


class ResearchSubagent(BaseAgent):
    """
    Worker agent that searches for specific information.

    Executes in parallel with other subagents, each with a distinct task.
    Writes findings directly to filesystem to avoid information loss.
    """

    def __init__(self, session_id: str, task: ResearchTask):
        """
        Initialize research subagent.

        Args:
            session_id: The session this agent belongs to
            task: The research task to execute
        """
        super().__init__(session_id, agent_id=f"research_{uuid.uuid4().hex[:8]}")
        self.task = task
        self.current_task = task.objective
        self.sources: List[Dict[str, Any]] = []
        self.findings: List[str] = []

    async def execute(self) -> Dict[str, Any]:
        """
        Execute the research task:
        1. Broad search to explore landscape
        2. Evaluate and select promising sources
        3. Narrow search on specific aspects
        4. Scrape top sources for detailed content
        5. Synthesize findings
        6. Write to filesystem

        Returns:
            Dictionary containing synthesis, sources, and metadata
        """
        self.status = "executing"

        try:
            # Step 1: Broad search
            broad_results = await self._search_broad()

            # Step 2: Evaluate sources (thinking step)
            promising_sources = await self._evaluate_sources(broad_results)

            # Step 3: Narrow search if needed
            if len(promising_sources) < self.task.max_sources:
                narrow_results = await self._search_narrow()
                promising_sources.extend(narrow_results)

            # Step 4: Scrape top sources for content
            scraped_content = await self._scrape_sources(
                promising_sources[:self.task.max_sources]
            )

            # Step 5: Synthesize findings
            synthesis = await self._synthesize_findings(scraped_content)

            # Step 6: Write to filesystem (avoid telephone game)
            self._write_findings_to_memory(synthesis)

            self.status = "complete"
            return synthesis

        except Exception as e:
            self.status = "error"
            self._write_error_to_memory(str(e))
            raise

    async def _search_broad(self) -> List[Dict[str, Any]]:
        """
        Start with broad search queries.

        Returns:
            List of search results from broad queries
        """
        all_results = []

        # First 2 queries are broad
        for query in self.task.search_queries[:2]:
            self.tool_calls += 1
            try:
                results = await search_web(query, limit=5)
                all_results.extend(results)
            except Exception:
                # Continue with other queries if one fails
                pass

        return all_results

    async def _evaluate_sources(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Use Claude to evaluate source quality.
        This is the "interleaved thinking" step.

        Args:
            results: Search results to evaluate

        Returns:
            Filtered list of high-quality sources
        """
        if not results:
            return []

        # Build evaluation prompt
        sources_text = "\n".join([
            f"- {r.get('title', 'No title')}: {r.get('url', '')}\n  "
            f"{r.get('description', '')[:200]}"
            for r in results[:10]
        ])

        prompt = f"""Evaluate these sources for the research task: "{self.task.objective}"

Sources:
{sources_text}

{self.task.tool_guidance}

Return the indices (0-based) of the most relevant and authoritative sources, separated by commas.
Consider: relevance to task, source authority, content quality.
Only return the numbers, like: 0, 2, 5"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse selected indices
        try:
            indices_text = response.content[0].text.strip()
            indices = [
                int(i.strip())
                for i in indices_text.split(",")
                if i.strip().isdigit()
            ]
            selected = [results[i] for i in indices if i < len(results)]
            return selected if selected else results[:3]
        except Exception:
            # Fallback to first 3 results if parsing fails
            return results[:3]

    async def _search_narrow(self) -> List[Dict[str, Any]]:
        """
        Narrow down with more specific queries.

        Returns:
            List of search results from narrow queries
        """
        all_results = []

        # Remaining queries are narrow
        for query in self.task.search_queries[2:]:
            self.tool_calls += 1
            try:
                results = await search_web(query, limit=3)
                all_results.extend(results)
            except Exception:
                pass

        return all_results

    async def _scrape_sources(
        self,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Scrape content from selected sources in parallel.

        Args:
            sources: List of sources to scrape

        Returns:
            List of scraped content dictionaries
        """
        scraped = []

        # Scrape up to 3 sources in parallel
        tasks = []
        for source in sources[:3]:
            url = source.get("url")
            if url:
                tasks.append(self._scrape_single(url, source))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            scraped = [r for r in results if isinstance(r, dict)]

        return scraped

    async def _scrape_single(
        self,
        url: str,
        source: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Scrape a single URL.

        Args:
            url: URL to scrape
            source: Original search result metadata

        Returns:
            Dictionary with scraped content and metadata
        """
        self.tool_calls += 1
        try:
            content = await scrape_url(url)
            return {
                "url": url,
                "title": source.get("title", ""),
                "content": content.get("markdown", "")[:3000],  # Limit content size
                "metadata": content.get("metadata", {})
            }
        except Exception as e:
            # Return partial data on error
            return {
                "url": url,
                "title": source.get("title", ""),
                "content": source.get("description", ""),
                "error": str(e)
            }

    async def _synthesize_findings(
        self,
        scraped: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesize findings into structured output.

        Args:
            scraped: List of scraped content dictionaries

        Returns:
            Synthesis dictionary with summary, sources, and metadata
        """
        # Build context from scraped content
        context_parts = []
        for s in scraped:
            context_parts.append(
                f"## {s.get('title', 'Source')}\n"
                f"URL: {s.get('url', '')}\n\n"
                f"{s.get('content', '')[:1500]}"
            )

        context = "\n\n---\n\n".join(context_parts)

        prompt = f"""Synthesize research findings for: "{self.task.objective}"

Research context:
{context}

Provide a {self.task.output_format} that:
1. Answers the research objective
2. Cites sources with URLs
3. Highlights key facts and insights
4. Notes any gaps or conflicting information

Format as markdown."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        synthesis_text = response.content[0].text

        return {
            "agent_id": self.agent_id,
            "objective": self.task.objective,
            "summary": synthesis_text,
            "sources": [
                {
                    "url": s.get("url", ""),
                    "title": s.get("title", ""),
                    "snippet": s.get("content", "")[:300]
                }
                for s in scraped
            ],
            "tool_calls": self.tool_calls,
            "completed_at": datetime.utcnow().isoformat()
        }

    def _write_findings_to_memory(self, synthesis: Dict[str, Any]) -> None:
        """
        Write findings to filesystem - avoids telephone game.

        Args:
            synthesis: Synthesized research findings
        """
        save_to_memory(
            self.session_id,
            f"research/{self.agent_id}",
            synthesis
        )

    def _write_error_to_memory(self, error: str) -> None:
        """
        Write error state to memory.

        Args:
            error: Error message to record
        """
        save_to_memory(
            self.session_id,
            f"research/{self.agent_id}",
            {
                "agent_id": self.agent_id,
                "objective": self.task.objective,
                "error": error,
                "tool_calls": self.tool_calls,
                "completed_at": datetime.utcnow().isoformat()
            }
        )

    def get_state(self) -> AgentState:
        """
        Get current agent state for UI display.

        Returns:
            Current state of this agent
        """
        return AgentState(
            agent_id=self.agent_id,
            agent_type="research",
            status=self.status,
            current_task=self.current_task,
            tool_calls=self.tool_calls,
            findings_count=len(self.sources)
        )


async def run_parallel_research(
    session_id: str,
    tasks: List[ResearchTask]
) -> List[Dict[str, Any]]:
    """
    Run multiple research subagents in parallel.

    This is the key multi-agent pattern - spawn workers that
    execute independently and write to shared filesystem.

    Args:
        session_id: Session identifier for memory coordination
        tasks: List of research tasks to execute in parallel

    Returns:
        List of synthesis results from successful agents

    Example:
        tasks = [
            ResearchTask(
                objective="Find statistics on topic X",
                search_queries=["topic X statistics", "topic X data 2024"]
            ),
            ResearchTask(
                objective="Find expert opinions on topic Y",
                search_queries=["topic Y expert analysis", "topic Y research"]
            )
        ]
        results = await run_parallel_research(session_id, tasks)
    """
    subagents = [ResearchSubagent(session_id, task) for task in tasks]

    # Execute all subagents in parallel
    results = await asyncio.gather(
        *[agent.execute() for agent in subagents],
        return_exceptions=True
    )

    # Filter out exceptions and return successful results
    return [r for r in results if isinstance(r, dict)]
