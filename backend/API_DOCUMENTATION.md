# Content Creation Engine - API Documentation

Complete REST API with Server-Sent Events (SSE) streaming for real-time content creation.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Quick Start](#quick-start)
- [Session Management](#session-management)
- [Research Endpoints](#research-endpoints)
- [Content Generation](#content-generation)
- [Publishing](#publishing)
- [SSE Event Streams](#sse-event-streams)
- [Error Handling](#error-handling)

---

## Architecture Overview

The API is built with FastAPI and follows a multi-agent orchestration pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Sessions   │  │   Research   │  │   Generate   │      │
│  │    Router    │  │    Router    │  │    Router    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │              │
│         │    ┌────────────┴──────────────────┴────┐         │
│         │    │                                     │         │
│         └────┤          Agent Layer                │         │
│              │  • Lead (Orchestrator)              │         │
│              │  • Research Subagents (Workers)     │         │
│              │  • Content Generator                │         │
│              │  • Iterator                         │         │
│              │  • Publisher                        │         │
│              └─────────────┬───────────────────────┘         │
│                            │                                 │
│                   ┌────────┴────────┐                        │
│                   │  Memory System  │                        │
│                   │  (Filesystem)   │                        │
│                   └─────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Core Concepts

- **Sessions**: Isolated workspaces for content creation workflows
- **Streaming**: Real-time updates via Server-Sent Events (SSE)
- **Memory**: Filesystem-based agent coordination
- **Agents**: Specialized workers for different tasks

---

## Quick Start

### 1. Installation

```bash
cd /Users/johnpugh/Documents/source/cce/backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Basic Workflow

```bash
# 1. Create a session
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"topic": "Introduction to FastAPI"}'

# 2. Start research (SSE stream)
curl -N http://localhost:8000/api/sessions/{session_id}/research \
  -X POST

# 3. Generate content (SSE stream)
curl -N http://localhost:8000/api/sessions/{session_id}/generate \
  -X POST

# 4. Get the content
curl http://localhost:8000/api/sessions/{session_id}/content
```

---

## Session Management

### Create Session

Create a new content creation session.

**Endpoint:** `POST /api/sessions`

**Request Body:**
```json
{
  "topic": "How to build REST APIs with FastAPI",
  "parameters": {
    "content_type": "blog_post",
    "tone": "professional",
    "audience_level": "intermediate",
    "word_count": 2000,
    "keywords": ["fastapi", "python", "api"],
    "custom_instructions": "Include code examples"
  }
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "topic": "How to build REST APIs with FastAPI",
  "status": "created",
  "complexity": "moderate",
  "created_at": "2024-01-17T10:30:00Z"
}
```

**Parameters:**
- `content_type`: `blog_post` | `technical_tutorial` | `marketing_content`
- `tone`: `professional` | `casual` | `technical` | `friendly`
- `audience_level`: `beginner` | `intermediate` | `expert` | `general`
- `word_count`: 500-5000 (default: 1500)

---

### Get Session

Get complete session details including metadata, agents, and versions.

**Endpoint:** `GET /api/sessions/{session_id}`

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "topic": "How to build REST APIs with FastAPI",
  "status": "ready_for_review",
  "complexity": "moderate",
  "parameters": { ... },
  "research_results_count": 25,
  "versions_count": 2,
  "agents": [
    {
      "agent_id": "lead",
      "agent_type": "lead",
      "status": "complete",
      "current_task": "research synthesis",
      "tool_calls": 8,
      "findings_count": 25
    }
  ],
  "created_at": "2024-01-17T10:30:00Z",
  "updated_at": "2024-01-17T10:35:00Z"
}
```

---

### Get Agent States

Get real-time status of all agents in a session.

**Endpoint:** `GET /api/sessions/{session_id}/agents`

**Response:**
```json
[
  {
    "agent_id": "research_001",
    "agent_type": "research",
    "status": "executing",
    "current_task": "Searching for FastAPI documentation",
    "tool_calls": 3,
    "findings_count": 8
  },
  {
    "agent_id": "research_002",
    "agent_type": "research",
    "status": "complete",
    "current_task": "Analyzing Python web frameworks",
    "tool_calls": 5,
    "findings_count": 12
  }
]
```

---

### Get Versions

List all content versions for a session.

**Endpoint:** `GET /api/sessions/{session_id}/versions`

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "versions": [
    {
      "version_number": 1,
      "generated_at": "2024-01-17T10:35:00Z",
      "feedback_applied": null,
      "content_preview": "# Introduction to FastAPI\n\nFastAPI is a modern..."
    },
    {
      "version_number": 2,
      "generated_at": "2024-01-17T10:40:00Z",
      "feedback_applied": "Add more code examples",
      "content_preview": "# Introduction to FastAPI\n\nFastAPI is a modern..."
    }
  ]
}
```

---

### Get Current Content

Get the latest content version.

**Endpoint:** `GET /api/sessions/{session_id}/content`

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "version_number": 2,
  "content": "# Introduction to FastAPI\n\n...",
  "generated_at": "2024-01-17T10:40:00Z",
  "feedback_applied": "Add more code examples"
}
```

---

### Delete Session

Delete a session and all associated memory.

**Endpoint:** `DELETE /api/sessions/{session_id}`

**Response:**
```json
{
  "status": "deleted",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Research Endpoints

### Start Research (SSE Stream)

Start the multi-agent research process with real-time streaming updates.

**Endpoint:** `POST /api/sessions/{session_id}/research`

**Response:** Server-Sent Events stream

**Event Types:**

1. **status** - Phase updates
```json
{
  "event": "status",
  "data": {
    "phase": "analyzing",
    "message": "Analyzing query complexity..."
  }
}
```

2. **complexity** - Complexity classification
```json
{
  "event": "complexity",
  "data": {
    "complexity": "moderate",
    "message": "Classified as moderate complexity"
  }
}
```

3. **plan** - Research plan created
```json
{
  "event": "plan",
  "data": {
    "tasks": 3,
    "plan": {
      "tasks": [
        {
          "focus": "FastAPI fundamentals and features",
          "queries": ["FastAPI documentation", "FastAPI vs Flask"]
        }
      ]
    },
    "message": "Created plan with 3 research tasks"
  }
}
```

4. **research_progress** - Agent completion updates
```json
{
  "event": "research_progress",
  "data": {
    "agents_completed": 2,
    "total_agents": 3,
    "message": "Completed 2 of 3 research tasks"
  }
}
```

5. **complete** - Research finished
```json
{
  "event": "complete",
  "data": {
    "status": "complete",
    "synthesis_preview": "Based on comprehensive research...",
    "total_sources": 25,
    "message": "Research complete and ready for content generation"
  }
}
```

**Status Flow:**
```
analyzing → planning → researching → synthesizing → complete
```

---

### Get Research Results

Get aggregated research data from all subagents.

**Endpoint:** `GET /api/sessions/{session_id}/research`

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_sources": 25,
  "sources": [
    {
      "url": "https://fastapi.tiangolo.com/",
      "title": "FastAPI Documentation",
      "snippet": "FastAPI is a modern, fast web framework...",
      "agent_id": "research_001"
    }
  ],
  "findings_count": 15,
  "has_synthesis": true
}
```

---

### Get Research Synthesis

Get the lead agent's synthesis of all research findings.

**Endpoint:** `GET /api/sessions/{session_id}/research/synthesis`

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "synthesis": "Based on comprehensive research across 25 sources...",
  "source_count": 25,
  "created_at": "2024-01-17T10:35:00Z"
}
```

---

## Content Generation

### Generate Content (SSE Stream)

Generate content from research findings with real-time streaming.

**Endpoint:** `POST /api/sessions/{session_id}/generate`

**Prerequisites:** Research must be completed first

**Response:** Server-Sent Events stream

**Event Types:**

1. **status** - Generation started
```json
{
  "event": "status",
  "data": {
    "phase": "generating",
    "message": "Starting content generation..."
  }
}
```

2. **outline** - Content structure created
```json
{
  "event": "outline",
  "data": {
    "content": "1. Introduction\n2. What is FastAPI?...",
    "message": "Content outline created"
  }
}
```

3. **content_start** - Content generation begins
```json
{
  "event": "content_start",
  "data": {
    "message": "Generating content..."
  }
}
```

4. **content** - Streaming content chunks
```json
{
  "event": "content",
  "data": {
    "chunk": "# Introduction to FastAPI\n\n"
  }
}
```

5. **complete** - Generation finished
```json
{
  "event": "complete",
  "data": {
    "status": "complete",
    "version": 1,
    "message": "Content generation complete"
  }
}
```

---

### Iterate on Content (SSE Stream)

Refine content based on user feedback with optional additional research.

**Endpoint:** `POST /api/sessions/{session_id}/iterate`

**Request Body:**
```json
{
  "feedback": "Add more practical code examples and expand the routing section"
}
```

**Response:** Server-Sent Events stream

**Event Types:**

1. **status** - Processing feedback
```json
{
  "event": "status",
  "data": {
    "phase": "iterating",
    "message": "Processing feedback..."
  }
}
```

2. **analysis** - Feedback analysis
```json
{
  "event": "analysis",
  "data": {
    "content": "User wants more code examples and routing details...",
    "message": "Feedback analyzed"
  }
}
```

3. **status** - Additional research (if needed)
```json
{
  "event": "status",
  "data": {
    "phase": "researching",
    "message": "Gathering additional information..."
  }
}
```

4. **content** - Streaming revised content
```json
{
  "event": "content",
  "data": {
    "chunk": "## FastAPI Routing Examples\n\n"
  }
}
```

5. **complete** - Iteration finished
```json
{
  "event": "complete",
  "data": {
    "status": "complete",
    "version": 2,
    "message": "Content iteration complete"
  }
}
```

---

### Get Specific Version

Retrieve a specific content version by number.

**Endpoint:** `GET /api/sessions/{session_id}/versions/{version_number}`

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "version_number": 2,
  "content": "# Introduction to FastAPI\n\n...",
  "generated_at": "2024-01-17T10:40:00Z",
  "feedback_applied": "Add more code examples"
}
```

---

## Publishing

### Publish to WordPress

Publish content directly to a WordPress site via REST API.

**Endpoint:** `POST /api/sessions/{session_id}/publish/wordpress`

**Request Body:**
```json
{
  "site_url": "https://example.com",
  "username": "admin",
  "app_password": "xxxx xxxx xxxx xxxx",
  "status": "draft",
  "categories": [1, 5],
  "tags": [10, 15, 20]
}
```

**Response:**
```json
{
  "status": "success",
  "post_id": 42,
  "url": "https://example.com/introduction-to-fastapi",
  "edit_url": "https://example.com/wp-admin/post.php?post=42&action=edit",
  "published_status": "draft"
}
```

**Notes:**
- Requires WordPress with REST API enabled
- Use Application Passwords (not regular password)
- `status` can be `draft` or `publish`

---

### Export to HTML

Export content as styled HTML document.

**Endpoint:** `POST /api/sessions/{session_id}/publish/html`

**Response:**
```json
{
  "status": "success",
  "filename": "introduction-to-fastapi.html",
  "title": "Introduction to FastAPI",
  "html": "<!DOCTYPE html>\n<html>...",
  "exported_at": "2024-01-17T10:45:00Z"
}
```

---

### Preview HTML

Preview content as rendered HTML in browser.

**Endpoint:** `GET /api/sessions/{session_id}/preview`

**Response:** HTML page (text/html)

Opens directly in browser with full styling.

---

### Download HTML

Download content as HTML file.

**Endpoint:** `GET /api/sessions/{session_id}/download`

**Response:** HTML file download with Content-Disposition header

Browser automatically downloads the file.

---

### Get Markdown

Download raw markdown content.

**Endpoint:** `GET /api/sessions/{session_id}/markdown`

**Response:** Markdown file download (text/markdown)

---

### Verify Citations

Check all URLs in the content for validity and accessibility.

**Endpoint:** `POST /api/sessions/{session_id}/verify-citations`

**Response:**
```json
{
  "status": "complete",
  "total_links": 15,
  "valid_count": 14,
  "invalid_count": 1,
  "valid_links": [
    {
      "url": "https://fastapi.tiangolo.com/",
      "status_code": 200,
      "title": "FastAPI"
    }
  ],
  "invalid_links": [
    {
      "url": "https://broken-link.com",
      "error": "Connection timeout",
      "status_code": null
    }
  ],
  "checked_at": "2024-01-17T10:45:00Z"
}
```

---

## SSE Event Streams

### Client Implementation

#### JavaScript/Browser

```javascript
const eventSource = new EventSource(
  'http://localhost:8000/api/sessions/{session_id}/research',
  { method: 'POST' }
);

eventSource.addEventListener('status', (e) => {
  const data = JSON.parse(e.data);
  console.log('Status:', data.message);
});

eventSource.addEventListener('complete', (e) => {
  const data = JSON.parse(e.data);
  console.log('Complete:', data);
  eventSource.close();
});

eventSource.onerror = (error) => {
  console.error('SSE error:', error);
  eventSource.close();
};
```

#### Python

```python
import httpx

with httpx.stream(
    'POST',
    'http://localhost:8000/api/sessions/{session_id}/research',
    timeout=300.0
) as response:
    for line in response.iter_lines():
        if line.startswith('data: '):
            data = json.loads(line[6:])
            print(f"Event: {data}")
```

#### cURL

```bash
curl -N -X POST http://localhost:8000/api/sessions/{session_id}/research
```

---

## Error Handling

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid input or state)
- `404` - Not Found (session or resource doesn't exist)
- `500` - Server Error (unexpected error during processing)

### Error Response Format

```json
{
  "detail": "Cannot start research: session is in ready_for_review state"
}
```

### Common Errors

**Session Not Found**
```json
{
  "detail": "Session not found"
}
```

**Invalid State Transition**
```json
{
  "detail": "Cannot generate: session must have completed research first (current status: created)"
}
```

**No Content Available**
```json
{
  "detail": "No content to publish"
}
```

**Publishing Failed**
```json
{
  "detail": "Publishing failed: Authentication failed"
}
```

---

## Complete Workflow Example

### Python Client

```python
import httpx
import json

BASE_URL = "http://localhost:8000"

# 1. Create session
response = httpx.post(
    f"{BASE_URL}/api/sessions",
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
print(f"Created session: {session_id}")

# 2. Research with streaming
with httpx.stream(
    'POST',
    f"{BASE_URL}/api/sessions/{session_id}/research",
    timeout=300.0
) as response:
    for line in response.iter_lines():
        if line.startswith('data: '):
            data = json.loads(line[6:])
            print(f"Research: {data.get('message', '')}")

# 3. Generate content with streaming
content_chunks = []
with httpx.stream(
    'POST',
    f"{BASE_URL}/api/sessions/{session_id}/generate",
    timeout=300.0
) as response:
    for line in response.iter_lines():
        if line.startswith('event: content'):
            # Next line has the data
            continue
        if line.startswith('data: '):
            data = json.loads(line[6:])
            if 'chunk' in data:
                content_chunks.append(data['chunk'])

# 4. Get final content
response = httpx.get(f"{BASE_URL}/api/sessions/{session_id}/content")
content = response.json()
print(f"Generated {len(content['content'])} characters")

# 5. Export to HTML
response = httpx.post(f"{BASE_URL}/api/sessions/{session_id}/publish/html")
html = response.json()
with open(html['filename'], 'w') as f:
    f.write(html['html'])
print(f"Exported to {html['filename']}")
```

---

## Development

### Run Tests

```bash
cd /Users/johnpugh/Documents/source/cce/backend
python test_api.py
```

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

### Project Structure

```
backend/
├── app/
│   ├── routers/           # API endpoints
│   │   ├── __init__.py
│   │   ├── sessions.py    # Session CRUD
│   │   ├── research.py    # Research with SSE
│   │   ├── generate.py    # Content generation with SSE
│   │   └── publish.py     # Publishing endpoints
│   ├── agents/            # Agent implementations
│   ├── models/            # Pydantic models
│   ├── tools/             # Shared utilities
│   ├── config.py          # Configuration
│   └── main.py            # FastAPI app
├── requirements.txt
├── test_api.py
└── API_DOCUMENTATION.md
```

---

## Next Steps

1. **Frontend Integration**: Build a React/Vue app that consumes these APIs
2. **Authentication**: Add JWT authentication for production
3. **Database**: Replace in-memory sessions with PostgreSQL
4. **Rate Limiting**: Add rate limiting for API endpoints
5. **Caching**: Cache research results and generated content
6. **WebSockets**: Consider WebSocket alternative to SSE for bidirectional communication
7. **Monitoring**: Add logging, metrics, and error tracking

---

## Support

For issues or questions:
- Check the interactive API docs at `/docs`
- Review agent implementation in `app/agents/`
- Check memory system in `app/tools/memory.py`
