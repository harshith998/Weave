"""
State manager for handling JSON-based project and scene data.

Provides thread-safe file operations for reading/writing:
- Project state (mode, global continuity, metadata)
- Scene data (individual scene JSONs)
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import threading
from datetime import datetime

# Paths
BACKEND_DIR = Path(__file__).parent.parent
STATE_DIR = BACKEND_DIR / "state"
PROJECTS_DIR = STATE_DIR / "projects"
SCENES_DIR = STATE_DIR / "scenes"

# Thread lock for file operations
_file_lock = threading.Lock()


def ensure_directories():
    """Ensure state directories exist."""
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    SCENES_DIR.mkdir(parents=True, exist_ok=True)


def get_project_state_path(project_id: str = "default") -> Path:
    """Get path to project state JSON file."""
    ensure_directories()
    return PROJECTS_DIR / f"{project_id}_state.json"


def get_scene_path(project_id: str, scene_number: str) -> Path:
    """Get path to scene JSON file."""
    ensure_directories()
    return SCENES_DIR / f"{project_id}_scene_{scene_number}.json"


def read_project_state(project_id: str = "default") -> Dict[str, Any]:
    """
    Read project state JSON.

    Args:
        project_id: Project identifier (default: "default" for single-user)

    Returns:
        Project state dictionary, or empty structure if not found
    """
    path = get_project_state_path(project_id)

    with _file_lock:
        if not path.exists():
            # Return default project state structure
            return {
                "projectId": project_id,
                "createdAt": datetime.utcnow().isoformat() + "Z",
                "lastModified": datetime.utcnow().isoformat() + "Z",
                "currentMode": "creative_overview",  # Default mode
                "sceneCount": 0,
                "globalContinuity": {
                    "timeline": [],
                    "characters": {},
                    "locations": {},
                    "lastSceneEndFrame": None
                },
                "metadata": {}
            }

        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading project state: {e}")
            return {}


def write_project_state(state: Dict[str, Any], project_id: str = "default") -> bool:
    """
    Write project state JSON.

    Args:
        state: Project state dictionary
        project_id: Project identifier

    Returns:
        True if successful, False otherwise
    """
    path = get_project_state_path(project_id)

    # Update lastModified timestamp
    state["lastModified"] = datetime.utcnow().isoformat() + "Z"

    with _file_lock:
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error writing project state: {e}")
            return False


def update_project_mode(mode: str, project_id: str = "default") -> bool:
    """
    Update the current mode in project state.

    Args:
        mode: Mode name (creative_overview, analytical, deep_dive)
        project_id: Project identifier

    Returns:
        True if successful
    """
    state = read_project_state(project_id)
    state["currentMode"] = mode
    return write_project_state(state, project_id)


def read_scene(project_id: str, scene_number: str) -> Optional[Dict[str, Any]]:
    """
    Read scene JSON.

    Args:
        project_id: Project identifier
        scene_number: Scene number (e.g., "1", "2A", "3")

    Returns:
        Scene dictionary, or None if not found
    """
    path = get_scene_path(project_id, scene_number)

    with _file_lock:
        if not path.exists():
            return None

        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading scene {scene_number}: {e}")
            return None


def write_scene(scene_data: Dict[str, Any], project_id: str, scene_number: str) -> bool:
    """
    Write scene JSON.

    Args:
        scene_data: Scene dictionary
        project_id: Project identifier
        scene_number: Scene number

    Returns:
        True if successful, False otherwise
    """
    path = get_scene_path(project_id, scene_number)

    # Update lastModified timestamp if metadata exists
    if "sceneMetadata" in scene_data:
        scene_data["sceneMetadata"]["lastModified"] = datetime.utcnow().isoformat() + "Z"

    with _file_lock:
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(scene_data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error writing scene {scene_number}: {e}")
            return False


def list_scenes(project_id: str = "default") -> List[str]:
    """
    List all scene numbers for a project.

    Args:
        project_id: Project identifier

    Returns:
        List of scene numbers
    """
    ensure_directories()
    prefix = f"{project_id}_scene_"
    suffix = ".json"

    scenes = []
    for file in SCENES_DIR.glob(f"{prefix}*{suffix}"):
        scene_num = file.stem.replace(prefix, "")
        scenes.append(scene_num)

    return sorted(scenes)


def get_scene_field(project_id: str, scene_number: str, field_path: str) -> Any:
    """
    Get a specific field from a scene JSON (intelligent loading).

    Args:
        project_id: Project identifier
        scene_number: Scene number
        field_path: Dot-notation path (e.g., "cinematography.shotSequence")

    Returns:
        Field value, or None if not found
    """
    scene = read_scene(project_id, scene_number)
    if not scene:
        return None

    # Navigate nested dictionary using dot notation
    fields = field_path.split('.')
    current = scene

    for field in fields:
        if isinstance(current, dict) and field in current:
            current = current[field]
        else:
            return None

    return current


def update_scene_field(project_id: str, scene_number: str, field_path: str, value: Any) -> bool:
    """
    Update a specific field in a scene JSON.

    Args:
        project_id: Project identifier
        scene_number: Scene number
        field_path: Dot-notation path
        value: New value

    Returns:
        True if successful
    """
    scene = read_scene(project_id, scene_number)
    if not scene:
        return False

    # Navigate nested dictionary and update
    fields = field_path.split('.')
    current = scene

    for field in fields[:-1]:
        if field not in current:
            current[field] = {}
        current = current[field]

    current[fields[-1]] = value

    return write_scene(scene, project_id, scene_number)


def get_global_continuity(project_id: str = "default") -> Dict[str, Any]:
    """
    Get global continuity state from project.

    Returns:
        Global continuity dictionary
    """
    state = read_project_state(project_id)
    return state.get("globalContinuity", {})


def update_global_continuity(continuity_data: Dict[str, Any], project_id: str = "default") -> bool:
    """
    Update global continuity state.

    Args:
        continuity_data: Updated continuity data
        project_id: Project identifier

    Returns:
        True if successful
    """
    state = read_project_state(project_id)
    state["globalContinuity"] = continuity_data
    return write_project_state(state, project_id)


def write_storyline(storyline_data: Dict[str, Any], project_id: str = "default") -> bool:
    """
    Write Entry Agent storyline to project state.

    Args:
        storyline_data: Storyline dict with overview, scenes, total_duration
        project_id: Project identifier

    Returns:
        True if successful
    """
    state = read_project_state(project_id)
    state["storyline"] = storyline_data
    state["sceneCount"] = len(storyline_data.get("scenes", []))
    return write_project_state(state, project_id)


def read_storyline(project_id: str = "default") -> Optional[Dict[str, Any]]:
    """
    Read Entry Agent storyline from project state.

    Returns:
        Storyline dict or None if not found
    """
    state = read_project_state(project_id)
    return state.get("storyline")


# Initialize directories on import
ensure_directories()
