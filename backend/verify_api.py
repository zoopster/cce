#!/usr/bin/env python3
"""
Quick verification script to check if the API layer is properly set up.
Run this before starting the server to catch any issues early.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))


def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a required file exists."""
    path = Path(filepath)
    if path.exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ MISSING {description}: {filepath}")
        return False


def verify_file_structure():
    """Verify that all required files exist."""
    print("=" * 70)
    print("Verifying File Structure")
    print("=" * 70)

    required_files = [
        ("app/main.py", "Main FastAPI app"),
        ("app/config.py", "Configuration"),
        ("app/__init__.py", "App package init"),
        ("app/routers/__init__.py", "Routers package init"),
        ("app/routers/sessions.py", "Sessions router"),
        ("app/routers/research.py", "Research router"),
        ("app/routers/generate.py", "Generate router"),
        ("app/routers/publish.py", "Publish router"),
        ("app/models/__init__.py", "Models package init"),
        ("app/models/content.py", "Content models"),
        ("app/models/parameters.py", "Parameter models"),
        ("app/agents/__init__.py", "Agents package init"),
        ("app/agents/base.py", "Base agent"),
        ("app/agents/lead.py", "Lead agent"),
        ("app/agents/research.py", "Research agent"),
        ("app/agents/generator.py", "Generator agent"),
        ("app/agents/iterator.py", "Iterator agent"),
        ("app/agents/publisher.py", "Publisher agent"),
        ("app/tools/__init__.py", "Tools package init"),
        ("app/tools/memory.py", "Memory system"),
        ("app/tools/search.py", "Search tool"),
        ("app/tools/scrape.py", "Scrape tool"),
        ("requirements.txt", "Dependencies"),
        (".env.example", "Environment example"),
    ]

    results = []
    for filepath, description in required_files:
        result = check_file_exists(filepath, description)
        results.append(result)

    return all(results)


def verify_imports():
    """Verify that all critical imports work."""
    print("\n" + "=" * 70)
    print("Verifying Python Imports")
    print("=" * 70)

    imports = [
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("anthropic", "Anthropic API client"),
        ("httpx", "HTTP client"),
        ("pydantic", "Data validation"),
        ("dotenv", "Environment variables"),
        ("markdown", "Markdown processing"),
        ("sse_starlette.sse", "SSE streaming"),
    ]

    results = []
    for module, description in imports:
        try:
            __import__(module)
            print(f"✓ {description}: {module}")
            results.append(True)
        except ImportError:
            print(f"✗ MISSING {description}: {module}")
            print(f"  Install with: pip install {module}")
            results.append(False)

    return all(results)


def verify_app_imports():
    """Verify that app modules can be imported."""
    print("\n" + "=" * 70)
    print("Verifying App Module Imports")
    print("=" * 70)

    app_modules = [
        ("app.config", "Configuration"),
        ("app.models.content", "Content models"),
        ("app.models.parameters", "Parameter models"),
        ("app.tools.memory", "Memory system"),
        ("app.agents.base", "Base agent"),
        ("app.agents.lead", "Lead agent"),
        ("app.routers.sessions", "Sessions router"),
        ("app.routers.research", "Research router"),
        ("app.routers.generate", "Generate router"),
        ("app.routers.publish", "Publish router"),
        ("app.main", "Main app"),
    ]

    results = []
    for module, description in app_modules:
        try:
            __import__(module)
            print(f"✓ {description}: {module}")
            results.append(True)
        except ImportError as e:
            print(f"✗ FAILED {description}: {module}")
            print(f"  Error: {e}")
            results.append(False)

    return all(results)


def verify_router_registration():
    """Verify that all routers are registered in main app."""
    print("\n" + "=" * 70)
    print("Verifying Router Registration")
    print("=" * 70)

    try:
        from app.main import app

        # Count registered routes
        route_count = len([r for r in app.routes if hasattr(r, 'path')])
        print(f"✓ Total routes registered: {route_count}")

        # Check for critical endpoints
        required_paths = [
            "/health",
            "/api/sessions",
            "/api/sessions/{session_id}",
            "/api/sessions/{session_id}/research",
            "/api/sessions/{session_id}/generate",
            "/api/sessions/{session_id}/publish/wordpress",
        ]

        route_paths = {r.path for r in app.routes if hasattr(r, 'path')}

        results = []
        for path in required_paths:
            if path in route_paths:
                print(f"✓ Endpoint registered: {path}")
                results.append(True)
            else:
                print(f"✗ MISSING endpoint: {path}")
                results.append(False)

        return all(results)

    except Exception as e:
        print(f"✗ Failed to load app: {e}")
        return False


def verify_environment():
    """Check environment configuration."""
    print("\n" + "=" * 70)
    print("Verifying Environment Configuration")
    print("=" * 70)

    env_file = Path(".env")

    if not env_file.exists():
        print("⚠ .env file not found")
        print("  Copy .env.example to .env and configure your API keys")
        return False

    # Check for required variables
    with open(env_file) as f:
        env_content = f.read()

    required_vars = ["ANTHROPIC_API_KEY"]
    results = []

    for var in required_vars:
        if f"{var}=" in env_content:
            # Check if it has a real value (not the example)
            if f"{var}=sk-ant-" in env_content:
                # Check if it's not the example placeholder
                if "..." not in env_content.split(f"{var}=")[1].split("\n")[0]:
                    print(f"✓ {var} is set")
                    results.append(True)
                else:
                    print(f"⚠ {var} appears to be placeholder value")
                    results.append(False)
            else:
                print(f"⚠ {var} is set but may be invalid")
                results.append(True)
        else:
            print(f"✗ {var} not found in .env")
            results.append(False)

    return all(results)


def verify_memory_directory():
    """Check memory directory setup."""
    print("\n" + "=" * 70)
    print("Verifying Memory Directory")
    print("=" * 70)

    memory_dir = Path("app/memory")

    try:
        memory_dir.mkdir(parents=True, exist_ok=True)

        # Test write permissions
        test_file = memory_dir / "test_write.txt"
        test_file.write_text("test")
        test_file.unlink()

        print(f"✓ Memory directory ready: {memory_dir.absolute()}")
        print(f"✓ Directory is writable")
        return True

    except Exception as e:
        print(f"✗ Memory directory issue: {e}")
        return False


def print_summary(results: dict):
    """Print verification summary."""
    print("\n" + "=" * 70)
    print("Verification Summary")
    print("=" * 70)

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for check, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {check}")

    print("=" * 70)
    print(f"Result: {passed}/{total} checks passed")
    print("=" * 70)

    if passed == total:
        print("\n✅ All checks passed! You're ready to start the server.")
        print("\nRun: ./run.sh")
        print("Or:  uvicorn app.main:app --reload\n")
        return True
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Create .env file: cp .env.example .env")
        print("  - Set ANTHROPIC_API_KEY in .env file\n")
        return False


def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print("Content Creation Engine - API Layer Verification")
    print("=" * 70)
    print()

    results = {
        "File Structure": verify_file_structure(),
        "Python Dependencies": verify_imports(),
        "App Module Imports": verify_app_imports(),
        "Router Registration": verify_router_registration(),
        "Environment Config": verify_environment(),
        "Memory Directory": verify_memory_directory(),
    }

    success = print_summary(results)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
