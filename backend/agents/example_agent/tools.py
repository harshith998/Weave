"""
Tools for ExampleAgent.

Define agent-specific tools and MCP integrations here.
Each agent can have its own set of tools.
"""

from typing import Any, Dict


class ExampleTools:
    """
    Tools available to ExampleAgent.

    TODO: Implement your agent-specific tools here.
    These can be:
    - MCP tool wrappers
    - Custom utility functions
    - API integrations
    """

    @staticmethod
    async def example_tool(param: str) -> Dict[str, Any]:
        """
        Example tool method.

        TODO: Replace with your actual tool implementation.

        Args:
            param: Tool parameter

        Returns:
            Tool result
        """
        pass

    @staticmethod
    async def call_mcp_tool(mcp_name: str, tool_name: str, **kwargs) -> Any:
        """
        Call an MCP tool through the registry.

        TODO: Implement MCP tool calling.

        Args:
            mcp_name: Name of the MCP server
            tool_name: Name of the tool
            **kwargs: Tool arguments

        Returns:
            Tool result
        """
        pass
