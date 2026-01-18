# Content Creation Engine - API Documentation

## Overview

The Content Creation Engine provides a RESTful API with Server-Sent Events (SSE) streaming for real-time content creation. The API follows a session-based workflow where each content creation task has its own isolated session.

**Base URL**: `http://localhost:8000`

**Interactive Docs**:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Architecture

The API is built with FastAPI and uses SSE (Server-Sent Events) for streaming real-time updates during long-running operations like research and content generation.

### Key Features

- **Session Management**: Isolated sessions for concurrent content creation
- **SSE Streaming**: Real-time progress updates for research, generation, and iteration
- **Multi-Agent System**: Orchestrated research and content generation
- **Version Control**: Track multiple content iterations with feedback
- **Multi-Platform Publishing**: WordPress, HTML export, and markdown download
- **Citation Verification**: Automatic link checking

## Workflow

```
1. Create Session → 2. Research (SSE) → 3. Generate (SSE) → 4. Review → 5. Iterate (SSE) → 6. Publish
```

## Authentication

Currently no authentication required. For production:
- Add API key authentication
- Implement rate limiting
- Add user-based session isolation

## Endpoints

### Session Management

#### Create Session
```http
POST /api/sessions
Content-Type: application/json

{
  "topic": "How to build a REST API with FastAPI",
  "parameters": {
    "content_type": "technical_tutorial",
    "tone": "technical",
    "audience_level": "intermediate",
    "word_count": 2000,
    "keywords": ["fastapi", "python", "api design"],
    "custom_instructions": "Include code examples and best practices"
  }
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "topic": "How to build a REST API with FastAPI",
  "status": "created",
  "complexity": "moderate",
  "created_at": "2025-01-17T12:00:00Z"
}
```

#### Get Session
```http
GET /api/sessions/{session_id}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "topic": "How to build a REST API with FastAPI",
  "status": "ready_for_review",
  "complexity": "moderate",
  "parameters": { ... },
  "research_results_count": 15,
  "versions_count": 2,
  "agents": [
    {
      "agent_id": "lead",
      "agent_type": "lead",
      "status": "complete",
      "current_task": "research complete",
      "tool_calls": 5,
      "findings_count": 3
    }
  ],
  "created_at": "2025-01-17T12:00:00Z",
  "updated_at": "2025-01-17T12:05:00Z"
}
```

#### Get Agent States
```http
GET /api/sessions/{session_id}/agents
```

Returns real-time status of all agents for UI progress display.

#### Delete Session
```http
DELETE /api/sessions/{session_id}
```

Deletes session and all associated memory (irreversible).

---

### Research

#### Start Research (SSE)
```http
POST /api/sessions/{session_id}/research
Accept: text/event-stream
```

**SSE Event Stream:**

```
event: status
data: {"phase": "analyzing", "message": "Analyzing query complexity..."}

event: complexity
data: {"complexity": "moderate", "message": "Classified as moderate complexity"}

event: status
data: {"phase": "planning", "message": "Creating research plan..."}

event: plan
data: {"tasks": 3, "plan": {...}, "message": "Created plan with 3 research tasks"}

event: status
data: {"phase": "researching", "message": "Spawning 3 parallel research agents..."}

event: research_progress
data: {"agents_completed": 3, "total_agents": 3, "message": "Completed 3 of 3 research tasks"}

event: status
data: {"phase": "synthesizing", "message": "Synthesizing findings from all agents..."}

event: complete
data: {"status": "complete", "synthesis_preview": "...", "total_sources": 15, "message": "Research complete"}
```

**Client Example (JavaScript):**
```javascript
const eventSource = new EventSource(`/api/sessions/${sessionId}/research`);

eventSource.addEventListener('status', (e) => {
  const data = JSON.parse(e.data);
  console.log(`Phase: ${data.phase} - ${data.message}`);
});

eventSource.addEventListener('complete', (e) => {
  const data = JSON.parse(e.data);
  console.log('Research complete!', data);
  eventSource.close();
});

eventSource.onerror = (error) => {
  console.error('SSE Error:', error);
  eventSource.close();
};
```

#### Get Research Results
```http
GET /api/sessions/{session_id}/research
```

Returns aggregated research findings from all subagents.

#### Get Research Synthesis
```http
GET /api/sessions/{session_id}/research/synthesis
```

Returns the lead agent's synthesized research summary.

---

### Content Generation

#### Generate Content (SSE)
```http
POST /api/sessions/{session_id}/generate
Accept: text/event-stream
```

**SSE Event Stream:**

```
event: status
data: {"phase": "generating", "message": "Starting content generation..."}

event: outline
data: {"content": "# Title\n## Section 1\n...", "message": "Content outline created"}

event: content_start
data: {"message": "Generating content..."}

event: content
data: {"chunk": "# How to Build"}

event: content
data: {"chunk": " a REST API"}

event: content
data: {"chunk": " with FastAPI\n\n"}

...

event: complete
data: {"status": "complete", "version": 1, "message": "Content generation complete"}
```

**Client Example (JavaScript):**
```javascript
const eventSource = new EventSource(`/api/sessions/${sessionId}/generate`);
let fullContent = '';

eventSource.addEventListener('outline', (e) => {
  const data = JSON.parse(e.data);
  displayOutline(data.content);
});

eventSource.addEventListener('content', (e) => {
  const data = JSON.parse(e.data);
  fullContent += data.chunk;
  updateContentDisplay(fullContent);
});

eventSource.addEventListener('complete', (e) => {
  console.log('Generation complete!');
  eventSource.close();
});
```

#### Iterate Content (SSE)
```http
POST /api/sessions/{session_id}/iterate
Content-Type: application/json
Accept: text/event-stream

{
  "feedback": "Add more code examples and explain authentication"
}
```

**SSE Event Stream:**

```
event: status
data: {"phase": "iterating", "message": "Processing feedback..."}

event: analysis
data: {"content": "User wants more code examples...", "message": "Feedback analyzed"}

event: status (optional)
data: {"phase": "researching", "message": "Gathering additional information..."}

event: content_start
data: {"message": "Generating revised content..."}

event: content
data: {"chunk": "..."}

event: complete
data: {"status": "complete", "version": 2, "message": "Content iteration complete"}
```

#### Get Current Content
```http
GET /api/sessions/{session_id}/content
```

Returns the latest content version.

#### Get Specific Version
```http
GET /api/sessions/{session_id}/versions/{version_number}
```

Returns a specific content version.

#### List Versions
```http
GET /api/sessions/{session_id}/versions
```

Returns metadata for all versions.

---

### Publishing

#### Publish to WordPress
```http
POST /api/sessions/{session_id}/publish/wordpress
Content-Type: application/json

{
  "site_url": "https://example.com",
  "username": "admin",
  "app_password": "xxxx xxxx xxxx xxxx",
  "status": "draft",
  "categories": [1, 5],
  "tags": [2, 7, 9]
}
```

**Response:**
```json
{
  "status": "success",
  "post_id": 123,
  "url": "https://example.com/2025/01/how-to-build-rest-api",
  "edit_url": "https://example.com/wp-admin/post.php?post=123&action=edit",
  "published_status": "draft"
}
```

**Note:** Requires WordPress Application Password (not regular password).

#### Export HTML
```http
POST /api/sessions/{session_id}/publish/html
```

Returns HTML with embedded styles for download.

#### Preview HTML
```http
GET /api/sessions/{session_id}/preview
```

Returns rendered HTML page for browser preview.

#### Download HTML
```http
GET /api/sessions/{session_id}/download
```

Downloads HTML file with proper Content-Disposition header.

#### Download Markdown
```http
GET /api/sessions/{session_id}/markdown
```

Downloads raw markdown file.

#### Verify Citations
```http
POST /api/sessions/{session_id}/verify-citations
```

**Response:**
```json
{
  "status": "complete",
  "total_links": 15,
  "valid_count": 14,
  "invalid_count": 1,
  "valid_links": [...],
  "invalid_links": [
    {
      "text": "Broken Link",
      "url": "https://example.com/404",
      "status": 404
    }
  ],
  "checked_at": "2025-01-17T12:10:00Z"
}
```

---

## Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

Currently no rate limiting. Recommended for production:
- 100 requests/minute per IP
- 10 concurrent sessions per user
- SSE connection timeout: 10 minutes

## Content Type Parameters

### content_type
- `blog_post`: General blog content
- `technical_tutorial`: Technical how-to content
- `marketing_content`: Marketing/promotional content

### tone
- `professional`: Formal, business-appropriate
- `casual`: Conversational, friendly
- `technical`: Technical, precise
- `friendly`: Warm, approachable

### audience_level
- `beginner`: No prior knowledge assumed
- `intermediate`: Some familiarity expected
- `expert`: Advanced, technical audience
- `general`: Mixed audience

## Session States

- `created`: Session initialized
- `researching`: Research in progress
- `ready_for_generation`: Research complete, ready to generate
- `generating`: Content generation in progress
- `ready_for_review`: Content generated, ready for review
- `iterating`: Applying feedback and regenerating
- `published`: Content published to a platform

## Best Practices

1. **Session Management**: Delete sessions when done to free memory
2. **SSE Connections**: Always close EventSource connections
3. **Error Handling**: Handle SSE errors and implement reconnection logic
4. **Version Control**: Keep important versions before iterating
5. **Citation Verification**: Run before publishing to external platforms
6. **Feedback**: Be specific with iteration feedback for better results

## Example: Complete Workflow

```python
import requests
import json

# 1. Create session
response = requests.post('http://localhost:8000/api/sessions', json={
    'topic': 'Introduction to Machine Learning',
    'parameters': {
        'content_type': 'technical_tutorial',
        'word_count': 1500
    }
})
session_id = response.json()['session_id']

# 2. Start research (SSE - use appropriate client)
# See JavaScript examples above

# 3. Generate content (SSE)
# ...

# 4. Get content
response = requests.get(f'http://localhost:8000/api/sessions/{session_id}/content')
content = response.json()['content']

# 5. Iterate with feedback
# POST to /api/sessions/{session_id}/iterate with feedback

# 6. Publish to WordPress
response = requests.post(
    f'http://localhost:8000/api/sessions/{session_id}/publish/wordpress',
    json={
        'site_url': 'https://myblog.com',
        'username': 'admin',
        'app_password': 'xxxx xxxx xxxx xxxx',
        'status': 'draft'
    }
)
print(f"Published: {response.json()['url']}")

# 7. Clean up
requests.delete(f'http://localhost:8000/api/sessions/{session_id}')
```

## Support

For issues and questions:
- Check `/docs` for interactive API testing
- Review error responses for details
- Check session status before operations
