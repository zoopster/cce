"""
Example usage of ResearchSubagent for parallel research.

This demonstrates Anthropic's multi-agent pattern where multiple
research agents execute in parallel, each with a distinct task.
"""

import asyncio
from research import ResearchTask, run_parallel_research


async def example_parallel_research():
    """
    Example: Research a topic using multiple parallel subagents.

    This shows the orchestrator-worker pattern where:
    1. Lead agent (not shown) creates specific research tasks
    2. Multiple research subagents execute in parallel
    3. Each writes findings to filesystem independently
    4. Lead agent aggregates results from filesystem
    """
    session_id = "example_session_123"

    # Create distinct research tasks (normally done by Lead Agent)
    tasks = [
        ResearchTask(
            objective="Find latest statistics and trends for topic",
            search_queries=[
                "topic statistics 2024",  # Broad
                "topic trends data",       # Broad
                "topic market size 2024"   # Narrow
            ],
            output_format="bullet_points",
            max_sources=5,
            tool_guidance="Focus on authoritative sources like research papers and industry reports"
        ),
        ResearchTask(
            objective="Find expert opinions and thought leadership",
            search_queries=[
                "topic expert analysis",   # Broad
                "topic thought leaders",   # Broad
                "topic industry insights"  # Narrow
            ],
            output_format="summary",
            max_sources=4,
            tool_guidance="Prioritize content from recognized experts and institutions"
        ),
        ResearchTask(
            objective="Find case studies and real-world applications",
            search_queries=[
                "topic case studies",      # Broad
                "topic implementation",    # Broad
                "topic success stories"    # Narrow
            ],
            output_format="detailed",
            max_sources=3,
            tool_guidance="Look for detailed case studies with measurable outcomes"
        )
    ]

    # Run all research tasks in parallel
    print(f"Starting parallel research with {len(tasks)} subagents...")
    results = await run_parallel_research(session_id, tasks)

    print(f"\nCompleted! {len(results)} subagents succeeded.")

    # Results are already written to filesystem at:
    # app/memory/{session_id}/research/research_<agent_id>.json

    for i, result in enumerate(results, 1):
        print(f"\n--- Subagent {i} ---")
        print(f"Objective: {result['objective']}")
        print(f"Sources found: {len(result['sources'])}")
        print(f"Tool calls: {result['tool_calls']}")
        print(f"Summary preview: {result['summary'][:200]}...")

    return results


async def example_single_research():
    """
    Example: Use a single research subagent.

    Useful for focused research on one specific aspect.
    """
    from research import ResearchSubagent, ResearchTask

    session_id = "example_session_456"

    task = ResearchTask(
        objective="Find technical specifications and requirements",
        search_queries=[
            "topic technical specs",
            "topic requirements",
            "topic architecture details"
        ],
        output_format="detailed",
        max_sources=5
    )

    # Create and execute single subagent
    agent = ResearchSubagent(session_id, task)
    result = await agent.execute()

    print(f"Research complete!")
    print(f"Agent ID: {result['agent_id']}")
    print(f"Sources: {len(result['sources'])}")
    print(f"Summary:\n{result['summary']}")

    return result


if __name__ == "__main__":
    # Run parallel research example
    asyncio.run(example_parallel_research())

    # Or run single research example
    # asyncio.run(example_single_research())
