# CHARACTER IDENTITY AGENT - DEEP DIVE INVESTIGATION

**Date:** November 8, 2025  
**Investigation Scope:** Complete analysis of Character Identity Agent implementation, wave structure, checkpoints, WebSocket flow, approval/rejection handling, and storage mechanism.

---

## EXECUTIVE SUMMARY

The Character Identity Agent is a sophisticated multi-agent character development system that orchestrates 6 specialized sub-agents (image generation disabled) in 3 waves to create comprehensive character profiles. The system uses checkpoint-based human-in-the-loop approval before continuing to the next agent.

**Key Finding:** Image generation is DISABLED in current implementation (commented out in orchestrator.py lines 288-326).

---

## 1. WAVE STRUCTURE - EXACT IMPLEMENTATION

### Wave Definition
The orchestrator.py file clearly documents the wave structure (lines 4-9):

```
Wave 1 (Foundation): Personality + Backstory & Motivation
Wave 2 (Expression): Voice & Dialogue + Physical Description + Story Arc  
Wave 3 (Social): Relationships + Image Generation (DISABLED)
```

### Detailed Wave Breakdown

#### WAVE 1 - FOUNDATION (Lines 124-189 in orchestrator.py)
**Execution Method:** Parallel (`asyncio.gather()`)  
**Agents Running in Parallel:**
- `personality_agent()` (subagents/personality.py)
- `backstory_motivation_agent()` (subagents/backstory_motivation.py)

**Checkpoints Generated:**
- Checkpoint #1: Personality
- Checkpoint #2: Backstory & Motivation

**Output Format:**
```python
# Wave 1 updates KB with:
self.kb["personality"] = personality_output
self.kb["backstory_motivation"] = backstory_output
self.kb["agent_statuses"]["personality"] = {"status": "completed", "wave": 1}
self.kb["agent_statuses"]["backstory_motivation"] = {"status": "completed", "wave": 1}
```

**Estimated Tokens:** 1500 + 1800 = 3300 total  
**Model Used:** claude-haiku-4-5-20251001

---

#### WAVE 2 - EXPRESSION (Lines 190-269 in orchestrator.py)
**Execution Method:** Parallel (`asyncio.gather()`)  
**Agents Running in Parallel:**
- `voice_dialogue_agent()` (subagents/voice_dialogue.py)
- `physical_description_agent()` (subagents/physical_description.py)
- `story_arc_agent()` (subagents/story_arc.py)

**Checkpoints Generated:**
- Checkpoint #3: Voice & Dialogue
- Checkpoint #4: Physical Description
- Checkpoint #5: Story Arc

**Output Format:**
```python
# Wave 2 updates KB with:
self.kb["voice_dialogue"] = voice_output
self.kb["physical_description"] = physical_output
self.kb["story_arc"] = story_arc_output
self.kb["agent_statuses"]["voice_dialogue"] = {"status": "completed", "wave": 2}
self.kb["agent_statuses"]["physical_description"] = {"status": "completed", "wave": 2}
self.kb["agent_statuses"]["story_arc"] = {"status": "completed", "wave": 2}
```

**Estimated Tokens:** 1600 + 1400 + 1700 = 4700 total  
**Model Used:** claude-haiku-4-5-20251001

---

#### WAVE 3 - SOCIAL (Lines 271-333 in orchestrator.py)
**Execution Method:** Sequential (NOT parallel)  
**Agent Running:**
- `relationships_agent()` (subagents/relationships.py)
- Image generation COMMENTED OUT (lines 288, 297, 303, 318-326)

**Checkpoints Generated:**
- Checkpoint #6: Relationships
- ~~Checkpoint #7: Image Generation~~ (DISABLED)

**Output Format:**
```python
# Wave 3 updates KB with:
self.kb["relationships"] = relationships_output
# COMMENTED OUT: self.kb["image_generation"] = image_output
self.kb["agent_statuses"]["relationships"] = {"status": "completed", "wave": 3}
```

**Estimated Tokens:** 1800 total  
**Model Used:** claude-haiku-4-5-20251001

**Important Note (Line 277):** `await self._send_update` references only `["relationships"]` - image generation removed from wave completion message.

---

### Sequence Diagram

```
START
  ↓
WAVE 1 (run_wave_1)
  ├─ personality_agent() ─────┐
  │                           ├─ Parallel
  └─ backstory_motivation()  ─┘
  ├─ Checkpoint #1 (awaiting approval)
  ├─ WAIT for approval
  ├─ Checkpoint #2 (awaiting approval)
  └─ WAIT for approval
  ↓
WAVE 2 (run_wave_2)
  ├─ voice_dialogue_agent() ──┐
  ├─ physical_description()   ├─ Parallel
  └─ story_arc_agent() ───────┘
  ├─ Checkpoint #3 (awaiting approval)
  ├─ WAIT for approval
  ├─ Checkpoint #4 (awaiting approval)
  ├─ WAIT for approval
  ├─ Checkpoint #5 (awaiting approval)
  └─ WAIT for approval
  ↓
WAVE 3 (run_wave_3)
  ├─ relationships_agent() (sequential)
  ├─ Checkpoint #6 (awaiting approval)
  └─ WAIT for approval
  ↓
FINAL CONSOLIDATION (create_final_profile)
  ├─ Validate all required fields
  ├─ Create FinalCharacterProfile
  ├─ Checkpoint #7 (final_consolidation, wave 4)
  └─ WAIT for approval
  ↓
COMPLETE
```

---

## 2. CHECKPOINT STRUCTURE - EXACT IMPLEMENTATION

### Total Checkpoints: 7 (Changed from 8 - see storage.py line 79)

**Metadata confirms:** `"total_checkpoints": 7` (storage.py line 79)

### Complete Checkpoint List

| # | Agent | Wave | Checkpoint File | Status | Content Type |
|---|-------|------|-----------------|--------|--------------|
| 1 | personality | 1 | `01_personality.json` | awaiting_approval | PersonalityOutput |
| 2 | backstory_motivation | 1 | `02_backstory_motivation.json` | awaiting_approval | BackstoryOutput |
| 3 | voice_dialogue | 2 | `03_voice_dialogue.json` | awaiting_approval | VoiceOutput |
| 4 | physical_description | 2 | `04_physical_description.json` | awaiting_approval | PhysicalOutput |
| 5 | story_arc | 2 | `05_story_arc.json` | awaiting_approval | StoryArcOutput |
| 6 | relationships | 3 | `06_relationships.json` | awaiting_approval | RelationshipsOutput |
| 7 | final_consolidation | 4 | `07_final_consolidation.json` | awaiting_approval | FinalCharacterProfile |

### Checkpoint JSON Structure

```typescript
{
  "checkpoint_number": number,      // 1-7
  "agent": string,                  // "personality", "backstory_motivation", etc.
  "status": "awaiting_approval" |   // Only status currently used (line 77 in orchestrator.py)
             "approved" |
             "rejected" |
             "in_progress",
  "output": {
    "narrative": string,            // Rich prose description (2-4 paragraphs)
    "structured": object            // Agent-specific structured data (JSON)
  },
  "metadata": {
    "wave": number,                 // 1, 2, 3, or 4 (final)
    "timestamp": ISO string,        // UTC timestamp when checkpoint created
    "tokens_used": number,          // Estimated tokens for this agent
    "agent_time_seconds": float     // Time agent took to complete
  }
}
```

### Checkpoint Content Details

#### Checkpoint #1 - Personality
**Structured Content:**
```json
{
  "core_traits": string[4-6],       // Fundamental personality characteristics
  "fears": string[2-4],             // Deep psychological fears
  "secrets": string[2-3],           // What they hide from others/themselves
  "emotional_baseline": string,     // Default emotional state
  "triggers": string[3-5]           // What causes strong reactions
}
```

**Narrative:** 2-3 paragraph psychological profile with depth and contradiction analysis

---

#### Checkpoint #2 - Backstory & Motivation
**Structured Content:**
```json
{
  "timeline": TimelineEvent[5-10],  // [{age: number, event: string}, ...]
  "formative_experiences": FormativeExperience[3-5],  // Experience + impact
  "goals": {
    "surface": string,              // What they consciously pursue
    "deep": string                  // What they actually need
  },
  "internal_conflicts": InternalConflict[2-4]  // [{conflict, description}, ...]
}
```

**Narrative:** 3-4 paragraph backstory with timeline, formative moments, motivation

---

#### Checkpoint #3 - Voice & Dialogue
**Structured Content:**
```json
{
  "speech_pattern": string,         // Formal/casual/fragmented/etc.
  "verbal_tics": string[],          // Characteristic phrases, stutters, patterns
  "vocabulary": string,             // Word choice level and style
  "sample_dialogue": {
    "confident": string,            // Dialogue in confident emotional state
    "vulnerable": string,           // Dialogue when vulnerable
    "stressed": string,             // Dialogue under stress
    "sarcastic": string             // Sarcastic/defensive dialogue
  }
}
```

**Narrative:** Analysis of voice patterns and how speech reflects personality

---

#### Checkpoint #4 - Physical Description
**Structured Content:**
```json
{
  "mannerisms": string[],           // Habitual physical behaviors
  "body_language": string,          // How they carry themselves
  "movement_style": string,         // Graceful/clumsy/tense/relaxed etc.
  "physical_quirks": string[]       // Distinctive physical habits
}
```

**Narrative:** Physical presence analysis and how body communicates personality

---

#### Checkpoint #5 - Story Arc
**Structured Content:**
```json
{
  "role": string,                   // Protagonist/antagonist/mentor/etc.
  "arc_type": string,               // Growth/corruption/redemption/etc.
  "transformation_beats": TransformationBeat[],  // [{act: 1-3, beat: string}, ...]
  "scene_presence": string[]        // Which scenes they appear in
}
```

**Narrative:** Narrative function and character arc throughout story

---

#### Checkpoint #6 - Relationships
**Structured Content:**
```json
{
  "relationships": Relationship[]   // Array of character relationships
}

// Where Relationship = 
{
  "character": string,              // Name of other character
  "type": string,                   // "ally", "enemy", "family", etc.
  "dynamic": string,                // Nature of the relationship
  "evolution": string               // How relationship changes
}
```

**Narrative:** Character's relational architecture and relationship patterns

---

#### Checkpoint #7 - Final Consolidation
**Structured Content:** Complete `FinalCharacterProfile` object:

```json
{
  "character_id": string,
  "name": string,
  "version": "1.0",
  "completed_at": ISO string,
  
  "overview": {
    "name": string,
    "role": string,
    "importance": number,           // 1-5 scale
    "one_line": string              // One-sentence summary
  },
  
  "visual": {
    "images": [],                   // Empty (image generation disabled)
    "style_notes": ""               // Empty (image generation disabled)
  },
  
  "psychology": PersonalityOutput,  // From checkpoint #1
  "physical_presence": PhysicalOutput,  // From checkpoint #4
  "voice": VoiceOutput,             // From checkpoint #3
  "backstory_motivation": BackstoryOutput,  // From checkpoint #2
  "narrative_arc": StoryArcOutput,  // From checkpoint #5
  "relationships": Relationship[],  // From checkpoint #6
  
  "metadata": {
    "mode": "fast" | "balanced" | "deep",
    "development_time_minutes": number,
    "total_checkpoints": 7,         // Changed from 8
    "regenerations": number,
    "total_tokens": 10000           // Reduced from 12000
  }
}
```

**Narrative:** "Character development complete. All aspects consolidated into comprehensive profile."

---

### Image Generation Status

**Location:** Lines 318-326 in orchestrator.py (COMMENTED OUT)

```python
# COMMENTED OUT: Image generation checkpoint
# await self._create_checkpoint(
#     checkpoint_number=7,
#     agent_name="image_generation",
#     wave=3,
#     output=image_output,
#     narrative=image_narrative,
#     tokens_used=5160,
#     agent_time=wave_time / 2
# )
```

**Why Disabled:**
- Line 277: Wave 3 message only includes `["relationships"]`
- Line 359-361: `visual` data in final profile is empty
- Line 387-390: Metadata has reduced totals (7 instead of 8, 10000 instead of 12000 tokens)

**Implementation Details (if re-enabled):**
- Would generate 4 image types: portrait, full_body, action, expression
- Uses Google Gemini API (not Anthropic)
- Requires `gemini_api_key` from environment
- Saves images to `backend/character_data/{character_id}/images/`

---

## 3. WEBSOCKET MESSAGE FLOW

### WebSocket Endpoint
**Location:** api/server.py lines 255-276

```python
@app.websocket("/ws/character/{character_id}")
async def websocket_endpoint(websocket: WebSocket, character_id: str):
```

### Message Types Sent During Development

#### 1. **wave_started** (Lines 127-131, 193-197, 274-278)
```json
{
  "type": "wave_started",
  "wave": 1 | 2 | 3,
  "agents": ["agent1", "agent2", ...]  // Array of agents running in wave
}
```
**Timing:** Sent at start of each wave  
**Wave 1 agents:** `["personality", "backstory_motivation"]`  
**Wave 2 agents:** `["voice_dialogue", "physical_description", "story_arc"]`  
**Wave 3 agents:** `["relationships"]`

---

#### 2. **checkpoint_ready** (Lines 99-104)
```json
{
  "type": "checkpoint_ready",
  "checkpoint_number": 1-7,
  "agent": "personality" | "backstory_motivation" | ... | "final_consolidation",
  "message": "{agent_name} analysis complete. Awaiting approval."
}
```
**Timing:** Sent after each agent completes and checkpoint is saved  
**Frequency:** 7 times total (once per checkpoint)

---

#### 3. **wave_complete** (Lines 183-188, 264-269, 328-333)
```json
{
  "type": "wave_complete",
  "wave": 1 | 2 | 3,
  "agents_completed": ["agent1", "agent2", ...],
  "next_wave": 2 | 3 | "final"
}
```
**Timing:** Sent after all agents in a wave are approved  
**Frequency:** 3 times (after each wave)

---

#### 4. **character_complete** (Lines 407-411)
```json
{
  "type": "character_complete",
  "character_id": "uuid",
  "message": "All agents completed. Character profile ready."
}
```
**Timing:** Sent after final consolidation checkpoint is created and approved  
**Frequency:** 1 time (at end)

---

#### 5. **error** (Lines 152-155)
```json
{
  "type": "error",
  "message": "Character development failed: {error_message}"
}
```
**Timing:** Sent if any error occurs during development  
**Frequency:** 0-1 times

---

### WebSocket Connection Flow

```
Frontend connects: 
  → POST /api/character/start
     ↓
  ← Returns character_id
  → WebSocket /ws/character/{character_id}
     ↓
  ← wave_started (wave 1)
  ← checkpoint_ready (checkpoint 1)
  
  [User approves checkpoint 1]
  → POST /api/character/{id}/approve (checkpoint: 1)
  
  ← checkpoint_ready (checkpoint 2)
  
  [User approves checkpoint 2]
  → POST /api/character/{id}/approve (checkpoint: 2)
  
  ← wave_complete (wave 1)
  ← wave_started (wave 2)
  ...
  [7 checkpoints total]
  ...
  ← character_complete
  → WebSocket disconnects or closes
```

---

## 4. APPROVAL/REJECTION FLOW

### Approval Mechanism

#### How Approval Works (agent.py lines 155-165)

```python
def approve_checkpoint(self, character_id: str, checkpoint_number: int):
    """Approve a checkpoint and allow continuation"""
    metadata = self.storage.load_metadata(character_id)
    metadata["completed_checkpoints"] = checkpoint_number  # KEY LINE
    self.storage.save_metadata(character_id, metadata)
```

**Simple Flag System:** 
- The orchestrator waits by checking if `completed_checkpoints >= checkpoint_number`
- Once approved, it increments this counter and continues

#### Wait Mechanism (orchestrator.py lines 111-122)

```python
async def _wait_for_checkpoint_approval(self, checkpoint_number: int):
    """Wait for checkpoint to be approved before continuing"""
    while True:
        metadata = self.storage.load_metadata(self.character_id)
        if metadata.get("completed_checkpoints", 0) >= checkpoint_number:
            # Checkpoint approved!
            break
        
        # Check every 0.5 seconds
        await asyncio.sleep(0.5)
```

**Polling Strategy:**
- Polls metadata file every 0.5 seconds
- Blocks async execution until approval
- No callback or event system - purely polling

---

### Rejection/Feedback Flow

#### Current Implementation (agent.py lines 167-189)

```python
async def regenerate_agent(
    self,
    character_id: str,
    agent_name: str,
    feedback: str
):
    """Regenerate a specific agent with user feedback"""
    # Update regeneration count
    metadata = self.storage.load_metadata(character_id)
    metadata["regenerations"] = metadata.get("regenerations", 0) + 1
    self.storage.save_metadata(character_id, metadata)
    
    # TODO: Implement regeneration logic
    # This would re-run specific agent with feedback incorporated
    # into the prompt
    pass
```

**Status:** STUBBED - NOT FULLY IMPLEMENTED

**Current Terminal Behavior (agent.py lines 374-381):**
```python
elif approval == 'n':
    print(f"✗ Checkpoint #{checkpoint_num} rejected")
    feedback = input("Feedback for regeneration (or Enter to skip): ").strip()
    if feedback:
        print(f"Noted: {feedback}")
    # For now, approve anyway to continue (regeneration TODO)
    self.approve_checkpoint(character_id, checkpoint_num)
    break
```

**Current Behavior:** 
- Rejection is accepted and noted
- But the system approves anyway (line 380)
- Regeneration is NOT actually performed
- Feedback is captured but not stored

#### API Endpoint for Feedback (api/server.py lines 220-234)

```python
@app.post("/api/character/{character_id}/feedback")
async def submit_feedback(character_id: str, request: FeedbackRequest):
    """Reject checkpoint and provide feedback for regeneration"""
    try:
        # This would trigger regeneration logic
        # For now, just acknowledge
        return {
            "message": f"Regenerating checkpoint {request.checkpoint} with feedback",
            "status": "regenerating",
            "estimated_time_seconds": 4
        }
```

**Status:** STUB ENDPOINT - Returns fake response, doesn't actually regenerate

---

### Metadata Tracking

**Metadata JSON Structure** (storage.py lines 71-81):

```json
{
  "character_id": "uuid",
  "created_at": "ISO timestamp",
  "status": "in_progress" | "completed" | "failed",
  "mode": "fast" | "balanced" | "deep",
  "current_wave": 1 | 2 | 3 | 4,
  "current_checkpoint": 0-7,
  "completed_checkpoints": 0-7,   // KEY: Updated when checkpoint approved
  "total_checkpoints": 7,
  "regenerations": 0,
  "completed_at": "ISO timestamp" (added when final profile saved)
}
```

---

## 5. FILE STORAGE STRUCTURE

### Base Directory
```
./backend/character_data/
```
(Can be configured via `CharacterStorage(base_path)` - default line 25 in storage.py)

### Directory Structure for Each Character

```
character_data/
└── {character_id}/                    # UUID format
    ├── input.json                     # Original Entry Agent output
    ├── metadata.json                  # Status, timestamps, progress tracking
    ├── knowledge_base.json            # Shared KB across all agents
    ├── final_profile.json             # Complete character profile (when done)
    ├── checkpoints/
    │   ├── 01_personality.json
    │   ├── 02_backstory_motivation.json
    │   ├── 03_voice_dialogue.json
    │   ├── 04_physical_description.json
    │   ├── 05_story_arc.json
    │   ├── 06_relationships.json
    │   └── 07_final_consolidation.json
    └── images/                        # (Currently unused - image gen disabled)
        ├── portrait.png               # (Would be here if enabled)
        ├── full_body.png
        ├── action.png
        └── expression.png
```

### Checkpoint Filename Convention (storage.py line 165)

```python
filename = f"{checkpoint['checkpoint_number']:02d}_{checkpoint['agent']}.json"
```

**Pattern:** `NN_agent_name.json`  
**Examples:**
- `01_personality.json`
- `02_backstory_motivation.json`
- `07_final_consolidation.json`

### File Operations (storage.py)

#### Create Character (lines 51-116)
```python
def create_character(self, input_data: EntryAgentOutput, mode: str = "balanced") -> str:
    # 1. Generate UUID
    character_id = str(uuid.uuid4())
    
    # 2. Create directory
    char_dir = self._get_character_dir(character_id)
    
    # 3. Save input.json
    input_path = char_dir / "input.json"
    
    # 4. Create and save metadata.json
    # 5. Create and save knowledge_base.json
    
    return character_id
```

#### Save Checkpoint (lines 160-169)
```python
def save_checkpoint(self, character_id: str, checkpoint: Checkpoint) -> None:
    checkpoints_dir = self._get_checkpoints_dir(character_id)
    
    # Filename: 01_personality.json, 02_backstory.json, etc.
    filename = f"{checkpoint['checkpoint_number']:02d}_{checkpoint['agent']}.json"
    checkpoint_path = checkpoints_dir / filename
    
    with open(checkpoint_path, 'w') as f:
        json.dump(checkpoint, f, indent=2)
```

#### Save Final Profile (lines 228-240)
```python
def save_final_profile(self, character_id: str, profile: FinalCharacterProfile) -> None:
    char_dir = self._get_character_dir(character_id)
    final_path = char_dir / "final_profile.json"
    
    with open(final_path, 'w') as f:
        json.dump(profile, f, indent=2)
    
    # Update metadata
    metadata = self.load_metadata(character_id)
    metadata["status"] = "completed"
    metadata["completed_at"] = datetime.utcnow().isoformat()
    self.save_metadata(character_id, metadata)
```

---

### Knowledge Base Structure (schemas.py lines 223-242)

```python
class CharacterKnowledgeBase(TypedDict):
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
    image_generation: Optional[ImageGenerationOutput]  # NULL (image gen disabled)
    
    # Status tracking
    current_wave: int
    current_checkpoint: int
    agent_statuses: Dict[str, AgentStatus]  # Status for each agent
```

**Knowledge Base Lifecycle:**
1. Created when character development starts (storage.py lines 88-114)
2. Updated by each agent as they complete
3. Passed to next agents as context (e.g., Wave 2 agents read Wave 1 outputs)
4. Saved to disk after each wave completes

---

## 6. ACTUAL EXECUTION FLOW - TRACED

### Initiation Flow

```python
# 1. Frontend starts character development
POST /api/character/start
{
  "characters": [...],
  "storyline": {...},
  "mode": "balanced"
}

# 2. Backend creates character
character_id = character_agent.start_character_development(entry_output, mode)
  → storage.create_character(input_data, mode)
     → Creates character_id (UUID)
     → Saves input.json
     → Creates metadata.json with status="in_progress"
     → Creates knowledge_base.json with all agent_statuses="pending"

# 3. Backend starts async development in background
background_tasks.add_task(run_development)
  → Defines websocket_callback()
  → Calls await orchestrator.run_all_waves()

# 4. Frontend connects to WebSocket
WebSocket /ws/character/{character_id}
```

### Wave 1 Execution

```python
# orchestrator.run_wave_1() (lines 124-188)

# 1. Send wave started message
await _send_update({
  "type": "wave_started",
  "wave": 1,
  "agents": ["personality", "backstory_motivation"]
})

# 2. Run both agents in parallel
personality_result, backstory_result = await asyncio.gather(
  personality_agent(kb, api_key),
  backstory_motivation_agent(kb, api_key)
)

# 3. Unpack results (each agent returns (output, narrative))
personality_output, personality_narrative = personality_result
backstory_output, backstory_narrative = backstory_result

# 4. Update KB
kb["personality"] = personality_output
kb["backstory_motivation"] = backstory_output
kb["agent_statuses"]["personality"] = {"status": "completed", "wave": 1}
kb["agent_statuses"]["backstory_motivation"] = {"status": "completed", "wave": 1}
storage.save_character_kb(kb)

# 5. Create checkpoint #1
await _create_checkpoint(
  checkpoint_number=1,
  agent_name="personality",
  wave=1,
  output=personality_output,
  narrative=personality_narrative,
  tokens_used=1500,
  agent_time=wave_time / 2
)
  → Creates checkpoint JSON
  → Saves to checkpoints/01_personality.json
  → Updates metadata: current_checkpoint=1
  → Sends WebSocket: checkpoint_ready
  → Calls _wait_for_checkpoint_approval(1)
    → Polls metadata every 0.5s
    → Waits until completed_checkpoints >= 1
    → Returns when approved

# 6. Create checkpoint #2 (same process)
# 7. Send wave_complete message
```

### Key Implementation Detail: Checkpoint Blocking (orchestrator.py lines 106-109)

```python
# INSIDE _create_checkpoint():
# Save checkpoint
self.storage.save_checkpoint(self.character_id, checkpoint)

# Wait for checkpoint approval before continuing
await self._wait_for_checkpoint_approval(checkpoint_number)

return checkpoint  # Doesn't return until approved
```

**Critical:** Each agent's work is saved and human approval is obtained BEFORE the next agent starts, even within the same wave. The "parallel" execution in `asyncio.gather()` means agents run at the same time, but each checkpoint must be approved before the next agent starts.

---

## 7. DEVELOPMENT MODES

### Defined in schemas.py (line 227)

```python
mode: Literal["fast", "balanced", "deep"]
```

### How Modes Affect Prompts

Each subagent includes mode-specific prompt instructions:

```python
# From personality.py lines 53-56
DEPTH MODE: {mode}
{"Focus on essential psychological elements only." if mode == "fast" else ""}
{"Provide comprehensive analysis with depth and nuance." if mode == "deep" else ""}
{"Balance depth with efficiency." if mode == "balanced" else ""}
```

### Default Mode
```python
# From agent.py line 259
character_id = self.start_character_development(entry_json, mode="balanced")
```

---

## 8. API ENDPOINTS SUMMARY

### Character Development Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/character/start` | Start character development |
| GET | `/api/character/{character_id}/status` | Get current status |
| GET | `/api/character/{character_id}/checkpoint/{n}` | Get specific checkpoint |
| GET | `/api/character/{character_id}/final` | Get final profile |
| POST | `/api/character/{character_id}/approve` | Approve checkpoint |
| POST | `/api/character/{character_id}/feedback` | Submit feedback (STUBBED) |
| WS | `/ws/character/{character_id}` | Real-time updates |

---

## 9. KEY CODE SECTIONS - REFERENCE

| Functionality | File | Lines |
|--------------|------|-------|
| Wave orchestration | orchestrator.py | 37-421 |
| Checkpoint creation | orchestrator.py | 62-109 |
| Approval wait loop | orchestrator.py | 111-122 |
| Main agent class | agent.py | 29-453 |
| Approval endpoint | agent.py | 155-165 |
| Regeneration (TODO) | agent.py | 167-189 |
| Data schemas | schemas.py | 1-296 |
| Storage operations | storage.py | 22-271 |
| API server | api/server.py | 1-526 |
| WebSocket handler | api/server.py | 83-101 |

---

## 10. IMPORTANT NOTES & ANOMALIES

### 1. Image Generation is DISABLED

**Evidence:**
- Lines 288, 297, 303 in orchestrator.py have "FIX: Removed image_generation"
- Checkpoint count changed from 8 to 7 (storage.py line 79)
- Final profile metadata.total_checkpoints = 7 (orchestrator.py line 387)
- visual.images = [] and visual.style_notes = "" (orchestrator.py lines 359-360)

### 2. Regeneration is NOT IMPLEMENTED

**Status:** TODO (agent.py lines 186-188)  
**Impact:** Rejecting a checkpoint doesn't regenerate - it just notes feedback and continues

### 3. Wave 3 Only Has One Agent (Actually)

Despite the README documenting 7 sub-agents, Wave 3 currently only runs relationships:
- Line 277 in orchestrator.py: `"agents": ["relationships"]`  
- Image generation commented out

### 4. Polling-Based Approval

No event system - uses 0.5-second polling to check metadata file for approval status.

### 5. Sequential Checkpoint Approval Within Waves

Even though Wave 1 runs personality and backstory in parallel:
```python
# Parallel execution of agents
personality_task = personality_agent(...)
backstory_task = backstory_motivation_agent(...)
personality_result, backstory_result = await asyncio.gather(personality_task, backstory_task)

# But checkpoints are sequential
await self._create_checkpoint(1, ...)  # Creates and waits for approval
await self._create_checkpoint(2, ...)  # Only runs after #1 approved
```

Each checkpoint must be individually approved before the next is created.

### 6. Knowledge Base as Context

All Wave 2 and Wave 3 agents receive the KB with previous outputs:
```python
# From voice_dialogue.py lines 40-48
if kb.get("personality"):
    p = kb["personality"]
    personality_context = f"""
PERSONALITY INSIGHTS (from Personality Agent):
- Core Traits: {", ".join(p["core_traits"])}
...
```

Agents intelligently use previous outputs to ensure consistency.

### 7. Model Used

All agents use the same model:
```python
model = "claude-haiku-4-5-20251001"  # In every subagent
```

This is Haiku for speed and cost efficiency.

---

## 11. EXAMPLE CHARACTER DATA

From actual run (character_id: 113eab3b-d544-4e69-99a8-e2d58f7c4e06):

### Character: Maya Chen

**Personality Output (Checkpoint #1):**
- Core traits: Analytical Observer, Romantic Pragmatist, Fiercely Independent, Introspective to Paralysis, Compartmentalizer, Pattern-Seeker
- Emotional baseline: "Controlled Vigilance" (alert but subdued)
- Narrative: 3 paragraphs analyzing psychological profile with depth

**Relationships Output (Checkpoint #6):**
- Contains relationship array (though currently shows "Unknown" in example)
- Narrative: Analysis of relational patterns and how relationships change

**Final Profile (Checkpoint #7):**
- Consolidates all 6 agent outputs
- Includes empty visual data (images disabled)
- Metadata shows 7 total checkpoints, 10000 tokens, mode="balanced"

---

## 12. DEVELOPMENT TIMELINE & PERFORMANCE

From actual metadata:
- **Created at:** 2025-11-09T06:26:04.669807
- **Completed at:** 2025-11-09T06:31:36.026180
- **Total time:** ~5.5 minutes
- **Mode:** balanced
- **Regenerations:** 0

---

## CONCLUSION

The Character Identity Agent is a sophisticated system with:
- **3 distinct waves** with parallel agent execution (but sequential checkpoint approval)
- **7 total checkpoints** (image generation disabled)
- **Comprehensive checkpoint structure** with narrative + structured data
- **WebSocket-based real-time updates** with 5 message types
- **File-based storage** using JSON with clear directory structure
- **Polling-based approval system** without event architecture
- **Stubbed regeneration** (not yet implemented)
- **Rich prompt engineering** with mode-dependent depth

The system prioritizes human oversight at every step while leveraging parallel execution for efficiency.

