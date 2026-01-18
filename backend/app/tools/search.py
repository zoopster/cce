"""
Web search tools using Firecrawl API.

Provides functions for searching the web and retrieving search results
with content extraction capabilities.
"""

import httpx
from typing import List, Dict, Any

from ..config import settings

FIRECRAWL_BASE_URL = "https://api.firecrawl.dev/v1"


async def search_web(
    query: str,
    limit: int = 5,
    lang: str = "en",
    country: str = "us"
) -> List[Dict[str, Any]]:
    """
    Search the web using Firecrawl.

    Args:
        query: Search query string
        limit: Maximum number of results to return (default: 5)
        lang: Language code for search results (default: "en")
        country: Country code for search results (default: "us")

    Returns:
        List of search results with: url, title, description, markdown content

    Raises:
        httpx.HTTPStatusError: If the API request fails
        ValueError: If Firecrawl API key is not configured
    """
    if not settings.firecrawl_api_key:
        raise ValueError("Firecrawl API key not configured in settings")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{FIRECRAWL_BASE_URL}/search",
            headers={"Authorization": f"Bearer {settings.firecrawl_api_key}"},
            json={
                "query": query,
                "limit": limit,
                "lang": lang,
                "country": country,
                "scrapeOptions": {
                    "formats": ["markdown"],
                    "onlyMainContent": True
                }
            },
            timeout=60.0
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])


async def search_broad(topic: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Start with broad search - short queries for initial exploration.

    Args:
        topic: The topic to search for
        limit: Maximum number of results (default: 5)

    Returns:
        List of search results
    """
    return await search_web(topic, limit=limit)


async def search_narrow(topic: str, aspect: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Narrow search on specific aspect of a topic.

    Args:
        topic: The main topic
        aspect: Specific aspect to focus on
        limit: Maximum number of results (default: 3)

    Returns:
        List of search results focused on the specific aspect
    """
    return await search_web(f"{topic} {aspect}", limit=limit)
