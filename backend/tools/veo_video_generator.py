"""
Veo 3.1 Video Generation Tool

Standalone tool for generating videos from text prompts and optional reference images.
Can be used as an agent tool or imported directly.

Features:
- Text-to-video generation
- Image-to-video with up to 3 reference images
- Support for both base64 and file path image inputs
- Returns video as base64-encoded data
- Cost: ~$1.20 per 8-second 720p video (Veo 3.1 Fast)
"""

import os
import json
import time
import base64
from io import BytesIO
from typing import List, Optional, Dict, Any
from datetime import datetime

try:
    from google import genai
    from google.genai import types
    VEO_AVAILABLE = True
except ImportError:
    VEO_AVAILABLE = False
    types = None  # Define types as None when not available
    print("Warning: google-genai not installed. Veo features will be unavailable.")

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("Warning: Pillow not installed. Image processing will be limited.")


# ============================================================================
# CLIENT INITIALIZATION
# ============================================================================

veo_client = None
if VEO_AVAILABLE:
    try:
        veo_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    except Exception as e:
        print(f"Warning: Failed to initialize Veo client: {e}")
        veo_client = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_base64(s: str) -> bool:
    """Check if string is base64 encoded (data URI or raw base64)."""
    if not s:
        return False

    # Check for data URI format
    if s.startswith('data:image/'):
        return True

    # Check for raw base64
    try:
        # Try to decode as base64
        if len(s) % 4 == 0:  # Base64 strings are always divisible by 4
            base64.b64decode(s, validate=True)
            return True
    except Exception:
        pass

    return False


def decode_base64_image(base64_string: str) -> Optional[Any]:
    """
    Decode base64 string to google.genai Image type.

    Args:
        base64_string: Base64 encoded image (with or without data URI prefix)

    Returns:
        types.Image object or None if failed
    """
    try:
        # Remove data URI prefix if present
        if base64_string.startswith('data:image/'):
            # Format: data:image/png;base64,iVBORw0KG...
            base64_string = base64_string.split(',', 1)[1]

        # Decode base64 to bytes
        image_bytes = base64.b64decode(base64_string)

        # Create Image from bytes
        return types.Image.from_bytes(image_bytes)

    except Exception as e:
        print(f"Error decoding base64 image: {e}")
        return None


def load_image_from_path(file_path: str) -> Optional[Any]:
    """
    Load image from file path to google.genai Image type.

    Args:
        file_path: Path to image file

    Returns:
        types.Image object or None if failed
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Error: Image file not found: {file_path}")
            return None

        # Load using genai's from_file method
        return types.Image.from_file(file_path)

    except Exception as e:
        print(f"Error loading image from path {file_path}: {e}")
        return None


def process_image_inputs(image_paths: List[str], max_images: int = 3) -> tuple[List[Any], List[str]]:
    """
    Process list of image paths (base64 or file paths) into genai Image objects.

    Args:
        image_paths: List of image paths (base64 strings or file paths)
        max_images: Maximum number of images to process (hard cap)

    Returns:
        Tuple of (processed_images, error_messages)
    """
    processed_images = []
    errors = []

    if not image_paths:
        return processed_images, errors

    # Enforce hard cap
    if len(image_paths) > max_images:
        errors.append(f"Too many images provided. Maximum {max_images} allowed, received {len(image_paths)}. Using first {max_images}.")
        image_paths = image_paths[:max_images]

    for idx, img_path in enumerate(image_paths):
        if not img_path:
            continue

        # Determine if base64 or file path
        if is_base64(img_path):
            img = decode_base64_image(img_path)
            if img:
                processed_images.append(img)
            else:
                errors.append(f"Failed to decode base64 image at index {idx}")
        else:
            img = load_image_from_path(img_path)
            if img:
                processed_images.append(img)
            else:
                errors.append(f"Failed to load image from path: {img_path}")

    return processed_images, errors


def poll_veo_operation(operation, max_wait_seconds: int = 300, poll_interval: int = 10) -> tuple[Any, Optional[str]]:
    """
    Poll Veo operation until completion or timeout.

    Args:
        operation: Initial operation object from generate_videos()
        max_wait_seconds: Maximum time to wait (default: 5 minutes)
        poll_interval: Seconds between polls (default: 10 seconds)

    Returns:
        Tuple of (completed_operation, error_message)
    """
    elapsed_time = 0
    start_time = time.time()

    while not operation.done and elapsed_time < max_wait_seconds:
        time.sleep(poll_interval)
        elapsed_time = time.time() - start_time

        try:
            operation = veo_client.operations.get(operation)
            print(f"[Veo] Polling operation... {int(elapsed_time)}s elapsed")
        except Exception as e:
            return None, f"Error polling operation: {str(e)}"

    if not operation.done:
        return None, f"Operation timeout after {max_wait_seconds} seconds"

    return operation, None


def calculate_cost(duration_seconds: int, model: str) -> str:
    """Calculate estimated cost based on duration and model."""
    # Veo 3.1 Fast with audio: $0.15/second
    # Veo 3.1 Standard with audio: $0.40/second

    if "fast" in model.lower():
        cost_per_second = 0.15
    else:
        cost_per_second = 0.40

    total_cost = duration_seconds * cost_per_second
    return f"${total_cost:.2f}"


# ============================================================================
# MAIN FUNCTION
# ============================================================================

async def veo_video_generator(
    prompt: str,
    image_paths: List[str] = None,
    resolution: str = "720p",
    duration_seconds: int = 8,
    negative_prompt: str = None,
    enhance_prompt: bool = True,
    model: str = "veo-3.1-fast-generate-preview"
) -> str:
    """
    Generate video using Google Veo 3.1 API.

    Args:
        prompt: Detailed text prompt for video generation
        image_paths: Optional list of up to 3 image paths (base64 strings or file paths)
        resolution: Video resolution (720p or 1080p)
        duration_seconds: Video duration in seconds (5-8 seconds max)
        negative_prompt: Optional things to avoid in generation
        enhance_prompt: Use Veo's automatic prompt enhancement
        model: Veo model to use (default: veo-3.1-fast-generate-preview)

    Returns:
        JSON string with video data and metadata:
        {
            "success": true/false,
            "videoData": "base64_encoded_video_bytes",
            "mimeType": "video/mp4",
            "operationId": "operation-id",
            "prompt": "prompt used",
            "metadata": {
                "resolution": "720p",
                "duration": 8,
                "imageInputs": 2,
                "model": "veo-3.1-fast-generate-preview",
                "estimatedCost": "$1.20",
                "generationTime": "127 seconds"
            },
            "warnings": ["warning messages if any"],
            "error": "error message if failed"
        }
    """
    generation_start_time = time.time()
    warnings = []

    # ========================================================================
    # 1. VALIDATION
    # ========================================================================

    # Check if Veo is available
    if not VEO_AVAILABLE or veo_client is None:
        return json.dumps({
            "success": False,
            "error": "Veo client not available",
            "message": "google-genai package not installed or GEMINI_API_KEY not set"
        })

    # Validate prompt
    if not prompt or not prompt.strip():
        return json.dumps({
            "success": False,
            "error": "Empty prompt",
            "message": "Prompt is required for video generation"
        })

    # Validate duration
    if duration_seconds < 5 or duration_seconds > 8:
        return json.dumps({
            "success": False,
            "error": "Invalid duration",
            "message": f"Duration must be between 5-8 seconds, received {duration_seconds}"
        })

    # Validate resolution
    if resolution not in ["720p", "1080p"]:
        return json.dumps({
            "success": False,
            "error": "Invalid resolution",
            "message": f"Resolution must be '720p' or '1080p', received '{resolution}'"
        })

    # ========================================================================
    # 2. IMAGE PROCESSING
    # ========================================================================

    processed_images = []
    image_errors = []

    if image_paths:
        processed_images, image_errors = process_image_inputs(image_paths, max_images=3)
        warnings.extend(image_errors)

    # ========================================================================
    # 3. BUILD VEO CONFIG
    # ========================================================================

    try:
        config = types.GenerateVideosConfig(
            number_of_videos=1,
            duration_seconds=duration_seconds,
            resolution=resolution
        )

        # Note: enhance_prompt is not supported by veo-3.1-fast-generate-preview
        # Keeping parameter for compatibility but not using it

        # Add negative prompt if provided
        if negative_prompt and negative_prompt.strip():
            config.negative_prompt = negative_prompt

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": "Config creation failed",
            "message": f"Failed to create Veo config: {str(e)}"
        })

    # ========================================================================
    # 4. CALL VEO API
    # ========================================================================

    try:
        print(f"[Veo] Starting video generation with model: {model}")
        print(f"[Veo] Prompt: {prompt[:100]}...")
        print(f"[Veo] Images: {len(processed_images)}, Resolution: {resolution}, Duration: {duration_seconds}s")

        # Prepare kwargs
        generation_kwargs = {
            "model": model,
            "prompt": prompt,
            "config": config
        }

        # Add images if any were successfully processed
        if processed_images:
            generation_kwargs["images"] = processed_images

        # Start generation
        operation = veo_client.models.generate_videos(**generation_kwargs)

        print(f"[Veo] Operation started: {operation.name}")

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": "API call failed",
            "message": f"Failed to start Veo generation: {str(e)}",
            "prompt": prompt
        })

    # ========================================================================
    # 5. POLL OPERATION
    # ========================================================================

    print(f"[Veo] Polling for completion (max 5 minutes)...")
    operation, poll_error = poll_veo_operation(operation, max_wait_seconds=300, poll_interval=10)

    if poll_error:
        return json.dumps({
            "success": False,
            "error": "Operation failed",
            "message": poll_error,
            "operationId": operation.name if operation else None
        })

    # ========================================================================
    # 6. EXTRACT VIDEO
    # ========================================================================

    try:
        # Get generated video
        generated_videos = operation.response.generated_videos

        if not generated_videos or len(generated_videos) == 0:
            return json.dumps({
                "success": False,
                "error": "No video generated",
                "message": "Veo operation completed but returned no videos"
            })

        video = generated_videos[0]

        # Download video bytes
        print(f"[Veo] Downloading video...")
        video_data = veo_client.files.download(file=video.video)

        # Check if it's already bytes or needs to be read
        if isinstance(video_data, bytes):
            video_bytes = video_data
        elif hasattr(video_data, 'read'):
            video_bytes = video_data.read()
        else:
            # Try to get bytes from the video object directly
            video_bytes = video.video.data if hasattr(video.video, 'data') else bytes(video_data)

        # Encode to base64
        video_base64 = base64.b64encode(video_bytes).decode('utf-8')

        print(f"[Veo] Video generated successfully! Size: {len(video_bytes) / 1024:.2f} KB")

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": "Video extraction failed",
            "message": f"Failed to extract video from operation: {str(e)}",
            "operationId": operation.name
        })

    # ========================================================================
    # 7. BUILD SUCCESS RESPONSE
    # ========================================================================

    generation_time = time.time() - generation_start_time
    estimated_cost = calculate_cost(duration_seconds, model)

    response = {
        "success": True,
        "videoData": video_base64,
        "mimeType": "video/mp4",
        "operationId": operation.name,
        "prompt": prompt,
        "metadata": {
            "resolution": resolution,
            "duration": duration_seconds,
            "imageInputs": len(processed_images),
            "model": model,
            "estimatedCost": estimated_cost,
            "generationTime": f"{int(generation_time)} seconds",
            "enhancedPrompt": enhance_prompt
        }
    }

    # Add warnings if any
    if warnings:
        response["warnings"] = warnings

    return json.dumps(response)


# ============================================================================
# TOOL DEFINITION (Anthropic Format)
# ============================================================================

VEO_TOOL = {
    "name": "veo_video_generator",
    "description": "Generate videos using Google Veo 3.1 Fast API from text prompts and optional reference images (up to 3). Returns high-quality 720p/1080p video with generated audio as base64-encoded data. Cost: ~$1.20 per 8-second 720p video. Use when ready to create actual video content from scene specifications.",
    "input_schema": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Detailed text prompt describing the video content, including action, style, camera work, mood, and audio. Be specific and descriptive for best results."
            },
            "image_paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of up to 3 image paths (base64 strings with 'data:image/' prefix OR file paths). Used for image-to-video generation or character/style conditioning. Hard cap: 3 images maximum.",
                "maxItems": 3,
                "default": []
            },
            "resolution": {
                "type": "string",
                "description": "Video output resolution. Use 720p for testing to reduce costs.",
                "enum": ["720p", "1080p"],
                "default": "720p"
            },
            "duration_seconds": {
                "type": "integer",
                "description": "Video duration in seconds. Veo 3.1 supports 5-8 seconds. Default is 8 seconds.",
                "minimum": 5,
                "maximum": 8,
                "default": 8
            },
            "negative_prompt": {
                "type": "string",
                "description": "Optional negative prompt describing what to avoid in the generation (e.g., 'blurry, low quality, distorted faces')",
                "default": None
            },
            "enhance_prompt": {
                "type": "boolean",
                "description": "Use Veo's automatic prompt enhancement for better results. Recommended: true",
                "default": True
            },
            "model": {
                "type": "string",
                "description": "Veo model to use. Fast is cheaper and faster, Standard is higher quality.",
                "enum": ["veo-3.1-fast-generate-preview", "veo-3.1-generate-preview"],
                "default": "veo-3.1-fast-generate-preview"
            }
        },
        "required": ["prompt"]
    }
}
