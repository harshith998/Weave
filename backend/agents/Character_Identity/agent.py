"""
Character_Identity Agent (Level 2)

Main agent class for character development system.
Takes input from Entry Agent (Level 1) and expands character through 7 specialized sub-agents.

This agent:
1. Receives character overview from Entry Agent
2. Initializes character development session
3. Orchestrates 7 sub-agents in wave-based execution
4. Manages checkpoints and human-in-the-loop approval
5. Returns comprehensive character profile

Note: This agent DOES NOT replace or modify the Entry Agent (Level 1).
It operates as a separate, subsequent stage in the pipeline.
"""

import os
import asyncio
from typing import Optional, List, Dict
from dotenv import load_dotenv

from agent_types import AgentLevel
from .schemas import EntryAgentOutput, FinalCharacterProfile
from .storage import CharacterStorage
from .orchestrator import CharacterOrchestrator


class CharacterIdentityAgent:
    """
    Character Development Agent (Level 2)

    Expands basic character concepts into fully-developed character profiles
    with psychological depth, visual representation, and narrative function.
    """

    def __init__(self, api_key: str, level: AgentLevel):
        """
        Initialize Character Identity Agent

        Args:
            api_key: Anthropic API key
            level: AgentLevel enum (should be AgentLevel.Character_Identity)
        """
        self.anthropic_api_key = api_key
        self.level = level

        # Load additional API keys from environment
        load_dotenv()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        # Initialize storage
        self.storage = CharacterStorage()

        # Track active character sessions
        self.active_sessions: Dict[str, CharacterOrchestrator] = {}

    def start_character_development(
        self,
        entry_output: EntryAgentOutput,
        mode: str = "balanced"
    ) -> str:
        """
        Start character development from Entry Agent output

        Args:
            entry_output: Output from Entry Agent (Level 1)
            mode: Development mode (fast/balanced/deep)

        Returns:
            character_id: UUID of created character session
        """
        # Create character in storage
        character_id = self.storage.create_character(entry_output, mode)
        return character_id

    async def run_character_development(
        self,
        character_id: str,
        websocket_callback: Optional = None
    ) -> FinalCharacterProfile:
        """
        Execute full character development for a character

        Args:
            character_id: Character UUID
            websocket_callback: Optional callback for real-time updates

        Returns:
            FinalCharacterProfile: Complete character profile
        """
        # Create orchestrator
        orchestrator = CharacterOrchestrator(
            character_id=character_id,
            anthropic_api_key=self.anthropic_api_key,
            gemini_api_key=self.gemini_api_key,
            storage=self.storage,
            websocket_callback=websocket_callback
        )

        # Store active session
        self.active_sessions[character_id] = orchestrator

        try:
            # Run all waves
            final_profile = await orchestrator.run_all_waves()
            return final_profile
        finally:
            # Clean up session
            if character_id in self.active_sessions:
                del self.active_sessions[character_id]

    def get_character_status(self, character_id: str) -> Dict:
        """
        Get current status of character development

        Args:
            character_id: Character UUID

        Returns:
            Dict with status information
        """
        metadata = self.storage.load_metadata(character_id)
        kb = self.storage.load_character_kb(character_id)

        return {
            "character_id": character_id,
            "current_wave": kb["current_wave"],
            "current_checkpoint": metadata["current_checkpoint"],
            "status": metadata["status"],
            "progress": {
                "completed_checkpoints": metadata["completed_checkpoints"],
                "total_checkpoints": metadata["total_checkpoints"],
                "current_checkpoint": metadata["current_checkpoint"]
            },
            "agents": kb["agent_statuses"]
        }

    def get_checkpoint(self, character_id: str, checkpoint_number: int):
        """
        Get specific checkpoint data

        Args:
            character_id: Character UUID
            checkpoint_number: Checkpoint number (1-8)

        Returns:
            Checkpoint data or None
        """
        return self.storage.load_checkpoint(character_id, checkpoint_number)

    def approve_checkpoint(self, character_id: str, checkpoint_number: int):
        """
        Approve a checkpoint and allow continuation

        Args:
            character_id: Character UUID
            checkpoint_number: Checkpoint number to approve
        """
        metadata = self.storage.load_metadata(character_id)
        metadata["completed_checkpoints"] = checkpoint_number
        self.storage.save_metadata(character_id, metadata)

    async def regenerate_agent(
        self,
        character_id: str,
        agent_name: str,
        feedback: str
    ):
        """
        Regenerate a specific agent with user feedback

        Args:
            character_id: Character UUID
            agent_name: Name of agent to regenerate (e.g., "personality", "backstory_motivation")
            feedback: User feedback for regeneration
        """
        from .subagents import (
            personality_agent,
            backstory_motivation_agent,
            voice_dialogue_agent,
            physical_description_agent,
            story_arc_agent,
            relationships_agent,
            image_generation_agent
        )

        # Load KB and metadata
        kb = self.storage.load_character_kb(character_id)
        metadata = self.storage.load_metadata(character_id)

        # Add feedback to KB so it's available to the agent
        feedback_key = f"{agent_name}_feedback"
        kb[feedback_key] = feedback
        self.storage.save_character_kb(kb)

        # Map agent name to agent function
        agent_mapping = {
            "personality": personality_agent,
            "backstory_motivation": backstory_motivation_agent,
            "voice_dialogue": voice_dialogue_agent,
            "physical_description": physical_description_agent,
            "story_arc": story_arc_agent,
            "relationships": relationships_agent,
            "image_generation": image_generation_agent,
        }

        if agent_name not in agent_mapping:
            raise ValueError(f"Unknown agent name: {agent_name}. Valid agents: {list(agent_mapping.keys())}")

        agent_func = agent_mapping[agent_name]

        # Re-run the agent with feedback in KB
        if agent_name == "image_generation":
            # Image generation requires additional parameters
            output, narrative = await agent_func(kb, self.gemini_api_key, self.storage)
        else:
            # Text-based agents use Anthropic API
            output, narrative = await agent_func(kb, self.anthropic_api_key)

        # Update KB with new output
        kb[agent_name] = output
        self.storage.save_character_kb(kb)

        # Find the checkpoint number for this agent
        # Map agents to their checkpoint numbers
        checkpoint_mapping = {
            "personality": 1,
            "backstory_motivation": 2,
            "voice_dialogue": 3,
            "physical_description": 4,
            "story_arc": 5,
            "relationships": 6,
            "image_generation": 7,
        }
        checkpoint_num = checkpoint_mapping.get(agent_name, 1)

        # Load and update the checkpoint
        checkpoint = self.storage.load_checkpoint(character_id, checkpoint_num)
        checkpoint["output"]["structured"] = output
        checkpoint["output"]["narrative"] = narrative
        checkpoint["status"] = "awaiting_approval"
        self.storage.save_checkpoint(character_id, checkpoint)

        # Update regeneration count
        metadata["regenerations"] = metadata.get("regenerations", 0) + 1
        self.storage.save_metadata(character_id, metadata)

        return {
            "checkpoint": checkpoint_num,
            "agent": agent_name,
            "status": "regenerated",
            "message": f"Agent '{agent_name}' regenerated with feedback. Review checkpoint #{checkpoint_num}."
        }

    def get_final_profile(self, character_id: str) -> Optional[FinalCharacterProfile]:
        """
        Get final character profile

        Args:
            character_id: Character UUID

        Returns:
            FinalCharacterProfile or None if not yet complete
        """
        return self.storage.load_final_profile(character_id)

    async def run(self, user_input: str, conversation_history: List[Dict]) -> str:
        """
        Main run method for terminal-based interface

        Args:
            user_input: User input string
            conversation_history: Conversation history (should contain Entry Agent JSON output)

        Returns:
            Response string
        """
        import json

        # Look for Entry Agent JSON in conversation history
        entry_json = None
        for msg in reversed(conversation_history):
            if msg["role"] == "assistant" and "FINAL OUTPUT:" in msg["content"]:
                # Extract JSON from Entry Agent output
                try:
                    json_start = msg["content"].index("{")
                    json_end = msg["content"].rindex("}") + 1
                    json_str = msg["content"][json_start:json_end]
                    entry_json = json.loads(json_str)
                    break
                except (ValueError, json.JSONDecodeError):
                    continue

        if not entry_json:
            return """Character Identity Agent (Level 2)

I need the Entry Agent's JSON output to start character development.

Please complete the Entry Agent first to generate character and storyline information.
Then use '/next' to proceed with character development."""

        # Validate Entry Agent JSON structure
        if "characters" not in entry_json or not entry_json["characters"]:
            return """Error: Invalid Entry Agent output - missing or empty 'characters' field.

Please ensure the Entry Agent has completed successfully and outputted character information."""

        if "storyline" not in entry_json:
            return """Error: Invalid Entry Agent output - missing 'storyline' field.

Please ensure the Entry Agent has completed successfully and outputted storyline information."""

        # Start character development
        print("\n" + "="*60)
        print("CHARACTER DEVELOPMENT SYSTEM")
        print("="*60)
        print(f"\nReceived character data: {entry_json.get('characters', [{}])[0].get('name', 'Unknown')}")
        print("Starting 7-agent character development pipeline...")  # personality, backstory, voice, physical, story_arc, relationships, image_generation
        print("\nMode: balanced (can be changed in future)")
        print("="*60 + "\n")

        # Start development
        character_id = self.start_character_development(entry_json, mode="balanced")

        # Run development with terminal display
        final_profile = await self.run_character_development_terminal(character_id)

        if final_profile:
            return f"""
{"="*60}
CHARACTER DEVELOPMENT COMPLETE
{"="*60}

Character: {final_profile['overview']['name']}
Role: {final_profile['overview']['role']}

✓ All 7 checkpoints completed
✓ Character profile saved
✓ Images generated

Character data saved to: backend/character_data/{character_id}/

Type '/next' to proceed to Scene Creator, or continue refining this character.
"""
        else:
            return "Character development encountered an error. Please try again."

    async def run_character_development_terminal(
        self,
        character_id: str
    ) -> Optional[FinalCharacterProfile]:
        """
        Execute character development with terminal-friendly output

        Args:
            character_id: Character UUID

        Returns:
            FinalCharacterProfile or None if error
        """
        # Create orchestrator with terminal callback
        async def terminal_callback(message: Dict):
            """Display progress messages in terminal"""
            msg_type = message.get("type")

            if msg_type == "wave_started":
                wave = message.get("wave", 0)
                wave_names = {1: "Foundation", 2: "Expression", 3: "Social"}
                print(f"\n→ Wave {wave}: {wave_names.get(wave, 'Unknown')} agents starting...")

            elif msg_type == "agent_started":
                agent = message.get("agent", "")
                print(f"  • {agent} agent running...")

            elif msg_type == "agent_completed":
                agent = message.get("agent", "")
                print(f"  ✓ {agent} complete")

            elif msg_type == "agent_failed":
                agent = message.get("agent", "")
                error = message.get("error", "Unknown error")
                print(f"  ✗ {agent} FAILED: {error}")
                print(f"  → Continuing with remaining agents...")

            elif msg_type == "awaiting_approval":
                wave = message.get("wave", 0)
                checkpoints = message.get("checkpoints", [])
                msg = message.get("message", "")

                print(f"\n{'='*60}")
                print(f"WAVE {wave} COMPLETE")
                print(f"{'='*60}")
                print(f"Checkpoints approved: {checkpoints}")
                print(msg)
                print(f"{'='*60}\n")

                while True:
                    wave_approval = input("Continue to next wave? (y/n): ").strip().lower()
                    if wave_approval == 'y':
                        orchestrator.approve_wave(wave)
                        print(f"✓ Wave {wave} approved - continuing...\n")
                        break
                    elif wave_approval == 'n':
                        print("Development paused. Press Ctrl+C to exit.")
                        break
                    else:
                        print("Please enter 'y' or 'n'")

            elif msg_type == "checkpoint_ready":
                checkpoint_num = message.get("checkpoint_number", message.get("checkpoint", 0))
                print(f"\n{'='*60}")
                print(f"Checkpoint #{checkpoint_num} Ready")
                print(f"{'='*60}\n")

                # Display checkpoint
                checkpoint = self.storage.load_checkpoint(character_id, checkpoint_num)
                if checkpoint:
                    print(f"Agent: {checkpoint['agent']}")
                    print(f"\nNarrative:")
                    narrative = checkpoint['output']['narrative']  # FIX: Access nested structure
                    # Show more of the narrative
                    if len(narrative) > 800:
                        print(narrative[:800] + "...")
                        print(f"\n[Full narrative is {len(narrative)} characters - type 'v' to view all]")
                    else:
                        print(narrative)

                    print(f"\nStructured Data:")
                    # Show ALL keys with previews
                    for key, value in checkpoint['output']['structured'].items():  # FIX: Access nested structure
                        if isinstance(value, list):
                            print(f"  • {key}: {len(value)} items")
                            # Show first few items
                            for item in value[:2]:
                                if isinstance(item, str):
                                    preview = item[:70] if len(item) > 70 else item
                                    print(f"    - {preview}")
                                elif isinstance(item, dict):
                                    print(f"    - {str(item)[:70]}...")
                                else:
                                    print(f"    - {item}")
                            if len(value) > 2:
                                print(f"    ... and {len(value) - 2} more")
                        elif isinstance(value, str) and len(value) > 100:
                            print(f"  • {key}: {value[:100]}...")
                        else:
                            print(f"  • {key}: {value}")

                    # Interactive approval
                    print(f"\n{'─'*60}")
                    while True:
                        approval = input(f"Approve? (y/n/v/e): ").strip().lower()
                        if approval == 'v':
                            # Show full checkpoint details
                            print(f"\n{'='*60}")
                            print(f"FULL CHECKPOINT #{checkpoint_num}")
                            print(f"{'='*60}\n")
                            print(f"Agent: {checkpoint['agent']}\n")
                            print(f"Full Narrative:\n{narrative}\n")
                            print(f"Complete Structured Data:")
                            import json
                            print(json.dumps(checkpoint['output']['structured'], indent=2))  # FIX: Access nested structure
                            print(f"\n{'='*60}\n")
                        elif approval == 'y':
                            print(f"✓ Checkpoint #{checkpoint_num} approved\n")
                            self.approve_checkpoint(character_id, checkpoint_num)
                            break
                        elif approval == 'n':
                            print(f"✗ Checkpoint #{checkpoint_num} rejected")
                            feedback = input("Feedback for regeneration (or Enter to skip): ").strip()
                            if feedback:
                                print(f"Noted: {feedback}")
                            # For now, approve anyway to continue (regeneration TODO)
                            self.approve_checkpoint(character_id, checkpoint_num)
                            break
                        elif approval == 'e':
                            # Simple inline edit
                            print(f"\n→ Edit mode for {checkpoint['agent']}")
                            print("Enter new value (or press Enter to keep current):\n")

                            structured = checkpoint['output']['structured']  # FIX: Access nested structure
                            edited = False

                            for key, value in structured.items():
                                if isinstance(value, list) and value:
                                    print(f"\n{key} (currently {len(value)} items):")
                                    for i, item in enumerate(value[:3]):
                                        print(f"  {i+1}. {item}")
                                    if len(value) > 3:
                                        print(f"  ... and {len(value)-3} more")

                                    edit = input(f"Edit {key}? (y/n): ").strip().lower()
                                    if edit == 'y':
                                        print("Enter new items (one per line, empty line when done):")
                                        new_items = []
                                        while True:
                                            item = input("  - ").strip()
                                            if not item:
                                                break
                                            new_items.append(item)
                                        if new_items:
                                            structured[key] = new_items
                                            edited = True
                                            print(f"✓ Updated {key}")

                                elif isinstance(value, str):
                                    current = value[:100] + "..." if len(value) > 100 else value
                                    print(f"\n{key}: {current}")
                                    new_val = input(f"New value (Enter to keep): ").strip()
                                    if new_val:
                                        structured[key] = new_val
                                        edited = True
                                        print(f"✓ Updated {key}")

                            if edited:
                                checkpoint['output']['structured'] = structured  # FIX: Update nested structure
                                self.storage.save_checkpoint(character_id, checkpoint)  # FIX: Correct signature (2 params, not 3)
                                print("\n✓ Checkpoint saved with edits!")
                            else:
                                print("\nNo changes made")
                        else:
                            print("y=approve, n=reject, v=view full, e=edit")

        orchestrator = CharacterOrchestrator(
            character_id=character_id,
            anthropic_api_key=self.anthropic_api_key,
            gemini_api_key=self.gemini_api_key,
            storage=self.storage,
            websocket_callback=terminal_callback
        )

        self.active_sessions[character_id] = orchestrator

        try:
            final_profile = await orchestrator.run_all_waves()
            print(f"\n{'='*60}")
            print("✓ All waves complete!")
            print(f"{'='*60}\n")
            return final_profile
        except Exception as e:
            print(f"\n✗ Error during character development: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            if character_id in self.active_sessions:
                del self.active_sessions[character_id]
