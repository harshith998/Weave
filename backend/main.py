"""
Main entry point for the Weave agent system.
Handles terminal interface and routes user input to agents based on AgentLevel enum.
"""

import asyncio
import os
from dotenv import load_dotenv
from agent_types import AgentLevel
from agents.Intro_General_Entry.agent import EntryAgent
from agents.Scene_Creator.agent import SceneCreatorAgent
from agents.Character_Identity.agent import CharacterIdentityAgent
from agents.Combiner.agent import CombinerAgent


async def main():
    load_dotenv()
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
    print("Scene Creator mode switching: '/mode creative_overview', '/mode analytical', '/mode deep_dive'")
    print("-" * 60)

    # Initialize first agent
    current_agent = EntryAgent(api_key=api_key, level=AgentLevel.Intro_General_Entry)
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
            # KEEP conversation history so next agent can see previous agent's output
            print(f"[Switched to Agent: {AgentLevel(agent_counter).name}]")

            # If switching to Character_Identity and we have Entry Agent output, auto-start
            if AgentLevel(agent_counter) == AgentLevel.Character_Identity:
                # Check if we have Entry Agent JSON in history
                import json
                entry_data = None
                for msg in reversed(conversation_history):
                    if msg["role"] == "assistant" and "FINAL OUTPUT:" in msg["content"]:
                        try:
                            json_start = msg["content"].index("{")
                            json_end = msg["content"].rindex("}") + 1
                            json_str = msg["content"][json_start:json_end]
                            entry_data = json.loads(json_str)
                            break
                        except:
                            continue

                if entry_data:
                    # Get important characters (main + supporting)
                    all_characters = entry_data.get("characters", [])
                    important_characters = [c for c in all_characters
                                          if c.get("importance") in ["main", "supporting"]]

                    print(f"\n→ Found {len(important_characters)} important character(s) to develop:")
                    for i, char in enumerate(important_characters, 1):
                        print(f"   {i}. {char.get('name')} ({char.get('importance')})")

                    print("\n→ Starting character development sequentially...\n")

                    # Process each important character
                    for i, char in enumerate(important_characters, 1):
                        print(f"\n{'='*60}")
                        print(f"CHARACTER {i}/{len(important_characters)}: {char.get('name')}")
                        print(f"{'='*60}\n")

                        try:
                            response = await current_agent.run("start", conversation_history)
                            print(f"\nAgent: {response}")
                            conversation_history.append({"role": "user", "content": "start"})
                            conversation_history.append({"role": "assistant", "content": response})
                        except Exception as e:
                            print(f"\nError: {str(e)}")
                            import traceback
                            traceback.print_exc()

                    print(f"\n✓ All {len(important_characters)} character(s) developed!")
                    print("→ Type '/next' to proceed to Scene Creator")

            # If switching to Scene_Creator, auto-start scene processing
            elif AgentLevel(agent_counter) == AgentLevel.Scene_Creator:
                print("\n→ Starting scene creation (4 scenes × 30s each)...")
                print("→ Processing scenes sequentially...\n")

                # Auto-start with Scene 1
                try:
                    response = await current_agent.run("start", conversation_history)
                    print(f"\nAgent: {response}")
                    conversation_history.append({"role": "user", "content": "start"})
                    conversation_history.append({"role": "assistant", "content": response})

                    # Process remaining scenes (2, 3, 4)
                    for scene_num in range(2, 5):  # Scenes 2, 3, 4
                        print(f"\n→ Type 'next' to proceed to Scene {scene_num}")
                        user_input = input("\nYou: ").strip()

                        if user_input.lower() == "next":
                            response = await current_agent.run("next", conversation_history)
                            print(f"\nAgent: {response}")
                            conversation_history.append({"role": "user", "content": "next"})
                            conversation_history.append({"role": "assistant", "content": response})
                        else:
                            print(f"Pausing at Scene {scene_num - 1}. Type 'next' when ready to continue.")
                            break

                    print("\n✓ Scene creation complete!")
                    print("→ Type '/next' to proceed to Agent 4 (Combiner)")

                except Exception as e:
                    print(f"\nError: {str(e)}")
                    import traceback
                    traceback.print_exc()

            # If switching to Combiner, auto-start video generation
            elif AgentLevel(agent_counter) == AgentLevel.Combiner:
                print("\n→ Starting video generation for 4 scenes (30s each)...")
                print("→ Each 30s scene will be subdivided into ~4 × 8s video chunks\n")

                # Auto-start video generation for all 4 scenes
                try:
                    for scene_num in range(1, 5):
                        print(f"\n{'='*60}")
                        print(f"PROCESSING SCENE {scene_num}/4")
                        print(f"{'='*60}\n")

                        # Agent 4 will subdivide scene and generate videos
                        response = await current_agent.run(f"generate_scene_{scene_num}", conversation_history)
                        print(f"\n{response}")

                        conversation_history.append({"role": "user", "content": f"generate_scene_{scene_num}"})
                        conversation_history.append({"role": "assistant", "content": response})

                    print(f"\n{'='*60}")
                    print("✓ ALL 4 SCENES GENERATED!")
                    print(f"{'='*60}\n")
                    print("→ Your 2-minute video is complete!")

                except Exception as e:
                    print(f"\nError: {str(e)}")
                    import traceback
                    traceback.print_exc()

            continue

        if user_input.lower() == '/reset':
            agent_counter = 1
            current_agent = EntryAgent(api_key=api_key, level=AgentLevel.Intro_General_Entry)
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
        return EntryAgent(api_key=api_key, level=agent_level)
    elif agent_level == AgentLevel.Character_Identity:
        print("Initializing Character Development Agent...")
        return CharacterIdentityAgent(api_key=api_key, level=agent_level)
    elif agent_level == AgentLevel.Scene_Creator:
        print("Initializing Scene Creator Agent...")
        return SceneCreatorAgent(api_key=api_key, level=agent_level)
    elif agent_level == AgentLevel.Combiner:
        print("Initializing Combiner Agent (Video Generation)...")
        return CombinerAgent(api_key=api_key, level=agent_level)
    else:
        print(f"Agent for {agent_level.name} not yet implemented, using EntryAgent as fallback")
        return EntryAgent(api_key=api_key, level=agent_level)


if __name__ == "__main__":
    asyncio.run(main())
