"""
Lead Agent (Orchestrator) - Coordinates the research process.

Key responsibilities:
1. Analyze query complexity (simple/moderate/complex)
2. Create research plan with task decomposition
3. Spawn parallel research subagents
4. Monitor progress and synthesize findings
5. Decide if more research needed

From Anthropic: "Teach the orchestrator how to delegate"
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from anthropic import Anthropic

from .base import BaseAgent
from .research import ResearchSubagent, ResearchTask, run_parallel_research
from ..tools.memory import save_to_memory, read_from_memory, aggregate_research
from ..models.content import ContentSession, Complexity, AgentState
from ..models.parameters import GenerationParameters
from ..config import settings


class LeadAgent(BaseAgent):
    """
    Orchestrator that coordinates the research process.

    Implements Anthropic's orchestrator-worker pattern:
    - Decomposes queries into subtasks
    - Spawns parallel subagents
    - Aggregates and synthesizes results
    """

    def __init__(self, session: ContentSession):
        super().__init__(session.session_id, agent_id="lead")
        self.session = session
        self.current_task = "initializing"
        self.subagents: List[ResearchSubagent] = []

    async def analyze_complexity(self) -> Complexity:
        """
        Determine query complexity to decide subagent count.

        Simple: 1 subagent, 3-10 tool calls (fact-finding)
        Moderate: 2-4 subagents, 10-15 tool calls (comparisons)
        Complex: 5-10 subagents, 15-20 tool calls (deep research)
        """
        self.status = "analyzing"
        self.current_task = "analyzing query complexity"

        prompt = f"""Analyze the complexity of this content creation request:

Topic: {self.session.topic}
Content Type: {self.session.parameters.content_type.value}
Target Length: {self.session.parameters.word_count} words
Custom Instructions: {self.session.parameters.custom_instructions or 'None'}

Classify as one of:
- SIMPLE: Straightforward topic, single focus area, facts readily available
- MODERATE: Multiple aspects to cover, some comparison or analysis needed
- COMPLEX: Broad topic, multiple perspectives, deep research required

Respond with just one word: SIMPLE, MODERATE, or COMPLEX"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.content[0].text.strip().upper()

        if "SIMPLE" in result:
            return Complexity.SIMPLE
        elif "COMPLEX" in result:
            return Complexity.COMPLEX
        else:
            return Complexity.MODERATE

    async def create_research_plan(self) -> Dict[str, Any]:
        """
        Create research strategy with task decomposition.

        Each task becomes a parallel research subagent.
        """
        self.status = "planning"
        self.current_task = "creating research plan"

        # Determine number of tasks based on complexity
        task_counts = {
            Complexity.SIMPLE: 1,
            Complexity.MODERATE: 3,
            Complexity.COMPLEX: 5
        }
        num_tasks = task_counts.get(self.session.complexity, 3)

        prompt = f"""Create a research plan for this content:

Topic: {self.session.topic}
Content Type: {self.session.parameters.content_type.value}
Tone: {self.session.parameters.tone.value}
Audience: {self.session.parameters.audience_level.value}
Keywords: {', '.join(self.session.parameters.keywords) or 'None specified'}

Create exactly {num_tasks} distinct research tasks. Each task should:
1. Have a clear, specific objective
2. Include 3-4 search queries (start broad, then narrow)
3. Not overlap with other tasks

Format your response as a JSON array:
[
  {{
    "objective": "What to research",
    "search_queries": ["broad query 1", "broad query 2", "narrow query 1", "narrow query 2"],
    "tool_guidance": "Special instructions for this search"
  }}
]

Only output the JSON array, no other text."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            tasks_json = response.content[0].text.strip()
            # Handle potential markdown code blocks
            if "```json" in tasks_json:
                tasks_json = tasks_json.split("```json")[1].split("```")[0]
            elif "```" in tasks_json:
                tasks_json = tasks_json.split("```")[1].split("```")[0]

            tasks = json.loads(tasks_json)
        except Exception:
            # Fallback to simple plan
            tasks = [{
                "objective": f"Research key information about {self.session.topic}",
                "search_queries": [
                    self.session.topic,
                    f"{self.session.topic} guide",
                    f"{self.session.topic} best practices",
                    f"{self.session.topic} examples"
                ],
                "tool_guidance": "Focus on authoritative sources"
            }]

        plan = {
            "topic": self.session.topic,
            "complexity": self.session.complexity.value,
            "num_tasks": len(tasks),
            "tasks": tasks,
            "created_at": datetime.utcnow().isoformat()
        }

        # Save plan to memory
        save_to_memory(self.session_id, "plan", plan)
        self.session.research_plan = json.dumps(plan)

        return plan

    async def execute_research(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Spawn parallel research subagents and collect results.
        """
        self.status = "researching"
        self.current_task = f"coordinating {len(plan['tasks'])} research agents"

        # Convert plan tasks to ResearchTask objects
        research_tasks = [
            ResearchTask(
                objective=task["objective"],
                search_queries=task["search_queries"],
                output_format="detailed",
                max_sources=5,
                tool_guidance=task.get("tool_guidance", "")
            )
            for task in plan["tasks"]
        ]

        # Run all subagents in parallel
        results = await run_parallel_research(self.session_id, research_tasks)

        return {
            "num_agents": len(research_tasks),
            "successful": len(results),
            "results": results
        }

    async def synthesize_findings(self) -> str:
        """
        Aggregate and synthesize all research findings from filesystem.
        """
        self.status = "synthesizing"
        self.current_task = "synthesizing research findings"

        # Read all research from filesystem
        aggregated = aggregate_research(self.session_id)

        if not aggregated["findings"]:
            return "No research findings available."

        # Combine all findings
        combined = "\n\n---\n\n".join(aggregated["findings"])

        prompt = f"""Synthesize these research findings into a coherent summary:

{combined}

Create a unified research summary that:
1. Identifies key themes and insights
2. Notes important facts with source references
3. Highlights any conflicting information
4. Suggests content structure based on findings

Format as markdown with clear sections."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        synthesis = response.content[0].text

        # Save synthesis to memory
        save_to_memory(self.session_id, "synthesis", {
            "content": synthesis,
            "source_count": aggregated["total_sources"],
            "created_at": datetime.utcnow().isoformat()
        })

        return synthesis

    async def decide_more_research(self, synthesis: str) -> bool:
        """
        Determine if additional research is needed.
        """
        prompt = f"""Based on this research synthesis, is additional research needed?

Topic: {self.session.topic}
Content requirements: {self.session.parameters.word_count} word {self.session.parameters.content_type.value}

Current synthesis:
{synthesis[:2000]}

Consider:
1. Are there major gaps in the research?
2. Are key aspects of the topic missing?
3. Is there enough material for the requested content length?

Respond with just YES or NO."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=5,
            messages=[{"role": "user", "content": prompt}]
        )

        return "YES" in response.content[0].text.upper()

    async def run_full_research(self) -> str:
        """
        Complete research workflow:
        1. Analyze complexity
        2. Create plan
        3. Execute parallel research
        4. Synthesize findings
        5. Check if more research needed
        """
        # Step 1: Analyze complexity
        self.session.complexity = await self.analyze_complexity()

        # Step 2: Create plan
        plan = await self.create_research_plan()

        # Step 3: Execute research
        await self.execute_research(plan)

        # Step 4: Synthesize
        synthesis = await self.synthesize_findings()

        # Step 5: Check if more research needed (optional second round)
        if await self.decide_more_research(synthesis):
            # Create additional targeted tasks
            additional_plan = await self._create_follow_up_plan(synthesis)
            if additional_plan:
                await self.execute_research(additional_plan)
                synthesis = await self.synthesize_findings()

        self.status = "complete"
        self.current_task = "research complete"

        return synthesis

    async def _create_follow_up_plan(self, synthesis: str) -> Optional[Dict[str, Any]]:
        """Create follow-up research tasks to fill gaps."""
        prompt = f"""Based on this synthesis, what specific gaps need more research?

{synthesis[:1500]}

Create 1-2 targeted research tasks to fill the gaps.
Format as JSON array with objective and search_queries.
If no gaps, respond with empty array []."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            tasks_text = response.content[0].text.strip()
            if "```" in tasks_text:
                tasks_text = tasks_text.split("```")[1].split("```")[0]
                if tasks_text.startswith("json"):
                    tasks_text = tasks_text[4:]

            tasks = json.loads(tasks_text)
            if tasks:
                return {"tasks": tasks}
        except Exception:
            pass

        return None

    def get_state(self) -> AgentState:
        return AgentState(
            agent_id=self.agent_id,
            agent_type="lead",
            status=self.status,
            current_task=self.current_task,
            tool_calls=self.tool_calls,
            findings_count=len(self.subagents)
        )
