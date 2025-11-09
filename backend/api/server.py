"""
FastAPI Server for Character Development System

Provides REST API and WebSocket endpoints for character development.
"""

import os
import sys
import asyncio
import json
import uuid
from pathlib import Path
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Add backend directory to Python path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# Load environment
load_dotenv()

# Import agent components
from agents.Character_Identity.agent import CharacterIdentityAgent
from agents.Character_Identity.schemas import EntryAgentOutput
from agent_types import AgentLevel


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_importance(importance_str: str) -> int:
    """
    Convert importance string to numeric priority (1-5, higher = more important)

    Args:
        importance_str: String like "main character", "supporting", "antagonist", etc.

    Returns:
        int: Priority score 1-5 (higher = more important)
    """
    if not importance_str:
        return 3  # Default medium priority

    importance_str = importance_str.lower().strip()

    # Main characters and antagonists (highest priority)
    if any(word in importance_str for word in ["main", "protagonist", "primary", "lead"]):
        return 5
    if any(word in importance_str for word in ["antagonist", "villain", "main antagonist"]):
        return 5

    # Secondary/supporting characters
    if any(word in importance_str for word in ["supporting", "secondary", "love interest"]):
        return 3

    # Minor/side characters
    if any(word in importance_str for word in ["side", "minor", "tertiary"]):
        return 1

    # Default medium priority
    return 3


def save_entry_session(session_id: str, session_data: Dict):
    """Save Entry Agent session to disk for persistence"""
    session_dir = BACKEND_DIR / "session_data"
    session_dir.mkdir(exist_ok=True)

    # Don't serialize the agent object, only the data
    serializable_data = {
        "conversation_history": session_data["conversation_history"],
        "status": session_data["status"],
        "output": session_data["output"]
    }

    session_file = session_dir / f"entry_{session_id}.json"
    with open(session_file, 'w') as f:
        json.dump(serializable_data, f, indent=2)


def load_entry_session(session_id: str, anthropic_api_key: str) -> Optional[Dict]:
    """Load Entry Agent session from disk"""
    session_file = BACKEND_DIR / "session_data" / f"entry_{session_id}.json"

    if not session_file.exists():
        return None

    with open(session_file, 'r') as f:
        data = json.load(f)

    # Recreate the session with a new agent instance
    return {
        "agent": EntryAgent(api_key=anthropic_api_key, level=AgentLevel.Intro_General_Entry),
        "conversation_history": data["conversation_history"],
        "status": data["status"],
        "output": data["output"]
    }


def save_scene_session(session_id: str, session_data: Dict):
    """Save Scene Creator session to disk for persistence"""
    session_dir = BACKEND_DIR / "session_data"
    session_dir.mkdir(exist_ok=True)

    # Don't serialize the agent object, only the data
    serializable_data = {
        "conversation_history": session_data["conversation_history"],
        "status": session_data["status"],
        "current_mode": session_data.get("current_mode", "creative_overview"),
        "scenes": session_data.get("scenes", [])
    }

    session_file = session_dir / f"scene_{session_id}.json"
    with open(session_file, 'w') as f:
        json.dump(serializable_data, f, indent=2)


def load_scene_session(session_id: str, anthropic_api_key: str) -> Optional[Dict]:
    """Load Scene Creator session from disk"""
    session_file = BACKEND_DIR / "session_data" / f"scene_{session_id}.json"

    if not session_file.exists():
        return None

    with open(session_file, 'r') as f:
        data = json.load(f)

    # Import Scene Creator agent
    from agents.Scene_Creator.agent import SceneCreatorAgent

    # Recreate the session with a new agent instance
    agent = SceneCreatorAgent(
        api_key=anthropic_api_key,
        level=AgentLevel.Scene_Creator,
        project_id=session_id
    )
    agent.switch_mode(data.get("current_mode", "creative_overview"))

    return {
        "agent": agent,
        "conversation_history": data["conversation_history"],
        "status": data["status"],
        "current_mode": data.get("current_mode", "creative_overview"),
        "scenes": data.get("scenes", [])
    }


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class StartCharacterRequest(BaseModel):
    characters: list
    storyline: dict
    mode: str = "balanced"


class ApproveRequest(BaseModel):
    checkpoint: int


class FeedbackRequest(BaseModel):
    checkpoint: int
    feedback: str


class ApproveWaveRequest(BaseModel):
    wave: int


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Character Development API",
    description="Multi-agent character development system with human-in-the-loop approvals",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve character data as static files
character_data_dir = BACKEND_DIR / "character_data"
if character_data_dir.exists():
    app.mount("/character_data", StaticFiles(directory=str(character_data_dir)), name="character_data")

# Initialize agent
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment")

character_agent = CharacterIdentityAgent(
    api_key=anthropic_api_key,
    level=AgentLevel.Character_Identity
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, character_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[character_id] = websocket

    def disconnect(self, character_id: str):
        if character_id in self.active_connections:
            del self.active_connections[character_id]

    async def send_message(self, character_id: str, message: dict):
        if character_id in self.active_connections:
            try:
                await self.active_connections[character_id].send_json(message)
            except:
                self.disconnect(character_id)


manager = ConnectionManager()


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {
        "message": "Character Development API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "active"
    }


@app.post("/api/character/start")
async def start_character(request: StartCharacterRequest, background_tasks: BackgroundTasks):
    """
    Start character development from Entry Agent output

    Returns character_id and initiates background processing
    """
    try:
        # Convert request to EntryAgentOutput
        entry_output: EntryAgentOutput = {
            "characters": request.characters,  # type: ignore
            "storyline": request.storyline  # type: ignore
        }

        # Create character
        character_id = character_agent.start_character_development(
            entry_output,
            mode=request.mode
        )

        # Run development in background with error handling
        async def run_development():
            try:
                async def websocket_callback(message: dict):
                    await manager.send_message(character_id, message)

                await character_agent.run_character_development(
                    character_id,
                    websocket_callback=websocket_callback
                )
            except Exception as e:
                # Send error message via WebSocket
                await manager.send_message(character_id, {
                    "type": "error",
                    "message": f"Character development failed: {str(e)}"
                })
                # Update character metadata to failed status
                try:
                    metadata = character_agent.storage.load_metadata(character_id)
                    metadata["status"] = "failed"
                    metadata["error"] = str(e)
                    character_agent.storage.save_metadata(character_id, metadata)
                except:
                    pass

        background_tasks.add_task(run_development)

        # Determine checkpoint count based on image generation setting
        IMAGE_GENERATION_ENABLED = os.getenv("IMAGE_GENERATION_ENABLED", "false").lower() == "true"
        checkpoint_count = 8 if IMAGE_GENERATION_ENABLED else 7

        return {
            "character_id": character_id,
            "status": "wave_1_started",
            "message": "Character development initiated",
            "checkpoint_count": checkpoint_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/character/start_batch")
async def start_batch_character_development(
    request: StartCharacterRequest,
    background_tasks: BackgroundTasks
):
    """
    Start character development for multiple high-priority characters

    Logic:
    - Develop ALL characters with importance >= 4 (Main characters + antagonists)
    - Develop first 2 characters with importance == 3 (Supporting characters)
    - Skip characters with importance < 3 (Side characters)

    Returns list of character_ids that were started
    """
    try:
        # Parse importance and add priority to each character
        characters_with_priority = []
        for char in request.characters:
            priority = parse_importance(char.get("importance", ""))
            characters_with_priority.append({
                **char,
                "priority": priority
            })

        # Sort by priority (highest first)
        characters_with_priority.sort(key=lambda x: x["priority"], reverse=True)

        # Select characters to develop
        characters_to_develop = []
        supporting_count = 0

        for char in characters_with_priority:
            if char["priority"] >= 4:
                # Auto-develop all main characters and antagonists
                characters_to_develop.append(char)
            elif char["priority"] == 3 and supporting_count < 2:
                # Develop first 2 supporting characters
                characters_to_develop.append(char)
                supporting_count += 1

        # Create development sessions for each selected character
        character_ids = []
        for char in characters_to_develop:
            # Create single-character entry output
            entry_output: EntryAgentOutput = {
                "characters": [char],  # type: ignore
                "storyline": request.storyline  # type: ignore
            }

            character_id = character_agent.start_character_development(
                entry_output,
                mode=request.mode
            )

            character_ids.append({
                "character_id": character_id,
                "name": char["name"],
                "priority": char["priority"],
                "importance": char.get("importance", "medium")
            })

            # Run development in background
            async def run_development(cid=character_id):
                try:
                    async def websocket_callback(message: dict):
                        await manager.send_message(cid, message)

                    await character_agent.run_character_development(
                        cid,
                        websocket_callback=websocket_callback
                    )
                except Exception as e:
                    await manager.send_message(cid, {
                        "type": "error",
                        "message": f"Character development failed: {str(e)}"
                    })
                    try:
                        metadata = character_agent.storage.load_metadata(cid)
                        metadata["status"] = "failed"
                        metadata["error"] = str(e)
                        character_agent.storage.save_metadata(cid, metadata)
                    except:
                        pass

            background_tasks.add_task(run_development)

        return {
            "characters": character_ids,
            "total_selected": len(character_ids),
            "total_submitted": len(request.characters),
            "status": "batch_started",
            "message": f"Started development for {len(character_ids)} characters based on importance"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/character/{character_id}/status")
async def get_status(character_id: str):
    """Get current status of character development"""
    try:
        status = character_agent.get_character_status(character_id)
        return status
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Character not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/character/{character_id}/checkpoint/{checkpoint_number}")
async def get_checkpoint(character_id: str, checkpoint_number: int):
    """Get specific checkpoint data"""
    try:
        checkpoint = character_agent.get_checkpoint(character_id, checkpoint_number)
        if checkpoint is None:
            raise HTTPException(status_code=404, detail="Checkpoint not found")
        return checkpoint
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Character not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/character/{character_id}/approve")
async def approve_checkpoint(character_id: str, request: ApproveRequest):
    """Approve a checkpoint and continue to next agent"""
    try:
        character_agent.approve_checkpoint(character_id, request.checkpoint)
        return {
            "message": f"Checkpoint {request.checkpoint} approved. Proceeding to next agent.",
            "next_checkpoint": request.checkpoint + 1,
            "status": "continuing"
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Character not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/character/{character_id}/feedback")
async def submit_feedback(character_id: str, request: FeedbackRequest):
    """Reject checkpoint and provide feedback for regeneration"""
    try:
        # Map checkpoint number to agent name
        checkpoint_to_agent = {
            1: "personality",
            2: "backstory_motivation",
            3: "voice_dialogue",
            4: "physical_description",
            5: "story_arc",
            6: "relationships",
            7: "image_generation",
        }

        agent_name = checkpoint_to_agent.get(request.checkpoint)
        if not agent_name:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid checkpoint number: {request.checkpoint}. Must be 1-7."
            )

        # Trigger regeneration
        result = await character_agent.regenerate_agent(
            character_id,
            agent_name,
            request.feedback
        )

        return {
            "message": result["message"],
            "status": "regenerated",
            "checkpoint": result["checkpoint"],
            "agent": result["agent"]
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Character not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/character/{character_id}/approve_wave")
async def approve_wave(character_id: str, request: ApproveWaveRequest):
    """Approve a wave and continue to the next wave"""
    try:
        # Get the active orchestrator session
        orchestrator = character_agent.active_sessions.get(character_id)
        if not orchestrator:
            raise HTTPException(status_code=404, detail="Active character development session not found")

        # Approve the wave (unblocks the approval gate)
        orchestrator.approve_wave(request.wave)

        next_wave = request.wave + 1 if request.wave < 3 else "final"
        return {
            "message": f"Wave {request.wave} approved. Continuing to {next_wave}.",
            "next_wave": next_wave,
            "status": "continuing"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/character/{character_id}/final")
async def get_final_profile(character_id: str):
    """Get final character profile"""
    try:
        profile = character_agent.get_final_profile(character_id)
        if profile is None:
            raise HTTPException(status_code=404, detail="Final profile not yet complete")
        return profile
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Character not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws/character/{character_id}")
async def websocket_endpoint(websocket: WebSocket, character_id: str):
    """
    WebSocket endpoint for real-time character development updates

    Messages sent:
    - agent_started: When an agent begins
    - agent_progress: Progress updates
    - checkpoint_ready: When checkpoint is ready for approval
    - wave_complete: When a wave finishes
    - character_complete: When all development is done
    - error: If something goes wrong
    """
    await manager.connect(character_id, websocket)
    try:
        while True:
            # Keep connection alive, listen for ping/pong
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(character_id)


# ============================================================================
# ENTRY AGENT ENDPOINTS
# ============================================================================

from agents.Intro_General_Entry.agent import EntryAgent
import uuid

# Store active entry sessions
entry_sessions: Dict[str, Dict] = {}

class EntryStartRequest(BaseModel):
    session_id: Optional[str] = None

class EntryChatRequest(BaseModel):
    message: str

@app.post("/api/entry/start")
async def start_entry_session(request: EntryStartRequest):
    """Start a new Entry Agent conversation session (or resume from disk)"""
    session_id = request.session_id or str(uuid.uuid4())

    # Try to load existing session from disk
    if request.session_id:
        loaded_session = load_entry_session(session_id, anthropic_api_key)
        if loaded_session:
            entry_sessions[session_id] = loaded_session
            return {
                "session_id": session_id,
                "status": loaded_session["status"],
                "message": "Entry Agent session resumed from disk!"
            }

    # Create new session if not found
    entry_sessions[session_id] = {
        "agent": EntryAgent(api_key=anthropic_api_key, level=AgentLevel.Intro_General_Entry),
        "conversation_history": [],
        "status": "active",
        "output": None
    }

    # Save new session to disk
    save_entry_session(session_id, entry_sessions[session_id])

    return {
        "session_id": session_id,
        "status": "active",
        "message": "Entry Agent session started. Ask me about your video concept!"
    }

@app.post("/api/entry/{session_id}/chat")
async def entry_chat(session_id: str, request: EntryChatRequest):
    """Send message to Entry Agent"""
    # Try to load session from disk if not in memory
    if session_id not in entry_sessions:
        loaded_session = load_entry_session(session_id, anthropic_api_key)
        if loaded_session:
            entry_sessions[session_id] = loaded_session
        else:
            raise HTTPException(status_code=404, detail="Session not found")

    session = entry_sessions[session_id]

    try:
        # Run Entry Agent
        response = await session["agent"].run(
            request.message,
            session["conversation_history"]
        )

        # Update history
        session["conversation_history"].append({"role": "user", "content": request.message})
        session["conversation_history"].append({"role": "assistant", "content": response})

        # Check if Entry Agent finalized output
        is_final = "FINAL OUTPUT:" in response
        if is_final and hasattr(session["agent"], "last_output"):
            session["output"] = session["agent"].last_output
            session["status"] = "completed"

        # Save session to disk after each message
        save_entry_session(session_id, session)

        return {
            "response": response,
            "is_final": is_final,
            "output": session["output"] if is_final else None,
            "status": session["status"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/entry/{session_id}/status")
async def get_entry_status(session_id: str):
    """Get Entry Agent session status"""
    if session_id not in entry_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = entry_sessions[session_id]
    return {
        "session_id": session_id,
        "status": session["status"],
        "message_count": len(session["conversation_history"]),
        "output": session["output"]
    }


# ============================================================================
# SCENE CREATOR ENDPOINTS
# ============================================================================

from agents.Scene_Creator.agent import SceneCreatorAgent

# Store active scene sessions
scene_sessions: Dict[str, Dict] = {}

class SceneStartRequest(BaseModel):
    project_id: Optional[str] = "default"
    mode: Optional[str] = "creative_overview"

class SceneChatRequest(BaseModel):
    message: str

class SceneModeRequest(BaseModel):
    mode: str

@app.post("/api/scene/start")
async def start_scene_session(request: SceneStartRequest):
    """Start a new Scene Creator session (or resume from disk)"""
    project_id = request.project_id

    # Try to load existing session from disk
    if project_id:
        loaded_session = load_scene_session(project_id, anthropic_api_key)
        if loaded_session:
            scene_sessions[project_id] = loaded_session
            return {
                "project_id": project_id,
                "status": loaded_session["status"],
                "mode": loaded_session["current_mode"],
                "message": "Scene Creator session resumed from disk!"
            }

    # Create new session
    scene_sessions[project_id] = {
        "agent": SceneCreatorAgent(
            api_key=anthropic_api_key,
            level=AgentLevel.Scene_Creator,
            project_id=project_id
        ),
        "conversation_history": [],
        "status": "active",
        "scenes": [],
        "current_mode": request.mode
    }

    # Set initial mode
    scene_sessions[project_id]["agent"].switch_mode(request.mode)

    # Save new session to disk
    save_scene_session(project_id, scene_sessions[project_id])

    return {
        "project_id": project_id,
        "status": "active",
        "mode": request.mode,
        "message": f"Scene Creator started in {request.mode} mode. Describe your first scene!"
    }

@app.post("/api/scene/{project_id}/chat")
async def scene_chat(project_id: str, request: SceneChatRequest):
    """Send message to Scene Creator"""
    # Try to load session from disk if not in memory
    if project_id not in scene_sessions:
        loaded_session = load_scene_session(project_id, anthropic_api_key)
        if loaded_session:
            scene_sessions[project_id] = loaded_session
        else:
            raise HTTPException(status_code=404, detail="Scene session not found")

    session = scene_sessions[project_id]

    try:
        # Run Scene Creator
        response = await session["agent"].run(
            request.message,
            session["conversation_history"]
        )

        # Update history
        session["conversation_history"].append({"role": "user", "content": request.message})
        session["conversation_history"].append({"role": "assistant", "content": response})

        # Save session to disk after each message
        save_scene_session(project_id, session)

        return {
            "response": response,
            "mode": session["current_mode"],
            "scene_count": len(session["scenes"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scene/{project_id}/mode")
async def switch_scene_mode(project_id: str, request: SceneModeRequest):
    """Switch Scene Creator mode"""
    if project_id not in scene_sessions:
        raise HTTPException(status_code=404, detail="Scene session not found")

    session = scene_sessions[project_id]
    success = session["agent"].switch_mode(request.mode)

    if success:
        session["current_mode"] = request.mode
        return {
            "success": True,
            "mode": request.mode,
            "message": f"Mode switched to {request.mode}"
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid mode")

@app.get("/api/scene/{project_id}/status")
async def get_scene_status(project_id: str):
    """Get Scene Creator session status"""
    if project_id not in scene_sessions:
        raise HTTPException(status_code=404, detail="Scene session not found")

    session = scene_sessions[project_id]
    return {
        "project_id": project_id,
        "status": session["status"],
        "mode": session["current_mode"],
        "message_count": len(session["conversation_history"]),
        "scene_count": len(session["scenes"])
    }


# ============================================================================
# PROJECT MANAGEMENT ENDPOINTS
# ============================================================================

from utils.state_manager import read_project_state

projects_store: Dict[str, Dict] = {}

class CreateProjectRequest(BaseModel):
    name: str
    description: Optional[str] = ""

@app.post("/api/projects")
async def create_project(request: CreateProjectRequest):
    """Create a new project"""
    project_id = str(uuid.uuid4())

    projects_store[project_id] = {
        "id": project_id,
        "name": request.name,
        "description": request.description,
        "created_at": str(asyncio.get_event_loop().time()),
        "entry_session": None,
        "character_ids": [],
        "scene_project_id": None,
        "status": "active"
    }

    return projects_store[project_id]

@app.get("/api/projects")
async def list_projects():
    """List all projects"""
    return {"projects": list(projects_store.values())}

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    if project_id not in projects_store:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects_store[project_id]


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "weave-multi-agent-api"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
