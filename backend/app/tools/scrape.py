"""
Content extraction tools using Firecrawl API.

Provides functions for scraping individual URLs and conducting
deep research on topics.
"""

import httpx
from typing import Dict, Any, List

from ..config import settings

FIRECRAWL_BASE_URL = "https://api.firecrawl.dev/v1"


async def scrape_url(
    url: str,
    formats: List[str] = None,
    only_main_content: bool = True
) -> Dict[str, Any]:
    """
    Scrape content from a URL using Firecrawl.

    Args:
        url: URL to scrape
        formats: List of content formats to extract (default: ["markdown"])
        only_main_content: Whether to extract only main content (default: True)

    Returns:
        Dictionary containing:
            - markdown: str - The extracted content in markdown format
            - metadata: dict - Page metadata (title, description, etc.)
            - url: str - The scraped URL

    Raises:
        httpx.HTTPStatusError: If the API request fails
        ValueError: If Firecrawl API key is not configured
    """
    if formats is None:
        formats = ["markdown"]

    if not settings.firecrawl_api_key:
        raise ValueError("Firecrawl API key not configured in settings")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{FIRECRAWL_BASE_URL}/scrape",
            headers={"Authorization": f"Bearer {settings.firecrawl_api_key}"},
            json={
                "url": url,
                "formats": formats,
                "onlyMainContent": only_main_content
            },
            timeout=60.0
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", {})


async def deep_research(
    topic: str,
    max_depth: int = 3,
    max_urls: int = 20
) -> Dict[str, Any]:
    """
    Conduct deep research on a topic using Firecrawl's deep research feature.

    This performs intelligent crawling, searching, and LLM analysis to gather
    comprehensive information about a topic.

    Args:
        topic: The research topic or question
        max_depth: Maximum depth for recursive search/crawl (default: 3)
        max_urls: Maximum number of URLs to analyze (default: 20)

    Returns:
        Dictionary containing:
            - finalAnalysis: str - Comprehensive analysis from the research
            - sources: list - List of sources used in the research
            - activities: list - Research activities performed

    Raises:
        httpx.HTTPStatusError: If the API request fails
        ValueError: If Firecrawl API key is not configured

    Note:
        Deep research can take several minutes depending on the topic complexity.
    """
    if not settings.firecrawl_api_key:
        raise ValueError("Firecrawl API key not configured in settings")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{FIRECRAWL_BASE_URL}/deep-research",
            headers={"Authorization": f"Bearer {settings.firecrawl_api_key}"},
            json={
                "query": topic,
                "maxDepth": max_depth,
                "maxUrls": max_urls
            },
            timeout=300.0  # Deep research can take a while
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", {})
