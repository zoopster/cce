# Research Subagent

Parallel worker agent that searches for specific information following Anthropic's multi-agent research patterns.

## Overview

The Research Subagent is a worker agent designed to execute in parallel with other subagents, each with a distinct research task. It implements the key principles from Anthropic's [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system):

1. **Broad-to-narrow search strategy** - Start with wide queries, then drill into specifics
2. **Filesystem-based coordination** - Write findings directly to disk to avoid "telephone game" information loss
3. **Interleaved thinking** - Evaluate source quality between tool calls
4. **Independent execution** - Each subagent explores autonomously

## Architecture

```
Lead Agent (Orchestrator)
    |
    |-- Creates ResearchTasks
    |
    +-- Spawns Multiple ResearchSubagents (Workers)
        |
        |-- ResearchSubagent 1 --> Filesystem
        |-- ResearchSubagent 2 --> Filesystem
        |-- ResearchSubagent 3 --> Filesystem
        |
    +-- Aggregates results from Filesystem
```

## Key Features

### 1. Parallel Execution
Multiple research subagents run simultaneously, each exploring different aspects:

```python
tasks = [
    ResearchTask(objective="Find statistics...", ...),
    ResearchTask(objective="Find expert opinions...", ...),
    ResearchTask(objective="Find case studies...", ...)
]

results = await run_parallel_research(session_id, tasks)
```

### 2. Broad-to-Narrow Search
Each subagent follows a systematic search strategy:
- **Broad queries (first 2)**: Explore the landscape
- **Evaluation**: Claude assesses source quality
- **Narrow queries (remaining)**: Drill into specifics
- **Scraping**: Deep content extraction from top sources

### 3. Filesystem Memory
Findings are written directly to disk:
```
app/memory/
  {session_id}/
    research/
      research_abc123.json  # Subagent 1 findings
      research_def456.json  # Subagent 2 findings
      research_ghi789.json  # Subagent 3 findings
```

This avoids the "telephone game" where information degrades through multiple LLM passes.

### 4. Source Evaluation
Between search and scraping, Claude evaluates sources:
- Relevance to research objective
- Source authority and credibility
- Content quality indicators

## Usage

### Basic Usage

```python
from app.agents import ResearchSubagent, ResearchTask

# Define a research task
task = ResearchTask(
    objective="Find latest AI safety research",
    search_queries=[
        "AI safety research 2024",        # Broad
        "AI alignment techniques",        # Broad
        "AI safety mechanistic interpretability"  # Narrow
    ],
    output_format="summary",
    max_sources=5,
    tool_guidance="Focus on academic papers and research institutions"
)

# Create and execute subagent
agent = ResearchSubagent(session_id="my_session", task=task)
result = await agent.execute()

# Result is also written to: app/memory/my_session/research/research_<id>.json
```

### Parallel Research

```python
from app.agents import run_parallel_research, ResearchTask

# Create multiple research tasks
tasks = [
    ResearchTask(
        objective="Find market size data",
        search_queries=["market size 2024", "industry growth statistics"]
    ),
    ResearchTask(
        objective="Find competitor analysis",
        search_queries=["competitor landscape", "competitive analysis"]
    ),
    ResearchTask(
        objective="Find customer needs",
        search_queries=["customer pain points", "user research"]
    )
]

# Run all tasks in parallel
results = await run_parallel_research(session_id="session_123", tasks)

# Each result contains:
# - agent_id: Unique identifier
# - objective: The research goal
# - summary: Synthesized findings
# - sources: List of sources with URLs
# - tool_calls: Number of API calls made
# - completed_at: Timestamp
```

## ResearchTask Configuration

### Constructor Parameters

```python
ResearchTask(
    objective: str,           # What to find out
    search_queries: List[str], # Queries to execute
    output_format: str = "summary",  # summary | detailed | bullet_points
    max_sources: int = 5,     # Max sources to scrape
    tool_guidance: str = ""   # Guidance for source evaluation
)
```

### Output Formats

- **summary**: Concise overview with key points
- **detailed**: Comprehensive analysis with examples
- **bullet_points**: Structured list format

### Tool Guidance Examples

```python
# For authoritative sources
tool_guidance="Focus on academic papers, research institutions, and expert analysis"

# For recent information
tool_guidance="Prioritize sources from 2024, prefer primary sources over secondary"

# For practical content
tool_guidance="Look for case studies, implementation guides, and real-world examples"
```

## Execution Flow

Each ResearchSubagent follows this workflow:

```python
async def execute(self):
    # 1. Broad search (first 2 queries)
    broad_results = await self._search_broad()

    # 2. Evaluate sources (LLM thinking step)
    promising = await self._evaluate_sources(broad_results)

    # 3. Narrow search if needed (remaining queries)
    if len(promising) < max_sources:
        narrow_results = await self._search_narrow()
        promising.extend(narrow_results)

    # 4. Scrape top sources (parallel, limit 3)
    scraped = await self._scrape_sources(promising)

    # 5. Synthesize findings (LLM synthesis)
    synthesis = await self._synthesize_findings(scraped)

    # 6. Write to filesystem
    self._write_findings_to_memory(synthesis)

    return synthesis
```

## Memory Structure

Findings written to filesystem:

```json
{
  "data": {
    "agent_id": "research_abc123",
    "objective": "Find AI safety research",
    "summary": "# AI Safety Research\n\n...",
    "sources": [
      {
        "url": "https://example.com/paper",
        "title": "AI Safety Paper",
        "snippet": "Abstract content..."
      }
    ],
    "tool_calls": 12,
    "completed_at": "2024-01-17T10:30:00"
  },
  "saved_at": "2024-01-17T10:30:00",
  "key": "research/research_abc123"
}
```

## Error Handling

Subagents handle errors gracefully:

```python
try:
    result = await agent.execute()
except Exception as e:
    # Error is written to memory
    # Other parallel agents continue
    # Lead agent can handle partial results
```

Error memory structure:
```json
{
  "agent_id": "research_abc123",
  "objective": "Research task",
  "error": "Connection timeout",
  "tool_calls": 5,
  "completed_at": "2024-01-17T10:30:00"
}
```

## Agent State

Track execution progress:

```python
state = agent.get_state()

# Returns:
AgentState(
    agent_id="research_abc123",
    agent_type="research",
    status="executing",  # created | executing | complete | error
    current_task="Find AI safety research",
    tool_calls=8,
    findings_count=3
)
```

## Integration with Lead Agent

The Lead Agent orchestrates research subagents:

```python
# Lead Agent creates tasks based on complexity analysis
if complexity == "COMPLEX":
    # Create 5-10 specialized research tasks
    tasks = lead_agent.decompose_research(topic)
elif complexity == "MODERATE":
    # Create 2-4 research tasks
    tasks = lead_agent.create_research_tasks(topic)
else:
    # Create 1 simple research task
    tasks = [lead_agent.create_basic_task(topic)]

# Spawn parallel workers
results = await run_parallel_research(session_id, tasks)

# Aggregate findings from filesystem
aggregated = aggregate_research(session_id)
```

## Best Practices

### 1. Task Decomposition
Create focused, specific research objectives:

```python
# Good - Specific and actionable
ResearchTask(objective="Find Python async/await performance benchmarks")

# Less good - Too broad
ResearchTask(objective="Research Python")
```

### 2. Query Design
First 2 queries broad, rest narrow:

```python
search_queries=[
    "topic overview",           # Broad
    "topic trends",             # Broad
    "topic specific_aspect",    # Narrow
    "topic detailed_subtopic"   # Narrow
]
```

### 3. Source Limits
Balance thoroughness with performance:

```python
# Quick research: 2-3 sources
max_sources=3

# Standard research: 4-5 sources
max_sources=5

# Deep research: 6-8 sources (rare)
max_sources=8
```

### 4. Parallelism
Run 2-10 subagents based on complexity:

```python
# Simple content: 1-2 subagents
# Moderate: 2-4 subagents
# Complex: 5-10 subagents
```

## Performance Characteristics

- **Broad search**: 2 queries × 5 results = 10 sources
- **Evaluation**: 1 LLM call (~100 tokens)
- **Narrow search**: 1-3 queries × 3 results = 3-9 sources
- **Scraping**: 3 sources in parallel
- **Synthesis**: 1 LLM call (~1500 tokens)

**Total per subagent**: 5-10 tool calls, ~2-3 LLM calls, 30-60 seconds

**Parallel execution**: 3 subagents complete in ~40 seconds vs 120 seconds sequential

## Dependencies

- `anthropic` - Claude API client
- `httpx` - Async HTTP for Firecrawl API
- `asyncio` - Async/parallel execution
- `pydantic` - Data models

## Related Files

- `/Users/johnpugh/Documents/source/cce/backend/app/agents/base.py` - BaseAgent class
- `/Users/johnpugh/Documents/source/cce/backend/app/agents/research.py` - ResearchSubagent implementation
- `/Users/johnpugh/Documents/source/cce/backend/app/tools/search.py` - Search tools
- `/Users/johnpugh/Documents/source/cce/backend/app/tools/scrape.py` - Scraping tools
- `/Users/johnpugh/Documents/source/cce/backend/app/tools/memory.py` - Memory operations
- `/Users/johnpugh/Documents/source/cce/backend/app/models/content.py` - Data models

## References

- [Anthropic Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Orchestrator-Worker Pattern](https://docs.anthropic.com/en/docs/agents/multi-agent-systems)
