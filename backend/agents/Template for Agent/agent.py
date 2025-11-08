"""
Example agent implementation using Anthropic API with tool calling.
"""

from typing import List, Dict, Any
from anthropic import Anthropic
from agent_types import AgentLevel
from .tools import TOOLS, execute_tool


class ExampleAgent:
    """Main conversational agent with tool calling capabilities"""

    def __init__(self, api_key: str, level: AgentLevel):
        self.api_key = api_key
        self.level = level
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"

    async def run(self, user_input: str, conversation_history: List[Dict[str, str]]) -> str:
        """
        Main execution method - handles conversation with tool calling loop

        Args:
            user_input: User's message
            conversation_history: Previous conversation turns

        Returns:
            Agent's response string
        """
        # Build messages list
        messages = conversation_history + [{"role": "user", "content": user_input}]

        # System prompt
        system_prompt = """

        You are a helpful conversational agent for the Weave video generation system.
        Ask the user to gain information and confirm understanding about the storyline, each individual character overview, and overall overview.
        use the subagent 'tools' to gain questions about this process.
        
        """

        # Initial API call
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
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

            # Get next response
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=messages,
                tools=TOOLS
            )

        # Extract final text response
        text_content = [block.text for block in response.content if hasattr(block, "text")]
        return " ".join(text_content)
