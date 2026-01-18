# Tools Layer - Quick Reference

## Import Everything

```python
from app.tools import (
    # Search
    search_web, search_broad, search_narrow,
    # Scrape
    scrape_url, deep_research,
    # Memory
    save_to_memory, read_from_memory, list_memory_keys,
    aggregate_research, clear_session_memory
)
```

## Search Tools

```python
# Basic search
results = await search_web("Python programming", limit=5)
# Returns: [{"url": "...", "title": "...", "description": "...", "markdown": "..."}]

# Broad topic search
results = await search_broad("artificial intelligence", limit=10)

# Focused search
results = await search_narrow("AI", "ethics", limit=3)
```

## Scrape Tools

```python
# Scrape single URL
content = await scrape_url("https://example.com")
# Returns: {"markdown": "...", "metadata": {...}, "url": "..."}

# Deep research (takes 2-5 minutes)
research = await deep_research("AI impact on jobs", max_depth=3, max_urls=20)
# Returns: {"finalAnalysis": "...", "sources": [...], "activities": [...]}
```

## Memory Tools

```python
session_id = "blog_post_123"

# Save data
path = save_to_memory(session_id, "research/agent_1", {
    "sources": ["https://example.com"],
    "findings": "Key insights..."
})

# Read data
data = read_from_memory(session_id, "research/agent_1")

# List keys
all_keys = list_memory_keys(session_id)
research_keys = list_memory_keys(session_id, prefix="research/")

# Aggregate research
combined = aggregate_research(session_id)
# Returns: {"sources": [...], "findings": [...], "total_sources": 5}

# Cleanup
clear_session_memory(session_id)
```

## Error Handling

```python
import httpx

try:
    results = await search_web("query")
except ValueError as e:
    print(f"Config error: {e}")  # Missing API key
except httpx.HTTPStatusError as e:
    print(f"API error: {e.response.status_code}")  # API failure
```

## Complete Example

```python
import asyncio
from app.tools import *

async def research_workflow():
    session_id = "research_001"

    # Search for sources
    results = await search_web("Python async patterns", limit=5)

    # Scrape top result
    if results:
        content = await scrape_url(results[0]["url"])

        # Save to memory
        save_to_memory(session_id, "research/web", {
            "sources": [r["url"] for r in results],
            "content": content["markdown"],
            "findings": "Async patterns are important for..."
        })

    # Read back
    data = read_from_memory(session_id, "research/web")
    print(f"Saved {len(data['sources'])} sources")

    # Cleanup
    clear_session_memory(session_id)

asyncio.run(research_workflow())
```

## Common Patterns

### Save Research from Multiple Agents

```python
# Agent 1
save_to_memory(session_id, "research/agent_1", {"findings": "..."})

# Agent 2
save_to_memory(session_id, "research/agent_2", {"findings": "..."})

# Combine all
all_research = aggregate_research(session_id)
```

### Hierarchical Keys

```python
# Create hierarchy
save_to_memory(sid, "research/step1/findings", data1)
save_to_memory(sid, "research/step2/findings", data2)
save_to_memory(sid, "outline/structure", outline)
save_to_memory(sid, "draft/content", draft)

# List by prefix
research_items = list_memory_keys(sid, "research/")
# Returns: ["research/step1/findings", "research/step2/findings"]
```

### Progressive Research

```python
# Step 1: Broad search
broad_results = await search_broad("AI ethics")
save_to_memory(sid, "research/broad", broad_results)

# Step 2: Narrow searches
for aspect in ["privacy", "bias", "transparency"]:
    results = await search_narrow("AI ethics", aspect)
    save_to_memory(sid, f"research/narrow/{aspect}", results)

# Step 3: Deep dive
research = await deep_research("AI ethics comprehensive analysis")
save_to_memory(sid, "research/deep", research)

# Step 4: Aggregate everything
final = aggregate_research(sid)
```

## Configuration

```bash
# .env file
FIRECRAWL_API_KEY=fc-your-key-here
```

## File Paths

All file paths are absolute:

- Tools: `/Users/johnpugh/Documents/source/cce/backend/app/tools/`
- Memory: `/Users/johnpugh/Documents/source/cce/backend/app/memory/`
- Config: `/Users/johnpugh/Documents/source/cce/backend/app/config.py`

## Testing

```bash
# Activate virtual environment
source /Users/johnpugh/Documents/source/cce/backend/venv/bin/activate

# Run tests
python3 -m app.tools.test_tools
```

## Performance Tips

- `search_web`: 2-5 seconds
- `scrape_url`: 1-3 seconds
- `deep_research`: 2-5 minutes (use sparingly)
- Memory operations: < 1ms

## Best Practices

1. Use unique session IDs for each workflow
2. Organize memory with prefixes (research/, outline/, draft/)
3. Always handle API errors
4. Clean up sessions when done
5. Use deep_research only when needed (it's slow)
6. Prefer search_web + scrape_url for most use cases
