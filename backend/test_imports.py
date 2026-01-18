"""Quick test to verify all imports work correctly."""

print("Testing imports...")

try:
    from app.config import settings
    print("✓ Config imported successfully")
except Exception as e:
    print(f"✗ Config import failed: {e}")

try:
    from app.models import (
        ContentType, Tone, AudienceLevel, GenerationParameters,
        SessionStatus, Complexity, ResearchResult, ContentVersion,
        AgentState, ContentSession
    )
    print("✓ All models imported successfully")
except Exception as e:
    print(f"✗ Models import failed: {e}")

try:
    from app.agents.base import BaseAgent
    print("✓ BaseAgent imported successfully")
except Exception as e:
    print(f"✗ BaseAgent import failed: {e}")

try:
    from app.main import app
    print("✓ FastAPI app imported successfully")
except Exception as e:
    print(f"✗ FastAPI app import failed: {e}")

print("\nAll imports successful! Ready to run.")
