"""
Domain-specific subagent implementations.
Each subagent is a single-purpose LLM call with specialized prompts.
"""

import os
from anthropic import Anthropic


# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-5-20250929"


async def research_subagent(query: str) -> str:
    """
    Research subagent - gathers information and analyzes topics

    Args:
        query: Research query

    Returns:
        Research results as string
    """
    # Placeholder supermemory data injection
    supermemory_data = {
        "context": "Video generation knowledge base",
        "relevant_docs": ["character_archetypes.md", "scene_composition.md"],
        "metadata": "Retrieved from supermemory"
    }

    system_prompt = f"""You are a research specialist for video generation projects.
Your job is to provide detailed, accurate information to help with creative decisions.

Available knowledge base:
{supermemory_data}

Provide concise but thorough research results."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": query}]
    )

    # Extract text response
    return response.content[0].text


async def creative_subagent(prompt: str, style: str = "neutral") -> str:
    """
    Creative subagent - generates creative content and ideas

    Args:
        prompt: Creative prompt
        style: Creative style (dramatic, comedic, realistic, etc.)

    Returns:
        Creative content as string
    """
    # Placeholder supermemory data injection
    supermemory_data = {
        "style_guides": {
            "dramatic": "High stakes, emotional intensity",
            "comedic": "Light-hearted, humorous elements",
            "realistic": "Grounded, authentic portrayals"
        },
        "creative_examples": ["Sample character: Alice - brave explorer", "Sample scene: Dawn marketplace"]
    }

    system_prompt = f"""You are a creative writing specialist for video generation.
Your job is to generate compelling characters, scenes, and story elements.

Style guide: {style}
Reference materials:
{supermemory_data}

Generate creative, vivid content that can be used for video generation."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract text response
    return response.content[0].text
