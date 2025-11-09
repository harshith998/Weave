"""Ultra-simple test to verify basic agent functionality"""
import asyncio
import os

# Load environment
env_file = os.path.join(os.path.dirname(__file__), '..', 'local.env')
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip().strip('"').strip("'")

from agents.Scene_Creator.agent import SceneCreatorAgent
from agent_types import AgentLevel

async def test():
    print("Testing Scene Creator Agent - Basic Functionality")
    print("="*60)

    api_key = os.getenv('ANTHROPIC_API_KEY')
    print(f"API Key: {api_key[:15]}...")

    # Create agent
    agent = SceneCreatorAgent(
        api_key=api_key,
        level=AgentLevel.Scene_Creator,
        project_id="basic_test"
    )
    print("Agent created successfully")
    print(f"Current mode: {agent.current_mode}")
    print(f"Model: {agent.model}")

    # Test mode switch (no API call)
    print("\nTesting mode switch...")
    result = agent.switch_mode("deep_dive")
    print(f"Mode switch result: {result}")
    print(f"New mode: {agent.current_mode}")

    # Test with API call - simple message
    print("\n" + "="*60)
    print("Testing with live API call...")
    print("Sending message to agent...")

    try:
        # Use a very simple prompt that shouldn't trigger many tools
        response = await agent.run("Hello, can you help me understand your role?", [])

        print(f"\nReceived response ({len(response)} chars)")
        # Safe print
        safe_response = response.encode('ascii', 'replace').decode('ascii')
        print(f"Response: {safe_response[:300]}...")

        print("\n[SUCCESS] Basic agent functionality works!")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
