# Contributing to Content Creation Engine

Thank you for your interest in contributing to the Content Creation Engine! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Development Workflow](#development-workflow)
- [Areas for Contribution](#areas-for-contribution)

## Code of Conduct

This project follows a standard code of conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Assume good intentions
- Keep discussions professional and on-topic

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.10 or higher
- Node.js 18 or higher
- Git
- A code editor (VS Code recommended)
- Anthropic API key (for testing)
- Firecrawl API key (for testing)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/cce.git
cd cce
```

3. Add upstream remote:

```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/cce.git
```

## Development Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio black flake8 mypy

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Run tests to verify setup
python -m pytest
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Install development dependencies
npm install --save-dev eslint prettier

# Start development server
npm run dev
```

## Project Structure

### Backend (`/backend`)

```
backend/
├── app/
│   ├── agents/           # Agent implementations
│   │   ├── base.py       # Base agent class - extend for new agents
│   │   ├── lead.py       # Lead orchestrator
│   │   ├── research.py   # Research subagent
│   │   ├── generator.py  # Content generator
│   │   ├── iterator.py   # Content iterator
│   │   └── publisher.py  # Publishing agent
│   ├── tools/            # Agent tools
│   │   ├── search.py     # Web search tool
│   │   ├── scrape.py     # Web scraping tool
│   │   └── memory.py     # Filesystem memory
│   ├── routers/          # FastAPI routes
│   │   ├── sessions.py   # Session management
│   │   ├── research.py   # Research endpoints
│   │   ├── generate.py   # Generation endpoints
│   │   └── publish.py    # Publishing endpoints
│   ├── models/           # Pydantic models
│   │   ├── content.py    # Content models
│   │   └── parameters.py # Parameter models
│   ├── config.py         # Configuration
│   └── main.py           # FastAPI app
└── tests/                # Test files
```

### Frontend (`/frontend`)

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── TopicInput.jsx
│   │   ├── ParameterPanel.jsx
│   │   ├── AgentStatusPanel.jsx
│   │   ├── ResearchPanel.jsx
│   │   ├── ContentEditor.jsx
│   │   ├── FeedbackPanel.jsx
│   │   └── PublishPanel.jsx
│   ├── api/
│   │   └── client.js     # API client
│   ├── styles/
│   │   └── app.css       # Styles
│   ├── App.jsx           # Main component
│   └── index.jsx         # Entry point
└── tests/                # Test files
```

## Coding Standards

### Python (Backend)

Follow PEP 8 style guide with these specifics:

```python
# Use Black for formatting
black app/

# Check with flake8
flake8 app/

# Type hints are encouraged
def process_content(content: str, parameters: ContentParameters) -> str:
    """Process content with given parameters."""
    pass

# Docstrings for all public functions
def create_agent(agent_type: str) -> BaseAgent:
    """
    Create an agent of the specified type.

    Args:
        agent_type: Type of agent to create (lead, research, etc.)

    Returns:
        Initialized agent instance

    Raises:
        ValueError: If agent_type is not recognized
    """
    pass
```

### JavaScript/React (Frontend)

```javascript
// Use functional components with hooks
import React, { useState, useEffect } from 'react'

export default function ComponentName({ prop1, prop2 }) {
  const [state, setState] = useState(initialValue)

  // Clear, descriptive function names
  const handleSubmit = async () => {
    // Implementation
  }

  return (
    <div>
      {/* JSX content */}
    </div>
  )
}

// Use ESLint and Prettier
npm run lint
npm run format
```

### General Guidelines

- **Clear naming**: Use descriptive variable and function names
- **Comments**: Explain why, not what
- **Error handling**: Always handle errors gracefully
- **Logging**: Use appropriate log levels
- **Security**: Never commit API keys or secrets
- **Documentation**: Update docs when changing functionality

## Testing Guidelines

### Backend Tests

```python
# tests/test_agents.py
import pytest
from app.agents.lead import LeadAgent

@pytest.mark.asyncio
async def test_lead_agent_initialization():
    """Test that lead agent initializes correctly."""
    agent = LeadAgent()
    assert agent is not None
    assert agent.name == "Lead Agent"

@pytest.mark.asyncio
async def test_research_planning():
    """Test research planning with various topics."""
    agent = LeadAgent()
    plan = await agent.plan_research("Test topic")
    assert plan.num_subagents > 0
    assert len(plan.research_areas) > 0
```

Run tests:
```bash
cd backend
python -m pytest tests/ -v
python -m pytest tests/ --cov=app  # With coverage
```

### Frontend Tests

```javascript
// tests/TopicInput.test.jsx
import { render, screen, fireEvent } from '@testing-library/react'
import TopicInput from '../src/components/TopicInput'

test('renders topic input field', () => {
  render(<TopicInput onSubmit={() => {}} />)
  const input = screen.getByPlaceholderText(/what would you like/i)
  expect(input).toBeInTheDocument()
})
```

Run tests:
```bash
cd frontend
npm test
```

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```
feat(agent): add citation verification to publisher agent

Add functionality to verify citations in generated content
before publishing. Uses Firecrawl to check if cited URLs
are accessible.

Closes #123
```

```
fix(api): correct SSE connection timeout issue

Increase SSE connection timeout from 60s to 300s to prevent
premature disconnections during long-running research tasks.

Fixes #456
```

```
docs(readme): update installation instructions

Add troubleshooting section and clarify Python version
requirements.
```

### Commit Best Practices

- Keep commits atomic (one logical change per commit)
- Write clear, descriptive commit messages
- Reference issue numbers when applicable
- Don't commit sensitive data (.env, API keys)
- Test before committing

## Pull Request Process

### Before Submitting

1. **Update from upstream:**
```bash
git fetch upstream
git rebase upstream/main
```

2. **Run tests:**
```bash
# Backend
cd backend
python -m pytest

# Frontend
cd frontend
npm test
npm run build  # Ensure it builds
```

3. **Check code style:**
```bash
# Backend
black app/
flake8 app/

# Frontend
npm run lint
```

4. **Update documentation:**
- Update README.md if adding features
- Add/update docstrings
- Update API documentation if changing endpoints

### Submitting Pull Request

1. **Push to your fork:**
```bash
git push origin feature-branch-name
```

2. **Create pull request on GitHub:**
- Use a clear, descriptive title
- Fill out the PR template
- Link related issues
- Add screenshots for UI changes
- Request review from maintainers

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests for changes
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows project style guidelines
- [ ] Documentation updated
- [ ] No new warnings
- [ ] All tests pass
```

### Review Process

1. Maintainer reviews code
2. Address feedback
3. Push updates to same branch
4. Once approved, maintainer will merge

## Development Workflow

### Feature Development

```bash
# 1. Create feature branch
git checkout -b feat/new-feature

# 2. Make changes and commit
git add .
git commit -m "feat(scope): description"

# 3. Keep branch updated
git fetch upstream
git rebase upstream/main

# 4. Push and create PR
git push origin feat/new-feature
```

### Bug Fixes

```bash
# 1. Create bugfix branch
git checkout -b fix/bug-description

# 2. Fix and commit
git add .
git commit -m "fix(scope): description"

# 3. Push and create PR
git push origin fix/bug-description
```

## Areas for Contribution

### High Priority

1. **Testing**
   - Increase test coverage
   - Add integration tests
   - Add end-to-end tests

2. **Documentation**
   - Improve API documentation
   - Add more examples
   - Create video tutorials

3. **Error Handling**
   - Better error messages
   - Graceful degradation
   - Retry logic

### Features

1. **Database Integration**
   - Persistent session storage
   - User management
   - Content history

2. **Additional Publishing Targets**
   - Medium integration
   - Ghost CMS
   - Notion
   - Google Docs

3. **Enhanced Research**
   - PDF document analysis
   - Academic paper search
   - Image search and inclusion

4. **Content Improvements**
   - SEO optimization suggestions
   - Readability scoring
   - Plagiarism detection
   - Fact-checking

5. **UI/UX Enhancements**
   - Dark mode
   - Keyboard shortcuts
   - Mobile responsive design
   - Accessibility improvements

6. **Performance**
   - Caching layer
   - Database query optimization
   - Frontend code splitting
   - Progressive web app features

### Bug Reports

When reporting bugs, include:

1. **Description**: Clear description of the bug
2. **Steps to reproduce**: Detailed steps
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**: OS, Python version, Node version
6. **Screenshots**: If applicable
7. **Logs**: Relevant error messages

Use this template:

```markdown
**Bug Description**
Clear description of the bug

**To Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python: [e.g., 3.10.5]
- Node: [e.g., 18.16.0]
- Browser: [e.g., Chrome 114]

**Screenshots**
If applicable

**Additional Context**
Any other relevant information
```

## Development Tools

### Recommended VS Code Extensions

- Python
- Pylance
- Black Formatter
- ESLint
- Prettier
- GitLens
- Thunder Client (API testing)

### Recommended Settings

`.vscode/settings.json`:
```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

## Getting Help

- Check existing issues
- Read documentation
- Review pull requests
- Ask in discussions
- Contact maintainers

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in documentation

## License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

## Questions?

Feel free to open an issue for questions about contributing!

---

Thank you for contributing to the Content Creation Engine!
