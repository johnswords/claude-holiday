#!/usr/bin/env python3
"""
Generate AI-powered cover art assets for Claude Holiday.

Creates professional artwork using OpenAI's image generation models,
based on visual descriptions from the master script.

Creates:
- YouTube thumbnails (1280x720)
- YouTube channel banner (2560x1440)
- Title cards for videos (1080x1920)
- Social media squares (1080x1080)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional
import requests
from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "output" / "cover_art"


def build_image_prompt(asset_type: str, title: str, subtitle: str, episode: str = None) -> str:
    """Build a detailed prompt based on master script visuals.

    Uses the visual language from docs/master_script.md to ensure consistency
    with the actual video content - warm Hallmark holiday aesthetic.
    """

    # From master script: warm Hallmark domestic drama palette
    base_prompt = (
        "Cinematic still from a Hallmark holiday romance film. "
        "Cozy inn lobby with crackling fireplace, vintage registry book, warm amber lighting. "
        "Snow visible through windows, rustic wood beams and holiday garland. "
        "Color palette: amber, cream, mahogany, forest green with brass accents. "
        "Style: warm domestic drama, 3200K fireplace key light, cool exterior rim light. "
    )

    if asset_type == "thumbnail":
        specific = (
            f"YouTube thumbnail design featuring professional woman in charcoal coat "
            f"and innkeeper in red flannel shirt at cozy inn registry desk. "
            f"Title text '{title}' in elegant Playfair Display serif, '{episode or 'EP00'}' in corner. "
            f"Warm fireplace glow, snow through windows, 16:9 aspect ratio."
        )
    elif asset_type == "title":
        specific = (
            f"Vertical title card with deep crimson to golden bloom gradient. "
            f"Slow snow fall, soft bokeh drift in background. "
            f"'{title}' in elegant Playfair Display serif centered. "
            f"'{subtitle}' below in smaller text. 9:16 vertical format."
        )
    elif asset_type == "banner":
        specific = (
            f"Wide panoramic view of Evergreen Inn exterior during golden hour. "
            f"Snow-covered small town, warm windows glowing, holiday decorations. "
            f"'{title}' text overlay, '{subtitle}' as tagline. "
            f"YouTube channel banner dimensions."
        )
    else:  # social
        specific = (
            f"Square format cozy inn fireplace scene with 'CH' monogram. "
            f"Warm amber glow, holiday garland, vintage feel. "
            f"Instagram-ready 1:1 aspect ratio."
        )

    # Add quality modifiers
    quality = (
        "High quality digital art, professional design, sharp details, "
        "perfect for social media, no text artifacts, clean composition."
    )

    return f"{base_prompt}{specific} {quality}"


def generate_with_openai(prompt: str, size: str, output_path: Path, api_key: str, model_name: str = "dall-e-3") -> bool:
    """Generate an image using OpenAI image generation models and save it."""

    try:
        client = OpenAI(api_key=api_key)

        print(f"[GENERATING] {output_path.name} using {model_name}")
        print(f"[PROMPT] {prompt[:150]}...")

        # Build parameters based on model
        params = {
            "model": model_name,
            "prompt": prompt,
            "size": size,
            "n": 1,
        }

        # Only add quality for DALL-E models
        if "dall-e" in model_name.lower():
            params["quality"] = "standard"

        response = client.images.generate(**params)
        image_url = response.data[0].url

        # Download and save the image
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(image_response.content)
            print(f"[SUCCESS] Saved to {output_path}")
            return True
        else:
            print(f"[ERROR] Failed to download image: {image_response.status_code}")
            return False

    except Exception as e:
        print(f"[ERROR] Image generation failed: {e}")
        return False


def generate_title_card(output_path: Path, title: str, subtitle: str, api_key: str, model_name: str = "dall-e-3") -> None:
    """Generate a title card (1080x1920) using OpenAI image generation."""

    prompt = build_image_prompt("title", title, subtitle)

    # Use 1024x1792 for vertical format (closest to 9:16)
    success = generate_with_openai(prompt, "1024x1792", output_path, api_key, model_name)

    if success and output_path.exists():
        # Resize to exact dimensions using FFmpeg
        temp_path = output_path.with_suffix('.tmp.png')
        output_path.rename(temp_path)

        cmd = [
            "ffmpeg", "-y",
            "-i", str(temp_path),
            "-vf", "scale=1080:1920",
            str(output_path)
        ]

        subprocess.run(cmd, capture_output=True)
        temp_path.unlink()


def generate_thumbnail(output_path: Path, episode: str, title: str, api_key: str, model_name: str = "dall-e-3") -> None:
    """Generate a YouTube thumbnail (1280x720) using OpenAI image generation."""

    prompt = build_image_prompt("thumbnail", title, "A COMPOSABLE MICRO-SERIES", episode)

    # Use 1792x1024 for horizontal format (we'll crop/resize to 1280x720)
    success = generate_with_openai(prompt, "1792x1024", output_path, api_key, model_name)

    if success and output_path.exists():
        # Resize to exact dimensions using FFmpeg
        temp_path = output_path.with_suffix('.tmp.png')
        output_path.rename(temp_path)

        cmd = [
            "ffmpeg", "-y",
            "-i", str(temp_path),
            "-vf", "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720",
            str(output_path)
        ]

        subprocess.run(cmd, capture_output=True)
        temp_path.unlink()


def generate_banner(output_path: Path, title: str, subtitle: str, api_key: str, model_name: str = "dall-e-3") -> None:
    """Generate a YouTube channel banner (2560x1440) using OpenAI image generation."""

    prompt = build_image_prompt("banner", title, subtitle)

    # Use 1792x1024 (we'll upscale to banner size)
    success = generate_with_openai(prompt, "1792x1024", output_path, api_key, model_name)

    if success and output_path.exists():
        # Upscale to banner dimensions using FFmpeg
        temp_path = output_path.with_suffix('.tmp.png')
        output_path.rename(temp_path)

        cmd = [
            "ffmpeg", "-y",
            "-i", str(temp_path),
            "-vf", "scale=2560:1440:flags=lanczos",
            str(output_path)
        ]

        subprocess.run(cmd, capture_output=True)
        temp_path.unlink()


def generate_social_square(output_path: Path, api_key: str, model_name: str = "dall-e-3") -> None:
    """Generate a social media square (1080x1080) using OpenAI image generation."""

    prompt = build_image_prompt("social", "CH", "CLAUDE HOLIDAY")

    # Use 1024x1024 (perfect square, we'll upscale slightly)
    success = generate_with_openai(prompt, "1024x1024", output_path, api_key, model_name)

    if success and output_path.exists():
        # Upscale to exact dimensions using FFmpeg
        temp_path = output_path.with_suffix('.tmp.png')
        output_path.rename(temp_path)

        cmd = [
            "ffmpeg", "-y",
            "-i", str(temp_path),
            "-vf", "scale=1080:1080:flags=lanczos",
            str(output_path)
        ]

        subprocess.run(cmd, capture_output=True)
        temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate AI-powered cover art assets for Claude Holiday")
    parser.add_argument("--type", choices=["all", "title", "thumbnail", "banner", "social"],
                       default="all", help="Type of asset to generate")
    parser.add_argument("--episode", default="EP00", help="Episode number for thumbnails")
    parser.add_argument("--title", default="CLAUDE HOLIDAY", help="Main title text")
    parser.add_argument("--subtitle", default="A COMPOSABLE MICRO-SERIES", help="Subtitle text")
    parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--model", default="dall-e-3", help="OpenAI model to use (dall-e-3, gpt-image-1, etc.)")
    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] OpenAI API key required. Set OPENAI_API_KEY or use --api-key")
        print("\nTo get an API key:")
        print("1. Sign up at platform.openai.com")
        print("2. Navigate to API keys section")
        print("3. Create a new key")
        print("4. Set: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate requested assets
    if args.type in ["all", "title"]:
        output_path = OUTPUT_DIR / "title_card.png"
        generate_title_card(output_path, args.title, args.subtitle, api_key, args.model)

    if args.type in ["all", "thumbnail"]:
        output_path = OUTPUT_DIR / f"thumbnail_{args.episode.lower()}.png"
        generate_thumbnail(output_path, args.episode, args.title, api_key, args.model)

    if args.type in ["all", "banner"]:
        output_path = OUTPUT_DIR / "youtube_banner.png"
        generate_banner(output_path, args.title, args.subtitle, api_key, args.model)

    if args.type in ["all", "social"]:
        output_path = OUTPUT_DIR / "social_square.png"
        generate_social_square(output_path, api_key, args.model)

    print(f"\n[SUCCESS] Cover art generated in: {OUTPUT_DIR}")
    print(f"[MODEL] Using: {args.model}")
    print("\nNote: Each image is unique. Regenerate if you want variations.")


if __name__ == "__main__":
    main()