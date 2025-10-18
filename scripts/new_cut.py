from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import yaml


def load_yaml(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)


def scaffold_recipe(base_recipe_path: Path, title: str, out_path: Path) -> Path:
    recipe = load_yaml(base_recipe_path)
    recipe.setdefault("metadata", {})
    recipe["metadata"]["title"] = title
    recipe["metadata"]["created"] = datetime.utcnow().isoformat() + "Z"
    save_yaml(out_path, recipe)
    return out_path


def main() -> None:
    p = argparse.ArgumentParser(description="Create a new RCFC recipe from a base example.")
    p.add_argument("--from", dest="base", required=True, help="Path to base example recipe")
    p.add_argument("--title", required=True, help="Title for your cut")
    p.add_argument("--out", required=True, help="Output recipe path")
    args = p.parse_args()
    out = scaffold_recipe(Path(args.base), args.title, Path(args.out))
    print(f"[NEW CUT] {out}")


if __name__ == "__main__":
    main()