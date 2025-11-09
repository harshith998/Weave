"""
Combiner Agent (Level 4)

Takes scene JSON from Scene Creator + character data from Character Identity
and creates concise 2-paragraph video generation prompts.

This agent:
1. Receives scene JSON (8-second scene specification)
2. Pulls relevant character appearance data
3. Generates 2-paragraph prompt for Veo
4. Calls Veo video generator with images
5. Handles user feedback and regeneration
"""

from typing import List, Dict, Any, Optional
from anthropic import AsyncAnthropic
from agent_types import AgentLevel
import json


class CombinerAgent:
    """
    Combiner Agent (Level 4)

    Creates final video prompts by combining scene specs + character data.
    Calls Veo video generation with images and handles feedback loops.
    """

    def __init__(self, api_key: str, level: AgentLevel, project_id: str = "default"):
        """
        Initialize Combiner Agent

        Args:
            api_key: Anthropic API key
            level: AgentLevel enum (should be AgentLevel.Combiner)
            project_id: Project identifier
        """
        self.anthropic_api_key = api_key
        self.level = level
        self.project_id = project_id
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"  # Sonnet for quality prompt generation

        # Track generated videos and prompts
        self.current_scene_number = None
        self.current_prompt = None
        self.last_video_path = None
        self.last_frame_path = None

    async def run(self, user_input: str, conversation_history: List[Dict[str, str]]) -> str:
        """
        Main execution method

        Args:
            user_input: User's message or command
            conversation_history: Previous conversation turns

        Returns:
            Agent's response string
        """
        # Check if this is a scene generation command
        if user_input.startswith("generate_scene_"):
            scene_number = int(user_input.split("_")[-1])
            return await self._generate_scene_videos(scene_number)

        # Default fallback
        return f"Combiner Agent received: {user_input}\n\nReady to generate video prompts!"

    async def create_video_prompt(
        self,
        chunk: Dict[str, Any],
        scene_number: int
    ) -> str:
        """
        Create a concise 2-paragraph video generation prompt for an 8s chunk.

        Args:
            chunk: Chunk dict with description, characters, setting, mood
            scene_number: Which scene (1-4)

        Returns:
            2-paragraph prompt for video generation
        """
        # Build prompt using LLM
        system_prompt = """You are a video generation prompt specialist for Veo video generation.

Your task: Convert a scene chunk specification into a concise, vivid 2-paragraph prompt.

PARAGRAPH 1: The action and characters
- What happens in this 8-second chunk (visual action)
- Who is present (brief character descriptions if needed)
- Keep it vivid and specific
- Focus on what's visually happening

PARAGRAPH 2: Cinematography and aesthetic
- Camera work (angle, movement)
- Lighting and color
- Mood and atmosphere

Keep each paragraph to 2-3 sentences. Be concise but descriptive. This is for an 8-second video clip."""

        messages = [
            {
                "role": "user",
                "content": f"""Create a 2-paragraph video generation prompt for this 8-second chunk:

Chunk: {chunk['chunk_number']}/4
Time: {chunk['start_time']}s - {chunk['end_time']}s
Description: {chunk['description']}
Characters: {', '.join(chunk['characters'])}
Setting: {chunk['setting']}
Mood: {chunk['mood']}

Scene number: {scene_number}/4
Duration: 8 seconds"""
            }
        ]

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=messages
        )

        # Extract text
        text_content = [block.text for block in response.content if hasattr(block, "text")]
        prompt = " ".join(text_content)

        self.current_prompt = prompt
        self.current_scene_number = scene_number

        return prompt

    async def generate_video(
        self,
        prompt: str,
        scene_number: int,
        character_ids: List[str],
        style_image_path: str,
        previous_frame_path: Optional[str] = None
    ) -> str:
        """
        Generate video using Veo with images.

        Args:
            prompt: 2-paragraph video prompt
            scene_number: Which scene (1-4)
            character_ids: List of character UUIDs appearing in this scene
            style_image_path: Path to style reference image
            previous_frame_path: Path to last frame of previous scene (if scene > 1)

        Returns:
            Path to generated video file
        """
        # Import Veo generator
        from video_test.veo_video_generator import veo_video_generator

        # Collect character reference images
        image_paths = []

        # Add character images
        for char_id in character_ids:
            char_img_path = f"character_data/{char_id}/reference_image.png"
            # TODO: Check if file exists
            image_paths.append(char_img_path)

        # Add style image
        if style_image_path:
            image_paths.append(style_image_path)

        # Add previous frame if not scene 1
        if scene_number > 1 and previous_frame_path:
            image_paths.append(previous_frame_path)

        # Call Veo
        video_path = await veo_video_generator(
            prompt=prompt,
            image_paths=image_paths,
            duration_seconds=8,
            resolution="720p",
            model="veo-3.1-fast-generate-preview"
        )

        self.last_video_path = video_path

        # TODO: Extract last frame for next scene

        return video_path

    async def _generate_scene_videos(self, scene_number: int) -> str:
        """
        Generate videos for a single 30s scene by subdividing into 8s chunks.

        Args:
            scene_number: Which scene (1-4)

        Returns:
            Summary of generation
        """
        from utils.state_manager import read_storyline

        # Read storyline from state
        storyline = read_storyline(self.project_id)
        if not storyline:
            return "Error: No storyline found in state. Please complete Entry Agent first."

        scenes = storyline.get('scenes', [])
        if scene_number < 1 or scene_number > len(scenes):
            return f"Error: Scene {scene_number} not found. Only {len(scenes)} scenes available."

        # Get the scene (scene_number is 1-indexed, list is 0-indexed)
        scene = scenes[scene_number - 1]

        print(f"📋 Scene {scene_number}: {scene.get('title', 'Untitled')}")
        print(f"   Duration: {scene.get('duration', '30s')}")
        print(f"   Description: {scene.get('description', '')[:100]}...")
        print(f"\n🔧 Subdividing 30s scene into ~4 × 8s video chunks...\n")

        # Subdivide scene into ~4 chunks (simple subdivision for now)
        chunks = await self._subdivide_scene(scene)

        print(f"✓ Created {len(chunks)} chunks for this scene\n")

        # Generate video for each chunk
        generated_videos = []
        for i, chunk in enumerate(chunks, 1):
            print(f"\n{'─'*60}")
            print(f"CHUNK {i}/{len(chunks)} ({chunk['start_time']}s - {chunk['end_time']}s)")
            print(f"{'─'*60}")

            # Generate prompt using LLM
            prompt = await self.create_video_prompt(chunk, scene_number)

            print(f"\n🎬 GENERATED PROMPT:")
            print(f"{prompt}")
            print(f"\n📹 Calling Veo video generator...")

            # For now, just show the prompt - actual Veo integration comes next
            print(f"   [Veo integration pending - prompt generated successfully]")

            generated_videos.append({
                "chunk": i,
                "prompt": prompt,
                "duration": "8s"
            })

        return f"✓ Scene {scene_number} subdivided into {len(chunks)} chunks. Prompts generated!"

    async def _subdivide_scene(self, scene: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Subdivide a 30s scene into ~4 × 8s chunks.

        For now, simple equal subdivision. Later, this could be smarter
        based on narrative beats.

        Args:
            scene: Scene dict from storyline

        Returns:
            List of chunk dicts with start/end times and descriptions
        """
        # Simple subdivision: 4 equal chunks of 7.5s each (30s / 4)
        chunks = []
        chunk_duration = 8  # seconds
        num_chunks = 4

        for i in range(num_chunks):
            start_time = i * chunk_duration
            end_time = min((i + 1) * chunk_duration, 30)

            chunks.append({
                "chunk_number": i + 1,
                "start_time": start_time,
                "end_time": end_time,
                "description": scene.get('description', ''),  # Full scene description for now
                "characters": scene.get('characters_involved', []),
                "setting": scene.get('setting', ''),
                "mood": scene.get('mood', '')
            })

        return chunks
