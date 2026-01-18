"""
Test suite for the tools layer.

Run this file to verify that all tools are working correctly.
Requires a valid FIRECRAWL_API_KEY in the .env file.
"""

import asyncio
from typing import Dict, Any

from .search import search_web, search_broad, search_narrow
from .scrape import scrape_url, deep_research
from .memory import (
    save_to_memory,
    read_from_memory,
    list_memory_keys,
    aggregate_research,
    clear_session_memory,
)


async def test_search_tools():
    """Test all search functions."""
    print("\n=== Testing Search Tools ===\n")

    try:
        # Test basic search
        print("1. Testing search_web...")
        results = await search_web("Python programming", limit=2)
        print(f"   Found {len(results)} results")
        if results:
            print(f"   First result: {results[0].get('url', 'N/A')}")

        # Test broad search
        print("\n2. Testing search_broad...")
        results = await search_broad("artificial intelligence", limit=2)
        print(f"   Found {len(results)} results")

        # Test narrow search
        print("\n3. Testing search_narrow...")
        results = await search_narrow("AI", "ethics", limit=2)
        print(f"   Found {len(results)} results")

        print("\n✓ All search tests passed!")
        return True

    except Exception as e:
        print(f"\n✗ Search test failed: {e}")
        return False


async def test_scrape_tools():
    """Test all scrape functions."""
    print("\n=== Testing Scrape Tools ===\n")

    try:
        # Test URL scraping
        print("1. Testing scrape_url...")
        content = await scrape_url("https://www.python.org")
        markdown_length = len(content.get("markdown", ""))
        print(f"   Scraped {markdown_length} characters of markdown")
        print(f"   Metadata: {content.get('metadata', {}).get('title', 'N/A')}")

        # Note: Deep research takes a long time, so we skip it in basic tests
        print("\n2. Skipping deep_research (takes too long for basic test)")
        print("   To test manually: await deep_research('topic', max_depth=2, max_urls=5)")

        print("\n✓ All scrape tests passed!")
        return True

    except Exception as e:
        print(f"\n✗ Scrape test failed: {e}")
        return False


def test_memory_tools():
    """Test all memory functions."""
    print("\n=== Testing Memory Tools ===\n")

    try:
        session_id = "test_session_123"

        # Test save
        print("1. Testing save_to_memory...")
        test_data = {
            "sources": ["https://example.com/1", "https://example.com/2"],
            "findings": "This is a test finding",
            "summary": "Test summary"
        }
        path = save_to_memory(session_id, "research/agent_1", test_data)
        print(f"   Saved to: {path}")

        # Test read
        print("\n2. Testing read_from_memory...")
        retrieved_data = read_from_memory(session_id, "research/agent_1")
        print(f"   Retrieved data: {retrieved_data is not None}")
        assert retrieved_data == test_data, "Data mismatch!"

        # Test save another entry
        print("\n3. Saving another entry...")
        save_to_memory(session_id, "research/agent_2", {
            "sources": ["https://example.com/3"],
            "findings": "Another finding"
        })

        # Test list keys
        print("\n4. Testing list_memory_keys...")
        all_keys = list_memory_keys(session_id)
        print(f"   All keys: {all_keys}")
        research_keys = list_memory_keys(session_id, prefix="research/")
        print(f"   Research keys: {research_keys}")
        assert len(research_keys) == 2, "Should have 2 research keys"

        # Test aggregate
        print("\n5. Testing aggregate_research...")
        aggregated = aggregate_research(session_id)
        print(f"   Total sources: {aggregated['total_sources']}")
        print(f"   Number of findings: {len(aggregated['findings'])}")
        assert aggregated['total_sources'] == 3, "Should have 3 total sources"

        # Test clear
        print("\n6. Testing clear_session_memory...")
        cleared = clear_session_memory(session_id)
        print(f"   Session cleared: {cleared}")
        assert cleared, "Session should have been cleared"

        # Verify cleared
        keys_after_clear = list_memory_keys(session_id)
        print(f"   Keys after clear: {keys_after_clear}")
        assert len(keys_after_clear) == 0, "Should have no keys after clear"

        print("\n✓ All memory tests passed!")
        return True

    except Exception as e:
        print(f"\n✗ Memory test failed: {e}")
        # Cleanup on error
        try:
            clear_session_memory(session_id)
        except:
            pass
        return False


async def run_all_tests():
    """Run all test suites."""
    print("\n" + "=" * 60)
    print("TOOLS LAYER TEST SUITE")
    print("=" * 60)

    results = []

    # Test memory (synchronous)
    results.append(("Memory Tools", test_memory_tools()))

    # Test search (async)
    results.append(("Search Tools", await test_search_tools()))

    # Test scrape (async)
    results.append(("Scrape Tools", await test_scrape_tools()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 All tests passed!\n")
    else:
        print("\n⚠️  Some tests failed. Check output above.\n")

    return all_passed


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(run_all_tests())
