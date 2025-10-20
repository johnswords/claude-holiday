#!/usr/bin/env python3
"""
ch - Claude Holiday CLI
Unified entry point for all Claude Holiday commands.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_script(script_path: Path, args: list[str]) -> None:
    """Execute a Python script with given arguments."""
    cmd = [sys.executable, str(script_path)] + args
    result = subprocess.run(cmd, cwd=script_path.parent.parent)
    sys.exit(result.returncode)


def cmd_compile(args: argparse.Namespace) -> None:
    """Compile a complete cut from an RCFC recipe."""
    script = Path(__file__).resolve().parent / "scripts" / "compile_cut.py"
    script_args = ["--recipe", args.recipe]
    run_script(script, script_args)


def cmd_candidates(args: argparse.Namespace) -> None:
    """Generate candidate renders for each scene (review before final compile)."""
    script = Path(__file__).resolve().parent / "scripts" / "compile_cut.py"
    script_args = ["--recipe", args.recipe, "--candidates-only"]
    run_script(script, script_args)


def cmd_select(args: argparse.Namespace) -> None:
    """Create selection YAML templates from generated candidates."""
    script = Path(__file__).resolve().parent / "scripts" / "select_winners.py"
    script_args = ["--cut-manifest", args.cut_manifest]
    run_script(script, script_args)


def cmd_bundle(args: argparse.Namespace) -> None:
    """Pack a compiled cut into a release bundle (zip)."""
    script = Path(__file__).resolve().parent / "scripts" / "pack_release.py"
    script_args = ["--cut-manifest", args.cut_manifest]
    if args.include:
        script_args.extend(["--include"] + args.include)
    if args.out != "output/releases":
        script_args.extend(["--out", args.out])
    run_script(script, script_args)


def cmd_ytmeta(args: argparse.Namespace) -> None:
    """Generate YouTube metadata JSON from a cut manifest."""
    script = Path(__file__).resolve().parent / "scripts" / "yt" / "metadata.py"
    script_args = ["--cut-manifest", args.cut_manifest]
    run_script(script, script_args)


def cmd_cover_art(args: argparse.Namespace) -> None:
    """Generate cover art assets (thumbnails, banners, title cards)."""
    script = Path(__file__).resolve().parent / "scripts" / "generate_cover_art.py"
    script_args = []

    if args.theme:
        script_args.extend(["--theme", args.theme])
    if args.type:
        script_args.extend(["--type", args.type])
    if args.episode:
        script_args.extend(["--episode", args.episode])
    if args.title:
        script_args.extend(["--title", args.title])
    if args.subtitle:
        script_args.extend(["--subtitle", args.subtitle])

    run_script(script, script_args)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ch",
        description="Claude Holiday - Community-composable media toolkit",
        epilog="Example: ch compile --recipe recipes/examples/dev-default.yaml"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="COMMAND"
    )

    # compile subcommand
    compile_parser = subparsers.add_parser(
        "compile",
        help="Compile a complete cut from recipe",
        description="Compile episodes from an RCFC recipe, applying selections if available."
    )
    compile_parser.add_argument(
        "--recipe",
        required=True,
        help="Path to RCFC recipe YAML file"
    )
    compile_parser.set_defaults(func=cmd_compile)

    # candidates subcommand
    candidates_parser = subparsers.add_parser(
        "candidates",
        help="Generate candidate renders (no stitching)",
        description="Generate multiple candidate renders per scene for review. Use 'ch select' afterward to choose winners."
    )
    candidates_parser.add_argument(
        "--recipe",
        required=True,
        help="Path to RCFC recipe YAML file"
    )
    candidates_parser.set_defaults(func=cmd_candidates)

    # select subcommand
    select_parser = subparsers.add_parser(
        "select",
        help="Create selection templates from candidates",
        description="Generate per-episode selection YAML files from candidates. Edit these to choose winner_index, then recompile."
    )
    select_parser.add_argument(
        "--cut-manifest",
        required=True,
        help="Path to cut manifest JSON (output/cuts/<id>/manifest/cut.manifest.json)"
    )
    select_parser.set_defaults(func=cmd_select)

    # bundle subcommand
    bundle_parser = subparsers.add_parser(
        "bundle",
        help="Pack cut into release bundle",
        description="Create a release ZIP bundle containing videos, manifests, and metadata."
    )
    bundle_parser.add_argument(
        "--cut-manifest",
        required=True,
        help="Path to cut manifest JSON (output/cuts/<id>/manifest/cut.manifest.json)"
    )
    bundle_parser.add_argument(
        "--include",
        nargs="+",
        default=["episodes"],
        help="Assets to include: episodes series captions (default: episodes)"
    )
    bundle_parser.add_argument(
        "--out",
        default="output/releases",
        help="Output directory for bundles (default: output/releases)"
    )
    bundle_parser.set_defaults(func=cmd_bundle)

    # ytmeta subcommand
    ytmeta_parser = subparsers.add_parser(
        "ytmeta",
        help="Generate YouTube metadata JSON",
        description="Build YouTube-ready metadata (title, description, tags) from a cut manifest."
    )
    ytmeta_parser.add_argument(
        "--cut-manifest",
        required=True,
        help="Path to cut manifest JSON (output/cuts/<id>/manifest/cut.manifest.json)"
    )
    ytmeta_parser.set_defaults(func=cmd_ytmeta)

    # cover-art subcommand
    cover_art_parser = subparsers.add_parser(
        "cover-art",
        help="Generate cover art assets",
        description="Generate YouTube thumbnails, banners, title cards, and social media images."
    )
    cover_art_parser.add_argument(
        "--theme",
        default="brass",
        choices=["brass", "dev", "corporate"],
        help="Style guide theme to use (default: brass)"
    )
    cover_art_parser.add_argument(
        "--type",
        default="all",
        choices=["all", "title", "thumbnail", "banner", "social"],
        help="Type of asset to generate (default: all)"
    )
    cover_art_parser.add_argument(
        "--episode",
        default="EP00",
        help="Episode number for thumbnails (default: EP00)"
    )
    cover_art_parser.add_argument(
        "--title",
        default="CLAUDE HOLIDAY",
        help="Main title text (default: CLAUDE HOLIDAY)"
    )
    cover_art_parser.add_argument(
        "--subtitle",
        default="A COMPOSABLE MICRO-SERIES",
        help="Subtitle text (default: A COMPOSABLE MICRO-SERIES)"
    )
    cover_art_parser.set_defaults(func=cmd_cover_art)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute the command
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
