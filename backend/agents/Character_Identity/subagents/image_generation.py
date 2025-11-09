"""
Image Generation Sub-Agent (Wave 3)

Generates character images using Google Gemini API including:
- Visual style profile based on all character data
- 4 image variations: portrait, full-body, action, expression
- Detailed prompts using photography/cinematic language
- Integration with character storage for image persistence
"""

import os
import json
from typing import Tuple, List
import google.generativeai as genai
from io import BytesIO
from PIL import Image

from ..schemas import CharacterKnowledgeBase, ImageGenerationOutput, GeneratedImage


async def image_generation_agent(
    kb: CharacterKnowledgeBase,
    api_key: str,
    storage  # CharacterStorage instance
) -> Tuple[ImageGenerationOutput, str]:
    """
    Generate character images using Gemini API

    Args:
        kb: Character knowledge base (requires all previous outputs)
        api_key: Google Gemini API key
        storage: CharacterStorage instance for saving images

    Returns:
        Tuple of (ImageGenerationOutput, narrative_description)
    """
    # Initialize Gemini like Entry Agent does
    genai.configure(api_key=api_key)
    image_model = genai.GenerativeModel('gemini-2.5-flash-image-preview')

    # Extract comprehensive character data
    character = kb["input_data"]["characters"][0]
    storyline = kb["input_data"]["storyline"]

    # Build visual profile from all previous outputs
    visual_context_parts = [
        f"Character Name: {character['name']}",
        f"Basic Appearance: {character['appearance']}",
        f"Story Tone: {storyline['tone']}"
    ]

    # Add personality visual cues
    if kb.get("personality"):
        p = kb["personality"]
        visual_context_parts.append(f"Personality (affects expression): {', '.join(p['core_traits'])}")
        visual_context_parts.append(f"Emotional Baseline: {p['emotional_baseline']}")

    # Add physical description
    if kb.get("physical_description"):
        pd = kb["physical_description"]
        visual_context_parts.append(f"Body Language: {pd['body_language']}")
        visual_context_parts.append(f"Movement Style: {pd['movement_style']}")

    # Add backstory context
    if kb.get("backstory_motivation"):
        b = kb["backstory_motivation"]
        if b["timeline"]:
            current_age_event = b["timeline"][-1]
            visual_context_parts.append(f"Current Context: Age {current_age_event.get('age', 'Unknown')}")

    visual_context = "\n".join(visual_context_parts)

    # Use Entry Agent's visual_style directly instead of deriving from tone
    if "visual_style" in kb["input_data"] and "description" in kb["input_data"]["visual_style"]:
        style_profile = kb["input_data"]["visual_style"]["description"]
    else:
        # Fallback if visual_style is missing (shouldn't happen but be defensive)
        style_profile = "Realistic cinematic photography with dramatic lighting, film-like quality, and attention to detail"

    # Create 4 different image prompts
    image_prompts = []

    # 1. Portrait (headshot, 1:1 aspect ratio)
    portrait_prompt = f"""A close-up portrait photograph of {character['name']}.

{visual_context}

Shot with an 85mm lens in soft natural light. Focus on facial expression capturing their {kb.get('personality', {}).get('emotional_baseline', 'complex')} nature. Professional portrait photography with depth and character.

Style: {style_profile}
Aspect ratio: 1:1 (1024x1024)
High detail, photorealistic."""

    image_prompts.append(("portrait", portrait_prompt, "1:1"))

    # 2. Full-body (standing pose, 4:3 aspect ratio)
    full_body_prompt = f"""A full-body photograph of {character['name']} standing.

{visual_context}

Capture their {kb.get('physical_description', {}).get('body_language', 'distinctive posture')} and how they inhabit space. Show their complete outfit and physical presence. Professional full-body portrait with environmental context.

Style: {style_profile}
Aspect ratio: 4:3 (1184x864)
High detail, show complete character."""

    image_prompts.append(("full_body", full_body_prompt, "4:3"))

    # 3. Action shot (character in motion, 16:9 aspect ratio)
    action_context = kb.get("story_arc", {}).get("arc_type", "their journey")
    action_prompt = f"""A dynamic photograph of {character['name']} in action, captured mid-movement.

{visual_context}

Show them engaged in a moment relevant to {action_context}. Capture motion and energy while maintaining character detail. Cinematic action photography with dramatic composition.

Style: {style_profile}
Aspect ratio: 16:9 (1344x768)
Dynamic composition, sense of motion."""

    image_prompts.append(("action", action_prompt, "16:9"))

    # 4. Expression study (close-up showing emotion, 1:1)
    key_emotion = "intensity"
    if kb.get("personality"):
        traits = kb["personality"].get("core_traits", [])
        if traits:
            key_emotion = traits[0] if len(traits) > 0 else "intensity"

    expression_prompt = f"""An intimate close-up photograph focusing on {character['name']}'s expression.

{visual_context}

Extreme close-up capturing the emotion of {key_emotion}. Focus on eyes and facial micro-expressions. Reveal their inner emotional state. Professional portrait photography with psychological depth.

Style: {style_profile}
Aspect ratio: 1:1 (1024x1024)
Intimate, emotionally revealing."""

    image_prompts.append(("expression", expression_prompt, "1:1"))

    # Generate images using Gemini (matching Entry Agent pattern)
    generated_images: List[GeneratedImage] = []

    for image_type, prompt, aspect_ratio in image_prompts:
        try:
            print(f"Generating {image_type} image...")

            # Generate image like Entry Agent does
            response = image_model.generate_content([prompt])

            # Extract image data from response (Entry Agent pattern)
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            # Convert inline_data to bytes using PIL like Entry Agent
                            image_data = BytesIO(part.inline_data.data)
                            img = Image.open(image_data)

                            # Convert PIL Image to bytes for storage
                            img_byte_arr = BytesIO()
                            img.save(img_byte_arr, format='PNG')
                            image_bytes = img_byte_arr.getvalue()

                            # Save image using storage
                            image_path = storage.save_image(
                                kb["character_id"],
                                image_type,
                                image_bytes
                            )

                            # Add to generated images
                            generated_image: GeneratedImage = {
                                "type": image_type,  # type: ignore
                                "path": image_path,
                                "prompt": prompt,
                                "approved": False
                            }
                            generated_images.append(generated_image)

                            # Show absolute path for user to view
                            absolute_path = storage.get_image_path(kb["character_id"], image_type)
                            print(f"✓ {image_type} image generated and saved")
                            print(f"  → View it here: {absolute_path}")
                            break

        except Exception as e:
            print(f"Warning: Failed to generate {image_type} image: {e}")
            # Create placeholder
            generated_image: GeneratedImage = {
                "type": image_type,  # type: ignore
                "path": f"/placeholder_{image_type}.png",
                "prompt": prompt,
                "approved": False
            }
            generated_images.append(generated_image)

    # Display summary of all generated images
    print("\n" + "="*65)
    print("📸 CHARACTER IMAGES GENERATED")
    print("="*65)
    for img in generated_images:
        if not img["path"].startswith("/placeholder"):
            abs_path = storage.get_image_path(kb["character_id"], img["type"])
            # Show relative path from backend/ for cleaner display
            rel_path = f"character_data/{kb['character_id']}/images/{img['type']}.png"
            print(f"{img['type'].upper():13} → backend/{rel_path}")
    print("\n→ Open these files to view your character images!")
    print("="*65 + "\n")

    # Create narrative description
    narrative = f"""Visual Style Profile: {style_profile}

Generated 4 character images for {character['name']}:
1. Portrait - Close-up headshot capturing their {kb.get('personality', {}).get('emotional_baseline', 'essence')}
2. Full-Body - Complete physical presence showing their {kb.get('physical_description', {}).get('body_language', 'stance')}
3. Action - Dynamic shot showing them in motion, embodying their {kb.get('story_arc', {}).get('arc_type', 'journey')}
4. Expression - Intimate close-up revealing their {key_emotion}

All images maintain visual consistency with {style_profile.lower()} aesthetic, suitable for the {storyline['tone']} tone of the story."""

    # Create output
    image_output: ImageGenerationOutput = {
        "images": generated_images,
        "style_profile": style_profile
    }

    return image_output, narrative
