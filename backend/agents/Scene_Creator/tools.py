"""
Tool definitions and executor for Scene Creator Agent.
Defines all specialized subagent tools in Anthropic format.
"""

from typing import Any, Dict

# Import all specialized subagents
from .subagents.subagent import (
    cinematography_designer,
    aesthetic_generator,
    scene_validator,
    reference_image_generator,
    timeline_validator,
    checkpoint_manager,
    visual_continuity_checker
)


# Tool definitions in Anthropic format
TOOLS = [
    {
        "name": "cinematography_designer",
        "description": "Generate cinematography options including shot sequences, camera movements, angles, and composition. Returns multiple creative approaches for comparison. Use when designing how to visually shoot a scene.",
        "input_schema": {
            "type": "object",
            "properties": {
                "scene_description": {
                    "type": "string",
                    "description": "Detailed description of what the scene is about, including actions, emotions, and key moments"
                },
                "options_count": {
                    "type": "integer",
                    "description": "Number of alternative cinematography approaches to generate (default: 2)",
                    "default": 2
                }
            },
            "required": ["scene_description"]
        }
    },
    {
        "name": "aesthetic_generator",
        "description": "Generate aesthetic specifications including color palettes, lighting setups, mood references, and visual style. Use when defining the visual atmosphere and look of a scene.",
        "input_schema": {
            "type": "object",
            "properties": {
                "scene_description": {
                    "type": "string",
                    "description": "Description of the scene and desired mood/atmosphere"
                },
                "element_type": {
                    "type": "string",
                    "description": "Type of aesthetic element to focus on: mood_board, color_palette, or lighting_setup",
                    "enum": ["mood_board", "color_palette", "lighting_setup"],
                    "default": "mood_board"
                }
            },
            "required": ["scene_description"]
        }
    },
    {
        "name": "scene_validator",
        "description": "Validate a scene JSON against continuity rules, narrative logic, and technical feasibility. Returns detailed validation report with issues and suggestions. Use before and after generation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "scene_json": {
                    "type": "string",
                    "description": "Complete scene JSON as string"
                },
                "validation_phase": {
                    "type": "string",
                    "description": "Validation phase: 'pre' (before generation) or 'post' (after generation)",
                    "enum": ["pre", "post"],
                    "default": "pre"
                }
            },
            "required": ["scene_json"]
        }
    },
    {
        "name": "reference_image_generator",
        "description": "Generate reference images using Nano Banana (Gemini 2.5 Flash Image) for storyboards, mood boards, or composition examples. Returns base64 image data. Use to create visual references for scenes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Detailed prompt for image generation, including composition, lighting, mood, and style"
                },
                "aspect_ratio": {
                    "type": "string",
                    "description": "Image aspect ratio",
                    "enum": ["16:9", "21:9", "9:16", "1:1", "2:3", "3:2", "4:5", "5:4"],
                    "default": "16:9"
                },
                "reference_type": {
                    "type": "string",
                    "description": "Type of reference image to generate",
                    "enum": ["storyboard", "mood_board", "composition", "character_reference"],
                    "default": "storyboard"
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "timeline_validator",
        "description": "Validate scene against global timeline and sequence logic. Checks for temporal paradoxes, timeline coherence, and proper sequence order. Use when validating scene continuity across the project.",
        "input_schema": {
            "type": "object",
            "properties": {
                "scene_json": {
                    "type": "string",
                    "description": "Complete scene JSON as string"
                },
                "project_id": {
                    "type": "string",
                    "description": "Project identifier",
                    "default": "default"
                },
                "scene_number": {
                    "type": "string",
                    "description": "Scene number (e.g., '1', '2A', '3')",
                    "default": "1"
                }
            },
            "required": ["scene_json"]
        }
    },
    {
        "name": "checkpoint_manager",
        "description": "Create and format checkpoints for sending progress updates to the orchestrator and combiner agent. Use to communicate status, proposals, validations, or completion.",
        "input_schema": {
            "type": "object",
            "properties": {
                "checkpoint_type": {
                    "type": "string",
                    "description": "Type of checkpoint",
                    "enum": ["proposal", "validation", "approval-request", "progress", "completion", "error"]
                },
                "data": {
                    "type": "object",
                    "description": "Checkpoint data as JSON object (will be converted to dict)",
                    "additionalProperties": True
                },
                "scene_id": {
                    "type": "string",
                    "description": "Scene identifier"
                },
                "agent_mode": {
                    "type": "string",
                    "description": "Current agent mode",
                    "enum": ["creative_overview", "analytical", "deep_dive"]
                }
            },
            "required": ["checkpoint_type", "data", "scene_id", "agent_mode"]
        }
    },
    {
        "name": "visual_continuity_checker",
        "description": "Analyze generated video clips for visual continuity, character consistency, and quality. Returns detailed analysis with quality scores and issues. Use after video generation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "generated_video_data": {
                    "type": "string",
                    "description": "Information about generated video clips (metadata, paths, descriptions)"
                },
                "scene_json": {
                    "type": "string",
                    "description": "Original scene specification JSON as string"
                },
                "character_references": {
                    "type": "string",
                    "description": "Character appearance data from Character_Identity agent (optional)",
                    "default": None
                }
            },
            "required": ["generated_video_data", "scene_json"]
        }
    }
]


async def execute_tool(tool_name: str, **kwargs) -> str:
    """
    Execute a tool by routing to the appropriate subagent.

    Args:
        tool_name: Name of the tool to execute
        **kwargs: Tool parameters

    Returns:
        Tool result as string (usually JSON)
    """
    if tool_name == "cinematography_designer":
        return await cinematography_designer(
            scene_description=kwargs.get("scene_description", ""),
            options_count=kwargs.get("options_count", 2)
        )

    elif tool_name == "aesthetic_generator":
        return await aesthetic_generator(
            scene_description=kwargs.get("scene_description", ""),
            element_type=kwargs.get("element_type", "mood_board")
        )

    elif tool_name == "scene_validator":
        return await scene_validator(
            scene_json=kwargs.get("scene_json", ""),
            validation_phase=kwargs.get("validation_phase", "pre")
        )

    elif tool_name == "reference_image_generator":
        return await reference_image_generator(
            prompt=kwargs.get("prompt", ""),
            aspect_ratio=kwargs.get("aspect_ratio", "16:9"),
            reference_type=kwargs.get("reference_type", "storyboard")
        )

    elif tool_name == "timeline_validator":
        return await timeline_validator(
            scene_json=kwargs.get("scene_json", ""),
            project_id=kwargs.get("project_id", "default"),
            scene_number=kwargs.get("scene_number", "1")
        )

    elif tool_name == "checkpoint_manager":
        return await checkpoint_manager(
            checkpoint_type=kwargs.get("checkpoint_type", "progress"),
            data=kwargs.get("data", {}),
            scene_id=kwargs.get("scene_id", ""),
            agent_mode=kwargs.get("agent_mode", "creative_overview")
        )

    elif tool_name == "visual_continuity_checker":
        return await visual_continuity_checker(
            generated_video_data=kwargs.get("generated_video_data", ""),
            scene_json=kwargs.get("scene_json", ""),
            character_references=kwargs.get("character_references", None)
        )

    else:
        return f"Error: Unknown tool '{tool_name}'"
