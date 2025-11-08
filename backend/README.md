# Weave Backend - Agentic System

Ultra-minimal wireframe for a hierarchical agentic system with MCP integration.

## Structure

```
backend/
├── agent_types.py           # Enum for agent hierarchy (MAIN=1, SUB=2, SUBSUB=3)
├── base_agent.py            # BaseAgent abstract class
├── agents/
│   └── example_agent/       # Template for creating new agents
│       ├── agent.py         # Agent implementation
│       ├── tools.py         # Agent-specific tools
│       └── subagents.py     # Subagent management
└── requirements.txt
```

## Quick Start

### 1. Creating a New Agent

Copy the `example_agent` folder and rename it:

```bash
cp -r agents/example_agent agents/my_new_agent
```

Then implement the TODOs in:
- `agent.py` - Main agent logic
- `tools.py` - Agent-specific tools and MCP integrations
- `subagents.py` - Subagent spawning and coordination

### 2. Agent Hierarchy

Agents can be at three levels (defined in [agent_types.py](agent_types.py)):

- **MAIN (1)**: Orchestrator agents
- **SUB (2)**: Sub-agents spawned by MAIN
- **SUBSUB (3)**: Sub-sub-agents spawned by SUB

### 3. Key Concepts

**BaseAgent** ([base_agent.py](base_agent.py))
- `run(task)` - Main execution method
- `call_tool(tool_name, **kwargs)` - Call MCP tools
- `spawn_subagent(agent_class, config)` - Create child agents
- `send_checkpoint(data)` - Report progress to parent/orchestrator

**Parallel Development**
Each team member can:
1. Create their own agent folder
2. Implement independently
3. Work in parallel without conflicts

### 4. Adding MCP Servers

1. Add MCP package to `requirements.txt`
2. Implement MCP tool calling in your agent's `tools.py`
3. Use `call_tool()` from your agent's `run()` method

### 5. Next Steps (TODO)

The following are NOT implemented and should be added as needed:
- [ ] Communication/message bus for peer-to-peer agent communication
- [ ] Checkpoint system implementation
- [ ] Centralized memory store
- [ ] MCP registry/plugin system
- [ ] Frontend API layer (FastAPI)
- [ ] Queue system for frontend injection
- [ ] Pause/Resume/Stop agent lifecycle

## Example Usage (Conceptual)

```python
from agents.example_agent.agent import ExampleAgent
from agent_types import AgentLevel

# Create a main agent
agent = ExampleAgent(agent_id="main_1", level=AgentLevel.MAIN)

# Run a task
result = await agent.run({"task": "process_video_clip"})

# Agent can spawn subagents
subagent = await agent.spawn_subagent(SomeSubAgent, config={"param": "value"})
```

## Design Philosophy

This is a **wireframe only**. All methods return `pass` - you implement the actual logic. This allows your team to:
- Work in parallel on different agents
- Decide implementation details later
- Keep a clean separation of concerns
