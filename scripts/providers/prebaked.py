from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from .base import Provider, RenderConfig
from scripts.utils.ffmpeg import preflight_check


class PrebakedProvider(Provider):
    def __init__(self) -> None:
        pass

    def name(self) -> str:
        return "prebaked"

    def generate_scene(
        self,
        episode_id: str,
        scene: dict[str, Any],
        output_dir: str,
        render_cfg: RenderConfig,
        seed: int | None = None,
    ) -> str:
        scene_id = scene.get("id") or "scene"
        duration = int(scene.get("duration_sec") or 1)
        ep_dir = Path("episodes") / episode_id / "renders"
        candidates = [
            ep_dir / "final" / f"{scene_id}.mp4",
            ep_dir / "drafts" / f"{scene_id}.mp4",
        ]
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{scene_id}.mp4"

        for cand in candidates:
            if cand.exists():
                shutil.copy(str(cand), str(out_path))
                return str(out_path)

        # Fallback: generate a solid color clip so the compile can complete
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
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.stderr:
                print(f"[FFMPEG] {result.stderr}", file=sys.stderr)
        except subprocess.CalledProcessError as e:
            error_msg = f"FFmpeg fallback generation failed for scene {scene_id}\n"
            error_msg += f"Command: {' '.join(cmd)}\n"
            if e.stderr:
                error_msg += f"Error output:\n{e.stderr}"
            raise RuntimeError(error_msg) from e
        return str(out_path)
