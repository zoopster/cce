"""
Agents module for the Content Creation Engine.

Contains agent implementations following Anthropic's multi-agent patterns:
- BaseAgent: Foundation class with memory operations
- ResearchSubagent: Parallel worker for information gathering
- LeadAgent: Orchestrator that coordinates research process
- ContentGeneratorAgent: Creates content from research findings
- IteratorAgent: Refines content based on user feedback
- PublisherAgent: Handles WordPress publishing and HTML export
"""

from .base import BaseAgent
from .research import ResearchSubagent, ResearchTask, run_parallel_research
from .lead import LeadAgent
from .generator import ContentGeneratorAgent
from .iterator import IteratorAgent
from .publisher import PublisherAgent

__all__ = [
    "BaseAgent",
    "ResearchSubagent",
    "ResearchTask",
    "run_parallel_research",
    "LeadAgent",
    "ContentGeneratorAgent",
    "IteratorAgent",
    "PublisherAgent",
]
