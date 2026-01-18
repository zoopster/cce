# Agent Usage Guide

This guide explains how to use the Iterator and Publisher agents in the Content Creation Engine.

## Overview

The Content Creation Engine now has a complete agent system:

1. **LeadAgent** - Orchestrates the entire workflow
2. **ResearchSubagent** - Gathers information in parallel
3. **ContentGeneratorAgent** - Creates content from research
4. **IteratorAgent** - Refines content based on feedback
5. **PublisherAgent** - Publishes to WordPress or exports HTML

## Iterator Agent

The Iterator Agent handles user feedback and content refinement.

### Basic Usage

```python
from app.agents import IteratorAgent
from app.models.content import ContentSession

# Assuming you have a session with generated content
session = ContentSession(...)  # Your existing session
iterator = IteratorAgent(session)

# Apply user feedback
feedback = "Add more examples and make it more beginner-friendly"
new_content = await iterator.iterate_content(feedback)

print(new_content)  # Updated content
```

### Streaming Updates

For real-time UI updates:

```python
async for chunk in iterator.iterate_stream(feedback):
    print(chunk, end='', flush=True)
```

### Feedback Analysis

The Iterator Agent automatically analyzes feedback to determine:

- Type of change needed (modify, rewrite, add content, research more)
- Which sections are affected
- Whether additional research is needed

```python
analysis = await iterator.analyze_feedback(feedback)
print(f"Action: {analysis['action']}")
print(f"Changes: {analysis['specific_changes']}")
```

### Features

- **Smart Analysis**: Understands different types of feedback
- **Targeted Changes**: Can modify specific sections or do full rewrites
- **Additional Research**: Spawns research subagents if needed
- **Version Tracking**: Maintains history of all iterations

## Publisher Agent

The Publisher Agent handles content publishing and export.

### HTML Export

Export content as a standalone, styled HTML file:

```python
from app.agents import PublisherAgent
from app.models.content import ContentSession

session = ContentSession(...)  # Your session with content
publisher = PublisherAgent(session)

# Export with styles
result = publisher.export_to_html(include_styles=True)

# Save to file
with open(result['filename'], 'w') as f:
    f.write(result['html'])

print(f"Exported to {result['filename']}")
```

### WordPress Publishing

Publish directly to WordPress via REST API:

```python
# Publish as draft
result = await publisher.publish_to_wordpress(
    site_url="https://your-site.com",
    username="your-username",
    app_password="your-app-password",
    status="draft",
    categories=[1, 5],  # Optional category IDs
    tags=[10, 20]       # Optional tag IDs
)

print(f"Published! Edit at: {result['edit_url']}")
```

### Citation Verification

Verify all links in the content are valid:

```python
results = await publisher.verify_citations()

print(f"Total links: {results['total_links']}")
print(f"Valid: {len(results['valid'])}")
print(f"Invalid: {len(results['invalid'])}")

# Show invalid links
for link in results['invalid']:
    print(f"❌ {link['url']} - {link.get('error', link.get('status'))}")
```

### Features

- **HTML Export**: Clean, styled HTML with responsive design
- **WordPress API**: Direct publishing via REST API
- **Link Verification**: Checks all citations are valid
- **Markdown Conversion**: Proper conversion with tables, code blocks, etc.

## Complete Workflow Example

Here's a complete workflow from research to publication:

```python
import asyncio
from app.agents import LeadAgent, ContentGeneratorAgent, IteratorAgent, PublisherAgent
from app.models.content import ContentSession
from app.models.parameters import GenerationParameters, Tone, AudienceLevel

async def complete_workflow():
    # 1. Create session
    params = GenerationParameters(
        tone=Tone.PROFESSIONAL,
        audience_level=AudienceLevel.INTERMEDIATE,
        word_count=1500,
        include_citations=True
    )

    session = ContentSession(
        topic="Python Async Programming Best Practices",
        parameters=params
    )

    # 2. Research (via LeadAgent)
    lead = LeadAgent(session)
    await lead.coordinate_research()

    # 3. Generate content
    generator = ContentGeneratorAgent(session)
    content = await generator.generate_content()
    print("Initial content generated!")

    # 4. User reviews and provides feedback
    feedback = "Add more real-world examples and explain when NOT to use async"

    # 5. Iterate based on feedback
    iterator = IteratorAgent(session)
    refined_content = await iterator.iterate_content(feedback)
    print("Content refined!")

    # 6. Verify citations
    publisher = PublisherAgent(session)
    citation_results = await publisher.verify_citations()
    print(f"Citations verified: {len(citation_results['valid'])} valid")

    # 7. Export HTML
    html_result = publisher.export_to_html()
    with open(html_result['filename'], 'w') as f:
        f.write(html_result['html'])
    print(f"Exported to {html_result['filename']}")

    # 8. Optionally publish to WordPress
    # wp_result = await publisher.publish_to_wordpress(
    #     site_url="https://your-site.com",
    #     username="username",
    #     app_password="app-password",
    #     status="draft"
    # )

if __name__ == "__main__":
    asyncio.run(complete_workflow())
```

## Memory and State Management

All agents use the memory system to track state:

### Iterator Memory

```python
# Version history stored at
session_id/versions/v1.json
session_id/versions/v2.json
# etc.

# Each version contains:
{
  "version_number": 2,
  "content": "...",
  "feedback_applied": "Add more examples",
  "analysis": {...},
  "generated_at": "2024-01-15T10:30:00"
}
```

### Publisher Memory

```python
# HTML exports stored at
session_id/publish/html.json

# WordPress publications at
session_id/publish/wordpress.json

# Citation checks at
session_id/publish/citation_check.json
```

## Error Handling

Both agents include proper error handling:

```python
try:
    result = await publisher.publish_to_wordpress(...)
except httpx.HTTPStatusError as e:
    print(f"WordPress API error: {e.response.status_code}")
except Exception as e:
    print(f"Publishing failed: {e}")
```

## Configuration

### WordPress Application Passwords

To publish to WordPress, you need an application password:

1. Go to WordPress Admin → Users → Profile
2. Scroll to "Application Passwords"
3. Create a new application password
4. Use this instead of your regular password

### Environment Variables

Recommended to store credentials in `.env`:

```bash
WP_SITE_URL=https://your-site.com
WP_USERNAME=your-username
WP_APP_PASSWORD=your-app-password
```

Then use in code:

```python
import os
from dotenv import load_dotenv

load_dotenv()

result = await publisher.publish_to_wordpress(
    site_url=os.getenv("WP_SITE_URL"),
    username=os.getenv("WP_USERNAME"),
    app_password=os.getenv("WP_APP_PASSWORD")
)
```

## API Integration

### FastAPI Endpoints

Example endpoints for the frontend:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1")

class FeedbackRequest(BaseModel):
    session_id: str
    feedback: str

class PublishRequest(BaseModel):
    session_id: str
    site_url: str
    username: str
    app_password: str
    status: str = "draft"

@router.post("/iterate")
async def iterate_content(request: FeedbackRequest):
    session = get_session(request.session_id)  # Your session retrieval
    iterator = IteratorAgent(session)
    new_content = await iterator.iterate_content(request.feedback)
    return {"content": new_content}

@router.post("/export-html")
async def export_html(session_id: str):
    session = get_session(session_id)
    publisher = PublisherAgent(session)
    result = publisher.export_to_html()
    return result

@router.post("/publish-wordpress")
async def publish_wordpress(request: PublishRequest):
    session = get_session(request.session_id)
    publisher = PublisherAgent(session)

    try:
        result = await publisher.publish_to_wordpress(
            site_url=request.site_url,
            username=request.username,
            app_password=request.app_password,
            status=request.status
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Testing

Run the verification script to ensure everything is set up correctly:

```bash
cd backend
python3 verify_agents.py
```

This verifies:
- File structure is correct
- Syntax is valid
- Classes are properly defined
- Imports are correct

## Next Steps

1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Configure Environment**: Copy `.env.example` to `.env` and configure
3. **Test Agents**: Run example workflows
4. **Integrate UI**: Connect to frontend endpoints
5. **Deploy**: Set up production environment

## Troubleshooting

### "Module not found" errors
Install dependencies: `pip install -r requirements.txt`

### WordPress publishing fails
- Verify application password is correct
- Check site URL has no trailing slash
- Ensure WordPress REST API is enabled

### Citation verification slow
This is normal - each link is checked individually. Consider:
- Running verification in background
- Caching results for recent checks
- Setting reasonable timeouts (default 10s)

## Support

For issues or questions:
- Check existing sessions in memory: `app/memory/{session_id}/`
- Review agent states via `agent.get_state()`
- Enable debug logging in settings
