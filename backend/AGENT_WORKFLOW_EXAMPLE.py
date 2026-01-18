#!/usr/bin/env python3
"""
Complete workflow example showing Lead Agent and Generator Agent in action.

This demonstrates the full content creation pipeline:
1. Lead Agent orchestrates research
2. Research Subagents gather information in parallel
3. Generator Agent creates content from findings
"""

import asyncio
from datetime import datetime

# Note: This is a demonstration script showing the workflow.
# Actual execution requires dependencies: anthropic, pydantic, firecrawl, etc.


async def demo_complete_workflow():
    """
    Demonstrates the complete content creation workflow.
    """
    print("=" * 70)
    print("CONTENT CREATION ENGINE - MULTI-AGENT WORKFLOW DEMONSTRATION")
    print("=" * 70)
    print()

    # -------------------------------------------------------------------------
    # STEP 1: Initialize Session
    # -------------------------------------------------------------------------
    print("STEP 1: Initialize Content Session")
    print("-" * 70)

    from app.models.content import ContentSession
    from app.models.parameters import (
        GenerationParameters,
        ContentType,
        Tone,
        AudienceLevel
    )

    session = ContentSession(
        topic="Building scalable microservices with Python and FastAPI",
        parameters=GenerationParameters(
            content_type=ContentType.TECHNICAL_TUTORIAL,
            tone=Tone.TECHNICAL,
            audience_level=AudienceLevel.INTERMEDIATE,
            word_count=2500,
            keywords=["FastAPI", "microservices", "Python", "REST API", "Docker"],
            custom_instructions="Include code examples and best practices for production deployment"
        )
    )

    print(f"  Topic: {session.topic}")
    print(f"  Content Type: {session.parameters.content_type.value}")
    print(f"  Target Length: {session.parameters.word_count} words")
    print(f"  Audience: {session.parameters.audience_level.value}")
    print(f"  Session ID: {session.session_id}")
    print()

    # -------------------------------------------------------------------------
    # STEP 2: Lead Agent - Research Orchestration
    # -------------------------------------------------------------------------
    print("STEP 2: Lead Agent - Research Orchestration")
    print("-" * 70)

    from app.agents import LeadAgent

    lead = LeadAgent(session)

    # 2a. Analyze complexity
    print("  2a. Analyzing topic complexity...")
    complexity = await lead.analyze_complexity()
    print(f"      ✓ Complexity: {complexity.value}")
    print()

    # 2b. Create research plan
    print("  2b. Creating research plan...")
    plan = await lead.create_research_plan()
    print(f"      ✓ Created {plan['num_tasks']} research tasks")
    for i, task in enumerate(plan['tasks'], 1):
        print(f"      Task {i}: {task['objective']}")
    print()

    # 2c. Execute parallel research
    print("  2c. Executing parallel research (spawning subagents)...")
    print("      ┌─ Research Agent 1 → Searching, scraping, synthesizing...")
    print("      ├─ Research Agent 2 → Searching, scraping, synthesizing...")
    print("      └─ Research Agent 3 → Searching, scraping, synthesizing...")

    research_results = await lead.execute_research(plan)
    print(f"      ✓ {research_results['successful']} agents completed successfully")
    print()

    # 2d. Synthesize findings
    print("  2d. Synthesizing research findings...")
    synthesis = await lead.synthesize_findings()
    print(f"      ✓ Created unified synthesis ({len(synthesis)} characters)")
    print(f"      Preview: {synthesis[:200]}...")
    print()

    # 2e. Check if more research needed
    print("  2e. Evaluating research completeness...")
    needs_more = await lead.decide_more_research(synthesis)
    if needs_more:
        print("      → Additional research needed, spawning follow-up agents...")
        follow_up = await lead._create_follow_up_plan(synthesis)
        if follow_up:
            await lead.execute_research(follow_up)
            synthesis = await lead.synthesize_findings()
            print("      ✓ Follow-up research complete")
    else:
        print("      ✓ Research complete, ready for generation")
    print()

    # -------------------------------------------------------------------------
    # STEP 3: Content Generator - Create Content
    # -------------------------------------------------------------------------
    print("STEP 3: Content Generator - Create Content")
    print("-" * 70)

    from app.agents import ContentGeneratorAgent

    generator = ContentGeneratorAgent(session)

    # 3a. Read research from filesystem
    print("  3a. Reading research from filesystem...")
    research = await generator.read_research()
    print(f"      ✓ Loaded research ({len(research)} characters)")
    print()

    # 3b. Plan content structure
    print("  3b. Planning content structure...")
    outline = await generator.plan_structure(research)
    print("      ✓ Created outline:")
    for line in outline.split('\n')[:10]:
        print(f"        {line}")
    print("        ...")
    print()

    # 3c. Generate content
    print("  3c. Generating content...")
    print("      → Using Claude Sonnet 4 to write content...")
    content = await generator.generate_content(research, outline)
    print(f"      ✓ Generated content ({len(content)} characters)")
    print()

    # -------------------------------------------------------------------------
    # STEP 4: Results
    # -------------------------------------------------------------------------
    print("STEP 4: Content Generation Results")
    print("-" * 70)

    print(f"  ✓ Research Plan: {plan['num_tasks']} parallel tasks")
    print(f"  ✓ Research Results: {research_results['successful']} successful agents")
    print(f"  ✓ Synthesis: {len(synthesis)} characters")
    print(f"  ✓ Content: {len(content)} characters (~{len(content.split())} words)")
    print(f"  ✓ Versions Saved: {len(session.versions)}")
    print()

    # Show content preview
    print("  Content Preview:")
    print("  " + "-" * 66)
    for line in content.split('\n')[:15]:
        print(f"  {line}")
    print("  ...")
    print()

    # Memory filesystem structure
    print("  Filesystem Memory Structure:")
    print("  " + "-" * 66)
    print(f"  app/memory/{session.session_id}/")
    print("    ├── plan.json              # Research plan")
    print("    ├── synthesis.json         # Synthesized findings")
    print("    ├── outline.json           # Content outline")
    print("    ├── research/")
    print(f"    │   ├── research_*.json  # {research_results['successful']} subagent findings")
    print("    └── versions/")
    print(f"    │   └── v1.json          # Generated content v{len(session.versions)}")
    print()

    print("=" * 70)
    print("✓ WORKFLOW COMPLETE")
    print("=" * 70)
    print()

    return session


async def demo_streaming_generation():
    """
    Demonstrates streaming content generation for real-time display.
    """
    print()
    print("=" * 70)
    print("BONUS: STREAMING CONTENT GENERATION")
    print("=" * 70)
    print()

    # Assume research is already complete from previous workflow
    from app.models.content import ContentSession
    from app.models.parameters import GenerationParameters
    from app.agents import ContentGeneratorAgent

    session = ContentSession(
        topic="Python async programming basics",
        parameters=GenerationParameters()
    )

    generator = ContentGeneratorAgent(session)

    print("Streaming content generation (real-time display):")
    print("-" * 70)

    async for chunk in generator.generate_stream():
        print(chunk, end='', flush=True)

    print()
    print("-" * 70)
    print(f"✓ Streaming complete, version {len(session.versions)} saved")
    print()


def show_architecture():
    """
    Display the multi-agent architecture diagram.
    """
    print()
    print("=" * 70)
    print("MULTI-AGENT ARCHITECTURE")
    print("=" * 70)
    print()
    print("  ┌─────────────────────────────────────────────┐")
    print("  │           Lead Agent                        │")
    print("  │  - Analyze complexity                       │")
    print("  │  - Create research plan                     │")
    print("  │  - Spawn parallel subagents                 │")
    print("  │  - Synthesize findings                      │")
    print("  └──────────────┬──────────────────────────────┘")
    print("                 │")
    print("       ┌─────────┼─────────┐")
    print("       │         │         │")
    print("  ┌────▼───┐ ┌───▼───┐ ┌──▼────┐")
    print("  │Research│ │Research│ │Research│")
    print("  │Agent 1 │ │Agent 2 │ │Agent 3 │")
    print("  └────┬───┘ └───┬───┘ └──┬────┘")
    print("       │         │         │")
    print("       └─────────┼─────────┘")
    print("                 │")
    print("       ┌─────────▼─────────┐")
    print("       │   Filesystem      │ (Shared Memory)")
    print("       │   Memory Store    │ (Prevents telephone game)")
    print("       └─────────┬─────────┘")
    print("                 │")
    print("       ┌─────────▼─────────┐")
    print("       │  Content          │")
    print("       │  Generator Agent  │")
    print("       │  - Plan structure │")
    print("       │  - Generate       │")
    print("       │  - Stream output  │")
    print("       └───────────────────┘")
    print()


def show_key_features():
    """
    Display key features and design patterns.
    """
    print("=" * 70)
    print("KEY FEATURES & DESIGN PATTERNS")
    print("=" * 70)
    print()

    features = [
        ("Orchestrator-Worker Pattern",
         "Lead Agent delegates to parallel Research Subagents"),

        ("Filesystem Coordination",
         "Agents share data via filesystem, avoiding telephone game"),

        ("Start Wide, Then Narrow",
         "Research begins broad, then narrows to specifics"),

        ("Interleaved Thinking",
         "Agents evaluate sources between tool calls"),

        ("Adaptive Research",
         "Lead Agent decides if follow-up research needed"),

        ("Extended Thinking",
         "Generator plans structure before writing"),

        ("Streaming Support",
         "Real-time content display as it's generated"),

        ("Version Management",
         "All content versions saved to filesystem"),
    ]

    for i, (feature, description) in enumerate(features, 1):
        print(f"  {i}. {feature}")
        print(f"     {description}")
        print()


if __name__ == "__main__":
    """
    Run the demonstration workflow.

    Note: This requires all dependencies to be installed:
    - anthropic
    - pydantic
    - firecrawl (or MCP server)
    - python-dotenv
    """

    show_architecture()
    show_key_features()

    print()
    print("To run the actual workflow, ensure all dependencies are installed:")
    print("  pip install anthropic pydantic python-dotenv")
    print()
    print("Then uncomment and run:")
    print("  # asyncio.run(demo_complete_workflow())")
    print("  # asyncio.run(demo_streaming_generation())")
    print()

    # Uncomment to run (requires dependencies):
    # asyncio.run(demo_complete_workflow())
    # asyncio.run(demo_streaming_generation())
