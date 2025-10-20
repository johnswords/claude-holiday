from __future__ import annotations

import shutil
import subprocess
import sys
from typing import Optional


def check_ffmpeg_installed() -> bool:
    """Check if ffmpeg is installed and available in PATH."""
    return shutil.which("ffmpeg") is not None


def get_ffmpeg_version() -> Optional[str]:
    """Get ffmpeg version string, or None if not installed."""
    if not check_ffmpeg_installed():
        return None
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        # First line typically contains version info
        if result.stdout:
            return result.stdout.split("\n")[0]
        return None
    except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


def preflight_check() -> None:
    """
    Verify ffmpeg is installed before attempting operations.
    Raises RuntimeError with friendly instructions if not found.
    """
    if not check_ffmpeg_installed():
        error_msg = (
            "FFmpeg is not installed or not found in PATH.\n\n"
            "Please install FFmpeg to use this tool:\n"
            "  macOS:    brew install ffmpeg\n"
            "  Ubuntu:   sudo apt install ffmpeg\n"
            "  Windows:  Download from https://ffmpeg.org/download.html\n\n"
            "After installation, ensure 'ffmpeg' is available in your PATH."
        )
        raise RuntimeError(error_msg)

    # Optional: Log version for debugging
    version = get_ffmpeg_version()
    if version:
        print(f"[FFMPEG] {version}", file=sys.stderr)
