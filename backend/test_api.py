"""
Comprehensive API test script for the Content Creation Engine.

Tests all routers without requiring external dependencies (runs in dry-run mode).
This validates that all imports work and endpoints are properly configured.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")

    try:
        # Test model imports
        from app.models.content import (
            ContentSession, SessionStatus, Complexity,
            ResearchResult, ContentVersion, AgentState
        )
        from app.models.parameters import (
            GenerationParameters, ContentType, Tone, AudienceLevel
        )
        print("✓ Models imported successfully")

        # Test tool imports
        from app.tools.memory import (
            save_to_memory, read_from_memory,
            aggregate_research, clear_session_memory
        )
        from app.tools.search import search_web
        from app.tools.scrape import scrape_url
        print("✓ Tools imported successfully")

        # Test agent imports
        from app.agents.base import BaseAgent
        from app.agents.research import ResearchSubagent, ResearchTask, run_parallel_research
        from app.agents.lead import LeadAgent
        from app.agents.generator import ContentGeneratorAgent
        from app.agents.iterator import IteratorAgent
        from app.agents.publisher import PublisherAgent
        print("✓ Agents imported successfully")

        # Test router imports
        from app.routers.sessions import router as sessions_router
        from app.routers.research import router as research_router
        from app.routers.generate import router as generate_router
        from app.routers.publish import router as publish_router
        print("✓ Routers imported successfully")

        # Test main app import
        from app.main import app
        print("✓ FastAPI app imported successfully")

        return True

    except ImportError as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_router_configuration():
    """Test that routers are properly configured."""
    print("\nTesting router configuration...")

    try:
        from app.main import app

        # Get all routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append({
                    'path': route.path,
                    'methods': list(route.methods) if route.methods else [],
                    'name': route.name
                })

        # Expected endpoints
        expected_endpoints = [
            ('/health', ['GET']),
            ('/', ['GET']),
            ('/api/sessions', ['POST']),
            ('/api/sessions/{session_id}', ['GET', 'DELETE']),
            ('/api/sessions/{session_id}/agents', ['GET']),
            ('/api/sessions/{session_id}/versions', ['GET']),
            ('/api/sessions/{session_id}/content', ['GET']),
            ('/api/sessions/{session_id}/research', ['POST', 'GET']),
            ('/api/sessions/{session_id}/research/synthesis', ['GET']),
            ('/api/sessions/{session_id}/generate', ['POST']),
            ('/api/sessions/{session_id}/iterate', ['POST']),
            ('/api/sessions/{session_id}/versions/{version_number}', ['GET']),
            ('/api/sessions/{session_id}/publish/wordpress', ['POST']),
            ('/api/sessions/{session_id}/publish/html', ['POST']),
            ('/api/sessions/{session_id}/preview', ['GET']),
            ('/api/sessions/{session_id}/download', ['GET']),
            ('/api/sessions/{session_id}/verify-citations', ['POST']),
            ('/api/sessions/{session_id}/markdown', ['GET']),
        ]

        print(f"\nFound {len(routes)} routes:")
        for route in sorted(routes, key=lambda x: x['path']):
            methods = ', '.join(sorted(route['methods']))
            print(f"  {methods:15} {route['path']}")

        # Verify critical endpoints exist
        route_paths = {r['path'] for r in routes}
        missing = []
        for path, methods in expected_endpoints:
            if path not in route_paths:
                missing.append(path)

        if missing:
            print(f"\n✗ Missing endpoints: {missing}")
            return False

        print("\n✓ All expected endpoints configured")
        return True

    except Exception as e:
        print(f"✗ Router configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_validation():
    """Test that Pydantic models work correctly."""
    print("\nTesting model validation...")

    try:
        from app.models.content import ContentSession, SessionStatus, Complexity
        from app.models.parameters import GenerationParameters, ContentType, Tone

        # Test GenerationParameters
        params = GenerationParameters(
            content_type=ContentType.BLOG_POST,
            tone=Tone.PROFESSIONAL,
            word_count=2000,
            keywords=["python", "fastapi"]
        )
        assert params.word_count == 2000
        assert len(params.keywords) == 2
        print("✓ GenerationParameters validated")

        # Test ContentSession
        session = ContentSession(
            topic="How to build a REST API with FastAPI",
            parameters=params
        )
        assert session.status == SessionStatus.CREATED
        assert session.complexity == Complexity.MODERATE
        assert len(session.session_id) > 0
        print("✓ ContentSession validated")

        # Test session serialization
        session_dict = session.model_dump()
        assert session_dict['topic'] == session.topic
        assert session_dict['status'] == 'created'
        print("✓ Model serialization works")

        return True

    except Exception as e:
        print(f"✗ Model validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_endpoints():
    """Test session router request/response models."""
    print("\nTesting session endpoint models...")

    try:
        from app.routers.sessions import CreateSessionRequest, CreateSessionResponse
        from app.models.parameters import GenerationParameters

        # Test request model
        request = CreateSessionRequest(
            topic="Test topic",
            parameters=GenerationParameters()
        )
        assert request.topic == "Test topic"
        print("✓ CreateSessionRequest validated")

        # Test response model (without creating actual session)
        from datetime import datetime
        response = CreateSessionResponse(
            session_id="test-123",
            topic="Test topic",
            status="created",
            complexity="moderate",
            created_at=datetime.utcnow()
        )
        assert response.session_id == "test-123"
        print("✓ CreateSessionResponse validated")

        return True

    except Exception as e:
        print(f"✗ Session endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sse_dependencies():
    """Test that SSE streaming dependencies are available."""
    print("\nTesting SSE streaming dependencies...")

    try:
        from sse_starlette.sse import EventSourceResponse
        print("✓ sse-starlette imported successfully")

        # Verify generator functions exist
        from app.routers.research import research_event_generator
        from app.routers.generate import generate_event_generator, iterate_event_generator
        print("✓ Event generator functions defined")

        return True

    except ImportError as e:
        print(f"✗ SSE dependency test failed: {e}")
        return False


def test_memory_system():
    """Test that memory system works."""
    print("\nTesting memory system...")

    try:
        from app.tools.memory import (
            save_to_memory, read_from_memory,
            list_memory_keys, clear_session_memory
        )

        # Test with temporary session
        test_session_id = "test_session_12345"

        # Save data
        test_data = {"test": "value", "number": 42}
        save_to_memory(test_session_id, "test_key", test_data)
        print("✓ Data saved to memory")

        # Read data
        loaded_data = read_from_memory(test_session_id, "test_key")
        assert loaded_data == test_data
        print("✓ Data read from memory")

        # List keys
        keys = list_memory_keys(test_session_id)
        assert "test_key" in keys
        print("✓ Memory keys listed")

        # Cleanup
        clear_session_memory(test_session_id)
        print("✓ Memory cleaned up")

        return True

    except Exception as e:
        print(f"✗ Memory system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("Content Creation Engine - API Layer Test Suite")
    print("=" * 70)

    tests = [
        ("Imports", test_imports),
        ("Router Configuration", test_router_configuration),
        ("Model Validation", test_model_validation),
        ("Session Endpoints", test_session_endpoints),
        ("SSE Dependencies", test_sse_dependencies),
        ("Memory System", test_memory_system),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            results.append((name, False))

    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {name}")

    print("=" * 70)
    print(f"Result: {passed}/{total} tests passed")
    print("=" * 70)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
