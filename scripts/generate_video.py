"""Generate video clips using Sora provider for specific episodes/scenes."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

# Load .env file if present (for OPENAI_API_KEY)
load_dotenv()

from scripts.providers.base import RenderConfig
from scripts.providers.sora import SoraProvider

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EPISODES_DIR = PROJECT_ROOT / "episodes"
OUTPUT_DIR = PROJECT_ROOT / "output" / "sora_renders"


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_default_render_config() -> RenderConfig:
    """Get default render configuration for 9:16 vertical video."""
    return RenderConfig.from_strings(
        resolution="1080x1920",
        fps=24,
        aspect="9:16",
    )


def generate_scene(
    episode_id: str,
    scene: dict[str, Any],
    provider: SoraProvider,
    render_cfg: RenderConfig,
    output_dir: Path,
    seed: int | None = None,
) -> str:
    """Generate a single scene video."""
    scene_id = scene.get("id", "scene")

    # Create episode output directory
    ep_out_dir = output_dir / episode_id
    ep_out_dir.mkdir(parents=True, exist_ok=True)

    # Generate the scene (positional args to match provider signature)
    output_path = provider.generate_scene(
        episode_id,
        scene,
        str(ep_out_dir),
        render_cfg,
        seed=seed,
    )

    return output_path


def generate_episode(
    episode_id: str,
    provider: SoraProvider,
    render_cfg: RenderConfig,
    output_dir: Path,
    scene_ids: list[str] | None = None,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    """
    Generate all scenes for an episode.

    Args:
        episode_id: Episode directory name (e.g., "ep00_checking_in")
        provider: SoraProvider instance
        render_cfg: Render configuration
        output_dir: Base output directory
        scene_ids: Optional list of specific scene IDs to generate
        seed: Optional seed for reproducibility

    Returns:
        List of generation results with paths
    """
    ep_dir = EPISODES_DIR / episode_id
    manifest_path = ep_dir / "episode.yaml"

    if not manifest_path.exists():
        raise FileNotFoundError(f"Episode manifest not found: {manifest_path}")

    manifest = load_yaml(manifest_path)
    scenes = manifest.get("scenes", [])
    results = []

    for scene in scenes:
        scene_id = scene.get("id", "unknown")

        # Skip if specific scenes requested and this isn't one of them
        if scene_ids and scene_id not in scene_ids:
            continue

        # Ensure scene has a sora_prompt
        if not scene.get("sora_prompt"):
            print(f"[SKIP] {episode_id}/{scene_id} - no sora_prompt", file=sys.stderr)
            continue

        print(f"[GENERATE] {episode_id}/{scene_id}...", file=sys.stderr)

        try:
            output_path = generate_scene(
                episode_id=episode_id,
                scene=scene,
                provider=provider,
                render_cfg=render_cfg,
                output_dir=output_dir,
                seed=seed,
            )
            results.append({
                "episode_id": episode_id,
                "scene_id": scene_id,
                "status": "success",
                "output_path": output_path,
            })
        except Exception as e:
            print(f"[ERROR] {episode_id}/{scene_id}: {e}", file=sys.stderr)
            results.append({
                "episode_id": episode_id,
                "scene_id": scene_id,
                "status": "error",
                "error": str(e),
            })

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate video clips using Sora provider.",
        epilog="Example: ./ch generate-video --episodes ep00_checking_in --scenes s1 s2",
    )
    parser.add_argument(
        "--episodes",
        nargs="+",
        required=True,
        help="Episode IDs to generate (e.g., ep00_checking_in)",
    )
    parser.add_argument(
        "--scenes",
        nargs="+",
        help="Specific scene IDs to generate (default: all scenes)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=str(OUTPUT_DIR),
        help=f"Output directory (default: {OUTPUT_DIR})",
    )
    parser.add_argument(
        "--resolution",
        default="1080x1920",
        help="Video resolution WxH (default: 1080x1920)",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=24,
        help="Frames per second (default: 24)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without actually calling Sora",
    )

    args = parser.parse_args()

    # Check for API key
    if not os.environ.get("OPENAI_API_KEY") and not args.dry_run:
        print("Error: OPENAI_API_KEY environment variable is required.", file=sys.stderr)
        print("Set it with: export OPENAI_API_KEY='your-key-here'", file=sys.stderr)
        sys.exit(1)

    # Create render config
    render_cfg = RenderConfig.from_strings(
        resolution=args.resolution,
        fps=args.fps,
        aspect="9:16",
    )

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print("\n[DRY RUN] Would generate the following:\n")
        for episode_id in args.episodes:
            ep_dir = EPISODES_DIR / episode_id
            manifest_path = ep_dir / "episode.yaml"
            if not manifest_path.exists():
                print(f"  [ERROR] {episode_id}: manifest not found")
                continue

            manifest = load_yaml(manifest_path)
            for scene in manifest.get("scenes", []):
                scene_id = scene.get("id", "unknown")
                if args.scenes and scene_id not in args.scenes:
                    continue
                if not scene.get("sora_prompt"):
                    continue
                duration = scene.get("duration_sec", 5)
                print(f"  {episode_id}/{scene_id} ({duration}s)")
        print()
        return

    # Initialize provider
    provider = SoraProvider()

    # Generate videos
    all_results = []
    for episode_id in args.episodes:
        try:
            results = generate_episode(
                episode_id=episode_id,
                provider=provider,
                render_cfg=render_cfg,
                output_dir=output_dir,
                scene_ids=args.scenes,
                seed=args.seed,
            )
            all_results.extend(results)
        except FileNotFoundError as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            all_results.append({
                "episode_id": episode_id,
                "status": "error",
                "error": str(e),
            })

    # Summary
    success_count = sum(1 for r in all_results if r.get("status") == "success")
    error_count = sum(1 for r in all_results if r.get("status") == "error")

    print(f"\n[SUMMARY] Generated: {success_count}, Errors: {error_count}", file=sys.stderr)

    # Output results as JSON
    print(json.dumps(all_results, indent=2))


if __name__ == "__main__":
    main()
