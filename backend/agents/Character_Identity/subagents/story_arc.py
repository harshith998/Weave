"""
Story Arc Sub-Agent (Wave 2)

Develops character's narrative function and transformation including:
- Character role classification (protagonist, antagonist, mentor, etc.)
- Character arc type and transformation beats
- Story function in different acts/scenes
- How they fit into overall plot structure
"""

import json
from typing import Tuple
from anthropic import AsyncAnthropic  # FIX: Use AsyncAnthropic for async functions

from ..schemas import CharacterKnowledgeBase, StoryArcOutput, TransformationBeat


async def story_arc_agent(
    kb: CharacterKnowledgeBase,
    api_key: str
) -> Tuple[StoryArcOutput, str]:
    """
    Generate detailed story arc and narrative function profile

    Args:
        kb: Character knowledge base (requires Wave 1 outputs)
        api_key: Anthropic API key

    Returns:
        Tuple of (StoryArcOutput, narrative_description)
    """
    client = AsyncAnthropic(api_key=api_key)  # FIX: Use AsyncAnthropic
    model = "claude-haiku-4-5-20251001"

    # Extract data
    character = kb["input_data"]["characters"][0]
    storyline = kb["input_data"]["storyline"]
    mode = kb.get("mode", "balanced")

    # Build rich context from all previous outputs
    context_blocks = []

    if kb.get("personality"):
        p = kb["personality"]
        context_blocks.append(f"""PERSONALITY:
- Core Traits: {", ".join(p["core_traits"])}
- Fears: {", ".join(p["fears"])}
- Internal State: {p["emotional_baseline"]}""")

    if kb.get("backstory_motivation"):
        b = kb["backstory_motivation"]
        # Handle internal_conflicts safely - can be list of strings or dicts
        conflicts = b.get("internal_conflicts", [])
        if conflicts and isinstance(conflicts[0], dict):
            conflict_str = ", ".join([str(c) for c in conflicts])
        else:
            conflict_str = ", ".join(conflicts) if conflicts else "None specified"

        context_blocks.append(f"""MOTIVATION:
- Surface Goal: {b["goals"].get("surface", "Unknown")}
- Deep Need: {b["goals"].get("deep", "Unknown")}
- Internal Conflicts: {conflict_str}""")

    full_context = "\n\n".join(context_blocks)

    system_prompt = f"""You are a narrative structure expert designing a character's story arc for a {storyline["tone"]} story.

Your task is to define this character's NARRATIVE FUNCTION and TRANSFORMATION ARC throughout the story.

CHARACTER OVERVIEW:
- Name: {character["name"]}
- Basic Role: {character["role"]}
- Story Context: {storyline["overview"]}
- Story Tone: {storyline["tone"]}
- Scenes in Story: {", ".join([
    scene.get('title', scene.get('description', 'Untitled')[:50] + '...' if len(scene.get('description', '')) > 50 else scene.get('description', 'Untitled'))
    if isinstance(scene, dict) else scene
    for scene in storyline.get("scenes", [])[:5]
])}

{full_context}

DEPTH MODE: {mode}

OUTPUT REQUIREMENTS:

1. ROLE (specific classification)
   - Protagonist, Antagonist, Deuteragonist (secondary main), Mentor, Guardian, Trickster, Herald, Shapeshifter, Shadow, etc.
   - Can be multiple roles (e.g., "Protagonist with Mentor elements")
   - Explain what narrative function they serve

2. ARC TYPE (specific arc classification)
   - Examples: Positive Change Arc (growth), Corruption Arc (fall), Flat Arc (unchanging but changes world), Disillusionment Arc, Redemption Arc, Coming of Age, etc.
   - Be SPECIFIC to this character's journey
   - Explain the transformation they undergo (or don't undergo)

3. TRANSFORMATION BEATS (4-6 key moments)
   - Map to story structure: Act 1, Act 2 (first half), Act 2 (second half), Act 3
   - Each beat is a moment where character changes or faces a test
   - Format: [{{"act": 1, "beat": "Description of moment"}}, ...]
   - Should build logically from personality/motivation

4. SCENE PRESENCE (list of scenes)
   - Which scenes from the storyline is this character crucial to?
   - What role do they play in each scene?
   - When do they appear vs. when are they absent?

IMPORTANT:
- Make arc SPECIFIC to THIS character, not generic hero's journey
- Connect transformation beats to internal conflicts
- Ensure arc aligns with personality and motivation
- Consider story tone when defining arc type

First, provide a rich NARRATIVE description of their story arc (2-3 paragraphs explaining their transformation and role).
Then, provide the STRUCTURED data in JSON format.

Format:
NARRATIVE:
[Your narrative here]

STRUCTURED:
{{
  "role": "Specific role classification",
  "arc_type": "Specific arc type",
  "transformation_beats": [
    {{"act": 1, "beat": "Description..."}},
    {{"act": 2, "beat": "Description..."}},
    ...
  ],
  "scene_presence": ["Scene 1", "Scene 2", ...]
}}"""

    # Make API call (FIX: Add await for async client)
    response = await client.messages.create(
        model=model,
        max_tokens=4000,
        temperature=0.7,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": f"Create a detailed story arc profile for {character['name']}. Provide both narrative and structured output."
        }]
    )

    # Parse response
    content = response.content[0].text

    # Split narrative and structured
    parts = content.split("STRUCTURED:")
    if len(parts) == 2:
        narrative = parts[0].replace("NARRATIVE:", "").strip()
        structured_text = parts[1].strip()
    else:
        narrative = content[:content.find("{")].strip() if "{" in content else content
        structured_text = content[content.find("{"):content.rfind("}")+1] if "{" in content else "{}"

    # Parse JSON
    try:
        if "```json" in structured_text:
            structured_text = structured_text.split("```json")[1].split("```")[0]
        elif "```" in structured_text:
            structured_text = structured_text.split("```")[1].split("```")[0]

        structured_data = json.loads(structured_text)
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse story arc JSON: {e}")
        structured_data = {
            "role": "Unknown",
            "arc_type": "Unknown",
            "transformation_beats": [{"act": 1, "beat": "Unknown"}],
            "scene_presence": []
        }

    # Create output
    story_arc_output: StoryArcOutput = {
        "role": structured_data.get("role", ""),
        "arc_type": structured_data.get("arc_type", ""),
        "transformation_beats": structured_data.get("transformation_beats", []),
        "scene_presence": structured_data.get("scene_presence", [])
    }

    return story_arc_output, narrative
