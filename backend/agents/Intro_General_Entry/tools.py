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
IMAGE_GENERATION_ENABLED = False

# COMMENTED OUT: Initialize NanoBanana (Gemini 2.5 Flash Image)
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# image_model = genai.GenerativeModel('gemini-2.5-flash-image-preview')


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

    # COMMENTED OUT: Image generation logic (enable by setting IMAGE_GENERATION_ENABLED = True)
    # Initialize model if not already done
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    image_model = genai.GenerativeModel('gemini-2.5-flash-image-preview')

    # print("\n" + "="*60)
    # print("🔧 DEBUG: generate_style_image called")
    # print("="*60)
    # print(f"📝 Style Description: {style_description}")
    # print(f"📝 Context: {context}")

    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"🔑 API Key Found: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("❌ API Key NOT FOUND in environment")
        return "Error: GEMINI_API_KEY not found in environment"

    try:
        # Build prompt for image generation
        prompt = f"Generate a visual style example image: {style_description}"
        if context:
            prompt += f". Context: {context}"

        # print(f"💬 Full Prompt: {prompt}")
        # print("🚀 Calling NanoBanana API...")

        # Generate image using NanoBanana
        response = image_model.generate_content([prompt])

        # print("✅ API call completed")
        # print(f"📦 Response type: {type(response)}")
        # print(f"📦 Response attributes: {dir(response)}")

        # Check response structure
        if hasattr(response, 'candidates'):
            # print(f"✅ Response has candidates: {len(response.candidates)} candidates")
            if response.candidates:
                candidate = response.candidates[0]
                # print(f"📦 Candidate type: {type(candidate)}")
                # print(f"📦 Candidate attributes: {dir(candidate)}")

                if hasattr(candidate, 'content'):
                    # print(f"✅ Candidate has content")
                    # print(f"📦 Content type: {type(candidate.content)}")

                    if hasattr(candidate.content, 'parts'):
                        # print(f"✅ Content has parts: {len(candidate.content.parts)} parts")

                        for i, part in enumerate(candidate.content.parts):
                            # print(f"\n--- Part {i} ---")
                            # print(f"📦 Part type: {type(part)}")
                            # print(f"📦 Part attributes: {dir(part)}")

                            if hasattr(part, 'inline_data'):
                                # print(f"✅ Part has inline_data")
                                if part.inline_data:
                                    # print(f"📦 inline_data type: {type(part.inline_data)}")
                                    # print(f"📦 inline_data attributes: {dir(part.inline_data)}")

                                    # Create output directory if it doesn't exist
                                    output_dir = "output/style_examples"
                                    os.makedirs(output_dir, exist_ok=True)
                                    # print(f"📁 Output directory created/verified: {output_dir}")

                                    # Generate unique filename with timestamp
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    filename = f"{output_dir}/style_{timestamp}.png"
                                    # print(f"📝 Filename: {filename}")

                                    # Save image
                                    image_data = BytesIO(part.inline_data.data)
                                    img = Image.open(image_data)
                                    img.save(filename)
                                    # print(f"💾 Image saved successfully!")

                                    return f"Image generated successfully! View it here: {filename}"
                                else:
                                    print("❌ inline_data is None")
                            else:
                                print("❌ Part does not have inline_data attribute")
                                if hasattr(part, 'text'):
                                    print(f"📝 Part has text: {part.text}")
                    else:
                        print("❌ Content does not have parts")
                else:
                    print("❌ Candidate does not have content")
            else:
                print("❌ No candidates in response")
        else:
            print("❌ Response does not have candidates attribute")

        print("\n❌ No image data found in response structure")
        return "Error: No image data in response"

    except Exception as e:
        print(f"\n❌ EXCEPTION OCCURRED")
        print(f"Exception type: {type(e)}")
        print(f"Exception message: {str(e)}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
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
