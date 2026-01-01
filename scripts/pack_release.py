from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def collect_assets(cut_manifest: dict[str, Any], include: list[str]) -> list[Path]:
    assets: list[Path] = []
    # Always include manifest (required)
    manifest_path = PROJECT_ROOT / "output" / "cuts" / cut_manifest["cut_id"] / "manifest" / "cut.manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Required manifest not found: {manifest_path}")
    assets.append(manifest_path)

    episodes = cut_manifest.get("episodes", [])
    if "episodes" in include:
        for ep in episodes:
            video_path = PROJECT_ROOT / ep["video_path"]
            if video_path.exists():
                assets.append(video_path)
            else:
                print(f"[WARN] Episode video not found, skipping: {video_path}", file=sys.stderr)

    # Include captions if requested
    if "captions" in include:
        for ep in episodes:
            captions = ep.get("captions", {})
            # Episode-level captions
            if "episode_captions" in captions:
                ep_caps = captions["episode_captions"]
                if "srt_path" in ep_caps:
                    srt_path = PROJECT_ROOT / ep_caps["srt_path"]
                    if srt_path.exists():
                        assets.append(srt_path)
                    else:
                        print(f"[WARN] Caption not found, skipping: {srt_path}", file=sys.stderr)
                if "ass_path" in ep_caps:
                    ass_path = PROJECT_ROOT / ep_caps["ass_path"]
                    if ass_path.exists():
                        assets.append(ass_path)
                    else:
                        print(f"[WARN] Caption not found, skipping: {ass_path}", file=sys.stderr)
            # Per-scene captions
            if "scene_captions" in captions:
                for scene_cap in captions["scene_captions"]:
                    if "srt_path" in scene_cap:
                        srt_path = PROJECT_ROOT / scene_cap["srt_path"]
                        if srt_path.exists():
                            assets.append(srt_path)
                        else:
                            print(f"[WARN] Caption not found, skipping: {srt_path}", file=sys.stderr)
                    if "ass_path" in scene_cap:
                        ass_path = PROJECT_ROOT / scene_cap["ass_path"]
                        if ass_path.exists():
                            assets.append(ass_path)
                        else:
                            print(f"[WARN] Caption not found, skipping: {ass_path}", file=sys.stderr)

    # Placeholder: series/full compilation can be added later

    # YouTube metadata (if created by yt/metadata.py)
    ytm = PROJECT_ROOT / "output" / "cuts" / cut_manifest["cut_id"] / "manifest" / "youtube.metadata.json"
    if ytm.exists():
        assets.append(ytm)

    return assets


def build_release_bundle(cut_manifest_path: Path, include: list[str], out_dir: Path) -> Path:
    cut_manifest = load_json(cut_manifest_path)
    cut_id = cut_manifest["cut_id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = out_dir / f"ClaudeHoliday_{cut_id}.zip"

    assets = collect_assets(cut_manifest, include)
    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in assets:
            arcname = p.relative_to(PROJECT_ROOT).as_posix()
            zf.write(p, arcname)

    print(f"[BUNDLE] {bundle_path}")
    return bundle_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Pack a compiled cut into a release bundle.")
    parser.add_argument("--cut-manifest", required=True, help="Path to output/cuts/<id>/manifest/cut.manifest.json")
    parser.add_argument(
        "--include", nargs="+", default=["episodes"], help="Assets to include: episodes series captions"
    )
    parser.add_argument("--out", default="output/releases", help="Output directory for bundles")
    args = parser.parse_args()

    cut_manifest_path = Path(args.cut_manifest)
    out_dir = PROJECT_ROOT / args.out
    build_release_bundle(cut_manifest_path, include=args.include, out_dir=out_dir)


if __name__ == "__main__":
    main()
