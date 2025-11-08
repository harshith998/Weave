"""
Base agent interface for the agentic system.

This provides the abstract base class that all agents (main, sub, subsub) inherit from.
Implement the methods below in your concrete agent classes.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from agent_types import AgentLevel


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.

    Each agent should:
    - Implement run() for main execution logic
    - Use call_tool() to interact with MCP tools
    - Use spawn_subagent() to create child agents
    - Use send_checkpoint() to report progress
    """

    def __init__(self, agent_id: str, level: AgentLevel, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent.

        Args:
            agent_id: Unique identifier for this agent
            level: Hierarchical level (MAIN, SUB, or SUBSUB)
            config: Optional configuration dictionary
        """
        self.agent_id = agent_id
        self.level = level
        self.config = config or {}
        self.subagents: List[BaseAgent] = []

    @abstractmethod
    async def run(self, task: Dict[str, Any]) -> Any:
        """
        Main execution method for the agent.

        Args:
            task: Task specification dictionary

        Returns:
            Task result
        """
        pass

    @abstractmethod
    async def call_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Call an MCP tool.

        Args:
            tool_name: Name of the tool to call
            **kwargs: Tool arguments

        Returns:
            Tool result
        """
        pass

    @abstractmethod
    async def spawn_subagent(self, agent_class: type, config: Optional[Dict[str, Any]] = None) -> "BaseAgent":
        """
        Spawn a sub-agent.

        Args:
            agent_class: Class of the agent to spawn
            config: Configuration for the new agent

        Returns:
            The spawned agent instance
        """
        pass

    @abstractmethod
    async def send_checkpoint(self, checkpoint_data: Dict[str, Any]) -> None:
        """
        Send a checkpoint update to the orchestrator/parent.

        Args:
            checkpoint_data: Progress/state information
        """
        pass

    async def pause(self) -> None:
        """Pause agent execution (to be implemented)."""
        pass

    async def resume(self) -> None:
        """Resume agent execution (to be implemented)."""
        pass

    async def stop(self) -> None:
        """Stop agent execution (to be implemented)."""
        pass
