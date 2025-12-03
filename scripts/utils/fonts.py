"""Cross-platform font resolution for Claude Holiday."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# Font search paths by platform
FONT_PATHS = {
    "darwin": [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/Library/Fonts/Arial.ttf",
    ],
    "linux": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ],
    "win32": [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/ArialUni.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ],
}


def find_system_font() -> str | None:
    """
    Find an available system font for FFmpeg drawtext.

    Returns the path to a suitable font file, or None if no font is found.
    Prioritizes Unicode-capable fonts for international character support.
    """
    platform = sys.platform

    # Get platform-specific paths
    paths = FONT_PATHS.get(platform, [])

    # Check each path
    for font_path in paths:
        if Path(font_path).exists():
            return font_path

    # Fallback: try fc-match on Linux/macOS
    if platform in ("darwin", "linux"):
        try:
            result = subprocess.run(
                ["fc-match", "-f", "%{file}", "sans"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                font = result.stdout.strip()
                if Path(font).exists():
                    return font
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    return None


def resolve_font(preferred: str | None = None) -> str | None:
    """
    Resolve a font path, with optional preferred path.

    Args:
        preferred: Optional preferred font path to check first

    Returns:
        Path to an available font, or None if no font found
    """
    # Check preferred path first
    if preferred and Path(preferred).exists():
        return preferred

    # Check CH_FONT_PATH environment variable
    env_font = os.environ.get("CH_FONT_PATH")
    if env_font and Path(env_font).exists():
        return env_font

    # Fall back to system font detection
    return find_system_font()
