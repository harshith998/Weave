"""
Agent hierarchy types for the agentic system.

This enum defines the three levels of agent hierarchy:
- MAIN (1): Top-level orchestrator agents
- SUB (2): Sub-agents spawned by main agents
- SUBSUB (3): Sub-sub-agents spawned by sub-agents
"""

from enum import IntEnum


class AgentLevel(IntEnum):
    """Defines the hierarchical level of an agent in the system."""

    MAIN = 1      # Main orchestrator agent
    SUB = 2       # Sub-agent
    SUBSUB = 3    # Sub-sub-agent
