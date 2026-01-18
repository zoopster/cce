#!/usr/bin/env python3
"""
Quick verification script for Lead Agent and Generator Agent.
This script checks that the agents are properly structured and can be instantiated.
"""

import sys
import asyncio
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Mock the models and config to avoid import errors
from unittest.mock import MagicMock
import app.models.content as content_models
import app.config as config_module

# Create mock settings
config_module.settings = MagicMock()
config_module.settings.memory_base_path = Path("app/memory")

def test_agent_structure():
    """Test that agent classes have correct structure."""
    from app.agents.lead import LeadAgent
    from app.agents.generator import ContentGeneratorAgent

    print("✓ Lead Agent imported successfully")
    print("✓ Content Generator Agent imported successfully")

    # Check Lead Agent methods
    lead_methods = [
        'analyze_complexity',
        'create_research_plan',
        'execute_research',
        'synthesize_findings',
        'decide_more_research',
        'run_full_research',
        'get_state'
    ]

    for method in lead_methods:
        if not hasattr(LeadAgent, method):
            print(f"✗ LeadAgent missing method: {method}")
            return False
        print(f"✓ LeadAgent.{method} exists")

    # Check Generator Agent methods
    generator_methods = [
        'read_research',
        'plan_structure',
        'generate_content',
        'generate_stream',
        'run_generation',
        'get_state'
    ]

    for method in generator_methods:
        if not hasattr(ContentGeneratorAgent, method):
            print(f"✗ ContentGeneratorAgent missing method: {method}")
            return False
        print(f"✓ ContentGeneratorAgent.{method} exists")

    print("\n✓ All required methods present")
    return True

def test_imports():
    """Test that all imports work correctly."""
    try:
        from app.agents import (
            BaseAgent,
            ResearchSubagent,
            ResearchTask,
            run_parallel_research,
            LeadAgent,
            ContentGeneratorAgent
        )
        print("✓ All agent imports successful from app.agents")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Lead Agent and Content Generator Agent Verification")
    print("=" * 60)
    print()

    print("Testing imports...")
    imports_ok = test_imports()
    print()

    if imports_ok:
        print("Testing agent structure...")
        structure_ok = test_agent_structure()
        print()

        if structure_ok:
            print("=" * 60)
            print("✓ ALL TESTS PASSED")
            print("=" * 60)
            sys.exit(0)

    print("=" * 60)
    print("✗ SOME TESTS FAILED")
    print("=" * 60)
    sys.exit(1)
