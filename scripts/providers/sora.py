from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore

from .base import Provider, RenderConfig


class SoraProvider(Provider):
    def __init__(self, api_key: Optional[str] = None) -> None:
        if OpenAI is None:
            raise ImportError(
                "OpenAI SDK is required for SoraProvider. "
                "Install it with: pip install openai"
            )
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for SoraProvider")
        self.client = OpenAI(api_key=self.api_key)

    def name(self) -> str:
        return "sora"

    def _build_prompt(self, scene: Dict[str, Any]) -> str:
        """Build a video generation prompt from scene data."""
        # Extract prompt from scene description or use default
        if "description" in scene:
            return str(scene["description"])
        if "prompt" in scene:
            return str(scene["prompt"])

        # Fallback: build from available metadata
        scene_id = scene.get("id", "scene")
        return f"A professional video scene for {scene_id}"

    def generate_scene(
        self,
        episode_id: str,
        scene: Dict[str, Any],
        output_dir: str,
        render_cfg: RenderConfig,
        seed: Optional[int] = None,
    ) -> str:
        """
        Generate a scene using OpenAI's Sora API.

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
            # Call OpenAI's video generation API (Sora)
            # Note: This uses the official OpenAI SDK
            extra_params = {}
            if seed is not None:
                extra_params["seed"] = seed

            # Generate video using Sora
            # Note: The actual API endpoint and parameters may vary
            # This implementation follows the expected Sora API pattern
            response = self.client.videos.create(
                model="sora-1.0",
                prompt=prompt,
                duration=duration,
                resolution=f"{render_cfg.width}x{render_cfg.height}",
                **extra_params
            )

            # Download the generated video from the URL
            import urllib.request
            video_url = response.url
            urllib.request.urlretrieve(video_url, out_path)

            print(f"[SORA] Generated scene {scene_id} ({duration}s) -> {out_path}", file=sys.stderr)
            return str(out_path)

        except Exception as e:
            # If Sora fails, fall back to generating a placeholder clip
            error_msg = f"Sora API request failed for scene {scene_id}: {e}"
            print(f"[SORA ERROR] {error_msg}", file=sys.stderr)
            print(f"[SORA] Generating fallback placeholder for {scene_id}", file=sys.stderr)

            # Generate a placeholder using ffmpeg (same as prebaked fallback)
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
                result = subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if result.stderr:
                    print(f"[FFMPEG] {result.stderr}", file=sys.stderr)
            except subprocess.CalledProcessError as ffmpeg_err:
                error_msg = f"FFmpeg fallback generation failed for scene {scene_id}\n"
                error_msg += f"Command: {' '.join(cmd)}\n"
                if ffmpeg_err.stderr:
                    error_msg += f"Error output:\n{ffmpeg_err.stderr}"
                raise RuntimeError(error_msg) from ffmpeg_err

            return str(out_path)
