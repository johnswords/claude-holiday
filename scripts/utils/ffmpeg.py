"""FFmpeg utilities and preflight checks for Claude Holiday."""
from __future__ import annotations

import shutil
import subprocess
import sys


def preflight_check() -> None:
    """
    Verify FFmpeg is installed and accessible.

    Raises:
        RuntimeError: If FFmpeg is not found or not functional
    """
    # Check if ffmpeg is in PATH
    ffmpeg_path = shutil.which("ffmpeg")

    if not ffmpeg_path:
        error_msg = (
            "FFmpeg is not installed or not in your PATH.\n"
            "Install it via:\n"
            "  • macOS: brew install ffmpeg\n"
            "  • Ubuntu/Debian: sudo apt install ffmpeg\n"
            "  • Windows: Download from https://ffmpeg.org/download.html"
        )
        raise RuntimeError(error_msg)

    # Verify ffmpeg is functional by checking version
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        # Extract version from output (first line typically contains version info)
        version_line = result.stdout.split('\n')[0] if result.stdout else "unknown"
        print(f"[FFMPEG] Found: {version_line}", file=sys.stderr)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg found at {ffmpeg_path} but failed to execute: {e}") from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"FFmpeg at {ffmpeg_path} timed out during version check") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error checking FFmpeg: {e}") from e
