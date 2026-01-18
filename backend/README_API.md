# Content Creation Engine - API Layer

## Overview

This is the FastAPI-based API layer for the Content Creation Engine, a multi-agent system for automated content creation using Anthropic's Claude.

## Features

- **RESTful API**: Clean, well-documented endpoints
- **SSE Streaming**: Real-time progress updates for long-running operations
- **Session-based**: Isolated sessions for concurrent content creation
- **Multi-Agent Orchestration**: Coordinated research and content generation
- **Version Control**: Track content iterations with feedback
- **Multi-Platform Publishing**: WordPress, HTML, and Markdown export
- **Citation Verification**: Automatic link validation

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create `.env` file:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

### 3. Start the Server

```bash
uvicorn app.main:app --reload
```

Server will start at `http://localhost:8000`

### 4. View API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Structure

```
backend/app/
├── main.py              # FastAPI application
├── config.py            # Configuration
├── routers/             # API endpoints
│   ├── __init__.py
│   ├── sessions.py      # Session management
│   ├── research.py      # Research endpoints (SSE)
│   ├── generate.py      # Content generation (SSE)
│   └── publish.py       # Publishing endpoints
├── agents/              # Agent implementations
│   ├── lead.py         # Orchestrator agent
│   ├── research.py     # Research subagent
│   ├── generator.py    # Content generator
│   ├── iterator.py     # Iteration handler
│   └── publisher.py    # Publishing agent
├── models/              # Pydantic models
│   ├── content.py      # Session and content models
│   └── parameters.py   # Generation parameters
└── tools/               # Utility functions
    └── memory.py       # Filesystem memory
```

## Workflow

```
1. POST /api/sessions
   ↓
2. POST /api/sessions/{id}/research (SSE)
   ↓
3. POST /api/sessions/{id}/generate (SSE)
   ↓
4. GET /api/sessions/{id}/content
   ↓
5. POST /api/sessions/{id}/iterate (SSE) [Optional]
   ↓
6. POST /api/sessions/{id}/publish/* [WordPress/HTML]
```

## API Endpoints

### Sessions
- `POST /api/sessions` - Create new session
- `GET /api/sessions/{id}` - Get session details
- `DELETE /api/sessions/{id}` - Delete session
- `GET /api/sessions/{id}/agents` - Get agent states
- `GET /api/sessions/{id}/versions` - List versions
- `GET /api/sessions/{id}/content` - Get current content

### Research (SSE)
- `POST /api/sessions/{id}/research` - Start research (streaming)
- `GET /api/sessions/{id}/research` - Get research results
- `GET /api/sessions/{id}/research/synthesis` - Get synthesis

### Generation (SSE)
- `POST /api/sessions/{id}/generate` - Generate content (streaming)
- `POST /api/sessions/{id}/iterate` - Iterate with feedback (streaming)
- `GET /api/sessions/{id}/versions/{num}` - Get specific version

### Publishing
- `POST /api/sessions/{id}/publish/wordpress` - Publish to WordPress
- `POST /api/sessions/{id}/publish/html` - Export as HTML
- `GET /api/sessions/{id}/preview` - Preview HTML
- `GET /api/sessions/{id}/download` - Download HTML
- `GET /api/sessions/{id}/markdown` - Download Markdown
- `POST /api/sessions/{id}/verify-citations` - Verify links

## Testing

### Using the Test Client

```bash
python test_client.py
```

This runs a complete workflow demonstration.

### Using the Frontend Example

1. Start the server
2. Open `frontend_example.html` in a browser
3. Follow the UI to create a session and generate content

### Using cURL

```bash
# Create session
SESSION_ID=$(curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"topic": "FastAPI Tutorial", "parameters": {"content_type": "technical_tutorial"}}' \
  | jq -r '.session_id')

# Start research (SSE)
curl -N http://localhost:8000/api/sessions/$SESSION_ID/research

# Generate content (SSE)
curl -N http://localhost:8000/api/sessions/$SESSION_ID/generate

# Get content
curl http://localhost:8000/api/sessions/$SESSION_ID/content | jq -r '.content'
```

## SSE (Server-Sent Events)

The API uses SSE for streaming real-time updates during:
- Research (complexity analysis, planning, execution, synthesis)
- Content generation (outline, streaming content)
- Content iteration (feedback analysis, revision)

### SSE Event Types

**Research:**
- `status` - Phase updates
- `complexity` - Complexity classification
- `plan` - Research plan
- `research_progress` - Agent progress
- `complete` - Final results

**Generation:**
- `status` - Phase updates
- `outline` - Content structure
- `content_start` - Begin streaming
- `content` - Content chunks
- `complete` - Generation done

**Iteration:**
- `status` - Phase updates
- `analysis` - Feedback analysis
- `content_start` - Begin revision
- `content` - Revised chunks
- `complete` - Iteration done

### JavaScript SSE Client Example

```javascript
const eventSource = new EventSource(`/api/sessions/${sessionId}/research`);

eventSource.addEventListener('status', (e) => {
  const data = JSON.parse(e.data);
  console.log(`[${data.phase}] ${data.message}`);
});

eventSource.addEventListener('complete', (e) => {
  const data = JSON.parse(e.data);
  console.log('Complete!', data);
  eventSource.close();
});

eventSource.onerror = (error) => {
  console.error('Error:', error);
  eventSource.close();
};
```

### Python SSE Client Example

```python
import httpx
import json

async with httpx.AsyncClient(timeout=300.0) as client:
    async with client.stream(
        "POST",
        f"http://localhost:8000/api/sessions/{session_id}/research",
        headers={"Accept": "text/event-stream"}
    ) as response:
        async for line in response.aiter_lines():
            if line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                data = json.loads(line.split(":", 1)[1].strip())
                print(f"{event_type}: {data}")
```

## Configuration

### Environment Variables

- `ANTHROPIC_API_KEY` - Required, your Anthropic API key
- `MEMORY_BASE_PATH` - Optional, default: `app/memory`

### Content Parameters

When creating a session:

```json
{
  "topic": "Your topic here",
  "parameters": {
    "content_type": "blog_post|technical_tutorial|marketing_content",
    "tone": "professional|casual|technical|friendly",
    "audience_level": "beginner|intermediate|expert|general",
    "word_count": 1500,
    "keywords": ["optional", "keywords"],
    "custom_instructions": "Any special instructions"
  }
}
```

## Session States

- `created` - Initial state
- `researching` - Research in progress
- `ready_for_generation` - Research complete
- `generating` - Content generation in progress
- `ready_for_review` - Content generated
- `iterating` - Applying feedback
- `published` - Published to platform

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error responses:

```json
{
  "detail": "Error message"
}
```

## WordPress Publishing

To publish to WordPress:

1. Install WordPress
2. Create Application Password:
   - Users → Profile → Application Passwords
   - Generate new password
3. Use the credentials:

```bash
curl -X POST http://localhost:8000/api/sessions/$SESSION_ID/publish/wordpress \
  -H "Content-Type: application/json" \
  -d '{
    "site_url": "https://yoursite.com",
    "username": "admin",
    "app_password": "xxxx xxxx xxxx xxxx",
    "status": "draft"
  }'
```

## Memory Management

Sessions store data in filesystem memory:

```
app/memory/{session_id}/
├── session.json
├── plan.json
├── research/
│   ├── agent_1.json
│   ├── agent_2.json
│   └── agent_3.json
├── synthesis.json
├── outline.json
└── versions/
    ├── v1.json
    ├── v2.json
    └── v3.json
```

Clean up sessions when done:

```bash
DELETE /api/sessions/{session_id}
```

## Performance

- Research: 30-90 seconds (complexity dependent)
- Generation: 20-60 seconds (length dependent)
- Iteration: 15-45 seconds

Optimize by:
- Using appropriate complexity levels
- Limiting word count
- Cleaning up unused sessions

## Production Deployment

For production:

1. **Add Authentication**
   ```python
   from fastapi.security import HTTPBearer
   ```

2. **Configure CORS**
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

3. **Add Rate Limiting**
   ```python
   from slowapi import Limiter
   ```

4. **Use Redis for Sessions**
   Replace in-memory dict with Redis

5. **Add Logging**
   ```python
   import logging
   ```

6. **Use Production ASGI Server**
   ```bash
   gunicorn -k uvicorn.workers.UvicornWorker app.main:app
   ```

## Troubleshooting

### Server won't start
- Check `ANTHROPIC_API_KEY` is set
- Verify dependencies installed
- Check port 8000 is available

### SSE not working
- Ensure `Accept: text/event-stream` header
- Check CORS settings
- Verify browser supports SSE

### Memory issues
- Clean up old sessions regularly
- Monitor `app/memory/` directory size
- Implement session timeout

## License

MIT

## Support

For issues:
1. Check `/docs` for endpoint details
2. Review error responses
3. Check session state before operations
4. Verify ANTHROPIC_API_KEY is valid

## Additional Resources

- [API Documentation](API.md) - Complete API reference
- [Frontend Example](frontend_example.html) - Web UI example
- [Test Client](test_client.py) - Python test client
- FastAPI Docs: https://fastapi.tiangolo.com/
- Anthropic API: https://docs.anthropic.com/
