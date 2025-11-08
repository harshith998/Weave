"""
Agent hierarchy for the order.
"""

from enum import IntEnum


class AgentLevel(IntEnum):
    """Defines the hierarchical level of an agent in the system."""

    Intro_General_Entry = 1      # Main entry point overview agent
    Character_Identity = 2       # Character discussion agent
    Scene_Creator = 3            # Scene flow discussion agent
