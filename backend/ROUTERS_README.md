# FastAPI Routers - Complete Implementation

## Overview

This document provides a complete overview of the router implementation for the Content Creation Engine API.

## Router Files

### 1. Sessions Router (`app/routers/sessions.py`)

**Purpose:** Manage content creation sessions (CRUD operations)

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/sessions` | Create new session |
| GET | `/api/sessions/{id}` | Get session details |
| DELETE | `/api/sessions/{id}` | Delete session |
| GET | `/api/sessions/{id}/agents` | Get agent states |
| GET | `/api/sessions/{id}/versions` | List content versions |
| GET | `/api/sessions/{id}/content` | Get current content |

**Key Features:**
- In-memory session storage (dict-based)
- Automatic persistence to filesystem via memory system
- Session restoration from disk on restart
- Pydantic models for request/response validation
- Comprehensive error handling

**Models:**
```python
class CreateSessionRequest(BaseModel):
    topic: str
    parameters: Optional[GenerationParameters] = None

class CreateSessionResponse(BaseModel):
    session_id: str
    topic: str
    status: str
    complexity: str
    created_at: datetime
```

**Example Usage:**
```python
# Create session
response = httpx.post(
    "http://localhost:8000/api/sessions",
    json={
        "topic": "Introduction to FastAPI",
        "parameters": {
            "content_type": "blog_post",
            "tone": "professional",
            "word_count": 2000
        }
    }
)
session_id = response.json()["session_id"]

# Get session
session = httpx.get(f"http://localhost:8000/api/sessions/{session_id}").json()

# Get current content
content = httpx.get(f"http://localhost:8000/api/sessions/{session_id}/content").json()

# Delete session
httpx.delete(f"http://localhost:8000/api/sessions/{session_id}")
```

---

### 2. Research Router (`app/routers/research.py`)

**Purpose:** Multi-agent research process with SSE streaming

**Endpoints:**

| Method | Path | Description | Streaming |
|--------|------|-------------|-----------|
| POST | `/api/sessions/{id}/research` | Start research | ✅ SSE |
| GET | `/api/sessions/{id}/research` | Get research results | No |
| GET | `/api/sessions/{id}/research/synthesis` | Get synthesis | No |

**Key Features:**
- Real-time streaming of research progress via SSE
- Integration with LeadAgent orchestrator
- Parallel research subagent coordination
- Research aggregation from multiple sources
- Automatic complexity analysis

**SSE Event Flow:**
```
1. status → "Analyzing query complexity..."
2. complexity → "Classified as moderate complexity"
3. status → "Creating research plan..."
4. plan → Research tasks created
5. status → "Spawning parallel research agents..."
6. research_progress → Agent completion updates
7. status → "Synthesizing findings..."
8. complete → Final results
```

**SSE Event Types:**

```python
# Status update
{
  "event": "status",
  "data": {
    "phase": "analyzing",
    "message": "Analyzing query complexity..."
  }
}

# Complexity classification
{
  "event": "complexity",
  "data": {
    "complexity": "moderate",
    "message": "Classified as moderate complexity"
  }
}

# Research plan
{
  "event": "plan",
  "data": {
    "tasks": 3,
    "plan": {...},
    "message": "Created plan with 3 research tasks"
  }
}

# Progress update
{
  "event": "research_progress",
  "data": {
    "agents_completed": 2,
    "total_agents": 3,
    "message": "Completed 2 of 3 research tasks"
  }
}

# Completion
{
  "event": "complete",
  "data": {
    "status": "complete",
    "synthesis_preview": "...",
    "total_sources": 25,
    "message": "Research complete"
  }
}
```

**Example Usage:**
```python
# Start research with SSE streaming
with httpx.stream(
    'POST',
    f"http://localhost:8000/api/sessions/{session_id}/research",
    timeout=300.0
) as response:
    for line in response.iter_lines():
        if line.startswith('event: '):
            event_type = line.split(': ')[1]
        elif line.startswith('data: '):
            data = json.loads(line[6:])
            print(f"{event_type}: {data.get('message', '')}")

# Get research results
results = httpx.get(
    f"http://localhost:8000/api/sessions/{session_id}/research"
).json()

# Get synthesis
synthesis = httpx.get(
    f"http://localhost:8000/api/sessions/{session_id}/research/synthesis"
).json()
```

---

### 3. Generate Router (`app/routers/generate.py`)

**Purpose:** Content generation and iteration with SSE streaming

**Endpoints:**

| Method | Path | Description | Streaming |
|--------|------|-------------|-----------|
| POST | `/api/sessions/{id}/generate` | Generate content | ✅ SSE |
| POST | `/api/sessions/{id}/iterate` | Iterate with feedback | ✅ SSE |
| GET | `/api/sessions/{id}/versions/{v}` | Get specific version | No |

**Key Features:**
- Streaming content generation in real-time
- Outline-first approach (structure before content)
- Feedback-driven iteration
- Automatic additional research when needed
- Version tracking with feedback history

**SSE Event Flow (Generate):**
```
1. status → "Starting content generation..."
2. outline → Content structure
3. content_start → "Generating content..."
4. content → Streaming chunks
5. content → More chunks...
6. complete → Generation finished
```

**SSE Event Flow (Iterate):**
```
1. status → "Processing feedback..."
2. analysis → Feedback analysis results
3. status → "Gathering additional information..." (optional)
4. status → "Revising content..."
5. content_start → "Generating revised content..."
6. content → Streaming revised chunks
7. complete → Iteration finished
```

**Models:**
```python
class IterateRequest(BaseModel):
    feedback: str
```

**Example Usage:**
```python
# Generate content with streaming
content_chunks = []
with httpx.stream(
    'POST',
    f"http://localhost:8000/api/sessions/{session_id}/generate",
    timeout=300.0
) as response:
    for line in response.iter_lines():
        if line.startswith('event: content'):
            # Skip event line
            continue
        elif line.startswith('data: '):
            data = json.loads(line[6:])
            if 'chunk' in data:
                content_chunks.append(data['chunk'])
                print(data['chunk'], end='', flush=True)

# Iterate with feedback
with httpx.stream(
    'POST',
    f"http://localhost:8000/api/sessions/{session_id}/iterate",
    json={"feedback": "Add more code examples"},
    timeout=300.0
) as response:
    for line in response.iter_lines():
        if line.startswith('data: '):
            data = json.loads(line[6:])
            if 'chunk' in data:
                print(data['chunk'], end='', flush=True)

# Get specific version
version = httpx.get(
    f"http://localhost:8000/api/sessions/{session_id}/versions/1"
).json()
```

---

### 4. Publish Router (`app/routers/publish.py`)

**Purpose:** Content export and publishing to various platforms

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/sessions/{id}/publish/wordpress` | Publish to WordPress |
| POST | `/api/sessions/{id}/publish/html` | Export as HTML |
| GET | `/api/sessions/{id}/preview` | Preview HTML |
| GET | `/api/sessions/{id}/download` | Download HTML file |
| POST | `/api/sessions/{id}/verify-citations` | Verify all URLs |
| GET | `/api/sessions/{id}/markdown` | Download markdown |

**Key Features:**
- WordPress REST API integration
- HTML export with embedded CSS
- Citation/link verification
- Multiple export formats
- Browser preview and download

**Models:**
```python
class WordPressPublishRequest(BaseModel):
    site_url: str
    username: str
    app_password: str
    status: str = "draft"  # draft or publish
    categories: Optional[List[int]] = None
    tags: Optional[List[int]] = None
```

**Example Usage:**
```python
# Publish to WordPress
response = httpx.post(
    f"http://localhost:8000/api/sessions/{session_id}/publish/wordpress",
    json={
        "site_url": "https://example.com",
        "username": "admin",
        "app_password": "xxxx xxxx xxxx xxxx",
        "status": "draft",
        "categories": [1, 5],
        "tags": [10, 15]
    }
)
result = response.json()
print(f"Published: {result['url']}")

# Export to HTML
html_result = httpx.post(
    f"http://localhost:8000/api/sessions/{session_id}/publish/html"
).json()
with open(html_result['filename'], 'w') as f:
    f.write(html_result['html'])

# Verify citations
verification = httpx.post(
    f"http://localhost:8000/api/sessions/{session_id}/verify-citations"
).json()
print(f"Valid links: {verification['valid_count']}")
print(f"Invalid links: {verification['invalid_count']}")

# Download markdown
response = httpx.get(
    f"http://localhost:8000/api/sessions/{session_id}/markdown"
)
with open('content.md', 'wb') as f:
    f.write(response.content)
```

---

## Integration with Agents

Each router integrates seamlessly with the agent system:

### Sessions Router
- Creates `ContentSession` instances
- Persists sessions via `save_to_memory()`
- Restores sessions via `read_from_memory()`

### Research Router
- Instantiates `LeadAgent` orchestrator
- Calls `analyze_complexity()` for classification
- Executes `create_research_plan()` for task decomposition
- Runs `execute_research()` for parallel subagent coordination
- Generates `synthesize_findings()` for result aggregation

### Generate Router
- Instantiates `ContentGeneratorAgent` for initial generation
- Instantiates `IteratorAgent` for refinement
- Streams content via `generate_stream()` async generator
- Handles iteration via `iterate_stream()` async generator
- Manages version history automatically

### Publish Router
- Instantiates `PublisherAgent` for export/publish operations
- Calls `publish_to_wordpress()` for WP integration
- Executes `export_to_html()` for HTML generation
- Runs `verify_citations()` for link checking

---

## Error Handling

All routers implement comprehensive error handling:

### Common Errors

**404 Not Found**
```python
if session_id not in sessions:
    raise HTTPException(status_code=404, detail="Session not found")
```

**400 Bad Request (Invalid State)**
```python
if session.status != "ready_for_generation":
    raise HTTPException(
        status_code=400,
        detail=f"Cannot generate: session must have completed research first"
    )
```

**500 Server Error**
```python
try:
    result = await publisher.publish_to_wordpress(...)
except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Publishing failed: {str(e)}"
    )
```

---

## SSE Implementation Details

### Event Source Response

All streaming endpoints use `sse-starlette`:

```python
from sse_starlette.sse import EventSourceResponse

@router.post("/{session_id}/research")
async def start_research(session_id: str):
    return EventSourceResponse(research_event_generator(session))
```

### Event Generator Pattern

```python
async def research_event_generator(session: ContentSession) -> AsyncGenerator[dict, None]:
    # Yield status events
    yield {
        "event": "status",
        "data": json.dumps({
            "phase": "analyzing",
            "message": "Analyzing query complexity..."
        })
    }

    # Perform work
    result = await some_async_operation()

    # Yield results
    yield {
        "event": "complete",
        "data": json.dumps(result)
    }
```

### Client Implementation

**JavaScript:**
```javascript
const eventSource = new EventSource('/api/sessions/{id}/research');

eventSource.addEventListener('status', (e) => {
    const data = JSON.parse(e.data);
    console.log(data.message);
});

eventSource.addEventListener('complete', (e) => {
    eventSource.close();
});
```

**Python:**
```python
with httpx.stream('POST', url, timeout=300.0) as response:
    for line in response.iter_lines():
        if line.startswith('event: '):
            event_type = line.split(': ')[1]
        elif line.startswith('data: '):
            data = json.loads(line[6:])
            handle_event(event_type, data)
```

---

## Memory System Integration

All routers use the filesystem memory system for coordination:

### Save Operations
```python
from ..tools.memory import save_to_memory

# Save session
save_to_memory(session_id, "session", session.model_dump())

# Save research results
save_to_memory(session_id, f"research/agent_{id}", results)

# Save content version
save_to_memory(session_id, f"versions/v{version}", version_data)
```

### Read Operations
```python
from ..tools.memory import read_from_memory

# Load session
session_data = read_from_memory(session_id, "session")

# Load synthesis
synthesis = read_from_memory(session_id, "synthesis")

# Load specific version
version_data = read_from_memory(session_id, f"versions/v{num}")
```

### Aggregation
```python
from ..tools.memory import aggregate_research

# Aggregate all research findings
aggregated = aggregate_research(session_id)
sources = aggregated["sources"]
total = aggregated["total_sources"]
```

---

## Testing

### Unit Tests (`test_api.py`)

Run comprehensive test suite:
```bash
python test_api.py
```

Tests include:
1. Import validation
2. Router configuration
3. Model validation
4. Session endpoint models
5. SSE dependencies
6. Memory system

### Verification (`verify_api.py`)

Run pre-flight checks:
```bash
./verify_api.py
```

Verifies:
1. File structure
2. Python dependencies
3. App module imports
4. Router registration
5. Environment config
6. Memory directory

### Manual Testing

Use interactive API docs:
```
http://localhost:8000/docs
```

---

## Configuration

### Environment Variables (`.env`)

Required:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Optional:
```bash
FIRECRAWL_API_KEY=fc-your-key-here
WORDPRESS_SITE_URL=https://example.com
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

### Settings (`app/config.py`)

```python
from app.config import settings

# Access configuration
api_key = settings.anthropic_api_key
memory_path = settings.memory_base_path
debug = settings.debug
```

---

## Complete Workflow Example

```python
import httpx
import json

BASE_URL = "http://localhost:8000"

# 1. Create session
response = httpx.post(
    f"{BASE_URL}/api/sessions",
    json={"topic": "Introduction to FastAPI"}
)
session_id = response.json()["session_id"]

# 2. Start research (SSE)
with httpx.stream(
    'POST',
    f"{BASE_URL}/api/sessions/{session_id}/research",
    timeout=300.0
) as response:
    for line in response.iter_lines():
        if line.startswith('data: '):
            data = json.loads(line[6:])
            print(f"Research: {data.get('message', '')}")

# 3. Generate content (SSE)
with httpx.stream(
    'POST',
    f"{BASE_URL}/api/sessions/{session_id}/generate",
    timeout=300.0
) as response:
    for line in response.iter_lines():
        if line.startswith('data: '):
            data = json.loads(line[6:])
            if 'chunk' in data:
                print(data['chunk'], end='', flush=True)

# 4. Get final content
content = httpx.get(
    f"{BASE_URL}/api/sessions/{session_id}/content"
).json()

# 5. Export to HTML
html = httpx.post(
    f"{BASE_URL}/api/sessions/{session_id}/publish/html"
).json()
with open(html['filename'], 'w') as f:
    f.write(html['html'])

print(f"\nExported to {html['filename']}")
```

---

## Next Steps

1. **Run Tests**: `python test_api.py`
2. **Verify Setup**: `./verify_api.py`
3. **Start Server**: `./run.sh`
4. **Test Endpoints**: Visit http://localhost:8000/docs
5. **Read Full Docs**: See `API_DOCUMENTATION.md`

---

## Status

✅ **All routers complete and tested**
- Sessions: 6 endpoints
- Research: 3 endpoints (1 SSE)
- Generate: 3 endpoints (2 SSE)
- Publish: 6 endpoints
- **Total: 18 endpoints**

Ready for production use!
