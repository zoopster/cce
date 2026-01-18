# Content Creation Engine - API Quick Start

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.11+
- Anthropic API key

### 1. Install & Configure (1 minute)

```bash
cd /Users/johnpugh/Documents/source/cce/backend

# Install dependencies
pip install -r requirements.txt

# Set API key
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

### 2. Start the Server (30 seconds)

```bash
uvicorn app.main:app --reload
```

Server starts at: `http://localhost:8000`

### 3. View Interactive Docs (30 seconds)

Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. Test the API (3 minutes)

#### Option A: Python Test Client
```bash
python test_client.py
```

This runs a complete workflow automatically!

#### Option B: Web UI
```bash
open frontend_example.html
```

Follow the UI to create content step-by-step.

#### Option C: Manual cURL
```bash
# Create session
SESSION_ID=$(curl -s -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "How to build a REST API",
    "parameters": {"content_type": "technical_tutorial", "word_count": 1000}
  }' | jq -r '.session_id')

echo "Session ID: $SESSION_ID"

# Start research (SSE stream)
curl -N http://localhost:8000/api/sessions/$SESSION_ID/research

# Generate content (SSE stream)
curl -N http://localhost:8000/api/sessions/$SESSION_ID/generate

# Get final content
curl http://localhost:8000/api/sessions/$SESSION_ID/content | jq -r '.content'

# Download as HTML
curl -o content.html http://localhost:8000/api/sessions/$SESSION_ID/download
```

## 📖 Complete Workflow Example

### JavaScript (Browser)

```javascript
// 1. Create session
const response = await fetch('http://localhost:8000/api/sessions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    topic: 'Introduction to FastAPI',
    parameters: {
      content_type: 'technical_tutorial',
      word_count: 1500
    }
  })
});
const { session_id } = await response.json();

// 2. Research with SSE
const researchEvents = new EventSource(
  `http://localhost:8000/api/sessions/${session_id}/research`
);

researchEvents.addEventListener('complete', (e) => {
  console.log('Research complete!', JSON.parse(e.data));
  researchEvents.close();

  // 3. Generate content
  startGeneration(session_id);
});

function startGeneration(sessionId) {
  const genEvents = new EventSource(
    `http://localhost:8000/api/sessions/${sessionId}/generate`
  );

  let content = '';

  genEvents.addEventListener('content', (e) => {
    const { chunk } = JSON.parse(e.data);
    content += chunk;
    document.getElementById('preview').textContent = content;
  });

  genEvents.addEventListener('complete', (e) => {
    console.log('Generation complete!');
    genEvents.close();
  });
}
```

### Python (Async)

```python
import httpx
import asyncio
import json

async def create_content():
    base_url = "http://localhost:8000"

    # 1. Create session
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/api/sessions",
            json={
                "topic": "Python Best Practices",
                "parameters": {
                    "content_type": "technical_tutorial",
                    "word_count": 1500
                }
            }
        )
        session_id = response.json()["session_id"]
        print(f"Session: {session_id}")

    # 2. Research
    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream(
            "POST",
            f"{base_url}/api/sessions/{session_id}/research",
            headers={"Accept": "text/event-stream"}
        ) as stream:
            async for line in stream.aiter_lines():
                if line.startswith("data:"):
                    print(line)

    # 3. Generate
    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream(
            "POST",
            f"{base_url}/api/sessions/{session_id}/generate",
            headers={"Accept": "text/event-stream"}
        ) as stream:
            async for line in stream.aiter_lines():
                if line.startswith("event: content"):
                    # Print content chunks
                    pass

    # 4. Get final content
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/api/sessions/{session_id}/content"
        )
        content = response.json()["content"]
        print(content)

asyncio.run(create_content())
```

## 🎯 Common Use Cases

### 1. Blog Post Generation
```json
POST /api/sessions
{
  "topic": "10 Tips for Remote Work Productivity",
  "parameters": {
    "content_type": "blog_post",
    "tone": "friendly",
    "audience_level": "general",
    "word_count": 1200
  }
}
```

### 2. Technical Tutorial
```json
POST /api/sessions
{
  "topic": "Building a REST API with FastAPI",
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

### 3. Marketing Content
```json
POST /api/sessions
{
  "topic": "Why Choose Our SaaS Platform",
  "parameters": {
    "content_type": "marketing_content",
    "tone": "professional",
    "audience_level": "general",
    "word_count": 800
  }
}
```

### 4. Iterate with Feedback
```json
POST /api/sessions/{session_id}/iterate
{
  "feedback": "Add more code examples and explain authentication in detail"
}
```

### 5. Publish to WordPress
```json
POST /api/sessions/{session_id}/publish/wordpress
{
  "site_url": "https://myblog.com",
  "username": "admin",
  "app_password": "xxxx xxxx xxxx xxxx",
  "status": "draft",
  "categories": [1, 5],
  "tags": [2, 7]
}
```

## 📊 API Endpoints Reference

### Sessions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions` | Create session |
| GET | `/api/sessions/{id}` | Get session details |
| DELETE | `/api/sessions/{id}` | Delete session |
| GET | `/api/sessions/{id}/content` | Get current content |
| GET | `/api/sessions/{id}/versions` | List versions |

### Research (SSE)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions/{id}/research` | Start research (stream) |
| GET | `/api/sessions/{id}/research` | Get research results |
| GET | `/api/sessions/{id}/research/synthesis` | Get synthesis |

### Generation (SSE)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions/{id}/generate` | Generate content (stream) |
| POST | `/api/sessions/{id}/iterate` | Iterate with feedback (stream) |
| GET | `/api/sessions/{id}/versions/{n}` | Get version N |

### Publishing
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions/{id}/publish/wordpress` | Publish to WordPress |
| POST | `/api/sessions/{id}/publish/html` | Export HTML |
| GET | `/api/sessions/{id}/preview` | Preview HTML |
| GET | `/api/sessions/{id}/download` | Download HTML |
| GET | `/api/sessions/{id}/markdown` | Download Markdown |
| POST | `/api/sessions/{id}/verify-citations` | Verify links |

## 🔧 Configuration

### Environment Variables
```env
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional
MEMORY_BASE_PATH=app/memory
```

### Content Parameters
```python
{
  "content_type": "blog_post" | "technical_tutorial" | "marketing_content",
  "tone": "professional" | "casual" | "technical" | "friendly",
  "audience_level": "beginner" | "intermediate" | "expert" | "general",
  "word_count": 500-5000,  # Default: 1500
  "keywords": ["optional", "keywords"],
  "custom_instructions": "Optional special instructions"
}
```

## 🐛 Troubleshooting

### Server won't start
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Check API key
grep ANTHROPIC_API_KEY .env

# Check port availability
lsof -i :8000
```

### SSE not working
```javascript
// Ensure proper headers
const eventSource = new EventSource(url, {
  headers: {
    'Accept': 'text/event-stream'
  }
});
```

### CORS errors
```python
# In app/main.py, update:
allow_origins=["http://localhost:3000"]  # Your frontend URL
```

## 📚 Documentation

- **API Reference**: [API.md](API.md) - Complete API documentation
- **Developer Guide**: [README_API.md](README_API.md) - Setup and deployment
- **Implementation Details**: [API_LAYER_COMPLETE.md](API_LAYER_COMPLETE.md) - Architecture

## 🎉 Next Steps

1. **Explore the API**: Use Swagger UI at `/docs`
2. **Run Examples**: Try `test_client.py` and `frontend_example.html`
3. **Build Frontend**: Create a React/Vue app using the API
4. **Customize**: Modify agents for your specific use case
5. **Deploy**: Follow production deployment guide in README_API.md

## 💡 Tips

1. **Session Management**: Always delete sessions when done
2. **SSE Connections**: Close EventSource when complete
3. **Iteration**: Be specific with feedback for better results
4. **WordPress**: Use Application Passwords, not regular passwords
5. **Performance**: Lower word count for faster generation

## 🚦 Quick Health Check

```bash
# Check if server is running
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","service":"content-creation-engine"}
```

## 📞 Support

For issues:
1. Check [API.md](API.md) for endpoint details
2. Review error messages in response
3. Check session state: `GET /api/sessions/{id}`
4. Verify API key is valid

---

**Ready to create content?** Start with the test client:
```bash
python test_client.py
```

Happy creating! 🚀
