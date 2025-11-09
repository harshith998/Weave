# Intro_General_Entry Agent

**Level 1 Agent** - Entry point for Weave video generation system

## Purpose

This agent serves as the initial entry point for users. It gathers foundational information about the video concept through conversational Q&A.

## Architecture

**Single LLM System** - No subagents required.

The agent uses a single Claude API call per turn with one tool (`finalize_output`) that gets called when the agent has gathered sufficient information.

## What It Does

1. **Asks Questions** - Conversationally gathers information about:
   - Characters (name, appearance, personality, role)
   - Storyline (overview, key scenes, tone/style)

2. **Validates Completeness** - Only finalizes when it has:
   - At least one main character with detailed visual description
   - Clear storyline with beginning/middle/end
   - Tone/style preference

3. **Outputs Structured JSON** - When ready, uses the `finalize_output` tool to return:
```json
{
  "characters": [
    {
      "name": "string",
      "appearance": "detailed visual description",
      "personality": "optional personality traits",
      "role": "role in story"
    }
  ],
  "storyline": {
    "overview": "brief summary",
    "scenes": ["scene 1", "scene 2", ...],
    "tone": "dramatic/comedic/realistic/etc"
  }
}
```

## How It Works

The agent uses Anthropic's tool calling feature with a single tool:
- **`finalize_output`** - Called when agent is confident it has enough information
- Tool input schema enforces the JSON structure
- Agent decides when to call this tool (no external trigger needed)

## Files

- **`agent.py`** - Main agent implementation (single file, no subagents)
- **`tools.py`** - *(Legacy, can be deleted)*
- **`subagents/`** - *(Legacy, can be deleted)*

## Usage

This agent is automatically initialized by `main.py` as the first agent in the hierarchy.

```python
from agents.Intro_General_Entry.agent import EntryAgent
from agent_types import AgentLevel

agent = EntryAgent(api_key="...", level=AgentLevel.Intro_General_Entry)
response = await agent.run(user_input, conversation_history)
```
