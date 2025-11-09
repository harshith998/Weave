"""
Storage layer for Character Development System

Handles JSON persistence of character data, checkpoints, and images.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import uuid

from .schemas import (
    EntryAgentOutput,
    Checkpoint,
    FinalCharacterProfile,
    CharacterKnowledgeBase
)


class CharacterStorage:
    """Manages file-based storage for character development data"""

    def __init__(self, base_path: str = "./backend/character_data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_character_dir(self, character_id: str) -> Path:
        """Get directory path for a character"""
        char_dir = self.base_path / character_id
        char_dir.mkdir(parents=True, exist_ok=True)
        return char_dir

    def _get_checkpoints_dir(self, character_id: str) -> Path:
        """Get checkpoints directory for a character"""
        checkpoints_dir = self._get_character_dir(character_id) / "checkpoints"
        checkpoints_dir.mkdir(parents=True, exist_ok=True)
        return checkpoints_dir

    def _get_images_dir(self, character_id: str) -> Path:
        """Get images directory for a character"""
        images_dir = self._get_character_dir(character_id) / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        return images_dir

    # ========================================================================
    # CHARACTER CRUD OPERATIONS
    # ========================================================================

    def create_character(self, input_data: EntryAgentOutput, mode: str = "balanced") -> str:
        """
        Create a new character development session

        Args:
            input_data: Output from Entry Agent
            mode: Development mode (fast/balanced/deep)

        Returns:
            character_id: UUID of created character
        """
        character_id = str(uuid.uuid4())
        char_dir = self._get_character_dir(character_id)

        # Save input data
        input_path = char_dir / "input.json"
        with open(input_path, 'w') as f:
            json.dump(input_data, f, indent=2)

        # Initialize metadata
        # Determine total checkpoints based on image generation setting
        IMAGE_GENERATION_ENABLED = os.getenv("IMAGE_GENERATION_ENABLED", "false").lower() == "true"
        total_checkpoints = 8 if IMAGE_GENERATION_ENABLED else 7

        metadata = {
            "character_id": character_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "in_progress",
            "mode": mode,
            "current_wave": 1,
            "current_checkpoint": 0,
            "completed_checkpoints": 0,
            "total_checkpoints": total_checkpoints,
            "regenerations": 0
        }

        metadata_path = char_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Initialize character knowledge base
        kb: CharacterKnowledgeBase = {
            "character_id": character_id,
            "input_data": input_data,
            "mode": mode,  # type: ignore
            "personality": None,
            "backstory_motivation": None,
            "voice_dialogue": None,
            "physical_description": None,
            "story_arc": None,
            "relationships": None,
            "image_generation": None,
            "current_wave": 1,
            "current_checkpoint": 0,
            "agent_statuses": {
                "personality": {"status": "pending", "wave": 1},
                "backstory_motivation": {"status": "pending", "wave": 1},
                "voice_dialogue": {"status": "pending", "wave": 2},
                "physical_description": {"status": "pending", "wave": 2},
                "story_arc": {"status": "pending", "wave": 2},
                "relationships": {"status": "pending", "wave": 3},
                "image_generation": {"status": "pending", "wave": 3}
            }
        }

        kb_path = char_dir / "knowledge_base.json"
        with open(kb_path, 'w') as f:
            json.dump(kb, f, indent=2)

        return character_id

    def load_character_kb(self, character_id: str) -> CharacterKnowledgeBase:
        """Load character knowledge base"""
        char_dir = self._get_character_dir(character_id)
        kb_path = char_dir / "knowledge_base.json"

        if not kb_path.exists():
            raise FileNotFoundError(f"Character {character_id} not found")

        with open(kb_path, 'r') as f:
            return json.load(f)

    def save_character_kb(self, kb: CharacterKnowledgeBase) -> None:
        """Save character knowledge base"""
        char_dir = self._get_character_dir(kb["character_id"])
        kb_path = char_dir / "knowledge_base.json"

        with open(kb_path, 'w') as f:
            json.dump(kb, f, indent=2)

    def load_metadata(self, character_id: str) -> Dict:
        """Load character metadata"""
        char_dir = self._get_character_dir(character_id)
        metadata_path = char_dir / "metadata.json"

        if not metadata_path.exists():
            raise FileNotFoundError(f"Character {character_id} metadata not found")

        with open(metadata_path, 'r') as f:
            return json.load(f)

    def save_metadata(self, character_id: str, metadata: Dict) -> None:
        """Save character metadata"""
        char_dir = self._get_character_dir(character_id)
        metadata_path = char_dir / "metadata.json"

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    # ========================================================================
    # CHECKPOINT OPERATIONS
    # ========================================================================

    def save_checkpoint(self, character_id: str, checkpoint: Checkpoint) -> None:
        """Save a checkpoint"""
        checkpoints_dir = self._get_checkpoints_dir(character_id)

        # Filename: 01_personality.json, 02_backstory.json, etc.
        filename = f"{checkpoint['checkpoint_number']:02d}_{checkpoint['agent']}.json"
        checkpoint_path = checkpoints_dir / filename

        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint, f, indent=2)

    def load_checkpoint(self, character_id: str, checkpoint_number: int) -> Optional[Checkpoint]:
        """Load a specific checkpoint"""
        checkpoints_dir = self._get_checkpoints_dir(character_id)

        # Find file matching checkpoint number
        for file_path in checkpoints_dir.glob(f"{checkpoint_number:02d}_*.json"):
            with open(file_path, 'r') as f:
                return json.load(f)

        return None

    def load_all_checkpoints(self, character_id: str) -> Dict[int, Checkpoint]:
        """Load all checkpoints for a character"""
        checkpoints_dir = self._get_checkpoints_dir(character_id)
        checkpoints = {}

        for file_path in sorted(checkpoints_dir.glob("*.json")):
            with open(file_path, 'r') as f:
                checkpoint = json.load(f)
                checkpoints[checkpoint["checkpoint_number"]] = checkpoint

        return checkpoints

    # ========================================================================
    # IMAGE OPERATIONS
    # ========================================================================

    def save_image(self, character_id: str, image_type: str, image_data: bytes) -> str:
        """
        Save a generated image

        Args:
            character_id: Character UUID
            image_type: Type of image (portrait, full_body, action, expression)
            image_data: Raw image bytes

        Returns:
            Relative path to saved image
        """
        images_dir = self._get_images_dir(character_id)
        image_path = images_dir / f"{image_type}.png"

        with open(image_path, 'wb') as f:
            f.write(image_data)

        # Return relative path for API responses
        return f"/character_data/{character_id}/images/{image_type}.png"

    def get_image_path(self, character_id: str, image_type: str) -> Path:
        """Get absolute path to an image"""
        images_dir = self._get_images_dir(character_id)
        return images_dir / f"{image_type}.png"

    # ========================================================================
    # FINAL OUTPUT
    # ========================================================================

    def save_final_profile(self, character_id: str, profile: FinalCharacterProfile) -> None:
        """Save final character profile"""
        char_dir = self._get_character_dir(character_id)
        final_path = char_dir / "final_profile.json"

        with open(final_path, 'w') as f:
            json.dump(profile, f, indent=2)

        # Update metadata
        metadata = self.load_metadata(character_id)
        metadata["status"] = "completed"
        metadata["completed_at"] = datetime.utcnow().isoformat()
        self.save_metadata(character_id, metadata)

    def load_final_profile(self, character_id: str) -> Optional[FinalCharacterProfile]:
        """Load final character profile"""
        char_dir = self._get_character_dir(character_id)
        final_path = char_dir / "final_profile.json"

        if not final_path.exists():
            return None

        with open(final_path, 'r') as f:
            return json.load(f)

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def character_exists(self, character_id: str) -> bool:
        """Check if character exists"""
        return self._get_character_dir(character_id).exists()

    def delete_character(self, character_id: str) -> None:
        """Delete all character data (use with caution)"""
        import shutil
        char_dir = self._get_character_dir(character_id)
        if char_dir.exists():
            shutil.rmtree(char_dir)

    def list_characters(self) -> list[str]:
        """List all character IDs"""
        return [d.name for d in self.base_path.iterdir() if d.is_dir()]
