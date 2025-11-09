# Scene Creator Agent - Quick Start Guide

## Overview

The Scene Creator Agent is responsible for creating cinematic scenes with continuity, cinematography, and narrative control for Weave's video generation system.

## Three Personality Modes

The Scene Creator operates in one of three modes, each with distinct personalities and workflows:

### 1. Creative Overview Mode (Fast)
- **Use when:** Quick prototyping, exploratory creation
- **Personality:** Confident, creatively-driven director
- **Approach:** 2-3 initial concepts, rapid execution
- **Speed:** FAST

### 2. Analytical Mode (Rigorous)
- **Use when:** Production-quality content, consistency-critical projects
- **Personality:** Meticulous quality guardian
- **Approach:** Comprehensive pre/post validation
- **Speed:** MEDIUM-SLOW (thorough)

### 3. Deep Dive Mode (Collaborative)
- **Use when:** Precise creative control, learning workflows
- **Personality:** Patient creative partner
- **Approach:** 2 options for every decision, modular approval
- **Speed:** SLOW (many checkpoints)

## How to Use

### Starting the Agent

```bash
cd backend
python main.py
```

Navigate to Scene Creator:
```
You: /next
You: /next  # Now at Scene_Creator agent
```

### Switching Modes

While in Scene Creator:
```
You: /mode creative_overview
You: /mode analytical
You: /mode deep_dive
```

**Note:** Conversation history is preserved when switching modes!

### Example Workflow (Creative Overview)

```
You: I need a tense confrontation scene between two characters

Agent: [Uses cinematography_designer tool to generate 2 concepts]
[Presents Concept A and Concept B with visual descriptions]
[Generates reference images using Nano Banana]

You: I like Concept A

Agent: [Builds complete scene JSON]
[Quick validation]
[Generates storyboard frames]
[Sends checkpoint: "Ready to generate"]
```

### Example Workflow (Analytical)

```
You: Add a warehouse entry scene

Agent: [Builds scene JSON]
[Runs comprehensive pre-validation]
[Detects continuity issue with previous scene]

CRITICAL ISSUE FOUND:
Previous scene ended at night. This scene specifies daytime.
Character appearance inconsistency.

Options:
A) Add transition scene
B) Change to night
C) Revise previous scene

You: Option B

Agent: [Rebuilds scene as night scene]
[Re-validates - PASS]
[Sends checkpoint: "Pre-validation passed"]
```

## Tools Available

The agent has access to 7 specialized subagents:

1. **cinematography_designer** - Generate shot sequences
2. **aesthetic_generator** - Create color palettes, lighting moods
3. **scene_validator** - Validate continuity and logic
4. **reference_image_generator** - Generate images with Nano Banana
5. **timeline_validator** - Check timeline coherence
6. **checkpoint_manager** - Send progress updates
7. **visual_continuity_checker** - Analyze generated videos

## File Structure

```
backend/
├── agents/Scene_Creator/
│   ├── agent.py              # Main agent
│   ├── tools.py              # Tool definitions
│   ├── modes/                # 3 mode system prompts
│   └── subagents/            # 7 specialized subagents
├── state/
│   ├── projects/             # Project state JSONs
│   └── scenes/               # Scene JSONs
└── utils/
    └── state_manager.py      # JSON file handling
```

## Environment Setup

Required environment variables:
```bash
export ANTHROPIC_API_KEY="your-key-here"
export GEMINI_API_KEY="your-gemini-key-here"  # For Nano Banana
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Scene JSON Output

Scenes are saved to: `backend/state/scenes/{project_id}_scene_{number}.json`

Contains:
- Scene metadata
- Narrative description
- Cinematography specifications
- Lighting and color design
- Audio design
- Continuity tracking
- Veo generation parameters
- Production notes

## Next Steps

- See [MODE_COMPARISON.md](MODE_COMPARISON.md) for detailed mode comparison
- See [SUBAGENT_REFERENCE.md](SUBAGENT_REFERENCE.md) for tool details
- See [SCENE_JSON_SCHEMA.md](SCENE_JSON_SCHEMA.md) for complete schema
