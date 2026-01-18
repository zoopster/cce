"""
Complete workflow example showing all agents working together.

This demonstrates the full content creation pipeline:
1. Research coordination
2. Content generation
3. User feedback iteration
4. Publishing/export

NOTE: This requires API keys to be configured in .env
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from app.agents import LeadAgent, ContentGeneratorAgent, IteratorAgent, PublisherAgent
from app.models.content import ContentSession
from app.models.parameters import (
    GenerationParameters,
    Tone,
    AudienceLevel,
    ContentFormat
)


async def complete_content_creation_workflow():
    """
    Demonstrates the complete workflow from research to publication.
    """
    print("\n" + "=" * 70)
    print("Content Creation Engine - Complete Workflow Example")
    print("=" * 70 + "\n")

    # Step 1: Configure session
    print("Step 1: Configuring session...")

    params = GenerationParameters(
        tone=Tone.PROFESSIONAL,
        audience_level=AudienceLevel.INTERMEDIATE,
        word_count=1200,
        content_format=ContentFormat.ARTICLE,
        include_citations=True,
        include_examples=True
    )

    session = ContentSession(
        topic="Best Practices for Python Async Programming",
        parameters=params
    )

    print(f"✓ Session created: {session.session_id}")
    print(f"  Topic: {session.topic}")
    print(f"  Target length: {params.word_count} words")
    print(f"  Tone: {params.tone.value}")
    print(f"  Audience: {params.audience_level.value}\n")

    # Step 2: Research phase
    print("Step 2: Coordinating research...")

    lead = LeadAgent(session)

    # This would normally coordinate research with ResearchSubagents
    # For this example, we'll simulate it
    print("✓ Research coordination initiated")
    print("  (In production, this spawns parallel ResearchSubagents)")
    print("  Skipping actual research for example...\n")

    # Step 3: Generate initial content
    print("Step 3: Generating initial content...")

    generator = ContentGeneratorAgent(session)

    # This would normally generate content from research
    # For this example, we'll create a mock version
    from app.models.content import ContentVersion
    from datetime import datetime

    initial_content = """# Best Practices for Python Async Programming

## Introduction

Python's async/await syntax provides powerful tools for concurrent programming. This article explores best practices for writing efficient asynchronous code.

## Core Principles

1. **Use async/await correctly**: Only use async when you have I/O-bound operations
2. **Avoid blocking the event loop**: Never use blocking operations in async functions
3. **Handle exceptions properly**: Use try/except with proper cleanup

## When to Use Async

Async programming is ideal for:
- Network I/O operations
- Database queries
- File operations
- Multiple concurrent API calls

## Common Pitfalls

Avoid these common mistakes:
- Mixing sync and async code incorrectly
- Not awaiting coroutines
- Blocking the event loop with CPU-intensive tasks

## Conclusion

Async programming can significantly improve application performance when used correctly."""

    session.versions.append(
        ContentVersion(
            version_number=1,
            content=initial_content,
            generated_at=datetime.utcnow()
        )
    )

    print("✓ Initial content generated")
    print(f"  Length: {len(initial_content.split())} words")
    print(f"  Sections: {initial_content.count('##')}")
    print("\n--- Preview (first 200 chars) ---")
    print(initial_content[:200] + "...\n")

    # Step 4: User provides feedback
    print("Step 4: Processing user feedback...")

    # Simulate user feedback
    feedback = """Add more concrete code examples for each principle.
    Also explain the difference between asyncio.gather() and asyncio.create_task()."""

    print(f"Feedback received: \"{feedback}\"\n")

    # Step 5: Iterate based on feedback
    print("Step 5: Applying feedback with Iterator Agent...")

    iterator = IteratorAgent(session)

    # Analyze feedback
    analysis = await iterator.analyze_feedback(feedback)
    print(f"✓ Feedback analyzed")
    print(f"  Action type: {analysis.get('action')}")
    print(f"  Changes needed: {analysis.get('specific_changes')[:100]}...")
    print(f"  Needs research: {analysis.get('needs_research')}\n")

    # Note: We're not actually calling iterate_content here because it requires API keys
    print("  (Skipping actual iteration - requires Anthropic API key)")
    print("  In production, this would:")
    print("    1. Optionally spawn additional research")
    print("    2. Generate improved content version")
    print("    3. Save as version 2\n")

    # Step 6: Verify citations
    print("Step 6: Verifying citations...")

    publisher = PublisherAgent(session)

    # Note: Skipping actual verification for example
    print("  (Skipping actual verification - would check all links)")
    print("  In production, this validates all markdown links\n")

    # Step 7: Export to HTML
    print("Step 7: Exporting to HTML...")

    html_result = publisher.export_to_html(include_styles=True)

    print(f"✓ HTML export complete")
    print(f"  Filename: {html_result['filename']}")
    print(f"  Title: {html_result['title']}")
    print(f"  Size: {len(html_result['html'])} bytes")

    # Save to file
    output_path = Path("output") / html_result['filename']
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(html_result['html'])

    print(f"  Saved to: {output_path.absolute()}\n")

    # Step 8: WordPress publishing (optional)
    print("Step 8: WordPress publishing...")

    load_dotenv()

    wp_url = os.getenv("WP_SITE_URL")
    wp_user = os.getenv("WP_USERNAME")
    wp_pass = os.getenv("WP_APP_PASSWORD")

    if wp_url and wp_user and wp_pass:
        print("  WordPress credentials found in .env")
        print("  (Skipping actual publish - remove this check to publish)")
        print(f"  Would publish to: {wp_url}")

        # To actually publish:
        # wp_result = await publisher.publish_to_wordpress(
        #     site_url=wp_url,
        #     username=wp_user,
        #     app_password=wp_pass,
        #     status="draft"
        # )
        # print(f"  Published! Edit at: {wp_result['edit_url']}")
    else:
        print("  WordPress not configured (set WP_* vars in .env)")

    print()

    # Final summary
    print("=" * 70)
    print("Workflow Summary")
    print("=" * 70)
    print(f"Session ID: {session.session_id}")
    print(f"Topic: {session.topic}")
    print(f"Versions created: {len(session.versions)}")
    print(f"HTML exported: {output_path.absolute()}")
    print(f"\nMemory location: app/memory/{session.session_id}/")
    print("=" * 70 + "\n")


async def iterator_example():
    """
    Focused example showing Iterator Agent capabilities.
    """
    print("\n" + "=" * 70)
    print("Iterator Agent Example")
    print("=" * 70 + "\n")

    from app.models.content import ContentVersion
    from datetime import datetime

    # Create session with existing content
    session = ContentSession(
        topic="Python Testing Best Practices",
        parameters=GenerationParameters(
            tone=Tone.CONVERSATIONAL,
            audience_level=AudienceLevel.BEGINNER,
            word_count=800
        )
    )

    # Add initial content
    initial = """# Python Testing Best Practices

Testing is important. Write tests for your code.

Use pytest. It's good.

## Types of Tests
- Unit tests
- Integration tests

That's all."""

    session.versions.append(
        ContentVersion(
            version_number=1,
            content=initial,
            generated_at=datetime.utcnow()
        )
    )

    print("Initial content (very basic):")
    print("-" * 40)
    print(initial)
    print("-" * 40 + "\n")

    # Create iterator
    iterator = IteratorAgent(session)

    # Different types of feedback
    feedback_examples = [
        "Add more detail about why testing matters",
        "Include code examples for pytest",
        "Explain the difference between unit and integration tests",
        "Make it more beginner-friendly with step-by-step instructions"
    ]

    print("Example feedback types:\n")
    for i, feedback in enumerate(feedback_examples, 1):
        print(f"{i}. \"{feedback}\"")

        # Analyze each (requires API key)
        # analysis = await iterator.analyze_feedback(feedback)
        # print(f"   → Action: {analysis.get('action')}")
        # print(f"   → Changes: {analysis.get('specific_changes')[:80]}...\n")

    print("\n(Analysis requires Anthropic API key)")
    print("=" * 70 + "\n")


async def publisher_example():
    """
    Focused example showing Publisher Agent capabilities.
    """
    print("\n" + "=" * 70)
    print("Publisher Agent Example")
    print("=" * 70 + "\n")

    from app.models.content import ContentVersion
    from datetime import datetime

    # Create session with polished content
    session = ContentSession(
        topic="Introduction to Docker",
        parameters=GenerationParameters()
    )

    content = """# Introduction to Docker

Docker revolutionizes application deployment through containerization.

## What is Docker?

Docker is a platform for developing, shipping, and running applications in containers.

## Key Concepts

1. **Images**: Templates for containers
2. **Containers**: Running instances
3. **Dockerfile**: Build instructions

## Getting Started

```bash
docker run hello-world
docker ps
docker images
```

## Resources

- [Docker Documentation](https://docs.docker.com)
- [Docker Hub](https://hub.docker.com)

## Conclusion

Docker simplifies deployment and ensures consistency across environments."""

    session.versions.append(
        ContentVersion(
            version_number=1,
            content=content,
            generated_at=datetime.utcnow()
        )
    )

    publisher = PublisherAgent(session)

    # 1. HTML Export
    print("1. HTML Export\n")
    html_result = publisher.export_to_html(include_styles=True)

    print(f"   Filename: {html_result['filename']}")
    print(f"   Title: {html_result['title']}")
    print(f"   HTML size: {len(html_result['html'])} bytes")
    print(f"   Has styles: {'<style>' in html_result['html']}")
    print(f"   Has code blocks: {'<code>' in html_result['html']}\n")

    # 2. Basic HTML (no styles)
    print("2. Basic HTML Export\n")
    basic_html = publisher.export_to_html(include_styles=False)
    print(f"   Size difference: {len(html_result['html']) - len(basic_html['html'])} bytes smaller\n")

    # 3. Citation verification
    print("3. Citation Verification\n")
    print("   (Requires actual HTTP requests - skipped)")
    print("   Would check 2 links found in content\n")

    print("=" * 70 + "\n")


async def main():
    """Run all examples."""
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "iterator":
            await iterator_example()
        elif sys.argv[1] == "publisher":
            await publisher_example()
        elif sys.argv[1] == "full":
            await complete_content_creation_workflow()
        else:
            print("Usage: python example_workflow.py [full|iterator|publisher]")
    else:
        print("\nAvailable examples:")
        print("  python example_workflow.py full       - Complete workflow")
        print("  python example_workflow.py iterator   - Iterator Agent focus")
        print("  python example_workflow.py publisher  - Publisher Agent focus")
        print("\nRunning all examples...\n")

        await complete_content_creation_workflow()
        await iterator_example()
        await publisher_example()


if __name__ == "__main__":
    asyncio.run(main())
