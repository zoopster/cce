# Architecture Documentation

Comprehensive architecture documentation for the Content Creation Engine.

## Table of Contents

- [System Overview](#system-overview)
- [Design Principles](#design-principles)
- [Multi-Agent System](#multi-agent-system)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [API Design](#api-design)
- [Memory Management](#memory-management)
- [Security Architecture](#security-architecture)
- [Performance Considerations](#performance-considerations)
- [Scalability](#scalability)

## System Overview

The Content Creation Engine is a sophisticated multi-agent system built on Anthropic's orchestrator-worker pattern. It orchestrates multiple Claude AI agents to research, generate, refine, and publish high-quality content.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
│                    (React + Vite)                           │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Topic   │  │Parameter │  │ Research │  │  Publish │  │
│  │  Input   │  │  Config  │  │  Display │  │ Controls │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  Agent   │  │ Content  │  │ Feedback │                 │
│  │  Status  │  │  Editor  │  │  Panel   │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/SSE
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                     API Layer                               │
│                    (FastAPI)                                │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Sessions │  │ Research │  │ Generate │  │ Publish  │  │
│  │  Router  │  │  Router  │  │  Router  │  │  Router  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                  Agent Orchestration Layer                  │
│                                                             │
│              ┌─────────────────────┐                        │
│              │    Lead Agent       │                        │
│              │   (Orchestrator)    │                        │
│              └──────────┬──────────┘                        │
│                         │                                    │
│         ┌───────────────┼───────────────┐                   │
│         ↓               ↓               ↓                   │
│    ┌─────────┐    ┌─────────┐    ┌─────────┐              │
│    │Research │    │Research │    │Research │              │
│    │  Sub-1  │    │  Sub-2  │    │  Sub-3  │  (Parallel)  │
│    └─────────┘    └─────────┘    └─────────┘              │
│                                                             │
│    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│    │  Generator  │  │  Iterator   │  │  Publisher  │     │
│    │    Agent    │  │    Agent    │  │    Agent    │     │
│    └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                      Tools Layer                            │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │ Firecrawl│  │ Firecrawl│  │Filesystem│                 │
│  │  Search  │  │  Scrape  │  │  Memory  │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                  External Services                          │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │ Anthropic│  │Firecrawl │  │WordPress │                 │
│  │   API    │  │   API    │  │   API    │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

## Design Principles

### 1. Orchestrator-Worker Pattern

Based on [Anthropic's multi-agent research](https://www.anthropic.com/engineering/multi-agent-research-system):

**Orchestrator (Lead Agent):**
- Analyzes task complexity
- Plans research strategy
- Spawns worker agents
- Synthesizes results
- Does not pass messages between workers

**Workers (Research Subagents):**
- Execute specific tasks in parallel
- Write results to shared memory (filesystem)
- Operate independently
- Do not communicate with each other directly

**Why This Pattern:**
- Avoids "delegation chains" complexity
- Enables true parallel execution
- Simplifies coordination
- Better performance for research tasks
- Clearer responsibility separation

### 2. Filesystem Memory

**Principle:** Agents write to filesystem instead of passing data through orchestrator.

**Benefits:**
- Prevents "telephone game" information loss
- Agents read primary sources directly
- Easier debugging (can inspect files)
- Natural versioning
- Transparent operation

**Implementation:**
```
app/memory/
├── session_{id}/
│   ├── research/
│   │   ├── subagent_1_findings.md
│   │   ├── subagent_2_findings.md
│   │   └── synthesis.md
│   └── content/
│       ├── version_1.md
│       └── version_2.md
```

### 3. Real-time Streaming

**Principle:** Stream content as it's generated, not after completion.

**Implementation:**
- Server-Sent Events (SSE) for one-way streaming
- Chunked content delivery
- Status updates during long operations

**Benefits:**
- Reduced perceived latency
- Better user experience
- Early error detection
- Progress visibility

### 4. Separation of Concerns

**Clear Layer Separation:**
```
Presentation (React)
    ↓ HTTP/SSE
API Layer (FastAPI)
    ↓ Function calls
Agent Layer (Claude)
    ↓ Tool calls
Tools Layer (Firecrawl, Memory)
    ↓ API calls
External Services
```

## Multi-Agent System

### Agent Hierarchy

```
                    User Request
                         ↓
                   ┌───────────┐
                   │Lead Agent │ (Orchestrator)
                   └─────┬─────┘
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
   ┌─────────┐      ┌─────────┐      ┌─────────┐
   │Research │      │Research │      │Research │
   │ Agent 1 │      │ Agent 2 │      │ Agent 3 │
   └────┬────┘      └────┬────┘      └────┬────┘
        │                │                │
        └────────────────┴────────────────┘
                         ↓
                  Filesystem Memory
                         ↓
                  ┌─────────────┐
                  │  Generator  │
                  │    Agent    │
                  └──────┬──────┘
                         ↓
                  ┌─────────────┐
                  │  Iterator   │
                  │    Agent    │
                  └──────┬──────┘
                         ↓
                  ┌─────────────┐
                  │  Publisher  │
                  │    Agent    │
                  └─────────────┘
```

### Agent Responsibilities

#### Lead Agent (Orchestrator)

**Role:** Strategic planning and coordination

**Capabilities:**
- Extended thinking for complex analysis
- Research strategy planning
- Subagent spawning (3-5 parallel)
- Research synthesis

**Does NOT:**
- Execute research directly
- Pass messages between subagents
- Generate content

**Tools:**
- Filesystem memory (read/write)

#### Research Subagent (Worker)

**Role:** Execute specific research tasks

**Capabilities:**
- Web search
- Content scraping
- Source evaluation
- Findings documentation

**Execution:**
- Runs in parallel with other subagents
- Independent operation
- Writes to filesystem memory

**Tools:**
- Firecrawl search
- Firecrawl scrape
- Filesystem memory (write)

#### Generator Agent

**Role:** Create initial content from research

**Capabilities:**
- Extended thinking for content planning
- Research analysis
- Structured content creation
- Real-time streaming

**Input:** Research findings from filesystem
**Output:** Markdown content (streamed)

**Tools:**
- Filesystem memory (read)

#### Iterator Agent

**Role:** Refine content based on feedback

**Capabilities:**
- Feedback analysis
- Targeted improvements
- Version management
- Iterative refinement

**Input:** Current content + user feedback
**Output:** Improved content (streamed)

**Tools:**
- Filesystem memory (read/write)

#### Publisher Agent

**Role:** Distribute content to platforms

**Capabilities:**
- WordPress publishing
- HTML generation
- Citation verification
- Preview generation

**Outputs:**
- WordPress post
- HTML file
- Preview HTML

**Tools:**
- WordPress REST API
- HTML templating

## Component Architecture

### Backend Components

#### FastAPI Application (`main.py`)

```python
app = FastAPI(
    title="Content Creation Engine",
    description="Multi-agent content creation system"
)

# CORS for frontend communication
app.add_middleware(CORSMiddleware, ...)

# Register routers
app.include_router(sessions_router)
app.include_router(research_router)
app.include_router(generate_router)
app.include_router(publish_router)
```

#### Configuration (`config.py`)

```python
class Settings(BaseSettings):
    # API Keys
    anthropic_api_key: str
    firecrawl_api_key: Optional[str]

    # WordPress
    wordpress_site_url: Optional[str]
    wordpress_username: Optional[str]
    wordpress_app_password: Optional[str]

    # Application
    app_name: str = "Content Creation Engine"
    memory_base_path: Path = Path("app/memory")
```

#### Base Agent (`agents/base.py`)

```python
class BaseAgent:
    """Base class for all agents."""

    def __init__(self, session_id: str, model: str = "claude-sonnet-4.5"):
        self.session_id = session_id
        self.model = model
        self.client = anthropic.Anthropic()

    async def execute(self, *args, **kwargs):
        """Execute agent-specific logic."""
        raise NotImplementedError
```

### Frontend Components

#### Component Hierarchy

```
App
├── TopicInput
├── ParameterPanel
├── AgentStatusPanel
├── ResearchPanel
├── ContentEditor
├── FeedbackPanel
└── PublishPanel
```

#### State Management

```javascript
// Session state
const [session, setSession] = useState(null)
const [step, setStep] = useState('input')

// Content state
const [content, setContent] = useState('')
const [research, setResearch] = useState(null)

// UI state
const [isLoading, setIsLoading] = useState(false)
const [error, setError] = useState(null)
const [agentStates, setAgentStates] = useState([])
```

#### API Client (`api/client.js`)

```javascript
// SSE connection handler
async function connectSSE(url, callbacks) {
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        // Parse and handle SSE events
        handleSSEChunk(chunk, callbacks)
    }
}
```

## Data Flow

### Research Phase

```
1. User Input
   Topic: "Sustainable urban farming"
   Parameters: { type, tone, audience, word_count }

2. Session Creation
   POST /api/sessions
   → Creates session with unique ID
   → Initializes memory directory

3. Research Initiation
   POST /api/sessions/{id}/research (SSE)
   → Lead agent analyzes topic
   → Plans research strategy
   → Spawns 3-5 subagents

4. Parallel Research
   Subagent 1: "Hydroponics techniques"
   Subagent 2: "Urban farming case studies"
   Subagent 3: "Sustainability metrics"
   Each:
   - Searches web via Firecrawl
   - Scrapes relevant content
   - Writes findings to filesystem

5. Synthesis
   Lead agent:
   - Reads all subagent findings
   - Synthesizes research
   - Writes synthesis to filesystem
   → SSE: event="complete"
```

### Generation Phase

```
1. Generation Request
   POST /api/sessions/{id}/generate (SSE)

2. Generator Agent
   - Reads research synthesis
   - Plans content structure (extended thinking)
   - Generates content section by section
   - Streams each section via SSE
   → SSE: event="content", data="{chunk}"

3. Content Storage
   - Complete content saved to filesystem
   - Version tracked
   → SSE: event="complete"
```

### Iteration Phase

```
1. User Feedback
   POST /api/sessions/{id}/iterate (SSE)
   Body: { feedback: "Add more examples" }

2. Iterator Agent
   - Reads current content
   - Analyzes feedback
   - Makes targeted improvements
   - Streams updated content

3. Version Update
   - New version saved to filesystem
   - Previous versions retained
```

### Publishing Phase

```
1. WordPress Publishing
   POST /api/sessions/{id}/publish/wordpress
   Body: { title, excerpt, status }

2. Publisher Agent
   - Verifies citations
   - Formats content for WordPress
   - Creates post via REST API
   - Returns post URL

OR

1. HTML Export
   POST /api/sessions/{id}/publish/html

2. Publisher Agent
   - Generates standalone HTML
   - Applies styling
   - Returns download link
```

## Technology Stack

### Backend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Core language |
| FastAPI | 0.115.0 | Web framework |
| Uvicorn | 0.30.0 | ASGI server |
| Anthropic SDK | 0.34.0 | Claude AI integration |
| Pydantic | 2.9.0 | Data validation |
| SSE-Starlette | 2.1.0 | Server-sent events |
| httpx | 0.27.0 | HTTP client |
| aiofiles | 24.1.0 | Async file I/O |

### Frontend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.3.1 | UI library |
| Vite | 5.4.0 | Build tool |
| React Markdown | 9.0.0 | Markdown rendering |

### External Services

| Service | Purpose | API Version |
|---------|---------|-------------|
| Anthropic Claude | AI agent execution | Latest |
| Firecrawl | Web search & scraping | Latest |
| WordPress | Publishing platform | REST API v2 |

## API Design

### RESTful Principles

- Resource-based URLs (`/api/sessions/{id}`)
- HTTP methods: GET, POST, DELETE
- JSON request/response
- Proper status codes

### SSE Endpoints

Research, generation, and iteration use SSE:

```
POST /api/sessions/{id}/research
POST /api/sessions/{id}/generate
POST /api/sessions/{id}/iterate
```

**Event Format:**
```json
{
  "event": "status",
  "data": {
    "agent": "research_subagent_1",
    "status": "searching",
    "details": "Searching for hydroponics techniques"
  }
}

{
  "event": "content",
  "data": {
    "chunk": "## Introduction\n\nSustainable urban farming..."
  }
}

{
  "event": "complete",
  "data": {
    "session_id": "uuid",
    "content": "...",
    "research": {...}
  }
}
```

### Error Handling

```python
# Standard error response
{
    "detail": "Error message",
    "status_code": 400,
    "type": "validation_error"
}
```

**HTTP Status Codes:**
- 200: Success
- 201: Created
- 400: Bad request
- 404: Not found
- 500: Server error

## Memory Management

### Session Memory Structure

```
app/memory/
└── session_{uuid}/
    ├── research/
    │   ├── plan.json
    │   ├── subagent_1_findings.md
    │   ├── subagent_2_findings.md
    │   ├── subagent_3_findings.md
    │   └── synthesis.md
    └── content/
        ├── version_1.md
        ├── version_2.md
        └── metadata.json
```

### Memory Operations

**Write Findings:**
```python
await memory.write_finding(
    session_id=session.id,
    agent_name="research_subagent_1",
    content=findings_markdown
)
```

**Read Research:**
```python
synthesis = await memory.read_synthesis(session_id)
```

**Store Content:**
```python
await memory.store_content(
    session_id=session.id,
    version=1,
    content=generated_content
)
```

### Cleanup

- Memory cleared on session deletion
- No automatic cleanup (sessions persist until deleted)
- Consider implementing TTL for production

## Security Architecture

### API Key Management

- All keys in environment variables
- Never committed to version control
- Loaded via python-dotenv
- Validated on startup

### CORS Configuration

Development:
```python
allow_origins=["*"]
```

Production:
```python
allow_origins=["https://yourdomain.com"]
```

### WordPress Authentication

- Application passwords (not main password)
- Transmitted over HTTPS only
- No storage of credentials beyond .env

### Input Validation

- Pydantic models validate all inputs
- Type checking enforced
- Content sanitization for HTML output

## Performance Considerations

### Parallel Research

- 3-5 subagents run simultaneously
- 3-5x faster than sequential
- Limited by Firecrawl API rate limits

### Streaming Response

- Content streams as generated
- Reduces perceived latency
- Better user experience

### Caching Opportunities

- Firecrawl results (future enhancement)
- Generated content (filesystem)
- Research synthesis (filesystem)

### Resource Usage

**Memory:**
- ~100MB base (Python + FastAPI)
- ~50MB per active session
- Grows with content size

**CPU:**
- Light (mostly I/O bound)
- Spikes during JSON parsing
- Minimal for streaming

**Network:**
- Heavy during research (Firecrawl calls)
- Moderate during generation (Claude API)
- Light for frontend (SSE streaming)

## Scalability

### Current Limitations

- In-memory session storage
- Single server
- No load balancing
- No database

### Scaling Strategies

**Horizontal Scaling:**
1. Add database for session persistence
2. Use Redis for shared state
3. Load balancer in front
4. Multiple API server instances

**Vertical Scaling:**
1. Increase Gunicorn workers
2. More CPU cores for parallel research
3. More RAM for concurrent sessions

**Future Architecture:**

```
┌─────────┐
│  Load   │
│Balancer │
└────┬────┘
     │
     ├─────────┬─────────┬─────────┐
     ↓         ↓         ↓         ↓
┌─────────┐┌─────────┐┌─────────┐
│  API    ││  API    ││  API    │
│Server 1 ││Server 2 ││Server 3 │
└────┬────┘└────┬────┘└────┬────┘
     │          │          │
     └──────────┴──────────┘
            ↓
     ┌─────────────┐
     │   Redis     │
     │   Cache     │
     └─────────────┘
            ↓
     ┌─────────────┐
     │  PostgreSQL │
     │  Database   │
     └─────────────┘
```

## Deployment Architecture

### Production Setup

```
Internet
   ↓
[Nginx/Caddy] (Reverse Proxy + SSL)
   ↓
   ├──→ [Static Files] (Frontend - port 80)
   └──→ [FastAPI] (Backend - port 8000)
         ↓
      [Gunicorn] (4 workers)
         ↓
      [uvicorn.workers.UvicornWorker]
```

### Docker Architecture

```
┌─────────────────────┐
│   Docker Compose    │
├─────────────────────┤
│                     │
│  ┌──────────────┐  │
│  │   Backend    │  │
│  │ Container    │  │
│  │  Port: 8000  │  │
│  └──────────────┘  │
│                     │
│  ┌──────────────┐  │
│  │  Frontend    │  │
│  │ Container    │  │
│  │   Port: 80   │  │
│  └──────────────┘  │
│                     │
│  [Shared Network]   │
└─────────────────────┘
```

## Design Decisions

### Why FastAPI over Flask?

- Automatic OpenAPI docs
- Native async/await support
- Type hints and validation
- Better performance
- Modern development experience

### Why SSE over WebSockets?

- Simpler for one-way streaming
- Built-in browser support
- Automatic reconnection
- No additional libraries needed
- Lower overhead

### Why Filesystem over Database?

**For MVP:**
- Simpler implementation
- Easier debugging
- No database management
- Natural for file-based content

**For Production:**
- Should migrate to database
- Better querying
- Easier scaling
- Session persistence

### Why React over Vue/Svelte?

- Larger ecosystem
- Better documentation
- More developers familiar
- Excellent tooling (Vite)
- Mature and stable

## Monitoring and Observability

### Logging Strategy

```python
# Structured logging
logger.info("Research started", extra={
    "session_id": session.id,
    "topic": topic,
    "num_subagents": 5
})
```

### Metrics to Track

- Request count by endpoint
- Average research time
- Average generation time
- Error rates
- Active sessions
- Memory usage
- API call counts (Anthropic, Firecrawl)

### Health Checks

```
GET /health
→ {"status": "healthy", "service": "content-creation-engine"}
```

## Future Architecture

### Database Integration

```python
# PostgreSQL schema
sessions (
    id UUID PRIMARY KEY,
    topic TEXT,
    parameters JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

research_findings (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions,
    agent_name TEXT,
    content TEXT,
    created_at TIMESTAMP
)

content_versions (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions,
    version INTEGER,
    content TEXT,
    created_at TIMESTAMP
)
```

### Caching Layer

```python
# Redis for caching
redis.set(f"research:{topic_hash}", synthesis, ex=3600)
```

### Queue System

```python
# Celery for background tasks
@celery.task
def research_task(session_id, topic, parameters):
    # Long-running research
    pass
```

---

**This architecture is designed for:**
- Clear separation of concerns
- Easy testing and debugging
- Scalable growth
- Maintainable codebase
- Production deployment

Built following [Anthropic's best practices](https://www.anthropic.com/engineering/multi-agent-research-system) for multi-agent systems.
