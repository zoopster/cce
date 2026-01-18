# Content Creation Engine (CCE)

A multi-agent content creation system built with Claude, following [Anthropic's orchestrator-worker pattern](https://www.anthropic.com/engineering/multi-agent-research-system).

## Overview

The Content Creation Engine is an intelligent, multi-agent system that automates the entire content creation workflow from research to publication. It leverages Claude's capabilities through a coordinated team of specialized agents that work together to produce high-quality content.

## Features

- **Multi-Agent Research**: Parallel research subagents gather information simultaneously from the web
- **Intelligent Content Generation**: Claude generates high-quality, well-structured content from research findings
- **Iterative Refinement**: Provide feedback to improve content through multiple iterations
- **Real-time Streaming**: Watch the content creation process unfold in real-time via Server-Sent Events (SSE)
- **Multiple Publishing Options**: Publish directly to WordPress or download as HTML
- **Extended Thinking**: Agents use Claude's extended thinking capabilities for complex analysis
- **Filesystem Memory**: Agents write findings to filesystem to prevent information loss

## Architecture

```
User Request
      ↓
┌─────────────────────────────────────────────┐
│         React Frontend (Vite)               │
│  - Topic Input & Parameters                 │
│  - Real-time Agent Status Display           │
│  - Content Editor & Preview                 │
│  - Publishing Controls                      │
└──────────────────┬──────────────────────────┘
                   │ SSE/HTTP
                   ↓
┌─────────────────────────────────────────────┐
│       FastAPI Backend (Python)              │
│  - Session Management                       │
│  - SSE Streaming Endpoints                  │
│  - Agent Orchestration                      │
└──────────────────┬──────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────┐
│        Multi-Agent System                   │
│                                             │
│  Lead Agent (Orchestrator)                 │
│         ↓                                   │
│    ┌────┴────┐                             │
│    ↓    ↓    ↓                             │
│   [R1] [R2] [R3]  Research Subagents       │
│    │    │    │    (Parallel Execution)     │
│    └────┬────┘                             │
│         ↓                                   │
│  Generator Agent (Content Creation)        │
│         ↓                                   │
│  Iterator Agent (Refinement)               │
│         ↓                                   │
│  Publisher Agent (WordPress/HTML)          │
└─────────────────────────────────────────────┘
         ↓              ↓
    Firecrawl API   Filesystem Memory
```

## Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Anthropic API key** ([Get one here](https://console.anthropic.com/))
- **Firecrawl API key** ([Get one here](https://www.firecrawl.dev/)) - for web research
- **WordPress credentials** (optional) - for WordPress publishing

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your API keys (see Configuration section below)

# Run the development server
uvicorn app.main:app --reload
```

The backend will start at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will start at `http://localhost:5173`

### Access the Application

- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## Usage

### Basic Workflow

1. **Enter Topic**: Describe what you want to write about
   - Example: "Write a guide about sustainable urban farming techniques"

2. **Configure Parameters**: Set content preferences
   - Content Type: blog_post, article, guide, tutorial, etc.
   - Tone: professional, casual, technical, friendly
   - Audience Level: beginner, intermediate, advanced, expert, general
   - Word Count: Target length (500-5000 words)
   - Keywords: SEO keywords to include
   - Custom Instructions: Specific requirements or guidelines

3. **Research Phase**: Watch parallel agents gather information
   - Lead agent analyzes topic complexity
   - Spawns 3-5 research subagents
   - Each subagent searches and scrapes web content
   - Findings are written to filesystem memory
   - Synthesis of all research is generated

4. **Generate Content**: Content streams in real-time
   - Generator agent reads research findings
   - Uses extended thinking for complex content
   - Streams content as it's being created
   - Structured with proper headings and sections

5. **Iterate (Optional)**: Provide feedback to refine
   - Review generated content
   - Provide specific feedback
   - Iterator agent refines based on your input
   - Repeat as needed

6. **Publish**: Choose your publishing method
   - **WordPress**: Publish directly to your WordPress site
   - **HTML Export**: Download as standalone HTML file
   - **Preview**: View formatted content before publishing

## Project Structure

```
cce/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── agents/            # Agent implementations
│   │   │   ├── base.py        # Base agent class
│   │   │   ├── lead.py        # Lead orchestrator agent
│   │   │   ├── research.py    # Research subagent
│   │   │   ├── generator.py   # Content generator agent
│   │   │   ├── iterator.py    # Content refinement agent
│   │   │   └── publisher.py   # Publishing agent
│   │   ├── tools/             # Agent tools
│   │   │   ├── search.py      # Firecrawl web search
│   │   │   ├── scrape.py      # Firecrawl web scraping
│   │   │   └── memory.py      # Filesystem memory operations
│   │   ├── routers/           # FastAPI route handlers
│   │   │   ├── sessions.py    # Session management
│   │   │   ├── research.py    # Research endpoints
│   │   │   ├── generate.py    # Content generation endpoints
│   │   │   └── publish.py     # Publishing endpoints
│   │   ├── models/            # Pydantic data models
│   │   │   ├── content.py     # Content models
│   │   │   └── parameters.py  # Parameter models
│   │   ├── config.py          # Configuration management
│   │   ├── main.py            # FastAPI application
│   │   └── memory/            # Runtime memory storage
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment variables template
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── TopicInput.jsx         # Topic entry
│   │   │   ├── ParameterPanel.jsx     # Parameter configuration
│   │   │   ├── AgentStatusPanel.jsx   # Agent status display
│   │   │   ├── ResearchPanel.jsx      # Research results
│   │   │   ├── ContentEditor.jsx      # Content editing
│   │   │   ├── FeedbackPanel.jsx      # Feedback input
│   │   │   └── PublishPanel.jsx       # Publishing controls
│   │   ├── api/
│   │   │   └── client.js      # API client with SSE support
│   │   ├── styles/
│   │   │   └── app.css        # Application styles
│   │   ├── App.jsx            # Main application component
│   │   └── index.jsx          # Application entry point
│   ├── package.json           # Node dependencies
│   ├── vite.config.js         # Vite configuration
│   └── index.html             # HTML template
└── README.md                   # This file
```

## Multi-Agent System

The Content Creation Engine implements Anthropic's recommended orchestrator-worker pattern for multi-agent systems.

### Agent Roles

| Agent | Type | Role | Key Features |
|-------|------|------|--------------|
| **Lead Agent** | Orchestrator | Analyzes topic complexity, spawns research subagents, coordinates workflow | - Plans research strategy<br>- Spawns 3-5 parallel subagents<br>- Synthesizes research findings |
| **Research Subagent** | Worker | Searches web, scrapes content, writes findings to filesystem | - Parallel execution<br>- Web search via Firecrawl<br>- Content scraping<br>- Filesystem memory |
| **Generator Agent** | Worker | Creates initial content from research | - Extended thinking<br>- Structured content<br>- Real-time streaming |
| **Iterator Agent** | Worker | Refines content based on user feedback | - Feedback analysis<br>- Targeted improvements<br>- Version management |
| **Publisher Agent** | Worker | Handles WordPress publishing and HTML export | - WordPress REST API<br>- HTML generation<br>- Citation verification |

### Key Design Principles

Based on [Anthropic's multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system):

1. **Orchestrator-Worker Pattern**
   - Lead agent orchestrates, research subagents execute in parallel
   - Clear separation of coordination and execution

2. **Filesystem Memory**
   - Agents write findings to files instead of passing through orchestrator
   - Prevents "telephone game" information loss
   - Each agent reads directly from filesystem memory

3. **Start Wide, Then Narrow**
   - Initial research spans broad areas
   - Subsequent research focuses on gaps and specific needs

4. **Parallel Execution**
   - 3-5 research subagents run simultaneously
   - Significantly faster than sequential research

5. **Extended Thinking**
   - Agents use Claude's extended thinking for complex analysis
   - Better reasoning about research strategies and content structure

## API Endpoints

### Session Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions` | Create new content session |
| GET | `/api/sessions/{id}` | Get session details |
| DELETE | `/api/sessions/{id}` | Delete session |
| GET | `/api/sessions/{id}/agents` | Get agent execution history |
| GET | `/api/sessions/{id}/versions` | List content versions |
| GET | `/api/sessions/{id}/content` | Get current content |

### Research

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions/{id}/research` | Start research (SSE stream) |
| GET | `/api/sessions/{id}/research` | Get research results |
| GET | `/api/sessions/{id}/research/synthesis` | Get research synthesis |

### Content Generation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions/{id}/generate` | Generate content (SSE stream) |
| POST | `/api/sessions/{id}/iterate` | Iterate with feedback (SSE stream) |
| GET | `/api/sessions/{id}/versions/{version}` | Get specific version |

### Publishing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions/{id}/publish/wordpress` | Publish to WordPress |
| POST | `/api/sessions/{id}/publish/html` | Export as HTML |
| GET | `/api/sessions/{id}/preview` | Preview HTML |
| GET | `/api/sessions/{id}/download` | Download HTML file |
| POST | `/api/sessions/{id}/verify-citations` | Verify citations |
| GET | `/api/sessions/{id}/markdown` | Get markdown content |

### Server-Sent Events (SSE)

Research, generation, and iteration endpoints stream events:

```javascript
// Event types
{
  "event": "status",        // Agent status update
  "event": "content",       // Content chunk
  "event": "complete",      // Operation complete
  "event": "error"          // Error occurred
}
```

## Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Required - Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# Required - Firecrawl for web research
FIRECRAWL_API_KEY=fc-...

# Optional - WordPress Publishing
WORDPRESS_SITE_URL=https://your-site.com
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=xxxx-xxxx-xxxx

# Optional - Application Settings
APP_NAME=Content Creation Engine
DEBUG=false
MEMORY_BASE_PATH=app/memory
```

### Getting API Keys

**Anthropic API Key:**
1. Visit https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key

**Firecrawl API Key:**
1. Visit https://www.firecrawl.dev/
2. Sign up for an account
3. Get your API key from the dashboard

**WordPress App Password:**
1. Log in to your WordPress admin panel
2. Go to Users → Profile
3. Scroll to "Application Passwords"
4. Create a new application password
5. Use your WordPress username and the generated password

## Technology Stack

### Backend
- **Python 3.10+**: Core language
- **FastAPI**: Modern web framework with automatic OpenAPI docs
- **Anthropic SDK**: Claude AI integration
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation and settings management
- **SSE-Starlette**: Server-Sent Events support
- **aiofiles**: Async file operations
- **httpx**: HTTP client for API calls
- **python-dotenv**: Environment variable management

### Frontend
- **React 18**: UI library
- **Vite**: Fast build tool and dev server
- **React Markdown**: Markdown rendering
- **Native Fetch API**: HTTP requests with SSE support

### External Services
- **Anthropic Claude**: AI model for all agents
- **Firecrawl**: Web search and content scraping
- **WordPress REST API**: Publishing integration

## Development

### Running Tests

```bash
# Backend tests
cd backend
python test_api.py           # Test API endpoints
python test_agents.py        # Test agent execution
python verify_api.py         # Verify API configuration

# Frontend
cd frontend
npm run build                # Build for production
npm run preview              # Preview production build
```

### Project Scripts

Backend helper scripts are available in `/backend`:
- `run.sh`: Quick start script for development
- `setup_and_run.sh`: Complete setup and run
- `test_*.py`: Various test scripts

Frontend helper scripts are available in `/frontend`:
- `start.sh`: Quick start script

### Memory Management

The system maintains filesystem memory at `backend/app/memory/`:
- Each session gets a unique directory
- Research findings stored as markdown files
- Content versions tracked separately
- Memory cleaned up on session deletion

## Deployment

### Production Considerations

1. **Environment Variables**: Use secure environment variable management
2. **CORS**: Configure `allow_origins` in `main.py` for specific domains
3. **HTTPS**: Use reverse proxy (nginx, Caddy) with SSL certificates
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **Monitoring**: Add logging and monitoring for agent execution
6. **Error Handling**: Configure error tracking (Sentry, etc.)

### Docker Deployment (Optional)

You can containerize both backend and frontend for easier deployment. Example Dockerfile structure:

```dockerfile
# Backend Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Frontend Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json .
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]
```

## Troubleshooting

### Common Issues

**"Module not found" errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**CORS errors in frontend**
- Check that backend is running on port 8000
- Verify CORS configuration in `main.py`

**API key errors**
- Verify `.env` file exists in backend directory
- Check that API keys are properly formatted
- Ensure no spaces or quotes around keys

**Research failing**
- Verify Firecrawl API key is valid
- Check internet connectivity
- Review Firecrawl API rate limits

**WordPress publishing fails**
- Verify WordPress URL is correct (include https://)
- Ensure application password is properly generated
- Check WordPress REST API is enabled

**SSE connection drops**
- This is normal for long-running operations
- Frontend will show completion status
- Check server logs for actual errors

## Performance

- **Research Phase**: 30-120 seconds (depends on topic complexity)
- **Content Generation**: 60-180 seconds (depends on length and complexity)
- **Iteration**: 30-90 seconds
- **Parallel Research**: 3-5 subagents run simultaneously
- **Streaming**: Real-time content chunks via SSE

## Limitations

- Maximum word count: 5000 words (configurable)
- Research subagents: 3-5 parallel maximum
- Firecrawl rate limits apply
- Content versions stored in memory (cleared on session deletion)
- WordPress publishing requires REST API access

## Roadmap

Potential future enhancements:
- [ ] Database persistence for sessions and content
- [ ] User authentication and multi-user support
- [ ] Advanced citation and fact-checking
- [ ] More publishing destinations (Medium, Ghost, etc.)
- [ ] Image generation integration
- [ ] SEO analysis and optimization
- [ ] Content templates and presets
- [ ] Collaborative editing features
- [ ] Analytics and performance metrics

## Contributing

This is a demonstration project built following Anthropic's best practices. Contributions, issues, and feature requests are welcome.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built following [Anthropic's Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) architecture
- Inspired by Anthropic's Building Effective Agents guide
- Uses [Firecrawl](https://www.firecrawl.dev/) for web research capabilities
- Powered by [Claude](https://www.anthropic.com/claude) AI models

## Support

For questions or issues:
1. Check the `/docs` endpoint for API documentation
2. Review agent execution logs in console
3. Examine session memory files for debugging
4. Consult Anthropic's documentation for Claude capabilities

## Version

Current Version: **1.0.0**

Built with Claude Sonnet 4.5
