#!/usr/bin/env python3
"""
Generate cover art assets for Claude Holiday using AI image generation.

Creates visually consistent artwork using OpenAI's gpt-image-1 model,
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
from typing import Dict, Any, Optional
import requests
from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STYLE_GUIDES_DIR = PROJECT_ROOT / "assets" / "style_guides"
OUTPUT_DIR = PROJECT_ROOT / "output" / "cover_art_ai"


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


def build_image_prompt(style: Dict[str, Any], asset_type: str, title: str, subtitle: str, episode: str = None) -> str:
    """Build a detailed prompt for gpt-image-1 based on master script visuals and style guide.

    Uses the visual language from docs/master_script.md to ensure consistency
    with the actual video content.
    """

    mood = style.get("mood", {})
    palette = style.get("palette", {})
    theme_name = style.get("name", "default")

    # Visual elements from master script - consistent across all themes
    # These come from the actual Sora prompts in the script
    base_visual_language = {
        "style": "warm Hallmark domestic drama meets tech satire",
        "palette": "amber/cream/mahogany/forest green with tech accents",
        "setting": "cozy inn in small holiday town, snow visible through windows",
        "lighting": "fireplace key light, golden hour through windows, warm tungsten",
        "atmosphere": "intimate domestic spaces with subtle tech elements"
    }

    # Build prompts based on the master script's visual language
    if theme_name == "brass":
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

    elif theme_name == "dev":
        # Tech/hacker aesthetic referencing the AI model themes
        base_prompt = (
            "Dark terminal interface showing AI assistant interactions. "
            "Black background with green phosphor text, code snippets visible. "
            "References to usage limits, API calls, and rate limiting. "
            "Matrix-style digital rain, CRT monitor aesthetic with scanlines. "
            "Style: cyberpunk meets developer environment, cathode glow. "
        )

        if asset_type == "thumbnail":
            specific = (
                f"YouTube thumbnail showing terminal with error message 'RATE LIMIT EXCEEDED'. "
                f"ASCII art '{title}' in green on black, '{episode or 'EP00'}' as system timestamp. "
                f"Glowing cursor, code snippets about API limits, 16:9 ratio."
            )
        elif asset_type == "title":
            specific = (
                f"Vertical terminal window with '$ ./holiday --init' command. "
                f"'{title}' as ASCII art output, '{subtitle}' as loading message. "
                f"Green text on black, phosphor glow, 9:16 vertical format."
            )
        elif asset_type == "banner":
            specific = (
                f"Multiple terminal windows showing different AI assistant statuses. "
                f"Model names visible in code output. '{title}' as main process. "
                f"'{subtitle}' as system message. YouTube banner dimensions."
            )
        else:  # social
            specific = (
                f"Square terminal with 'CH' ASCII art logo and blinking cursor. "
                f"Green phosphor on black, retro CRT effect, 1:1 ratio."
            )

    elif theme_name == "corporate":
        # Sterile corporate aesthetic referencing The Software Company/Olympus acquisition
        base_prompt = (
            "Modern corporate office environment, sterile and professional. "
            "Glass conference rooms, whiteboards with process diagrams, fluorescent lighting. "
            "References to 'The Software Company of New York' and 'Olympus Corporation'. "
            "Color scheme: corporate blue, gray, white. Minimalist design. "
            "Style: tech company aesthetic, clean lines, antiseptic atmosphere. "
        )

        if asset_type == "thumbnail":
            specific = (
                f"Corporate presentation slide as YouTube thumbnail. "
                f"'{title}' as slide header in Helvetica, '{episode or 'EP00'}' as agenda item. "
                f"Professional PowerPoint aesthetic with company logos, 16:9 ratio."
            )
        elif asset_type == "title":
            specific = (
                f"Vertical corporate report cover page design. "
                f"'{title}' as report title, 'Q4 2025 Initiative: {subtitle}' below. "
                f"Clean sans-serif typography, corporate blue gradient, 9:16 format."
            )
        elif asset_type == "banner":
            specific = (
                f"Corporate office skyline view with glass buildings. "
                f"'{title}' as company initiative overlay, '{subtitle}' as tagline. "
                f"Professional website header design, YouTube banner dimensions."
            )
        else:  # social
            specific = (
                f"Square corporate logo with 'CH' monogram in minimalist style. "
                f"Blue on white, clean design, LinkedIn-appropriate, 1:1 ratio."
            )
    else:
        # Fallback generic prompt
        base_prompt = f"A creative design for '{title}'. "
        specific = f"{asset_type} format with '{subtitle}' as supporting text."

    # Add quality modifiers
    quality = (
        "High quality digital art, professional design, sharp details, "
        "perfect for social media, no text artifacts, clean composition."
    )

    return f"{base_prompt}{specific} {quality}"


def generate_with_openai_image(prompt: str, size: str, output_path: Path, api_key: str, model_name: str = "dall-e-3") -> bool:
    """Generate an image using OpenAI image generation models and save it.

    Args:
        model_name: The model to use (dall-e-3, gpt-image-1, etc.)
                   Note: gpt-image-1 doesn't accept quality parameter
    """

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
        print(f"[ERROR] DALL-E generation failed: {e}")
        return False


def generate_title_card_ai(style: Dict[str, Any], output_path: Path, title: str, subtitle: str, api_key: str, model_name: str = "dall-e-3") -> None:
    """Generate a title card (1080x1920) using OpenAI image generation."""

    prompt = build_image_prompt(style, "title", title, subtitle)

    # Use 1024x1792 for vertical format (closest to 9:16)
    # Note: Adjust size based on model capabilities
    success = generate_with_openai_image(prompt, "1024x1792", output_path, api_key, model_name)

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


def generate_thumbnail_ai(style: Dict[str, Any], output_path: Path, episode: str, api_key: str, model_name: str = "dall-e-3") -> None:
    """Generate a YouTube thumbnail (1280x720) using OpenAI image generation."""

    prompt = build_image_prompt(style, "thumbnail", "CLAUDE HOLIDAY", "A COMPOSABLE MICRO-SERIES", episode)

    # Use 1792x1024 for horizontal format (we'll crop/resize to 1280x720)
    success = generate_with_openai_image(prompt, "1792x1024", output_path, api_key, model_name)

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


def generate_banner_ai(style: Dict[str, Any], output_path: Path, api_key: str, model_name: str = "dall-e-3") -> None:
    """Generate a YouTube channel banner (2560x1440) using OpenAI image generation."""

    prompt = build_image_prompt(style, "banner", "CLAUDE HOLIDAY", "COMMUNITY-COMPOSABLE MICRO-SERIES")

    # Use 1792x1024 (we'll upscale to banner size)
    success = generate_with_openai_image(prompt, "1792x1024", output_path, api_key, model_name)

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


def generate_social_square_ai(style: Dict[str, Any], output_path: Path, api_key: str, model_name: str = "dall-e-3") -> None:
    """Generate a social media square (1080x1080) using OpenAI image generation."""

    prompt = build_image_prompt(style, "social", "CH", "CLAUDE HOLIDAY")

    # Use 1024x1024 (perfect square, we'll upscale slightly)
    success = generate_with_openai_image(prompt, "1024x1024", output_path, api_key, model_name)

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
    parser.add_argument("--theme", default="brass", help="Style guide theme to use")
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
        sys.exit(1)

    # Load style guide
    style = load_style_guide(args.theme)

    # Create output directory
    theme_dir = OUTPUT_DIR / args.theme
    theme_dir.mkdir(parents=True, exist_ok=True)

    # Generate requested assets
    if args.type in ["all", "title"]:
        output_path = theme_dir / "title_card.png"
        generate_title_card_ai(style, output_path, args.title, args.subtitle, api_key, args.model)

    if args.type in ["all", "thumbnail"]:
        output_path = theme_dir / f"thumbnail_{args.episode.lower()}.png"
        generate_thumbnail_ai(style, output_path, args.episode, api_key, args.model)

    if args.type in ["all", "banner"]:
        output_path = theme_dir / "youtube_banner.png"
        generate_banner_ai(style, output_path, api_key, args.model)

    if args.type in ["all", "social"]:
        output_path = theme_dir / "social_square.png"
        generate_social_square_ai(style, output_path, api_key, args.model)

    print(f"\n[SUCCESS] AI cover art generated in: {theme_dir}")
    print(f"[MODEL] Using: {args.model}")
    print("\nNote: Each image is unique. Regenerate if you want variations.")
    print("\nAvailable themes:")
    for guide in STYLE_GUIDES_DIR.glob("*.json"):
        if guide.stem != "base":
            print(f"  - {guide.stem}")


if __name__ == "__main__":
    main()