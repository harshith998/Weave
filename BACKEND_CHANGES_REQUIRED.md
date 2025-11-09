# Backend Changes Required for Frontend Integration

This document outlines the **critical backend changes** needed to support the full frontend feature set.

---

## 1. **CRITICAL: Implement Approval Gates in Character Development**

### **Current Issue:**
The `CharacterOrchestrator.run_all_waves()` method runs all waves sequentially **without waiting for approval**:

```python
# Current implementation (orchestrator.py:415-421)
async def run_all_waves(self):
    """Execute all waves sequentially"""
    await self.run_wave_1()  # Runs immediately
    await self.run_wave_2()  # Runs immediately after wave 1
    await self.run_wave_3()  # Runs immediately after wave 2
    final_profile = await self.create_final_profile()
    return final_profile
```

The `approve_checkpoint()` method only updates metadata but **doesn't control execution flow**.

### **Required Change:**
Implement **asyncio Event-based approval gates** that pause execution between waves until user approval.

### **Implementation Plan:**

```python
# Modified orchestrator.py

class CharacterOrchestrator:
    def __init__(self, ...):
        # ... existing code ...
        self.approval_events = {
            1: asyncio.Event(),  # Wave 1 approval gate
            2: asyncio.Event(),  # Wave 2 approval gate
            3: asyncio.Event(),  # Wave 3 approval gate
        }

    async def run_all_waves(self):
        """Execute all waves with approval gates"""
        # Wave 1
        await self.run_wave_1()
        await self._send_update({"type": "awaiting_approval", "wave": 1, "checkpoints": [1, 2]})
        await self.approval_events[1].wait()  # PAUSE HERE until approved

        # Wave 2
        await self.run_wave_2()
        await self._send_update({"type": "awaiting_approval", "wave": 2, "checkpoints": [3, 4, 5]})
        await self.approval_events[2].wait()  # PAUSE HERE until approved

        # Wave 3
        await self.run_wave_3()
        await self._send_update({"type": "awaiting_approval", "wave": 3, "checkpoints": [6]})
        await self.approval_events[3].wait()  # PAUSE HERE until approved

        # Final
        final_profile = await self.create_final_profile()
        return final_profile

    def approve_wave(self, wave_number: int):
        """Signal approval for a wave"""
        self.approval_events[wave_number].set()
```

### **API Changes:**

```python
# api/server.py

@app.post("/api/character/{character_id}/approve_wave")
async def approve_wave(character_id: str, request: ApproveWaveRequest):
    """Approve a wave and continue to next wave"""
    orchestrator = character_agent.active_sessions.get(character_id)
    if not orchestrator:
        raise HTTPException(status_code=404, detail="Active session not found")

    orchestrator.approve_wave(request.wave)

    return {
        "message": f"Wave {request.wave} approved. Continuing to next wave.",
        "next_wave": request.wave + 1,
        "status": "continuing"
    }
```

---

## 2. **Implement Character Importance-Based Selection**

### **Current Issue:**
Entry Agent outputs multiple characters with an `importance` field (string), but backend develops **only the first character**.

### **Required Change:**
Parse importance field and automatically develop characters based on priority.

### **Implementation Plan:**

```python
# api/server.py

def parse_importance(importance_str: str) -> int:
    """Convert importance string to numeric priority (1-5, higher = more important)"""
    importance_str = importance_str.lower()

    if any(word in importance_str for word in ["main", "protagonist", "primary"]):
        return 5
    elif any(word in importance_str for word in ["antagonist", "villain", "main antagonist"]):
        return 5
    elif any(word in importance_str for word in ["supporting", "secondary", "love interest"]):
        return 3
    elif any(word in importance_str for word in ["side", "minor", "cameo"]):
        return 1
    else:
        return 3  # Default medium priority

@app.post("/api/character/start_batch")
async def start_batch_character_development(
    request: StartCharacterRequest,
    background_tasks: BackgroundTasks
):
    """
    Start character development for high-priority characters

    Logic:
    - Develop ALL characters with importance >= 4 (Main + antagonists)
    - Develop first 2 characters with importance == 3 (Supporting)
    - Skip characters with importance < 3 (Side characters)
    """
    characters_with_priority = [
        {**char, "priority": parse_importance(char.get("importance", ""))}
        for char in request.characters
    ]

    # Sort by priority (highest first)
    characters_with_priority.sort(key=lambda x: x["priority"], reverse=True)

    # Select characters to develop
    characters_to_develop = []
    supporting_count = 0

    for char in characters_with_priority:
        if char["priority"] >= 4:
            characters_to_develop.append(char)
        elif char["priority"] == 3 and supporting_count < 2:
            characters_to_develop.append(char)
            supporting_count += 1

    # Create development sessions for each
    character_ids = []
    for char in characters_to_develop:
        entry_output = {
            "characters": [char],
            "storyline": request.storyline
        }

        character_id = character_agent.start_character_development(entry_output, mode=request.mode)
        character_ids.append({
            "character_id": character_id,
            "name": char["name"],
            "priority": char["priority"]
        })

        background_tasks.add_task(run_development, character_id)

    return {
        "characters": character_ids,
        "total_selected": len(character_ids),
        "status": "batch_started"
    }
```

---

## 3. **Add Image Generation Conditional Logic**

### **Current State:**
Image generation is **commented out** in orchestrator.py (line 288).

### **Required Change:**

```python
# orchestrator.py

async def run_wave_3(self):
    """Execute Wave 3: Social (Relationships + optional Image Generation)"""

    IMAGE_GENERATION_ENABLED = os.getenv("IMAGE_GENERATION_ENABLED", "false").lower() == "true"

    agents_list = ["relationships"]
    tasks = [relationships_agent(self.kb, self.anthropic_api_key)]

    if IMAGE_GENERATION_ENABLED and self.gemini_api_key:
        agents_list.append("image_generation")
        tasks.append(image_generation_agent(self.kb, self.gemini_api_key, self.storage))

    await self._send_update({
        "type": "wave_started",
        "wave": 3,
        "agents": agents_list
    })

    # Run tasks
    results = await asyncio.gather(*tasks)

    # Handle results conditionally
    # ... rest of implementation
```

---

## 4. **Implement Session Persistence for Entry & Scene**

### **Current Issue:**
Entry and Scene sessions are **in-memory dicts** (lost on restart).

### **Required Change:**

```python
# api/server.py

import json
from pathlib import Path

SESSION_STORAGE_DIR = Path("./backend/session_data")
SESSION_STORAGE_DIR.mkdir(exist_ok=True)

def save_entry_session(session_id: str, session_data: dict):
    with open(SESSION_STORAGE_DIR / f"entry_{session_id}.json", "w") as f:
        json.dump({
            "conversation_history": session_data["conversation_history"],
            "status": session_data["status"],
            "output": session_data["output"]
        }, f)

def load_entry_session(session_id: str) -> Optional[dict]:
    path = SESSION_STORAGE_DIR / f"entry_{session_id}.json"
    if not path.exists():
        return None

    with open(path, "r") as f:
        data = json.load(f)

    return {
        "agent": EntryAgent(api_key=anthropic_api_key, level=AgentLevel.Intro_General_Entry),
        **data
    }

# Same for scene sessions
```

---

## 5. **Implement Rejection/Regeneration Logic**

### **Current Issue:**
`regenerate_agent()` has `pass` - not implemented (agent.py:189).

### **Required Change:**

```python
# agent.py

async def regenerate_agent(self, character_id: str, agent_name: str, feedback: str):
    """Regenerate a specific agent with user feedback"""

    kb = self.storage.load_character_kb(character_id)
    metadata = self.storage.load_metadata(character_id)

    # Add feedback to KB
    kb[f"{agent_name}_feedback"] = feedback
    self.storage.save_character_kb(kb)

    # Get agent function
    agent_mapping = {
        "personality": personality_agent,
        "backstory_motivation": backstory_motivation_agent,
        "voice_dialogue": voice_dialogue_agent,
        "physical_description": physical_description_agent,
        "story_arc": story_arc_agent,
        "relationships": relationships_agent,
    }

    agent_func = agent_mapping[agent_name]
    output, narrative = await agent_func(kb, self.anthropic_api_key)

    # Update checkpoint
    checkpoint_num = metadata["current_checkpoint"]
    checkpoint = self.storage.load_checkpoint(character_id, checkpoint_num)
    checkpoint["output"]["structured"] = output
    checkpoint["output"]["narrative"] = narrative
    checkpoint["status"] = "awaiting_approval"
    self.storage.save_checkpoint(character_id, checkpoint_num, checkpoint)

    metadata["regenerations"] += 1
    self.storage.save_metadata(character_id, metadata)
```

---

## Summary

| Change | Priority | Complexity | Estimated Time |
|--------|----------|------------|----------------|
| Approval gates with asyncio Events | **CRITICAL** | Medium | 2-3 hours |
| Importance-based selection | High | Low | 1 hour |
| Image generation conditional | Medium | Low | 30 min |
| Session persistence | High | Medium | 2 hours |
| Rejection/regeneration | High | Medium | 2 hours |

**Total: ~8-10 hours of backend work**

**Once complete, frontend will have full human-in-the-loop control.**
