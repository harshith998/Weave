"""
Entry agent for Weave - gathers initial video concept information.
Single LLM system that asks questions and outputs structured JSON when ready.
"""

from typing import List, Dict, Any
import json
from anthropic import Anthropic
from agent_types import AgentLevel


class EntryAgent:
    """Entry agent that gathers video concept details through conversation"""

    def __init__(self, api_key: str, level: AgentLevel):
        self.api_key = api_key
        self.level = level
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"

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

Your mission: Understand the user's video concept and gather complete information about characters and storyline.

CONTEXT: Video generation tools like Sora are inconsistent for long-form content (scenes change, characters look different). Weave solves this by maintaining continuity across clips. You're gathering the foundational information needed.

GATHERING PHASE:
Ask clarifying questions to collect:

1. CHARACTERS (for each main character):
   - Name
   - Physical appearance (detailed visual description)
   - Personality traits
   - Role in the story

2. STORYLINE:
   - Overall concept/theme
   - Beginning, middle, end (basic story arc)
   - Key scenes or moments
   - Tone/style (dramatic, comedic, realistic, etc.)

QUESTION ASKING STRATEGY:
- Start by understanding the basic concept
- Ask focused, specific questions (not overwhelming)
- Ask follow-up questions based on answers
- Be conversational and natural
- If user gives vague answers, probe for specifics (especially visual details for characters)

COMPLETION CRITERIA:
Only finalize when you have:
- At least ONE main character with visual description and role
- Clear storyline with beginning/middle/end or key scenes
- Tone/style preference

When you're confident you have sufficient information, use the finalize_output tool to generate the structured JSON.

DO NOT output JSON directly in your responses - only use the finalize_output tool when ready."""

        # Tool definition - single tool for finalizing output
        tools = [
            {
                "name": "finalize_output",
                "description": "Call this tool when you have gathered sufficient information about characters and storyline. This will generate the final structured JSON output.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "characters": {
                            "type": "array",
                            "description": "List of character objects with their details",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "appearance": {"type": "string", "description": "Detailed visual description"},
                                    "personality": {"type": "string"},
                                    "role": {"type": "string", "description": "Role in the story"}
                                },
                                "required": ["name", "appearance", "role"]
                            }
                        },
                        "storyline": {
                            "type": "object",
                            "description": "Overall storyline information",
                            "properties": {
                                "overview": {"type": "string", "description": "Brief summary of the story"},
                                "scenes": {
                                    "type": "array",
                                    "description": "List of key scenes or story beats",
                                    "items": {"type": "string"}
                                },
                                "tone": {"type": "string", "description": "Overall tone/style"}
                            },
                            "required": ["overview", "tone"]
                        }
                    },
                    "required": ["characters", "storyline"]
                }
            }
        ]

        # Initial API call
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
            tools=tools
        )

        # Tool use loop (should only happen once when agent is ready to finalize)
        while response.stop_reason == "tool_use":
            # Extract tool uses
            tool_uses = [block for block in response.content if block.type == "tool_use"]

            # Build tool results
            tool_results = []
            for tool_use in tool_uses:
                if tool_use.name == "finalize_output":
                    # Format the JSON output nicely
                    output_data = tool_use.input
                    formatted_json = json.dumps(output_data, indent=2)
                    return f"FINAL OUTPUT:\n\n{formatted_json}\n\nInformation gathering complete!"

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": result_message
                    })
                else:
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": "Error: Unknown tool"
                    })

            # Continue conversation with tool results
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

            # Get next response
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=messages,
                tools=tools
            )

        # Extract final text response
        text_content = [block.text for block in response.content if hasattr(block, "text")]
        return " ".join(text_content)
