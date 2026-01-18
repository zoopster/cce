# Content Creation Engine - Backend

Multi-agent content creation system following Anthropic's orchestrator-worker pattern.

## Setup

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

4. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the API:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py           # Configuration and settings
│   ├── main.py             # FastAPI application
│   ├── models/             # Pydantic models
│   │   ├── __init__.py
│   │   ├── parameters.py   # Generation parameters
│   │   └── content.py      # Content session models
│   ├── agents/             # Agent implementations
│   │   ├── __init__.py
│   │   └── base.py         # Base agent with memory
│   └── memory/             # Session data storage
│       └── .gitkeep
├── requirements.txt
├── .env.example
└── README.md
```

## Models

### GenerationParameters
- `content_type`: Type of content (blog_post, technical_tutorial, marketing_content)
- `tone`: Voice tone (professional, casual, technical, friendly)
- `audience_level`: Target audience (beginner, intermediate, expert, general)
- `word_count`: Target length (500-5000 words)
- `keywords`: SEO keywords
- `custom_instructions`: Additional guidance

### ContentSession
- `session_id`: Unique session identifier
- `topic`: Content topic
- `parameters`: Generation parameters
- `status`: Current workflow status
- `complexity`: Agent allocation strategy (simple, moderate, complex)
- `research_plan`: Research strategy
- `research_results`: Gathered findings
- `versions`: Content iterations
- `agents`: Active agent states

## Next Steps

Phase 2 will implement:
- Lead Orchestrator Agent
- Research Worker Agents
- Content Generator Agent
- API endpoints for session management
- Server-Sent Events for real-time updates
