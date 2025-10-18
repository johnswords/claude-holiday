from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_youtube_metadata(cut_manifest_path: Path) -> Path:
    manifest = load_json(cut_manifest_path)
    cut_id = manifest["cut_id"]
    cut_uri = manifest["cut_uri"]
    recipe = manifest.get("recipe_snapshot", {})
    title = (recipe.get("metadata") or {}).get("title", f"Claude Holiday — Cut {cut_id}")
    audience = recipe.get("audience_profile", "general")
    repo_url = (recipe.get("project") or {}).get("repo_url", "https://github.com/johnswords/claude_holiday")
    timeline = manifest.get("timeline") or (recipe.get("metadata") or {}).get("timeline") or "Prime"

    desc_lines = [
        f"{title}",
        "",
        "A community-composable micro-series parody about AI models as romance archetypes.",
        "",
        f"Timeline: {timeline}",
        f"Cut URI: {cut_uri}",
        f"Repo: {repo_url}",
        "",
        "How to make your own cut:",
        "1) Fork the repo",
        "2) Copy a recipe from recipes/examples/",
        "3) Run: python scripts/compile_cut.py --recipe your_recipe.yaml",
        "",
        "© 2025 John Swords — All rights semi-reserved",
    ]
    metadata = {
        "title": f"{title} [{audience}]",
        "description": "\n".join(desc_lines),
        "tags": [
            "Claude Holiday",
            "AI",
            "Hallmark",
            "Sora",
            "Open Source",
            "RCFC",
            "Dev Humor",
            "Parody"
        ],
        "category": "Film & Animation",
        "language": "en-US",
    }

    out_path = PROJECT_ROOT / "output" / "cuts" / cut_id / "manifest" / "youtube.metadata.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"[YT META] {out_path}")
    return out_path


def main() -> None:
    p = argparse.ArgumentParser(description="Build YouTube metadata JSON from a cut manifest.")
    p.add_argument("--cut-manifest", required=True, help="Path to output/cuts/<id>/manifest/cut.manifest.json")
    args = p.parse_args()
    build_youtube_metadata(Path(args.cut_manifest))


if __name__ == "__main__":
    main()