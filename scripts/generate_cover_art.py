#!/usr/bin/env python3
"""
Generate cover art assets for Claude Holiday using style guides.

Creates:
- YouTube thumbnails (1280x720)
- YouTube channel banner (2560x1440)
- Title cards for videos (1080x1920)
- Social media squares (1080x1080)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STYLE_GUIDES_DIR = PROJECT_ROOT / "assets" / "style_guides"
OUTPUT_DIR = PROJECT_ROOT / "output" / "cover_art"


def load_style_guide(theme: str) -> Dict[str, Any]:
    """Load and merge style guide with base if needed."""
    guide_path = STYLE_GUIDES_DIR / f"{theme}.json"
    if not guide_path.exists():
        print(f"[ERROR] Style guide not found: {guide_path}")
        sys.exit(1)

    with open(guide_path, "r", encoding="utf-8") as f:
        guide = json.load(f)

    # If guide extends base, merge them
    if guide.get("extends") == "base":
        base_path = STYLE_GUIDES_DIR / "base.json"
        with open(base_path, "r", encoding="utf-8") as f:
            base = json.load(f)
        # Simple merge - guide overrides base
        merged = {**base, **guide}
        # Deep merge some nested dicts
        for key in ["dimensions", "typography", "spacing"]:
            if key in base and key in guide:
                merged[key] = {**base[key], **guide.get(key, {})}
        return merged

    return guide


def generate_title_card(style: Dict[str, Any], output_path: Path, title: str = "CLAUDE HOLIDAY", subtitle: str = "A COMPOSABLE MICRO-SERIES") -> None:
    """Generate a title card (1080x1920) using FFmpeg."""

    dimensions = style["dimensions"]["cover_art"]["title_card"]
    width = dimensions["width"]
    height = dimensions["height"]

    cover_config = style.get("cover_art", {}).get("title_card", {})
    palette = style.get("palette", {})

    # Get background
    bg = cover_config.get("background", {})
    if bg.get("type") == "gradient":
        # Parse gradient - simplified for FFmpeg
        bg_value = bg.get("value", "linear-gradient(135deg, #B87333 0%, #CD7F32 100%)")
        # Extract colors from gradient string (simplified)
        if "#B87333" in bg_value and "#CD7F32" in bg_value:
            color1 = "0xB87333"
            color2 = "0xCD7F32"
        elif "#0052CC" in bg_value:
            color1 = "0x0052CC"
            color2 = "0x0065FF"
        elif "#FFFFFF" in bg_value and "#F4F5F7" in bg_value:
            color1 = "0xFFFFFF"
            color2 = "0xF4F5F7"
        elif "#0D1117" in bg_value:
            color1 = "0x0D1117"
            color2 = "0x0D1117"
        else:
            color1 = "0x444444"
            color2 = "0x666666"
    else:
        # Solid color
        color1 = color2 = bg.get("value", "#444444").lstrip("#")
        color1 = f"0x{color1}"
        color2 = f"0x{color2}"

    # Get text config
    title_config = cover_config.get("title", {})
    title_color = title_config.get("color", "#FFFFFF").lstrip("#")
    title_size = title_config.get("size", 72)

    subtitle_config = cover_config.get("subtitle", {})
    subtitle_color = subtitle_config.get("color", "#FFFFFF").lstrip("#")
    subtitle_size = subtitle_config.get("size", 32)
    subtitle_prefix = subtitle_config.get("prefix", "")
    if subtitle_prefix:
        subtitle = f"{subtitle_prefix} {subtitle}"

    # Escape special characters for FFmpeg drawtext filter
    # Must escape: quotes, colons, commas, brackets, backslashes
    title_escaped = title.replace("'", "'\\''").replace(":", "\\:")
    subtitle_escaped = subtitle.replace("'", "'\\''").replace(":", "\\:")

    # Build FFmpeg command - use color filter since gradients might not be available
    # Create a simple gradient effect with two colors
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c={color1}:s={width}x{height}",
        "-f", "lavfi",
        "-i", f"color=c={color2}:s={width}x{height}",
        "-filter_complex", (
            f"[0][1]blend=all_expr='A*(1-Y/{height})+B*(Y/{height})'[bg];"
            f"[bg]drawtext=text='{title_escaped}':fontsize={title_size}:fontcolor=0x{title_color}:"
            f"x=(w-text_w)/2:y=h/3-text_h/2,"
            f"drawtext=text='{subtitle_escaped}':fontsize={subtitle_size}:fontcolor=0x{subtitle_color}:"
            f"x=(w-text_w)/2:y=h/3+{title_size}"
        ),
        "-frames:v", "1",
        str(output_path)
    ]

    print(f"[GENERATE] Title card: {output_path}")
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def generate_thumbnail(style: Dict[str, Any], output_path: Path, episode: str = "EP00") -> None:
    """Generate a YouTube thumbnail (1280x720) using FFmpeg."""

    dimensions = style["dimensions"]["cover_art"]["youtube_thumbnail"]
    width = dimensions["width"]
    height = dimensions["height"]

    cover_config = style.get("cover_art", {}).get("thumbnail", {})
    palette = style.get("palette", {})

    # Get layout type
    layout = cover_config.get("layout", "split")

    if layout == "split":
        # Split layout - two colors from theme
        primary_keys = list(palette.get("primary", {}).keys())
        if primary_keys:
            left_color = palette["primary"][primary_keys[0]]
        else:
            left_color = "#B87333"

        secondary_keys = list(palette.get("secondary", {}).keys())
        if secondary_keys:
            right_color = palette["secondary"][secondary_keys[0]]
        else:
            right_color = "#FFF8E7"

        # Generate split background with text
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={left_color}:s={width//2}x{height}",
            "-f", "lavfi",
            "-i", f"color=c={right_color}:s={width//2}x{height}",
            "-filter_complex",
            f"[0][1]hstack,drawtext=text='CLAUDE':fontsize=96:fontcolor=white:"
            f"x={width//4}-text_w/2:y=h/2-100,"
            f"drawtext=text='HOLIDAY':fontsize=96:fontcolor=white:"
            f"x={width//4}-text_w/2:y=h/2,"
            f"drawtext=text='{episode}':fontsize=48:fontcolor=black:"
            f"x={width*3//4}-text_w/2:y=h/2-24",
            "-frames:v", "1",
            str(output_path)
        ]
    else:
        # Simple gradient background - get colors from style
        primary_keys = list(palette.get("primary", {}).keys())
        if primary_keys:
            color1 = palette["primary"][primary_keys[0]]
            color2 = palette["primary"][primary_keys[1]] if len(primary_keys) > 1 else "#0065FF"
        else:
            color1 = "#0052CC"
            color2 = "#0065FF"

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={color1}:s={width}x{height}",
            "-f", "lavfi",
            "-i", f"color=c={color2}:s={width}x{height}",
            "-filter_complex", (
                f"[0][1]blend=all_expr='A*(1-X/{width}-Y/{height})+B*(X/{width}+Y/{height})/2'[bg];"
                f"[bg]drawtext=text='CLAUDE HOLIDAY':fontsize=80:fontcolor=white:"
                f"x=(w-text_w)/2:y=h/2-40,"
                f"drawtext=text='{episode}':fontsize=40:fontcolor=white:"
                f"x=(w-text_w)/2:y=h/2+40"
            ),
            "-frames:v", "1",
            str(output_path)
        ]

    print(f"[GENERATE] Thumbnail: {output_path}")
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def generate_banner(style: Dict[str, Any], output_path: Path) -> None:
    """Generate a YouTube channel banner (2560x1440) using FFmpeg."""

    dimensions = style["dimensions"]["cover_art"]["youtube_banner"]
    width = dimensions["width"]
    height = dimensions["height"]
    safe_width = dimensions["safe_area"]["width"]
    safe_height = dimensions["safe_area"]["height"]

    palette = style.get("palette", {})

    # Calculate safe area position (centered)
    safe_x = (width - safe_width) // 2
    safe_y = (height - safe_height) // 2

    # Generate banner with safe area indicator
    primary_color = palette.get("primary", {}).get("brass", "#B87333")

    # Get the first color key to find a secondary color for gradient
    primary_keys = list(palette.get("primary", {}).keys())
    if len(primary_keys) > 1:
        secondary_color = palette["primary"][primary_keys[1]]
    else:
        secondary_color = "#FFD700"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c={primary_color}:s={width}x{height}",
        "-f", "lavfi",
        "-i", f"color=c={secondary_color}:s={width}x{height}",
        "-filter_complex", (
            f"[0][1]blend=all_expr='A*(1-X/{width})+B*(X/{width})'[bg];"
            f"[bg]drawtext=text='CLAUDE HOLIDAY':fontsize=120:fontcolor=white:"
            f"x={safe_x + safe_width//2}-text_w/2:y={safe_y + safe_height//2}-60,"
            f"drawtext=text='COMMUNITY-COMPOSABLE MICRO-SERIES':fontsize=40:fontcolor=white:"
            f"x={safe_x + safe_width//2}-text_w/2:y={safe_y + safe_height//2}+60,"
            # Add subtle safe area border for debugging
            f"drawbox=x={safe_x}:y={safe_y}:w={safe_width}:h={safe_height}:"
            f"color=white@0.1:t=2"
        ),
        "-frames:v", "1",
        str(output_path)
    ]

    print(f"[GENERATE] Banner: {output_path}")
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def generate_social_square(style: Dict[str, Any], output_path: Path) -> None:
    """Generate a social media square (1080x1080) using FFmpeg."""

    dimensions = style["dimensions"]["cover_art"]["social_square"]
    size = dimensions["width"]  # Square, so width = height

    palette = style.get("palette", {})
    # Get the first primary color
    primary_keys = list(palette.get("primary", {}).keys())
    if primary_keys:
        primary_color = palette["primary"][primary_keys[0]]
    else:
        primary_color = "#B87333"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c={primary_color}:s={size}x{size}",
        "-vf", (
            f"drawtext=text='CH':fontsize=200:fontcolor=white:"
            f"x=(w-text_w)/2:y=(h-text_h)/2"
        ),
        "-frames:v", "1",
        str(output_path)
    ]

    print(f"[GENERATE] Social square: {output_path}")
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate cover art assets for Claude Holiday")
    parser.add_argument("--theme", default="brass", help="Style guide theme to use")
    parser.add_argument("--type", choices=["all", "title", "thumbnail", "banner", "social"],
                       default="all", help="Type of asset to generate")
    parser.add_argument("--episode", default="EP00", help="Episode number for thumbnails")
    parser.add_argument("--title", default="CLAUDE HOLIDAY", help="Main title text")
    parser.add_argument("--subtitle", default="A COMPOSABLE MICRO-SERIES", help="Subtitle text")
    args = parser.parse_args()

    # Load style guide
    style = load_style_guide(args.theme)

    # Create output directory
    theme_dir = OUTPUT_DIR / args.theme
    theme_dir.mkdir(parents=True, exist_ok=True)

    # Generate requested assets
    if args.type in ["all", "title"]:
        output_path = theme_dir / "title_card.png"
        generate_title_card(style, output_path, args.title, args.subtitle)

    if args.type in ["all", "thumbnail"]:
        output_path = theme_dir / f"thumbnail_{args.episode.lower()}.png"
        generate_thumbnail(style, output_path, args.episode)

    if args.type in ["all", "banner"]:
        output_path = theme_dir / "youtube_banner.png"
        generate_banner(style, output_path)

    if args.type in ["all", "social"]:
        output_path = theme_dir / "social_square.png"
        generate_social_square(style, output_path)

    print(f"\n[SUCCESS] Cover art generated in: {theme_dir}")
    print("\nAvailable themes:")
    for guide in STYLE_GUIDES_DIR.glob("*.json"):
        if guide.stem != "base":
            print(f"  - {guide.stem}")


if __name__ == "__main__":
    main()