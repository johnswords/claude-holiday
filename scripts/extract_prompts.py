"""Extract Sora prompts from episode manifests for review or batch generation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EPISODES_DIR = PROJECT_ROOT / "episodes"


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def extract_prompts_from_episode(episode_path: Path) -> list[dict[str, Any]]:
    """
    Extract all Sora prompts from an episode manifest.

    Returns a list of dicts with scene metadata and prompts.
    """
    manifest = load_yaml(episode_path)
    episode_id = manifest.get("episode_id", episode_path.parent.name)
    title = manifest.get("title", episode_id)

    prompts = []
    for scene in manifest.get("scenes", []):
        scene_id = scene.get("id", "unknown")
        scene_title = scene.get("title", scene_id)
        duration = scene.get("duration_sec", 5)
        sora_prompt = scene.get("sora_prompt", "")

        if sora_prompt:
            prompts.append({
                "episode_id": episode_id,
                "episode_title": title,
                "scene_id": scene_id,
                "scene_title": scene_title,
                "duration_sec": duration,
                "sora_prompt": sora_prompt.strip(),
            })

    return prompts


def extract_all_prompts(episode_ids: list[str] | None = None) -> list[dict[str, Any]]:
    """
    Extract prompts from all episodes or a specific list.

    Args:
        episode_ids: Optional list of episode IDs to process. If None, processes all.

    Returns:
        List of prompt dicts sorted by episode and scene.
    """
    all_prompts = []

    # Find all episode directories
    episode_dirs = sorted(EPISODES_DIR.glob("ep*"))

    for ep_dir in episode_dirs:
        ep_id = ep_dir.name
        manifest_path = ep_dir / "episode.yaml"

        # Skip if episode_ids specified and this episode not in list
        if episode_ids and ep_id not in episode_ids:
            continue

        if not manifest_path.exists():
            print(f"[WARN] No episode.yaml found in {ep_dir}", file=sys.stderr)
            continue

        prompts = extract_prompts_from_episode(manifest_path)
        all_prompts.extend(prompts)

    return all_prompts


def format_prompts_markdown(prompts: list[dict[str, Any]]) -> str:
    """Format prompts as Markdown for human review."""
    lines = ["# Sora Prompts — Claude Holiday\n"]

    current_episode = None
    for p in prompts:
        if p["episode_id"] != current_episode:
            current_episode = p["episode_id"]
            lines.append(f"\n## {p['episode_title']}\n")

        lines.append(f"### Scene: {p['scene_id']} — {p['scene_title']} ({p['duration_sec']}s)\n")
        lines.append("```")
        lines.append(p["sora_prompt"])
        lines.append("```\n")

    return "\n".join(lines)


def format_prompts_json(prompts: list[dict[str, Any]]) -> str:
    """Format prompts as JSON for programmatic use."""
    return json.dumps(prompts, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract Sora prompts from episode manifests.",
        epilog="Example: ./ch extract-prompts --episodes ep00_checking_in ep01_first_contact --format json",
    )
    parser.add_argument(
        "--episodes",
        nargs="+",
        help="Specific episode IDs to extract (default: all episodes)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)",
    )

    args = parser.parse_args()

    prompts = extract_all_prompts(args.episodes)

    if not prompts:
        print("No prompts found.", file=sys.stderr)
        sys.exit(1)

    # Format output
    if args.format == "json":
        output = format_prompts_json(prompts)
    else:
        output = format_prompts_markdown(prompts)

    # Write output
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"[EXTRACT] Wrote {len(prompts)} prompts to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
