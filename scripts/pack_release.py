from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def collect_assets(cut_manifest: dict[str, Any], include: list[str]) -> list[Path]:
    assets: list[Path] = []
    # Always include manifest
    manifest_path = Path("output") / "cuts" / cut_manifest["cut_id"] / "manifest" / "cut.manifest.json"
    assets.append(manifest_path)

    episodes = cut_manifest.get("episodes", [])
    if "episodes" in include:
        for ep in episodes:
            assets.append(Path(ep["video_path"]))

    # Placeholder: series/full compilation can be added later
    # Captions not generated in MVP; reserved for future.

    # YouTube metadata (if created by yt/metadata.py)
    ytm = Path("output") / "cuts" / cut_manifest["cut_id"] / "manifest" / "youtube.metadata.json"
    if ytm.exists():
        assets.append(ytm)

    return [PROJECT_ROOT / a for a in assets]


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
