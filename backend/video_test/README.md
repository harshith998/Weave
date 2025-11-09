# Veo Video Generator Tool

Standalone tool for generating videos using Google Veo 3.1 API.

## Overview

The `veo_video_generator` tool enables AI agents to generate high-quality videos from text prompts and optional reference images. It integrates seamlessly with the Scene Creator agent and can be called by any agent in the system.

## Features

- **Text-to-Video**: Generate videos from detailed text descriptions
- **Image-to-Video**: Animate up to 3 reference images
- **Flexible Input**: Supports both base64-encoded images and file paths
- **Cost Effective**: Uses Veo 3.1 Fast by default (~$1.20 per 8-second video)
- **High Quality**: 720p or 1080p output with generated audio
- **Async Operation**: Polls Veo API with automatic timeout handling

## Setup

### 1. Environment Variables

Set your Gemini API key (same key used for Nano Banana):

```bash
export GEMINI_API_KEY="your_api_key_here"
```

### 2. Dependencies

Already included in `backend/requirements.txt`:

```
google-genai>=0.8.0
pillow>=10.0.0
```

## Usage

### As an Agent Tool

The tool is automatically registered with the Scene Creator agent and can be called via the tool calling pattern:

```python
# Agent will call this tool when needed
{
    "name": "veo_video_generator",
    "input": {
        "prompt": "A majestic eagle soaring over mountains at sunset...",
        "resolution": "720p",
        "duration_seconds": 8
    }
}
```

### Direct Python Import

You can also import and use the tool directly:

```python
from tools.veo_video_generator import veo_video_generator
import asyncio
import json

# Text-to-video example
async def generate_video():
    result_json = await veo_video_generator(
        prompt="A cinematic shot of waves crashing on a beach at golden hour",
        resolution="720p",
        duration_seconds=8
    )

    result = json.loads(result_json)

    if result["success"]:
        video_base64 = result["videoData"]
        # Use video_base64 as needed
        print(f"Video generated! Cost: {result['metadata']['estimatedCost']}")
    else:
        print(f"Error: {result['error']}")

asyncio.run(generate_video())
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | **Required** | Detailed text description of the video content |
| `image_paths` | `List[str]` | `[]` | Up to 3 images (base64 or file paths) |
| `resolution` | `str` | `"720p"` | Video resolution (`720p` or `1080p`) |
| `duration_seconds` | `int` | `8` | Video duration (5-8 seconds) |
| `negative_prompt` | `str` | `None` | What to avoid in generation |
| `enhance_prompt` | `bool` | `True` | Use Veo's prompt enhancement |
| `model` | `str` | `"veo-3.1-fast-generate-preview"` | Veo model to use |

## Examples

### Example 1: Simple Text-to-Video

```python
result = await veo_video_generator(
    prompt="A close-up of a cat playing with yarn. Soft lighting, shallow depth of field."
)
```

### Example 2: Image-to-Video with File Paths

```python
result = await veo_video_generator(
    prompt="Character walks forward confidently. Camera tracks backward.",
    image_paths=[
        "backend/state/images/character_front.png",
        "backend/state/images/character_side.png"
    ],
    resolution="720p"
)
```

### Example 3: Image-to-Video with Base64

```python
result = await veo_video_generator(
    prompt="Animate this scene with dramatic lighting changes",
    image_paths=[
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA..."
    ],
    negative_prompt="blurry, low quality, distorted",
    duration_seconds=6
)
```

### Example 4: Scene Creator Integration

```python
# Inside Scene Creator agent workflow
from utils.state_manager import read_scene

# Load scene data
scene = read_scene("default", "1")

# Build comprehensive prompt from scene
prompt = f"""
{scene['description']}

Cinematography: {scene['cinematography']['shotSequence'][0]['shotSize']}
{scene['cinematography']['shotSequence'][0]['cameraAngle']}
Camera Movement: {scene['cinematography']['shotSequence'][0]['cameraMovement']['type']}
Lighting: {scene['aesthetic']['lighting']['setup']}
Mood: {scene['aesthetic']['mood']}
"""

# Use reference images from scene
reference_images = [
    img['imageData']
    for img in scene.get('referenceImages', [])
][:3]

# Generate video
result = await veo_video_generator(
    prompt=prompt,
    image_paths=reference_images,
    resolution="720p"
)
```

## Response Format

### Success Response

```json
{
    "success": true,
    "videoData": "base64_encoded_mp4_bytes...",
    "mimeType": "video/mp4",
    "operationId": "projects/123/operations/456",
    "prompt": "The prompt used for generation",
    "metadata": {
        "resolution": "720p",
        "duration": 8,
        "imageInputs": 2,
        "model": "veo-3.1-fast-generate-preview",
        "estimatedCost": "$1.20",
        "generationTime": "127 seconds",
        "enhancedPrompt": true
    },
    "warnings": ["Warning messages if any"]
}
```

### Error Response

```json
{
    "success": false,
    "error": "Error type",
    "message": "Detailed error message",
    "operationId": "operation-id (if available)"
}
```

## Error Handling

The tool handles various error scenarios gracefully:

- **API Not Available**: Returns error if `google-genai` not installed or API key missing
- **Invalid Input**: Validates prompt, duration, resolution before API call
- **Too Many Images**: Enforces hard cap of 3 images maximum
- **Image Processing Failures**: Reports which images failed to load
- **Generation Timeout**: Times out after 5 minutes with clear error
- **API Errors**: Catches and reports Veo API errors with context

## Pricing (as of 2025)

| Model | Price per Second | 8-Second Video Cost |
|-------|------------------|---------------------|
| Veo 3.1 Fast (with audio) | $0.15 | $1.20 |
| Veo 3.1 Standard (with audio) | $0.40 | $3.20 |

**Cost Optimization Tips:**
- Use `veo-3.1-fast-generate-preview` for testing (default)
- Use 720p resolution to reduce costs
- Enable `enhance_prompt=True` to reduce regenerations
- Batch similar scenes together

## Limitations

- **Max Duration**: 8 seconds per video (Veo API limit)
- **Max Images**: 3 reference images (hard cap)
- **Timeout**: 5 minutes max wait time
- **Resolution**: 720p or 1080p only
- **Format**: Returns MP4 format only

## Troubleshooting

### "Veo client not available"
- Ensure `google-genai>=0.8.0` is installed: `pip install google-genai`
- Check `GEMINI_API_KEY` environment variable is set

### "Operation timeout"
- 1080p videos may take longer; consider using 720p
- Check Veo API status if timeouts persist

### "Too many images provided"
- Hard limit is 3 images
- Tool automatically uses first 3 if more are provided

### "Failed to decode base64 image"
- Ensure base64 strings include proper data URI prefix: `data:image/png;base64,...`
- OR remove prefix and provide raw base64

### "Failed to load image from path"
- Verify file path exists and is accessible
- Check file format is supported (PNG, JPG, JPEG, etc.)

## Integration Points

This tool can be used by:

- ✅ Scene Creator Agent (via tool calling)
- ✅ Future Combiner Agent
- ✅ Any custom agent
- ✅ Direct Python scripts

## File Structure

```
backend/
├── tools/
│   ├── veo_video_generator.py    # Main tool implementation
│   └── README.md                  # This documentation
└── agents/
    └── Scene_Creator/
        └── tools.py               # Registers veo_video_generator
```

## Development Notes

- Tool follows same pattern as `reference_image_generator` (Nano Banana)
- Uses same `google-genai` client for consistency
- Returns base64-encoded video for flexibility
- Fully async for non-blocking operation
- Thread-safe and stateless

## Future Enhancements

Potential improvements for future versions:

- [ ] Support for video extension (continue existing Veo videos)
- [ ] Batch generation (multiple variations)
- [ ] Frame-specific generation (first/last frame control)
- [ ] Audio-only generation toggle
- [ ] Automatic cost estimation before generation
- [ ] Video quality analysis post-generation
- [ ] Integration with visual continuity checker

## Support

For issues or questions:
- Check this documentation first
- Review error messages in JSON responses
- Verify API key and dependencies
- Check Veo API status: https://status.cloud.google.com/
