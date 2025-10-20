from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Optional, Dict, Any
import re


@dataclass
class RenderConfig:
    width: int
    height: int
    fps: int
    aspect: str
    resolution: str

    @staticmethod
    def from_strings(resolution: str, fps: int, aspect: str) -> "RenderConfig":
        m = re.match(r"^(\d+)x(\d+)$", resolution)
        if not m:
            raise ValueError(f"Invalid resolution '{resolution}'. Expected WIDTHxHEIGHT, e.g., 1080x1920.")
        w, h = int(m.group(1)), int(m.group(2))
        return RenderConfig(width=w, height=h, fps=fps, aspect=aspect, resolution=resolution)


class Provider(Protocol):
    def name(self) -> str:
        ...

    def generate_scene(
        self,
        episode_id: str,
        scene: Dict[str, Any],
        output_dir: str,
        render_cfg: RenderConfig,
        seed: Optional[int] = None,
    ) -> str:
        """
        Generate or resolve a scene clip.

        Returns: path to MP4 file for this scene.
        """
        ...