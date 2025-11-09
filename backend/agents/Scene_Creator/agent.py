"""
Scene Creator agent implementation with mode-switching capabilities.

Supports three personality modes:
- Creative Overview: Fast, smart defaults
- Analytical: Validation-focused, rigorous
- Deep Dive: Maximum user collaboration
"""

from typing import List, Dict, Any, Optional
from anthropic import AsyncAnthropic  # FIX: Use AsyncAnthropic for async functions
from agent_types import AgentLevel
from .tools import TOOLS, execute_tool
import json
from utils.state_manager import read_project_state, update_project_mode

# Import mode system prompts
from .modes import creative_overview, analytical, deep_dive


class SceneCreatorAgent:
    """
    Scene Creator agent with adaptive personality modes.

    Handles scene continuity, cinematography, and narrative flow.
    Mode can be switched mid-creation while preserving conversation history.
    """

    def __init__(self, api_key: str, level: AgentLevel, project_id: str = "default"):
        self.api_key = api_key
        self.level = level
        self.project_id = project_id
        self.client = AsyncAnthropic(api_key=api_key)  # FIX: Use AsyncAnthropic
        self.model = "claude-haiku-4-5-20251001"  # Using Haiku for speed + cost efficiency

        # Load current mode from project state
        self.current_mode = self._load_current_mode()

        # Store scene data when loaded from state
        self.scene_data = None
        self.current_scene_index = 0
        self.total_scenes = 0

    def _load_current_mode(self) -> str:
        """Load current mode from project state."""
        state = read_project_state(self.project_id)
        return state.get("currentMode", "creative_overview")

    def _get_system_prompt(self) -> str:
        """Get system prompt based on current mode."""
        mode_prompts = {
            "creative_overview": creative_overview.SYSTEM_PROMPT,
            "analytical": analytical.SYSTEM_PROMPT,
            "deep_dive": deep_dive.SYSTEM_PROMPT
        }
        return mode_prompts.get(self.current_mode, creative_overview.SYSTEM_PROMPT)

    def switch_mode(self, new_mode: str) -> bool:
        """
        Switch to a different mode.

        Args:
            new_mode: Mode name (creative_overview, analytical, deep_dive)

        Returns:
            True if successful
        """
        valid_modes = ["creative_overview", "analytical", "deep_dive"]
        if new_mode not in valid_modes:
            print(f"Invalid mode: {new_mode}. Valid modes: {valid_modes}")
            return False

        self.current_mode = new_mode
        return update_project_mode(new_mode, self.project_id)

    async def run(self, user_input: str, conversation_history: List[Dict[str, str]]) -> str:
        """
        Main execution method - handles conversation with tool calling loop.

        Args:
            user_input: User's message
            conversation_history: Previous conversation turns (preserved across mode switches)

        Returns:
            Agent's response string
        """
        # Load scene data from state (first time only)
        if self.scene_data is None and user_input.lower() == "start":
            if not self._load_scene_data():
                return "Error: No scene data found in state. Please complete Entry Agent first."
            # Auto-start with Scene 1
            return await self._process_scene_simple(0)

        # Check for mode switch command
        if user_input.lower().startswith("/mode "):
            requested_mode = user_input.lower().replace("/mode ", "").strip()
            if self.switch_mode(requested_mode):
                return f"Mode switched to {requested_mode}. Conversation history preserved. I'll now operate with {requested_mode.replace('_', ' ')} personality."
            else:
                return f"Failed to switch mode. Valid modes: creative_overview, analytical, deep_dive"

        # Check for "next scene" command
        if user_input.lower() in ["next", "next scene", "continue"]:
            next_index = self.current_scene_index + 1
            if next_index >= self.total_scenes:
                return f"✓ All {self.total_scenes} scenes complete! Ready for video generation with Agent 4."
            return await self._process_scene_simple(next_index)

        # Build messages list with scene context if available
        if self.scene_data and user_input.lower() == "start":
            # Inject detailed scene information from Entry Agent
            scenes_list = []
            for i, scene in enumerate(self.scene_data.get('scenes', []), 1):
                if isinstance(scene, dict):
                    # New format: detailed scene objects
                    scene_text = f"""  {i}. **{scene.get('title', 'Untitled Scene')}**
     Description: {scene.get('description', 'No description')}
     Characters: {', '.join(scene.get('characters_involved', ['None']))}
     Setting: {scene.get('setting', 'Not specified')}
     Mood: {scene.get('mood', 'Not specified')}"""
                else:
                    # Old format: simple strings (backwards compatibility)
                    scene_text = f"  {i}. {scene}"
                scenes_list.append(scene_text)

            context = f"""I have storyline information from the Entry Agent:

**Storyline Overview:** {self.scene_data.get('overview', 'Not provided')}
**Overall Tone:** {self.scene_data.get('tone', 'Not specified')}

**Scenes from Entry Agent:**
{chr(10).join(scenes_list)}

I'll help you refine these scenes for video generation. You can ask me to:
- Expand on any scene with more cinematic details
- Ensure continuity between scenes
- Add camera angles and shot types
- Validate technical feasibility

Which scene would you like to work on first, or would you like me to review all scenes for continuity?"""
            messages = conversation_history + [{"role": "user", "content": context}]
        else:
            messages = conversation_history + [{"role": "user", "content": user_input}]

        # Get system prompt based on current mode
        system_prompt = self._get_system_prompt()

        # Initial API call (FIX: Add await for async client)
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=8192,  # Increased for complex scene planning
            system=system_prompt,
            messages=messages,
            tools=TOOLS
        )

        # Tool use loop
        while response.stop_reason == "tool_use":
            # Extract tool uses from response
            tool_uses = [block for block in response.content if block.type == "tool_use"]

            # Build tool results
            tool_results = []
            for tool_use in tool_uses:
                # Execute the tool
                result = await execute_tool(tool_use.name, **tool_use.input)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": str(result)
                })

            # Continue conversation with tool results
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

            # Get next response (FIX: Add await for async client)
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                system=system_prompt,
                messages=messages,
                tools=TOOLS
            )

        # Extract final text response
        text_content = [block.text for block in response.content if hasattr(block, "text")]
        return " ".join(text_content)

    def _load_scene_data(self) -> bool:
        """Load scene data from project state (not conversation history)."""
        from utils.state_manager import read_storyline

        storyline = read_storyline(self.project_id)
        if storyline:
            self.scene_data = storyline
            self.total_scenes = len(storyline.get('scenes', []))
            print(f"✓ Loaded {self.total_scenes} scenes from project state")
            print(f"  Storyline: {self.scene_data.get('overview', 'No overview')[:60]}...")
            return True
        else:
            print("⚠ No storyline found in project state")
            self.scene_data = None
            self.total_scenes = 0
            return False

    async def _process_scene_simple(self, scene_index: int) -> str:
        """
        Process a single scene with simple output (no complex tool calling).

        Args:
            scene_index: 0-based scene index

        Returns:
            Simple confirmation message
        """
        if scene_index >= self.total_scenes:
            return "All scenes complete!"

        scene = self.scene_data['scenes'][scene_index]
        self.current_scene_index = scene_index

        # Simple output for now - just acknowledge the scene
        return f"""
=== Scene {scene_index + 1} of {self.total_scenes} ===

Title: {scene.get('title', 'Untitled')}
Duration: {scene.get('duration', '30s')}
Description: {scene.get('description', '')}
Characters: {', '.join(scene.get('characters_involved', []))}
Setting: {scene.get('setting', 'Not specified')}
Mood: {scene.get('mood', 'Not specified')}

✓ Scene {scene_index + 1} ready for cinematography refinement.

Type 'next' to proceed to Scene {scene_index + 2 if scene_index + 1 < self.total_scenes else 'complete'}.
"""
