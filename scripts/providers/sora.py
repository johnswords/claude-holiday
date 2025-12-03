from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore

from scripts.utils.ffmpeg import preflight_check

from .base import Provider, RenderConfig

# Polling configuration for async video generation
POLL_INTERVAL_SECONDS = 5
MAX_POLL_ATTEMPTS = 120  # 10 minutes max wait


class SoraProvider(Provider):
    def __init__(self, api_key: str | None = None, model: str = "sora-2") -> None:
        if OpenAI is None:
            raise ImportError("OpenAI SDK is required for SoraProvider. Install it with: pip install openai")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model  # "sora-2" or "sora-2-pro"

    def name(self) -> str:
        return "sora"

    def _build_prompt(self, scene: dict[str, Any]) -> str:
        """Build a video generation prompt from scene data."""
        # Get the sora_prompt if available (from episode manifests)
        if "sora_prompt" in scene:
            return str(scene["sora_prompt"]).strip()
        # Fallback to description or prompt fields
        if "description" in scene:
            return str(scene["description"])
        if "prompt" in scene:
            return str(scene["prompt"])

        # Fallback: build from available metadata
        scene_id = scene.get("id", "scene")
        duration = scene.get("duration_sec", 5)
        return f"A {duration}-second professional video scene. Vertical 9:16 format. Scene ID: {scene_id}"

    def generate_scene(  # noqa: ARG002 (seed reserved for future use)
        self,
        _episode_id: str,
        scene: dict[str, Any],
        output_dir: str,
        render_cfg: RenderConfig,
        seed: int | None = None,  # noqa: ARG002
    ) -> str:
        """
        Generate a scene using OpenAI's Sora 2 API.

        The Sora API is async: create a job, then poll until complete.
        Returns: path to MP4 file for this scene.
        """
        scene_id = scene.get("id") or "scene"
        duration = int(scene.get("duration_sec") or 5)

        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{scene_id}.mp4"

        # Build the prompt for Sora
        prompt = self._build_prompt(scene)

        try:
            # Initialize client (will fail if API key is missing)
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required for SoraProvider")
            client = OpenAI(api_key=self.api_key)

            print(f"[SORA] Creating video job for scene {scene_id}...", file=sys.stderr)

            # Create video generation job (async)
            # Note: Sora 2 API only takes model and prompt
            # Duration and size are inferred or specified in the prompt
            video = client.videos.create(
                model=self.model,
                prompt=prompt,
            )

            video_id = video.id
            print(f"[SORA] Job created: {video_id}, polling for completion...", file=sys.stderr)

            # Poll for completion
            for _attempt in range(MAX_POLL_ATTEMPTS):
                video_status = client.videos.retrieve(video_id)

                if video_status.status == "completed":
                    # Download the video
                    print("[SORA] Video completed, downloading...", file=sys.stderr)
                    import urllib.request

                    # The completed video should have a URL
                    video_url = None
                    if hasattr(video_status, "url") and video_status.url:
                        video_url = video_status.url
                    elif hasattr(video_status, "download_url") and video_status.download_url:
                        video_url = video_status.download_url

                    if video_url:
                        urllib.request.urlretrieve(video_url, out_path)
                    else:
                        # Try to get video content directly via the content endpoint
                        video_content = client.videos.content(video_id)
                        with open(out_path, "wb") as f:
                            f.write(video_content.read())

                    print(f"[SORA] Generated scene {scene_id} -> {out_path}", file=sys.stderr)
                    return str(out_path)

                elif video_status.status == "failed":
                    error_msg = getattr(video_status, "error", "Unknown error")
                    raise RuntimeError(f"Sora video generation failed: {error_msg}")

                else:
                    # Still processing (queued or in_progress)
                    progress = getattr(video_status, "progress", 0)
                    print(f"[SORA] Status: {video_status.status}, progress: {progress}%", file=sys.stderr)
                    time.sleep(POLL_INTERVAL_SECONDS)

            raise TimeoutError(f"Sora video generation timed out after {MAX_POLL_ATTEMPTS * POLL_INTERVAL_SECONDS}s")

        except Exception as e:
            # If Sora fails, fall back to generating a placeholder clip
            error_msg = f"Sora API request failed for scene {scene_id}: {e}"
            print(f"[SORA ERROR] {error_msg}", file=sys.stderr)
            print(f"[SORA] Generating fallback placeholder for {scene_id}", file=sys.stderr)

            # Generate a placeholder using ffmpeg (same as prebaked fallback)
            preflight_check()
            color = "0x202833"
            cmd = [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"color=size={render_cfg.width}x{render_cfg.height}:rate={render_cfg.fps}:color={color}",
                "-t",
                str(duration),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(out_path),
            ]
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                if result.stderr:
                    print(f"[FFMPEG] {result.stderr}", file=sys.stderr)
            except subprocess.CalledProcessError as ffmpeg_err:
                error_msg = f"FFmpeg fallback generation failed for scene {scene_id}\n"
                error_msg += f"Command: {' '.join(cmd)}\n"
                if ffmpeg_err.stderr:
                    error_msg += f"Error output:\n{ffmpeg_err.stderr}"
                raise RuntimeError(error_msg) from ffmpeg_err

            return str(out_path)
