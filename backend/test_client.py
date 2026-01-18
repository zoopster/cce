#!/usr/bin/env python3
"""
Simple test client for the Content Creation Engine API.

Demonstrates the complete workflow:
1. Create session
2. Start research (with SSE streaming)
3. Generate content (with SSE streaming)
4. Get final content
5. Export as HTML

Usage:
    python test_client.py
"""

import httpx
import json
import sys
from typing import AsyncIterator


BASE_URL = "http://localhost:8000"


async def create_session(topic: str, content_type: str = "blog_post") -> str:
    """Create a new content creation session."""
    print(f"\n{'='*60}")
    print("Creating new session...")
    print(f"{'='*60}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/sessions",
            json={
                "topic": topic,
                "parameters": {
                    "content_type": content_type,
                    "tone": "professional",
                    "audience_level": "intermediate",
                    "word_count": 1000,
                    "keywords": [],
                    "custom_instructions": None
                }
            }
        )
        response.raise_for_status()
        data = response.json()

    session_id = data["session_id"]
    print(f"✓ Session created: {session_id}")
    print(f"  Topic: {data['topic']}")
    print(f"  Status: {data['status']}")
    print(f"  Complexity: {data['complexity']}")

    return session_id


async def stream_research(session_id: str):
    """Start research with SSE streaming."""
    print(f"\n{'='*60}")
    print("Starting research (streaming)...")
    print(f"{'='*60}")

    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream(
            "POST",
            f"{BASE_URL}/api/sessions/{session_id}/research",
            headers={"Accept": "text/event-stream"}
        ) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                if line.startswith("event:"):
                    event_type = line.split(":", 1)[1].strip()
                elif line.startswith("data:"):
                    data_str = line.split(":", 1)[1].strip()
                    try:
                        data = json.loads(data_str)
                        if event_type == "status":
                            print(f"  [{data['phase'].upper()}] {data['message']}")
                        elif event_type == "complexity":
                            print(f"  ✓ Complexity: {data['complexity']}")
                        elif event_type == "plan":
                            print(f"  ✓ Research plan: {data['tasks']} tasks")
                        elif event_type == "research_progress":
                            print(f"  ✓ Progress: {data['agents_completed']}/{data['total_agents']} agents")
                        elif event_type == "complete":
                            print(f"  ✓ COMPLETE: {data['total_sources']} sources found")
                            print(f"\n  Synthesis preview:")
                            print(f"  {data['synthesis_preview'][:200]}...")
                    except json.JSONDecodeError:
                        pass


async def stream_generation(session_id: str):
    """Generate content with SSE streaming."""
    print(f"\n{'='*60}")
    print("Generating content (streaming)...")
    print(f"{'='*60}")

    content_chunks = []

    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream(
            "POST",
            f"{BASE_URL}/api/sessions/{session_id}/generate",
            headers={"Accept": "text/event-stream"}
        ) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                if line.startswith("event:"):
                    event_type = line.split(":", 1)[1].strip()
                elif line.startswith("data:"):
                    data_str = line.split(":", 1)[1].strip()
                    try:
                        data = json.loads(data_str)
                        if event_type == "status":
                            print(f"  [{data['phase'].upper()}] {data['message']}")
                        elif event_type == "outline":
                            print(f"  ✓ Outline created")
                            print(f"\n{data['content'][:300]}...\n")
                        elif event_type == "content_start":
                            print(f"  ✓ Generating content...")
                        elif event_type == "content":
                            chunk = data['chunk']
                            content_chunks.append(chunk)
                            # Print first few chunks to show progress
                            if len(content_chunks) < 10:
                                print(chunk, end='', flush=True)
                        elif event_type == "complete":
                            print(f"\n  ✓ COMPLETE: Version {data['version']} generated")
                    except json.JSONDecodeError:
                        pass


async def get_content(session_id: str) -> str:
    """Get the final content."""
    print(f"\n{'='*60}")
    print("Retrieving final content...")
    print(f"{'='*60}")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/sessions/{session_id}/content")
        response.raise_for_status()
        data = response.json()

    print(f"✓ Content retrieved")
    print(f"  Version: {data['version_number']}")
    print(f"  Length: {len(data['content'])} characters")
    print(f"\nContent preview:")
    print(f"{'-'*60}")
    print(data['content'][:500])
    print(f"{'-'*60}")

    return data['content']


async def export_html(session_id: str):
    """Export content as HTML."""
    print(f"\n{'='*60}")
    print("Exporting as HTML...")
    print(f"{'='*60}")

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/api/sessions/{session_id}/publish/html")
        response.raise_for_status()
        data = response.json()

    print(f"✓ HTML exported")
    print(f"  Filename: {data['filename']}")
    print(f"  Title: {data['title']}")
    print(f"  Size: {len(data['html'])} characters")

    # Save to file
    with open(f"/tmp/{data['filename']}", "w") as f:
        f.write(data["html"])
    print(f"  Saved to: /tmp/{data['filename']}")


async def get_session_info(session_id: str):
    """Get session information."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/sessions/{session_id}")
        response.raise_for_status()
        return response.json()


async def delete_session(session_id: str):
    """Delete the session."""
    print(f"\n{'='*60}")
    print("Cleaning up...")
    print(f"{'='*60}")

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{BASE_URL}/api/sessions/{session_id}")
        response.raise_for_status()

    print(f"✓ Session deleted: {session_id}")


async def main():
    """Run the complete workflow."""
    print("\n" + "="*60)
    print("Content Creation Engine - Test Client")
    print("="*60)

    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            response.raise_for_status()
            print("✓ Server is running")
    except Exception as e:
        print(f"✗ Server not running: {e}")
        print(f"\nStart the server with:")
        print(f"  cd backend && uvicorn app.main:app --reload")
        sys.exit(1)

    try:
        # 1. Create session
        session_id = await create_session(
            topic="Best practices for building RESTful APIs",
            content_type="technical_tutorial"
        )

        # 2. Research
        await stream_research(session_id)

        # 3. Generate content
        await stream_generation(session_id)

        # 4. Get final content
        content = await get_content(session_id)

        # 5. Export as HTML
        await export_html(session_id)

        # 6. Show final session state
        session_info = await get_session_info(session_id)
        print(f"\n{'='*60}")
        print("Final Session State:")
        print(f"{'='*60}")
        print(f"  Status: {session_info['status']}")
        print(f"  Agents: {len(session_info['agents'])}")
        print(f"  Research results: {session_info['research_results_count']}")
        print(f"  Versions: {session_info['versions_count']}")

        # 7. Clean up
        await delete_session(session_id)

        print(f"\n{'='*60}")
        print("✓ Test workflow completed successfully!")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
