"""
Entry agent for Weave - gathers initial video concept information.
Single LLM system that asks questions and outputs structured JSON when ready.
"""

from typing import List, Dict, Any
import json
from anthropic import AsyncAnthropic  # FIX: Use AsyncAnthropic for async functions
from agent_types import AgentLevel
from .tools import TOOLS, execute_tool


class EntryAgent:
    """Entry agent that gathers video concept details through conversation"""

    def __init__(self, api_key: str, level: AgentLevel):
        self.api_key = api_key
        self.level = level
        self.client = AsyncAnthropic(api_key=api_key)  # FIX: Use AsyncAnthropic for async functions
        self.model = "claude-haiku-4-5-20251001"  # Using Haiku for speed + cost efficiency

    async def run(self, user_input: str, conversation_history: List[Dict[str, str]]) -> str:
        """
        Main execution method - conversational Q&A until ready to output JSON

        Args:
            user_input: User's message
            conversation_history: Previous conversation turns

        Returns:
            Agent's response string (questions or final JSON)
        """
        # Build messages list
        messages = conversation_history + [{"role": "user", "content": user_input}]

        # System prompt - defines behavior and output format
        system_prompt = """You are the entry agent for Weave, an AI video generation orchestration system.

Your mission: Understand the user's general video concept and gather complete information about characters, storyline, AND visual style.

CONTEXT: Video generation tools like Sora are inconsistent for long-form content (scenes change, characters look different). Weave solves this by maintaining continuity across clips. You're gathering the foundational information needed.

CRITICAL CONSTRAINTS:
- Total video duration: 2 minutes (4 scenes × 30 seconds each)
- You MUST create exactly 4 scenes, each exactly 30 seconds long
- Number scenes 1, 2, 3, 4
- Track which characters appear in which scenes
- Each 30-second scene will later be subdivided into shorter video chunks

GATHERING PHASE (TWO PARTS):

PART 1 - STORY & CHARACTERS:
Ask clarifying questions to collect:

1. CHARACTERS (for each character):
   - Name
   - Physical appearance (BRIEF - detailed development happens later)
   - Personality traits (brief overview)
   - Role in the story
   - Importance level: 'main', 'supporting', or 'minor'
   - Which scenes they appear in (scene numbers: 1, 2, 3, 4)

2. STORYLINE (EXACTLY 4 SCENES):
   - Beginning, middle, end (2-minute story arc across 4 scenes)
   - EXACTLY 4 KEY SCENES (30 seconds each):
     * scene_number (1, 2, 3, or 4)
     * duration (always "30s")
     * Scene title/label
     * What happens visually in this 30-second scene (detailed description)
     * Which characters appear
     * Setting/location
     * Mood/emotional tone of the scene
   - Overall tone/style (dramatic, comedic, realistic, etc.)

PART 2 - VISUAL STYLE:
After gathering story info, discuss visual style:
- Ask about style preferences (cartoon, realistic, anime, Pixar-style, etc.)
- When user describes a style, use the generate_style_image tool to show them an example
- Present the image path clearly so they can view it
- Ask for feedback on the generated style
- If they want changes, refine the description and generate again
- Iterate until they approve the visual style

QUESTION ASKING STRATEGY:
- Start by understanding the basic concept
- Ask focused, specific questions (not overwhelming)
- Ask follow-up questions based on answers
- Be conversational and natural
- If user gives vague answers, probe for specifics (especially visual details for characters)

When gathering scene information, ask about:
- What happens visually in each scene
- Which characters are present
- Where the scene takes place (setting)
- The emotional mood of the scene

USING THE TOOLS:
- generate_style_image: Use when you have a style description to visualize
- finalize_output: ONLY use when you have characters, storyline, AND approved visual style

COMPLETION CRITERIA:
Only finalize when you have:
- At least ONE character with importance level and scenes they appear in
- Clear storyline with beginning/middle/end
- EXACTLY 4 scenes with all required fields (scene_number, duration "30s", title, description, characters, setting, mood)
- Each scene numbered 1, 2, 3, 4
- Each character has appears_in_scenes array populated
- Overall tone/style preference
- APPROVED visual style with generated image (generate ONLY ONE style reference image for the entire project)

When you're confident you have sufficient information, use the finalize_output tool to generate the structured JSON.

IMPORTANT:
- Ensure scene_number and duration "30s" are included for each scene
- Ensure appears_in_scenes is populated for each character
- Generate ONLY ONE style image (not multiple iterations or character-specific images)

DO NOT output JSON directly in your responses - only use the finalize_output tool when ready."""

        # Use tools from tools.py (includes generate_style_image and finalize_output)
        tools = TOOLS

        # Initial API call (FIX: Add await for async client)
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
            tools=tools
        )

        # Tool use loop - handles both image generation and finalization
        while response.stop_reason == "tool_use":
            print("\n" + "="*60)
            print("🔧 DEBUG: Tool use detected in agent.py")
            print("="*60)

            # Extract tool uses
            tool_uses = [block for block in response.content if block.type == "tool_use"]
            print(f"🔢 Number of tool uses: {len(tool_uses)}")

            # Build tool results
            tool_results = []
            for i, tool_use in enumerate(tool_uses):
                print(f"\n--- Tool Use {i+1} ---")
                print(f"🛠️  Tool Name: {tool_use.name}")
                print(f"🆔 Tool Use ID: {tool_use.id}")
                print(f"📦 Tool Input: {tool_use.input}")

                if tool_use.name == "finalize_output":
                    print("✅ Finalize output triggered - formatting JSON...")
                    # Format the JSON output nicely
                    output_data = tool_use.input
                    formatted_json = json.dumps(output_data, indent=2)

                    # Store for next agent
                    self.last_output = output_data

                    # Write storyline to state file
                    from utils.state_manager import write_storyline
                    storyline = output_data.get("storyline", {})
                    if storyline:
                        write_storyline(storyline, project_id="default")
                        print("✓ Storyline written to project state")

                    return f"""FINAL OUTPUT:

{formatted_json}

✓ Video concept captured and saved to state!
✓ {len(output_data.get('characters', []))} character(s) outlined
✓ {len(storyline.get('scenes', []))} scene(s) × 30 seconds = 2 minutes total

→ Ready for deep character development!
→ Type '/next' to expand characters with the Character Development system
   (6 AI agents will create: psychology, backstory, voice, physical details, story arc, relationships)

→ After that, type '/next' again to reach Scene Creator for cinematography refinement
"""

                elif tool_use.name == "generate_style_image":
                    print("🎨 Image generation tool triggered - executing...")
                    # Execute the image generation tool
                    result = await execute_tool(tool_use.name, **tool_use.input)
                    print(f"📤 Tool result: {result}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": str(result)
                    })

                else:
                    print(f"❌ Unknown tool: {tool_use.name}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": "Error: Unknown tool"
                    })

            # Continue conversation with tool results
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

            # Get next response (FIX: Add await for async client)
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=messages,
                tools=tools
            )

        # Extract final text response
        text_content = [block.text for block in response.content if hasattr(block, "text")]
        return " ".join(text_content)
