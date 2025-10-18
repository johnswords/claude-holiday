from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from .base import Provider, RenderConfig


class PrebakedProvider(Provider):
    def __init__(self) -> None:
        pass

    def name(self) -> str:
        return "prebaked"

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
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return str(out_path)