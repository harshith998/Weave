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

GATHERING PHASE (TWO PARTS):

PART 1 - STORY & CHARACTERS:
Ask clarifying questions to collect:

1. CHARACTERS (for each main character):
   - Name
   - Physical appearance (general visual description)
   - Personality traits
   - Role in the story
   - Importance in story (side character, main character, antagonist, etc.)

2. STORYLINE:
   - Beginning, middle, end (basic story arc)
   - KEY SCENES (with detailed descriptions):
     * Scene title/label
     * What happens visually in this scene (detailed description for video generation)
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
- At least ONE main character with visual description and role
- Clear storyline with beginning/middle/end
- AT LEAST 3 key scenes with detailed descriptions (title, visual description, characters, setting, mood)
- Overall tone/style preference
- APPROVED visual style with generated image

When you're confident you have sufficient information, use the finalize_output tool to generate the structured JSON.

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

                    return f"""FINAL OUTPUT:

{formatted_json}

✓ Video concept captured!
✓ {len(output_data.get('characters', []))} character(s) outlined
✓ {len(output_data.get('storyline', {}).get('scenes', []))} scene(s) with detailed descriptions

→ Ready for deep character development!
→ Type '/next' to expand characters with the Character Development system
   (6 AI agents will create: psychology, backstory, voice, physical details, story arc, relationships)

→ After that, type '/next' again to reach Scene Creator for final scene refinement
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
