"""
Main entry point for the Weave agent system.
Handles terminal interface and routes user input to agents based on AgentLevel enum.
"""

import asyncio
import os
from agent_types import AgentLevel
from agents.Intro_General_Entry.agent import ExampleAgent


async def main():
    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        return

    # Start at first agent in enum
    agent_counter = 1
    conversation_history = []

    print("Weave Agent System")
    print("Type 'exit' to quit, '/next' to move to next agent, '/reset' to restart")
    print("-" * 60)

    # Initialize first agent
    current_agent = ExampleAgent(api_key=api_key, level=AgentLevel.Intro_General_Entry)
    print(f"[Agent: {AgentLevel(agent_counter).name}]")

    while True:
        user_input = input("\nYou: ").strip()

        # Handle commands
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        if user_input.lower() == '/next':
            agent_counter += 1
            if agent_counter > max([level.value for level in AgentLevel]):
                print("Already at last agent!")
                agent_counter = max([level.value for level in AgentLevel])
                continue

            # Switch to next agent
            current_agent = get_agent_by_level(agent_counter, api_key)
            conversation_history = []  # Reset conversation for new agent
            print(f"[Switched to Agent: {AgentLevel(agent_counter).name}]")
            continue

        if user_input.lower() == '/reset':
            agent_counter = 1
            current_agent = ExampleAgent(api_key=api_key, level=AgentLevel.Intro_General_Entry)
            conversation_history = []
            print(f"[Reset to Agent: {AgentLevel(agent_counter).name}]")
            continue

        if not user_input:
            continue

        # Run current agent
        try:
            response = await current_agent.run(user_input, conversation_history)
            print(f"\nAgent: {response}")

            # Update conversation history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})

        except Exception as e:
            print(f"\nError: {str(e)}")


def get_agent_by_level(level: int, api_key: str):
    """Route to appropriate agent based on level"""
    agent_level = AgentLevel(level)

    if agent_level == AgentLevel.Intro_General_Entry:
        return ExampleAgent(api_key=api_key, level=agent_level)
    elif agent_level == AgentLevel.Character_Identity:
        # TODO: return CharacterIdentityAgent(api_key=api_key, level=agent_level)
        print("Character_Identity agent not yet implemented, using ExampleAgent")
        return ExampleAgent(api_key=api_key, level=agent_level)
    elif agent_level == AgentLevel.Scene_Creator:
        # TODO: return SceneCreatorAgent(api_key=api_key, level=agent_level)
        print("Scene_Creator agent not yet implemented, using ExampleAgent")
        return ExampleAgent(api_key=api_key, level=agent_level)
    else:
        return ExampleAgent(api_key=api_key, level=agent_level)


if __name__ == "__main__":
    asyncio.run(main())
