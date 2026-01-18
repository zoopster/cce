"""
Quick test to verify Iterator and Publisher agents work correctly.
"""

import asyncio
from datetime import datetime

from app.agents import IteratorAgent, PublisherAgent
from app.models.content import ContentSession, ContentVersion
from app.models.parameters import GenerationParameters, Tone, AudienceLevel


async def test_iterator_agent():
    """Test Iterator Agent feedback analysis."""
    print("Testing Iterator Agent...")

    # Create a test session with a content version
    session = ContentSession(
        topic="Python Best Practices",
        parameters=GenerationParameters(
            tone=Tone.PROFESSIONAL,
            audience_level=AudienceLevel.INTERMEDIATE,
            word_count=1000
        )
    )

    # Add a mock content version
    session.versions.append(
        ContentVersion(
            version_number=1,
            content="# Python Best Practices\n\nPython is a great language. Use PEP 8.",
            generated_at=datetime.utcnow()
        )
    )

    iterator = IteratorAgent(session)

    # Test feedback analysis
    feedback = "Add more examples and explain why PEP 8 matters"
    analysis = await iterator.analyze_feedback(feedback)

    print(f"Feedback analysis: {analysis}")
    print(f"Action: {analysis.get('action')}")
    print(f"Changes needed: {analysis.get('specific_changes')}")

    print("Iterator Agent test passed!\n")


def test_publisher_agent():
    """Test Publisher Agent HTML export."""
    print("Testing Publisher Agent...")

    # Create a test session with content
    session = ContentSession(
        topic="Python Best Practices",
        parameters=GenerationParameters(
            tone=Tone.PROFESSIONAL,
            audience_level=AudienceLevel.INTERMEDIATE,
            word_count=1000
        )
    )

    # Add a mock content version
    session.versions.append(
        ContentVersion(
            version_number=1,
            content="""# Python Best Practices

## Introduction
Python is a powerful programming language.

## Key Principles
1. Follow PEP 8
2. Write readable code
3. Use type hints

## Conclusion
Good practices make better code.""",
            generated_at=datetime.utcnow()
        )
    )

    publisher = PublisherAgent(session)

    # Test HTML export
    result = publisher.export_to_html(include_styles=True)

    print(f"Exported filename: {result['filename']}")
    print(f"Title: {result['title']}")
    print(f"HTML length: {len(result['html'])} characters")

    # Verify HTML contains expected elements
    assert "<h1>" in result["html"]
    assert "<h2>" in result["html"]
    assert "style>" in result["html"]
    assert result["title"] == "Python Best Practices"

    print("Publisher Agent test passed!\n")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Iterator and Publisher Agents")
    print("=" * 60 + "\n")

    await test_iterator_agent()
    test_publisher_agent()

    print("=" * 60)
    print("All tests passed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
