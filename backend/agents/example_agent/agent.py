"""
Example agent implementation.

This is a template showing how to create a new agent.
Copy this folder and implement the methods for your specific agent.
"""

from typing import Any, Dict, Optional
import sys
sys.path.append('../..')

from base_agent import BaseAgent
from agent_types import AgentLevel


class ExampleAgent(BaseAgent):
    """
    Example agent implementation.

    TODO: Implement your agent logic here.
    """

    def __init__(self, agent_id: str, level: AgentLevel = AgentLevel.MAIN, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, level, config)
        # TODO: Add agent-specific initialization

    async def run(self, task: Dict[str, Any]) -> Any:
        """
        Main execution logic.

        TODO: Implement your agent's main logic here.
        - Process the task
        - Call tools as needed
        - Spawn subagents if required
        - Send checkpoints for progress
        """
        pass

    async def call_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Call an MCP tool.

        TODO: Implement tool calling logic.
        See tools.py for available tools.
        """
        pass

    async def spawn_subagent(self, agent_class: type, config: Optional[Dict[str, Any]] = None) -> BaseAgent:
        """
        Spawn a sub-agent.

        TODO: Implement subagent spawning logic.
        See subagents.py for subagent management.
        """
        pass

    async def send_checkpoint(self, checkpoint_data: Dict[str, Any]) -> None:
        """
        Send checkpoint to orchestrator.

        TODO: Implement checkpoint sending.
        """
        pass
