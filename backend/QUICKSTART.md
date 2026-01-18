# Content Creation Engine - Quick Start Guide

Get the FastAPI backend running in under 5 minutes.

## Prerequisites

- Python 3.9 or higher
- Anthropic API key (get one at https://console.anthropic.com/)
- Optional: Firecrawl API key for enhanced web scraping

## Installation

### 1. Navigate to Backend Directory

```bash
cd /Users/johnpugh/Documents/source/cce/backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **FastAPI** - Modern web framework
- **Anthropic** - Claude API client
- **SSE-Starlette** - Server-Sent Events for streaming
- **Pydantic** - Data validation
- **HTTPX** - Async HTTP client
- And more...

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use your preferred editor
```

Required in `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Optional:
```bash
FIRECRAWL_API_KEY=fc-your-key-here
WORDPRESS_SITE_URL=https://your-site.com
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

### 5. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 6. Verify Installation

Open your browser to:
- **API Root**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Or run the test suite:
```bash
python test_api.py
```

Expected output:
```
======================================================================
Content Creation Engine - API Layer Test Suite
======================================================================
✓ Imports
✓ Router Configuration
✓ Model Validation
✓ Session Endpoints
✓ SSE Dependencies
✓ Memory System
======================================================================
Result: 6/6 tests passed
======================================================================
```

## Your First Request

### Using cURL

```bash
# Create a session
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Introduction to FastAPI",
    "parameters": {
      "content_type": "blog_post",
      "tone": "professional",
      "word_count": 1500
    }
  }'
```

Response:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "topic": "Introduction to FastAPI",
  "status": "created",
  "complexity": "moderate",
  "created_at": "2024-01-17T10:30:00Z"
}
```

### Using Python

```python
import httpx

# Create session
response = httpx.post(
    "http://localhost:8000/api/sessions",
    json={
        "topic": "Introduction to FastAPI",
        "parameters": {
            "content_type": "blog_post",
            "tone": "professional",
            "word_count": 1500
        }
    }
)

session = response.json()
session_id = session["session_id"]
print(f"Created session: {session_id}")
```

### Using the Interactive Docs

1. Go to http://localhost:8000/docs
2. Click on `POST /api/sessions`
3. Click "Try it out"
4. Edit the request body
5. Click "Execute"

## Complete Workflow

### 1. Create Session
```bash
SESSION_ID=$(curl -s -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"topic": "Introduction to FastAPI"}' | jq -r '.session_id')

echo "Session ID: $SESSION_ID"
```

### 2. Run Research (SSE Stream)
```bash
curl -N -X POST "http://localhost:8000/api/sessions/$SESSION_ID/research"
```

You'll see real-time streaming events:
```
event: status
data: {"phase":"analyzing","message":"Analyzing query complexity..."}

event: complexity
data: {"complexity":"moderate","message":"Classified as moderate complexity"}

event: plan
data: {"tasks":3,"plan":{...},"message":"Created plan with 3 research tasks"}

event: complete
data: {"status":"complete","total_sources":25,"message":"Research complete"}
```

### 3. Generate Content (SSE Stream)
```bash
curl -N -X POST "http://localhost:8000/api/sessions/$SESSION_ID/generate"
```

Streams content in real-time:
```
event: outline
data: {"content":"1. Introduction\n2. What is FastAPI?..."}

event: content
data: {"chunk":"# Introduction to FastAPI\n\n"}

event: content
data: {"chunk":"FastAPI is a modern, fast web framework..."}

event: complete
data: {"status":"complete","version":1,"message":"Content generation complete"}
```

### 4. Get Generated Content
```bash
curl "http://localhost:8000/api/sessions/$SESSION_ID/content" | jq '.content'
```

### 5. Export to HTML
```bash
curl -X POST "http://localhost:8000/api/sessions/$SESSION_ID/publish/html" \
  | jq -r '.html' > output.html

open output.html  # macOS
# or
xdg-open output.html  # Linux
```

## Project Structure

```
backend/
├── app/
│   ├── routers/              # API endpoints
│   │   ├── __init__.py      # Router exports
│   │   ├── sessions.py      # Session CRUD
│   │   ├── research.py      # Research with SSE
│   │   ├── generate.py      # Content gen with SSE
│   │   └── publish.py       # Publishing endpoints
│   ├── agents/              # Agent implementations
│   │   ├── base.py          # Base agent class
│   │   ├── lead.py          # Lead orchestrator
│   │   ├── research.py      # Research subagents
│   │   ├── generator.py     # Content generator
│   │   ├── iterator.py      # Content iterator
│   │   └── publisher.py     # Publishing agent
│   ├── models/              # Pydantic models
│   │   ├── content.py       # Session/content models
│   │   └── parameters.py    # Generation params
│   ├── tools/               # Shared utilities
│   │   ├── memory.py        # Filesystem memory
│   │   ├── search.py        # Web search
│   │   └── scrape.py        # Web scraping
│   ├── config.py            # Configuration
│   └── main.py              # FastAPI app
├── requirements.txt         # Python dependencies
├── test_api.py             # API test suite
├── QUICKSTART.md           # This file
└── API_DOCUMENTATION.md    # Complete API docs
```

## Key Features

### Server-Sent Events (SSE)
Real-time streaming for:
- Research progress
- Content generation
- Content iteration

### Multi-Agent System
- **Lead Agent**: Orchestrates research
- **Research Subagents**: Parallel workers
- **Generator Agent**: Creates content
- **Iterator Agent**: Refines based on feedback
- **Publisher Agent**: Exports and publishes

### Filesystem Memory
- Session-isolated storage
- Agent coordination
- Research aggregation

## Common Issues

### ModuleNotFoundError
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### API Key Missing
```bash
# Check .env file exists
ls -la .env

# Verify ANTHROPIC_API_KEY is set
grep ANTHROPIC_API_KEY .env
```

### Port Already in Use
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

### Memory Directory Permissions
```bash
# Ensure memory directory is writable
mkdir -p app/memory
chmod 755 app/memory
```

## Development Mode

### Auto-Reload
```bash
# Server automatically reloads on file changes
uvicorn app.main:app --reload
```

### Debug Mode
```bash
# Set DEBUG=True in .env
echo "DEBUG=true" >> .env
```

### View Logs
```bash
# Uvicorn logs show all requests
uvicorn app.main:app --reload --log-level debug
```

## Next Steps

1. **Read API Documentation**: See `API_DOCUMENTATION.md` for complete endpoint reference
2. **Explore Agents**: Check `app/agents/` to understand the multi-agent system
3. **Test Endpoints**: Use the interactive docs at http://localhost:8000/docs
4. **Build a Frontend**: Connect a React/Vue app to these APIs
5. **Customize Agents**: Modify agent behavior in `app/agents/`

## Testing

### Run Test Suite
```bash
python test_api.py
```

### Test Specific Endpoint
```bash
# Test health check
curl http://localhost:8000/health

# Test session creation
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"topic": "Test Topic"}'
```

### Manual Testing with Interactive Docs
1. Go to http://localhost:8000/docs
2. Try each endpoint
3. View request/response schemas
4. See validation errors in real-time

## Production Deployment

### Environment Variables
```bash
# Production .env
ANTHROPIC_API_KEY=sk-ant-production-key
DEBUG=false
```

### Run with Gunicorn
```bash
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker (Coming Soon)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Support

- **API Docs**: http://localhost:8000/docs
- **Complete API Reference**: `API_DOCUMENTATION.md`
- **Agent Documentation**: `app/agents/*.py`
- **Tool Reference**: `app/tools/README.md`

## License

See LICENSE file in project root.
