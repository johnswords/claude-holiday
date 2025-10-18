from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)


def build_episode_selections(cut_manifest_path: Path) -> List[Path]:
    manifest = load_json(cut_manifest_path)
    cut_id = manifest["cut_id"]
    recipe = manifest.get("recipe_snapshot", {})
    scope = recipe.get("scope") or {}
    include_eps = scope.get("include_episodes") or []

    selections_files: List[Path] = []
    for ep in include_eps:
        ep_manifest_path = PROJECT_ROOT / "episodes" / ep / "episode.yaml"
        if not ep_manifest_path.exists():
            print(f"[WARN] Episode manifest not found: {ep_manifest_path}")
            continue
        ep_manifest = load_yaml(ep_manifest_path)
        scenes = ep_manifest.get("scenes") or []

        out_doc: Dict[str, Any] = {
            "episode_id": ep,
            "cut_id": cut_id,
            "scenes": {}
        }
        for scene in scenes:
            sid = scene.get("id", "scene")
            cand_dir = PROJECT_ROOT / "output" / "tmp" / cut_id / ep / sid
            cand_meta = cand_dir / "candidates.json"
            candidates: List[Dict[str, Any]] = []
            if cand_meta.exists():
                try:
                    meta = load_json(cand_meta)
                    candidates = meta.get("candidates") or []
                except Exception:
                    candidates = []
            # Default winner_index = 1; include candidates list for reference
            out_doc["scenes"][sid] = {
                "winner_index": 1,
                "candidates": candidates,
            }

        sel_path = PROJECT_ROOT / "episodes" / ep / "renders" / "selections" / f"{cut_id}.yaml"
        save_yaml(sel_path, out_doc)
        selections_files.append(sel_path)
        print(f"[SELECT] Wrote selections template: {sel_path}")

    return selections_files


def main() -> None:
    p = argparse.ArgumentParser(description="Generate per-episode selections YAML from cut candidates.")
    p.add_argument("--cut-manifest", required=True, help="Path to output/cuts/<id>/manifest/cut.manifest.json generated with --candidates-only")
    args = p.parse_args()
    build_episode_selections(Path(args.cut_manifest))


if __name__ == "__main__":
    main()