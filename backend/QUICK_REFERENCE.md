# Content Creation Engine - Quick Reference

## Agent Files

```
/Users/johnpugh/Documents/source/cce/backend/app/agents/
├── base.py              # BaseAgent (foundation class)
├── research.py          # ResearchSubagent (parallel workers)
├── lead.py             # LeadAgent (orchestrator) ← NEW
├── generator.py        # ContentGeneratorAgent ← NEW
└── __init__.py         # Module exports (updated)
```

## Lead Agent Quick Reference

### Import
```python
from app.agents import LeadAgent
```

### Initialize
```python
lead = LeadAgent(session)
```

### Main Methods
```python
# Complete workflow (recommended)
synthesis = await lead.run_full_research()

# Or step-by-step:
complexity = await lead.analyze_complexity()
plan = await lead.create_research_plan()
results = await lead.execute_research(plan)
synthesis = await lead.synthesize_findings()
```

### Complexity Determination
- **SIMPLE**: 1 subagent, 3-10 tool calls
- **MODERATE**: 3 subagents, 10-15 tool calls each
- **COMPLEX**: 5 subagents, 15-20 tool calls each

## Content Generator Quick Reference

### Import
```python
from app.agents import ContentGeneratorAgent
```

### Initialize
```python
generator = ContentGeneratorAgent(session)
```

### Main Methods
```python
# Non-streaming (recommended for API)
content = await generator.run_generation()

# Streaming (recommended for UI)
async for chunk in generator.generate_stream():
    print(chunk, end='', flush=True)

# Step-by-step:
research = await generator.read_research()
outline = await generator.plan_structure(research)
content = await generator.generate_content(research, outline)
```

## Complete Workflow Example

```python
from app.agents import LeadAgent, ContentGeneratorAgent
from app.models import ContentSession, GenerationParameters
from app.models.parameters import ContentType, Tone, AudienceLevel

# 1. Create session
session = ContentSession(
    topic="Your topic here",
    parameters=GenerationParameters(
        content_type=ContentType.BLOG_POST,
        tone=Tone.PROFESSIONAL,
        audience_level=AudienceLevel.GENERAL,
        word_count=1500,
        keywords=["keyword1", "keyword2"],
        custom_instructions="Optional instructions"
    )
)

# 2. Research
lead = LeadAgent(session)
synthesis = await lead.run_full_research()

# 3. Generate
generator = ContentGeneratorAgent(session)
content = await generator.run_generation()

# 4. Access
print(content)
```

## Filesystem Memory

All data persists in: `app/memory/{session_id}/`

```
app/memory/{session_id}/
├── plan.json              # Research plan
├── synthesis.json         # Research synthesis
├── outline.json          # Content outline
├── research/
│   ├── research_*.json   # Subagent findings
└── versions/
    └── v*.json           # Content versions
```

## Agent States

Track agent progress via `get_state()`:

```python
state = lead.get_state()
# Returns AgentState with:
# - agent_id, agent_type, status, current_task
# - tool_calls, findings_count
```

## Configuration

Agents use models from:
- `app.models.content` - ContentSession, Complexity, ContentVersion
- `app.models.parameters` - GenerationParameters, ContentType, Tone
- `app.config` - settings (API keys, memory path)

## Tools Used

Agents integrate with:
- `app.tools.search.search_web()` - Web search
- `app.tools.scrape.scrape_url()` - Content extraction
- `app.tools.memory.save_to_memory()` - Persistence
- `app.tools.memory.aggregate_research()` - Aggregation

## Error Handling

```python
try:
    synthesis = await lead.run_full_research()
except Exception as e:
    print(f"Research failed: {e}")
    # Error logged to filesystem
    # Session state reflects error
```

## Key Design Patterns

1. **Orchestrator-Worker**: Lead delegates to parallel subagents
2. **Filesystem Coordination**: Shared memory prevents data loss
3. **Start Wide, Then Narrow**: Broad → specific searches
4. **Adaptive Research**: Optional follow-up if gaps found
5. **Extended Thinking**: Plan structure before writing
6. **Streaming**: Real-time content display

## Next Steps After Implementation

1. Create API endpoints (FastAPI routes)
2. Add WebSocket support for streaming
3. Implement Iterator Agent for refinement
4. Add Publisher Agent for WordPress
5. Build frontend UI for session management

## Documentation

- `AGENTS_README.md` - Complete architecture guide
- `AGENT_WORKFLOW_EXAMPLE.py` - Workflow demonstration
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `QUICK_REFERENCE.md` - This file

## References

- [Anthropic Multi-Agent Research](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [Claude Sonnet 4 Docs](https://docs.anthropic.com/)
