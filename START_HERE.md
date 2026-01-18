# 🚀 Start Here - Content Creation Engine

Welcome to the Content Creation Engine! This guide will help you get started quickly.

## What is This?

A **multi-agent AI content creation system** that:
- Researches topics using parallel AI agents
- Generates high-quality content
- Refines content based on your feedback
- Publishes to WordPress or exports HTML

Built with Claude AI, following Anthropic's orchestrator-worker pattern.

## Quick Links

| I want to... | Go to... |
|--------------|----------|
| **Get started in 5 minutes** | [QUICKSTART.md](QUICKSTART.md) |
| **Understand the full system** | [README.md](README.md) |
| **Learn the architecture** | [ARCHITECTURE.md](ARCHITECTURE.md) |
| **Deploy to production** | [DEPLOYMENT.md](DEPLOYMENT.md) |
| **Contribute code** | [CONTRIBUTING.md](CONTRIBUTING.md) |
| **Find any documentation** | [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) |

## 5-Minute Quick Start

### 1. Get API Keys
- [Anthropic API Key](https://console.anthropic.com/) (required)
- [Firecrawl API Key](https://www.firecrawl.dev/) (required)

### 2. Start Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn app.main:app --reload
```

### 3. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Open Browser
Go to: http://localhost:5173

## What You Get

```
User Input
    ↓
Research (3-5 parallel AI agents search the web)
    ↓
Generate (AI creates content from research)
    ↓
Iterate (Optional: refine with feedback)
    ↓
Publish (WordPress or HTML export)
```

## Architecture Overview

```
React Frontend
    ↓ (Real-time streaming)
FastAPI Backend
    ↓
Multi-Agent System
├── Lead Agent (Orchestrator)
├── Research Agents (3-5 parallel workers)
├── Generator Agent
├── Iterator Agent
└── Publisher Agent
    ↓
Firecrawl API (Web research)
Anthropic API (Claude AI)
WordPress API (Publishing)
```

## Key Features

- **Parallel Research**: 3-5 AI agents research simultaneously
- **Real-time Streaming**: Watch content generate live
- **Iterative Refinement**: Improve content with feedback
- **Extended Thinking**: Claude uses extended thinking for complex tasks
- **Filesystem Memory**: Prevents information loss
- **WordPress Publishing**: Direct publishing support
- **HTML Export**: Standalone HTML files

## Project Structure

```
cce/
├── README.md              ← Full documentation
├── QUICKSTART.md          ← 5-minute setup guide
├── ARCHITECTURE.md        ← System design
├── DEPLOYMENT.md          ← Production deployment
├── CONTRIBUTING.md        ← Development guide
├── backend/               ← Python/FastAPI
│   ├── app/
│   │   ├── agents/        ← AI agents
│   │   ├── tools/         ← Firecrawl integration
│   │   ├── routers/       ← API endpoints
│   │   └── main.py        ← FastAPI app
│   └── requirements.txt
└── frontend/              ← React/Vite
    ├── src/
    │   ├── components/    ← React components
    │   └── api/           ← API client
    └── package.json
```

## Documentation Map

**Getting Started:**
- [START_HERE.md](START_HERE.md) ← You are here
- [QUICKSTART.md](QUICKSTART.md) - Get running fast
- [README.md](README.md) - Complete overview

**Deep Dives:**
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production setup
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development

**Reference:**
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) - All docs
- [API Docs](http://localhost:8000/docs) - Interactive API reference

## Technology Stack

**Backend:**
- Python 3.10+
- FastAPI
- Anthropic SDK (Claude)
- Firecrawl API

**Frontend:**
- React 18
- Vite
- Server-Sent Events (SSE)

## Use Cases

1. **Blog Posts**: Research and write engaging blog content
2. **Technical Guides**: Create comprehensive how-to guides
3. **Articles**: Write well-researched articles on any topic
4. **Documentation**: Generate technical documentation
5. **Marketing Content**: Create marketing materials with research

## Example Workflow

```bash
# 1. User inputs topic
"Write a guide about sustainable urban farming"

# 2. Research phase (30-120 seconds)
- Lead agent analyzes topic
- Spawns 3-5 research agents
- Agents search web in parallel
- Findings synthesized

# 3. Generation phase (60-180 seconds)
- Generator reads research
- Creates structured content
- Streams to frontend in real-time

# 4. Iteration (optional, 30-90 seconds)
- User provides feedback
- Iterator refines content
- Repeat as needed

# 5. Publish
- Export HTML or publish to WordPress
```

## Requirements

**Minimum:**
- Python 3.10+
- Node.js 18+
- 4GB RAM
- Internet connection

**Recommended:**
- Python 3.11+
- Node.js 20+
- 8GB RAM
- Fast internet

## Support

- **Documentation**: See [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- **API Reference**: http://localhost:8000/docs
- **Issues**: Open a GitHub issue
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## Next Steps

Choose your path:

**👤 New User**
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Set up and run the system
3. Create your first content
4. Explore features

**👨‍💻 Developer**
1. Read [README.md](README.md)
2. Study [ARCHITECTURE.md](ARCHITECTURE.md)
3. Review [CONTRIBUTING.md](CONTRIBUTING.md)
4. Start contributing

**🚀 DevOps**
1. Read [README.md](README.md)
2. Follow [DEPLOYMENT.md](DEPLOYMENT.md)
3. Deploy to production
4. Set up monitoring

## License

MIT License - See [LICENSE](LICENSE)

## Acknowledgments

Built following [Anthropic's Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) architecture.

---

**Ready to start?** → [QUICKSTART.md](QUICKSTART.md)

**Want full details?** → [README.md](README.md)

**Need specific docs?** → [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
