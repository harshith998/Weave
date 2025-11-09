"""
Specialized subagent implementations for Scene Creator.
Each subagent is a single-purpose LLM call or API integration with specialized prompts.
"""

import os
import json
import base64
from io import BytesIO
from typing import Dict, Any, List, Optional
from anthropic import Anthropic

try:
    from google import genai
    NANO_BANANA_AVAILABLE = True
except ImportError:
    NANO_BANANA_AVAILABLE = False
    print("Warning: google-genai not installed. Nano Banana features will be unavailable.")

import sys
sys.path.append('../../..')
from utils.state_manager import read_scene, get_global_continuity


# Initialize clients
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-5-20250929"

if NANO_BANANA_AVAILABLE:
    try:
        nano_banana_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    except Exception as e:
        print(f"Warning: Failed to initialize Nano Banana client: {e}")
        nano_banana_client = None
else:
    nano_banana_client = None


# ============================================================================
# 1. CINEMATOGRAPHY DESIGNER
# ============================================================================

async def cinematography_designer(scene_description: str, options_count: int = 2) -> str:
    """
    Generate cinematography options (shot sequences, camera work, composition).

    Args:
        scene_description: What the scene is about
        options_count: Number of alternative approaches to generate (default: 2)

    Returns:
        JSON string with cinematography options
    """
    system_prompt = """You are a master cinematographer and director of photography.

Your job is to design shot sequences that tell stories visually. You understand:
- Camera movements and their emotional impact
- Shot sizes and framing principles
- The 180-degree rule and spatial continuity
- Eyeline matches and screen direction
- Composition techniques (rule of thirds, leading lines, etc.)
- How camera work creates pace and rhythm

Generate detailed, professional cinematography plans formatted as JSON."""

    user_prompt = f"""Design {options_count} distinct cinematography approaches for this scene:

{scene_description}

For each approach, provide:
1. Overall shooting style/philosophy
2. Complete shot sequence (4-8 shots) with:
   - Shot number and purpose
   - Shot size (ECU, CU, MCU, MS, WS, etc.)
   - Camera angle
   - Camera movement type and direction
   - Lens choice and depth of field
   - Composition notes
   - Duration estimate
   - Transition to next shot

Make each approach distinctly different in style, pacing, or emotional impact.

Return as JSON:
{{
  "options": [
    {{
      "name": "Approach name",
      "philosophy": "Overall style description",
      "pacing": "fast/moderate/slow",
      "shotSequence": [
        {{
          "shotNumber": "1",
          "purpose": "establishing/action/reaction/etc",
          "shotSize": "WS/MS/CU/etc",
          "cameraAngle": "eye-level/low/high/etc",
          "cameraMovement": {{"type": "static/dolly/pan/etc", "direction": "description", "speed": "slow/fast"}},
          "lens": "focal length and DOF",
          "composition": "composition techniques used",
          "duration": 5,
          "transition": "cut/fade/etc"
        }}
      ]
    }}
  ]
}}"""

    response = anthropic_client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )

    return response.content[0].text


# ============================================================================
# 2. AESTHETIC GENERATOR
# ============================================================================

async def aesthetic_generator(scene_description: str, element_type: str = "mood_board") -> str:
    """
    Generate aesthetic concepts (color palettes, lighting moods, style references).

    Args:
        scene_description: What the scene is about
        element_type: Type of aesthetic element (mood_board, color_palette, lighting_setup)

    Returns:
        JSON string with aesthetic recommendations
    """
    system_prompt = """You are a visual aesthetics specialist for film and video.

You understand:
- Color theory and emotional impact of palettes
- Lighting setups (three-point, natural, motivated, etc.)
- Color grading and LUT selection
- Film references and genre aesthetics
- How visual style supports narrative

Generate detailed aesthetic specifications formatted as JSON."""

    user_prompt = f"""Create aesthetic specifications for this scene:

{scene_description}

Focus on: {element_type}

Provide:
1. Color palette (hex codes and descriptions)
2. Lighting setup recommendations
3. Mood/atmosphere description
4. Film/visual references
5. Color grading approach
6. Specific aesthetic keywords

Return as JSON:
{{
  "colorPalette": {{
    "dominant": ["#hex", "description"],
    "accent": ["#hex", "description"],
    "mood": "emotional quality"
  }},
  "lighting": {{
    "setup": "three-point/natural/etc",
    "mood": "high-key/low-key/etc",
    "keyLight": "description",
    "atmosphere": ["effects like fog, haze, etc"]
  }},
  "style": {{
    "filmReferences": ["film names"],
    "aestheticKeywords": ["descriptive terms"],
    "grading": "color grading approach"
  }}
}}"""

    response = anthropic_client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )

    return response.content[0].text


# ============================================================================
# 3. SCENE VALIDATOR
# ============================================================================

async def scene_validator(scene_json: str, validation_phase: str = "pre") -> str:
    """
    Validate scene against continuity rules, narrative logic, and technical feasibility.

    Args:
        scene_json: Scene JSON as string
        validation_phase: "pre" (before generation) or "post" (after generation)

    Returns:
        JSON validation report
    """
    system_prompt = """You are a continuity supervisor and script supervisor.

You validate scenes for:
- Narrative coherence and logic
- Continuity rules (180-degree, screen direction, eyeline match)
- Technical feasibility
- Timeline logic
- Character consistency
- Spatial coherence

Run comprehensive checks and report issues with severity levels."""

    user_prompt = f"""Validate this scene ({validation_phase}-generation):

{scene_json}

Run checks across categories:
1. Narrative: Logic, coherence, character motivations, pacing
2. Continuity: 180-degree rule, screen direction, eyeline matches, spatial logic
3. Technical: Camera physics, lighting reality, feasibility
4. Timeline: Temporal coherence, sequence logic
5. Character: Consistency with character data (if available)

Return validation report as JSON:
{{
  "overallStatus": "approved/rejected/needs-revision",
  "checks": [
    {{
      "category": "narrative/continuity/technical/etc",
      "checkName": "specific check",
      "status": "pass/fail/warning",
      "severity": "critical/high/medium/low",
      "details": "explanation",
      "suggestedFix": "how to fix if failed"
    }}
  ],
  "blockers": ["list of critical issues"],
  "recommendations": ["list of improvements"]
}}"""

    response = anthropic_client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )

    return response.content[0].text


# ============================================================================
# 4. REFERENCE IMAGE GENERATOR (Nano Banana)
# ============================================================================

async def reference_image_generator(
    prompt: str,
    aspect_ratio: str = "16:9",
    reference_type: str = "storyboard"
) -> str:
    """
    Generate reference images using Nano Banana (Gemini 2.5 Flash Image).

    Args:
        prompt: Detailed image generation prompt
        aspect_ratio: Image aspect ratio (16:9, 21:9, 9:16, 1:1, etc.)
        reference_type: Type of reference (storyboard, mood_board, composition, etc.)

    Returns:
        JSON with image data (base64) and metadata
    """
    if not NANO_BANANA_AVAILABLE or nano_banana_client is None:
        return json.dumps({
            "error": "Nano Banana (google-genai) not available",
            "message": "Install google-genai package to enable image generation"
        })

    try:
        # Build detailed prompt based on reference type
        if reference_type == "storyboard":
            full_prompt = f"Professional film storyboard frame: {prompt}. Cinematic composition, clear staging, {aspect_ratio} aspect ratio."
        elif reference_type == "mood_board":
            full_prompt = f"Cinematic mood board reference image: {prompt}. Atmospheric, stylized, {aspect_ratio} format."
        elif reference_type == "composition":
            full_prompt = f"Cinematography composition example: {prompt}. Professional framing, {aspect_ratio} format."
        else:
            full_prompt = prompt

        # Generate image
        response = nano_banana_client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[full_prompt],
            config={
                "responseModalities": ["Image"],
                "imageConfig": {"aspectRatio": aspect_ratio}
            }
        )

        # Extract image data
        image_data = None
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data'):
                image_data = part.inline_data.data
                break

        if image_data:
            return json.dumps({
                "success": True,
                "referenceType": reference_type,
                "aspectRatio": aspect_ratio,
                "prompt": full_prompt,
                "imageData": image_data,  # base64 encoded
                "mimeType": "image/png"
            })
        else:
            return json.dumps({
                "error": "No image generated",
                "message": "Nano Banana response did not contain image data"
            })

    except Exception as e:
        return json.dumps({
            "error": "Image generation failed",
            "message": str(e)
        })


# ============================================================================
# 5. TIMELINE VALIDATOR
# ============================================================================

async def timeline_validator(
    scene_json: str,
    project_id: str = "default",
    scene_number: str = "1"
) -> str:
    """
    Validate scene against global timeline and sequence logic.

    Args:
        scene_json: Scene JSON as string
        project_id: Project identifier
        scene_number: Scene number

    Returns:
        JSON validation report
    """
    # Get global continuity state
    global_continuity = get_global_continuity(project_id)
    timeline = global_continuity.get("timeline", [])

    system_prompt = """You are a timeline and continuity specialist.

You validate:
- Temporal logic and coherence
- Scene sequence order
- Time passage consistency
- Flashback/flash-forward logic
- Parallel storylines
- Timeline paradoxes

Check for logical inconsistencies and timeline errors."""

    user_prompt = f"""Validate this scene against the global timeline:

SCENE:
{scene_json}

GLOBAL TIMELINE:
{json.dumps(timeline, indent=2)}

SCENE NUMBER: {scene_number}

Check:
1. Does time progression make sense?
2. Are there temporal paradoxes?
3. Does this fit logically in the timeline sequence?
4. Are character states consistent with timeline position?
5. Do location/environment states match timeline?

Return as JSON:
{{
  "valid": true/false,
  "issues": [
    {{
      "type": "temporal_paradox/sequence_error/etc",
      "severity": "critical/high/medium/low",
      "description": "what's wrong",
      "suggestion": "how to fix"
    }}
  ],
  "timelinePosition": "where this fits in timeline",
  "recommendations": ["timeline improvements"]
}}"""

    response = anthropic_client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )

    return response.content[0].text


# ============================================================================
# 6. CHECKPOINT MANAGER
# ============================================================================

async def checkpoint_manager(
    checkpoint_type: str,
    data: Dict[str, Any],
    scene_id: str,
    agent_mode: str
) -> str:
    """
    Create and format checkpoint for sending to orchestrator and combiner.

    Args:
        checkpoint_type: Type (proposal, validation, approval-request, progress, completion, error)
        data: Checkpoint data dictionary
        scene_id: Scene identifier
        agent_mode: Current agent mode

    Returns:
        Formatted checkpoint JSON string
    """
    from datetime import datetime

    checkpoint = {
        "checkpointType": checkpoint_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sceneId": scene_id,
        "agentId": "scene_creator",
        "agentMode": agent_mode,
        "data": data
    }

    # Format as JSON string for transmission
    return json.dumps(checkpoint, indent=2)


# ============================================================================
# 7. VISUAL CONTINUITY CHECKER
# ============================================================================

async def visual_continuity_checker(
    generated_video_data: str,
    scene_json: str,
    character_references: Optional[str] = None
) -> str:
    """
    Analyze generated video for visual continuity and consistency.

    Args:
        generated_video_data: Information about generated video clips
        scene_json: Original scene specification
        character_references: Character appearance data (from Character_Identity agent)

    Returns:
        JSON analysis report
    """
    system_prompt = """You are a visual continuity and quality control specialist.

You analyze generated video content for:
- Visual consistency across clips
- Character appearance consistency
- Lighting continuity
- Color consistency
- Environmental continuity
- Technical quality issues
- Adherence to scene specifications

Provide detailed analysis with specific issues and quality scores."""

    user_prompt = f"""Analyze these generated video clips for visual continuity:

SCENE SPECIFICATION:
{scene_json}

GENERATED VIDEO DATA:
{generated_video_data}

CHARACTER REFERENCES:
{character_references if character_references else "None provided"}

Check:
1. Character appearance consistency across clips
2. Lighting continuity
3. Color grading consistency
4. Environmental/prop consistency
5. Technical quality (resolution, artifacts, etc.)
6. Adherence to scene specifications

Return as JSON:
{{
  "overallQuality": "pass/fail/warning",
  "qualityScore": 8.5,
  "issues": [
    {{
      "category": "character/lighting/color/etc",
      "severity": "critical/high/medium/low",
      "clipNumber": 2,
      "description": "what's wrong",
      "timestamp": "if applicable",
      "suggestedFix": "how to fix"
    }}
  ],
  "characterConsistency": "pass/fail/warning",
  "visualContinuity": "pass/fail/warning",
  "technicalQuality": "pass/fail/warning",
  "retakeRequired": false,
  "retakeReasons": ["if true, list reasons"]
}}"""

    response = anthropic_client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )

    return response.content[0].text
