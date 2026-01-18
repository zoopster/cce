# Tools Layer

The Tools Layer provides reusable utilities for web research, content extraction, and agent coordination through filesystem-based memory operations.

## Overview

This layer wraps the Firecrawl API and provides three main categories of tools:

1. **Search Tools** - Web search capabilities
2. **Scrape Tools** - Content extraction and deep research
3. **Memory Tools** - Filesystem-based agent coordination

## Modules

### search.py

Web search functionality using Firecrawl API.

**Functions:**

- `search_web(query, limit=5, lang="en", country="us")` - General web search
- `search_broad(topic, limit=5)` - Broad topic exploration
- `search_narrow(topic, aspect, limit=3)` - Focused aspect search

**Example:**

```python
from app.tools import search_web, search_broad, search_narrow

# General search
results = await search_web("Python async programming", limit=5)

# Broad topic search
results = await search_broad("artificial intelligence", limit=10)

# Narrow search on specific aspect
results = await search_narrow("AI", "ethics and safety", limit=5)
```

### scrape.py

Content extraction and deep research using Firecrawl API.

**Functions:**

- `scrape_url(url, formats=["markdown"], only_main_content=True)` - Extract content from URL
- `deep_research(topic, max_depth=3, max_urls=20)` - Conduct comprehensive research

**Example:**

```python
from app.tools import scrape_url, deep_research

# Scrape a single URL
content = await scrape_url("https://example.com/article")
print(content["markdown"])  # Markdown content
print(content["metadata"])  # Page metadata

# Deep research on a topic
research = await deep_research(
    "Impact of AI on software development",
    max_depth=3,
    max_urls=30
)
print(research["finalAnalysis"])  # Comprehensive analysis
print(research["sources"])  # List of sources used
```

### memory.py

Filesystem-based memory operations for agent coordination.

**Functions:**

- `save_to_memory(session_id, key, data)` - Save data to memory
- `read_from_memory(session_id, key)` - Read data from memory
- `list_memory_keys(session_id, prefix="")` - List all keys
- `aggregate_research(session_id)` - Combine research findings
- `clear_session_memory(session_id)` - Delete session data
- `get_session_path(session_id)` - Get session directory path

**Example:**

```python
from app.tools import (
    save_to_memory,
    read_from_memory,
    list_memory_keys,
    aggregate_research
)

session_id = "session_123"

# Save research findings
save_to_memory(
    session_id,
    "research/agent_1",
    {
        "sources": ["https://example.com"],
        "findings": "Key insights about the topic..."
    }
)

# Read from memory
data = read_from_memory(session_id, "research/agent_1")

# List all research keys
keys = list_memory_keys(session_id, prefix="research/")

# Aggregate all research findings
all_research = aggregate_research(session_id)
```

## Memory Structure

Memory is organized hierarchically:

```
app/memory/
└── {session_id}/
    ├── research/
    │   ├── agent_1.json
    │   ├── agent_2.json
    │   └── agent_3.json
    ├── outline/
    │   └── structure.json
    └── draft/
        └── content.json
```

Each JSON file contains:

```json
{
  "data": { ... },
  "saved_at": "2024-01-17T10:30:00",
  "key": "research/agent_1"
}
```

## Configuration

The tools layer requires the following environment variables:

```bash
FIRECRAWL_API_KEY=fc-your-api-key-here
```

These are automatically loaded from the `config.py` settings object.

## Error Handling

All functions that interact with the Firecrawl API will raise:

- `ValueError` - If API key is not configured
- `httpx.HTTPStatusError` - If the API request fails

**Example:**

```python
from app.tools import search_web

try:
    results = await search_web("Python programming")
except ValueError as e:
    print(f"Configuration error: {e}")
except httpx.HTTPStatusError as e:
    print(f"API error: {e.response.status_code}")
```

## Dependencies

Required packages (already in requirements.txt):

- `httpx>=0.27.0` - HTTP client for API requests
- `pydantic>=2.9.0` - Settings validation
- `python-dotenv>=1.0.0` - Environment variable loading

## Testing

To test the tools layer:

```python
# test_tools.py
import asyncio
from app.tools import search_web, scrape_url, save_to_memory, read_from_memory

async def test_search():
    results = await search_web("Python", limit=3)
    print(f"Found {len(results)} results")
    return results

async def test_scrape():
    content = await scrape_url("https://www.python.org")
    print(f"Scraped {len(content.get('markdown', ''))} characters")
    return content

def test_memory():
    session_id = "test_session"

    # Save
    path = save_to_memory(session_id, "test_key", {"value": 123})
    print(f"Saved to: {path}")

    # Read
    data = read_from_memory(session_id, "test_key")
    print(f"Read data: {data}")

    return data

if __name__ == "__main__":
    # Test async functions
    asyncio.run(test_search())
    asyncio.run(test_scrape())

    # Test sync functions
    test_memory()
```

## Best Practices

1. **Session Management**: Use unique session IDs for each content creation workflow
2. **Memory Prefixes**: Organize memory with prefixes (e.g., "research/", "outline/", "draft/")
3. **Error Handling**: Always wrap API calls in try-except blocks
4. **Timeouts**: Deep research can take several minutes - plan accordingly
5. **API Limits**: Be mindful of Firecrawl API rate limits and quotas

## Integration with Agents

The tools layer is designed to work seamlessly with the agents layer:

```python
from app.agents import ResearchAgent
from app.tools import save_to_memory, aggregate_research

# Research agent uses tools internally
agent = ResearchAgent()
findings = await agent.research("topic", session_id="session_123")

# Aggregate findings from multiple agents
all_research = aggregate_research("session_123")
```

## Future Enhancements

Potential improvements for the tools layer:

- Caching layer for API responses
- Retry logic with exponential backoff
- Batch operations for multiple URLs
- Database backend option (in addition to filesystem)
- Metrics and monitoring integration
