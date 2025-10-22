from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

FFMPEG_AVAILABLE = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


@pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg and ffprobe required for CLI smoke test")
def test_apply_overlays_cli_smoke(tmp_path: Path) -> None:
    input_video = tmp_path / "input.mp4"
    output_video = tmp_path / "output.mp4"
    spec_path = tmp_path / "overlay.json"

    spec_path.write_text(json.dumps({"overlays": []}), encoding="utf-8")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=size=16x16:rate=1:color=black",
            "-t",
            "1",
            str(input_video),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.apply_overlays",
            "--in",
            str(input_video),
            "--spec",
            str(spec_path),
            "--out",
            str(output_video),
            "--width",
            "16",
            "--height",
            "16",
            "--fps",
            "12",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert output_video.exists()
    assert str(output_video) in result.stdout
