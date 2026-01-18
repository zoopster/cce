# Tools Layer Setup Guide

This guide will help you set up and verify the Tools Layer for the Content Creation Engine.

## Files Created

The following files have been created in `/Users/johnpugh/Documents/source/cce/backend/app/tools/`:

1. **__init__.py** (806 bytes) - Module exports and initialization
2. **search.py** (2,491 bytes) - Web search tools using Firecrawl API
3. **scrape.py** (3,318 bytes) - Content extraction and deep research tools
4. **memory.py** (4,403 bytes) - Filesystem-based memory operations
5. **test_tools.py** (5,566 bytes) - Comprehensive test suite
6. **README.md** - Complete documentation

**Total:** 584 lines of Python code

## Prerequisites

### 1. Virtual Environment Setup

Create and activate a virtual environment (if not already done):

```bash
cd /Users/johnpugh/Documents/source/cce/backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Ensure your `.env` file has the Firecrawl API key:

```bash
# .env file location: /Users/johnpugh/Documents/source/cce/backend/.env
FIRECRAWL_API_KEY=fc-your-api-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
```

## Installation

With the virtual environment activated:

```bash
# Navigate to backend directory
cd /Users/johnpugh/Documents/source/cce/backend

# Verify dependencies are installed
pip list | grep -E "httpx|pydantic|python-dotenv"

# Should show:
# httpx        0.27.0
# pydantic     2.9.0
# python-dotenv 1.0.0
```

## Verification

### Quick Import Test

```bash
# Activate virtual environment first
source venv/bin/activate

# Test imports
python3 -c "from app.tools import search_web, scrape_url, save_to_memory; print('✓ All imports successful!')"
```

### Run Test Suite

```bash
# Full test suite (requires valid Firecrawl API key)
python3 -m app.tools.test_tools
```

Expected output:
```
============================================================
TOOLS LAYER TEST SUITE
============================================================

=== Testing Memory Tools ===
...
✓ All memory tests passed!

=== Testing Search Tools ===
...
✓ All search tests passed!

=== Testing Scrape Tools ===
...
✓ All scrape tests passed!

============================================================
TEST SUMMARY
============================================================
✓ PASS: Memory Tools
✓ PASS: Search Tools
✓ PASS: Scrape Tools
============================================================

🎉 All tests passed!
```

## Usage Examples

### 1. Web Search

```python
import asyncio
from app.tools import search_web, search_broad, search_narrow

async def example_search():
    # Basic search
    results = await search_web("Python async programming", limit=5)
    for result in results:
        print(f"Title: {result.get('title')}")
        print(f"URL: {result.get('url')}")
        print(f"Description: {result.get('description')}")
        print("---")

    # Broad topic exploration
    broad_results = await search_broad("artificial intelligence", limit=10)

    # Focused search
    narrow_results = await search_narrow("AI", "ethics", limit=3)

asyncio.run(example_search())
```

### 2. Content Scraping

```python
import asyncio
from app.tools import scrape_url, deep_research

async def example_scrape():
    # Scrape a single URL
    content = await scrape_url("https://www.python.org")
    print("Markdown content:", content["markdown"][:500])
    print("Title:", content.get("metadata", {}).get("title"))

    # Deep research (takes 2-5 minutes)
    research = await deep_research(
        "Impact of AI on software development",
        max_depth=3,
        max_urls=20
    )
    print("Analysis:", research.get("finalAnalysis"))
    print("Sources:", len(research.get("sources", [])))

asyncio.run(example_scrape())
```

### 3. Memory Operations

```python
from app.tools import (
    save_to_memory,
    read_from_memory,
    list_memory_keys,
    aggregate_research,
    clear_session_memory
)

# Save research findings
session_id = "blog_post_123"

save_to_memory(session_id, "research/agent_1", {
    "sources": ["https://example.com/article1"],
    "findings": "Key insight about the topic...",
    "summary": "Brief summary of findings"
})

save_to_memory(session_id, "research/agent_2", {
    "sources": ["https://example.com/article2"],
    "findings": "Additional insights..."
})

# Read specific findings
agent_1_data = read_from_memory(session_id, "research/agent_1")
print(agent_1_data)

# List all research keys
research_keys = list_memory_keys(session_id, prefix="research/")
print(f"Research agents: {research_keys}")

# Aggregate all research
all_research = aggregate_research(session_id)
print(f"Total sources: {all_research['total_sources']}")
print(f"All findings: {all_research['findings']}")

# Cleanup
clear_session_memory(session_id)
```

## File Structure

```
backend/app/tools/
├── __init__.py           # Module exports
├── search.py             # Search tools
│   ├── search_web()
│   ├── search_broad()
│   └── search_narrow()
├── scrape.py             # Scrape tools
│   ├── scrape_url()
│   └── deep_research()
├── memory.py             # Memory tools
│   ├── save_to_memory()
│   ├── read_from_memory()
│   ├── list_memory_keys()
│   ├── aggregate_research()
│   ├── clear_session_memory()
│   └── get_session_path()
├── test_tools.py         # Test suite
└── README.md             # Documentation
```

## Memory Storage Location

Memory files are stored in:
```
/Users/johnpugh/Documents/source/cce/backend/app/memory/{session_id}/
```

Example structure:
```
app/memory/
└── blog_post_123/
    ├── research/
    │   ├── agent_1.json
    │   ├── agent_2.json
    │   └── agent_3.json
    ├── outline/
    │   └── structure.json
    └── draft/
        └── content.json
```

## Integration with Agents

The tools layer integrates with the agents layer:

```python
from app.agents import ResearchAgent
from app.tools import aggregate_research

# Research agent uses tools internally
agent = ResearchAgent()
findings = await agent.research("AI ethics", session_id="session_123")

# Aggregate findings from all agents
all_research = aggregate_research("session_123")
```

## Troubleshooting

### ImportError: No module named 'httpx'

**Solution:** Make sure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### ValueError: Firecrawl API key not configured

**Solution:** Add your Firecrawl API key to the `.env` file:
```bash
echo "FIRECRAWL_API_KEY=fc-your-key-here" >> .env
```

### httpx.HTTPStatusError

**Solution:** Check your Firecrawl API key is valid and you haven't exceeded rate limits.

### Memory files not being created

**Solution:** Check permissions and ensure the memory directory exists:
```bash
mkdir -p /Users/johnpugh/Documents/source/cce/backend/app/memory
chmod 755 /Users/johnpugh/Documents/source/cce/backend/app/memory
```

## Next Steps

1. **Test the tools layer** - Run the test suite to verify everything works
2. **Review the README** - See `app/tools/README.md` for detailed documentation
3. **Integrate with agents** - Use these tools in the agent implementations
4. **Customize as needed** - Extend the tools layer for your specific needs

## API Documentation

### Search Tools

- **search_web(query, limit=5, lang="en", country="us")** → List[Dict]
  - General web search with content extraction
  - Returns: List of results with url, title, description, markdown

- **search_broad(topic, limit=5)** → List[Dict]
  - Broad topic exploration with short queries

- **search_narrow(topic, aspect, limit=3)** → List[Dict]
  - Focused search on specific aspect

### Scrape Tools

- **scrape_url(url, formats=["markdown"], only_main_content=True)** → Dict
  - Extract content from a single URL
  - Returns: {markdown: str, metadata: dict, url: str}

- **deep_research(topic, max_depth=3, max_urls=20)** → Dict
  - Comprehensive research with LLM analysis
  - Returns: {finalAnalysis: str, sources: list, activities: list}

### Memory Tools

- **save_to_memory(session_id, key, data)** → str
  - Save data to filesystem memory
  - Returns: File path where data was saved

- **read_from_memory(session_id, key)** → Optional[Any]
  - Read data from memory
  - Returns: Stored data or None

- **list_memory_keys(session_id, prefix="")** → List[str]
  - List all memory keys for a session
  - Returns: Sorted list of keys

- **aggregate_research(session_id)** → Dict
  - Combine all research findings
  - Returns: {sources: list, findings: list, total_sources: int}

- **clear_session_memory(session_id)** → bool
  - Delete all memory for a session
  - Returns: True if deleted, False if didn't exist

- **get_session_path(session_id)** → Path
  - Get the filesystem path for a session
  - Returns: Path object

## Performance Notes

- **search_web**: Typically completes in 2-5 seconds
- **scrape_url**: Typically completes in 1-3 seconds
- **deep_research**: Can take 2-5 minutes depending on max_depth and max_urls
- **memory operations**: Sub-millisecond for most operations

## License

Part of the Content Creation Engine project.
