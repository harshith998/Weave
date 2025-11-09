"""
Tool definitions and executor for ExampleAgent.
Defines tools in Anthropic format and routes tool calls to subagents.
"""

from typing import Any, Dict

# Import subagents
from .subagents.subagent import research_subagent, creative_subagent


# Tool definitions in Anthropic format
TOOLS = [
    {
        "name": "research_subagent",
        "description": "Research a topic or gather information. Use this when you need to look up facts, analyze concepts, or gather background information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The research query or topic to investigate"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "creative_subagent",
        "description": "Generate creative content like character ideas, scene descriptions, or story elements. Use this when you need creative writing or brainstorming.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The creative prompt or request"
                },
                "style": {
                    "type": "string",
                    "description": "Optional style guide (e.g., 'dramatic', 'comedic', 'realistic')",
                    "default": "neutral"
                }
            },
            "required": ["prompt"]
        }
    }
]


async def execute_tool(tool_name: str, **kwargs) -> str:
    """
    Execute a tool by routing to the appropriate subagent

    Args:
        tool_name: Name of the tool to execute
        **kwargs: Tool parameters

    Returns:
        Tool result as string
    """
    if tool_name == "research_subagent":
        return await research_subagent(kwargs.get("query", ""))

    elif tool_name == "creative_subagent":
        return await creative_subagent(
            prompt=kwargs.get("prompt", ""),
            style=kwargs.get("style", "neutral")
        )

    else:
        return f"Error: Unknown tool '{tool_name}'"
