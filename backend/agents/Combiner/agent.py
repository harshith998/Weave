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
import base64
import os
from pathlib import Path


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

    def _get_character_uuid(self, character_name: str) -> Optional[str]:
        """Get character UUID from name using state mapping."""
        from utils.state_manager import get_character_uuid
        return get_character_uuid(character_name, self.project_id)

    def _collect_images_for_chunk(
        self,
        chunk: Dict[str, Any],
        scene_number: int,
        previous_frame_path: Optional[str] = None
    ) -> List[str]:
        """
        Collect all reference images for this chunk.

        Args:
            chunk: Chunk dict with character names
            scene_number: Which scene (1-4)
            previous_frame_path: Path to last frame of previous chunk

        Returns:
            List of valid image paths (only existing files)
        """
        image_paths = []
        character_names = chunk.get('characters', [])

        # 1. Add character portrait images
        for char_name in character_names:
            char_uuid = self._get_character_uuid(char_name)
            if char_uuid:
                # Use portrait.png instead of reference_image.png
                portrait_path = f"backend/character_data/{char_uuid}/images/portrait.png"
                if os.path.exists(portrait_path):
                    image_paths.append(portrait_path)
                else:
                    print(f"   ⚠️  Character image not found: {portrait_path}")
            else:
                print(f"   ⚠️  Character UUID not found for: {char_name}")

        # 2. Add style image from Entry Agent
        from utils.state_manager import read_storyline
        storyline = read_storyline(self.project_id)
        if storyline:
            visual_style = storyline.get('visual_style', {})
            style_image_path = visual_style.get('image_path', '')
            if style_image_path and os.path.exists(style_image_path):
                image_paths.append(style_image_path)
            elif style_image_path:
                # Try with backend/ prefix
                backend_style_path = f"backend/{style_image_path}"
                if os.path.exists(backend_style_path):
                    image_paths.append(backend_style_path)

        # 3. Add previous frame if available (for continuity)
        if previous_frame_path and os.path.exists(previous_frame_path):
            image_paths.append(previous_frame_path)

        return image_paths

    def _save_video_from_veo(
        self,
        veo_json_response: str,
        scene_number: int,
        chunk_number: int
    ) -> Optional[str]:
        """
        Parse Veo JSON response and save video to file.

        Args:
            veo_json_response: JSON string from veo_video_generator
            scene_number: Scene number (1-4)
            chunk_number: Chunk number (1-4)

        Returns:
            Absolute path to saved video file, or None if error
        """
        try:
            result = json.loads(veo_json_response)

            if not result.get('success'):
                error_msg = result.get('error', 'Unknown error')
                print(f"   ✗ Veo generation failed: {error_msg}")
                return None

            # Decode base64 video data
            video_base64 = result.get('videoData', '')
            if not video_base64:
                print(f"   ✗ No video data in response")
                return None

            video_bytes = base64.b64decode(video_base64)

            # Create output directory
            output_dir = Path("backend/output/videos")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save video file
            video_filename = f"scene_{scene_number}_chunk_{chunk_number}.mp4"
            video_path = output_dir / video_filename

            with open(video_path, 'wb') as f:
                f.write(video_bytes)

            # Return absolute path
            abs_path = video_path.resolve()
            return str(abs_path)

        except Exception as e:
            print(f"   ✗ Error saving video: {str(e)}")
            return None

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

        # Generate video for each chunk - ONE AT A TIME with visible progress
        generated_videos = []
        previous_frame = None  # Track previous frame for continuity

        for i, chunk in enumerate(chunks, 1):
            print(f"\n{'─'*60}")
            print(f"📍 CHUNK {i}/{len(chunks)} ({chunk['start_time']}s - {chunk['end_time']}s)")
            print(f"{'─'*60}")

            # Step 1: Generate prompt using LLM
            print(f"\n⏳ Generating video prompt with LLM...")
            prompt = await self.create_video_prompt(chunk, scene_number)

            print(f"\n🎬 GENERATED PROMPT:")
            print(f"{'─'*60}")
            print(f"{prompt}")
            print(f"{'─'*60}")

            # Step 2: Collect reference images
            print(f"\n📸 Collecting reference images...")
            image_paths = self._collect_images_for_chunk(chunk, scene_number, previous_frame)
            print(f"   • Found {len(image_paths)} reference image(s)")

            # Step 3: Call Veo video generator
            print(f"\n📹 Calling Veo video generator...")
            print(f"   • Duration: 8 seconds")
            print(f"   • Resolution: 720p")
            print(f"   • Model: veo-3.1-fast-generate-preview")

            try:
                # Import and call Veo
                from video_test.veo_video_generator import veo_video_generator

                veo_response = await veo_video_generator(
                    prompt=prompt,
                    image_paths=image_paths,
                    duration_seconds=8,
                    resolution="720p",
                    model="veo-3.1-fast-generate-preview"
                )

                # Step 4: Save video to file
                print(f"\n💾 Saving video...")
                video_path = self._save_video_from_veo(veo_response, scene_number, i)

                if video_path:
                    # Make path clickable in terminal (file:// protocol for VSCode)
                    file_url = f"file://{video_path}"
                    print(f"\n✅ CLIP {i}/{len(chunks)} COMPLETE")
                    print(f"   📁 Video saved: {video_path}")
                    print(f"   🔗 Click to open: {file_url}")

                    # Parse metadata
                    result = json.loads(veo_response)
                    metadata = result.get('metadata', {})
                    cost = metadata.get('estimatedCost', 'N/A')
                    gen_time = metadata.get('generationTime', 'N/A')
                    print(f"   💰 Est. cost: {cost}")
                    print(f"   ⏱️  Generation time: {gen_time}")

                    generated_videos.append({
                        "chunk": i,
                        "prompt": prompt,
                        "duration": "8s",
                        "video_path": video_path
                    })

                    # TODO: Extract last frame for next chunk continuity
                    # previous_frame = self._extract_last_frame(video_path, scene_number, i)
                else:
                    print(f"\n⚠️  CLIP {i}/{len(chunks)} FAILED - Skipping to next chunk")

            except Exception as e:
                print(f"\n✗ Error generating video: {str(e)}")
                import traceback
                traceback.print_exc()
                print(f"\n⚠️  CLIP {i}/{len(chunks)} FAILED - Skipping to next chunk")

            # Add visual separator between clips
            if i < len(chunks):
                print(f"\n{'═'*60}")
                print(f"Moving to next chunk...")
                print(f"{'═'*60}")

        # Summary
        print(f"\n{'█'*60}")
        print(f"✅ SCENE {scene_number} COMPLETE - All {len(chunks)} clips generated!")
        print(f"{'█'*60}\n")

        return f"✓ Scene {scene_number}: Generated {len(chunks)} video clips ({len(chunks) * 8}s total)"

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
