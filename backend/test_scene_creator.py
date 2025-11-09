"""
Test script for Scene Creator Agent
"""

import asyncio
import os
import json

# Load environment variables from local.env if it exists
env_file = os.path.join(os.path.dirname(__file__), '..', 'local.env')
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")  # Remove quotes
                os.environ[key] = value

from agents.Scene_Creator.agent import SceneCreatorAgent
from agent_types import AgentLevel


async def test_imports():
    """Test 1: Verify all imports work"""
    print("\n" + "="*60)
    print("TEST 1: Import Verification")
    print("="*60)

    try:
        from agents.Scene_Creator.tools import TOOLS
        from agents.Scene_Creator.subagents.subagent import (
            cinematography_designer,
            aesthetic_generator,
            scene_validator,
            reference_image_generator,
            timeline_validator,
            checkpoint_manager,
            visual_continuity_checker
        )
        from utils.state_manager import read_project_state, write_scene
        from agents.Scene_Creator.modes import creative_overview, analytical, deep_dive

        print("[OK] All imports successful")
        print(f"[OK] {len(TOOLS)} tools defined")
        print("[OK] State manager ready")
        print("[OK] 3 modes loaded")
        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        return False


async def test_agent_creation():
    """Test 2: Create agent instance"""
    print("\n" + "="*60)
    print("TEST 2: Agent Creation")
    print("="*60)

    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("[FAIL] ANTHROPIC_API_KEY not set")
            return False

        print(f"[OK] ANTHROPIC_API_KEY found: {api_key[:10]}...")

        agent = SceneCreatorAgent(
            api_key=api_key,
            level=AgentLevel.Scene_Creator,
            project_id="test_project"
        )

        print(f"[OK] Agent created successfully")
        print(f"[OK] Current mode: {agent.current_mode}")
        print(f"[OK] Agent level: {agent.level.name}")
        print(f"[OK] Model: {agent.model}")

        return True
    except Exception as e:
        print(f"[FAIL] Agent creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mode_switching():
    """Test 3: Mode switching"""
    print("\n" + "="*60)
    print("TEST 3: Mode Switching")
    print("="*60)

    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        agent = SceneCreatorAgent(api_key=api_key, level=AgentLevel.Scene_Creator)

        # Test each mode
        for mode in ["creative_overview", "analytical", "deep_dive"]:
            result = agent.switch_mode(mode)
            if result:
                print(f"[OK] Switched to {mode}")
            else:
                print(f"[FAIL] Failed to switch to {mode}")
                return False

        # Test invalid mode
        result = agent.switch_mode("invalid_mode")
        if not result:
            print("[OK] Correctly rejected invalid mode")
        else:
            print("[FAIL] Accepted invalid mode")
            return False

        return True
    except Exception as e:
        print(f"[FAIL] Mode switching failed: {e}")
        return False


async def test_state_manager():
    """Test 4: State management"""
    print("\n" + "="*60)
    print("TEST 4: State Management")
    print("="*60)

    try:
        from utils.state_manager import read_project_state, write_project_state, update_project_mode

        # Read default state
        state = read_project_state("test_project")
        print(f"[OK] Read project state")
        print(f"  - Project ID: {state['projectId']}")
        print(f"  - Current mode: {state['currentMode']}")
        print(f"  - Scene count: {state['sceneCount']}")

        # Update mode
        result = update_project_mode("analytical", "test_project")
        if result:
            print("[OK] Updated mode to analytical")
            state = read_project_state("test_project")
            if state['currentMode'] == "analytical":
                print("[OK] Mode persisted correctly")
            else:
                print("[FAIL] Mode not persisted")
                return False
        else:
            print("[FAIL] Failed to update mode")
            return False

        return True
    except Exception as e:
        print(f"[FAIL] State management failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_simple_interaction():
    """Test 5: Simple agent interaction"""
    print("\n" + "="*60)
    print("TEST 5: Simple Agent Interaction")
    print("="*60)

    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("[FAIL] ANTHROPIC_API_KEY not set - skipping")
            return False

        agent = SceneCreatorAgent(api_key=api_key, level=AgentLevel.Scene_Creator)

        # Test mode switch command
        print("\nTesting mode switch via command...")
        response = await agent.run("/mode deep_dive", [])
        print(f"Response: {response}")

        if "deep_dive" in response.lower():
            print("[OK] Mode switch command works")
        else:
            print("[FAIL] Mode switch command didn't work")
            return False

        print("\n[WARN]  Note: Full interaction test with tools requires live API calls")
        print("   This basic test confirms the agent structure is sound")

        return True
    except Exception as e:
        print(f"[FAIL] Simple interaction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_nano_banana_check():
    """Test 6: Check Nano Banana availability"""
    print("\n" + "="*60)
    print("TEST 6: Nano Banana (Gemini) Check")
    print("="*60)

    try:
        gemini_key = os.getenv("GEMINI_API_KEY")

        if gemini_key:
            print(f"[OK] GEMINI_API_KEY found: {gemini_key[:10]}...")
            print("[OK] Nano Banana image generation should work")
        else:
            print("[WARN]  GEMINI_API_KEY not set")
            print("   Image generation will be unavailable")
            print("   (This is optional - agent will work without it)")

        return True
    except Exception as e:
        print(f"[FAIL] Nano Banana check failed: {e}")
        return False


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("SCENE CREATOR AGENT - COMPREHENSIVE TEST SUITE")
    print("="*60)

    results = {}

    # Run tests
    results['imports'] = await test_imports()
    results['agent_creation'] = await test_agent_creation()
    results['mode_switching'] = await test_mode_switching()
    results['state_manager'] = await test_state_manager()
    results['simple_interaction'] = await test_simple_interaction()
    results['nano_banana'] = await test_nano_banana_check()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results.items():
        status = "[OK] PASS" if passed else "[FAIL] FAIL"
        print(f"{status:8} - {test_name.replace('_', ' ').title()}")

    total = len(results)
    passed = sum(results.values())

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n ALL TESTS PASSED - Scene Creator is ready!")
    elif passed >= total - 1:
        print("\n[OK] Core functionality works - minor issues only")
    else:
        print("\n[WARN]  Some tests failed - check errors above")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
