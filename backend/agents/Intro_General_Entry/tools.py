"""
Tool definitions and executor for EntryAgent.
Handles image generation (NanoBanana) and output finalization.
"""

import os
from typing import Any, Dict
import google.generativeai as genai
from io import BytesIO
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Image generation feature flag (currently disabled but available)
IMAGE_GENERATION_ENABLED = True

# Initialize NanoBanana (Gemini 2.5 Flash Image) when enabled
if IMAGE_GENERATION_ENABLED:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    image_model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
else:
    image_model = None


# Tool definitions in Anthropic format
TOOLS = [
    {
        "name": "generate_style_image",
        "description": "Generate an example image showing the requested visual style. Use this when the user describes a style preference (cartoon, realistic, anime, etc.) and you want to show them a visual example. You can generate multiple iterations based on their feedback.",
        "input_schema": {
            "type": "object",
            "properties": {
                "style_description": {
                    "type": "string",
                    "description": "Detailed description of the visual style to generate (e.g., 'Pixar-style 3D animation', 'realistic cinematic', 'hand-drawn anime style')"
                },
                "context": {
                    "type": "string",
                    "description": "Optional context from the story/characters to incorporate (e.g., 'featuring a detective in a trench coat', 'with a forest setting')",
                    "default": ""
                }
            },
            "required": ["style_description"]
        }
    },
    {
        "name": "finalize_output",
        "description": "Call this tool when you have gathered sufficient information about characters, storyline, AND have an approved visual style with generated image. This will generate the final structured JSON output.",
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
                            "role": {"type": "string", "description": "Role in the story"},
                            "importance": {"type": "string", "description": "Importance in story (main character, side character, antagonist, etc.)"}
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
                            "description": "List of key scenes with detailed descriptions for video generation",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Scene title or label"},
                                    "description": {"type": "string", "description": "Detailed visual description of what happens in this scene"},
                                    "characters_involved": {
                                        "type": "array",
                                        "description": "Which characters appear in this scene",
                                        "items": {"type": "string"}
                                    },
                                    "setting": {"type": "string", "description": "Location and environment for this scene"},
                                    "mood": {"type": "string", "description": "Emotional tone of this specific scene"}
                                },
                                "required": ["title", "description", "characters_involved", "setting"]
                            }
                        },
                        "tone": {"type": "string", "description": "Overall tone/style"}
                    },
                    "required": ["overview", "scenes", "tone"]
                },
                "visual_style": {
                    "type": "object",
                    "description": "Approved visual style information",
                    "properties": {
                        "description": {"type": "string", "description": "Description of the visual style"},
                        "image_path": {"type": "string", "description": "Local path to the approved style example image"}
                    },
                    "required": ["description", "image_path"]
                }
            },
            "required": ["characters", "storyline", "visual_style"]
        }
    }
]


async def generate_style_image(style_description: str, context: str = "") -> str:
    """
    Generate a visual style example using NanoBanana (Gemini 2.5 Flash Image)

    NOTE: Image generation currently disabled. Set IMAGE_GENERATION_ENABLED = True to enable.

    Args:
        style_description: Description of visual style to generate
        context: Optional context from story/characters

    Returns:
        String with image path for user to view
    """
    # Return early if image generation is disabled
    if not IMAGE_GENERATION_ENABLED:
        return ("Image generation is currently disabled. "
                "To enable: Set IMAGE_GENERATION_ENABLED = True in tools.py and ensure GEMINI_API_KEY is set.")

    try:
        # Check API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "Error: GEMINI_API_KEY not found in environment. Please set it in your .env file."
        # Build prompt for image generation
        prompt = f"Generate a visual style example image: {style_description}"
        if context:
            prompt += f". Context: {context}"

        # Generate image using NanoBanana (Gemini 2.5 Flash Image)
        response = image_model.generate_content([prompt])

        # Check response structure and extract image data
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]

            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # Create output directory if it doesn't exist
                        output_dir = "output/style_examples"
                        os.makedirs(output_dir, exist_ok=True)

                        # Generate unique filename with timestamp
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{output_dir}/style_{timestamp}.png"

                        # Save image
                        image_data = BytesIO(part.inline_data.data)
                        img = Image.open(image_data)
                        img.save(filename)

                        return f"Image generated successfully! View it here: {filename}"

        return "Error: No image data found in response. The AI may have refused to generate the image."

    except Exception as e:
        return f"Error generating image: {str(e)}"


async def execute_tool(tool_name: str, **kwargs) -> Any:
    """
    Execute a tool by routing to the appropriate function

    Args:
        tool_name: Name of the tool to execute
        **kwargs: Tool parameters

    Returns:
        Tool result (string or dict)
    """
    # print("\n" + "="*60)
    # print("🔧 DEBUG: execute_tool called")
    # print("="*60)
    # print(f"🛠️  Tool Name: {tool_name}")
    # print(f"📦 Tool Arguments: {kwargs}")

    if tool_name == "generate_style_image":
        # print("➡️  Routing to generate_style_image function...")
        result = await generate_style_image(
            style_description=kwargs.get("style_description", ""),
            context=kwargs.get("context", "")
        )
        # print(f"✅ generate_style_image returned: {result}")
        return result

    elif tool_name == "finalize_output":
        # print("➡️  Finalize output called (no execution needed)")
        # This tool doesn't actually execute - it signals completion
        # The agent.py handles the JSON formatting
        return kwargs

    else:
        print(f"❌ Unknown tool: {tool_name}")
        return f"Error: Unknown tool '{tool_name}'"
