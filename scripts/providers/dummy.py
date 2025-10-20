from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib

from .base import Provider, RenderConfig


class DummyProvider(Provider):
    def __init__(self, base_color: str = "0x1e2630") -> None:
        self.base_color = base_color

    def name(self) -> str:
        return "dummy"

    def _color_for_scene(self, scene_id: str) -> str:
        # Derive a color from the scene id for variety
        h = hashlib.blake2s(scene_id.encode("utf-8")).hexdigest()
        return f"0x{h[:6]}"

    def generate_scene(
        self,
        episode_id: str,
        scene: Dict[str, Any],
        output_dir: str,
        render_cfg: RenderConfig,
        seed: Optional[int] = None,
    ) -> str:
        scene_id = scene.get("id") or "scene"
        duration = int(scene.get("duration_sec") or 1)
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{scene_id}.mp4"

        # Include seed in color derivation to ensure distinct candidates
        key = f"{episode_id}:{scene_id}:{seed or 0}"
        color = self._color_for_scene(key)
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
        except subprocess.CalledProcessError as e:
            error_msg = f"FFmpeg dummy generation failed for scene {scene_id}\n"
            error_msg += f"Command: {' '.join(cmd)}\n"
            if e.stderr:
                error_msg += f"Error output:\n{e.stderr}"
            raise RuntimeError(error_msg) from e
        return str(out_path)