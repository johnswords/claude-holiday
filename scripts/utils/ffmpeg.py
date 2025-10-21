"""FFmpeg utility functions and checks"""

import shutil
import subprocess


def preflight_check() -> None:
    """
    Verify FFmpeg is installed and accessible.

    Raises:
        RuntimeError: If FFmpeg is not found or not functional
    """
    ffmpeg_path = shutil.which("ffmpeg")

    if not ffmpeg_path:
        raise RuntimeError(
            "FFmpeg not found in PATH. Please install FFmpeg:\n"
            "  macOS: brew install ffmpeg\n"
            "  Ubuntu/Debian: sudo apt install ffmpeg\n"
            "  Windows: Download from https://ffmpeg.org/download.html"
        )

    # Verify FFmpeg is functional
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg found at {ffmpeg_path} but failed to execute")
    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg check timed out") from None
    except Exception as e:
        raise RuntimeError(f"Error running FFmpeg: {e}") from e
