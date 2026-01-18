# Documentation Index

Complete guide to all documentation for the Content Creation Engine.

## Quick Navigation

| Document | Purpose | Audience |
|----------|---------|----------|
| [README.md](README.md) | Project overview and setup | Everyone |
| [QUICKSTART.md](QUICKSTART.md) | 5-minute getting started guide | New users |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design and architecture | Developers |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment guide | DevOps/SysAdmins |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines | Contributors |
| [CHANGELOG.md](CHANGELOG.md) | Version history and changes | Everyone |
| [LICENSE](LICENSE) | MIT License | Everyone |

## Documentation by Purpose

### Getting Started

**New to the project?** Start here:

1. [QUICKSTART.md](QUICKSTART.md) - Get up and running in 5 minutes
   - Prerequisites check
   - API key setup
   - Backend setup
   - Frontend setup
   - First content creation
   - Troubleshooting

2. [README.md](README.md) - Complete project overview
   - Features and capabilities
   - Architecture overview
   - Full setup instructions
   - Usage guide
   - API reference
   - Configuration details

### Understanding the System

**Want to understand how it works?**

1. [ARCHITECTURE.md](ARCHITECTURE.md) - Deep dive into system design
   - Design principles
   - Multi-agent system explained
   - Component architecture
   - Data flow diagrams
   - Technology decisions
   - Scalability considerations

2. [README.md - Multi-Agent System](README.md#multi-agent-system) - Agent overview
   - Lead Agent (Orchestrator)
   - Research Subagents (Workers)
   - Generator Agent
   - Iterator Agent
   - Publisher Agent

### Deploying to Production

**Ready to deploy?**

1. [DEPLOYMENT.md](DEPLOYMENT.md) - Complete deployment guide
   - Server setup
   - Environment configuration
   - Backend deployment with systemd
   - Frontend deployment
   - Nginx/Caddy reverse proxy
   - SSL certificate setup
   - Docker deployment
   - Monitoring and logging
   - Security hardening
   - Backup strategies

### Contributing to the Project

**Want to contribute?**

1. [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
   - Development setup
   - Coding standards
   - Testing guidelines
   - Commit message format
   - Pull request process
   - Areas for contribution

2. [ARCHITECTURE.md](ARCHITECTURE.md) - Understand the codebase
   - Project structure
   - Component responsibilities
   - Design patterns used

### Version History

**Want to see what's changed?**

1. [CHANGELOG.md](CHANGELOG.md) - Version history
   - Release notes
   - New features
   - Bug fixes
   - Breaking changes
   - Future roadmap

## Documentation by Component

### Backend Documentation

Located in `/backend/`:

- **API Documentation**
  - Interactive docs at http://localhost:8000/docs
  - [README.md - API Endpoints](README.md#api-endpoints)

- **Agent Documentation**
  - [ARCHITECTURE.md - Multi-Agent System](ARCHITECTURE.md#multi-agent-system)
  - `/backend/app/agents/RESEARCH_SUBAGENT.md` - Research agent details
  - Agent code with inline documentation

- **Configuration**
  - [README.md - Configuration](README.md#configuration)
  - `/backend/.env.example` - Environment variables
  - `/backend/app/config.py` - Configuration code

### Frontend Documentation

Located in `/frontend/`:

- **Component Documentation**
  - [ARCHITECTURE.md - Component Architecture](ARCHITECTURE.md#component-architecture)
  - Component code with inline documentation

- **API Client**
  - `/frontend/src/api/client.js` - API integration
  - SSE handling

## Quick Reference Guides

### Installation

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

See: [QUICKSTART.md](QUICKSTART.md)

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/sessions` | POST | Create session |
| `/api/sessions/{id}/research` | POST | Start research (SSE) |
| `/api/sessions/{id}/generate` | POST | Generate content (SSE) |
| `/api/sessions/{id}/iterate` | POST | Iterate with feedback (SSE) |
| `/api/sessions/{id}/publish/wordpress` | POST | Publish to WordPress |
| `/api/sessions/{id}/publish/html` | POST | Export HTML |

See: [README.md - API Endpoints](README.md#api-endpoints)

### Agent Roles

| Agent | Type | Role |
|-------|------|------|
| Lead | Orchestrator | Plans research, spawns subagents |
| Research | Worker | Searches web, scrapes content |
| Generator | Worker | Creates content from research |
| Iterator | Worker | Refines based on feedback |
| Publisher | Worker | Publishes to platforms |

See: [README.md - Multi-Agent System](README.md#multi-agent-system)

### Environment Variables

```env
# Required
ANTHROPIC_API_KEY=sk-ant-...
FIRECRAWL_API_KEY=fc-...

# Optional
WORDPRESS_SITE_URL=https://site.com
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=xxxx-xxxx-xxxx
```

See: [README.md - Configuration](README.md#configuration)

## Troubleshooting Guides

### Quick Troubleshooting

1. **Backend won't start**
   - See: [QUICKSTART.md - Common Issues](QUICKSTART.md#common-issues)
   - See: [DEPLOYMENT.md - Troubleshooting](DEPLOYMENT.md#troubleshooting)

2. **Frontend errors**
   - See: [QUICKSTART.md - CORS errors](QUICKSTART.md#cors-errors)

3. **Research fails**
   - See: [QUICKSTART.md - Research fails](QUICKSTART.md#research-fails)

4. **API connection issues**
   - See: [DEPLOYMENT.md - API Connection Timeouts](DEPLOYMENT.md#api-connection-timeouts)

## External Resources

### Anthropic Documentation

- [Claude API Documentation](https://docs.anthropic.com/)
- [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Building Effective Agents](https://docs.anthropic.com/claude/docs/building-effective-agents)

### Technology Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Firecrawl Documentation](https://docs.firecrawl.dev/)

## Documentation Structure

```
cce/
├── README.md                    # Main documentation
├── QUICKSTART.md               # Quick start guide
├── ARCHITECTURE.md             # Architecture details
├── DEPLOYMENT.md               # Deployment guide
├── CONTRIBUTING.md             # Contribution guide
├── CHANGELOG.md                # Version history
├── LICENSE                     # MIT License
├── DOCUMENTATION_INDEX.md      # This file
├── backend/
│   ├── README.md               # Backend specific docs
│   ├── app/
│   │   └── agents/
│   │       └── RESEARCH_SUBAGENT.md
│   └── .env.example
└── frontend/
    └── README.md               # Frontend specific docs
```

## Reading Paths

### Path 1: Beginner User

1. [QUICKSTART.md](QUICKSTART.md) - Get started
2. [README.md - Usage](README.md#usage) - Learn to use it
3. [README.md - API Endpoints](README.md#api-endpoints) - Understand endpoints

### Path 2: Developer

1. [README.md](README.md) - Project overview
2. [ARCHITECTURE.md](ARCHITECTURE.md) - System design
3. [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution setup
4. Agent code in `/backend/app/agents/`

### Path 3: DevOps Engineer

1. [README.md - Technology Stack](README.md#technology-stack) - Understand stack
2. [DEPLOYMENT.md](DEPLOYMENT.md) - Deploy to production
3. [ARCHITECTURE.md - Scalability](ARCHITECTURE.md#scalability) - Scale system

### Path 4: Contributor

1. [CONTRIBUTING.md](CONTRIBUTING.md) - Setup dev environment
2. [ARCHITECTURE.md](ARCHITECTURE.md) - Understand architecture
3. [CONTRIBUTING.md - Areas for Contribution](CONTRIBUTING.md#areas-for-contribution)

## Documentation Standards

All documentation follows these standards:

- **Markdown format** for easy reading and version control
- **Clear headings** for navigation
- **Code examples** with syntax highlighting
- **Tables** for structured information
- **Links** to related documentation
- **Up-to-date** with current codebase

## Keeping Documentation Updated

When making changes:

1. Update relevant markdown files
2. Update inline code documentation
3. Update API documentation if endpoints change
4. Update CHANGELOG.md with changes
5. Verify all links still work

See: [CONTRIBUTING.md - Documentation](CONTRIBUTING.md#coding-standards)

## Getting Help

### Documentation

- Read through all documentation in order listed above
- Check FAQ sections in each document
- Review troubleshooting guides

### Code

- Check inline code comments
- Review test files for usage examples
- Look at `/backend/example_workflow.py`

### Support

- Open an issue on GitHub
- Check existing issues for similar problems
- Review closed issues for solutions

## Documentation Feedback

Found an error in the documentation? Want to suggest improvements?

1. Open an issue describing the problem
2. Submit a pull request with fixes
3. Follow [CONTRIBUTING.md](CONTRIBUTING.md) guidelines

## Search Tips

### Finding Information

**To find API endpoints:**
- Search README.md for "API Endpoints"
- Check http://localhost:8000/docs
- Look at router files in `/backend/app/routers/`

**To understand agents:**
- Search README.md for "Multi-Agent"
- Read ARCHITECTURE.md "Multi-Agent System" section
- Check agent code in `/backend/app/agents/`

**To troubleshoot:**
- Search QUICKSTART.md for error message
- Check DEPLOYMENT.md troubleshooting section
- Search ARCHITECTURE.md for component details

**To deploy:**
- Read DEPLOYMENT.md top to bottom
- Follow production checklist
- Review security considerations

## Version Information

This documentation is for:
- **Version:** 1.0.0
- **Last Updated:** 2026-01-17
- **Status:** Complete

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

All documentation is covered under the same MIT License as the code.
See [LICENSE](LICENSE) for details.

---

## Document Summary

| Document | Pages | Last Updated | Status |
|----------|-------|--------------|--------|
| README.md | ~15 | 2026-01-17 | ✓ Complete |
| QUICKSTART.md | ~8 | 2026-01-17 | ✓ Complete |
| ARCHITECTURE.md | ~20 | 2026-01-17 | ✓ Complete |
| DEPLOYMENT.md | ~18 | 2026-01-17 | ✓ Complete |
| CONTRIBUTING.md | ~12 | 2026-01-17 | ✓ Complete |
| CHANGELOG.md | ~6 | 2026-01-17 | ✓ Complete |
| LICENSE | ~1 | 2026-01-17 | ✓ Complete |

**Total Documentation:** ~80 pages of comprehensive documentation

---

**Happy Reading!**

Start with [QUICKSTART.md](QUICKSTART.md) if you're new, or dive into [ARCHITECTURE.md](ARCHITECTURE.md) if you want to understand the internals.
