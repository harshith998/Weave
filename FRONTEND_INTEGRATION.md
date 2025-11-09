# Weave Frontend Integration Guide
**Complete Implementation Guide for External Developer**

**Last Updated:** November 8, 2025
**Backend Version:** 1.0
**Target:** React + TypeScript + Zustand + Tailwind

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Backend API Contracts](#backend-api-contracts)
3. [TypeScript Type Definitions](#typescript-type-definitions)
4. [Architecture & State Management](#architecture--state-management)
5. [Component Breakdown](#component-breakdown)
6. [WebSocket Implementation](#websocket-implementation)
7. [Integration with Existing IDE Interface](#integration-with-existing-ide-interface)
8. [Error Handling & Edge Cases](#error-handling--edge-cases)
9. [Testing Strategy](#testing-strategy)
10. [Known Backend Limitations](#known-backend-limitations)

---

## System Overview

### The 3-Agent Pipeline

Weave is a **3-level agent system** for AI video content creation:

```
┌────────────────────────────────────────────────────────────────┐
│  LEVEL 1: Entry Agent (Intro_General_Entry)                   │
│  ─────────────────────────────────────────────────────────    │
│  Purpose: Conversational intake - gather story concept        │
│  Input:   User describes video idea via chat                  │
│  Output:  Structured JSON with characters + scenes            │
│  Tech:    Claude Haiku, 2 tools (style image, finalize)       │
│  Session: In-memory (lost on backend restart)*                │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│  LEVEL 2: Character Identity Agent (Character_Identity)       │
│  ─────────────────────────────────────────────────────────    │
│  Purpose: Deep character development in 3 waves               │
│  Input:   Entry Agent JSON output                             │
│  Output:  7-8 checkpoints with psychological profiles         │
│  Tech:    6 subagents, AsyncAnthropic, WebSocket updates      │
│  Session: File-based persistence (survives restart)            │
│                                                                │
│  Wave 1: Personality + Backstory        (Checkpoints 1-2)     │
│  Wave 2: Voice + Physical + Story Arc   (Checkpoints 3-5)     │
│  Wave 3: Relationships + [Image Gen]    (Checkpoint 6-7)      │
│  Final:  Consolidation                  (Checkpoint 7 or 8)   │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│  LEVEL 3: Scene Creator Agent (Scene_Creator)                 │
│  ─────────────────────────────────────────────────────────    │
│  Purpose: Refine scenes with cinematography details           │
│  Input:   Entry Agent scenes + user refinement requests       │
│  Output:  Production-ready scene descriptions                 │
│  Tech:    3 modes (creative/analytical/deep_dive)             │
│  Session: In-memory (lost on backend restart)*                │
└────────────────────────────────────────────────────────────────┘
```

**\*Note:** Backend changes needed for Entry/Scene persistence - see [BACKEND_CHANGES_REQUIRED.md](BACKEND_CHANGES_REQUIRED.md)

---

## Backend API Contracts

### Base URLs

```typescript
const API_BASE_URL = 'http://localhost:8000';
const WS_BASE_URL = 'ws://localhost:8000';
```

---

### **1. Entry Agent Endpoints**

#### **POST `/api/entry/start`**

Start a new Entry Agent conversation session.

**Request Body:**
```typescript
{
  session_id?: string  // Optional - if omitted, backend generates UUID
}
```

**Response:**
```typescript
{
  session_id: string       // "550e8400-e29b-41d4-a716-446655440000"
  status: "active"
  message: string          // "Entry Agent session started. Ask me about your video concept!"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/entry/start \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

#### **POST `/api/entry/{session_id}/chat`**

Send a message to the Entry Agent.

**Request Body:**
```typescript
{
  message: string  // User's message
}
```

**Response (during conversation):**
```typescript
{
  response: string         // Agent's conversational response
  is_final: false
  output: null
  status: "active"
}
```

**Response (when finalized):**
```typescript
{
  response: string         // Contains "FINAL OUTPUT:\n\n{json}\n\n✓ Video concept captured!"
  is_final: true
  output: {
    characters: Array<{
      name: string
      appearance: string
      personality: string
      role: string
      importance?: string  // "Main character", "Side character", etc.
    }>
    storyline: {
      overview: string
      tone: string
      scenes: Array<{
        title: string
        description: string
        characters_involved: string[]
        setting: string
        mood: string
      }>
    }
    visual_style?: {
      description: string
      image_path: string   // Local path like "backend/output/style_examples/style_20251108_142532.png"
    }
  }
  status: "completed"
}
```

**Completion Detection:**
- Check if `response` contains the string `"FINAL OUTPUT:"`
- When `is_final === true`, the `output` field contains the structured JSON
- Entry Agent requires: ≥1 character, ≥3 scenes, 1 approved visual style image

**Example Conversation Flow:**
```
User: "I want to create a detective thriller"
Agent: "Great! Tell me about your main character..."

User: "A tough detective named Sarah who lost her partner"
Agent: "Perfect. What kind of scenes do you envision?"

User: "Opening crime scene, interrogation, final confrontation"
Agent: "Excellent! What visual style - realistic, animated, noir?"

User: "Dark noir style"
Agent: [Calls generate_style_image tool] "Here's a noir style example: [path]. Does this work?"

User: "Yes, that's perfect"
Agent: [Calls finalize_output tool] "FINAL OUTPUT:\n\n{...}\n\n✓ Video concept captured!"
```

---

#### **GET `/api/entry/{session_id}/status`**

Get Entry Agent session status.

**Response:**
```typescript
{
  session_id: string
  status: "active" | "completed"
  message_count: number    // Total messages exchanged
  output: object | null    // Structured output if completed, else null
}
```

---

### **2. Character Identity Endpoints**

#### **POST `/api/character/start`**

Start character development from Entry Agent output.

**Request Body:**
```typescript
{
  characters: Array<{
    name: string
    appearance: string
    personality: string
    role: string
    importance?: string
  }>
  storyline: {
    overview: string
    tone: string
    scenes: Array<{...}>
  }
  mode: "balanced" | "detailed" | "quick"  // Default: "balanced"
}
```

**Response:**
```typescript
{
  character_id: string         // "4ee6624f-8699-4a60-85a9-68d30a1c0398"
  status: "wave_1_started"
  message: "Character development initiated"
  checkpoint_count: 7          // Currently hardcoded to 7 (image gen disabled)
}
```

**CRITICAL:** After this endpoint returns, the backend **immediately starts running all 3 waves** in a background task. It does **NOT** wait for approval between waves. This is a **known limitation** that requires backend changes (see [BACKEND_CHANGES_REQUIRED.md](BACKEND_CHANGES_REQUIRED.md) Section 1).

**Workaround for MVP:** Frontend should connect to WebSocket immediately after calling this endpoint to receive real-time updates.

---

#### **GET `/api/character/{character_id}/status`**

Get current status of character development.

**Response:**
```typescript
{
  character_id: string
  current_wave: number         // 1, 2, or 3
  current_checkpoint: number   // 1-8
  status: string               // "wave_1_started", "wave_2_in_progress", "complete", etc.
  progress: {
    completed_checkpoints: number
    total_checkpoints: number
    current_checkpoint: number
  }
  agents: {
    personality: { status: "completed" | "in_progress" | "pending", wave: number }
    backstory_motivation: { ... }
    voice_dialogue: { ... }
    physical_description: { ... }
    story_arc: { ... }
    relationships: { ... }
    // image_generation: { ... }  // Only if IMAGE_GENERATION_ENABLED=true
  }
}
```

---

#### **GET `/api/character/{character_id}/checkpoint/{checkpoint_number}`**

Get specific checkpoint data. Checkpoint numbers: 1-7 (or 1-8 if image generation enabled).

**Response:**
```typescript
{
  checkpoint_number: number    // 1-7 (or 1-8)
  agent: string                // "personality", "backstory_motivation", etc.
  status: "pending" | "awaiting_approval" | "approved" | "rejected"
  output: {
    narrative: string          // Long-form narrative description (500-2000 chars)
    structured: {
      // Structure varies by checkpoint type:

      // Checkpoint 1 (Personality):
      core_traits: string[]
      fears: string[]
      secrets: string[]
      emotional_baseline: string
      triggers: string[]

      // Checkpoint 2 (Backstory):
      childhood_summary: string
      formative_experiences: Array<{ experience: string, impact: string }>
      education: string
      career_path: string
      internal_conflicts: Array<{ conflict: string, description: string }>

      // Checkpoint 3 (Voice):
      speaking_style: string
      vocabulary_level: string
      common_phrases: string[]
      accent_dialect: string
      speech_patterns: string[]

      // Checkpoint 4 (Physical):
      age: number
      height: string
      build: string
      distinctive_features: string[]
      posture_movement: string
      style_aesthetic: string

      // Checkpoint 5 (Story Arc):
      starting_point: string
      character_goal: string
      obstacles: string[]
      transformation: string
      ending_point: string

      // Checkpoint 6 (Relationships):
      key_relationships: Array<{ character: string, relationship_type: string, dynamics: string }>
      social_patterns: string
      trust_issues: string[]

      // Checkpoint 7/8 (Final Consolidation):
      // Full combined profile - see final_profile endpoint
    }
  }
  metadata: {
    wave: number               // 1, 2, or 3
    timestamp: string          // ISO 8601: "2025-11-09T06:26:44.402624"
    tokens_used: number        // ~1500-1800 per checkpoint
    agent_time_seconds: number // ~3-20 seconds per agent
  }
}
```

**Real Example from Backend:**
```json
{
  "checkpoint_number": 1,
  "agent": "personality",
  "status": "awaiting_approval",
  "output": {
    "narrative": "Maya Chen exists in a state of controlled contradiction—her mind operates like the probability timelines she navigates...",
    "structured": {
      "core_traits": [
        "Analytical Observer - Compulsively seeks patterns...",
        "Romantic Pragmatist - Holds wonder and skepticism in tension...",
        "Fiercely Independent - Equates self-reliance with safety..."
      ],
      "fears": [
        "Fundamental Meaninglessness - Her deepest existential terror...",
        "Irrelevance and Invisibility - Connected to her independence..."
      ],
      "secrets": [
        "She's already made a choice she's hiding from herself...",
        "She's terrified she's becoming like Dr. Venn..."
      ],
      "emotional_baseline": "Controlled Vigilance - Maya's default state is alert but subdued...",
      "triggers": [
        "Betrayal of Trust or Broken Promises - Specific trigger...",
        "Being Patronized or Having Her Intelligence Questioned..."
      ]
    }
  },
  "metadata": {
    "wave": 1,
    "timestamp": "2025-11-09T06:26:44.402624",
    "tokens_used": 1500,
    "agent_time_seconds": 19.86495
  }
}
```

---

#### **POST `/api/character/{character_id}/approve`**

Approve a checkpoint and allow continuation.

**Request Body:**
```typescript
{
  checkpoint: number  // Checkpoint number to approve (1-7)
}
```

**Response:**
```typescript
{
  message: "Checkpoint 1 approved. Proceeding to next agent."
  next_checkpoint: number
  status: "continuing"
}
```

**CRITICAL:** This endpoint currently **only updates metadata**. It does **NOT** control the execution flow because all waves run immediately when `/api/character/start` is called. Backend changes needed - see [BACKEND_CHANGES_REQUIRED.md](BACKEND_CHANGES_REQUIRED.md) Section 1.

---

#### **POST `/api/character/{character_id}/feedback`**

Reject checkpoint with feedback for regeneration.

**Request Body:**
```typescript
{
  checkpoint: number
  feedback: string   // "Make the character more extroverted and less guarded"
}
```

**Response:**
```typescript
{
  message: "Regenerating checkpoint 1 with feedback"
  status: "regenerating"
  estimated_time_seconds: number
}
```

**CRITICAL:** This endpoint is **NOT IMPLEMENTED** - it returns a response but doesn't actually regenerate. Backend changes needed - see [BACKEND_CHANGES_REQUIRED.md](BACKEND_CHANGES_REQUIRED.md) Section 5.

---

#### **GET `/api/character/{character_id}/final`**

Get final consolidated character profile.

**Response:**
```typescript
{
  character_id: string
  name: string
  version: string
  completed_at: string  // ISO 8601
  overview: {
    name: string
    role: string
    importance: number  // 1-5
    one_line: string
  }
  visual: {
    images: Array<{
      type: "portrait" | "full_body" | "action" | "expression"
      url: string  // "/placeholder_portrait.png" or actual image path
    }>
    style_notes: string
  }
  psychology: {
    core_traits: string[]
    fears: string[]
    secrets: string[]
    emotional_baseline: string
    triggers: string[]
  }
  physical_presence: {
    mannerisms: string[]
    body_language: string
    movement_style: string
    physical_quirks: string[]
  }
  voice: {
    speech_pattern: string
    verbal_tics: string[]
    vocabulary: string
    sample_dialogue: {
      confident: string
      vulnerable: string
      stressed: string
      sarcastic: string
    }
  }
  backstory_motivation: {
    timeline: Array<{ age: number, event: string }>
    formative_experiences: string[]
    goals: { surface: string, deep: string }
    internal_conflicts: string[]
  }
  narrative_arc: {
    role: string
    arc_type: string
    transformation_beats: Array<{ act: number, beat: string }>
    scene_presence: string[]
  }
  relationships: Array<{
    character: string
    type: string
    dynamic: string
    evolution: string
  }>
  metadata: {
    mode: "balanced" | "detailed" | "quick"
    development_time_minutes: number
    total_checkpoints: number
    regenerations: number
    total_tokens: number
  }
}
```

---

### **3. Scene Creator Endpoints**

#### **POST `/api/scene/start`**

Start a Scene Creator session.

**Request Body:**
```typescript
{
  project_id?: string           // Default: "default"
  mode?: "creative_overview" | "analytical" | "deep_dive"  // Default: "creative_overview"
}
```

**Response:**
```typescript
{
  project_id: string
  status: "active"
  mode: string
  message: "Scene Creator started in creative_overview mode. Describe your first scene!"
}
```

---

#### **POST `/api/scene/{project_id}/chat`**

Send message to Scene Creator.

**Request Body:**
```typescript
{
  message: string
}
```

**Response:**
```typescript
{
  response: string       // Agent's conversational response
  mode: "creative_overview" | "analytical" | "deep_dive"
  scene_count: number    // Number of scenes currently tracked
}
```

**Special Command:** Typing `"start"` as the first message shows all scenes from Entry Agent output (if they were passed to Scene Creator - see limitation below).

**CRITICAL:** Scene Creator currently **does NOT automatically access Entry Agent output**. You must pass the scenes manually or implement backend changes. See [BACKEND_CHANGES_REQUIRED.md](BACKEND_CHANGES_REQUIRED.md).

**Workaround:** Initialize Scene Creator with Entry Agent storyline in the first message:
```typescript
const entryOutput = // ... from Entry Agent
const firstMessage = `Here are the scenes to refine:\n\n${JSON.stringify(entryOutput.storyline.scenes, null, 2)}\n\nLet's start with scene 1.`;

await sceneAgent.chat(projectId, firstMessage);
```

---

#### **POST `/api/scene/{project_id}/mode`**

Switch Scene Creator mode.

**Request Body:**
```typescript
{
  mode: "creative_overview" | "analytical" | "deep_dive"
}
```

**Response:**
```typescript
{
  success: boolean
  mode: string
  message: "Mode switched to analytical"
}
```

**Mode Differences:**
- **creative_overview:** Fast, high-level scene descriptions
- **analytical:** Detailed cinematography, lighting, camera angles
- **deep_dive:** Maximum detail, shot-by-shot breakdown

---

#### **GET `/api/scene/{project_id}/status`**

Get Scene Creator session status.

**Response:**
```typescript
{
  project_id: string
  status: "active" | "completed"
  mode: string
  message_count: number
  scene_count: number
}
```

---

### **4. WebSocket Connection**

#### **WS `/ws/character/{character_id}`**

Real-time updates during character development.

**Connection:**
```typescript
const ws = new WebSocket(`ws://localhost:8000/ws/character/${characterId}`);
```

**Keep-Alive Protocol:**
- Frontend sends `"ping"` (string) every 30 seconds
- Backend responds with `"pong"` (string)

**Message Types Received:**

```typescript
// 1. Wave Started
{
  type: "wave_started"
  wave: number                    // 1, 2, or 3
  agents: string[]                // ["personality", "backstory_motivation"]
}

// 2. Agent Completed
{
  type: "agent_completed"
  agent: string                   // "personality"
  wave: number
  time_seconds: number            // 19.86495
}

// 3. Checkpoint Ready
{
  type: "checkpoint_ready"
  checkpoint: number              // 1-7
  agent: string                   // "personality"
}

// 4. Wave Complete
{
  type: "wave_complete"
  wave: number
  agents_completed: string[]      // ["personality", "backstory_motivation"]
  next_wave?: number              // 2 (if not final wave)
}

// 5. Awaiting Approval (sent after each wave)
{
  type: "awaiting_approval"
  wave: number
  checkpoints: number[]           // [1, 2] for wave 1
}

// 6. Character Complete
{
  type: "character_complete"
  character_id: string
  total_checkpoints: number       // 7 or 8
}

// 7. Error
{
  type: "error"
  message: string
  agent?: string
}
```

**Message Sequence Example:**
```
1. wave_started { wave: 1, agents: ["personality", "backstory_motivation"] }
2. agent_completed { agent: "personality", wave: 1, time_seconds: 19.8 }
3. checkpoint_ready { checkpoint: 1, agent: "personality" }
4. agent_completed { agent: "backstory_motivation", wave: 1, time_seconds: 15.2 }
5. checkpoint_ready { checkpoint: 2, agent: "backstory_motivation" }
6. wave_complete { wave: 1, agents_completed: [...], next_wave: 2 }
7. awaiting_approval { wave: 1, checkpoints: [1, 2] }  // But doesn't actually wait!
8. wave_started { wave: 2, agents: ["voice_dialogue", "physical_description", "story_arc"] }
... (continues through wave 3)
9. character_complete { character_id: "...", total_checkpoints: 7 }
```

**Error Handling:**
- If WebSocket disconnects, try to reconnect with exponential backoff
- Backend does **NOT** support mid-development resume (limitation)
- If development fails, character metadata will have `status: "failed"` and `error` field

---

### **5. Project Management Endpoints (Optional)**

These endpoints exist but are **not required** for MVP. Use if you want project-level organization.

#### **POST `/api/projects`**
#### **GET `/api/projects`**
#### **GET `/api/projects/{project_id}`**

See [backend/api/server.py:482-511](backend/api/server.py#L482-L511) for details.

---

## TypeScript Type Definitions

Create `frontend/src/types/weave.ts`:

```typescript
// ============================================================================
// ENTRY AGENT TYPES
// ============================================================================

export interface Character {
  name: string;
  appearance: string;
  personality: string;
  role: string;
  importance?: string;
}

export interface Scene {
  title: string;
  description: string;
  characters_involved: string[];
  setting: string;
  mood: string;
}

export interface Storyline {
  overview: string;
  tone: string;
  scenes: Scene[];
}

export interface VisualStyle {
  description: string;
  image_path: string;
}

export interface EntryAgentOutput {
  characters: Character[];
  storyline: Storyline;
  visual_style?: VisualStyle;
}

export interface EntryChatResponse {
  response: string;
  is_final: boolean;
  output: EntryAgentOutput | null;
  status: 'active' | 'completed';
}

// ============================================================================
// CHARACTER IDENTITY TYPES
// ============================================================================

export interface CheckpointOutput {
  narrative: string;
  structured: Record<string, any>;  // Varies by checkpoint type
}

export interface Checkpoint {
  checkpoint_number: number;
  agent: string;
  status: 'pending' | 'awaiting_approval' | 'approved' | 'rejected';
  output: CheckpointOutput;
  metadata: {
    wave: number;
    timestamp: string;
    tokens_used: number;
    agent_time_seconds: number;
  };
}

export interface CharacterStatus {
  character_id: string;
  current_wave: number;
  current_checkpoint: number;
  status: string;
  progress: {
    completed_checkpoints: number;
    total_checkpoints: number;
    current_checkpoint: number;
  };
  agents: Record<string, any>;
}

export interface FinalCharacterProfile {
  character_id: string;
  name: string;
  version: string;
  completed_at: string;
  overview: {
    name: string;
    role: string;
    importance: number;
    one_line: string;
  };
  visual: {
    images: Array<{ type: string; url: string }>;
    style_notes: string;
  };
  psychology: Record<string, any>;
  physical_presence: Record<string, any>;
  voice: Record<string, any>;
  backstory_motivation: Record<string, any>;
  narrative_arc: Record<string, any>;
  relationships: Array<Record<string, any>>;
  metadata: {
    mode: string;
    development_time_minutes: number;
    total_checkpoints: number;
    regenerations: number;
    total_tokens: number;
  };
}

// ============================================================================
// WEBSOCKET TYPES
// ============================================================================

export type WebSocketMessage =
  | { type: 'wave_started'; wave: number; agents: string[] }
  | { type: 'agent_completed'; agent: string; wave: number; time_seconds: number }
  | { type: 'checkpoint_ready'; checkpoint: number; agent: string }
  | { type: 'wave_complete'; wave: number; agents_completed: string[]; next_wave?: number }
  | { type: 'awaiting_approval'; wave: number; checkpoints: number[] }
  | { type: 'character_complete'; character_id: string; total_checkpoints: number }
  | { type: 'error'; message: string; agent?: string };

// ============================================================================
// SCENE CREATOR TYPES
// ============================================================================

export type SceneMode = 'creative_overview' | 'analytical' | 'deep_dive';

export interface SceneChatResponse {
  response: string;
  mode: SceneMode;
  scene_count: number;
}
```

---

## Architecture & State Management

### Recommended Stack

- **Framework:** React 18+ with TypeScript
- **State:** Zustand (already in project: `frontend/package.json:18`)
- **Styling:** Tailwind CSS (already configured with custom design tokens)
- **Animations:** Framer Motion (already in project: `frontend/package.json:14`)
- **HTTP:** Axios or native fetch
- **WebSocket:** Native WebSocket API

### State Structure (Zustand Store)

```typescript
// frontend/src/store/useWeaveStore.ts

import { create } from 'zustand';

interface WeaveStore {
  // Entry Agent State
  entrySessionId: string | null;
  entryOutput: EntryAgentOutput | null;
  entryMessages: Message[];
  entryIsComplete: boolean;

  // Character Development State
  characterId: string | null;
  characterName: string;
  currentWave: number;
  checkpoints: Checkpoint[];
  wsConnection: WebSocket | null;
  developmentComplete: boolean;

  // Scene Creator State
  sceneProjectId: string | null;
  sceneMode: SceneMode;
  sceneMessages: Message[];

  // UI State
  currentView: 'entry' | 'character' | 'scene' | 'tree';
  isLoading: boolean;
  error: string | null;

  // Actions
  setEntrySessionId: (id: string) => void;
  setEntryOutput: (output: EntryAgentOutput) => void;
  addEntryMessage: (message: Message) => void;

  setCharacterId: (id: string) => void;
  addCheckpoint: (checkpoint: Checkpoint) => void;
  updateCheckpoint: (num: number, updates: Partial<Checkpoint>) => void;
  setCurrentWave: (wave: number) => void;
  connectWebSocket: (characterId: string) => void;
  disconnectWebSocket: () => void;

  setSceneProjectId: (id: string) => void;
  setSceneMode: (mode: SceneMode) => void;
  addSceneMessage: (message: Message) => void;

  setCurrentView: (view: string) => void;
  setError: (error: string | null) => void;

  reset: () => void;
}
```

---

## Component Breakdown

### Existing IDE Interface

The current frontend (`frontend/src/App.tsx`) has:
- **TopBar:** Navigation and status
- **LeftPanel:** Tree view / conversation list
- **RightPanel:** Chat interface
- **StatusBar:** Bottom status bar
- **TreeView:** Hierarchical node visualization
- **FlowChart:** ReactFlow-based workflow diagram

### Integration Strategy: Add Weave Pipeline to Tree

**Option A (Recommended):** Add Weave pipeline as **collapsible nodes in the existing tree view**.

```
Project Root
├─ Entry Agent Session
│  ├─ Chat History
│  └─ Output JSON ✓
│
├─ Character Development
│  ├─ Wave 1: Foundation
│  │  ├─ Checkpoint 1: Personality [Awaiting Approval]
│  │  └─ Checkpoint 2: Backstory [Pending]
│  ├─ Wave 2: Expression
│  │  ├─ Checkpoint 3: Voice [Pending]
│  │  ├─ Checkpoint 4: Physical [Pending]
│  │  └─ Checkpoint 5: Story Arc [Pending]
│  └─ Wave 3: Social
│     └─ Checkpoint 6: Relationships [Pending]
│
└─ Scene Creator
   ├─ Scene 1: Opening
   ├─ Scene 2: Midpoint
   └─ Scene 3: Climax
```

**Option B:** Create **dedicated tab** for Weave pipeline (separate from tree view).

### New Components to Build

#### 1. **EntryAgentChat.tsx**

Simple chat interface for Entry Agent.

**Features:**
- Text input + send button
- Message list (user/agent/system messages)
- Auto-scroll to latest message
- Detect "FINAL OUTPUT:" to trigger completion
- Display style image when generated
- "Continue to Character Development" button when complete

**Props:**
```typescript
interface EntryAgentChatProps {
  onComplete: (output: EntryAgentOutput) => void;
}
```

**API Calls:**
- On mount: `POST /api/entry/start`
- On send: `POST /api/entry/{session_id}/chat`

**UI States:**
- Loading (waiting for agent response)
- Active (conversation ongoing)
- Complete (finalized output received)

---

#### 2. **CharacterDevelopment.tsx**

Container component for character development flow.

**Features:**
- Display current wave and progress (e.g., "Wave 2/3 - 5/7 checkpoints complete")
- List of checkpoints with status badges
- Real-time updates via WebSocket
- Approval/rejection UI for each checkpoint

**Props:**
```typescript
interface CharacterDevelopmentProps {
  entryOutput: EntryAgentOutput;
  onComplete: (profile: FinalCharacterProfile) => void;
}
```

**API Calls:**
- On mount: `POST /api/character/start` (triggers background development)
- WebSocket: Connect to `/ws/character/{character_id}`
- On checkpoint ready: `GET /api/character/{character_id}/checkpoint/{num}`
- On approval: `POST /api/character/{character_id}/approve`
- On completion: `GET /api/character/{character_id}/final`

**UI States:**
- Initializing (waiting for first wave)
- Wave in progress (show spinner + agent status)
- Checkpoint ready (show approval/rejection UI)
- Complete (show final profile summary)

---

#### 3. **CheckpointReviewCard.tsx**

Claude Code-style approval UI for individual checkpoints.

**Design Inspiration:**
```
┌─────────────────────────────────────────────────────────┐
│ Checkpoint #1: Personality                    [Wave 1] │
│ ────────────────────────────────────────────────────── │
│                                                          │
│ NARRATIVE DESCRIPTION                                    │
│ Maya Chen exists in a state of controlled               │
│ contradiction—her mind operates like the probability...  │
│                                                          │
│ [Show Full ▼]                                            │
│                                                          │
│ STRUCTURED DATA                                          │
│ ├─ core_traits: [6 items]                               │
│ ├─ fears: [4 items]                                     │
│ ├─ secrets: [3 items]                                   │
│ ├─ emotional_baseline: "Controlled Vigilance..."        │
│ └─ triggers: [5 items]                                  │
│                                                          │
│ [View JSON]                                              │
│                                                          │
│ ────────────────────────────────────────────────────── │
│ [✓ Approve] [✗ Reject & Provide Feedback]               │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Collapsible narrative (show first 500 chars, expand for full)
- Structured data preview (key-value pairs)
- "View JSON" button for raw data
- Approve button (green) - calls API and moves to next checkpoint
- Reject button (red) - shows feedback textarea
- Feedback submission (currently not implemented in backend - show warning)

**Props:**
```typescript
interface CheckpointReviewCardProps {
  checkpoint: Checkpoint;
  onApprove: () => void;
  onReject: (feedback: string) => void;
}
```

---

#### 4. **CharacterViewer.tsx**

Display final character profile in a beautiful, comprehensive view.

**Features:**
- Character overview card (name, role, one-line summary)
- Visual section (4 character images in grid)
- Tabbed interface for different aspects:
  - Psychology
  - Physical Presence
  - Voice & Dialogue
  - Backstory & Motivation
  - Narrative Arc
  - Relationships
- Metadata footer (tokens used, time taken, regenerations)

**Props:**
```typescript
interface CharacterViewerProps {
  profile: FinalCharacterProfile;
  onEdit?: () => void;  // Optional: trigger regeneration
}
```

**Layout:**
```
┌──────────────────────────────────────────────┐
│  Maya Chen                        [Importance: 5] │
│  Protagonist - Digital archivist with probability │
│  timeline abilities                               │
├──────────────────────────────────────────────┤
│  VISUAL                                           │
│  [Portrait] [Full Body] [Action] [Expression]     │
├──────────────────────────────────────────────┤
│  [Psychology] [Physical] [Voice] [Backstory] [Arc] [Relationships] │
│  ──────────────────────────────────────────  │
│  Core Traits:                                     │
│  • Analytical Observer - Compulsively seeks...    │
│  • Romantic Pragmatist - Holds wonder and...      │
│  ...                                              │
└──────────────────────────────────────────────┘
```

---

#### 5. **SceneCreatorChat.tsx**

Chat interface for Scene Creator with mode switching.

**Features:**
- Mode selector (3 buttons: Creative / Analytical / Deep Dive)
- Chat interface (similar to Entry Agent)
- Scene list display (when user types "start")
- Real-time refinement

**Props:**
```typescript
interface SceneCreatorChatProps {
  entryScenes: Scene[];
  onComplete?: () => void;
}
```

**API Calls:**
- On mount: `POST /api/scene/start`
- On mode switch: `POST /api/scene/{project_id}/mode`
- On send: `POST /api/scene/{project_id}/chat`

---

## WebSocket Implementation

### Connection Management

```typescript
// frontend/src/services/websocket.ts

export class CharacterWebSocket {
  private ws: WebSocket | null = null;
  private pingInterval: NodeJS.Timeout | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  constructor(
    private characterId: string,
    private onMessage: (msg: WebSocketMessage) => void,
    private onError?: (error: Event) => void,
    private onClose?: () => void
  ) {}

  connect() {
    this.ws = new WebSocket(`ws://localhost:8000/ws/character/${this.characterId}`);

    this.ws.onopen = () => {
      console.log('[WS] Connected to character', this.characterId);
      this.reconnectAttempts = 0;

      // Start ping interval
      this.pingInterval = setInterval(() => {
        if (this.ws?.readyState === WebSocket.OPEN) {
          this.ws.send('ping');
        }
      }, 30000);
    };

    this.ws.onmessage = (event) => {
      if (event.data === 'pong') return;

      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.onMessage(message);
      } catch (e) {
        console.error('[WS] Parse error:', e);
      }
    };

    this.ws.onerror = (error) => {
      console.error('[WS] Error:', error);
      this.onError?.(error);
    };

    this.ws.onclose = () => {
      console.log('[WS] Closed');

      if (this.pingInterval) {
        clearInterval(this.pingInterval);
        this.pingInterval = null;
      }

      this.onClose?.();

      // Auto-reconnect with exponential backoff
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
        console.log(`[WS] Reconnecting in ${delay}ms...`);
        setTimeout(() => this.connect(), delay);
        this.reconnectAttempts++;
      }
    };
  }

  disconnect() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
```

### Usage in Component

```typescript
// In CharacterDevelopment.tsx

useEffect(() => {
  if (!characterId) return;

  const wsClient = new CharacterWebSocket(
    characterId,
    (message) => {
      switch (message.type) {
        case 'wave_started':
          setCurrentWave(message.wave);
          setStatus(`Wave ${message.wave} started: ${message.agents.join(', ')}`);
          break;

        case 'checkpoint_ready':
          fetchCheckpoint(message.checkpoint);
          break;

        case 'character_complete':
          setDevelopmentComplete(true);
          fetchFinalProfile();
          break;

        case 'error':
          setError(message.message);
          break;
      }
    },
    (error) => setError('WebSocket connection error'),
    () => console.log('WebSocket disconnected')
  );

  wsClient.connect();

  return () => wsClient.disconnect();
}, [characterId]);
```

---

## Integration with Existing IDE Interface

### Modify Existing Files

#### **1. Update `frontend/src/store/useStore.ts`**

Add Weave-specific state to the existing Zustand store:

```typescript
// Add to existing interface
interface WeaveStore {
  // ... existing tree/chat state ...

  // Weave state
  weaveEntrySessionId: string | null;
  weaveEntryOutput: EntryAgentOutput | null;
  weaveCharacterId: string | null;
  weaveCheckpoints: Checkpoint[];
  weaveCurrentWave: number;

  setWeaveEntrySessionId: (id: string) => void;
  setWeaveEntryOutput: (output: EntryAgentOutput) => void;
  setWeaveCharacterId: (id: string) => void;
  addWeaveCheckpoint: (checkpoint: Checkpoint) => void;
  setWeaveCurrentWave: (wave: number) => void;
}
```

#### **2. Update `frontend/src/components/layout/LeftPanel.tsx`**

Add a new tab or section for "Weave Pipeline":

```typescript
// Add to tab options
const tabs = ['tree', 'timeline', 'weave'] as const;

// In render:
{activeTab === 'weave' && <WeaveTreeView />}
```

#### **3. Create `frontend/src/components/weave/WeaveTreeView.tsx`**

Tree visualization specific to Weave pipeline:

```typescript
export const WeaveTreeView = () => {
  const entryOutput = useStore(state => state.weaveEntryOutput);
  const characterId = useStore(state => state.weaveCharacterId);
  const checkpoints = useStore(state => state.weaveCheckpoints);

  return (
    <div className="weave-tree">
      <WeaveNode
        title="Entry Agent"
        status={entryOutput ? 'completed' : 'in_progress'}
        onClick={() => setCurrentView('entry')}
      />

      {entryOutput && (
        <WeaveNode
          title="Character Development"
          status={characterId ? 'in_progress' : 'pending'}
          onClick={() => setCurrentView('character')}
        >
          {checkpoints.map(cp => (
            <CheckpointNode
              key={cp.checkpoint_number}
              checkpoint={cp}
            />
          ))}
        </WeaveNode>
      )}

      {/* Scene Creator node */}
    </div>
  );
};
```

#### **4. Update `frontend/src/components/layout/RightPanel.tsx`**

Add view switching for Weave components:

```typescript
const currentView = useStore(state => state.currentView);

return (
  <div className="right-panel">
    {currentView === 'entry' && <EntryAgentChat />}
    {currentView === 'character' && <CharacterDevelopment />}
    {currentView === 'scene' && <SceneCreatorChat />}
    {currentView === 'tree' && <ChatMessages />}  // Existing
  </div>
);
```

---

## Error Handling & Edge Cases

### Common Error Scenarios

| Error | Cause | Solution |
|-------|-------|----------|
| "Session not found" | Backend restarted (Entry/Scene sessions lost) | Show warning, allow user to start new session |
| "Active session not found" | Approval called but character dev already complete | Fetch status first, disable approve button if complete |
| WebSocket disconnects mid-development | Network issue or backend restart | Auto-reconnect with exponential backoff, show "Reconnecting..." message |
| Checkpoint fetch returns 404 | Checkpoint not yet generated | Poll status endpoint until checkpoint exists, then fetch |
| "ANTHROPIC_API_KEY not found" | Backend .env misconfigured | Show clear error: "Backend configuration error - check ANTHROPIC_API_KEY" |
| Image generation disabled | IMAGE_GENERATION_ENABLED=false | Show 7 checkpoints instead of 8, skip checkpoint 7 |

### Defensive Programming

```typescript
// Always check if session exists before API calls
const chat = async (message: string) => {
  if (!sessionId) {
    const newSession = await entryAgent.start();
    setSessionId(newSession.session_id);
  }

  await entryAgent.chat(sessionId!, message);
};

// Handle missing checkpoints
const fetchCheckpoint = async (num: number) => {
  try {
    const checkpoint = await characterAgent.getCheckpoint(characterId, num);
    addCheckpoint(checkpoint);
  } catch (error) {
    if (error.response?.status === 404) {
      // Checkpoint not ready yet, wait and retry
      setTimeout(() => fetchCheckpoint(num), 1000);
    } else {
      setError('Failed to fetch checkpoint');
    }
  }
};

// Validate Entry Agent output before passing to Character Agent
const validateEntryOutput = (output: any): boolean => {
  if (!output.characters || output.characters.length === 0) return false;
  if (!output.storyline || !output.storyline.scenes) return false;
  if (output.storyline.scenes.length < 3) return false;
  return true;
};
```

---

## Testing Strategy

### Unit Tests

- API service methods (mock axios/fetch)
- WebSocket connection handling (mock WebSocket)
- State management (Zustand actions)
- Type validations

### Integration Tests

- Entry Agent complete flow (start → chat → finalize)
- Character development flow (start → WebSocket → checkpoints)
- Approval/rejection workflows

### E2E Tests (Cypress/Playwright)

```typescript
// Example E2E test
describe('Weave Pipeline E2E', () => {
  it('completes full pipeline from entry to scene creator', () => {
    // 1. Entry Agent
    cy.visit('/');
    cy.get('[data-testid="entry-input"]').type('Create a detective thriller');
    cy.get('[data-testid="send-button"]').click();
    cy.contains('Tell me about your main character').should('exist');

    // ... more chat messages ...

    cy.contains('FINAL OUTPUT').should('exist');
    cy.get('[data-testid="start-character-dev"]').click();

    // 2. Character Development
    cy.contains('Wave 1 started').should('exist');
    cy.get('[data-testid="checkpoint-1"]', { timeout: 30000 }).should('exist');
    cy.get('[data-testid="approve-btn"]').click();

    // ... continue through waves ...

    cy.contains('Character development complete').should('exist');
    cy.get('[data-testid="start-scene-creator"]').click();

    // 3. Scene Creator
    cy.get('[data-testid="scene-input"]').type('start');
    cy.contains('Opening Crime Scene').should('exist');
  });
});
```

---

## Known Backend Limitations

### **CRITICAL:** These require backend changes before full functionality

See [BACKEND_CHANGES_REQUIRED.md](BACKEND_CHANGES_REQUIRED.md) for detailed implementation plans.

| Limitation | Impact | Workaround |
|------------|--------|-----------|
| **No approval gates** | All 3 waves run immediately without waiting for approval | Show all checkpoints as they arrive, make approve/reject buttons informational only |
| **No regeneration** | Rejection feedback doesn't actually regenerate | Disable feedback UI or show "Coming soon" message |
| **Entry/Scene sessions in-memory** | Lost on backend restart | Store session IDs in localStorage, detect stale sessions and restart |
| **No importance-based selection** | Only first character is developed | Frontend selects highest-importance character and passes only that one to `/api/character/start` |
| **No resume-from-failure** | If backend crashes mid-wave, must restart | Show error message, allow user to start new character development |
| **Scene Creator doesn't auto-access Entry output** | Must manually pass scenes | Include Entry output in first Scene Creator message |

### MVP Approach

For an MVP frontend that works **today** (without backend changes):

1. ✅ **Entry Agent:** Fully functional as-is
2. ⚠️ **Character Development:** Shows real-time progress, but approval buttons don't control flow - they just mark checkpoints as "reviewed"
3. ⚠️ **Scene Creator:** Requires manual initialization with Entry scenes
4. ❌ **Regeneration:** Disable this feature until backend implements it

### Post-MVP (After Backend Changes)

Once backend changes are complete:

1. ✅ Approval buttons actually pause execution
2. ✅ Rejection triggers real regeneration
3. ✅ Sessions persist across restarts
4. ✅ Intelligent character selection based on importance
5. ✅ Resume from failure

---

## Implementation Checklist

### Phase 1: Core Integration (MVP)

- [ ] Set up TypeScript types (`types/weave.ts`)
- [ ] Create API service layer (`services/weaveApi.ts`)
- [ ] Extend Zustand store with Weave state
- [ ] Build Entry Agent chat component
- [ ] Build Character Development container
- [ ] Build Checkpoint review cards
- [ ] Implement WebSocket connection
- [ ] Add Weave tree nodes to LeftPanel
- [ ] Add view switching to RightPanel
- [ ] Test full pipeline flow manually

### Phase 2: Polish

- [ ] Add loading states and spinners
- [ ] Add error messages and recovery
- [ ] Build Character Viewer component
- [ ] Build Scene Creator chat component
- [ ] Add animations (Framer Motion)
- [ ] Style with existing design tokens
- [ ] Add keyboard shortcuts
- [ ] Add progress indicators

### Phase 3: Advanced Features (Post-Backend Changes)

- [ ] Implement real approval gates
- [ ] Implement regeneration UI
- [ ] Add session persistence
- [ ] Add character importance UI
- [ ] Add retry-from-failure logic
- [ ] Add batch character development

---

## Questions for Clarification

Before starting implementation, confirm:

1. **UI Framework:** Continue using existing React + Tailwind setup?
2. **Design System:** Use existing design tokens from `DESIGN_SYSTEM.md`?
3. **Tree Integration:** Add Weave as nodes in existing tree, or separate tab?
4. **MVP Scope:** Build with current backend limitations and upgrade later?
5. **Image Display:** How to handle `image_path` from backend (local file path)? Need image server or base64 encoding?
6. **Multi-Character:** Should UI support multiple characters in parallel, or one at a time for MVP?
7. **Session Persistence:** Use localStorage for session IDs, or wait for backend changes?

---

## Support & Contact

For questions about this guide or backend implementation:
- Backend Code: `/Users/iceca/Documents/Weave/backend/`
- API Server: `backend/api/server.py`
- Agent Implementations: `backend/agents/`
- Backend Changes Doc: `BACKEND_CHANGES_REQUIRED.md`

**Good luck building! This is a complex but well-architected system. The backend is solid - the frontend just needs to wire it all together beautifully.** 🚀
