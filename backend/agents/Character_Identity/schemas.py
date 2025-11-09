"""
Data schemas for Character Development System

This module defines all TypedDicts and data structures used across
the character development multi-agent system.
"""

from typing import TypedDict, List, Dict, Literal, Optional, Union
try:
    from typing import NotRequired  # Python 3.11+
except ImportError:
    from typing_extensions import NotRequired  # Python < 3.11


# ============================================================================
# INPUT SCHEMAS (from Entry Agent)
# ============================================================================

class CharacterInput(TypedDict):
    """Single character from Entry Agent output"""
    name: str
    appearance: str
    personality: str
    role: str
    importance: NotRequired[str]  # Optional: "main character", "supporting", "antagonist", etc.


class SceneInput(TypedDict, total=False):
    """Scene from Entry Agent output (enhanced format after merge)"""
    title: str
    description: str
    characters_involved: List[str]
    setting: str
    mood: str


class StorylineInput(TypedDict):
    """Storyline context from Entry Agent"""
    overview: str
    tone: str
    scenes: List[Union[str, SceneInput]]  # Support both old (str) and new (dict) formats


class EntryAgentOutput(TypedDict):
    """Complete input from Entry Agent (Level 1)"""
    characters: List[CharacterInput]
    storyline: StorylineInput


# ============================================================================
# AGENT OUTPUT SCHEMAS
# ============================================================================

class PersonalityOutput(TypedDict):
    """Output from Personality sub-agent"""
    core_traits: List[str]
    fears: List[str]
    secrets: List[str]
    emotional_baseline: str
    triggers: List[str]


class TimelineEvent(TypedDict):
    """Single event in character timeline"""
    age: int
    event: str


class FormativeExperience(TypedDict):
    """Single formative experience with impact"""
    experience: str
    impact: str


class InternalConflict(TypedDict):
    """Single internal conflict with description"""
    conflict: str
    description: str


class BackstoryOutput(TypedDict):
    """Output from Backstory & Motivation sub-agent"""
    timeline: List[TimelineEvent]
    formative_experiences: List[FormativeExperience]  # FIX: Changed from List[str]
    goals: Dict[str, str]  # {"surface": "...", "deep": "..."}
    internal_conflicts: List[InternalConflict]  # FIX: Changed from List[str]


class SampleDialogue(TypedDict):
    """Sample dialogue in different emotional states"""
    confident: str
    vulnerable: str
    stressed: str
    sarcastic: str


class VoiceOutput(TypedDict):
    """Output from Voice & Dialogue sub-agent"""
    speech_pattern: str
    verbal_tics: List[str]
    vocabulary: str
    sample_dialogue: SampleDialogue


class PhysicalOutput(TypedDict):
    """Output from Physical Description sub-agent"""
    mannerisms: List[str]
    body_language: str
    movement_style: str
    physical_quirks: List[str]


class TransformationBeat(TypedDict):
    """Single transformation beat in story arc"""
    act: int
    beat: str


class StoryArcOutput(TypedDict):
    """Output from Story Arc sub-agent"""
    role: str
    arc_type: str
    transformation_beats: List[TransformationBeat]
    scene_presence: List[str]


class Relationship(TypedDict):
    """Single relationship to another character"""
    character: str
    type: str
    dynamic: str
    evolution: str


class RelationshipsOutput(TypedDict):
    """Output from Relationships sub-agent"""
    relationships: List[Relationship]


class GeneratedImage(TypedDict):
    """Single generated image with metadata"""
    type: Literal["portrait", "full_body", "action", "expression"]
    path: str
    prompt: str
    approved: bool


class ImageGenerationOutput(TypedDict):
    """Output from Image Generation sub-agent"""
    images: List[GeneratedImage]
    style_profile: str


# ============================================================================
# CHECKPOINT SCHEMAS
# ============================================================================

class CheckpointMetadata(TypedDict):
    """Metadata for a checkpoint"""
    wave: int
    timestamp: str
    tokens_used: int
    agent_time_seconds: float


class CheckpointOutput(TypedDict):
    """Generic checkpoint output structure"""
    narrative: str
    structured: Dict  # Specific to each agent


class Checkpoint(TypedDict):
    """Complete checkpoint data"""
    checkpoint_number: int
    agent: str
    status: Literal["in_progress", "awaiting_approval", "approved", "rejected"]
    output: CheckpointOutput
    metadata: CheckpointMetadata


# ============================================================================
# FINAL OUTPUT SCHEMA
# ============================================================================

class CharacterOverview(TypedDict):
    """High-level character overview"""
    name: str
    role: str
    importance: int
    one_line: str


class VisualData(TypedDict):
    """Visual representation data"""
    images: List[Dict[str, str]]  # [{"type": "...", "url": "..."}]
    style_notes: str


class FinalCharacterProfile(TypedDict):
    """Complete character profile (final output)"""
    character_id: str
    name: str
    version: str
    completed_at: str

    overview: CharacterOverview
    visual: VisualData
    psychology: PersonalityOutput
    physical_presence: PhysicalOutput
    voice: VoiceOutput
    backstory_motivation: BackstoryOutput
    narrative_arc: StoryArcOutput
    relationships: List[Relationship]

    metadata: Dict  # mode, development_time, tokens, etc.


# ============================================================================
# INTERNAL STATE SCHEMAS
# ============================================================================

class AgentStatus(TypedDict):
    """Status of a single agent"""
    status: Literal["pending", "in_progress", "completed", "failed"]
    wave: int


class CharacterKnowledgeBase(TypedDict):
    """Shared knowledge base accessed by all agents"""
    character_id: str
    input_data: EntryAgentOutput
    mode: Literal["fast", "balanced", "deep"]

    # Agent outputs (populated as agents complete)
    personality: Optional[PersonalityOutput]
    backstory_motivation: Optional[BackstoryOutput]
    voice_dialogue: Optional[VoiceOutput]
    physical_description: Optional[PhysicalOutput]
    story_arc: Optional[StoryArcOutput]
    relationships: Optional[RelationshipsOutput]
    image_generation: Optional[ImageGenerationOutput]

    # Status tracking
    current_wave: int
    current_checkpoint: int
    agent_statuses: Dict[str, AgentStatus]


# ============================================================================
# API REQUEST/RESPONSE SCHEMAS
# ============================================================================

class StartCharacterRequest(TypedDict):
    """Request to start character development"""
    characters: List[CharacterInput]
    storyline: StorylineInput
    mode: Optional[Literal["fast", "balanced", "deep"]]


class StartCharacterResponse(TypedDict):
    """Response from starting character development"""
    character_id: str
    status: str
    message: str
    checkpoint_count: int


class StatusResponse(TypedDict):
    """Response for status check"""
    character_id: str
    current_wave: int
    current_agent: str
    status: str
    progress: Dict[str, int]
    agents: Dict[str, AgentStatus]


class ApproveRequest(TypedDict):
    """Request to approve a checkpoint"""
    checkpoint: int


class FeedbackRequest(TypedDict):
    """Request to regenerate with feedback"""
    checkpoint: int
    feedback: str


class ApproveResponse(TypedDict):
    """Response after approving checkpoint"""
    message: str
    next_checkpoint: int
    status: str


class FeedbackResponse(TypedDict):
    """Response after submitting feedback"""
    message: str
    status: str
    estimated_time_seconds: int
