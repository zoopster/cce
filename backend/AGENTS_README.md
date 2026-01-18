# Content Creation Engine - Multi-Agent Architecture

This document describes the Lead Agent and Content Generator Agent implementation following Anthropic's orchestrator-worker pattern.

## Overview

The Content Creation Engine uses a multi-agent system with the following components:

1. **Lead Agent (Orchestrator)** - Coordinates the research process
2. **Research Subagents (Workers)** - Execute parallel research tasks
3. **Content Generator Agent** - Creates content from research findings

## Architecture Pattern

Following [Anthropic's Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system):

```
┌─────────────────────────────────────────────────────┐
│                   Lead Agent                        │
│  (Orchestrator - Delegates & Synthesizes)           │
└──────────────────┬──────────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
    ┌────▼─────┐      ┌─────▼─────┐
    │ Research │      │ Research  │    (3-5 agents
    │  Agent 1 │ ...  │  Agent N  │     in parallel)
    └────┬─────┘      └─────┬─────┘
         │                   │
         └─────────┬─────────┘
                   │
         ┌─────────▼─────────┐
         │   Filesystem      │
         │   (Memory Store)  │
         └─────────┬─────────┘
                   │
         ┌─────────▼─────────┐
         │ Content Generator │
         │     Agent         │
         └───────────────────┘
```

## Lead Agent (`app/agents/lead.py`)

### Responsibilities

1. **Analyze Complexity** - Determine research scope (simple/moderate/complex)
2. **Create Research Plan** - Decompose topic into parallel tasks
3. **Execute Research** - Spawn parallel research subagents
4. **Synthesize Findings** - Aggregate results from filesystem
5. **Adaptive Research** - Decide if more research is needed

### Complexity Levels

- **SIMPLE**: 1 subagent, 3-10 tool calls (fact-finding)
- **MODERATE**: 3 subagents, 10-15 tool calls each (comparisons)
- **COMPLEX**: 5 subagents, 15-20 tool calls each (deep research)

### Key Methods

```python
async def analyze_complexity() -> Complexity:
    """Determines research complexity using Claude."""

async def create_research_plan() -> Dict[str, Any]:
    """Creates task decomposition with search queries."""

async def execute_research(plan: Dict) -> Dict:
    """Spawns parallel research subagents."""

async def synthesize_findings() -> str:
    """Aggregates results from filesystem memory."""

async def run_full_research() -> str:
    """Complete workflow with optional follow-up research."""
```

### Usage Example

```python
from app.agents import LeadAgent
from app.models import ContentSession, GenerationParameters

session = ContentSession(
    topic="Python async programming",
    parameters=GenerationParameters(
        content_type=ContentType.TECHNICAL_TUTORIAL,
        word_count=2000,
        audience_level=AudienceLevel.INTERMEDIATE
    )
)

lead = LeadAgent(session)
synthesis = await lead.run_full_research()
print(synthesis)
```

## Content Generator Agent (`app/agents/generator.py`)

### Responsibilities

1. **Read Research** - Load synthesized findings from filesystem
2. **Plan Structure** - Create content outline using extended thinking
3. **Generate Content** - Write complete content based on parameters
4. **Stream Output** - Support real-time content display
5. **Version Management** - Save content versions to memory

### Key Methods

```python
async def read_research() -> str:
    """Loads synthesized research from filesystem."""

async def plan_structure(research: str) -> str:
    """Creates detailed content outline."""

async def generate_content(research: str, outline: str) -> str:
    """Generates complete content (non-streaming)."""

async def generate_stream() -> AsyncGenerator[str, None]:
    """Streams content generation for real-time display."""

async def run_generation() -> str:
    """Complete generation workflow."""
```

### Usage Example

```python
from app.agents import ContentGeneratorAgent

# After research is complete
generator = ContentGeneratorAgent(session)
content = await generator.run_generation()
print(content)
```

### Streaming Example

```python
async for chunk in generator.generate_stream():
    print(chunk, end='', flush=True)
```

## Filesystem Memory Pattern

Following Anthropic's recommendation to **avoid the telephone game**:

All agents write findings directly to filesystem:

```
app/memory/{session_id}/
├── plan.json                    # Research plan from Lead Agent
├── synthesis.json               # Synthesized findings
├── outline.json                 # Content outline
├── research/
│   ├── research_abc123.json    # Subagent 1 findings
│   ├── research_def456.json    # Subagent 2 findings
│   └── research_ghi789.json    # Subagent 3 findings
└── versions/
    ├── v1.json                  # Content version 1
    └── v2.json                  # Content version 2
```

This prevents information loss during agent coordination.

## Key Design Patterns

### 1. Orchestrator-Worker Pattern

The Lead Agent orchestrates multiple Research Subagents:
- Delegates specific tasks
- Each worker explores independently
- Results aggregated from shared filesystem

### 2. Start Wide, Then Narrow

Research queries progress from broad to specific:
```python
search_queries = [
    "Python async programming",           # Broad
    "Python asyncio tutorial",            # Broad
    "Python async await best practices",  # Narrow
    "Python asyncio error handling"       # Narrow
]
```

### 3. Interleaved Thinking

Research Subagents evaluate sources between tool calls:
```python
# Step 1: Search broad
results = await search_web(broad_query)

# Step 2: Think - evaluate quality
promising = await evaluate_sources(results)

# Step 3: Search narrow
more_results = await search_web(narrow_query)

# Step 4: Think - synthesize
synthesis = await synthesize_findings(all_results)
```

### 4. Filesystem Coordination

Agents coordinate via shared filesystem rather than passing data:
```python
# Subagent writes
save_to_memory(session_id, "research/agent_1", findings)

# Lead Agent reads
findings = aggregate_research(session_id)
```

## Integration with Existing Code

The agents integrate with existing models and tools:

### Models Used

- `ContentSession` - Session state and metadata
- `GenerationParameters` - Content configuration
- `Complexity` - Research complexity enum
- `ContentVersion` - Version tracking
- `AgentState` - UI state updates

### Tools Used

- `search_web()` - Web search via Firecrawl
- `scrape_url()` - URL content extraction
- `save_to_memory()` - Filesystem persistence
- `aggregate_research()` - Result aggregation

## Complete Workflow

```python
from app.agents import LeadAgent, ContentGeneratorAgent
from app.models import ContentSession, GenerationParameters

# 1. Create session
session = ContentSession(
    topic="Building REST APIs with FastAPI",
    parameters=GenerationParameters(
        content_type=ContentType.TECHNICAL_TUTORIAL,
        tone=Tone.TECHNICAL,
        audience_level=AudienceLevel.INTERMEDIATE,
        word_count=2500,
        keywords=["FastAPI", "REST API", "Python"]
    )
)

# 2. Research phase
lead = LeadAgent(session)
synthesis = await lead.run_full_research()

# 3. Generation phase
generator = ContentGeneratorAgent(session)
content = await generator.run_generation()

# 4. Access content
print(content)
print(f"Version: {len(session.versions)}")
```

## Error Handling

Both agents implement robust error handling:

```python
try:
    synthesis = await lead.run_full_research()
except Exception as e:
    # Lead agent logs error to filesystem
    # Session state reflects error condition
    print(f"Research failed: {e}")
```

## Performance Characteristics

### Lead Agent
- **Parallel execution**: 3-5 subagents run concurrently
- **Adaptive research**: Optional second round if gaps detected
- **Token efficient**: Uses Sonnet 4 for planning

### Generator Agent
- **Streaming support**: Real-time content display
- **Extended thinking**: Plans structure before writing
- **Version tracking**: All versions saved to filesystem

## Testing

Run the verification script:

```bash
cd backend
python3 test_agents.py
```

## Next Steps

Potential enhancements:
1. **Iterator Agent** - Refine content based on feedback
2. **Publisher Agent** - Deploy to WordPress/other platforms
3. **Quality Scorer** - Evaluate content against criteria
4. **Caching Layer** - Reuse research across similar topics

## References

- [Anthropic: Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [Anthropic: Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Anthropic API Documentation](https://docs.anthropic.com/)

## Files Created

- `/Users/johnpugh/Documents/source/cce/backend/app/agents/lead.py`
- `/Users/johnpugh/Documents/source/cce/backend/app/agents/generator.py`
- `/Users/johnpugh/Documents/source/cce/backend/app/agents/__init__.py` (updated)
