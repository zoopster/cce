"""
Tools Layer for Content Creation Engine.

This module provides:
- Web search tools using Firecrawl API
- Content scraping and deep research capabilities
- Filesystem-based memory operations for agent coordination
"""

from .search import search_web, search_broad, search_narrow
from .scrape import scrape_url, deep_research
from .memory import (
    save_to_memory,
    read_from_memory,
    list_memory_keys,
    aggregate_research,
    clear_session_memory,
    get_session_path,
)

__all__ = [
    # Search tools
    "search_web",
    "search_broad",
    "search_narrow",
    # Scrape tools
    "scrape_url",
    "deep_research",
    # Memory tools
    "save_to_memory",
    "read_from_memory",
    "list_memory_keys",
    "aggregate_research",
    "clear_session_memory",
    "get_session_path",
]
