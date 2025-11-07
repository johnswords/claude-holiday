from __future__ import annotations

from pathlib import Path
from typing import Any

import pysubs2


def generate_captions(
    captions_cues: list[dict[str, Any]],
    output_dir: Path,
    episode_id: str,
    cut_id: str,
    _fps: int = 24,
) -> dict[str, Path]:
    """
    Generate .srt and .ass subtitle files from caption cues.

    Args:
        captions_cues: List of caption cue dictionaries with keys:
            - text: Caption text
            - start_sec: Start time in seconds
            - end_sec: End time in seconds (optional, defaults to start_sec + 3)
            - scene_id: Scene ID (optional, for organizing per-scene captions)
        output_dir: Directory to write caption files
        episode_id: Episode identifier
        cut_id: Cut identifier
        fps: Frames per second (for timing calculations)

    Returns:
        Dictionary with 'srt' and 'ass' keys pointing to generated files
    """
    if not captions_cues:
        return {}

    output_dir.mkdir(parents=True, exist_ok=True)

    # Create subtitle object
    subs = pysubs2.SSAFile()

    # Convert cues to pysubs2 events
    for cue in captions_cues:
        text = cue.get("text", "")
        start_sec = float(cue.get("start_sec", 0.0))
        # Default duration: 3 seconds if no end time specified
        end_sec = float(cue.get("end_sec", start_sec + 3.0))

        # Convert seconds to milliseconds
        start_ms = int(start_sec * 1000)
        end_ms = int(end_sec * 1000)

        # Create subtitle event
        event = pysubs2.SSAEvent(start=start_ms, end=end_ms, text=text)
        subs.append(event)

    # Sort events by start time
    subs.sort()

    # Write .srt file
    srt_path = output_dir / f"{episode_id}__{cut_id}.srt"
    subs.save(str(srt_path))

    # Write .ass file (Advanced SubStation Alpha format)
    ass_path = output_dir / f"{episode_id}__{cut_id}.ass"
    subs.save(str(ass_path))

    return {
        "srt": srt_path,
        "ass": ass_path,
    }


def generate_per_scene_captions(
    scenes: list[dict[str, Any]],
    output_dir: Path,
    episode_id: str,
    cut_id: str,
    fps: int = 24,
) -> list[dict[str, Any]]:
    """
    Generate captions from per-scene caption cues.

    Args:
        scenes: List of scene dictionaries with optional 'captions_cues' key
        output_dir: Directory to write caption files
        episode_id: Episode identifier
        cut_id: Cut identifier
        fps: Frames per second

    Returns:
        List of caption file metadata dictionaries
    """
    caption_files = []
    cumulative_time = 0.0

    for scene in scenes:
        scene_id = scene.get("id", "scene")
        scene_cues = scene.get("captions_cues", [])

        if not scene_cues:
            # Update cumulative time for next scene
            cumulative_time += float(scene.get("duration_sec", 0))
            continue

        # Adjust cue times to be relative to episode start
        adjusted_cues = []
        for cue in scene_cues:
            adjusted = cue.copy()
            adjusted["start_sec"] = float(cue.get("start_sec", 0.0)) + cumulative_time
            if "end_sec" in cue:
                adjusted["end_sec"] = float(cue["end_sec"]) + cumulative_time
            else:
                # Default 3-second duration
                adjusted["end_sec"] = adjusted["start_sec"] + 3.0
            adjusted_cues.append(adjusted)

        # Generate captions for this scene
        scene_dir = output_dir / scene_id
        caption_paths = generate_captions(
            captions_cues=adjusted_cues,
            output_dir=scene_dir,
            episode_id=episode_id,
            cut_id=f"{cut_id}_{scene_id}",
            _fps=fps,
        )

        if caption_paths:
            caption_files.append(
                {
                    "scene_id": scene_id,
                    "srt_path": str(caption_paths["srt"].relative_to(output_dir.parent.parent)),
                    "ass_path": str(caption_paths["ass"].relative_to(output_dir.parent.parent)),
                }
            )

        # Update cumulative time
        cumulative_time += float(scene.get("duration_sec", 0))

    return caption_files
