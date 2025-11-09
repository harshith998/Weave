# Scene Creator Agent

**Version:** 1.0
**Status:** Production Ready
**Agent Level:** 3 (Scene_Creator)

## Purpose

The Scene Creator Agent handles all aspects of scene creation for Weave's video generation pipeline:

- Scene narrative and emotional design
- Cinematography (camera work, shot composition)
- Lighting and color aesthetics
- Scene continuity validation
- Timeline coherence
- Integration with character data
- Reference image generation

## Three Operating Modes

### 1. Creative Overview
Fast, creatively-driven mode for quick iterations.

**System Prompt:** `modes/creative_overview.py`
**Use Case:** Rapid prototyping, exploratory creation

### 2. Analytical
Validation-focused mode for production quality.

**System Prompt:** `modes/analytical.py`
**Use Case:** High-quality, continuity-critical projects

### 3. Deep Dive
Maximum collaboration mode with granular control.

**System Prompt:** `modes/deep_dive.py`
**Use Case:** Precise creative control, learning

## Mode Switching

Users can switch modes mid-creation:
```
/mode creative_overview
/mode analytical
/mode deep_dive
```

Conversation history is preserved across mode switches.

## Architecture

```
SceneCreatorAgent (agent.py)
    │
    ├─ Loads current mode from project state
    ├─ Dynamically selects system prompt
    ├─ Tool calling loop with 7 specialized subagents
    └─ Mode switching with conversation preservation
```

## Specialized Subagents

All implemented in `subagents/subagent.py`:

1. **cinematography_designer** - Shot sequences, camera work
2. **aesthetic_generator** - Color, lighting, mood
3. **scene_validator** - Pre/post validation
4. **reference_image_generator** - Nano Banana integration
5. **timeline_validator** - Timeline coherence
6. **checkpoint_manager** - Progress updates
7. **visual_continuity_checker** - Generated video analysis

## Tools Definition

All tools defined in Anthropic format in `tools.py`.

Each tool routes to its corresponding subagent function.

## State Management

Uses `utils/state_manager.py` for:
- Reading/writing project state
- Reading/writing scene JSONs
- Mode persistence
- Global continuity tracking

## Integration Points

**Receives data from:**
- Character_Identity agent (character appearance, state)
- Intro_General_Entry agent (orchestration commands)

**Sends checkpoints to:**
- Intro_General_Entry agent (orchestrator)
- Combiner agent (future - scene+character data merge)

## File Outputs

**Scene JSONs:** `backend/state/scenes/{project_id}_scene_{number}.json`

Contains complete scene specification ready for video generation.

## Dependencies

- `anthropic` - Main LLM (Claude Sonnet 4.5)
- `google-genai` - Nano Banana image generation
- `pillow` - Image processing

## Development

### Adding a New Subagent

1. Implement function in `subagents/subagent.py`
2. Define tool schema in `tools.py` TOOLS list
3. Add routing in `tools.py` execute_tool()
4. Update mode system prompts to reference new tool

### Adding a New Mode

1. Create `modes/your_mode.py` with SYSTEM_PROMPT
2. Update `agent.py` _get_system_prompt() dict
3. Update mode validation in switch_mode()

## Testing

```bash
cd backend
python main.py
# Navigate to Scene_Creator with /next /next
# Test mode switching with /mode commands
```

## Documentation

See `backend/docs/`:
- SCENE_CREATOR_QUICK_START.md
- MODE_COMPARISON.md
- SUBAGENT_REFERENCE.md
- SCENE_JSON_SCHEMA.md

## Future Enhancements

- [ ] Character consistency tracking improvements
- [ ] Advanced temporal validation
- [ ] Multi-scene batch validation
- [ ] Style transfer from reference videos
- [ ] Automated A/B testing of cinematography options
